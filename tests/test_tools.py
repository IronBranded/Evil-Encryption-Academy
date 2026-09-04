#!/usr/bin/env python3
"""
Regression tests for Evil-Encryption-Academy tooling.

Every test here exists because a real bug shipped. The comments name which one.

    python3 -m unittest discover tests -v
    python3 tests/test_tools.py

Requires: cryptography (for the AES specimens). Everything else is stdlib.
"""

import base64
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, relpath):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, relpath))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pf = load("parse_footer", "02-Hybrid-Encryption-Model/labs/parse_footer.py")
rp = load("recover_partial", "10-Recovery-and-Decryption/labs/recover_partial.py")
cd = load("canary_deploy", "11-Endpoint-Detection/labs/canary_deploy.py")
ic = load("identify_crypto", "tools/identify_crypto.py")


def verdict(path, block=4096):
    return pf.analyze(path, block)["classification"]["verdict"]


def write(tmp, name, data):
    p = os.path.join(tmp, name)
    with open(p, "wb") as fh:
        fh.write(data)
    return p


RECORD = (b"BEGIN RECORD; customer=ACME; invoice=2024-0417; "
          b"amount=48200.00; status=UNPAID; END RECORD\n")


class TestEntropyCalibration(unittest.TestCase):
    """
    BUG: normalization used the theoretical ceiling log2(min(n,256)). Real random
    data never reaches it at small sample sizes, so a 128-byte RSA-wrapped key
    scored 0.936 and fell below the 0.94 detection threshold. The tool was
    rejecting genuine ciphertext.
    """

    def test_small_random_samples_normalize_near_one(self):
        for n in (32, 64, 128, 256, 512, 4096):
            with self.subTest(size=n):
                vals = [pf.normalized(os.urandom(n)) for _ in range(30)]
                mean = sum(vals) / len(vals)
                self.assertGreater(mean, 0.94,
                                   f"{n}-byte random scored {mean:.3f}; would be missed")
                self.assertLess(mean, 1.08)

    def test_structured_data_scores_low(self):
        self.assertLess(pf.normalized(RECORD * 100), 0.75)


