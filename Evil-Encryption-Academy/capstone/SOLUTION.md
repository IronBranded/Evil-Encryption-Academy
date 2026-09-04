# Capstone ALPHA — Answer Key

> **Do not read this until your assessment is written.**

Values below are for `--seed 1337`. Other seeds change file sizes and counts but not the scheme, so the findings and traps hold.

---

## Finding 1 — Which files are encrypted (15 points)

| Location | Files | Status |
|---|---|---|
| `finance/`, `hr/` — `.lksm` extension | 7 | **Encrypted** |
| `media/` — `.mp4`, `.jpg`, `.zip` | 3 | **NOT encrypted** |
| `README-LOCKSMITH.txt` (×4) | 4 | Ransom note, plaintext |

**TRAP 1.** The media files score ~8.0 entropy — identical to ciphertext — but their headers are intact and match their extensions, and no ransom extension was appended. They were never touched. An entropy-only assessment reports 10 encrypted files instead of 7 and inflates the loss by 43%.

- **15 pts** — correctly excludes media, with format-header reasoning
- **7 pts** — excludes media but justifies it only by extension
- **0 pts** — counts media as encrypted

## Finding 2 — Encryption paradigm (15 points)

Two behaviours, split by size:

| Group | Size | Paradigm | Encrypted |
|---|---|---|---|
| `ledger_2025.mdf`, `receivables.mdf`, `personnel.pst` | >1 MB | **Distributed-chunk**, 3 chunks at head/midpoint/tail | ~9% |
| 4 × `.xlsx` / `.docx` | <1 MB | **Full encryption** | 100% |

- **15 pts** — identifies both and links the split to file size
- **8 pts** — identifies both, misses the size threshold
- **0 pts** — reports a single paradigm

## Finding 3 — Key model (15 points)

**Per-file keys.** Every footer is unique.

```bash
for f in $(find ./incident-alpha/fileserver -name "*.lksm"); do
    tail -c 70 "$f" | sha256sum | cut -c1-16
done | sort -u | wc -l
# 7 distinct footers across 7 files -> per-file, not a session key
```

**Consequence:** recovering one key recovers one file. This closes off any "recover the key, decrypt everything" outcome and must be stated plainly.

- **15 pts** — correct, with the comparison as basis
- **7 pts** — correct, asserted without basis
- **0 pts** — claims a session key

## Finding 4 — Cryptographic scheme (15 points)

From `identify_crypto.py` on the recovered binary:

- **XChaCha20** (or ChaCha20) — the `expand 32-byte k` sigma constant
- **Poly1305** — AEAD clamp constant
- **Curve25519** — a24 constant `41 db 01 00`, medium confidence
- **Go, statically linked**, Garble-obfuscated
- Footer `--eph--<base64>--marker--LOCKSMITH` → base64 decodes to **32 bytes** = an ephemeral public key

Together: **per-file ephemeral Curve25519 ECDH wrapping an XChaCha20 key.** No cryptographic recovery path.

**TRAP 2.** Running `identify_crypto.py --min-confidence high` suppresses the Curve25519 marker, because it is medium confidence. The tool now refuses to conclude and tells you to re-run — but a careless reading of an older output would report "symmetric only, decryptor plausible," which is the single most damaging error available in this exercise. **It would have you tell the board recovery is likely when it is impossible.**

- **15 pts** — identifies the hybrid scheme and states there is no crypto shortcut
- **8 pts** — identifies the bulk cipher only
- **−5 pts** — concludes a decryptor is plausible

## Finding 5 — Recoverable volume (20 points)

Large files, via `recover_partial.py --footer 70`:

| File | Recoverable |
|---|---|
| `ledger_2025.mdf` | **~91%** |
| `receivables.mdf` | ~91% |
| `personnel.pst` | ~91% |

Small files: **0% by partial recovery.** Fully encrypted.

`ledger_2025.mdf` also has a **surviving backup copy**, so it is 100% recoverable by restore — use the backup, not the partial extraction.

**The correct answer by volume:** the overwhelming majority of affected data sits in the three large files, so roughly **90%+ of affected data volume is recoverable** even without the backup. The four small files are lost unless other backups exist.

Extraction must use `--out` (offset-preserving), not `--fragments`, because MDF and PST are offset-addressed.

- **20 pts** — per-file percentages, notes the backup, specifies offset preservation
- **12 pts** — percentages only
- **5 pts** — "some data may be recoverable"
- **0 pts** — declares total loss

## Finding 6 — Timeline (10 points)

From `event_excerpt.csv`:

| Time (UTC) | Event |
|---|---|
| 01:33 | Logon as `SVC_BACKUP` from 10.4.2.87 (Type 3) |
| 01:36 | `svchost32.exe` created in `C:\Windows\Temp` from `cmd.exe` |
| 01:38 | **`vssadmin delete shadows`** and `wbadmin delete catalog` |
| 01:39 | Kernel driver `WinRing0x64` installed (BYOVD indicator) |
| 02:15 | **Audit log cleared** |
| 02:17 | Canary tripped |
| 02:28 | `wevtutil cl System` |

**Anchor: ~01:33**, about 44 minutes before the canary fired. Anti-recovery preceded encryption by ~39 minutes — that was the window in which this was stoppable.

The service account logon from a single internal IP is the lead for scoping.

- **10 pts** — anchors at 01:33 and notes anti-recovery preceded encryption
- **5 pts** — anchors at 02:17 (canary trip) only
- **0 pts** — no timeline

## Finding 7 — The payment question (10 points)

What you can legitimately say:

- ~90%+ of affected data **volume** is recoverable without paying
- One large file is fully recoverable from backup
- Four small files are not recoverable by technical means available here
- The note's **"RSA-4048" claim is false** — that key size does not exist. The actual scheme is Curve25519-based. Note it as an attribution signal and as a reason to distrust the rest of the note
- Log clearing means **exfiltration cannot be ruled out**, which is a legal and notification question, likely bigger than the encryption

What is outside your remit: whether to pay. That is legal, regulatory and commercial. Your contribution is an accurate technical picture.

- **10 pts** — quantified position, flags the false RSA-4048 claim, raises exfiltration, declines to advise on payment
- **5 pts** — quantified position only
- **0 pts** — recommends for or against paying on technical grounds

---

## Written quality (bonus, up to 10)

- Basis stated for every claim
- Confirmed / expected / unknown kept distinct
- "Intact but unreadable," not "destroyed"
- An executive could act on it without a translator

## Scoring

| Score | Meaning |
|---|---|
| 90+ | Ready to lead this engagement |
| 70–89 | Solid. Review whichever finding you lost points on |
| 50–69 | Re-read Modules 02, 10 and 11, retry with `--seed 99` |
| <50 | Work through the modules in order first |

**If you fell into either trap, note it.** Both produce a *confident, specific, wrong* answer — the most damaging failure mode in this work, because nobody thinks to question a number that came from a tool.
