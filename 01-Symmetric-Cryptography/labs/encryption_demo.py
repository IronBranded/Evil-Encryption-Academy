#!/usr/bin/env python3
"""
encryption_demo.py - See what encryption actually does to data.

WHY THIS EXISTS
    Module 02 asks you to triage encrypted files, but you need encrypted files
    to practise on and you should not be handling live ransomware to get them.
    This generates safe specimens and shows you the before/after so the entropy
    numbers in parse_footer.py stop being abstract.

WHAT IT DEMONSTRATES
    hexdump    Before and after: raw bytes, entropy, byte-frequency histogram
    modes      Why AES-ECB is broken, using the classic pattern-leakage result
    avalanche  Flip one bit of plaintext, watch half the ciphertext change
    specimens  Generate lab files for parse_footer.py (full/intermittent/header)
    roundtrip  Encrypt then decrypt, proving this is reversible

THIS IS A TEACHING TOOL, NOT AN ENCRYPTOR. By design:
    * The key is FIXED and PRINTED on every run. Nothing is ephemeral.
    * There is NO asymmetric key wrapping and no attacker public key.
    * The key is never destroyed. Decryption is always possible, and included.
    * Originals are NEVER overwritten, renamed, or deleted. Output is a new file.
    * Default input is synthetic data this script generates itself.

    Those four properties are precisely what separate a cryptography demo from
    ransomware. Ransomware is defined by irreversibility for the victim:
    a random key you never see, wrapped under a public key whose private half
    you will never have, then wiped from memory. None of that happens here.

USAGE
    python3 encryption_demo.py hexdump
    python3 encryption_demo.py modes
    python3 encryption_demo.py avalanche
    python3 encryption_demo.py specimens --outdir ./lab-samples
    python3 encryption_demo.py roundtrip

REQUIRES
    pip install cryptography

Part of Evil-Encryption-Academy, Module 01: Symmetric Cryptography.
MIT licensed.
"""

from __future__ import annotations

import argparse
import hashlib
import math
import os
import sys
from collections import Counter

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ImportError:
    sys.exit("error: pip install cryptography")


# ---------------------------------------------------------------------------
# Fixed demo key. Printed every run, on purpose.
# ---------------------------------------------------------------------------

DEMO_PASSPHRASE = b"evil-encryption-academy-module-01-demo-key"
DEMO_KEY = hashlib.sha256(DEMO_PASSPHRASE).digest()      # 32 bytes -> AES-256
DEMO_IV = bytes(range(16))                                # fixed, non-secret

IMG_W, IMG_H = 64, 32     # 2048 bytes, a clean multiple of the 16-byte AES block

