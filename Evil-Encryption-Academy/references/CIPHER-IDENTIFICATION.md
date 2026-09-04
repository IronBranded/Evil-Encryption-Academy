# Cipher Identification Catalog

Every cryptographic mechanism observed in ransomware, how it works, and how to identify it.

**Companion tool:** [`tools/identify_crypto.py`](../tools/identify_crypto.py) automates the constant matching below.

```bash
python3 tools/identify_crypto.py sample.exe
python3 tools/identify_crypto.py memdump.raw --min-confidence high
```

---

## How identification works

Cipher implementations cannot hide. Almost every algorithm requires hardcoded tables, initialization values, or derived constants that must appear verbatim in the binary. These are mathematically required, not stylistic. They survive stripped symbols, renamed functions, and static linking.

You have four identification routes, in descending order of convenience:

1. **Import table** — API names. Fastest, but absent in Rust/Go/statically linked samples.
2. **Constants** — S-boxes, IVs, round constants. Works on stripped and static binaries.
3. **Structure** — loop shapes, block sizes, round counts. Works when constants are obfuscated.
4. **Behavior** — ciphertext properties, file layout, key sizes. Works with no binary at all.

> **A constant proves presence, not use.** A statically linked Rust binary pulls in an entire crypto library. Scanning one real example produced hits for AES both directions, Blowfish, ChaCha20, secp256k1, and P-256 — from a library where the program may call one of them. Always confirm in a disassembler.

### Decision tree

```
Do you have the binary?
├─ No  → Work from ciphertext: block-size analysis, entropy profile,
│        footer size. See 02-Hybrid-Encryption-Model.
└─ Yes → Is it packed? (entropy > 7.5 across the whole PE, tiny import table)
   ├─ Yes → Unpack first. Constants are encrypted until runtime.
   └─ No  → Does it import bcrypt.dll / advapi32 crypto?
      ├─ Yes → Read the API sequence. Module 02, section 5.
      └─ No  → Scan for constants (this catalog).
         └─ Nothing matches? → AES-NI hardware path (no tables),
            custom/XOR scheme, or OS-delegated encryption (Module 04).
```

---

## 1. Symmetric block ciphers

The bulk workhorses. Fast, and the reason gigabytes encrypt in minutes.

### AES (Rijndael) — the overwhelming default

**How it works.** Operates on 16-byte blocks. The key is expanded into a round-key schedule (10, 12, or 14 rounds for 128/192/256-bit keys). Each round applies byte substitution through an S-box, row shifting, column mixing, and a round-key XOR. Every step is reversible with the same key.

**Why ransomware uses it.** Hardware acceleration. `AESENC` on modern x86-64 pushes 1–5 GB/s per core.

| Identification route | Signature |
|---|---|
| Forward S-box | `63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76` |
| Inverse S-box | `52 09 6a d5 30 36 a5 38 bf 40 a3 9e 81 f3 d7 fb` |
| T-tables (Te0) | `a5 63 63 c6 84 7c 7c f8 99 77 77 ee 8d 7b 7b f6` |
| Round constants | `01 02 04 08 10 20 40 80 1b 36` |
| Hardware path | `AESENC`, `AESENCLAST`, `AESKEYGENASSIST` opcodes, **no tables at all** |
| Windows API | `BCRYPT_AES_ALGORITHM` (`L"AES"`), `CALG_AES_256` |
| In memory | Expanded key schedule: 176 B (AES-128), 208 B (192), **240 B (256)** |

**Presence of the inverse S-box means decryption is implemented.** An encrypt-only deployed encryptor often ships without it.

**The AES-NI blind spot:** a sample using hardware AES has no S-box and no T-tables. Constant scanning finds nothing. Look for the instructions instead. This is a common false-negative.

### AES modes — the mode matters more than the cipher

