#!/usr/bin/env python3
"""
canary_deploy.py - Deploy and verify ransomware canary (decoy) files.

WHAT A CANARY IS
    A file that exists only to be attacked. No legitimate process should ever
    write to it, so ANY modification is a high-confidence signal - no entropy
    threshold, no rate heuristic, no tuning.

WHY IT COMPLEMENTS EDR
    Every behavioural signal an EDR uses (file-change rate, entropy delta,
    extension mismatch) is a statistical judgement that must be tuned against
    backup software, media encoders and compression tools doing similar things.
    A canary is not statistical. It is binary and it is nearly false-positive
    free, which makes it useful precisely where EDR is weakest:

      * Encryption over SMB, where writes land on a file server that may have
        no agent installed.
      * LOTL encryption, where the writing process is a signed Microsoft binary.
      * A tampered or unloaded agent.

    It is an early-warning tripwire, NOT a replacement for EDR. It tells you
    something is wrong. It does not stop it.

USAGE
    python3 canary_deploy.py deploy /srv/share1 /srv/share2 --state canaries.json
    python3 canary_deploy.py check --state canaries.json
    python3 canary_deploy.py check --state canaries.json --json    # for monitoring
    python3 canary_deploy.py remove --state canaries.json

    Exit codes for `check`:  0 = intact,  1 = TRIPPED,  2 = error

    Run `check` on a schedule (cron / scheduled task) and alert on exit code 1.

Part of Evil-Encryption-Academy, Module 11. Stdlib only. MIT licensed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from datetime import datetime, timezone

# Names chosen to sort early in a directory listing. Many encryptors enumerate
# with FindFirstFile/FindNextFile and process in the order returned, which on
# NTFS is roughly alphabetical - so an early-sorting name is hit early, which is
# the entire point of a tripwire.
CANARY_NAMES = [
    "!!!-DO-NOT-MODIFY-{tag}.docx",
    "!!-archive-index-{tag}.xlsx",
    "!-payroll-backup-{tag}.docx",
    "0000-accounts-{tag}.xlsx",
    "AAA-contracts-{tag}.docx",
]

# Realistic-looking content. A canary containing obvious filler is a canary an
# operator can recognise and skip.
FILLER = (
    "Confidential - Internal Use Only\r\n"
    "Document reference: {ref}\r\n"
    "Prepared by: Finance Operations\r\n"
    "Review cycle: quarterly\r\n\r\n"
    "Account,Description,Amount,Status\r\n"
)


def _content(tag: str, n: int = 40) -> bytes:
    rnd = random.Random(tag)
    body = FILLER.format(ref=tag.upper())
    for i in range(n):
        body += (f"AC-{rnd.randint(1000, 9999)},Quarterly reconciliation line {i},"
                 f"{rnd.randint(100, 90000)}.{rnd.randint(0, 99):02d},CLOSED\r\n")
    return body.encode("utf-8")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def deploy(dirs: list, state_path: str, per_dir: int, hide: bool) -> int:
    entries, failed = [], 0
    for d in dirs:
        if not os.path.isdir(d):
            print(f"  SKIP {d} (not a directory)", file=sys.stderr)
            failed += 1
            continue
        for i in range(min(per_dir, len(CANARY_NAMES))):
            tag = hashlib.sha256(f"{d}{i}".encode()).hexdigest()[:8]
            path = os.path.join(d, CANARY_NAMES[i].format(tag=tag))
            try:
                with open(path, "wb") as fh:
                    fh.write(_content(tag))
                if hide and os.name == "nt":
                    os.system(f'attrib +h "{path}"')
                entries.append({
                    "path": os.path.abspath(path),
                    "sha256": sha256(path),
                    "size": os.path.getsize(path),
                    "deployed": datetime.now(timezone.utc).isoformat(),
                })
                print(f"  deployed {path}")
            except OSError as e:
                print(f"  FAILED {path}: {e}", file=sys.stderr)
                failed += 1

    with open(state_path, "w") as fh:
        json.dump({"created": datetime.now(timezone.utc).isoformat(),
                   "canaries": entries}, fh, indent=2)

    print(f"\n  {len(entries)} canaries deployed across {len(dirs)} location(s)")
    print(f"  state: {state_path}")
    print("\n  NEXT STEPS")
    print("  1. Exclude these paths from backup jobs and file-integrity noise.")
    print("  2. Schedule `check` (every 5-15 min) and alert on exit code 1.")
    print("  3. Keep the state file OFF the monitored shares - if it is encrypted")
    print("     too you lose the baseline at the moment you need it.")
    return 2 if failed and not entries else 0


def check(state_path: str, as_json: bool) -> int:
    try:
        with open(state_path) as fh:
            state = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: cannot read state: {e}", file=sys.stderr)
        return 2

    intact, tripped = [], []
    for c in state["canaries"]:
        p = c["path"]
        if not os.path.exists(p):
            tripped.append({**c, "status": "MISSING",
                            "note": "deleted or renamed - both are ransomware behaviour"})
            continue
        try:
            now = sha256(p)
        except OSError as e:
            tripped.append({**c, "status": "UNREADABLE", "note": str(e)})
            continue
        if now != c["sha256"]:
            tripped.append({**c, "status": "MODIFIED", "observed_sha256": now,
                            "observed_size": os.path.getsize(p),
                            "note": "content changed - no legitimate process writes here"})
        else:
            intact.append(p)

    result = {"checked": datetime.now(timezone.utc).isoformat(),
              "total": len(state["canaries"]), "intact": len(intact),
              "tripped": tripped, "status": "TRIPPED" if tripped else "OK"}

    if as_json:
        print(json.dumps(result, indent=2))
        return 1 if tripped else 0

    if not tripped:
        print(f"  OK - {len(intact)}/{result['total']} canaries intact")
        return 0

    print("=" * 70)
    print(f"  *** CANARY TRIPPED *** {len(tripped)} of {result['total']} affected")
    print("=" * 70)
    for t in tripped:
        print(f"\n  [{t['status']}] {t['path']}")
        print(f"     {t['note']}")
    print("\n  THIS IS A HIGH-CONFIDENCE SIGNAL. No legitimate process writes here.")
    print("\n  IMMEDIATE ACTIONS - see FIRST-60-MINUTES.md")
    print("   1. Identify which host is writing to this share. Isolate it,")
    print("      but LEAVE IT RUNNING - the keys are in its memory.")
    print("   2. Do NOT reboot or power off anything.")
    print("   3. Disconnect backup systems from the network.")
    print("   4. Capture memory from the writing host before anything else.")
    return 1


def remove(state_path: str) -> int:
    with open(state_path) as fh:
        state = json.load(fh)
    n = 0
    for c in state["canaries"]:
        try:
            os.remove(c["path"])
            n += 1
        except OSError:
            pass
    print(f"  removed {n} canaries")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Deploy and verify ransomware canary files.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("deploy", help="create canaries and record baseline hashes")
    d.add_argument("dirs", nargs="+")
    d.add_argument("--state", default="canaries.json")
    d.add_argument("--per-dir", type=int, default=3)
    d.add_argument("--hide", action="store_true", help="set hidden attribute (Windows)")

    c = sub.add_parser("check", help="verify canaries; exit 1 if any tripped")
    c.add_argument("--state", default="canaries.json")
    c.add_argument("--json", action="store_true")

    r = sub.add_parser("remove", help="delete deployed canaries")
    r.add_argument("--state", default="canaries.json")

    a = ap.parse_args()
    if a.cmd == "deploy":
        return deploy(a.dirs, a.state, a.per_dir, a.hide)
    if a.cmd == "check":
        return check(a.state, a.json)
    return remove(a.state)


if __name__ == "__main__":
    sys.exit(main())