class TestClassification(unittest.TestCase):
    """Each encryption paradigm must be distinguishable from the ciphertext alone."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.plain = (RECORD * 400)

    def test_plaintext(self):
        p = write(self.tmp, "notes.txt", self.plain)
        self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_full_encryption(self):
        p = write(self.tmp, "doc.dat", os.urandom(64 * 1024))
        self.assertEqual(verdict(p), "FULL ENCRYPTION")

    def test_intermittent_encryption(self):
        chunks = []
        for i in range(10):
            chunks.append(os.urandom(4096) if i % 2 == 0 else (RECORD * 80)[:4096])
        p = write(self.tmp, "db.dat", b"".join(chunks))
        self.assertIn("INTERMITTENT", verdict(p))

    def test_distributed_chunk_encryption(self):
        """The Gentlemen pattern: three chunks at head, midpoint and tail."""
        body = bytearray((RECORD * 12000)[:1200000])
        n, clen = len(body), int(len(body) * 0.09)
        for off in (0, n // 2, n - clen):
            body[off:off + clen] = os.urandom(clen)
        p = write(self.tmp, "big.dat", bytes(body))
        self.assertIn("DISTRIBUTED-CHUNK", verdict(p))

    def test_header_only_encryption(self):
        p = write(self.tmp, "hdr.dat", os.urandom(4096) + (RECORD * 800)[:32768])
        self.assertIn("HEADER-ONLY", verdict(p))


class TestFormatFalsePositives(unittest.TestCase):
    """
    BUG: the entropy classifier called a JPEG and an MP4 FULL ENCRYPTION at HIGH
    confidence. Running it across a file server to scope an incident would flag
    every photo and video as encrypted and massively inflate the blast radius.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_jpeg_not_flagged(self):
        p = write(self.tmp, "photo.jpg",
                  b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + os.urandom(300000))
        self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_mp4_not_flagged(self):
        p = write(self.tmp, "clip.mp4", b"\x00\x00\x00\x20ftypmp42" + os.urandom(400000))
        self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_zip_not_flagged(self):
        p = write(self.tmp, "a.zip", b"PK\x03\x04" + os.urandom(200000))
        self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_short_magic_does_not_veto_format_verdict(self):
        """
        BUG: find_magics carried a 3-byte pattern (the bare X25519 OID). In 300KB
        of random data a given 3-byte sequence appears ~1.8% of the time, which
        set has_markers, suppressed the format correction, and made the JPEG
        false positive come back intermittently. On a 1GB file it would hit ~60
        times by chance. Short magics must not override format evidence.
        """
        for magic in (b"\x2b\x65\x6e", b"RSA1", b"ECK1", b"KDBM"):
            with self.subTest(magic=magic):
                body = bytearray(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + os.urandom(300000))
                body[150000:150000 + len(magic)] = magic          # mid-file, not the tail
                p = write(self.tmp, f"photo_{magic.hex()}.jpg", bytes(body))
                self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_no_signature_shorter_than_four_bytes(self):
        """Patterns under 4 bytes are noise on any large file, not signatures."""
        for needle, meaning in pf.MAGICS:
            self.assertGreaterEqual(len(needle), 4, f"{meaning}: {needle!r} too short")

    def test_media_verdict_is_stable_across_random_content(self):
        """The false-positive fix must not be probabilistic."""
        for i in range(25):
            p = write(self.tmp, f"clip_{i}.mp4",
                      b"\x00\x00\x00\x20ftypmp42" + os.urandom(200000))
            self.assertIn("NOT ENCRYPTED", verdict(p).upper(), f"flaked on iteration {i}")

    def test_encrypted_jpeg_still_detected(self):
        """Header destroyed + ransom extension: must NOT be excused as media."""
        p = write(self.tmp, "holiday.jpg.umc16h", os.urandom(400000))
        v = verdict(p)
        self.assertIn("FULL ENCRYPTION", v)
        detail = pf.analyze(p, 4096)["classification"]["detail"]
        self.assertIn("MISMATCH", detail)

    def test_header_preserving_encryption_detected(self):
        """
        BUG (introduced by the fix above): an intermittently encrypted JPEG whose
        header survived was dismissed as an intact media file. An unrecognized
        appended extension must override the intact-header correction.
        """
        img = bytearray(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + os.urandom(200000))
        for i in range(0, len(img), 8192):
            if (i // 8192) % 2:
                img[i:i + 8192] = b"\x00\x11\x22\x33" * 2048
        p = write(self.tmp, "beach.jpg.akira", bytes(img))
        self.assertNotIn("NOT ENCRYPTED", verdict(p).upper())


class TestTextFooter(unittest.TestCase):
    """
    BUG: The Gentlemen stores its ephemeral Curve25519 public key as BASE64 behind
    ASCII delimiters. Base64 scores ~6.0 bits/byte, so entropy-based tail scanning
    is structurally incapable of seeing it. The tool reported spurious RSA-4096
    candidates (the tail of the last encrypted chunk) and missed the real footer.
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_base64_ephemeral_key_detected(self):
        eph = os.urandom(32)
        footer = b"--eph--" + base64.b64encode(eph) + b"--marker--GENTLEMEN"
        p = write(self.tmp, "report.xlsx.umc16h", os.urandom(200000) + footer)
        tf = pf.analyze(p, 4096)["text_footer"]
        self.assertTrue(any(b["decoded_len"] == 32 for b in tf["b64_blobs"]),
                        "32-byte ephemeral public key not recovered from footer")
        self.assertTrue(any("eph" in d["text"] for d in tf["delimiters"]))

    def test_tail_strings_sorted_nearest_eof(self):
        """
        BUG: strings were returned in file order, so footer markers were pushed
        past the display limit behind random printable runs earlier in the tail.
        """
        p = write(self.tmp, "x.bin", os.urandom(8000) + b"--marker--GENTLEMEN")
        hits = pf.analyze(p, 4096)["tail_strings"]
        self.assertTrue(hits)
        self.assertEqual(hits, sorted(hits, key=lambda h: h["from_eof"]))
        self.assertLess(hits[0]["from_eof"], 40)


class TestFooterSizing(unittest.TestCase):
    def test_rsa2048_footer_and_delta(self):
        tmp = tempfile.mkdtemp()
        orig = (RECORD * 400)
        o = write(tmp, "invoice.xlsx", orig)
        body = os.urandom(len(orig) + (-len(orig) % 16))
        e = write(tmp, "invoice.xlsx.locked", body + os.urandom(256))
        r = pf.analyze(e, 4096, original=o)
        self.assertEqual(r["delta"]["overhead"] - 256, len(body) - len(orig))
        strong = [f for f in r["footer_candidates"]
                  if f["looks_random"] and f["block_aligned"] and f["size"] == 256]
        self.assertTrue(strong, "RSA-2048 sized footer not flagged")


class TestCryptoIdentification(unittest.TestCase):
    def _scan(self, data):
        return {f["name"] for f in ic.scan(data, "low", [])}

    def test_aes_sbox(self):
        blob = os.urandom(512) + bytes.fromhex("637c777bf26b6fc53001672bfed7ab76")
        self.assertIn("AES S-box", self._scan(blob))

    def test_chacha_sigma(self):
        self.assertIn("ChaCha/Salsa sigma (256-bit)",
                      self._scan(os.urandom(256) + b"expand 32-byte k"))

    def test_hybrid_inference(self):
        blob = (os.urandom(256)
                + bytes.fromhex("637c777bf26b6fc53001672bfed7ab76")
                + b"-----BEGIN PUBLIC KEY-----")
        notes = " ".join(ic.interpret(ic.scan(blob, "low", [])))
        self.assertIn("HYBRID", notes)

    def test_lotl_bitlocker_inference(self):
        notes = " ".join(ic.interpret(ic.scan(b"Win32_EncryptableVolume", "low", [])))
        self.assertIn("LIVING-OFF-THE-LAND", notes)

    def test_no_findings_gives_guidance(self):
        notes = " ".join(ic.interpret([]))
        self.assertIn("packed", notes.lower())


class TestPartialRecovery(unittest.TestCase):
    """Partial recovery is the highest-value branch of the Module 10 decision tree."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        rows = b"".join(b"INSERT INTO t VALUES (%d,'ACME','48200.00','UNPAID');\n" % i
                        for i in range(1, 3001))
        self.body = bytearray((rows * 12)[:2_000_000])

    def _chunked(self, pct):
        b = bytearray(self.body)
        n, clen = len(b), int(len(b) * pct)
        for off in (0, n // 2, n - clen):
            b[off:off + clen] = os.urandom(clen)
        return bytes(b)

    def test_ultrafast_recovers_almost_everything(self):
        p = write(self.tmp, "db.mdf.umc16h", self._chunked(0.003))
        r = rp.analyze(p, rp.COARSE, rp.FINE, 0)
        self.assertGreater(r["recoverable_pct"], 95.0)

    def test_default_mode_recovers_majority(self):
        p = write(self.tmp, "db.mdf.umc16h", self._chunked(0.09))
        r = rp.analyze(p, rp.COARSE, rp.FINE, 0)
        self.assertGreater(r["recoverable_pct"], 60.0)

    def test_full_encryption_yields_nothing(self):
        p = write(self.tmp, "db.mdf.locked", os.urandom(500000))
        r = rp.analyze(p, rp.COARSE, rp.FINE, 0)
        self.assertLess(r["recoverable_pct"], 1.0)

    def test_output_preserves_offsets(self):
        """
        Offset preservation is the whole point for offset-addressed formats.
        Nulling must not change file length or shift surviving bytes.
        """
        p = write(self.tmp, "db.mdf.umc16h", self._chunked(0.003))
        out = os.path.join(self.tmp, "recovered.mdf")
        r = rp.analyze(p, rp.COARSE, rp.FINE, 0)
        rp.write_outputs(r, out, None, False)
        orig, rec = open(p, "rb").read(), open(out, "rb").read()
        self.assertEqual(len(orig), len(rec), "output length changed; offsets shifted")
        mid = len(rec) // 4
        self.assertEqual(orig[mid:mid + 64], rec[mid:mid + 64],
                         "surviving bytes moved from their original offset")

    def test_format_guidance_present_for_known_extensions(self):
        for ext, fmt in [("mdf", "SQL MDF"), ("pst", "PST/OST"), ("log", "text")]:
            p = write(self.tmp, f"x.{ext}.locked", self._chunked(0.003))
            self.assertEqual(rp.analyze(p, rp.COARSE, rp.FINE, 0)["format"], fmt)

    def test_sparkline_shows_small_chunks(self):
        """
        BUG: sampling one byte per cell hid chunks narrower than a cell, so an
        ultrafast third chunk never appeared on the region map.
        """
        regions = [(0, 1000, "enc"), (1000, 999000, "plain"), (999000, 1000000, "enc")]
        line = rp.sparkline(regions, 1000000, width=64)
        self.assertTrue(line.startswith("\u2588"))
        self.assertTrue(line.endswith("\u2588"), "trailing small chunk not rendered")


class TestFineGrainedStriping(unittest.TestCase):
    """
    BUG: 512-byte stripes inside a 4096-byte entropy window are diluted to ~12%
    random and read as plaintext. recover_partial reported "0 bytes encrypted,
    100% recoverable" on a file with a tenth of it destroyed - it would hand back
    a corrupted database while calling it intact.
    Pattern from DeadLock (MSTIC, Aug 2026).
    """

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        size, pct = 6_000_000, 10
        total = -(-size * pct // 100)
        blocks = -(-total // 512)
        self.skip = (size - total) // blocks
        rec = b"".join(b"INSERT INTO t VALUES (%d,'ACME','48200.00');\n" % i
                       for i in range(1, 2001))
        body = bytearray((rec * 200)[:size])
        off = 0
        while off < size:
            body[off:off + 512] = os.urandom(512)
            off += 512 + self.skip
        self.path = write(self.tmp, "ledger.mdf.dlock", bytes(body))

    def test_recover_partial_detects_stripes(self):
        r = rp.analyze(self.path, rp.COARSE, rp.FINE, 0)
        self.assertTrue(r["micro_rescanned"], "coarse pass reported the file as clean")
        self.assertLess(r["recoverable_pct"], 99.0,
                        "reported ~100% recoverable on a striped file")
        self.assertGreater(r["recoverable_pct"], 50.0)

    def test_triage_flags_fine_striping(self):
        v = pf.analyze(self.path, 4096)["classification"]["verdict"]
        self.assertNotIn("NOT ENCRYPTED", v.upper())

    def test_clean_file_not_falsely_striped(self):
        """The multi-scale pass must not invent stripes in ordinary data."""
        p = write(self.tmp, "plain.txt", (b"BEGIN RECORD; customer=ACME;\n" * 40000))
        r = rp.analyze(p, rp.COARSE, rp.FINE, 0)
        self.assertFalse(r["micro_rescanned"])
        self.assertGreater(r["recoverable_pct"], 99.0)

    def test_media_not_falsely_striped(self):
        p = write(self.tmp, "photo.jpg",
                  b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + os.urandom(400000))
        self.assertIn("NOT ENCRYPTED", verdict(p).upper())


class TestCanaries(unittest.TestCase):
    """Canaries are the one non-statistical signal; they must be exactly reliable."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.share = os.path.join(self.tmp, "finance")
        os.makedirs(self.share)
        self.state = os.path.join(self.tmp, "canaries.json")
        cd.deploy([self.share], self.state, 3, False)

    def _paths(self):
        import json as j
        return [c["path"] for c in j.load(open(self.state))["canaries"]]

    def test_deploy_then_intact(self):
        self.assertEqual(cd.check(self.state, True), 0)

    def test_detects_content_encryption(self):
        with open(self._paths()[0], "wb") as fh:
            fh.write(os.urandom(4096))
        self.assertEqual(cd.check(self.state, True), 1)

    def test_detects_rename(self):
        p = self._paths()[0]
        os.rename(p, p + ".umc16h")
        self.assertEqual(cd.check(self.state, True), 1)

    def test_detects_deletion(self):
        os.remove(self._paths()[0])
        self.assertEqual(cd.check(self.state, True), 1)

    def test_names_sort_early(self):
        """
        Encryptors commonly process directory entries in returned order, roughly
        alphabetical on NTFS. A canary that sorts late is hit late and is useless
        as a tripwire.
        """
        names = sorted(os.path.basename(p) for p in self._paths())
        others = sorted(["Annual Report.docx", "budget.xlsx", "zebra.txt", "1099.pdf"])
        self.assertLess(names[0], others[0],
                        "canary does not sort before ordinary business filenames")

    def test_content_is_not_obvious_filler(self):
        with open(self._paths()[0], "rb") as fh:
            body = fh.read()
        self.assertNotIn(b"AAAA", body)
        self.assertIn(b"Confidential", body)
        self.assertGreater(len(body), 500)


class TestCapstone(unittest.TestCase):
    """The capstone must stay solvable and its traps must keep working."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.inc = os.path.join(cls.tmp, "incident")
        script = os.path.join(ROOT, "capstone/generate_incident.py")
        r = subprocess.run([sys.executable, script, "--outdir", cls.inc],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    def test_media_trap_holds(self):
        """TRAP 1: high-entropy media must not be classified as encrypted."""
        for f in ("conference_2025.mp4", "headshot_ceo.jpg", "brand_assets.zip"):
            p = os.path.join(self.inc, "fileserver", "media", f)
            with self.subTest(file=f):
                self.assertIn("NOT ENCRYPTED", verdict(p).upper())

    def test_large_files_are_distributed_chunk(self):
        p = os.path.join(self.inc, "fileserver", "finance", "ledger_2025.mdf.lksm")
        self.assertIn("DISTRIBUTED-CHUNK", verdict(p))

    def test_small_files_are_fully_encrypted(self):
        p = os.path.join(self.inc, "fileserver", "finance", "invoice_4417.xlsx.lksm")
        self.assertEqual(verdict(p), "FULL ENCRYPTION")

    def test_key_model_is_per_file(self):
        """Answer key states per-file keys; every footer must differ."""
        seen = set()
        for root, _, files in os.walk(os.path.join(self.inc, "fileserver")):
            for f in files:
                if f.endswith(".lksm"):
                    with open(os.path.join(root, f), "rb") as fh:
                        fh.seek(-70, 2)
                        seen.add(fh.read())
        self.assertGreater(len(seen), 1, "footers identical - would imply a session key")

    def test_large_file_recovery_is_substantial(self):
        p = os.path.join(self.inc, "fileserver", "finance", "ledger_2025.mdf.lksm")
        r = rp.analyze(p, rp.COARSE, rp.FINE, 70)
        self.assertGreater(r["recoverable_pct"], 85.0)

    def test_filtered_scan_refuses_to_conclude(self):
        """
        TRAP 2: --min-confidence high hides the Curve25519 marker. The tool must
        refuse to conclude rather than report 'symmetric only, decryptor plausible',
        which would tell a client recovery is likely when it is impossible.
        """
        with open(os.path.join(self.inc, "artifacts", "recovered_binary.bin"), "rb") as fh:
            data = fh.read()
        notes = " ".join(ic.interpret(ic.scan(data, "high", []), "high"))
        self.assertIn("INCONCLUSIVE", notes)
        self.assertNotIn("decryptor becomes plausible", notes)

    def test_unfiltered_scan_flags_possible_hybrid(self):
        with open(os.path.join(self.inc, "artifacts", "recovered_binary.bin"), "rb") as fh:
            data = fh.read()
        notes = " ".join(ic.interpret(ic.scan(data, "low", []), "low"))
        self.assertIn("HYBRID", notes)

    def test_backup_exists_for_one_large_file(self):
        self.assertTrue(os.path.exists(
            os.path.join(self.inc, "backups", "ledger_2025.mdf")))


class TestDemoScript(unittest.TestCase):
    """The teaching demo must stay runnable and must never overwrite an original."""

    def test_specimens_preserve_original(self):
        tmp = tempfile.mkdtemp()
        script = os.path.join(ROOT, "01-Symmetric-Cryptography/labs/encryption_demo.py")
        r = subprocess.run([sys.executable, script, "specimens", "--outdir", tmp,
                            "--force"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        orig = os.path.join(tmp, "invoice.xlsx")
        self.assertTrue(os.path.exists(orig))
        with open(orig, "rb") as fh:
            self.assertIn(b"BEGIN RECORD", fh.read(200),
                          "original was modified; demo must never destroy input")

    def test_ecb_leaks_structure(self):
        """The pedagogical claim must actually hold: ECB repeats blocks, CBC does not."""
        demo = load("encryption_demo", "01-Symmetric-Cryptography/labs/encryption_demo.py")
        img = demo.make_image()
        ecb, cbc = demo.aes_ecb(img), demo.aes_cbc(img)
        u = lambda d: len({d[i:i + 16] for i in range(0, len(d), 16)})
        self.assertLess(u(ecb), u(cbc) // 2, "ECB should collapse to few distinct blocks")
        self.assertEqual(u(cbc), len(cbc) // 16, "CBC blocks should all be distinct")


class TestRepositoryIntegrity(unittest.TestCase):
    """
    Prevents documentation drifting from reality.

    An audit found STRUCTURE.txt promising 14 files that did not exist - the same
    class of problem as dead links, and equally corrosive to trust in the repo.
    These tests make that drift fail CI instead of quietly accumulating.
    """

    def test_structure_txt_only_promises_files_that_exist(self):
        import re
        missing = []
        with open(os.path.join(ROOT, "STRUCTURE.txt"), encoding="utf-8") as fh:
            for line in fh:
                if "\U0001F4CB" in line or "📋" in line:      # explicitly marked planned
                    continue
                m = re.search(r"([A-Za-z0-9_\-]+\.(?:md|py|yar|yml|txt))", line)
                if not m:
                    continue
                name = m.group(1)
                if name in ("STRUCTURE.txt", "requirements.txt"):
                    continue
                found = any(name in files
                            for _, _, files in os.walk(ROOT))
                if not found:
                    missing.append(name)
        self.assertEqual(missing, [], f"STRUCTURE.txt promises missing files: {missing}")

    def test_no_dead_internal_links(self):
        import re
        bad = []
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d != ".git"]
            for f in files:
                if not f.endswith(".md"):
                    continue
                p = os.path.join(root, f)
                with open(p, encoding="utf-8") as fh:
                    body = fh.read()
                for link in re.findall(r"\]\((?!https?://|#|mailto:)([^)#]+)", body):
                    if not os.path.exists(os.path.normpath(os.path.join(root, link))):
                        bad.append(f"{os.path.relpath(p, ROOT)} -> {link}")
        self.assertEqual(bad, [], f"dead internal links: {bad}")

    def test_site_pages_have_valid_javascript(self):
        """
        BUG: a Python escape collapsed \\' into a bare apostrophe inside a
        single-quoted JS string, silently breaking an entire page simulation.
        Balanced-brace heuristics caught it; only a real parser proves it fixed.
        Skips cleanly where node is unavailable.
        """
        import re, shutil, subprocess, tempfile
        node = shutil.which("node")
        pages = [f for f in os.listdir(ROOT) if f.endswith(".html")]
        self.assertTrue(pages, "no site pages found")
        if not node:
            self.skipTest("node not available")
        for p in pages:
            with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
                body = fh.read()
            js = "\n".join(re.findall(r"<script>(.*?)</script>", body, re.S))
            if not js.strip():
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                             encoding="utf-8") as tf:
                tf.write(js)
                path = tf.name
            try:
                r = subprocess.run([node, "--check", path],
                                   capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{p} has invalid JS:\n{r.stderr}")
            finally:
                os.unlink(path)

    def test_site_pages_link_only_to_existing_files(self):
        import re
        bad = []
        for p in [f for f in os.listdir(ROOT) if f.endswith(".html")]:
            with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
                body = fh.read()
            for href in re.findall(r'href="(?!https?:|#|mailto:)([^"]+)"', body):
                if not os.path.exists(os.path.join(ROOT, href)):
                    bad.append(f"{p} -> {href}")
        self.assertEqual(bad, [], f"dead links in site pages: {bad}")

    def test_license_exists_and_matches_claims(self):
        """Six files claim MIT. Without a LICENSE the repo is all-rights-reserved."""
        lic = os.path.join(ROOT, "LICENSE")
        self.assertTrue(os.path.exists(lic), "LICENSE missing but files claim MIT")
        with open(lic, encoding="utf-8") as fh:
            self.assertIn("MIT License", fh.read())

    def test_detection_rules_are_wellformed(self):
        """YARA rules must have balanced braces and the required sections."""
        import re
        yars = []
        for root, dirs, files in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d != ".git"]
            yars += [os.path.join(root, f) for f in files if f.endswith(".yar")]
        self.assertTrue(yars, "no YARA rule files found")
        for p in yars:
            with open(p, encoding="utf-8") as fh:
                body = fh.read()
            with self.subTest(rule_file=os.path.basename(p)):
                self.assertEqual(body.count("{"), body.count("}"), "unbalanced braces")
                # Match only real rule declarations at line start - splitting on
                # the bare word "rule" also catches it inside header comments.
                decls = re.findall(r"(?m)^rule\s+(\w+)\s*\{", body)
                self.assertTrue(decls, "no rule declarations found")
                blocks = re.split(r"(?m)^rule\s+\w+\s*\{", body)[1:]
                for name, block in zip(decls, blocks):
                    self.assertIn("condition:", block, f"rule {name} has no condition")
                    self.assertIn("meta:", block, f"rule {name} has no meta")

    def test_sigma_rules_have_required_fields(self):
        sig = os.path.join(ROOT, "11-Endpoint-Detection", "sigma")
        files = [f for f in os.listdir(sig) if f.endswith(".yml")]
        self.assertTrue(files, "no Sigma rules found")
        for f in files:
            with open(os.path.join(sig, f), encoding="utf-8") as fh:
                body = fh.read()
            for doc in body.split("\n---\n"):
                if "title:" not in doc:
                    continue
                with self.subTest(rule_file=f, title=doc.split("title:")[1].split("\n")[0].strip()):
                    for field in ("id:", "logsource:", "detection:", "level:", "condition:"):
                        self.assertIn(field, doc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