| Mode | Structure | How to spot it | Notes |
|---|---|---|---|
| **ECB** | Each block independent | **Repeating 16-byte ciphertext blocks** | Broken. Leaks file structure. See [Module 01 labs](../01-Symmetric-Cryptography/labs/) |
| **CBC** | Each block XORed with the previous | 16-byte IV, size a multiple of 16, PKCS#7 padding | Most common in ransomware |
| **CTR** | Counter turned into a keystream | Ciphertext same size as plaintext, no padding | Allows random access, good for partial encryption |
| **GCM** | CTR plus authentication | 12-byte nonce, **16-byte auth tag appended** | Tag presence is diagnostic |
| **XTS** | Tweakable, sector-based | Used by full-disk encryption | BitLocker default. See Module 04 |

Mode identification from ciphertext alone: size a multiple of 16 with padding suggests CBC/ECB; identical size to the original suggests CTR/stream; a consistent 16-byte overhead suggests GCM.

### Other block ciphers

| Cipher | Block/key | Constant signature | Ransomware relevance |
|---|---|---|---|
| **Blowfish** | 64-bit / up to 448 | P-array from pi: `88 6a 3f 24 d3 08 a3 85` | Occasional; also underlies bcrypt |
| **Twofish** | 128-bit / 128–256 | q0 table: `a9 67 b3 e8 04 fd a3 76` | Rare, AES finalist |
| **Serpent** | 128-bit / 128–256 | `0x9E3779B9` (phi) | Rare; appears in FDE tools |
| **3DES/DES** | 64-bit / 56·3 | IP table: `3a 32 2a 22 1a 12 0a 02` | Legacy only. Very slow |
| **TEA/XTEA/XXTEA** | 64-bit / 128 | delta `b9 79 37 9e` | Tiny code size; seen in droppers and simple lockers |
| **RC5 / RC6** | 64/128-bit | P32 `63 51 e1 b7`, Q32 `b9 79 37 9e` | RC6 seen in older families |
| **Camellia** | 128-bit / 128–256 | sigma from golden ratio | Rare, regional |
| **CAST-128** | 64-bit / 128 | S-box `d2 c4 a3 f4` | Uncommon |

`0x9E3779B9` appears in TEA, Serpent, RC5/RC6, and several hashes. **On its own it identifies nothing.** Corroborate.

---

## 2. Stream ciphers

Generate a keystream XORed with the plaintext. No padding, no block alignment, ciphertext identical in size to plaintext.

### ChaCha20 / Salsa20 — the modern favourite

**How it works.** Builds a 64-byte state from a constant, the key, a counter, and a nonce, then applies quarter-round mixing to produce keystream. Fast in pure software with no hardware support and no cache-timing side channels, which is why Rust and Go families favour it.

| Route | Signature |
|---|---|
| Sigma constant (256-bit key) | `"expand 32-byte k"` |
| Tau constant (128-bit key) | `"expand 16-byte k"` |
| As dwords | `61 70 78 65 33 20 64 6e 79 62 2d 32 6b 20 65 74` |
| In memory | 32-byte key inside a 64-byte state block, adjacent to the sigma constant |

**The sigma string is one of the strongest single indicators in this catalog.** It is required, it is ASCII, and it survives everything short of packing.

**Memory recovery is harder than AES.** ChaCha20 has no expanded key schedule to verify mathematically. You hunt the sigma constant and take the neighbouring 32 bytes as a candidate, then test. Expect false positives.

### XChaCha20 — the extended-nonce variant

Same core as ChaCha20 with a **24-byte nonce** instead of 8 or 12. It derives a subkey with HChaCha20 first, which makes random nonces safe at scale — attractive when encrypting millions of files.

**It shares the `expand 32-byte k` constant, so constant scanning cannot tell it from ChaCha20.** Distinguish by nonce size in the code or by the footer layout. Reported in The Gentlemen ransomware (MSTIC, May 2026), where the 24-byte nonce is derived from the first 24 bytes of the per-file ephemeral public key rather than stored separately.

### Others

