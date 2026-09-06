#!/usr/bin/env python3
"""
Tests for the Evil Encryption Academy site.

Every test here exists because something actually went wrong during
development. They are guards against specific known failures, not coverage
for its own sake.

    python3 -m unittest discover tests -v
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES = [f"{i:02d}" for i in range(1, 14)]


def pages():
    return sorted(f for f in os.listdir(ROOT) if f.endswith(".html"))


def read(name):
    with open(os.path.join(ROOT, name), encoding="utf-8") as fh:
        return fh.read()


def body_words(html):
    body = html.split("<main")[1].split("</main>")[0]
    return len(re.sub(r"<[^>]+>", " ", body).split())


class TestBuild(unittest.TestCase):
    def test_site_rebuilds_reproducibly(self):
        """The generator must produce exactly what is checked in."""
        before = {p: read(p) for p in pages()}
        r = subprocess.run([sys.executable, "engine.py"], cwd=ROOT,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        for p, old in before.items():
            self.assertEqual(old, read(p), f"{p} differs from a fresh build")

    def test_every_module_page_exists(self):
        for m in MODULES:
            hits = [p for p in pages() if p.startswith(m + "-")]
            self.assertEqual(len(hits), 1, f"module {m}: expected 1 page, found {hits}")
        for extra in ("index.html", "reference.html", "404.html"):
            self.assertIn(extra, pages(), f"{extra} missing")


class TestJavaScript(unittest.TestCase):
    """
    BUG: a Python escape collapsed \\' into a bare apostrophe inside a JS
    string, silently breaking an entire page's simulation. Only a real parser
    catches that; brace counting does not.
    """

    def test_all_inline_javascript_parses(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        for p in pages():
            js = "\n".join(re.findall(r"<script>(.*?)</script>", read(p), re.S))
            if not js.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                             encoding="utf-8") as tf:
                tf.write(js)
                path = tf.name
            try:
                r = subprocess.run([node, "--check", path], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{p} has invalid JS:\n{r.stderr}")
            finally:
                os.unlink(path)

    def test_shared_script_parses(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available")
        r = subprocess.run([node, "--check", os.path.join(ROOT, "assets/academy.js")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class TestNavigation(unittest.TestCase):
    def test_nav_links_resolve(self):
        nav = read("assets/_nav.html")
        for href in re.findall(r'href="([^"]+)"', nav):
            self.assertTrue(os.path.exists(os.path.join(ROOT, href)),
                            f"nav points at missing page: {href}")

    def test_progress_list_matches_nav(self):
        """
        academy.js tracks progress against a hardcoded module list. If it drifts
        from the nav, the progress bar silently reports the wrong total.
        """
        js = read("assets/academy.js")
        listed = re.search(r"const PAGES = \[(.*?)\]", js, re.S).group(1)
        tracked = re.findall(r"'(\d\d)'", listed)
        self.assertEqual(tracked, MODULES,
                         "academy.js PAGES is out of step with the module set")

    def test_pager_chain_is_complete(self):
        """Following 'next' from the index must reach every page exactly once."""
        seen, cur = [], "index.html"
        while cur and cur not in seen:
            seen.append(cur)
            m = re.search(r'<a class="nxt" href="([^"]+)"', read(cur))
            cur = m.group(1) if m else None
        self.assertEqual(len(seen), len(MODULES) + 2,
                         f"pager chain covers {len(seen)} pages: {seen}")

    def test_no_dead_internal_links(self):
        bad = []
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in files:
                if not f.endswith((".html", ".md")):
                    continue
                p = os.path.join(root, f)
                with open(p, encoding="utf-8") as fh:
                    text = fh.read()
                pat = (r'(?:href|src)="(?!https?:|#|mailto:|data:)([^"]+)"'
                       if f.endswith(".html")
                       else r"\]\((?!https?://|#|mailto:)([^)#]+)")
                # _nav.html is a fragment inlined into root-level pages, so its
                # links resolve against the repository root, not assets/.
                base = ROOT if f == "_nav.html" else root
                for link in re.findall(pat, text):
                    if not os.path.exists(os.path.normpath(os.path.join(base, link))):
                        bad.append(f"{os.path.relpath(p, ROOT)} -> {link}")
        self.assertEqual(bad, [], f"dead links: {bad}")


class TestContent(unittest.TestCase):
    def test_no_module_is_thin(self):
        """
        The ransomware modules were once 30% shorter than the background
        material leading up to them, which is the wrong way round. This holds
        a floor so that cannot quietly return.
        """
        thin = []
        for p in pages():
            if not re.match(r"^\d\d-", p):
                continue
            w = body_words(read(p))
            if w < 900:
                thin.append(f"{p} ({w} words)")
        self.assertEqual(thin, [], f"modules below the 900-word floor: {thin}")

    def test_every_module_has_a_simulation(self):
        for p in pages():
            if not re.match(r"^\d\d-", p):
                continue
            self.assertIn('class="sim"', read(p), f"{p} has no simulation")

    def test_module_pages_use_svg_diagrams(self):
        """Diagram work drawn in monospace was what made the site look plain."""
        for p in pages():
            if not re.match(r"^\d\d-", p):
                continue
            html = read(p)
            with self.subTest(page=p):
                self.assertIn("<svg", html, "no SVG diagram")
                self.assertIn("<figcaption", html, "SVG has no caption")
                self.assertIn('role="img"', html, "SVG has no accessible label")

    def test_no_leftover_references_to_removed_material(self):
        """
        The repository previously carried a DFIR curriculum with recovery
        tooling. It was removed deliberately; nothing should still point at it.
        """
        gone = ["recover_partial", "parse_footer", "canary_deploy", "identify_crypto",
                "capstone/", "SAFE_LAB_SETUP", "FIRST-60-MINUTES", "MYTHS.md"]
        hits = []
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
            for f in files:
                if not f.endswith((".html", ".md", ".py", ".yml", ".txt")):
                    continue
                p = os.path.join(root, f)
                with open(p, encoding="utf-8", errors="ignore") as fh:
                    text = fh.read()
                for g in gone:
                    if g in text and "test_site" not in f:
                        hits.append(f"{os.path.relpath(p, ROOT)} mentions {g}")
        self.assertEqual(hits, [], f"stale references: {hits}")


class TestAccessibilityAndMetadata(unittest.TestCase):
    """
    The site once had zero aria attributes, no favicon and no social preview.
    The canvas simulations are visual arguments with no text alternative unless
    one is supplied deliberately.
    """

    def test_every_page_has_metadata_and_landmarks(self):
        for p in pages():
            html = read(p)
            with self.subTest(page=p):
                self.assertIn('property="og:title"', html, "no social preview")
                self.assertIn('rel="icon"', html, "no favicon")
                self.assertIn('class="skip"', html, "no skip-to-content link")
                self.assertIn('lang="en"', html, "no language declared")
                self.assertIn("data-theme", html, "no theme handling")

    def test_canvas_pages_provide_text_alternatives(self):
        for p in pages():
            html = read(p)
            if "<canvas" in html:
                with self.subTest(page=p):
                    self.assertIn('role="status"', html,
                                  "canvas present but no text alternative")

    def test_referenced_assets_exist(self):
        bad = []
        for p in pages():
            for a in re.findall(r'(?:href|src)="(assets/[^"]+)"', read(p)):
                if not os.path.exists(os.path.join(ROOT, a)):
                    bad.append(f"{p} -> {a}")
        self.assertEqual(bad, [], f"missing assets: {bad}")


class TestRepositoryIntegrity(unittest.TestCase):
    def test_structure_txt_is_current(self):
        """
        BUG: the hand-written map drifted to describe a completely different
        repository and passed, because the old check only verified that named
        files existed and never that existing files were named.
        """
        gen = os.path.join(ROOT, "make_structure.py")
        current = read("STRUCTURE.txt")
        try:
            subprocess.run([sys.executable, gen], cwd=ROOT, capture_output=True, check=True)
            regenerated = read("STRUCTURE.txt")
        finally:
            with open(os.path.join(ROOT, "STRUCTURE.txt"), "w", encoding="utf-8") as fh:
                fh.write(current)
        self.assertEqual(current, regenerated,
                         "STRUCTURE.txt is stale - run python3 make_structure.py")

    def test_license_exists(self):
        self.assertIn("MIT License", read("LICENSE"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
