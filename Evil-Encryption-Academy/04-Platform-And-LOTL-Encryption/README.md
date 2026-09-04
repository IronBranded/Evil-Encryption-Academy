# Module 04 — Platform & Living-off-the-Land Encryption

![Difficulty](https://img.shields.io/badge/difficulty-intermediate-orange.svg)
![Focus](https://img.shields.io/badge/focus-BitLocker%20%7C%20EFS%20%7C%20FDE-red.svg)

> The ransomware that ships no cryptography, because Windows already has some.

**Prerequisites:** [Module 02](../02-Hybrid-Encryption-Model/) for the key-wrapping model. Modules 00–03 assume the malware implements its own crypto. This module covers the growing share of incidents where it does not.

---

## Why this module exists

Every technique in Modules 01–03 assumes there is a cipher in the binary to find. Constants, imports, key schedules in RAM. That mental model fails completely against an attacker who runs:

```
manage-bde.exe -on C: -password
```

There is no cipher to reverse. No S-box, no import table, no key schedule in a process you can dump. Microsoft wrote the encryption, Microsoft signed the binary, and it is doing exactly what it was designed to do. Your YARA rules match nothing. Your memory scanner finds the key material of a legitimate OS feature.

**And it is faster and more destructive than most custom ransomware.** BitLocker encrypts the entire volume including the OS, so the victim does not lose files — they lose the ability to boot.

| | Custom encryptor | OS-native abuse |
|---|---|---|
| Artifact to reverse | PE with crypto | None. Signed Microsoft binaries |
| Detection surface | Imports, constants, entropy | Command lines, WMI, event logs |
| Scope | Files matching a target list | Entire volume, OS included |
| Anti-analysis | Packing, obfuscation | Nothing needed. It is legitimate |
| Recovery path | Attacker's private key | **Key escrow, sometimes immediate** |

That last row is why this module matters commercially. A BitLocker incident is sometimes recoverable in minutes, and only if someone checks.

---

## 1. How BitLocker actually works

Three layers, and the middle one is where attacks happen.

```
      YOUR DATA on the volume
             ▲
             │ encrypted with
             │
      FVEK  (Full Volume Encryption Key)
             ▲          AES-XTS-128/256 by default (Win10 1511+)
             │          AES-CBC 128/256 + Elephant diffuser (legacy)
             │ encrypted with
             │
      VMK   (Volume Master Key)          ◄── THE ATTACK SURFACE
             ▲
             │ protected by one or more PROTECTORS
             │
   ┌─────────┴──────────┬───────────┬──────────────┬─────────────┐
   TPM            TPM + PIN    Recovery      Startup key    Password
                               password       (USB)
                               (48 digits)
                                   │
                                   └── escrowed to AD / Entra ID / MBAM
```

The volume is never re-encrypted when protectors change. Add or remove a protector and only the small VMK-protection layer is rewritten. **That is why a BitLocker attack is near-instant on an already-encrypted volume** — the attacker is not encrypting terabytes, they are swapping the lock on the key.

The core of the attack is simple: **add a protector only the attacker knows, then delete every protector the victim knows.** The data never moves.

---

## 2. The abuse pattern

Two scenarios, and they need different responses.

**Scenario A — volume already BitLocker-encrypted.** The attacker adds a protector, removes the existing ones, discards or exfiltrates the recovery password, and reboots. Seconds of work. No bulk encryption occurs at all.

**Scenario B — volume not encrypted.** The attacker must enable BitLocker first, which requires more setup: registry changes to permit BitLocker without a TPM, sometimes repartitioning to create a boot volume, then a full encryption pass. Noisier and slower, and it leaves far more evidence.

### Case study: ShrinkLocker

<cite index="2-1">Discovered in May 2024 by Kaspersky, ShrinkLocker uses Windows' built-in BitLocker to lock victim files, and Bitdefender's later analysis found it was repurposed from roughly ten-year-old benign VBScript code using dated techniques.</cite> <cite index="4-1">Kaspersky identified it in Mexico, Indonesia, and Jordan against enterprise systems.</cite>

The operational sequence, as reported:

<cite index="2-1">It runs a WMI query to check whether BitLocker is available and installs it if absent, then strips the default protections that would normally prevent accidental encryption.</cite> <cite index="6-1">It gets its name from shrinking non-boot partitions to construct a boot volume, and it modifies registry entries to disable RDP and to permit BitLocker on hosts with no TPM.</cite> <cite index="1-1">It then re-encrypts the system using a randomly generated password.</cite>

The key handling is the interesting part forensically. <cite index="6-1">The encryption key is a 64-character construction built from random arithmetic and substitution against digits, special characters, and the pangram "The quick brown fox jumps over the lazy dog", delivered to the attacker through TryCloudflare — a legitimate Cloudflare Tunnel service. In the final stage it forces a shutdown so the changes take effect, leaving the drives locked with BitLocker recovery options removed.</cite>

<cite index="6-1">Notably it leaves no conventional ransom note; the contact address is set as the drive label, which led Kaspersky to suggest the campaign may be destructive rather than financially motivated.</cite> <cite index="7-1">The script also self-deletes after encrypting.</cite>

<cite index="3-1">Using Group Policy Objects and scheduled tasks it can encrypt systems across a network in around ten minutes per device.</cite>

**Recovery status:** <cite index="1-1">Bitdefender published a decryptor along with a detailed analysis of how the strain works.</cite> <cite index="2-1">Their analysis found the operators to be low-skilled, leaving redundant code, typos, and reconnaissance logs behind as text files.</cite> Check for a current decryptor before assuming loss.

BitLocker abuse predates ShrinkLocker. <cite index="6-1">One actor used it against 40 servers at a Belgian hospital covering 100TB of data, and another against a Moscow meat producer.</cite>

---

## 3. Finding it

Because there is no binary to analyze, detection is entirely behavioral. These are the signals worth hunting, ordered by reliability.

### Command line and script execution

| Indicator | Why it matters |
|---|---|
| `manage-bde -on`, `-protectors -add`, `-protectors -delete`, `-forcerecovery` | The BitLocker CLI. Protector deletion is the hostile step |
| `Enable-BitLocker`, `Add-BitLockerKeyProtector`, `Remove-BitLockerKeyProtector`, `Disable-BitLocker` | PowerShell BitLocker module |
| `BackupToAAD-BitLockerKeyProtector` **absent** where policy requires it | Encryption deliberately kept out of escrow |
| WMI calls against `Win32_EncryptableVolume` | ShrinkLocker's primary interface. Methods include `ProtectKeyWithNumericalPassword`, `ProtectKeyWithPassphrase`, `DisableKeyProtectors` |
| `cscript` / `wscript` running `.vbs` on a server | VBScript on a domain controller is almost never legitimate |
| `diskpart` shrink operations near BitLocker activity | Repartitioning to create a boot volume |

Source these from Security 4688 (with command-line auditing enabled), Sysmon Event ID 1, and PowerShell Script Block Logging (Microsoft-Windows-PowerShell/Operational, Event ID 4104). **Script block logging is the highest-value control for this threat** — it captures the VBScript or PowerShell body even when the file self-deletes.

### Registry

`HKLM\SOFTWARE\Policies\Microsoft\FVE` is the BitLocker policy key. Watch for values appearing on a host that never had a BitLocker policy, particularly `EnableBDEWithNoTPM` and `UseAdvancedStartup`. Enabling BitLocker without a TPM is a deliberate choice, and on a corporate host with a TPM it is a strong hostile signal.

### On disk

BitLocker volumes carry the `-FVE-FS-` signature in the volume boot record. Useful when triaging a disk image where you cannot boot the host:

```bash
python3 ../tools/identify_crypto.py /evidence/disk.img --categories container
```

### Event logs

Relevant channels:

- `Microsoft-Windows-BitLocker/BitLocker Management`
- `Microsoft-Windows-BitLocker-API/Management`
- `System` (provider `Microsoft-Windows-BitLocker-Driver`)
- `Microsoft-Windows-MBAM/*` where MBAM is deployed

> **On event IDs.** Published BitLocker event ID lists contradict each other badly, including on what common IDs such as 24620 mean, and the meanings vary across Windows builds. Rather than copying a list that may be wrong for your environment, enumerate the channel on a representative build and record what you actually observe:
>
> ```powershell
> Get-WinEvent -ListProvider Microsoft-Windows-BitLocker-API |
>     Select-Object -ExpandProperty Events |
>     Select-Object Id, Description
> ```
>
> Build that mapping once for your estate and keep it under version control. A wrong event ID in a detection rule is worse than no rule, because it produces confident silence.

Correlate with **System 1074** (shutdown initiated) and **Security 4608/4609**. A forced reboot immediately after protector changes is the signature of the attack completing.

---

## 4. Responding to it

**Check key escrow before anything else.** This is the single highest-value action in a BitLocker incident and it is routinely missed while responders start imaging disks.

1. **Active Directory** — recovery data is stored on `msFVE-RecoveryInformation` child objects under the computer object. If escrow was configured, the key may still be there even though the attacker deleted the local protector.
2. **Entra ID / Intune** — recovery keys under the device record.
3. **MBAM / Configuration Manager** — the BitLocker management database.
4. **Printed or file-saved recovery keys** — check user profiles and any `BitLocker Recovery Key *.txt` on other drives or in cloud sync folders.

Escrowed recovery data survives local protector deletion. The attacker removed the lock on the door; the spare key may be sitting in your directory.

Then, in order: identify the strain, check for a public decryptor (ShrinkLocker has one), preserve the VBScript or PowerShell body from script block logs, and check whether the recovery password was exfiltrated and to where.

**Do not reboot hosts that are still running.** A host mid-attack that has not yet restarted may still have the VMK resident in memory. The Module 02 acquisition doctrine applies with even more force here, because after the reboot the machine will not boot at all.

---

## 5. The wider living-off-the-land category

BitLocker is the most common but not the only OS-native encryption abused for extortion.

| Mechanism | How it is abused | Where to look |
|---|---|---|
| **EFS** (Encrypting File System) | `cipher.exe` encrypts files under an attacker-controlled certificate; `cipher /w` wipes free space to defeat carving | Certificate store additions, `cipher.exe` execution, `$EFS` attribute in `$MFT` |
| **VeraCrypt / DiskCryptor / BestCrypt** | Legitimate signed FDE tools deployed as the encryptor | Service and driver installs (System 7045), installer artifacts, container headers |
| **7-Zip / WinRAR / WinZip** | Archive with AES-256 password, originals deleted. Doubles as the exfil stage | Archive tool execution with `-p`, large archive creation, mass deletes in `$UsnJrnl` |
| **SQL Server TDE** | Database encrypted with an attacker-controlled certificate | `sys.dm_database_encryption_keys`, certificate creation in SQL audit logs |
| **ESXi / vSphere native encryption** | Hypervisor encrypts VMs wholesale; one action locks hundreds of workloads | `vim-cmd` and `esxcli` history, `hostd.log`, `vpxa.log`, KMS config changes |
| **Cloud storage SSE-C** | Objects rewritten with a customer-supplied key held only by the attacker | CloudTrail `CopyObject` / `PutObject` with SSE-C headers, sudden `x-amz-server-side-encryption-customer-*` usage |
| **LUKS / dm-crypt** | Linux and NAS equivalent of the BitLocker attack | `cryptsetup` history, `LUKS\xba\xbe` header magic |

The common thread: **the encryption is performed by trusted, signed, expected software**, so control-plane logging replaces binary analysis as your primary evidence source. If your detection strategy is entirely file- and process-reputation based, this whole category is invisible to it.

---

## 5b. ESXi and Linux hypervisors — the highest-impact case

One `esxcli` or `vim-cmd` action can encrypt hundreds of VMs at once. ESXi is arguably the highest-impact target in the whole threat model, and its forensics are unlike everything else in this repository.

**Why it is different:**

- **No EDR agent.** ESXi does not run Windows security tooling. Most estates have zero endpoint visibility on the hypervisor.
- **No `$MFT`, no `$UsnJrnl`, no Volatility profile.** The Windows artifact set does not exist.
- **The VMs are just files.** Encrypting `.vmdk` and `.vmx` files is far cheaper than encrypting guest filesystems, and it takes every workload down at once.
- **Datastores are shared.** One compromised host reaches storage used by many others.

**Two distinct attacks:**

| Attack | Mechanism | Signal |
|---|---|---|
| **File-level encryption of VM disks** | An ELF encryptor run on the host encrypts `.vmdk`/`.vmx` in the datastore | Files renamed in `/vmfs/volumes`, VMs failing to power on |
| **Native vSphere VM encryption** | Legitimate encryption enabled with an attacker-controlled KMS | KMS configuration change, VM encryption state change |

**Where to look:**

- `/var/log/hostd.log`, `/var/log/vpxa.log`, `/var/log/shell.log`, `/var/log/auth.log`
- `/var/log/vmware/` on vCenter
- `esxcli system account list` for added accounts
- SSH enablement and the ESXi Shell — normally disabled, and enabling them is a strong signal
- `/vmfs/volumes/<datastore>/` for renamed or newly extensioned files
- Snapshot deletion across many VMs in a short window

**Controls that matter:** lockdown mode, SSH disabled by default, hypervisor management on an isolated network, MFA on vCenter, and patching — MSTIC has documented ransomware operators exploiting an ESXi hypervisor vulnerability specifically to achieve mass encryption ([`PRIMARY_SOURCES.md`](../references/PRIMARY_SOURCES.md)).

**Recovery angle:** VM disks are large, so fast-mode partial encryption applies to them. `recover_partial.py` works on `.vmdk` files, and the guest filesystem inside is often substantially intact — see [Module 10](../10-Recovery-and-Decryption/).

**Linux equivalents:** LUKS/dm-crypt abuse follows the BitLocker pattern (`cryptsetup` history, `LUKS\xba\xbe` header magic), and NAS appliances are targeted the same way.

## 6. Detection content

```yara
rule LOTL_BitLocker_Abuse_Script
{
    meta:
        description = "Script referencing BitLocker control interfaces used for volume encryption"
        reference   = "04-Platform-And-LOTL-Encryption"
        note        = "TRIAGE AID. Legitimate admin scripts match. Context decides."

    strings:
        $wmi1 = "Win32_EncryptableVolume"        ascii wide nocase
        $wmi2 = "ProtectKeyWithNumericalPassword" ascii wide nocase
        $wmi3 = "ProtectKeyWithPassphrase"        ascii wide nocase
        $ps1  = "Enable-BitLocker"                ascii wide nocase
        $ps2  = "Remove-BitLockerKeyProtector"    ascii wide nocase
        $cli  = "manage-bde"                      ascii wide nocase
        $hostile1 = "DisableKeyProtectors"        ascii wide nocase
        $hostile2 = "-forcerecovery"              ascii wide nocase
        $reg  = "EnableBDEWithNoTPM"              ascii wide nocase

    condition:
        2 of ($wmi*, $ps*, $cli) and 1 of ($hostile*, $reg)
}
```

**Sigma logic to implement** (behavioral, higher fidelity than the YARA rule):

- Protector removal (`Remove-BitLockerKeyProtector`, `manage-bde -protectors -delete`) by any process — should be near-zero in a healthy estate
- BitLocker enablement on a host with no prior BitLocker policy
- `EnableBDEWithNoTPM` set on a machine that has a TPM
- Any BitLocker configuration change followed by a forced shutdown inside 10 minutes
- `cscript`/`wscript` spawning from a service account or on a domain controller
- Outbound connections to tunnelling services (`trycloudflare.com` and similar) from a host with recent BitLocker activity

---

## 7. Exercises

1. In a lab VM, enable BitLocker normally and capture the full artifact set: command line, registry, event log entries, `-FVE-FS-` on disk. Build the event ID mapping for your Windows build.
2. Add a second protector, then remove the first. Which artifacts distinguish this from routine key rotation? This is the hard detection problem in this module.
3. Write the escrow-check runbook for your own environment: exact AD query, exact Entra portal path, exact MBAM query. Time yourself executing it. That number is your best-case recovery time.
4. A client reports servers that will not boot and show a BitLocker recovery prompt. List, in order, the first five actions — and justify why imaging the disk is not first.

---

## 8. References

- Kaspersky Securelist — original ShrinkLocker analysis (May 2024)
- [Bitdefender — ShrinkLocker analysis and decryptor](https://www.bitdefender.com/en-us/blog/businessinsights/shrinklocker-decryptor-from-friend-to-foe-and-back-again)
- Microsoft Learn — BitLocker operations guide, recovery guide, and Group Policy reference
- Microsoft Learn — [BitLocker event logs](https://learn.microsoft.com/en-us/intune/configmgr/protect/tech-ref/bitlocker/about-event-logs)
- [No More Ransom](https://www.nomoreransom.org/) — check before declaring data lost
- SANS FOR500 for Windows artifact grounding; FOR509 for the cloud variants

---

| ◄ [Module 03: Encryption Paradigms](../03-Encryption-Paradigms/) | [Module 05: Windows Crypto Internals](../05-Windows-Crypto-Internals/) ► |
|---|---|
