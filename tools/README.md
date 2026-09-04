# Toolkit

Five tools. This page shows how they chain, which is not obvious from any one of them.

All are **read-only on their inputs** and **stdlib-only**, except the teaching demo which needs `cryptography`. That is deliberate — they run on a locked-down forensic workstation with no package installs.

```bash
pip install -r tools/requirements.txt   # only needed for encryption_demo.py
```

---

## The incident pipeline

```
   evidence
      │
      ├─ 1. IDENTIFY ──── tools/identify_crypto.py
      │                   What cipher? Hybrid? Statically linked?
      │                   -> feeds the scheme into your assessment
      │
      ├─ 2. TRIAGE ────── 02-Hybrid-Encryption-Model/labs/parse_footer.py
      │                   Actually encrypted? Which paradigm? Footer layout?
      │                   -> tells you whether step 3 is worth running
      │
      ├─ 3. RECOVER ───── 10-Recovery-and-Decryption/labs/recover_partial.py
      │                   How much survived? Extract it, offsets preserved.
      │
      └─ 4. VERIFY ────── parse_footer.py again, on the recovered output
                          Intact format header == you got it right
```

`canary_deploy.py` sits outside this pipeline — it is a standing control that runs *before* an incident and tells you one has started.

---

## 1. `identify_crypto.py` — what am I looking at?

```bash
python3 tools/identify_crypto.py sample.exe
python3 tools/identify_crypto.py memdump.raw --categories asymmetric
```

Matches ~60 signatures: cipher constants, Windows crypto APIs, container magics, LOTL indicators, build toolchain. Then reasons about them — symmetric plus asymmetric implies a hybrid scheme; a forward S-box with no inverse implies an encrypt-only build.

> **Run it without `--min-confidence` first.** Asymmetric markers like the Curve25519 constant are medium confidence, so filtering to `high` hides exactly the evidence a recoverability verdict depends on. The tool now refuses to conclude when filtered, but the habit matters.

## 2. `parse_footer.py` — is it encrypted, and how?

```bash
python3 02-Hybrid-Encryption-Model/labs/parse_footer.py /evidence/share --recurse
python3 02-Hybrid-Encryption-Model/labs/parse_footer.py locked.xlsx --original /backup/orig.xlsx
```

Classifies full / intermittent / header-only / distributed-chunk, reconciles file format against extension, finds binary and **text-encoded** footers, and sizes wrapped keys.

> **Read the `FORMAT` line, not just the verdict.** It is what stops you counting every JPEG on the share as encrypted.

## 3. `recover_partial.py` — how much survived?

```bash
python3 10-Recovery-and-Decryption/labs/recover_partial.py locked.mdf --footer 256 --out recovered.mdf
```

Maps encrypted regions, reports recoverable percentage, extracts. **Use `--out`, not `--fragments`,** for PST, MDF, VMDK and PDF — it nulls damaged regions in place so internal pointers still resolve.

## 4. `canary_deploy.py` — has an incident started?

```bash
python3 11-Endpoint-Detection/labs/canary_deploy.py deploy /srv/finance --state canaries.json
python3 11-Endpoint-Detection/labs/canary_deploy.py check --state canaries.json   # exit 1 = tripped
```

Schedule `check` and alert on exit code 1. The only non-statistical ransomware signal available.

## 5. `encryption_demo.py` — learn and generate specimens

```bash
python3 01-Symmetric-Cryptography/labs/encryption_demo.py all
python3 01-Symmetric-Cryptography/labs/encryption_demo.py specimens --outdir ./lab-samples
```

Teaching tool and safe specimen generator. Never touches live malware. See [`SCOPE.md`](../SCOPE.md) for why it is not an encryptor.

---

## Testing

```bash
python -m unittest discover tests -v
```

37 tests. Every one exists because a real bug shipped. If a test is intermittent, **that is a bug** — see [`CONTRIBUTING.md`](../CONTRIBUTING.md).
