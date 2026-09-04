# Module 07 — Memory Forensics

![Difficulty](https://img.shields.io/badge/difficulty-advanced-red.svg)
![Time](https://img.shields.io/badge/time-4--6%20hours-blue.svg)
![Prereq](https://img.shields.io/badge/prereq-Modules%2001--03-lightgrey.svg)

> Every other module in this repository points here. This is the one window where a defender can undo the encryption.

**Prerequisites:** [Module 02](../02-Hybrid-Encryption-Model/) for the recovery window, [Module 01](../01-Symmetric-Cryptography/) for cipher internals.

---

## 1. The entire premise

From Module 02: the plaintext symmetric key exists in RAM between generation and `SecureZeroMemory`. Before that moment it does not exist. After it, the only copy is wrapped under a private key on attacker infrastructure.

```
   key generated          bulk encryption          key wiped
        │                        │                     │
        ▼                        ▼                     ▼
  ──────┬──────────────────────────────────────────────┬──────►
        │            RECOVERY WINDOW                   │
        │   plaintext key resident in process memory   │
        └──────────────────────────────────────────────┘
                            ▲
                   memory acquisition
                   must land in here
```

Everything below exists to land an acquisition inside that band and extract what is in it.

**Set expectations honestly.** Memory key recovery works often enough to always attempt and never often enough to promise. Attempt it in every incident. Promise it in none.

---

## 2. Acquisition doctrine

> **Capture RAM before anything else. Do not reboot. Do not shut down. Do not pull the power.**

This is the highest-value action available in a live ransomware incident and it is routinely destroyed within minutes by the instinct every IT team has: turn it off to stop it.

**Isolate without killing the host.** Pull the network cable, disable the switch port, or use an EDR containment action that leaves the machine running. All of those stop spread while preserving memory. Powering off stops spread and destroys the only recoverable copy of the key.

### The conversation you will actually have

Someone senior will want the machines off. You need a one-sentence answer ready:

> "The decryption keys are in RAM on those machines right now. Powering them off destroys the only copy we can reach. Pull the network cables instead — that stops the spread and keeps the evidence."

Have this ready before you need it. The window closes while you are constructing the argument.

### Order of operations

| Priority | Action | Why |
|---|---|---|
| 1 | Network isolate, host stays running | Stops spread, preserves RAM |
| 2 | **Acquire memory** | Volatile. Everything else survives longer |
| 3 | Capture pagefile and hiberfil | Key material may have been paged out |
| 4 | Preserve `$MFT`, `$UsnJrnl:$J` | `$UsnJrnl` rolls over. Hours, not days, on a busy volume |
| 5 | Event logs, registry hives | May already be cleared. Check the SIEM copy |
| 6 | Disk image | Least volatile. Last |

### Tools

- **WinPmem** — open source, well understood, minimal footprint
- **Magnet RAM Capture** — free, GUI, defensible for less technical responders
- **EDR memory acquisition** — often fastest at scale if your platform supports it
- **VM suspend** — for virtual hosts, suspending writes RAM to a `.vmem`/`.vmss` file with no in-guest software at all. Usually the cleanest option available

Capture to external media or a network share, never to the volume being encrypted.

---

## 3. Why AES keys cannot hide

AES does not use your 32-byte key directly. It runs a **key expansion** producing a round-key schedule held in contiguous memory for the duration of the encryption:

| Variant | Rounds | Schedule in RAM |
|---|---|---|
| AES-128 | 10 | 176 bytes |
| AES-192 | 12 | 208 bytes |
| AES-256 | 14 | **240 bytes** |

That schedule is not random. Each 16-byte round key is a deterministic function of the previous one. A scanner walks memory, treats each window as a candidate schedule, runs the expansion relation, and checks whether it holds.

**Random data does not satisfy the AES key schedule recurrence.** False positives are essentially impossible in the mathematical sense — which is why this technique is reliable in a way that most memory-scanning heuristics are not.

The catch is that Windows itself uses AES constantly, for TLS, BitLocker, DPAPI and more. You will get many *mathematically valid* keys. Almost all of them belong to the operating system. Validation is the real work.

---

## 4. Workflow

```bash
# 1. Confirm the image is sane and identify the profile
python3 vol.py -f victim.raw windows.info

# 2. Find the encryptor process
python3 vol.py -f victim.raw windows.pslist
python3 vol.py -f victim.raw windows.cmdline          # speed flags, password args
python3 vol.py -f victim.raw windows.malfind          # injected / RWX regions

# 3. Dump that process's memory
python3 vol.py -f victim.raw -o ./dump windows.memmap --pid 4812 --dump

# 4. Scan for verifiable AES key schedules
findaes ./dump/pid.4812.dmp
bulk_extractor -E aes -o ./bulk ./dump/pid.4812.dmp

# 5. VALIDATE against known plaintext  ← the step everyone skips
```

### Identifying the right process

The encryptor may not be obvious. Useful signals:

- High I/O counts against many distinct files (`windows.handles`, `windows.filescan`)
- Recently created process with an unusual parent
- RWX private memory regions (`windows.malfind`) if it was injected
- Command line carrying a password argument or a speed flag — The Gentlemen requires a build-specific password and accepts `--fast` / `--superfast` / `--ultrafast`

**Capture `windows.cmdline` output early.** For families with speed flags the command line tells you how much plaintext survived, which drives the entire recovery plan.

If the encryptor already exited, scan the whole image rather than one process. Freed heap pages often still hold the key.

### Validation is the actual work

`findaes` will hand you a list of candidates. To identify the right one:

1. **Take a file whose plaintext you know.** A default OS file, an application resource, or anything you hold in backup.
2. **Determine the scheme** — cipher, mode, IV/nonce location — from [Module 02](../02-Hybrid-Encryption-Model/) and the footer analysis.
3. **Attempt decryption with each candidate.**
4. **Check for structure**, not for absence of errors. A correct key produces a valid file header. A wrong key produces noise that decrypts without complaint.

The header check is the whole test. `parse_footer.py` will tell you whether the output looks like an intact format:

```bash
python3 ../02-Hybrid-Encryption-Model/labs/parse_footer.py ./recovered/test.jpg
# FORMAT   header: JPEG | extension implies: JPEG -> header matches extension
# VERDICT  NOT ENCRYPTED - intact JPEG
```

That output means the key is correct.

---

## 5. When it is harder

### ChaCha20 and XChaCha20

No expanded key schedule, so there is nothing to verify mathematically. The 32-byte key sits inside a 64-byte state block adjacent to the `expand 32-byte k` sigma constant.

Approach: locate the sigma constant, take the neighbouring 32 bytes as a candidate, test. Expect substantially more false positives than AES, and expect to test many candidates.

### Per-file keys

Families using a fresh key per file — including any per-file ephemeral ECDH scheme like The Gentlemen — mean **one recovered secret decrypts one file**. Confirm the key model before setting expectations. Compare footers across files:

```bash
for f in *.locked; do tail -c 512 "$f" | sha256sum | cut -d' ' -f1; done | sort -u | wc -l
# 1  → single session key. One recovery unlocks everything
# N  → per-file keys. One recovery unlocks one file
```

This single command changes the entire response strategy. Run it early.

### Prompt key destruction

A well-written encryptor zeroes each key immediately after use. You may recover only the key for the file being encrypted at the moment of capture. That is still worth having — it proves the scheme and validates your reconstruction.

### Paged-out memory

Key material may sit in `pagefile.sys` rather than RAM. Acquire it alongside the memory image and scan it too. Hibernation files are also worth checking on laptops.

---

## 6. BitLocker cases

Different mechanism, same doctrine. In a [Module 04](../04-Platform-And-LOTL-Encryption/) BitLocker attack the Volume Master Key may still be resident on a host that has not yet rebooted.

**But check key escrow first.** Recovery data in AD (`msFVE-RecoveryInformation`), Entra ID, or MBAM survives the attacker deleting local protectors, and querying it takes minutes. Memory forensics is the fallback, not the opening move.

Once the host reboots it will not boot at all, so the acquisition urgency is higher here than anywhere else in this curriculum.

---

## 7. Lab

Produce a memory image safely without touching live malware:

1. Follow [`labs/SAFE_LAB_SETUP.md`](../labs/SAFE_LAB_SETUP.md).
2. Run the demo encryptor in a VM with a deliberate pause, or attach a debugger and break inside the encryption routine.
3. **Suspend the VM** — this writes RAM to a `.vmem` file with no in-guest tooling.
4. Scan the `.vmem` for the key. The demo prints the key at startup, so you have ground truth to check against.

```bash
python3 ../01-Symmetric-Cryptography/labs/encryption_demo.py hexdump | head -3
#   Demo key (AES-256, FIXED and PUBLIC): 3a7c...
```

Knowing the answer in advance is the point. It teaches you what a true positive looks like among the operating system's own AES keys, which is the skill that transfers.

---

## 8. Exercises

1. Acquire memory from a VM mid-encryption and recover the key. Record how many false candidates you rejected and how you rejected them.
2. Write the "don't power it off" argument as three sentences a non-technical executive will accept. Practise saying it out loud.
3. Determine the key model (session vs per-file) for a specimen set using only footer comparison. How many files do you need before you are confident?
4. Repeat exercise 1 against a ChaCha20 specimen. Quantify how much harder it is.
5. Your client rebooted every affected host before calling you. Write the paragraph explaining what that cost them, without blame and without overstating what would have been recovered.

---

## 9. References

- *The Art of Memory Forensics* — Ligh, Case, Levy, Walters. The standard text
- **SANS FOR508** — Advanced Incident Response and Memory Forensics
- **SANS FOR498** — Digital Acquisition, directly relevant to section 2
- [13cubed](https://www.13cubed.com/) — free memory forensics walkthroughs
- Volatility 3 documentation · WinPmem · `findaes` · `bulk_extractor`

---

| ◄ [Module 06: Case Studies](../06-Case-Studies/) | [Module 08: Reverse Engineering](../08-Reverse-Engineering/) ► |
|---|---|