| Cipher | Signature | Notes |
|---|---|---|
| **RC4** | No constants. Identify by the KSA loop initializing a 256-byte array to `0..255` | Legacy. Broken but adequate for extortion |
| **HC-128** | `96 5f a1 f2` | Rare eSTREAM cipher; appears in a few families |
| **Sosemanuk** | Serpent-derived tables | Reported in ESXi-targeting families |
| **Custom XOR** | Repeating key visible in low-entropy regions | Often recoverable without any key — see below |

---

## 3. Authenticated encryption (AEAD)

Encryption plus integrity. Detects tampering, and conveniently for the attacker, proves to the victim that decryption succeeded.

| Scheme | Signature | Overhead |
|---|---|---|
| **AES-GCM** | `BCRYPT_CHAIN_MODE_GCM` (`L"ChainingModeGCM"`); GHASH tables | 16-byte tag |
| **ChaCha20-Poly1305** | Poly1305 clamp `ff ff ff 0f fc ff ff 0f fc ff ff 0f fc ff ff 0f` plus the sigma constant | 16-byte tag |
| **AES-CCM** | `L"ChainingModeCCM"` | Variable tag |
| **NaCl `crypto_box`** (XSalsa20-Poly1305) | Salsa sigma + Poly1305 clamp together; libsodium strings | 16-byte tag. Used by DeadLock for key encapsulation |

> **A zero nonce is not automatically a bug.** DeadLock uses a constant zero `crypto_box` nonce, which is safe there because a fresh ephemeral keypair per file makes every shared secret unique, so the nonce never repeats under the same key. Check the key lifecycle before reporting nonce reuse as a weakness.

A consistent 16-byte per-file overhead beyond the wrapped key blob suggests an AEAD tag. Account for it when reconciling file size deltas.

---

## 4. Asymmetric — why you cannot decrypt

These do not encrypt your files. They encrypt the key that encrypted your files. See [Module 02](../02-Hybrid-Encryption-Model/).

### RSA

**How it works.** Security rests on the difficulty of factoring a large modulus. Encryption is a modular exponentiation with the public exponent, decryption requires the private key. A ciphertext is always exactly the modulus size.

| Route | Signature |
|---|---|
| DER OID | `2a 86 48 86 f7 0d 01 01 01` (rsaEncryption) |
| PEM | `-----BEGIN PUBLIC KEY-----`, `-----BEGIN RSA PUBLIC KEY-----` |
| CNG/CAPI blob | `RSA1` (public), `RSA2` (private) |
| Public exponent | `01 00 01` (65537) — three bytes, **very high false-positive rate** |
| Ciphertext size | 128 B (1024), 256 B (2048), 384 B (3072), 512 B (4096) |

**Key sizes are 1024, 2048, 3072, 4096.** "RSA-4048" appears in ransom notes and secondhand writeups; it is not a real size, and it is worth recording as an attribution signal when you see it.

### Elliptic curve

Smaller keys for equivalent strength, so the wrapped blob is much smaller — 32 to 65 bytes rather than 256 or 512. Increasingly common.

| Curve | Signature | Notes |
|---|---|---|
| **Curve25519 / X25519** | a24 constant `41 db 01 00` (121665); `"25519"` strings | Very common in modern families |
| **secp256k1** | Gx `79 be 66 7e f9 dc bb ac` | Bitcoin curve, sometimes reused |
| **NIST P-256** | p `ff ff ff ff 00 00 00 01 00 00 ...` | `ECK1` CNG magic |
| **DER** | `2a 86 48 ce 3d 02 01` (id-ecPublicKey) | |

> **A 33-byte key with a `02`/`03` prefix is not necessarily secp256k1.** DeadLock stores a Curve25519 key with a SEC1 compressed-point prefix borrowed from Bitcoin, then uses only the trailing 32 bytes in the scalar multiplication — apparently for format versioning in its own tooling. Check what the code does with the bytes before attributing a curve.

