# The First 60 Minutes

A live ransomware incident, in order. This cuts across modules because that is how incidents arrive.

**The organising principle: act in order of volatility.** Memory disappears in seconds, `$UsnJrnl` in hours, disk in days. Do the perishable things first.

---

## 0–5 min — Stop the spread without destroying evidence

- [ ] **Network isolate affected hosts. Leave them running.** Pull cables, disable switch ports, or use EDR containment. Do **not** power off — see below.
- [ ] Disable the account(s) involved if known.
- [ ] Disconnect backup systems and shares from the network so they are not reached next.
- [ ] Identify whether encryption is **still running** anywhere. Those hosts are your highest-value evidence.

> **The one thing that matters most.** Someone will want the machines off. Have the answer ready:
> *"The decryption keys are in RAM on those machines right now. Powering them off destroys the only copy we can reach. Pull the network cables instead — that stops the spread and keeps the evidence."*

## 5–20 min — Capture what is perishable

- [ ] **Acquire memory** from any host still running, prioritising ones still encrypting. VM? Suspend it — cleanest capture available. ([Module 07](07-Memory-Forensics/))
- [ ] Capture `pagefile.sys` and `hiberfil.sys` alongside it.
- [ ] Preserve `$MFT` and `$UsnJrnl:$J` before the journal rolls. Hours, not days, on a busy volume.
- [ ] Pull event logs, and **check the SIEM copy** — local logs are often already cleared.
- [ ] Collect a ransom note and 3–5 encrypted files, plus known-good originals of the same files if any exist.

## 20–35 min — Characterise the attack

- [ ] **Is this BitLocker or another OS-native mechanism?** If hosts show a recovery prompt rather than encrypted files, go to [Module 04](04-Platform-And-LOTL-Encryption/) and **check key escrow immediately** — AD `msFVE-RecoveryInformation`, Entra ID, MBAM. This can end the incident in minutes.
- [ ] Triage the encrypted samples:
  ```bash
  python3 02-Hybrid-Encryption-Model/labs/parse_footer.py /evidence/samples --recurse
  python3 02-Hybrid-Encryption-Model/labs/parse_footer.py /evidence/x.xlsx.locked --original /backup/x.xlsx
  ```
- [ ] **Determine the encryption paradigm.** Full, intermittent, header-only, or distributed-chunk? This sets the ceiling on partial recovery.
- [ ] **Determine the key model.** Session or per-file?
  ```bash
  for f in *.locked; do tail -c 512 "$f" | sha256sum | cut -d' ' -f1; done | sort -u | wc -l
  ```
- [ ] Identify the family from note name, extension, and footer markers. Check [No More Ransom](https://www.nomoreransom.org/) for an existing decryptor.

## 35–50 min — Scope

- [ ] How many hosts, which shares, which cloud storage? Assume wider than first reported.
- [ ] **First encrypted file timestamp** — anchors the timeline and usually predates detection significantly.
- [ ] Evidence of exfiltration? Most modern operations steal before encrypting, which changes the legal and notification picture entirely.
- [ ] Check for persistence and propagation. Assume redundant mechanisms.
- [ ] Verify backup integrity **from the backup side**, offline. Do not mount backups to an affected network.

## 50–60 min — First communication

Give stakeholders four things and resist pressure to go beyond them:

1. **What happened** — plain language, no speculation on attribution.
2. **What is contained** — and what is not yet.
3. **What we know about recoverability** — honestly, with the basis stated.
4. **What we need** — decisions, access, authority.

Say "we don't know yet" where true. An early confident wrong answer about recoverability is far more damaging than an honest unknown, because people make irreversible decisions on it.

---

## Do not

- ❌ **Power off or reboot** a host that may still hold keys
- ❌ Run a downloaded decryptor on the only copy of client data
- ❌ Delete ransom notes or "clean up" encrypted files — they are evidence
- ❌ Mount backups to the affected network before you understand persistence
- ❌ Upload client samples to public services — VirusTotal submissions are visible to subscribers and can leak the victim's identity
- ❌ Promise recoverability before you have determined the key model and paradigm

## Hand-off checklist

- Memory images, with acquisition times and tool versions
- `$MFT`, `$UsnJrnl`, event logs, registry hives
- Encrypted samples + known-good originals + ransom note
- Paradigm, key model, and family determination with the evidence for each
- Timeline anchor: first encrypted file
- Open questions, explicitly listed

---

Related: [Module 07 Memory Forensics](07-Memory-Forensics/) · [Module 04 BitLocker](04-Platform-And-LOTL-Encryption/) · [MYTHS.md](MYTHS.md)
