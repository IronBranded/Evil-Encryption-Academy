#!/usr/bin/env python3
"""
Generates STRUCTURE.txt from the actual repository tree.

Written because the hand-maintained version drifted badly out of date without
anything noticing: the integrity test only checked that named files exist, not
that existing files are named, so a stale map passed cleanly. Deriving the tree
from the filesystem removes that failure mode entirely — the map cannot claim
something false, because it is not written by hand.

Run:  python3 make_structure.py
"""
import os

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "lab-samples", "specimens"}
SKIP_FILES = {"STRUCTURE.txt", ".DS_Store"}

NOTES = {
    "index.html": "Academy home with live ECB hero",
    "01-what-encryption-is.html": "Encoding / hashing / signing / encryption; XOR; Kerckhoffs",
    "02-keys-and-randomness.html": "Key size, CSPRNG vs PRNG, KDFs, nonces",
    "03-hashing-and-integrity.html": "Hashes, MACs, AEAD; confidentiality vs integrity",
    "04-symmetric.html": "AES rounds and key schedule; ChaCha20 state",
    "05-modes.html": "ECB/CBC/CTR/GCM/XTS; padding; the ECB image leak",
    "06-asymmetric.html": "RSA maths, OAEP, capacity limits, ECC, ECDH",
    "07-hybrid.html": "The combined scheme; what an attacker must protect",
    "08-coverage.html": "Four coverage patterns; format fragility; fine striping",
    "09-key-models.html": "Session vs per-file; ephemeral ECDH; the zero-nonce case",
    "10-os-native.html": "Full-disk layering; protectors; key escrow",
    "11-telling-them-apart.html": "A four-question identification method; three traps",
    "reference.html": "Sizes, constants, glossary, common misconceptions",
    "engine.py": "Page template engine",
    "pages.py": "All page content — run engine.py to build",
    "svg_diagrams.py": "SVG diagram components, theme-aware",
    "make_structure.py": "Generates this file from the tree",
    "academy.css": "Shared styles including dark mode",
    "academy.js": "Crypto helpers, progress, theme, keyboard navigation",
    "favicon.svg": "Site icon",
    "card.svg": "Social preview image",
    "_nav.html": "Shared sidebar navigation",
    "test_tools.py": "Regression tests — every one exists because a bug shipped",
    "ci.yml": "Tests on Python 3.9-3.12 plus repository integrity",
    ".nojekyll": "Serve GitHub Pages as static files",
    ".gitignore": "Blocks samples, specimens and generated output",
    "LICENSE": "MIT",
    "README.md": "Repository readme",
    "SCOPE.md": "What this project covers and deliberately omits",
    "CONTRIBUTING.md": "Contribution rules",
    "CODE_OF_CONDUCT.md": "Conduct and sample-handling rules",
}

HEADER = """Evil-Encryption-Academy/
#
#  GENERATED FILE — do not edit by hand.
#  Run  python3 make_structure.py  to regenerate from the actual tree.
#
#  The previous hand-written version drifted out of date silently, because the
#  integrity test only checked that named files existed and never that existing
#  files were named. Generating it removes that whole class of error.
#
"""


def walk(root=".", prefix=""):
    entries = []
    for name in sorted(os.listdir(root)):
        if name in SKIP_DIRS or name in SKIP_FILES:
            continue
        path = os.path.join(root, name)
        entries.append((name, path, os.path.isdir(path)))
    entries.sort(key=lambda e: (not e[2], e[0].lower()))

    lines = []
    for i, (name, path, is_dir) in enumerate(entries):
        last = i == len(entries) - 1
        branch = "└── " if last else "├── "
        label = name + "/" if is_dir else name
        note = NOTES.get(name, "")
        if note:
            lines.append(f"{prefix}{branch}{label:<34}{note}")
        else:
            lines.append(f"{prefix}{branch}{label}")
        if is_dir:
            lines += walk(path, prefix + ("    " if last else "│   "))
    return lines


def main():
    body = "\n".join(walk("."))
    files = sum(1 for _, _, fs in os.walk(".")
                for f in fs
                if not any(s in _ for s in SKIP_DIRS) and f not in SKIP_FILES)
    out = HEADER + body + f"\n\n{len(body.splitlines())} entries listed.\n"
    with open("STRUCTURE.txt", "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"STRUCTURE.txt regenerated — {len(body.splitlines())} entries")


if __name__ == "__main__":
    main()