With ECC the scheme is usually ECIES-style: an ephemeral keypair is generated per file or per host, combined with the attacker's public key via ECDH to derive a symmetric key, and the ephemeral **public** key is stored with the file. A 32-byte tail is the tell.

**Practical consequence:** a small fixed tail means ECC, a 256/512-byte tail means RSA. This is a fast first read from the ciphertext alone.

#### Per-file ephemeral ECDH — the current state of the art

A pattern worth knowing in detail, because it removes the weaknesses older families had. Per MSTIC's May 2026 analysis of The Gentlemen, for **every file**:

1. Generate a fresh ephemeral Curve25519 keypair
2. ECDH the ephemeral private key against the operator's embedded public key
3. Use the shared secret directly as the XChaCha20 key
4. Derive the nonce from the first 24 bytes of the ephemeral **public** key
5. Store the ephemeral public key with the file; discard the ephemeral private key

Why this matters to a responder:

- **No key or nonce reuse anywhere.** Cross-file cryptanalysis is off the table.
- **Nothing needs a separate nonce field**, because it is recomputed from the stored public key.
- **The stored value is a public key, not a wrapped key.** It is harmless on its own and reveals nothing.
- **Recovery requires the operator's private key or the shared secret in RAM.** The memory window from Module 02 is the entire opportunity.

The stored ephemeral key may be **base64 text, not a binary blob** — which entropy-based footer detection cannot see. `parse_footer.py` string-scans the tail for exactly this reason.

---

## 5. Hashes and key derivation

Rarely encrypt anything, but they identify files, generate victim IDs, and derive keys. **KDFs are where recovery opportunities appear.**

| Function | Signature (little-endian) |
|---|---|
| **MD5** | `01 23 45 67 89 ab cd ef fe dc ba 98 76 54 32 10` |
| **SHA-1** | MD5 state plus `f0 e1 d2 c3` |
| **SHA-256** | `67 e6 09 6a 85 ae 67 bb 72 f3 6e 3c 3a f5 4f a5` |
| **SHA-256 K table** | `98 2f 8a 42 91 44 37 71 cf fb c0 b5 a5 db b5 e9` |
| **SHA-512 / BLAKE2b IV** | `08 c9 bc f3 67 e6 09 6a 3b a7 ca 84 85 ae 67 bb` |
| **SHA-3 / Keccak** | `01 00 00 00 00 00 00 00 82 00 00 00 00 00 00 00` |
| **CRC32** | `00 00 00 00 96 30 07 77 2c 61 0e ee ba 51 09 99` |
| **bcrypt** | `"OrpheanBeholderScryDoubt"` |
| **PBKDF2 / Argon2 / scrypt** | Usually string identifiers |

BLAKE2s and BLAKE3 share the SHA-256 IV; BLAKE2b shares the SHA-512 IV. A SHA-256 IV hit does not by itself confirm SHA-256.

**Why KDFs matter for recovery.** If the symmetric key derives from a password, a timestamp, a process ID, or any low-entropy seed rather than a CSPRNG, the key space may be brute-forceable. Most public decryptors exist because of exactly this class of bug. When you find a KDF, trace its input — that is the highest-value question in the sample.

---

## 6. Weak and custom schemes

Amateur families roll their own. This is good news.

| Scheme | Identification | Recovery |
|---|---|---|
| **Single-byte XOR** | 256-key brute force; entropy stays low | Trivial |
| **Repeating-key XOR** | Key length via Hamming distance / Kasiski | Trivial with known plaintext |
| **XOR with a PRNG stream** | Entropy near-random but seed is often `time()` or PID | Brute-force the seed space |
| **Custom LCG keystream** | Multiplier/increment constants in the binary | Reimplement and reverse |
| **Base64 "encryption"** | Standard alphabet present | Not encryption at all |
| **Header-only overwrite** | Small high-entropy prefix, body untouched | Body recoverable; often full recovery via file carving |

