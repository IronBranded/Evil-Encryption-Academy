#!/usr/bin/env python3
"""
generate_incident.py - Build a synthetic ransomware incident for the capstone.

Produces a complete, self-consistent scenario on disk: an encrypted file share,
surviving backups, a ransom note, a tripped canary, a recovered encryptor binary,
and a log excerpt. Everything a responder would actually have.

NOTHING HERE IS MALICIOUS. The "encryptor" is an inert file containing crypto
constants for identification practice - it has no code and cannot run. Encrypted
files are produced by overwriting regions with random bytes, so no key exists and
nothing can be decrypted. That is deliberate: the exercise is to determine what is
RECOVERABLE, and the answer never depends on obtaining a key.

USAGE
    python3 generate_incident.py --outdir ./incident-alpha
    python3 generate_incident.py --outdir ./incident-bravo --seed 99

    Different seeds produce different file counts and sizes but the same
    underlying scheme, so the answer key stays valid.

Part of Evil-Encryption-Academy, capstone. Stdlib only. MIT licensed.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone

EXT = ".lksm"
FAMILY = "LOCKSMITH"          # fictional family - do not look it up, it isn't real
NOTE = "README-LOCKSMITH.txt"

DOC = (b"CONFIDENTIAL - Internal Use Only\r\n"
       b"Reference: {ref}\r\nPrepared by: Finance Operations\r\n\r\n"
       b"Account,Description,Amount,Status\r\n")


def rows(rnd, n):
    return b"".join(
        (f"AC-{rnd.randint(1000,9999)},Reconciliation line {i},"
         f"{rnd.randint(100,90000)}.{rnd.randint(0,99):02d},CLOSED\r\n").encode()
        for i in range(n))


def business_file(rnd, ref, n):
    return DOC.replace(b"{ref}", ref.encode()) + rows(rnd, n)


def footer(rnd):
    """Per-file ephemeral public key, base64, behind ASCII delimiters."""
    eph = bytes(rnd.getrandbits(8) for _ in range(32))
    return b"--eph--" + base64.b64encode(eph) + b"--marker--" + FAMILY.encode()


def rand_bytes(rnd, n):
    return bytes(rnd.getrandbits(8) for _ in range(n))


def encrypt_full(rnd, data):
    return rand_bytes(rnd, len(data) + (-len(data) % 16)) + footer(rnd)


def encrypt_chunked(rnd, data, pct):
    """Three chunks at head, midpoint and tail - the distributed-chunk pattern."""
    b = bytearray(data)
    n = len(b)
    clen = max(1024, int(n * pct))
    for off in (0, n // 2, max(0, n - clen)):
        b[off:off + clen] = rand_bytes(rnd, min(clen, n - off))
    return bytes(b) + footer(rnd)


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(data)


def build(out, seed):
    rnd = random.Random(seed)
    t0 = datetime(2026, 3, 14, 2, 17, 0, tzinfo=timezone.utc)
    fs = os.path.join(out, "fileserver")
    art = os.path.join(out, "artifacts")
    manifest = {"seed": seed, "generated": datetime.now(timezone.utc).isoformat()}

    # --- Large business files: distributed-chunk at 3% per chunk -------------
    large = []
    for name, ref, nrows in [("finance/ledger_2025.mdf", "FIN-2025-Q4", 90000),
                             ("finance/receivables.mdf", "FIN-AR-2025", 70000),
                             ("hr/personnel.pst", "HR-ARCHIVE-01", 80000)]:
        plain = business_file(rnd, ref, nrows)
        write(os.path.join(fs, name + EXT), encrypt_chunked(rnd, plain, 0.03))
        large.append((name, len(plain)))

    # --- Small business files: fully encrypted ------------------------------
    for name, ref in [("finance/invoice_4417.xlsx", "INV-4417"),
                      ("finance/budget_q1.xlsx", "BUD-Q1"),
                      ("hr/offer_letter.docx", "HR-OFF-88"),
                      ("hr/handbook.docx", "HR-HB-02")]:
        plain = business_file(rnd, ref, 300)
        write(os.path.join(fs, name + EXT), encrypt_full(rnd, plain))

    # --- Media: NOT encrypted. High entropy, intact headers. The trap. ------
    write(os.path.join(fs, "media/conference_2025.mp4"),
          b"\x00\x00\x00\x20ftypmp42" + rand_bytes(rnd, 3_000_000))
    write(os.path.join(fs, "media/headshot_ceo.jpg"),
          b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + rand_bytes(rnd, 900_000) + b"\xff\xd9")
    write(os.path.join(fs, "media/brand_assets.zip"),
          b"PK\x03\x04" + rand_bytes(rnd, 1_400_000))

    # --- Surviving backups: originals for two of the large files ------------
    r2 = random.Random(seed)
    r2.getrandbits(8)  # keep streams distinct
    for name, ref, nrows in [("finance/ledger_2025.mdf", "FIN-2025-Q4", 90000)]:
        rr = random.Random(seed)
        write(os.path.join(out, "backups", os.path.basename(name)),
              business_file(rr, ref, nrows))

    # --- Ransom note, dropped in each affected directory --------------------
    note = (f"YOUR NETWORK HAS BEEN ENCRYPTED BY {FAMILY}\r\n\r\n"
            "All your important files have been encrypted with military grade\r\n"
            "RSA-4048 encryption. Recovery is impossible without our private key.\r\n\r\n"
            "Do not attempt to use third party recovery software or your files\r\n"
            "will be permanently damaged.\r\n\r\n"
            "Contact: locksmith-support@[redacted].onion\r\n"
            f"Your ID: {hashlib.sha256(str(seed).encode()).hexdigest()[:16].upper()}\r\n")
    for d in ("finance", "hr", "media", ""):
        write(os.path.join(fs, d, NOTE), note.encode())

    # --- Recovered "encryptor": inert file with identifying constants -------
    binary = bytearray(b"MZ\x90\x00" + rand_bytes(rnd, 900))
    binary += b"Go build ID: \"" + base64.b64encode(rand_bytes(rnd, 20)) + b"\"\x00"
    binary += rand_bytes(rnd, 400) + b"expand 32-byte k"
    binary += rand_bytes(rnd, 200) + bytes.fromhex("41db0100")      # Curve25519 a24
    binary += rand_bytes(rnd, 150) + bytes.fromhex("ffffff0ffcffff0ffcffff0ffcffff0f")
    binary += rand_bytes(rnd, 300) + b"--marker--" + FAMILY.encode()
    binary += b"\x00garble\x00" + rand_bytes(rnd, 200)
    binary += b"\x00vssadmin delete shadows /all /quiet\x00"
    binary += b"wevtutil cl System\x00wbadmin delete catalog -quiet\x00"
    binary += rand_bytes(rnd, 500)
    write(os.path.join(art, "recovered_binary.bin"), bytes(binary))

    # --- Log excerpt --------------------------------------------------------
    ev = [
        (t0 - timedelta(minutes=44), "4624", "Successful logon: SVC_BACKUP from 10.4.2.87 (Type 3)"),
        (t0 - timedelta(minutes=41), "4688", "Process created: C:\\Windows\\Temp\\svchost32.exe (parent: cmd.exe)"),
        (t0 - timedelta(minutes=39), "4688", "Process created: vssadmin.exe delete shadows /all /quiet"),
        (t0 - timedelta(minutes=39), "4688", "Process created: wbadmin.exe delete catalog -quiet"),
        (t0 - timedelta(minutes=38), "7045", "Service installed: WinRing0x64 (kernel driver)"),
        (t0 - timedelta(minutes=2),  "1102", "The audit log was cleared"),
        (t0,                          "CANARY", "Canary tripped on \\\\FS01\\finance"),
        (t0 + timedelta(minutes=11), "4688", "Process created: wevtutil.exe cl System"),
    ]
    log = "timestamp,event_id,description\n" + "\n".join(
        f"{ts.isoformat()},{eid},\"{desc}\"" for ts, eid, desc in ev)
    write(os.path.join(art, "event_excerpt.csv"), log.encode())

    # --- Tripped canary state ----------------------------------------------
    write(os.path.join(art, "canary_state.json"), json.dumps({
        "created": (t0 - timedelta(days=90)).isoformat(),
        "canaries": [
            {"path": "\\\\FS01\\finance\\!!!-DO-NOT-MODIFY-8effb112.docx",
             "sha256": hashlib.sha256(b"baseline-1").hexdigest(), "size": 2048},
            {"path": "\\\\FS01\\hr\\!!-archive-index-3a602bf0.xlsx",
             "sha256": hashlib.sha256(b"baseline-2").hexdigest(), "size": 2048},
        ],
        "last_check": t0.isoformat(),
        "status": "TRIPPED",
        "tripped": [
            {"path": "\\\\FS01\\finance\\!!!-DO-NOT-MODIFY-8effb112.docx",
             "status": "MISSING", "note": "deleted or renamed"},
        ],
    }, indent=2).encode())

    write(os.path.join(out, "MANIFEST.json"), json.dumps(manifest, indent=2).encode())

    total = sum(len(files) for _, _, files in os.walk(out))
    print(f"\n  Incident generated: {out}")
    print(f"  {total} files across fileserver/, backups/ and artifacts/\n")
    print("  START HERE:  capstone/README.md")
    print("  Do not read SOLUTION.md until you have written your assessment.\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Generate a synthetic ransomware incident.")
    ap.add_argument("--outdir", default="./incident-alpha")
    ap.add_argument("--seed", type=int, default=1337)
    a = ap.parse_args()
    if os.path.exists(a.outdir) and os.listdir(a.outdir):
        print(f"error: {a.outdir} exists and is not empty", file=sys.stderr)
        return 2
    return build(a.outdir, a.seed)


if __name__ == "__main__":
    sys.exit(main())
