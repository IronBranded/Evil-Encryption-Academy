# Module 05 — Windows Crypto Internals

![Difficulty](https://img.shields.io/badge/difficulty-advanced-red.svg)
![Position](https://img.shields.io/badge/read-last-lightgrey.svg)

> Where key material actually lives, from API call to heap allocation to key storage provider.

**Prerequisites:** [Module 02](../02-Hybrid-Encryption-Model/) and ideally [Module 07](../07-Memory-Forensics/).

**This module is deliberately last.** The internals are far easier once you have watched the APIs get used and tried to pull a key out of a memory image. Read it when "the key is in RAM" has stopped being an abstraction.

---

## 1. Correcting the thing everyone is told

A claim you will see repeatedly, including in curricula and course outlines:

> *"Ransomware's ephemeral keys are held in `lsass.exe` memory."*

**This is wrong, and acting on it wastes the recovery window.**

`lsass.exe` hosts the **CNG Key Isolation service (`KeyIso`)**, which performs operations for *persisted private keys* that are marked for isolation, and it holds **DPAPI master keys** and cached credentials. That is real and it matters — for credential theft, and for decrypting DPAPI-protected material.

It is not where a ransomware file-encryption key lives.

When an encryptor calls `BCryptGenerateSymmetricKey`, the key material and its expanded schedule are placed in a **buffer the caller allocated in its own process heap**. No system process is involved. There is no isolation, no service boundary, nothing marshalled across a process.

| Key material | Where it lives | Dump which process? |
|---|---|---|
| **Ephemeral AES/ChaCha20 file key** | The **encryptor's own heap** | **The encryptor** |
| Expanded AES key schedule | The encryptor's key object buffer | The encryptor |
| DPAPI master keys | `lsass.exe` | `lsass.exe` |
| Persisted isolated private keys | `lsass.exe` (`KeyIso`) | `lsass.exe` |
| Cached domain credentials | `lsass.exe` | `lsass.exe` |

**Practical consequence:** in [Module 07](../07-Memory-Forensics/) you dump the *encryptor* process, not LSASS. Dumping LSASS for an AES file key returns Windows' own key material and nothing useful.

---

## 2. The two stacks

Windows has two cryptography APIs, and modern ransomware uses whichever the author found first.

```
   CAPI (legacy)                    CNG (modern)
   ─────────────                    ────────────
   advapi32.dll                     bcrypt.dll        ncrypt.dll
   Crypt*                           BCrypt*           NCrypt*
        │                              │                  │
        ▼                              ▼                  ▼
   CSP (Cryptographic              Algorithm          Key Storage
   Service Provider)               providers          Providers (KSP)
        │                              │                  │
   rsaenh.dll etc.                 Primitives:        Persisted keys,
   PROV_RSA_AES                    AES, RSA, ECC,     key isolation,
                                   hashes, RNG        TPM binding
```

**`BCrypt*` is the primitive layer.** Stateless algorithms, caller-managed key buffers, no persistence. This is what bulk file encryption uses.

**`NCrypt*` is the key storage layer.** Persisted named keys, hardware binding, key isolation. Ransomware rarely touches it — persisting a key is the opposite of what an encryptor wants.

**If you see `NCrypt*` in a ransomware sample, look harder.** It usually means the sample is doing something other than bulk encryption, or that it is not the encryptor at all.

---

## 3. Where a CNG key physically lives

This is the section that pays for the module. The allocation pattern is what makes key recovery possible.

```c
// The shape of every CNG symmetric setup. Read it as forensics, not as a recipe.

BCryptOpenAlgorithmProvider(&hAlg, BCRYPT_AES_ALGORITHM, NULL, 0);

// 1. Ask how big the key OBJECT needs to be
BCryptGetProperty(hAlg, BCRYPT_OBJECT_LENGTH, (PUCHAR)&cbKeyObject, ...);

// 2. Caller allocates it. IN ITS OWN HEAP.
pbKeyObject = HeapAlloc(GetProcessHeap(), 0, cbKeyObject);

// 3. Raw key bytes -> another caller buffer
BCryptGenRandom(NULL, pbSecret, 32, BCRYPT_USE_SYSTEM_PREFERRED_RNG);

// 4. CNG expands the key INTO pbKeyObject
BCryptGenerateSymmetricKey(hAlg, &hKey, pbKeyObject, cbKeyObject,
                           pbSecret, 32, 0);
```

Three separate pieces of recoverable material now exist in the encryptor's heap:

| Artifact | Size | Notes |
|---|---|---|
| `pbSecret` — the raw key | 32 bytes for AES-256 | Often zeroed promptly with `SecureZeroMemory` |
| `pbKeyObject` — the key object | ~654 bytes typical for AES | **Contains the expanded round-key schedule** |
| `hKey` — the key handle | pointer-sized | A **pointer into `pbKeyObject`**, not a kernel handle |

**The key object is the durable target.** The raw `pbSecret` buffer is small and frequently wiped, but the expanded schedule must persist for the lifetime of the encryption — and it is mathematically verifiable, which is why `findaes` works. See [Module 07](../07-Memory-Forensics/).

`hKey` being a plain pointer matters too: there is no kernel handle to enumerate, so `windows.handles` in Volatility will not show you crypto keys. You scan process memory instead.

### After `BCryptDestroyKey`

`BCryptDestroyKey` zeroes the key object, but **the heap allocation is freed, not scrubbed from the page**. Freed heap pages routinely retain their contents until reused. This is why scanning the whole memory image, rather than only live allocations, is worth doing — and why keys are sometimes recoverable from a process that has already exited.

---

## 4. CAPI, for older families

The CAPI equivalent keeps key material **inside the CSP**, not in a caller buffer:

```c
CryptAcquireContextW(&hProv, NULL, MS_ENH_RSA_AES_PROV, PROV_RSA_AES,
                     CRYPT_VERIFYCONTEXT);
CryptGenKey(hProv, CALG_AES_256, CRYPT_EXPORTABLE, &hKey);
// ...
CryptExportKey(hSessionKey, hPubKey, SIMPLEBLOB, 0, pbBlob, &dwLen);
```

Two things to take from this:

- **`hKey` here is an opaque CSP handle**, so the key is not sitting in an obvious caller buffer. It still lands in the process heap via the CSP's own allocations — recovery works, but the layout is less predictable than CNG's.
- **`CRYPT_EXPORTABLE` is a tell.** A key flagged exportable exists to be wrapped, and `CryptExportKey` with a public key handle *is* the hybrid key wrap.

`CRYPT_VERIFYCONTEXT` means no persisted key container is created — the ephemeral path, which is what an encryptor wants.

---

## 5. Persisted keys and DPAPI, for the cases that aren't ransomware

Where CNG *does* persist keys, the Microsoft Software KSP writes them as files:

- `%APPDATA%\Microsoft\Crypto\Keys` — user keys
- `C:\ProgramData\Microsoft\Crypto\Keys` — machine keys
- `HKLM\SYSTEM\CurrentControlSet\Control\Cryptography\Providers` — provider registration

Those files are protected with **DPAPI**, whose master keys live under `%APPDATA%\Microsoft\Protect\<SID>` and are unlocked via `lsass.exe` — which is the legitimate LSASS connection.

**Relevant to ransomware incidents in two ways only:** EFS abuse ([Module 04](../04-Platform-And-LOTL-Encryption/)) uses certificates that land here, and credential theft preceding deployment often targets DPAPI-protected secrets. Bulk file encryption does not touch this path.

---

## 6. Below the API: syscalls and drivers

**Direct syscalls.** Some samples call `NtWriteFile` / `NtCreateFile` directly rather than through `kernel32`, bypassing user-mode API hooks. Worth understanding precisely what this defeats:

| Telemetry layer | Bypassed by direct syscalls? |
|---|---|
| User-mode inline hooks | **Yes** |
| **Filesystem minifilter** | **No** — it sits below the syscall in the I/O path |
| Kernel callbacks | No |
| ETW (kernel providers) | No |

So direct syscalls are a real evasion against a declining telemetry source and **no evasion at all against the layer that matters most** for ransomware ([Module 11](../11-Endpoint-Detection/)). Do not overstate their significance in a report.

**BYOVD.** Loading a signed but vulnerable driver to obtain kernel execution, typically to unload or blind a security product's minifilter. This is the technique that *does* defeat the minifilter, which is why it appears alongside mass encryption.

The artifact is a service installation: **System event ID 7045**, a driver in an unusual path, loaded shortly before mass file I/O. The capstone's log excerpt includes exactly this pattern.

---

## 7. What to take away

1. **Dump the encryptor, not LSASS.** Ephemeral file keys live in the encryptor's own heap.
2. **The key object outlives the raw key buffer** and contains the verifiable schedule.
3. **`hKey` is a pointer**, so there is no handle table to enumerate — scan memory.
4. **Freed heap is not scrubbed heap.** Scan the whole image, including after the process exits.
5. **`CryptExportKey` with a public key handle is the CAPI key wrap.** One call, whole scheme.
6. **Direct syscalls do not evade minifilters.** BYOVD is the technique that does.

---

## 8. Exercises

1. In a debugger, break on `BCryptGenerateSymmetricKey` and locate all three artifacts: `pbSecret`, `pbKeyObject`, and what `hKey` points at. Confirm the handle is a pointer into the object.
2. Query `BCRYPT_OBJECT_LENGTH` for AES on your build. How much larger is it than the 240-byte AES-256 schedule, and what else is in there?
3. Free a key object and search the freed pages for the schedule. How long does it survive under load?
4. Explain to a colleague why dumping LSASS will not recover a ransomware file key, using the table in section 1.

---

## 9. References

- Microsoft Learn — CNG reference (`BCrypt*`, `NCrypt*`), CryptoAPI reference, DPAPI documentation
- *Windows Internals, Part 1 & 2* — Yosifovich, Russinovich, Solomon, Ionescu. Security and I/O chapters
- *The Art of Memory Forensics* — heap and process memory analysis
- [Module 07](../07-Memory-Forensics/) — applying all of this to a real image

---

| ◄ [Module 04: Platform & LOTL](../04-Platform-And-LOTL-Encryption/) | [Repository index](../README.md) |
|---|---|
