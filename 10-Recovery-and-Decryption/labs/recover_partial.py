#!/usr/bin/env python3
"""
recover_partial.py - Extract surviving plaintext from partially encrypted files.

WHY THIS EXISTS
    Fast ransomware families encrypt only a fraction of large files. The Gentlemen
    at --ultrafast encrypts roughly 0.9% of a large file, leaving ~99% untouched.
    Akira, BlackCat, LockBit and Play all ship comparable modes. Those percentages
    are chosen to destroy file STRUCTURE at minimum I/O cost - not to destroy data.

    So the data is still there. This tool finds it and gets it out, with no key
    and no cooperation from the attacker.

WHAT IT DOES
    1. Maps encrypted vs plaintext regions by entropy, refining boundaries to
       byte-level precision.
    2. Reports exactly how much is recoverable and the largest contiguous run.
    3. Extracts it three ways, for three different downstream jobs:
         --out        offset-preserving image, encrypted regions nulled
         --fragments  each surviving run as its own file
         --strings    readable text pulled from surviving regions
    4. Gives format-specific repair guidance.

    OFFSET PRESERVATION IS THE IMPORTANT ONE. Most structured formats (PST, MDF,
    VMDK, PDF) are offset-addressed: internal pointers reference absolute
    positions. Nulling the damaged regions instead of removing them keeps every
    surviving pointer valid, so format repair tools can still parse the file.
    Concatenating the good fragments destroys that and is usually the wrong move.

USAGE
    python3 recover_partial.py locked.mdf
    python3 recover_partial.py locked.mdf --out recovered.mdf
    python3 recover_partial.py locked.pst --fragments ./runs --strings
    python3 recover_partial.py locked.dat --footer 256      # ignore a known footer

SAFETY
    Read-only on the input. Never writes to, renames, or deletes the source.
    ALWAYS work on a copy of evidence.

Part of Evil-Encryption-Academy, Module 10. Stdlib only. MIT licensed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter

COARSE = 4096          # first-pass window
FINE = 256             # boundary refinement granularity
HIGH = 0.94            # normalized entropy: looks like ciphertext
MIN_RUN = 512          # ignore plaintext runs shorter than this
PRINTABLE = re.compile(rb"[\x20-\x7e\t\r\n]{6,}")

_BASELINE = [(32, 4.880), (33, 4.929), (64, 5.765), (65, 5.783), (128, 6.550),
             (256, 7.177), (384, 7.444), (512, 7.592), (1024, 7.809),
             (2048, 7.909), (4096, 7.954), (8192, 7.977), (16384, 7.989)]

FORMAT_GUIDANCE = {
    "text": ("EXCELLENT", "Every surviving byte is directly usable. Logs, CSV, SQL dumps "
             "and source code recover essentially in full."),
    "PST/OST": ("GOOD", "Record-structured and offset-addressed. Null the damaged regions and "
                "run a PST repair tool (scanpst). Individual messages outside the damaged "
                "regions usually recover intact."),
    "VMDK/VHD": ("GOOD", "Often sparse, and the guest filesystem inside is largely independent. "
                 "Null damaged regions, then carve files from the guest filesystem directly. "
                 "Damage is usually confined to a small number of guest files."),
    "SQL MDF": ("MODERATE", "8KB page structure. Intact pages remain individually parseable. "
                "Null damaged regions, then extract page-by-page. Expect header damage to "
                "prevent a normal ATTACH; a page-level extractor is the route."),
    "PDF": ("MODERATE", "Object-structured with an xref table at the END. If the tail is "
            "damaged the xref is gone, but objects can be rebuilt by scanning for 'obj' "
            "markers. Many repair tools do this automatically."),
    "ZIP/OOXML": ("POOR TO MODERATE", "Central directory sits at the END of the file. If the "
                  "tail is encrypted, the index is gone - but individual members can still be "
                  "carved by scanning for local file headers (PK\\x03\\x04)."),
    "JPEG": ("POOR", "Entropy-coded and sequentially dependent. Damage early in the scan "
             "corrupts everything after it. If only the tail is damaged, the top portion of "
             "the image may render."),
    "MP4/MOV": ("VARIES", "Depends entirely on whether the 'moov' atom survived. If it did, "
                "undamaged samples play. If not, use an untruncate tool with a reference file "
                "from the same camera or encoder."),
    "unknown": ("UNKNOWN", "Identify the format first. Offset-addressed and record-structured "
                "formats recover well; sequentially-dependent compressed formats do not."),
}

EXT_MAP = {
    "txt": "text", "log": "text", "csv": "text", "tsv": "text", "sql": "text",
    "json": "text", "xml": "text", "md": "text", "py": "text", "c": "text", "h": "text",
    "pst": "PST/OST", "ost": "PST/OST",
    "vmdk": "VMDK/VHD", "vhd": "VMDK/VHD", "vhdx": "VMDK/VHD", "vdi": "VMDK/VHD",
    "mdf": "SQL MDF", "ndf": "SQL MDF", "ldf": "SQL MDF",
    "pdf": "PDF", "zip": "ZIP/OOXML", "docx": "ZIP/OOXML", "xlsx": "ZIP/OOXML",
    "pptx": "ZIP/OOXML", "jpg": "JPEG", "jpeg": "JPEG",
    "mp4": "MP4/MOV", "mov": "MP4/MOV",
}


def shannon(d: bytes) -> float:
    if not d:
        return 0.0
    c = Counter(d)
    n = len(d)
    return -sum((x / n) * math.log2(x / n) for x in c.values())


def baseline(n: int) -> float:
    if n <= 0:
        return 0.0
    if n <= _BASELINE[0][0]:
        return math.log2(min(n, 256))
    if n >= _BASELINE[-1][0]:
        return 8.0
    for (x0, y0), (x1, y1) in zip(_BASELINE, _BASELINE[1:]):
        if x0 <= n <= x1:
            t = (math.log2(n) - math.log2(x0)) / (math.log2(x1) - math.log2(x0))
            return y0 + t * (y1 - y0)
    return 8.0


def norm(d: bytes) -> float:
    b = baseline(len(d))
    return shannon(d) / b if b else 0.0


def map_regions(data: bytes, coarse: int, fine: int) -> list:
    """
    Return [(start, end, 'enc'|'plain'), ...] covering the whole file.

    Two passes. The coarse pass finds approximate regions cheaply; the fine pass
    walks each boundary at higher resolution. Boundary precision matters directly:
    every byte misclassified as encrypted is a byte of recoverable data thrown away.
    """
    n = len(data)
    if n == 0:
        return []

    coarse_lbl = [("enc" if norm(data[i:i + coarse]) >= HIGH else "plain")
                  for i in range(0, n, coarse)]

    regions, start, cur = [], 0, coarse_lbl[0]
    for idx in range(1, len(coarse_lbl)):
        if coarse_lbl[idx] != cur:
            regions.append([start, idx * coarse, cur])
            start, cur = idx * coarse, coarse_lbl[idx]
    regions.append([start, n, cur])

    # Refine each internal boundary at `fine` granularity
    for i in range(len(regions) - 1):
        b = regions[i][1]
        lo, hi = max(0, b - coarse), min(n, b + coarse)
        want = regions[i + 1][2]
        pos = b
        for off in range(lo, hi, fine):
            chunk = data[off:off + fine]
            if len(chunk) < fine:
                break
            lbl = "enc" if norm(chunk) >= HIGH else "plain"
            if lbl == want:
                pos = off
                break
        regions[i][1] = regions[i + 1][0] = pos

    return [tuple(r) for r in regions if r[1] > r[0]]


MICRO = 512          # finest stripe size observed in the wild
MICRO_TRIGGER = 0.985  # coarse pass found essentially nothing


def micro_stripe_fraction(data: bytes, sample: int = 400) -> float:
    """
    Sample MICRO-sized windows and report what fraction look like ciphertext.

    Fine-grained striping defeats coarse entropy windows by dilution. DeadLock
    (MSTIC, Aug 2026) encrypts 512-byte blocks at computed intervals - on a
    40 MB file at its 10% rule that is 512 encrypted bytes every 4,607. Inside a
    4096-byte window that is ~12% random and ~88% plaintext, which normalizes
    well below any ciphertext threshold. The coarse pass reports the file as
    completely clean while 10% of it is destroyed.
    """
    n = len(data)
    if n < MICRO * 4:
        return 0.0
    step = max(MICRO, n // sample)
    hits = checked = 0
    for off in range(0, n - MICRO, step):
        checked += 1
        if norm(data[off:off + MICRO]) >= HIGH:
            hits += 1
    return hits / checked if checked else 0.0


def analyze(path: str, coarse: int, fine: int, footer: int) -> dict:
    with open(path, "rb") as fh:
        data = fh.read()

    body = data[:-footer] if footer and len(data) > footer else data
    regions = map_regions(body, coarse, fine)
    plain = [r for r in regions if r[2] == "plain" and (r[1] - r[0]) >= MIN_RUN]
    recovered = sum(e - s for s, e, _ in plain)

    # Multi-scale check. If the coarse pass found almost nothing encrypted,
    # verify at MICRO resolution before reporting the file as clean - otherwise
    # fine-grained striping is invisible and we hand back corrupted data while
    # calling it intact.
    micro_frac, rescanned = 0.0, False
    if body and recovered / len(body) >= MICRO_TRIGGER:
        micro_frac = micro_stripe_fraction(body)
        if micro_frac >= 0.02:
            regions = map_regions(body, MICRO, MICRO)
            plain = [r for r in regions if r[2] == "plain" and (r[1] - r[0]) >= MICRO]
            recovered = sum(e - s for s, e, _ in plain)
            rescanned = True

    ext = os.path.basename(path).split(".")
    fmt = "unknown"
    for part in reversed(ext):
        if part.lower() in EXT_MAP:
            fmt = EXT_MAP[part.lower()]
            break

    return {
        "path": path, "size": len(data), "body_size": len(body),
        "footer_skipped": footer, "regions": regions, "plain_runs": plain,
        "recoverable_bytes": recovered,
        "recoverable_pct": (recovered / len(body) * 100) if body else 0.0,
        "largest_run": max((e - s for s, e, _ in plain), default=0),
        "format": fmt, "data": data, "body": body,
        "micro_stripe_fraction": round(micro_frac, 4), "micro_rescanned": rescanned,
    }


def write_outputs(r: dict, out: str, fragdir: str, dump_strings: bool) -> list:
    made = []
    body = r["body"]

    if out:
        # Offset-preserving: null the damaged regions, keep everything else in place.
        buf = bytearray(body)
        for s, e, kind in r["regions"]:
            if kind == "enc":
                buf[s:e] = b"\x00" * (e - s)
        with open(out, "wb") as fh:
            fh.write(bytes(buf))
        made.append(out)

    if fragdir:
        os.makedirs(fragdir, exist_ok=True)
        for i, (s, e, _) in enumerate(r["plain_runs"]):
            p = os.path.join(fragdir, f"run_{i:03d}_0x{s:08x}-0x{e:08x}.bin")
            with open(p, "wb") as fh:
                fh.write(body[s:e])
            made.append(p)

    if dump_strings:
        p = (out or r["path"]) + ".strings.txt"
        with open(p, "w", encoding="utf-8", errors="replace") as fh:
            for s, e, _ in r["plain_runs"]:
                for m in PRINTABLE.finditer(body[s:e]):
                    fh.write(m.group().decode("ascii", "replace") + "\n")
        made.append(p)

    return made


def sparkline(regions: list, total: int, width: int = 64) -> str:
    """
    One cell is marked encrypted if ANY encrypted region overlaps it.

    Sampling a single byte per cell hides small chunks entirely: at ultrafast
    percentages a chunk can be far narrower than one cell, and a responder
    reading the map would never see that third region exists.
    """
    enc = [(s, e) for s, e, k in regions if k == "enc"]
    cells = []
    for i in range(width):
        lo = int(i / width * total)
        hi = max(lo + 1, int((i + 1) / width * total))
        cells.append("█" if any(s < hi and e > lo for s, e in enc) else "·")
    return "".join(cells)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Extract surviving plaintext from a partially encrypted file.",
        epilog="Read-only on input. Always work on a COPY of evidence.")
    ap.add_argument("target")
    ap.add_argument("--out", help="offset-preserving output; encrypted regions nulled")
    ap.add_argument("--fragments", metavar="DIR", help="write each surviving run separately")
    ap.add_argument("--strings", action="store_true", help="dump readable text")
    ap.add_argument("--footer", type=int, default=0, help="bytes of known footer to ignore")
    ap.add_argument("--block", type=int, default=COARSE)
    ap.add_argument("--fine", type=int, default=FINE)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.target):
        print(f"error: not a file: {a.target}", file=sys.stderr)
        return 2

    r = analyze(a.target, a.block, a.fine, a.footer)

    if a.json:
        r.pop("data"); r.pop("body")
        print(json.dumps(r, indent=2, default=str))
        return 0

    print("=" * 74)
    print(f"  PARTIAL RECOVERY - {r['path']}")
    print(f"  {r['size']:,} bytes" +
          (f"  ({r['footer_skipped']} byte footer excluded)" if r["footer_skipped"] else ""))
    print("=" * 74)

    print(f"\nREGION MAP")
    print(f"  {sparkline(r['regions'], r['body_size'])}")
    print("  █ encrypted    · surviving plaintext\n")

    enc = r["body_size"] - r["recoverable_bytes"]
    print(f"  encrypted    {enc:>12,} bytes  ({100 - r['recoverable_pct']:5.1f}%)")
    print(f"  RECOVERABLE  {r['recoverable_bytes']:>12,} bytes  ({r['recoverable_pct']:5.1f}%)")
    print(f"  runs         {len(r['plain_runs']):>12,}   largest {r['largest_run']:,} bytes")

    if r.get("micro_rescanned"):
        print(f"\n  ** FINE-GRAINED STRIPING DETECTED ** "
              f"({r['micro_stripe_fraction']:.1%} of {MICRO}-byte windows are ciphertext)")
        print(f"  The coarse pass reported this file as clean. Re-mapped at {MICRO}-byte")
        print("  resolution. Damage is spread in narrow stripes rather than blocks, so")
        print("  the surviving runs are short and MOST FILE FORMATS WILL NOT SURVIVE IT")
        print("  even at a high recoverable percentage. Verify before promising recovery.")

    if r["recoverable_pct"] < 1:
        print("\n  Essentially fully encrypted. Partial recovery is not viable here;")
        print("  pursue key recovery (Module 07) or backups instead.")
    else:
        verdict, advice = FORMAT_GUIDANCE[r["format"]]
        print(f"\nFORMAT: {r['format']}   OUTLOOK: {verdict}")
        for line in [advice[i:i + 66] for i in range(0, len(advice), 66)]:
            print(f"  {line}")

    made = write_outputs(r, a.out, a.fragments, a.strings)
    if made:
        print("\nWROTE")
        for p in made:
            print(f"  {p}  ({os.path.getsize(p):,} bytes)")
        if a.out:
            print("\n  Encrypted regions were NULLED, not removed, so every byte in the")
            print("  output sits at its original offset. Internal pointers still resolve.")
            print("  Do NOT concatenate the fragments instead - that shifts offsets and")
            print("  breaks format repair for offset-addressed files.")
    else:
        print("\n  (analysis only - pass --out, --fragments or --strings to extract)")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