**Always check whether the file is actually encrypted before assuming it is.** [`parse_footer.py`](../02-Hybrid-Encryption-Model/labs/parse_footer.py) distinguishes encryption from corruption, compression, and header damage. A meaningful share of "ransomware" incidents involve broken or partial encryption where much of the data survives.

---

## 7. OS-delegated encryption

No cipher in the binary because the OS does the work. Full treatment in [Module 04](../04-Platform-And-LOTL-Encryption/).

| Mechanism | On-disk signature | Detection surface |
|---|---|---|
| **BitLocker** | `-FVE-FS-` in the volume boot record | `manage-bde`, `Win32_EncryptableVolume`, PowerShell cmdlets, FVE registry |
| **EFS** | `$EFS` attribute in `$MFT` | `cipher.exe`, certificate store changes |
| **LUKS / dm-crypt** | `LUKS\xba\xbe` | `cryptsetup` history |
| **VeraCrypt / DiskCryptor** | Container headers, driver installs | System 7045 |
| **7-Zip / RAR** | `37 7a bc af 27 1c`, `Rar!\x1a\x07\x01\x00` | Archive tool execution with a password flag |
| **ESXi / vSphere** | VM encryption metadata | `hostd.log`, `esxcli` history |
| **Cloud SSE-C** | Object metadata | CloudTrail SSE-C headers |

---

## 8. Family reference

Commonly reported schemes, as a starting hypothesis only.

| Family | Bulk cipher | Key wrap |
|---|---|---|
| WannaCry | AES-128-CBC (CAPI) | RSA-2048 |
| CryptoLocker | AES-256 | RSA-2048 |
| Petya / NotPetya | Salsa20 | RSA / destructive |
| Ryuk | AES-256 | RSA-4096 |
| Conti | AES-256 (ChaCha8 in variants) | RSA-4096 |
| REvil / Sodinokibi | Salsa20 | Curve25519 |
| DarkSide / BlackMatter | Salsa20 | RSA-1024 |
| LockBit 2.0 / 3.0 | AES | RSA |
| BlackCat / ALPHV | ChaCha20 or AES (selectable) | RSA |
| Akira | ChaCha20 | RSA-4096 |
| Babuk | ChaCha8 / HC-128 | Curve25519 |
| Maze | ChaCha20 | RSA |
| Clop | RC4 | RSA |
| ShrinkLocker | **BitLocker (AES-XTS)** | BitLocker protector |
| The Gentlemen (Storm-2697) | **XChaCha20**, per-file | **Per-file ephemeral Curve25519 ECDH** |
| DeadLock | **XChaCha20**, per-file | **Curve25519 ECDH + XSalsa20-Poly1305 (NaCl `crypto_box`)** |

> **Verify per sample.** Variants within a family differ, builders are leaked and modified, and affiliates recompile. Reporting ages badly. Treat this table as a hypothesis to test with `identify_crypto.py` and a disassembler, never as a conclusion. Getting this wrong produces a confidently incorrect recoverability verdict, which is the worst deliverable in this field.

---

## 9. When nothing matches

In order of likelihood:

1. **Packed or crypted binary.** Whole-file entropy above 7.5 with a tiny import table. Unpack first; constants are encrypted until runtime. Dump from memory after unpacking.
2. **AES-NI hardware path.** No tables exist. Search for `AESENC` / `AESKEYGENASSIST` instead.
3. **OS-delegated encryption.** Nothing to find because Windows is doing it. Pivot to Module 04.
4. **Custom scheme.** Look for tight XOR/rotate/shift loops over a buffer with a small state.
5. **Wrong artifact.** You may be scanning a loader or dropper, not the encryptor.

---

## References

- Microsoft Learn — CNG and CryptoAPI reference
- *Serious Cryptography*, Aumasson — the algorithms themselves
- *Practical Malware Analysis*, ch. 13 — crypto identification in binaries
- FindCrypt, KANAL, and `yara-rules/crypto` — prior art this catalog builds on
- [No More Ransom](https://www.nomoreransom.org/) — check for an existing decryptor first
