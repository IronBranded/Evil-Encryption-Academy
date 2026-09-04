# Safe Lab Setup

**Read this before handling any live sample. It is referenced as mandatory from several modules for a reason.**

Ransomware is the one malware class where an analysis mistake destroys data immediately and irreversibly. There is no "I'll clean it up after." By the time you notice, the encryption has finished.

---

## You probably do not need a live sample

Every lab in this repository can be completed with synthetic specimens:

```bash
python3 01-Symmetric-Cryptography/labs/encryption_demo.py specimens --outdir ./lab-samples
```

These reproduce full, intermittent, header-only, and distributed-chunk encryption, plus realistic footers. They cannot encrypt anything, because they contain no ransomware.

**Use live samples only when you need behavior the specimens cannot reproduce**: API call traces, memory key recovery, persistence artifacts, propagation. If you are practising triage or entropy analysis, synthetic is strictly better because you have ground truth.

---

## Minimum viable safe lab

### 1. Isolation

- **Type 2 hypervisor on a dedicated machine.** Not your daily driver. Not a work laptop.
- **Network adapter removed, not just disconnected.** "Disconnected" is one misclick from connected. Remove the virtual NIC from the VM configuration.
- **No shared folders. No clipboard sharing. No drag-and-drop. No USB passthrough.** These are the documented VM escape and lateral paths, and shared folders in particular are just a mounted drive to an encryptor.
- **Host firewall blocks the hypervisor's virtual network** outbound, as a second layer.
- If you need network behavior, use an isolated host-only network with INetSim or FakeNet-NG. Never bridge to a real network.

### 2. Snapshots

- Snapshot **clean, before the sample ever lands on disk.**
- Snapshot again after tooling is installed and configured, so you never rebuild from scratch.
- Revert after every detonation. Do not reuse a detonated VM for the next sample.

### 3. Credentials and data

- The VM contains **nothing you care about** and no credentials that work anywhere else.
- Never log into real accounts, cloud storage, email, or source control from a lab VM.
- Assume every keystroke in that VM is captured.

### 4. Backups on the host

Ransomware that escapes hits mapped drives, network shares, and cloud sync folders first. Your host should have an offline or immutable backup that is **not mounted** while you work.

---

## Ransomware-specific precautions

These go beyond generic malware handling.

| Risk | Control |
|---|---|
| Encrypts mapped drives | No mapped drives on the VM. None |
| Encrypts network shares | No network. If unavoidable, isolated segment with nothing of value |
| Reaches cloud sync (OneDrive, Dropbox, Drive) | Never sign in to sync clients on a lab host |
| Deletes shadow copies and disables recovery | Expected. Rely on hypervisor snapshots, not in-guest recovery |
| Self-propagates to other hosts | Assume it will try. This is why the NIC is removed, not disabled |
| Encrypts the VM disk file from the host | Never store VM disks on a synced or shared volume |
| Clears event logs | Configure Windows Event Forwarding to a collector **outside** the VM if you need the logs |

### Password-gated samples

Some families require a build-specific password to execute. The Gentlemen validates an argument against a hardcoded value, which MSTIC notes is a static comparison identifiable and bypassable through static analysis.

**Treat a gated sample as fully live.** The gate is an operator convenience, not a safety feature, and it is trivially bypassed — including by accident while experimenting with arguments.

---

## Handling samples on disk

- **Store password-protected**, conventionally `infected`, in a ZIP or 7z archive.
- **Neuter the extension** while at rest: `sample.exe` becomes `sample.exe_` or `sample.malz`.
- **Exclude the sample directory from your host AV** only if you understand you are removing your last safety net. Prefer keeping AV on and accepting the quarantine.
- **Never** put samples in a synced folder, a repository, or anywhere with an automatic backup job.
- Record the SHA-256 before and after every handling step.

---

## Static analysis is safe. Dynamic is not.

A large fraction of this curriculum runs on **static** analysis, which never executes anything:

- `parse_footer.py` and `identify_crypto.py` are read-only and stdlib-only
- Strings, entropy, constant hunting, disassembly in Ghidra
- Reading an existing memory image

You can do Modules 00 through 04 and most of 08 without detonating anything. Detonate only when you need runtime behavior, and only in a VM you are ready to discard.

---

## Memory capture in the lab

To practise key recovery from Module 07, you need a memory image captured *during* encryption:

1. Snapshot clean.
2. Start the sample.
3. **Suspend the VM mid-encryption** — this writes RAM to disk as a `.vmem` or `.vmss` file.
4. Copy that file out to your analysis environment.
5. Revert the snapshot.

Suspending is safer than running an in-guest acquisition tool: no additional software, no timing race, and the resulting file is a clean image you can analyze offline at leisure.

---

## Legal and organizational

- **Get written authorization** before handling malware on any employer-owned equipment or network. Many organizations prohibit it outright.
- Some jurisdictions restrict possession or distribution of malicious code. Understand your local position.
- Never test against systems you do not own. Never redistribute samples.

---

## If something escapes

1. **Physically disconnect the host** from the network. Pull the cable, disable Wi-Fi at the hardware level.
2. **Do not power off if you want evidence.** Capture memory first if you intend to analyze what happened.
3. Assume anything reachable from that host is compromised, including cloud sync and mapped drives.
4. Restore from your offline backup. This is why it exists.

---

## Reference

- [`SAMPLE_SOURCING.md`](SAMPLE_SOURCING.md) — obtaining samples legitimately
- [`../SCOPE.md`](../SCOPE.md) — what this repository does and does not contain
- SANS FOR610 covers lab construction in far more depth than this page
- REMnux and FLARE-VM are the standard prebuilt analysis distributions
