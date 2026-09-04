# Case Study — DeadLock

![Source](https://img.shields.io/badge/primary%20source-MSTIC%20Aug%202026-blue.svg)
![Scheme](https://img.shields.io/badge/scheme-XChaCha20%20%2B%20NaCl%20crypto__box-red.svg)

> Fine-grained striping that hides from entropy triage, throttling that hides from EDR, and infrastructure that survives takedown.

**Primary source:** Microsoft Threat Intelligence, [DeadLock ransomware: Breaking down a Rust-based encryptor with decentralized recovery infrastructure](https://www.microsoft.com/en-us/security/blog/2026/08/10/deadlock-ransomware-breaking-down-a-rust-based-encryptor-with-decentralized-recovery-infrastructure/) (10 August 2026).

---

## Why this case is in the curriculum

1. **Its striping defeated our tooling.** 512-byte blocks at computed intervals are invisible to a 4096-byte entropy window. Our recovery tool reported *100% recoverable* on a file with a tenth of it destroyed.
2. **Its throttling is designed against the Module 11 signals**, explicitly to look like normal resource consumption.
3. **It disables future logging**, not just clears logs — which changes what Module 09 can promise.
4. **Its infrastructure survives takedown**, which changes how an incident is scoped.

---

## 1. Operator and model

<cite index="16-1">Microsoft tracks DeadLock as an emerging financially motivated operation distinguished by decentralized infrastructure supporting victim communications and data leak operations, deployed by multiple groups including an affiliate of the Lynx and INC ransomware ecosystems.</cite>

<cite index="16-1">First observed in July 2025, the operators use double extortion. As of July 2026 they had published more than 80 organizations on their leak site, more than half in Europe, across IT, mining, transportation and logistics, manufacturing, hospitality and consumer goods, spanning Europe, Asia, North America, South America and Africa.</cite>

---

## 2. Cryptographic scheme

<cite index="16-1">A hybrid design combining Curve25519 elliptic-curve cryptography with the XChaCha20 stream cipher. Key encapsulation uses the NaCl `crypto_box` construction, pairing an asymmetric key exchange with authenticated encryption to wrap each file's symmetric key.</cite>

| Layer | Algorithm | Purpose |
|---|---|---|
| File content | **XChaCha20** | Symmetric stream cipher |
| Key encapsulation | **Curve25519 ECDH + XSalsa20-Poly1305** (NaCl `crypto_box`) | Asymmetric key wrapping |
| Randomness | **Windows CryptoAPI** | All key material |

Per file, <cite index="16-1">the malware generates a 32-byte XChaCha20 key, a 24-byte nonce (first 16 bytes for HChaCha20 subkey derivation, last 8 as the stream nonce), a 32-byte ephemeral Curve25519 private key, a 12-byte random file tag whose first byte derives the padding length, and 1–10 bytes of random padding.</cite> It then <cite index="16-1">performs ECDH against the attacker's embedded public key, builds a metadata plaintext of key + nonce + padding + a `dDlK` magic + optional `FA` flag + chunk parameters, encrypts that metadata with `crypto_box` using a zero nonce, encrypts the file content with XChaCha20, and appends the encrypted footer.</cite>

**The zero nonce is safe here, and knowing why matters.** <cite index="16-1">Each file generates a unique ephemeral Curve25519 keypair, producing a unique ECDH shared secret, so a constant zero nonce never repeats with the same key.</cite> A zero nonce is normally a textbook implementation bug and a recovery path — here it is not, because the key never repeats. Do not report it as a weakness.

<cite index="16-1">MSTIC's assessment is that the construction is sound and does not present a practical path to decryption without the attacker's private key.</cite>

### A quirk worth knowing

<cite index="16-1">The operator public key is 33 bytes with a leading `03` byte — a SEC1 compressed-point prefix borrowed from Bitcoin/secp256k1. The malware validates the prefix against a lookup accepting `00`, `02`, `03`, `04` and `05`, then uses only the remaining 32 bytes in the Curve25519 scalar multiplication. The SEC1 prefix is non-standard for Curve25519, which natively uses bare 32-byte keys, and was likely adopted for format versioning across the builder and decryptor tooling.</cite>

For an analyst: **a 33-byte key with a `03` prefix is not necessarily secp256k1.** Check what the code actually does with it before attributing the curve.

---

## 3. The striping that broke our tooling

<cite index="16-1">A tiered policy based on file size, encoded in the configuration string `1000,05052429880,025124288000,010524288000,F991114288000`. Each comma-separated entry splits at position 3: the first 3 characters are the encryption percentage, the remainder is the file size threshold in bytes. An `F` prefix replaces the percentage with a chunked-full mode.</cite>

| Rule | Percent | Threshold | Behaviour |
|---|---|---|---|
| `1000` | 100% | ≥ 0 | Encrypt entire file |
| `05052429880` | 50% | ≥ ~50 MB | 50% in distributed chunks |
| `025124288000` | 25% | ≥ ~118 MB | 25% in distributed chunks |
| `010524288000` | 10% | ≥ ~500 MB | 10% in distributed chunks |
| `F991114288000` | chunked | ≥ ~1 GB | Special full-chunk mode |

<cite index="16-1">Rules are evaluated in order and the last matching rule wins.</cite> Note the inversion: **the bigger the file, the less of it is encrypted.**

<cite index="16-1">For partial encryption the malware computes total bytes to encrypt as `ceil(file_size × percentage/100)`, block count as `ceil(total_bytes / 512)`, and skip interval as `floor((file_size − total_bytes) / block_count)`, producing an intermittent pattern where 512-byte blocks are encrypted at regular intervals throughout the file.</cite>

### Why that hid from us

Apply the formula to a 40 MB file at the 10% rule: **512 encrypted bytes every 4,607.**

Our triage used a 4096-byte entropy window. Each window contained ~512 random bytes and ~3,584 plaintext bytes — roughly 12% random, which normalizes far below any ciphertext threshold. Running the real numbers:

```
BEFORE (4096-byte window)
  encrypted               0 bytes  (  0.0%)
  RECOVERABLE    40,000,378 bytes  (100.0%)      <-- WRONG
```

The tool would have handed a responder a corrupted database while reporting it intact. `parse_footer.py` only flagged the file at all because `.dlock` had been appended to the name — the entropy classifier saw nothing.

Both tools now run a **multi-scale pass**: when the coarse scan reports a file as essentially clean, they re-check at 512-byte resolution before concluding.

```
AFTER
  encrypted       2,878,330 bytes  (  7.2%)
  RECOVERABLE    37,122,048 bytes  ( 92.8%)
  runs                5,621   largest 669,696 bytes

  ** FINE-GRAINED STRIPING DETECTED **
```

### The recovery nuance that matters more than the percentage

92.8% recoverable sounds excellent. It is not, and this is the important lesson.

With damage every ~4,607 bytes, an 8 KB SQL Server page contains a stripe **almost every time**. The surviving runs are short — 5,621 of them, versus 2 runs for a distributed-chunk family at a similar percentage. **Contiguity matters more than volume** for structured formats.

| | Distributed-chunk (The Gentlemen) | Fine striping (DeadLock) |
|---|---|---|
| Recoverable | ~91% | ~93% |
| Surviving runs | 2 | 5,621 |
| Longest run | ~2 MB | ~670 KB |
| 8 KB DB pages intact | nearly all | nearly none |

Report both numbers. A percentage without a run count overstates what the client gets back.

### The footer

<cite index="16-1">The cleartext ephemeral Curve25519 public key (33 bytes) at the end of the footer lets the decryptor recompute the ECDH shared secret and open the `crypto_box`. An inner `dDlK` marker at offset 32 + 24 + padding_length inside the decrypted plaintext confirms the correct key was used. An `FA` flag indicates sequential/contiguous encryption and is absent when intermittent/skip encryption was used, resolving what would otherwise be ambiguity in the 8-byte chunk parameters — they could represent either a block count or a skip interval.</cite>

**For a responder, the `FA` flag tells you which recovery strategy applies before you run anything.**

---

## 4. Evasion aimed at the detection signals

### Resource-aware throttling

<cite index="16-1">A dedicated monitoring/dispatch thread per drive batch gates file dispatch. Before dispatching each file it polls memory and CPU idle, and if memory usage exceeds 29% or CPU load exceeds 70% (idle under 30%), it pauses on a waitable timer and retries until resources fall below the thresholds.</cite>

<cite index="16-1">Worker threads already encrypting are not interrupted, so throttling manifests as reduced parallelism rather than stop/start behaviour. Microsoft notes this can prevent system hangs that would alert the user and reduce the likelihood of behavioural detection by maintaining normal-looking resource consumption patterns.</cite>

This is aimed directly at [Module 11](../../11-Endpoint-Detection/): file-modification-rate thresholds and CPU-based heuristics both assume ransomware is loud. **Rate-based detection degrades against an encryptor that deliberately stays quiet.** Weight breadth, format mismatch, and canaries accordingly.

<cite index="16-1">Directory processing threads are spawned at twice the CPU core count.</cite>

### Logging: disabled, not just cleared

<cite index="16-1">Three complementary methods: direct clearing of Application, Security, Setup, Servicing, Eventlog, Forwarded Events, Windows PowerShell and System via the classic Event Log API; registry-based disabling that enumerates every sub-key under `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WINEVT\Channels`, sets `Enabled` to 0 and overwrites `ChannelAccess` with a restrictive SDDL string; and enumeration via `wevtapi.dll` to find all registered channels including custom application channels not in the hardcoded list.</cite>

**This goes beyond clearing.** Future logging is switched off and channel permissions are locked down. A responder arriving afterwards has no local event logs *and no new ones being written*. [Module 09](../../09-Triage-and-IR/)'s tier-1 artifacts — `$MFT`, `$UsnJrnl`, and forwarded copies — are not optional here, they are all you have.

### Other pre-encryption behaviour

<cite index="16-1">The configuration blob is XOR-decoded with an 8-byte key. As an early exit the malware queries the default and UI languages and self-deletes without encrypting if either matches its exclude list</cite> — 17 LANGIDs covering CIS states and select Middle Eastern countries.

<cite index="16-1">When not elevated it writes a randomly named 8-uppercase-character `.cmd` file and runs it via `ShellExecuteW` with the `RunAs` verb to trigger UAC, retrying up to 10 times.</cite> When elevated it <cite index="16-1">enables SeDebugPrivilege, SeRestorePrivilege, SeBackupPrivilege, SeTakeOwnershipPrivilege, SeAuditPrivilege and SeSecurityPrivilege</cite>, <cite index="16-1">silently empties the recycle bin on all drives</cite>, and <cite index="16-1">registers a custom icon for `.dlock` files via `HKLM\SOFTWARE\Classes\.dlock\DefaultIcon`.</cite>

<cite index="16-1">It disables and stops services including windefend, vss, swprv, wbengine, mssearch, Hyper-V services and Active Directory services, and terminates processes including security tools, OneDrive, Dropbox, remote access tools and shell processes.</cite>

**An analyst gotcha worth repeating:** <cite index="16-1">the text ransom note is only deployed on the second pass of the directory processing loop, so testing with a minimal drive configuration that triggers only a single iteration means the note never appears.</cite> If you detonate and see no note, that is not evidence of a different family.

---

## 5. Infrastructure that survives takedown

<cite index="16-1">Rather than domain-based infrastructure that can be seized, the operators store configuration on the Polygon blockchain in two smart contracts — one holding the chat proxy URL, one holding blog posts. The HTML recovery page issues `eth_call` requests to public Polygon RPC endpoints, requiring no wallet for read-only calls, and cycles through six public endpoints for redundancy.</cite>

<cite index="16-1">Victim-operator chat is routed through the Session decentralized messenger, an onion-routed swarm-based protocol, with the blockchain-supplied proxy relaying between the victim's browser and Session swarm nodes. Stolen data is hosted on Wasabi, with the HTML page containing a full S3-compatible browser that generates AWS4-HMAC-SHA256 signed requests and pre-signed download URLs.</cite>

<cite index="16-1">The victim's Session identity is derived deterministically from their sign-in credentials, so the same credentials always reproduce the same keypair and no registration is needed — but if the victim forgets them the identity is unrecoverable.</cite>

**Not fully takedown-proof.** <cite index="16-1">The page still requires access to at least one public Polygon RPC endpoint, chat depends on the current proxy remaining reachable, and images and leaked files can be removed from Wasabi hosting.</cite>

**IR implication:** attacker infrastructure can change mid-incident without the victim-side artifacts changing at all. Do not treat a blocked proxy as containment, and expect leak-site addresses to move.

---

## 6. Response notes

- **Determine the encryption rule early.** File size decides the paradigm, so a share can contain fully encrypted small files and 10%-striped large ones simultaneously.
- **Report run count alongside recoverable percentage.** Fine striping produces thousands of short runs; contiguity governs whether a structured format survives.
- **Assume no local logs at all.** Logging is disabled going forward, not just cleared.
- **Do not report the zero `crypto_box` nonce as a weakness.** Per-file ephemeral keys make it safe.
- **Check the `FA` flag** to learn the encryption strategy before choosing a recovery approach.
- <cite index="16-1">Microsoft's mitigations include tamper protection, EDR in block mode, controlled folder access configured as strictly as possible, automatic attack disruption, and the ASR rules blocking process creation from PsExec and WMI and blocking executables that fail prevalence/age/trust criteria.</cite>

IOCs and Defender detections are in the source and are maintained there.

---

## 7. Exercises

1. Reproduce the striping with MSTIC's formula at each configured percentage. At which does `recover_partial.py` stop detecting it, and why?
2. A 2 GB VM disk and a 200 KB document are on the same share. Predict the paradigm for each from the encryption rule and verify.
3. Explain to a client why 93% recoverable and 5,621 runs is a worse outcome than 91% recoverable and 2 runs.
4. Given logging disabled via `WINEVT\Channels`, list every artifact you can still build a timeline from.

---

## 8. References

- **Primary:** [MSTIC — DeadLock ransomware](https://www.microsoft.com/en-us/security/blog/2026/08/10/deadlock-ransomware-breaking-down-a-rust-based-encryptor-with-decentralized-recovery-infrastructure/), 10 August 2026
- [The Gentlemen case study](../the-gentlemen/) — contrast in striping strategy
- [Module 03](../../03-Encryption-Paradigms/) · [Module 09](../../09-Triage-and-IR/) · [Module 10](../../10-Recovery-and-Decryption/) · [Module 11](../../11-Endpoint-Detection/)
