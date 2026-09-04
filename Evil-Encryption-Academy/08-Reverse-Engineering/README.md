# Module 08 — Reverse Engineering

![Difficulty](https://img.shields.io/badge/difficulty-advanced-red.svg)
![Time](https://img.shields.io/badge/time-5--8%20hours-blue.svg)
![Prereq](https://img.shields.io/badge/prereq-Modules%2001--02-lightgrey.svg)

> Finding the crypto and the embedded public key in a stripped, statically linked, obfuscated binary.

**Prerequisites:** [Modules 01–02](../01-Symmetric-Cryptography/), and comfort in a disassembler.

---

## 1. The problem has changed

The classic workflow — open the binary, read the import table, see `CryptEncrypt`, done — still works on older families. It does not work on what you will actually be handed.

Modern ransomware is written in **Go or Rust**, statically linked and often obfuscated. There is no `bcrypt.dll` in the import table because the crypto is compiled in. There are no helpful symbol names. And 90%+ of the code is standard library and runtime, not attacker logic.

| | Classic C/C++ | Go / Rust |
|---|---|---|
| Import table | Reveals the crypto APIs | Nearly empty |
| Symbols | Often present | Stripped or mangled |
| Code volume | Mostly attacker logic | Mostly library and runtime |
| Primary route | Read the IAT | **Constants, then cut the library noise** |

So the work splits into two questions: *which crypto is present*, and *which of this code did the attacker actually write*.

---

## 2. Triage before you disassemble

Answer these in the first ten minutes. Each one changes what you do next.

**Is it packed?** Whole-file entropy above ~7.5 with a very small import table means the real code is encrypted until runtime. **Constant scanning will find nothing until you unpack.** Dump from memory after the unpacking stub runs, then restart your analysis on the dump.

**What language is it?**

| Language | Tell |
|---|---|
| **Go** | `Go build ID:`, `runtime.` symbols, the `pclntab` structure |
| **Rust** | `/rustc/` build paths, `core::panicking`, ``called `Option::unwrap()` `` |
| C/C++ with CNG | `bcrypt.dll` in the IAT |
| C/C++ with CAPI | `advapi32.dll`, `CryptAcquireContext` |
| .NET | CLR header, analyse with dnSpy/ILSpy instead |

**What crypto is present?**

```bash
python3 tools/identify_crypto.py sample.exe
```

Against the capstone's recovered binary this returns, in seconds:

```
[HIGH]   ChaCha/Salsa sigma (256-bit)      expand 32-byte k
[HIGH]   Poly1305 clamp                    AEAD
[MEDIUM] Curve25519 a24 constant           121665
[HIGH]   Go build ID                       statically linked
[MEDIUM] Garble obfuscation

* POSSIBLE HYBRID SCHEME ... CONFIRM IN A DISASSEMBLER before giving any
  recoverability verdict either way.
```

> **Run it without `--min-confidence`.** Asymmetric markers such as the Curve25519 constant are medium confidence. Filtering to `high` hides exactly the evidence a recoverability verdict depends on — see the capstone's second trap.

Full constant reference: [`references/CIPHER-IDENTIFICATION.md`](../references/CIPHER-IDENTIFICATION.md).

---

## 3. Cutting through library noise

This is the defining problem with Go and Rust samples. A constant hit tells you the *library* contains AES. It does not tell you the malware calls it. A statically linked Rust binary can produce hits for AES both directions, Blowfish, ChaCha20, secp256k1 and P-256 from a crypto crate where the program uses one of them.

**You need to separate attacker-written code from compiled-in library code.**

### Rust: use RIFT

Microsoft Threat Intelligence open-sourced **RIFT** in June 2025 for exactly this. <cite index="6-1">It is designed to help analysts automate identification of attacker-written code within Rust binaries</cite>, addressing the problem that <cite index="1-1">Rust's abstractions produce binaries that are harder to decompile, leaving analysts grappling with unfamiliar patterns and library-heavy output</cite>.

<cite index="4-1">The toolkit has three components — a static analyzer, a generator, and a diff applier — and uses two pattern-matching techniques: FLIRT signatures and binary diffing.</cite>

The workflow is clever and worth understanding rather than just running:

1. **Static Analyzer** extracts compiler and dependency information from the sample into JSON.
2. **Generator** <cite index="1-1">downloads the matching Rust compiler and dependencies, compiles them, then extracts COFF files from the resulting RLIB archives</cite> to build FLIRT signatures for precisely the library code in *this* binary.
3. **Diff Applier** <cite index="5-1">is an IDA plugin that applies the FLIRT and binary-diffing results in IDA, labelling library functions in the malware.</cite>

<cite index="1-1">It uses `idat.exe`, IDA's text-mode interface, to automate the disassembly, and the open-source Diaphora project for binary diffing.</cite> <cite index="4-1">Microsoft applied it to the RALord ransomware, where it extracted compiler information and let analysts isolate the malicious logic, substantially reducing analysis time.</cite>

The key insight: rather than using generic signatures, it **rebuilds the exact library code from the exact compiler version** the sample used, so matches are precise. What remains unlabelled is attacker code.

Requires IDA Pro. If you are on Ghidra, the equivalent is manual: identify the compiler version, build reference binaries with the same toolchain, and diff.

### Go: recover names from `pclntab`

Go binaries embed a **`pclntab`** (program counter line table) mapping addresses to function names, used by the runtime for stack traces. It usually survives stripping, so function names are frequently recoverable even from a "stripped" Go binary.

Tools: **GoReSym** (Mandiant) and **redress**. Recovering `main.encryptFile` from a stripped binary is a very fast route to the crypto.

**Garble breaks this.** It mangles names and strips build info, which is why The Gentlemen is harder than an ordinary Go sample. When names are gone, fall back to constants and to xrefs from the crypto constants outward.

---

## 4. Locating the crypto in a disassembler

### Work outward from the constants

The most reliable route in any stripped binary:

1. Locate the constant (S-box, sigma string, curve parameter) in the data section.
2. **Cross-reference it.** Whatever reads it is the cipher implementation.
3. Cross-reference *that* function. Its callers are the encryption routine.
4. The caller of the encryption routine is usually the file-handling loop.

This works regardless of language, obfuscation, or stripping, because the constants cannot be removed without breaking the algorithm.

### Ghidra

- Apply **Function ID** databases to label known library functions.
- Define the CNG structures (`BCRYPT_KEY_HANDLE`, `BCRYPT_OAEP_PADDING_INFO`) so the decompiler output becomes readable.
- Use **Search → Memory** for the byte patterns in the cipher catalog.
- Retype the buffer parameters. Decompiler output is far more legible once `void*` becomes `BYTE[32]`.

### x64dbg — the highest-value breakpoints

If you can run the sample safely ([`labs/SAFE_LAB_SETUP.md`](../labs/SAFE_LAB_SETUP.md)), dynamic analysis short-circuits a lot of static work.

| Breakpoint | Why |
|---|---|
| **`BCryptGenerateSymmetricKey`** | **`pbSecret` is the plaintext key.** The single most valuable breakpoint in ransomware analysis |
| `BCryptImportKeyPair` | The blob passed in *is* the attacker's embedded public key. Dump it |
| `CryptExportKey` | With a non-NULL `hExpKey`, this call **is** the CAPI key wrap |
| `BCryptEncrypt` | Confirms mode and IV handling |
| `CreateFileW` / `WriteFile` | The file loop, and the target-selection logic |

On x64 Windows, arguments 1–4 arrive in `RCX`, `RDX`, `R8`, `R9`; further arguments are on the stack. For `BCryptGenerateSymmetricKey(hAlg, phKey, pbKeyObject, cbKeyObject, pbSecret, cbSecret, flags)`, **`pbSecret` is argument 5**, at `[rsp+0x28]` on entry. Follow that pointer in the dump window and you are looking at the key.

Statically linked Go/Rust samples that implement crypto internally will not hit these breakpoints at all — another reason to identify the language first.

---

## 5. The embedded public key

Find it and extract it. It is a durable campaign identifier — far more stable than a hash — and it confirms the scheme.

| Form | Search for |
|---|---|
| PEM | `-----BEGIN PUBLIC KEY-----` |
| DER SPKI | `2a 86 48 86 f7 0d 01 01 01` (rsaEncryption OID) |
| CNG/CAPI blob | `RSA1`, `ECK1` magics |
| Raw ECC | A 32-byte constant near the curve parameters |
| Base64 | A 44-character base64 run decoding to 32 bytes |

```bash
python3 tools/identify_crypto.py sample.exe --categories asymmetric
```

**Watch for base64.** Modern families frequently store keys as text, which entropy-based scanning cannot see. That blind spot cost this repository a real bug — see [The Gentlemen case study](../06-Case-Studies/the-gentlemen/).

---

## 6. The question that actually matters: where did the key come from?

Everything above is groundwork for one question, because it determines recoverability.

Trace backwards from `pbSecret` (or the equivalent buffer) to its source:

| Source | Recovery outlook |
|---|---|
| `BCryptGenRandom` / OS CSPRNG | **None.** Cryptographically sound |
| Per-file ephemeral ECDH | **None.** Current state of the art |
| PBKDF2/Argon2 over a strong password | None, unless the password is recoverable |
| **KDF over a timestamp, PID, or hostname** | **Searchable key space. Build a decryptor** |
| `rand()` seeded from `time()` | **Searchable. This is how most public decryptors exist** |
| Hardcoded or embedded key | Full recovery |

**Almost every published ransomware decryptor exists because of a bug on this line**, not because anyone broke a cipher. `identify_crypto.py` flags KDF presence specifically to send you here.

If the key comes from a CSPRNG and is wrapped asymmetrically, say so plainly and move to [Module 10](../10-Recovery-and-Decryption/). That is a finding, not a failure.

---

## 7. What to hand off

Your output feeds the recoverability assessment. Produce:

- **Scheme**: bulk cipher, mode, key wrap, key model (session vs per-file)
- **Key origin** — the section 6 answer, with the evidence
- **Footer/header layout**: offsets, delimiters, what is stored where
- **Encryption paradigm** and any speed flags in the command line
- **Extracted public key**, as a campaign identifier
- **Detection material**: constants, strings, structural YARA
- **Explicit uncertainty.** "Probably AES" is useless. "AES confirmed by S-box xref from the encryption routine; mode not yet determined" is actionable

---

## 8. Exercises

1. Run `identify_crypto.py` on the capstone binary with and without `--min-confidence high`. Explain precisely why the conclusions differ and which is safe to report.
2. Take any Go binary you built yourself, strip it, and recover function names with GoReSym. Then obfuscate with Garble and repeat. What survives?
3. Given only the AES S-box location in a stripped binary, work outward by xref to the file-handling loop. Document each hop.
4. For a family of your choice, trace the key source from published analysis and place it in the section 6 table. Was a decryptor ever released, and does that match your placement?

---

## 9. References

- <cite index="6-1">MSTIC — Unveiling RIFT: Enhancing Rust malware analysis through pattern matching</cite> (June 2025), and the RIFT repository
- Diaphora — binary diffing, used by RIFT
- GoReSym (Mandiant) and redress — Go symbol recovery
- *Practical Malware Analysis*, ch. 13 — crypto identification
- [`references/CIPHER-IDENTIFICATION.md`](../references/CIPHER-IDENTIFICATION.md) — the constant catalog
- SANS **FOR610**

---

| ◄ [Module 07: Memory Forensics](../07-Memory-Forensics/) | [Module 09: Triage and IR](../09-Triage-and-IR/) ► |
|---|---|