PADLOCK = [
    "                                ",
    "            ########            ",
    "          ####    ####          ",
    "         ###        ###         ",
    "         ##          ##         ",
    "         ##          ##         ",
    "         ##          ##         ",
    "      ####################      ",
    "      ####################      ",
    "      #########  #########      ",
    "      ########    ########      ",
    "      ########    ########      ",
    "      #########  #########      ",
    "      #########  #########      ",
    "      ####################      ",
    "                                ",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def shannon(data: bytes) -> float:
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def aes_ecb(data: bytes) -> bytes:
    enc = Cipher(algorithms.AES(DEMO_KEY), modes.ECB()).encryptor()
    return enc.update(data) + enc.finalize()


def aes_cbc(data: bytes, iv: bytes = DEMO_IV) -> bytes:
    enc = Cipher(algorithms.AES(DEMO_KEY), modes.CBC(iv)).encryptor()
    return enc.update(data) + enc.finalize()


def aes_cbc_decrypt(data: bytes, iv: bytes = DEMO_IV) -> bytes:
    dec = Cipher(algorithms.AES(DEMO_KEY), modes.CBC(iv)).decryptor()
    return dec.update(data) + dec.finalize()


def pad16(data: bytes) -> bytes:
    """PKCS#7."""
    n = 16 - (len(data) % 16)
    return data + bytes([n]) * n


def unpad16(data: bytes) -> bytes:
    return data[:-data[-1]]


def hexdump(data: bytes, length: int = 128, base: int = 0) -> str:
    out = []
    for off in range(0, min(len(data), length), 16):
        chunk = data[off:off + 16]
        hexs = " ".join(f"{b:02x}" for b in chunk).ljust(47)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        out.append(f"  {base + off:08x}  {hexs}  |{text}|")
    return "\n".join(out)


def histogram(data: bytes, buckets: int = 32, height: int = 6) -> str:
    """ASCII byte-frequency distribution. Flat = random. Spiky = structured."""
    counts = [0] * buckets
    span = 256 // buckets
    for b in data:
        counts[b // span] += 1
    peak = max(counts) or 1
    rows = []
    for lvl in range(height, 0, -1):
        row = "".join("█" if c / peak * height >= lvl else " " for c in counts)
        rows.append("  |" + row + "|")
    rows.append("  +" + "-" * buckets + "+")
    rows.append("   0x00" + " " * (buckets - 9) + "0xFF")
    return "\n".join(rows)


def render(data: bytes, w: int = IMG_W, h: int = IMG_H) -> list:
    """Map bytes to blocks so we can 'see' the buffer."""
    return ["".join("█" if data[y * w + x] >= 128 else "·" for x in range(w))
            for y in range(h)]


BLOCK_PALETTE = " ·:-=+*#%@█"


def render_blockmap(data: bytes, w: int = IMG_W, h: int = IMG_H) -> list:
    """
    Render each 16-byte AES block as one uniform shade keyed to its CONTENT.

    Two blocks get the same shade if and only if they are byte-identical.
    This visualizes the single property that breaks ECB: identical plaintext
    blocks encrypt to identical ciphertext blocks, so uniform regions of the
    original stay uniform in the output and the shape leaks straight through.
    """
    rows = []
    for y in range(h):
        row = data[y * w:(y + 1) * w]
        line = ""
        for i in range(0, len(row), 16):
            blk = row[i:i + 16]
            shade = BLOCK_PALETTE[hashlib.sha256(blk).digest()[0] % len(BLOCK_PALETTE)]
            line += shade * 16
        rows.append(line)
    return rows


def side_by_side(left: list, right: list, lt: str, rt: str, gap: str = "    ") -> str:
    out = [f"  {lt.ljust(len(left[0]))}{gap}{rt}"]
    for a, b in zip(left, right):
        out.append(f"  {a}{gap}{b}")
    return "\n".join(out)


def make_image() -> bytes:
    """2x upscale of the padlock template into a 64x32 byte buffer."""
    buf = bytearray()
    for row in PADLOCK:
        line = bytes(0xFF if ch == "#" else 0x00 for ch in row for _ in range(2))
        buf += line * 2
    return bytes(buf)


def banner(title: str) -> None:
    print("\n" + "=" * 74)
    print(f"  {title}")
    print("=" * 74)


def key_notice() -> None:
    print(f"  Demo key (AES-256, FIXED and PUBLIC): {DEMO_KEY.hex()}")
    print(f"  Demo IV:                              {DEMO_IV.hex()}")
    print("  Nothing here is secret. That is the point - every step is reversible.\n")


# ---------------------------------------------------------------------------
# Demo 1: before and after
# ---------------------------------------------------------------------------

def demo_hexdump(_args) -> None:
    banner("DEMO 1 - BEFORE AND AFTER")
    key_notice()

    plaintext = (
        b"INVOICE #2024-0417\r\n"
        b"Customer: Acme Industrial Ltd\r\n"
        b"Amount Due: 48,200.00 GBP\r\n"
        b"Status: UNPAID\r\n"
        b"Account: 8812-4417-9930\r\n"
    ) * 4
    ciphertext = aes_cbc(pad16(plaintext))

    print("  BEFORE - plaintext")
    print(hexdump(plaintext, 96))
    print(f"\n    entropy    {shannon(plaintext):.3f} / 8.000")
    print("    byte distribution:")
    print(histogram(plaintext))
    print("    Spiky. Real data clusters - ASCII letters, digits, whitespace.")
    print("    You can read the content straight out of the hex dump.\n")

    print("  " + "-" * 70 + "\n")

    print("  AFTER - AES-256-CBC")
    print(hexdump(ciphertext, 96))
    print(f"\n    entropy    {shannon(ciphertext):.3f} / 8.000")
    print("    byte distribution:")
    print(histogram(ciphertext))
    print("    Flat. Every byte value now occurs about equally often.")
    print("    No structure, no readable strings, no recoverable meaning.\n")

    print(f"  Size before: {len(plaintext):,} bytes")
    print(f"  Size after:  {len(ciphertext):,} bytes  "
          f"(+{len(ciphertext) - len(plaintext)} bytes of PKCS#7 padding)")
    print("\n  THE TAKEAWAY")
    print("  Encryption does not compress, shrink, or scramble in place. It maps")
    print("  structured data onto output indistinguishable from random noise. That")
    print("  flat histogram IS the high entropy score parse_footer.py measures.")


# ---------------------------------------------------------------------------
# Demo 2: why ECB is broken
# ---------------------------------------------------------------------------

def demo_modes(_args) -> None:
    banner("DEMO 2 - WHY MODE OF OPERATION MATTERS")
    key_notice()

    img = make_image()
    ecb = aes_ecb(img)
    cbc = aes_cbc(img)

    print("  A 64x32 buffer holding a simple image. Every byte is 0x00 or 0xFF.")
    print("  Below, each 16-byte AES block is drawn as ONE uniform shade, keyed to")
    print("  its contents. Same shade means byte-identical block.\n")

    print(side_by_side(render_blockmap(img), render_blockmap(ecb),
                       "PLAINTEXT BLOCKS", "AES-256-ECB  <-- shape leaks through"))
    print()
    print(side_by_side(render_blockmap(cbc), render(img),
                       "AES-256-CBC  <-- no structure", "(plaintext, for reference)"))

    print(f"\n    plaintext entropy    {shannon(img):.3f}")
    print(f"    ECB entropy          {shannon(ecb):.3f}")
    print(f"    CBC entropy          {shannon(cbc):.3f}")

    blocks_ecb = len(set(ecb[i:i + 16] for i in range(0, len(ecb), 16)))
    blocks_cbc = len(set(cbc[i:i + 16] for i in range(0, len(cbc), 16)))
    total = len(img) // 16
    print(f"\n    distinct 16-byte blocks, ECB: {blocks_ecb:>3} of {total}")
    print(f"    distinct 16-byte blocks, CBC: {blocks_cbc:>3} of {total}")

    print("\n  WHAT HAPPENED")
    print("  ECB encrypts each 16-byte block independently, so identical plaintext")
    print("  blocks always produce identical ciphertext blocks. Every run of")
    print("  background encrypts to the same thing, so the shape survives.")
    print("  CBC chains each block into the next, so identical input blocks")
    print("  produce different output. The structure is destroyed.")
    print("\n  Note the entropy scores: ECB scores HIGH and is still broken.")
    print("  High entropy means 'looks random'. It does not mean 'secure'.")
    print("  This is the most common misreading of an entropy number in DFIR.")


# ---------------------------------------------------------------------------
# Demo 3: avalanche effect
# ---------------------------------------------------------------------------

def demo_avalanche(_args) -> None:
    banner("DEMO 3 - THE AVALANCHE EFFECT")
    key_notice()

    a = pad16(b"Transfer 1000.00 GBP to account 4417" + b" " * 28)
    b_ = bytearray(a)
    b_[0] ^= 0x01                      # flip exactly one bit
    b_ = bytes(b_)

    ca, cb = aes_cbc(a), aes_cbc(b_)

    print(f"  Plaintext A : {a[:36]!r}")
    print(f"  Plaintext B : {b_[:36]!r}")
    print("  Difference  : one single bit, in the first byte\n")

    print("  Ciphertext A:")
    print(hexdump(ca, 48))
    print("\n  Ciphertext B:")
    print(hexdump(cb, 48))

    diff_bits = sum(bin(x ^ y).count("1") for x, y in zip(ca, cb))
    diff_bytes = sum(1 for x, y in zip(ca, cb) if x != y)
    total_bits = len(ca) * 8

    print(f"\n    bytes changed : {diff_bytes} of {len(ca)}")
    print(f"    bits changed  : {diff_bits} of {total_bits} "
          f"({diff_bits / total_bits:.1%})")

    print("\n  WHAT HAPPENED")
    print("  One flipped input bit changed roughly half of every output bit.")
    print("  That is the avalanche property, and it is why you cannot chip away")
    print("  at ciphertext. There is no partial progress and no 'close enough'.")
    print("  Guessing 255 of 256 key bits correctly gets you nothing at all.")


# ---------------------------------------------------------------------------
# Demo 4: lab specimens
# ---------------------------------------------------------------------------

def demo_specimens(args) -> None:
    banner("DEMO 4 - GENERATING LAB SPECIMENS FOR parse_footer.py")
    key_notice()

    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    record = (b"BEGIN RECORD; customer=ACME; invoice=2024-0417; "
              b"amount=48200.00; status=UNPAID; END RECORD\n")
    original = record * 400
    orig_path = os.path.join(outdir, "invoice.xlsx")

    with open(orig_path, "wb") as fh:
        fh.write(original)

    # Footer filler. NOT a wrapped key - this script performs no asymmetric
    # operations. It is random padding sized like an RSA-2048 ciphertext so
    # parse_footer.py has a realistic tail to identify during triage practice.
    footer = os.urandom(256)

    specimens = []

    # (a) full encryption
    full = aes_cbc(pad16(original)) + footer
    specimens.append(("invoice.xlsx.full-enc", full,
                      "every byte encrypted"))

    # (b) intermittent - alternating 4 KB encrypted / 4 KB untouched
    chunks, step = [], 4096
    for i in range(0, len(original), step):
        piece = original[i:i + step]
        chunks.append(aes_cbc(pad16(piece))[:len(piece)]
                      if (i // step) % 2 == 0 else piece)
    inter = b"".join(chunks)
    inter += b"\x00" * (-len(inter) % 16)
    specimens.append(("invoice.xlsx.intermittent", inter + footer,
                      "alternating encrypted/plaintext bands"))

    # (c) header-only
    head = aes_cbc(pad16(original[:4096]))[:4096]
    specimens.append(("invoice.xlsx.header-only", head + original[4096:] + footer,
                      "first 4 KB encrypted only"))

    print(f"  Original written: {orig_path}  ({len(original):,} bytes)\n")
    for name, data, desc in specimens:
        path = os.path.join(outdir, name)
        if os.path.exists(path) and not args.force:
            print(f"  SKIP  {name}  (exists; use --force)")
            continue
        with open(path, "wb") as fh:
            fh.write(data)
        print(f"  WROTE {name:<28} {len(data):>8,} bytes   entropy "
              f"{shannon(data):.3f}   {desc}")

    print("\n  The original was copied, never modified. Now triage them:\n")
    print(f"    python3 ../../02-Hybrid-Encryption-Model/labs/parse_footer.py \\")
    print(f"        {outdir} --recurse")
    print(f"\n    python3 ../../02-Hybrid-Encryption-Model/labs/parse_footer.py \\")
    print(f"        {outdir}/invoice.xlsx.full-enc --original {orig_path}")
    print("\n  Predict each verdict before you run it. Then check whether the tool")
    print("  agrees, and work out why when it does not.")


# ---------------------------------------------------------------------------
# Demo 5: roundtrip
# ---------------------------------------------------------------------------

def demo_roundtrip(_args) -> None:
    banner("DEMO 5 - ROUNDTRIP: THIS IS REVERSIBLE")
    key_notice()

    original = b"The quick brown fox jumps over the lazy dog. " * 3
    ct = aes_cbc(pad16(original))
    recovered = unpad16(aes_cbc_decrypt(ct))

    print(f"  original   {original[:60]!r}...")
    print(f"  encrypted  {ct[:30].hex()}...")
    print(f"  decrypted  {recovered[:60]!r}...")
    print(f"\n  byte-for-byte identical: {original == recovered}")
    print(f"  sha256 before: {hashlib.sha256(original).hexdigest()}")
    print(f"  sha256 after:  {hashlib.sha256(recovered).hexdigest()}")

    print("\n  WHY THIS MATTERS")
    print("  Encryption is a reversible transformation. It is not damage and it")
    print("  is not deletion. The file is fully intact; it is just unreadable")
    print("  without the key.")
    print("\n  A ransomware victim is in exactly this position with one difference:")
    print("  the key is not printed at the top of the screen. It was random, it")
    print("  was wrapped under a public key whose private half sits on attacker")
    print("  infrastructure, and it was wiped from RAM.")
    print("\n  That gap - between a key you have and a key you do not - is the")
    print("  entire incident. It is also why memory acquisition matters so much:")
    print("  see Module 02, section 6.")


# ---------------------------------------------------------------------------

DEMOS = {
    "hexdump": demo_hexdump,
    "modes": demo_modes,
    "avalanche": demo_avalanche,
    "specimens": demo_specimens,
    "roundtrip": demo_roundtrip,
}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="See what encryption does to data. Teaching tool; key is fixed and printed.",
    )
    ap.add_argument("demo", choices=list(DEMOS) + ["all"])
    ap.add_argument("--outdir", default="./lab-samples",
                    help="output directory for the specimens demo")
    ap.add_argument("--force", action="store_true", help="overwrite existing specimens")
    args = ap.parse_args()

    if args.demo == "all":
        for name, fn in DEMOS.items():
            if name != "specimens":
                fn(args)
    else:
        DEMOS[args.demo](args)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
