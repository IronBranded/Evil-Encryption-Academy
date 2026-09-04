# Module 11 — Endpoint Detection Mechanics

![Difficulty](https://img.shields.io/badge/difficulty-intermediate-orange.svg)
![Focus](https://img.shields.io/badge/focus-real--time%20detection-red.svg)

> How EDR actually catches ransomware, why each signal fails on its own, and what to do about the gaps.

**Prerequisites:** [Module 03](../03-Encryption-Paradigms/) (paradigms) and [Module 04](../04-Platform-And-LOTL-Encryption/) (LOTL). Read after those — several detections exist specifically because of what those modules describe.

---

## 1. The core problem

Encryption is not anomalous. It is ordinary work.

Backup software reads thousands of files and writes compressed, high-entropy output. Media encoders do the same. Disk encryption tools, archivers, database maintenance, and search indexers all produce telemetry that looks broadly like an encryptor.

**There is no single signal that separates ransomware from legitimate bulk file work.** Every detection below is a probabilistic judgement, and every one has a legitimate process that trips it. Detection is therefore a *correlation* problem, not a signature problem — which is why a rule that works in a lab produces thousands of alerts in production.

Understanding which signals are weak and why is the actual skill here.

---

## 2. Where the telemetry comes from

An EDR sees file activity through several collection points. They differ in what they can see and how easily they are defeated.

| Layer | Mechanism | Sees | Notes |
|---|---|---|---|
| **Filesystem minifilter** | `FltMgr` driver at a registered altitude | Every create, write, rename, delete, **before it lands on disk** | The important one for ransomware. Can block inline |
| Kernel callbacks | `PsSetCreateProcessNotifyRoutineEx`, `ObRegisterCallbacks`, `CmRegisterCallback` | Process creation, handle access, registry | Process lineage and tamper attempts |
| **ETW** | `Microsoft-Windows-Kernel-File`, `Kernel-Process`, Threat-Intelligence ETW | File and process events, some memory operations | Broad, but higher latency than a minifilter |
| User-mode hooks | Inline hooks in `ntdll` | API calls in-process | Declining. Trivially bypassed by direct syscalls |
| Volume/journal | `$UsnJrnl` monitoring | Rename and modify records | Survives log clearing. See [Module 09](../09-Triage-and-IR/) |

**The minifilter is the one that matters**, because it sits in the write path. It sees the content being written before it exists on disk, which is what makes inline entropy checks and blocking responses possible at all.

---

## 3. The signals

### 3.1 File modification rate and breadth

The most intuitive signal: one process modifying N files across M directories in T seconds.

**Why it works.** Mass encryption produces a write pattern with no normal analogue — hundreds or thousands of distinct files, spanning many directories and many extensions, from a single process, in minutes.

**Why it fails.** Backup agents, sync clients, antivirus scans, indexers, and installers all do this. Tuning the threshold high enough to silence them leaves room for slow encryption to pass underneath.

**What makes it stronger:** *breadth* rather than volume. Touching 500 files in one directory is a backup job. Touching 500 files across 60 directories spanning `.docx`, `.xlsx`, `.pdf`, `.jpg` and `.mdf` is not.

### 3.2 Entropy — and why the naive version is wrong

This is the signal most people name first, and the one most often implemented badly.

**Absolute entropy is a weak signal.** A JPEG scores ~7.9 and an MP4 ~8.0 — the same as AES output. Flagging high-entropy writes flags every photo, video, archive, and compressed file on the estate. This repository's own triage tool had exactly this bug, calling a JPEG `FULL ENCRYPTION` at high confidence (see [`tests/`](../tests/)).

**Entropy delta is the real signal.** Compare the entropy of the file *before* the write against *after*:

| Before | After | Interpretation |
|---|---|---|
| 4.2 (document) | 7.99 | **Encryption.** Large positive delta from structured to random |
| 7.9 (JPEG) | 7.9 | Normal. A photo was rewritten |
| 7.9 (JPEG) | 7.99 | Suspicious in context, but a small delta — weak on its own |
| 4.2 | 4.3 | Normal document edit |

The minifilter can compute this because it sees the buffer before it is committed.

**Complementary statistical tests.** Entropy is one measure of randomness and not the best one alone. Chi-square distribution tests and arithmetic-mean checks catch cases entropy misses, and are cheap enough to run on a sampled block.

**Sampling is the weak point.** An EDR cannot hash and score entire multi-gigabyte files at write time. It samples — typically the header plus a few blocks. **Intermittent and distributed-chunk encryption attack this directly.** At Gentlemen `--ultrafast` percentages roughly 99% of a large file is untouched, so a sampled block is overwhelmingly likely to land on plaintext. See [Module 10](../10-Recovery-and-Decryption/).

### 3.3 Format and extension mismatch after write

Post-write, does the file's magic still match its extension? A `.docx` whose ZIP header is gone was not edited — it was encrypted.

This is a strong, low-false-positive signal and it is the same insight that fixed this repository's triage tool. It also catches header-only encryption, which barely moves file-level entropy at all.

### 3.4 Mass rename and uniform extension change

Renaming many files to a single new extension has essentially no legitimate analogue at scale. Visible via minifilter `IRP_MJ_SET_INFORMATION` and in `$UsnJrnl` as `RENAME_NEW_NAME` records.

Watch for **new extensions with no registered handler** appearing across many directories.

### 3.5 Read-encrypt-write pattern

The same process opens a file, reads it in full, and overwrites it in place with the same or similar length. Repeated across many files, this sequence is distinctive — the *ordering* carries more information than any individual event.

### 3.6 Canary files

A decoy file that no legitimate process should ever touch. Any modification is a signal.

**This is the only signal here that is not statistical.** It requires no threshold and no tuning, and it works precisely where the others are weakest: writes over SMB landing on a file server with no agent, LOTL encryption by a signed Microsoft binary, or a tampered agent.

[`labs/canary_deploy.py`](labs/canary_deploy.py) implements it:

```bash
python3 labs/canary_deploy.py deploy /srv/finance /srv/hr --state canaries.json
python3 labs/canary_deploy.py check --state canaries.json   # exit 1 = tripped
```

```
*** CANARY TRIPPED *** 2 of 4 affected

  [MODIFIED] /srv/finance/!!!-DO-NOT-MODIFY-8effb112.docx
     content changed - no legitimate process writes here
  [MISSING] /srv/finance/!!-archive-index-67b89f90.xlsx
     deleted or renamed - both are ransomware behaviour
```

Deployment notes that determine whether it works:

- **Name them to sort early.** Many encryptors enumerate with `FindFirstFile`/`FindNextFile` and process in returned order, roughly alphabetical on NTFS. An early-sorting name is hit early, which is the whole point of a tripwire.
- **Use realistic names, content, and extensions.** A canary full of obvious filler is one an operator can recognise and skip.
- **Spread them widely** — the root of every share and deep in directory trees.
- **Keep the state file off the monitored shares.** If it is encrypted too, you lose the baseline exactly when you need it.
- **Exclude them from backup and FIM noise**, or you will disable the alerting yourself within a week.

A canary tells you something is wrong. It does not stop it. Treat it as early warning, not control.

### 3.7 Anti-recovery behaviour

Often the *earliest* reliable signal, because it usually precedes bulk encryption:

- Shadow copy deletion (`vssadmin`, `wmic shadowcopy`, `Win32_ShadowCopy`)
- Backup catalog deletion (`wbadmin delete catalog`)
- Recovery environment disabling (`bcdedit /set recoveryenabled no`)
- Event log clearing (`wevtutil cl`)
- Security service tampering

By the time these fire, encryption may be minutes away. **These are your highest-value blocking opportunities.**

### 3.8 Ransom note creation

The same filename appearing in many directories in a short window, typically `.txt`, `.hta`, or `.html`, and often written by the process doing the encrypting. Distinctive and cheap to detect, but late — the note usually lands during or after encryption.

### 3.9 Process lineage and provenance

Office spawning a script host spawning an unsigned binary is a stronger signal than any file event. `PsSetCreateProcessNotifyRoutineEx` gives full parentage.

Also watch for raw volume handles (`\\.\PhysicalDrive0`), which bypass the filesystem entirely — used by MBR lockers and some disk-level encryptors.

---

## 4. Correlation is the product

No single signal is deployable alone. Real detection scores a weighted combination within a time window:

```
  mass file modification         +2
  entropy delta across many files +3
  format/extension mismatch      +3
  mass rename, uniform extension +3
  shadow copy deletion           +4
  canary tripped                 +5
  unsigned binary, odd lineage   +2
  ────────────────────────────────
  score >= 7 within 120s  ->  block, isolate, alert
```

Weights and windows are illustrative. The principle is not: **a single-signal rule is not deployable, and the sequence carries more information than the individual events.**

### Response actions

| Action | Effect |
|---|---|
| Kill process | Stops further encryption. Files already done stay done |
| Network isolate | Stops spread. **Preserves memory** — the right call |
| Block inline | Minifilter denies the write. Best outcome, needs high confidence |
| **Rollback** | Restores files from EDR-journaled copies of modified files |

**Rollback is the mechanism that actually saves data.** Several EDR platforms keep copies of files as they are modified, then restore them on detection. It is bounded by journal size and retention, so it works best when detection fires early — which is the argument for canaries and anti-recovery detection over waiting for volume thresholds.

**Never let containment mean "power off."** See [Module 07](../07-Memory-Forensics/): the keys are in RAM on that host.

---

## 5. Where detection fails

Framed as gaps to cover, not techniques to use. Consistent with [`SCOPE.md`](../SCOPE.md), this describes *why your telemetry misses things*, not how to build an evader.

| Gap | Why it works | What to do |
|---|---|---|
| **Intermittent / chunked encryption** | Less I/O, and sampled blocks often land on plaintext | Sample more blocks; weight format mismatch over entropy |
| **Slow encryption** | Stays under rate thresholds | Use long windows and breadth-based rules, not just rate |
| **LOTL (BitLocker, EFS)** | The writing process is a signed Microsoft binary | Command-line and WMI detection ([Module 04](../04-Platform-And-LOTL-Encryption/)) |
| **Encryption over SMB** | Writes land on a file server that may have no agent | **Deploy agents on file servers.** Canaries on every share |
| **Agent tampering / BYOVD** | Minifilter unloaded or agent killed first | Tamper protection; alert on agent health loss as an incident |
| **Header-only encryption** | Tiny write; file-level entropy barely moves | Format mismatch detection catches this cleanly |

The SMB gap deserves emphasis. A single compromised workstation can encrypt an entire file server across the network. All the file writes happen **on the server**, where organisations frequently have no EDR coverage because "it's just a file server." An endpoint-only deployment can be blind to the highest-impact scenario in the whole threat model.

---

## 6. Detection content

Behavioural Sigma rules for the anti-recovery signals, which are the earliest reliable ones. File-volume and entropy detection requires EDR telemetry rather than event logs.

```yaml
title: Shadow Copy Deletion via Native Tooling
id: 8b1c9f42-0e3a-4a71-9c2d-3f7b1a6e5d40
status: stable
description: Deletion of volume shadow copies, a near-universal ransomware precursor
references:
  - https://www.microsoft.com/en-us/security/blog/threat-intelligence/ransomware/
logsource:
  category: process_creation
  product: windows
detection:
  vssadmin:
    Image|endswith: '\vssadmin.exe'
    CommandLine|contains|all: ['delete', 'shadows']
  wmic:
    Image|endswith: '\wmic.exe'
    CommandLine|contains: 'shadowcopy'
    CommandLine|contains: 'delete'
  powershell:
    CommandLine|contains|all: ['Win32_ShadowCopy', 'Delete']
  condition: 1 of them
falsepositives:
  - Storage maintenance scripts. Rare, and should be individually allow-listed.
level: high
---
title: Backup and Recovery Destruction
id: c4d7e219-6b85-4f13-8a90-2e5c7d1b4a63
status: stable
description: Backup catalog deletion or recovery environment disabling
logsource:
  category: process_creation
  product: windows
detection:
  wbadmin:
    Image|endswith: '\wbadmin.exe'
    CommandLine|contains|all: ['delete', 'catalog']
  bcdedit_recovery:
    Image|endswith: '\bcdedit.exe'
    CommandLine|contains: 'recoveryenabled'
    CommandLine|contains: 'no'
  bcdedit_failure:
    Image|endswith: '\bcdedit.exe'
    CommandLine|contains: 'ignoreallfailures'
  condition: 1 of them
falsepositives:
  - Legitimate backup rotation, which should originate from a known scheduler.
level: high
---
title: Ransom Note Written Across Multiple Directories
id: f2a8b031-5c47-4d92-b1e6-9a3f8c2d7e51
status: experimental
description: Same filename created repeatedly across directories by one process
logsource:
  category: file_event
  product: windows
detection:
  selection:
    TargetFilename|endswith: ['.txt', '.hta', '.html']
    TargetFilename|contains:
      - 'README'
      - 'RECOVER'
      - 'DECRYPT'
      - 'RESTORE'
      - 'HOW_TO'
  condition: selection
  timeframe: 5m
falsepositives:
  - Software installers writing README files. Correlate on directory count.
level: medium
---
title: Canary File Modified
id: 7e5d3c98-1a62-4b80-9f45-6c8e2d0a3b71
status: stable
description: Write to a deployed decoy file. No legitimate process touches these.
logsource:
  category: file_event
  product: windows
detection:
  selection:
    TargetFilename|contains:
      - '!!!-DO-NOT-MODIFY-'
      - '!!-archive-index-'
  condition: selection
falsepositives:
  - Backup software, if canary paths were not excluded from backup jobs.
level: critical
```

BitLocker-specific detection is in [Module 04](../04-Platform-And-LOTL-Encryption/).

---

## 7. Configuration that matters

Ordered by impact:

1. **Tamper protection.** Prevents the agent being stopped. Without it, every other control is optional from the attacker's perspective.
2. **EDR in block mode**, not detect-only. Detection without prevention just documents the incident.
3. **Controlled folder access** on user data locations.
4. **ASR rules**, particularly blocking process creation from PsExec and WMI commands.
5. **Agents on file servers**, not just endpoints. Closes the SMB gap.
6. **Canary files** on every share.
7. **Windows Event Forwarding.** Encryptors clear local logs; a forwarded copy is what survives.
8. **Alert on agent health loss** as an incident, not a helpdesk ticket.

---

## 8. Exercises

1. Deploy canaries in a lab share, run the demo specimen generator against it, and confirm the trip. Measure how long detection takes.
2. Compute entropy delta for a document before and after encryption, and for a JPEG rewritten unchanged. Explain why absolute entropy cannot distinguish them.
3. Your EDR samples one 4 KB block per write. At Gentlemen `--ultrafast` percentages, what is the approximate probability a sampled block lands on ciphertext? What does that tell you about weighting entropy against format mismatch?
4. Design a scoring rule for a 200-user estate with a nightly backup agent. Which signals do you weight up, and what did you have to give up to keep the alert volume workable?

---

## 9. References

- [MSTIC ransomware coverage](https://www.microsoft.com/en-us/security/blog/threat-intelligence/ransomware/) — see [`PRIMARY_SOURCES.md`](../references/PRIMARY_SOURCES.md)
- Microsoft Learn — filesystem minifilter drivers, ASR rules, controlled folder access, tamper protection
- [Sigma HQ](https://github.com/SigmaHQ/sigma) — community rule repository
- *Windows Internals* — I/O system and filter manager architecture
- SANS FOR508 for the detection-engineering context

---

| ◄ [Module 10: Recovery](../10-Recovery-and-Decryption/) | [Repository index](../README.md) |
|---|---|
