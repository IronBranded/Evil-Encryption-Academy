# Module 09 — Triage and Incident Response

![Difficulty](https://img.shields.io/badge/difficulty-intermediate-orange.svg)
![Focus](https://img.shields.io/badge/focus-defensible%20timeline-red.svg)

> Building a timeline that survives scrutiny, when the attacker has deliberately destroyed your logs.

**Prerequisites:** [Modules 02–04](../02-Hybrid-Encryption-Model/). For a live incident, go to [`FIRST-60-MINUTES.md`](../FIRST-60-MINUTES.md) instead — this module is the depth behind it.

---

## 1. Assume the logs are gone

Modern ransomware clears event logs as standard practice. MSTIC's Gentlemen analysis documents clearing System, Application and Security with `wevtutil`, deleting prefetch and RDP logs, and removing PowerShell history from every user profile.

So plan around it. **Artifacts fall into three tiers by how well they survive an attacker who is actively destroying evidence:**

| Tier | Artifact | Survives log clearing? |
|---|---|---|
| **1** | `$MFT`, `$UsnJrnl:$J`, `$LogFile` | **Yes** — filesystem metadata, not logs |
| **1** | Forwarded/SIEM log copies | **Yes** — off the host |
| **1** | Memory (if captured) | Yes, until reboot |
| 2 | Registry hives, prefetch, AmCache, SRUM | Often partially |
| 3 | Local Windows event logs | Frequently cleared |

**Build your timeline on tier 1 and corroborate with the rest.** An investigation that depends on local event logs will collapse the moment you meet a competent operator — and 1102 tells you it already has.

---

## 2. `$UsnJrnl:$J` — the highest-value artifact

The USN journal records every change on the volume: creates, writes, renames, deletes, each with a timestamp and file reference. It is **filesystem metadata, not a log**, so `wevtutil` does not touch it.

For ransomware specifically it is close to ideal, because mass renaming is exactly what the journal is designed to record:

- `RENAME_OLD_NAME` / `RENAME_NEW_NAME` pairs give you **the extension change, per file, with a timestamp**
- `FILE_CREATE` records show ransom notes appearing across directories
- `DATA_OVERWRITE` shows the encryption writes themselves
- The **first and last** encryption-related records bracket the whole event

**It rolls over.** On a busy volume that is hours, not days. Preserve it early — it is item 4 in the [first-60-minutes](../FIRST-60-MINUTES.md) order for that reason.

Parse with MFTECmd (Eric Zimmerman), then Timeline Explorer. `$MFT` gives you the four `$STANDARD_INFORMATION` timestamps plus `$FILE_NAME` timestamps, which is also where timestomping shows up as a mismatch between the two sets.

---

## 3. Event logs, when you have them

| ID | Log | Meaning in this context |
|---|---|---|
| **4688** | Security | Process creation. **Requires command-line auditing** to be useful — enable it before you need it |
| **4624 / 4625** | Security | Logons. Type 3 = network, Type 10 = RDP. Service accounts from unusual hosts are the lead |
| **4663** | Security | Object access. Requires SACLs; rarely configured, high value where it is |
| **7045** | System | Service installed. Kernel driver installs here are a BYOVD indicator |
| **1102** | Security | **Audit log cleared.** Not a loss — it is a timestamped event marking when the attacker cleaned up |
| **1074 / 6008** | System | Shutdown initiated / unexpected shutdown |
| **4104** | PowerShell Operational | **Script block logging.** Captures the script body even when the file self-deletes. The single highest-value control for scripted attacks |
| Sysmon 1 / 11 / 23 | Sysmon | Process create / file create / file delete archived |

**1102 is evidence, not absence of evidence.** It gives you the moment cleanup happened, which brackets the attack from the other end. Note the gap it creates rather than treating it as a dead end.

---

## 4. Constructing the timeline

Anchor on the **first encrypted file**, not on when someone noticed. Detection typically lags initiation by a long way, and the gap is where the story is.

A useful ordering, working outward:

1. **First encryption write** (`$UsnJrnl`) — the anchor
2. **Anti-recovery actions** — shadow copy deletion, backup catalog deletion. These usually *precede* encryption by minutes to tens of minutes, and that window was when it was stoppable
3. **Encryptor process creation** (4688 / Sysmon 1)
4. **Initial access and lateral movement** — logons, service installs, scheduled tasks
5. **Last encryption write** — the other bracket
6. **Log clearing** (1102) and note creation

The capstone's log excerpt is a worked example: logon at 01:33, encryptor at 01:36, anti-recovery at 01:38, canary trip at 02:17. Anchoring on the canary alone loses 44 minutes of the intrusion and misses the initial-access lead entirely.

---

## 5. Ransom note analysis

Notes are marketing copy. Read them for what they leak, not what they claim.

| Extract | Why |
|---|---|
| Note filename and format | Family attribution, often the fastest identifier |
| Victim/campaign ID | Correlates hosts to a single intrusion; identifies affiliate |
| Contact channel (onion, Tox, email) | IOC, and legal/notification relevance |
| **Technical claims** | Usually wrong. "RSA-4048" is not a real key size — treat it as an attribution signal, not a fact |
| Directory spread | `FILE_CREATE` records show note placement and the traversal path |

Verify every technical claim against the ciphertext. The capstone's note claims RSA-4048 while the evidence shows a Curve25519 scheme; believing the note produces a wrong verdict.

**Do not upload notes to public services.** They routinely contain victim identifiers, and VirusTotal submissions are visible to subscribers.

---

## 6. Scoping

Scope is almost always wider than first reported. Establish:

- **Which hosts** — check for the encryptor binary, ransom notes, persistence, and the appended extension
- **Which shares and mapped drives** — the writes may have originated from one host and landed on many
- **Cloud sync** — OneDrive, SharePoint, Dropbox propagate encryption to the cloud copy
- **Backup infrastructure** — reached before encryption in most competent intrusions
- **Exfiltration** — most modern operations steal first. Large outbound transfers, tunnelling services, cloud storage uploads. **This is frequently the larger legal exposure**
- **Hypervisors** — one ESXi host can account for hundreds of affected workloads ([Module 04](../04-Platform-And-LOTL-Encryption/))

Propagation is often redundant: MSTIC records The Gentlemen attempting 21 remote execution operations per target across multiple APIs and privilege levels, each tried regardless of whether earlier ones failed. Treating that as a single-host incident understates it badly.

---

## 7. Deliverables

[`templates/recoverability-assessment.md`](templates/recoverability-assessment.md) is the client-facing output, and it is the one that matters. Every claim needs a stated basis.

Alongside it, keep an internal record of:

- Acquisition log — what, when, which tool, which hashes
- The timeline, with the artifact backing each entry
- Scope: hosts, shares, accounts, cloud
- Open questions, explicitly listed

**Separate confirmed from expected from unknown.** Blurring them to sound decisive is how an assessment becomes indefensible three weeks later.

---

## 8. Exercises

1. Work the capstone's `event_excerpt.csv`. Produce the full timeline and identify the window in which the attack was stoppable.
2. Your client's Security log shows 1102 and nothing before it. List what you can still reconstruct, and from where.
3. Write the `$UsnJrnl` query that establishes the first and last encryption writes. What tells you the difference between an attacker rename and ordinary file churn?
4. Given a ransom note claiming RSA-4048, describe how you verify or refute it from the encrypted files alone.

---

## 9. References

- Eric Zimmerman's tools — MFTECmd, Timeline Explorer, RECmd
- [13cubed](https://www.13cubed.com/) — `$MFT` and `$UsnJrnl` walkthroughs, free
- SANS **FOR500** (Windows artifacts) and **FOR508** (advanced IR)
- [`FIRST-60-MINUTES.md`](../FIRST-60-MINUTES.md) — the live-incident ordering
- [The Gentlemen case study](../06-Case-Studies/the-gentlemen/) — anti-forensics behaviour in detail

---

| ◄ [Module 08: Reverse Engineering](../08-Reverse-Engineering/) | [Module 10: Recovery](../10-Recovery-and-Decryption/) ► |
|---|---|
