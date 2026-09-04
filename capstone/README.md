# Capstone — Incident ALPHA

![Type](https://img.shields.io/badge/type-graded%20exercise-purple.svg)
![Time](https://img.shields.io/badge/time-2--3%20hours-blue.svg)

> Everything else in this repository teaches a skill. This asks you to assemble them and produce the deliverable a client pays for.

---

## Setup

```bash
python3 capstone/generate_incident.py --outdir ./incident-alpha
```

Nothing generated is malicious. The "encryptor" is an inert file containing crypto constants for identification practice — it has no code and cannot run. Encrypted files were produced by overwriting regions with random bytes, so **no key exists and nothing can be decrypted.** That is deliberate: the exercise is to determine what is *recoverable*, and the honest answer never depends on obtaining a key.

---

## The brief

> **From:** Head of IT, Meridian Logistics (240 staff, 3 sites)
> **Received:** 14 March, 06:40
>
> "We came in this morning to find most of the finance and HR file shares
> unreadable and a ransom note everywhere. FS01 is our main file server. Our
> monitoring flagged something at 02:17 but nobody was on shift.
>
> We have one backup that ran before this started but I'm told it only covers
> part of finance. The board is meeting at 14:00 and wants to know whether we're
> paying. **How much of our data is actually gone?**"

You have:

```
incident-alpha/
├── fileserver/          the affected share (finance, hr, media)
├── backups/             what survived
└── artifacts/           recovered binary, log excerpt, canary state
```

---

## Your deliverable

**One completed [recoverability assessment](../09-Triage-and-IR/templates/recoverability-assessment.md).** That is it. No technical appendix, no slide deck.

It must answer, with a stated basis for each:

1. **Which files are actually encrypted?** Be precise. Do not assume.
2. **What encryption paradigm** was used, and does it vary by file?
3. **Session key or per-file keys?** How do you know?
4. **What is the cryptographic scheme,** as far as the evidence supports?
5. **How much data is recoverable,** by volume, and by what method?
6. **When did this start?** Anchor the timeline.
7. **Is paying necessary?** Answer what you legitimately can, and be explicit about what is outside your remit.

---

## Rules

- **Work only from the generated evidence.** No outside information about the family.
- **State a basis for every claim.** An assertion without a basis is a guess and will be challenged in the board meeting.
- **Separate confirmed from expected from unknown.** Do not blur them to sound decisive.
- **Do not read [`SOLUTION.md`](SOLUTION.md) until you have written your assessment.** Reading it first turns a two-hour exercise into a ten-minute one and teaches you nothing.

---

## Suggested approach

Not a script — if you follow it mechanically you will fall into at least one of the traps.

```bash
# Triage the whole share. Read the FORMAT line, not just the verdict.
python3 02-Hybrid-Encryption-Model/labs/parse_footer.py ./incident-alpha/fileserver --recurse

# Identify the scheme from the recovered binary
python3 tools/identify_crypto.py ./incident-alpha/artifacts/recovered_binary.bin

# Quantify what survives
python3 10-Recovery-and-Decryption/labs/recover_partial.py <a large file> --footer 70

# Use the backup where you have one
python3 02-Hybrid-Encryption-Model/labs/parse_footer.py <encrypted> --original <backup copy>
```

Then read `artifacts/event_excerpt.csv` and `artifacts/canary_state.json`, and work the decision tree in [Module 10](../10-Recovery-and-Decryption/).

## Three things that catch people

1. **Not every high-entropy file is encrypted.** Check before you count.
2. **Tool output is evidence, not conclusions.** At least one tool will tell you something misleading if you run it carelessly. Read what it actually says.
3. **The ransom note is marketing copy.** Treat its technical claims as claims.

---

## Grading

`SOLUTION.md` scores out of 100 across seven findings plus the quality of the written assessment. **70 is a pass.** Below 50 means re-reading Modules 02, 10 and 11 before retrying with `--seed 99`.
