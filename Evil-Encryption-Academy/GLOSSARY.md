# Glossary

Terms used across this repository. Written for someone encountering them for the first time.

## Cryptography

**AEAD** — Authenticated Encryption with Associated Data. Encryption plus a tamper check. AES-GCM and ChaCha20-Poly1305 are the common ones. Adds a 16-byte tag per file.

**AES** — Advanced Encryption Standard. The default bulk cipher. Works on 16-byte blocks with 128, 192 or 256-bit keys. Hardware-accelerated on modern CPUs, which is why it encrypts gigabytes in seconds.

**AES-NI** — CPU instructions implementing AES in hardware. Relevant to analysts because an AES-NI implementation has **no lookup tables**, so constant-scanning misses it entirely.

**Asymmetric encryption** — Two keys: a public one that locks, a private one that unlocks. RSA and elliptic curve. Slow, so ransomware uses it only to wrap the fast key.

**Avalanche effect** — Flipping one input bit changes about half the output bits. Why there is no "close enough" key and no partial progress against a cipher.

**Block cipher mode** — How a block cipher handles data longer than one block. ECB (broken, leaks structure), CBC (most common), CTR, GCM (adds authentication), XTS (disk encryption).

**ChaCha20 / Salsa20** — Stream ciphers. Fast in pure software with no hardware support, so favoured by Rust and Go families. Identified by the ASCII constant `expand 32-byte k`.

**Curve25519 / X25519** — An elliptic curve used for key agreement. Produces 32-byte keys, so an ECC-wrapped footer is much smaller than an RSA one.

**ECDH** — Elliptic Curve Diffie-Hellman. Two parties derive a shared secret from their own private key and the other's public key. Modern ransomware generates a throwaway keypair per file and uses ECDH against the operator's embedded public key.

**Entropy (Shannon)** — Randomness of byte distribution, 0.0 to 8.0. Encrypted data scores near 8.0 — but so do JPEGs, MP4s and ZIPs. **High entropy does not mean encrypted, and does not mean secure.** See [`MYTHS.md`](MYTHS.md).

**Ephemeral key** — A key generated for one use and discarded. Ephemeral keys are why memory acquisition has a narrow window.

**Hybrid encryption** — Bulk-encrypt with a fast symmetric cipher, then encrypt that symmetric key with a slow asymmetric one. The construction behind essentially all ransomware. Also how TLS and PGP work.

**IV / Nonce** — A non-secret value making each encryption unique even with the same key. Reuse is a classic implementation bug and a recovery opportunity.

**KDF** — Key Derivation Function (PBKDF2, Argon2, scrypt). Turns a password or seed into a key. **Where recovery opportunities live** — if the input is low-entropy, the key space may be searchable.

**Key schedule** — AES expands its key into round keys held contiguously in memory: 176 bytes (AES-128), 240 (AES-256). Mathematically verifiable, which is why AES keys can be found reliably in a memory image.

**Symmetric encryption** — One key both locks and unlocks. Fast. AES, ChaCha20.

**XChaCha20** — ChaCha20 with a 24-byte nonce. Shares the same sigma constant, so constants cannot distinguish them — only nonce size can.

## Ransomware behaviour

**Distributed-chunk encryption** — Encrypting a few regions at the head, midpoint and tail of a large file. Destroys structure at minimal I/O cost and can leave 99% of the file as plaintext.

**Double extortion** — Stealing data before encrypting, then threatening publication. Usually the larger legal exposure.

**Intermittent / partial encryption** — Encrypting only part of each file for speed and to reduce detection signal. Creates real partial-recovery opportunities.

**LOTL (Living off the Land)** — Using built-in OS tooling instead of custom malware. BitLocker abuse is the flagship case: nothing to reverse, because Microsoft wrote and signed the encryptor.

**RaaS** — Ransomware-as-a-Service. Operators build the encryptor; affiliates run the intrusions.

**Ransom extension** — An extension appended to encrypted files. A double extension where the outer part is unrecognized is a strong signal.

**Session key vs per-file key** — One key for the whole host, or a fresh key per file. Determines whether recovering one key recovers everything or one file. **Check this early.**

## Windows and forensics

**BitLocker: FVEK / VMK / protector** — The FVEK encrypts the volume; the VMK encrypts the FVEK; protectors (TPM, PIN, recovery password) protect the VMK. Attacks swap protectors, which is why they are near-instant.

**BYOVD** — Bring Your Own Vulnerable Driver. Loading a signed but vulnerable driver to reach kernel privileges, often to unload security agents.

**CAPI / CNG** — Windows cryptography APIs. CAPI is legacy (`CryptEncrypt`); CNG is modern (`BCryptEncrypt`). Recognizing their calls tells you the scheme without reversing the maths.

**ETW** — Event Tracing for Windows. A telemetry source EDR uses for file and process events.

**Key escrow** — Recovery keys stored centrally, in Active Directory (`msFVE-RecoveryInformation`), Entra ID or MBAM. **Survives an attacker deleting local protectors. Check it first.**

**Minifilter** — A filesystem filter driver. Sees every write *before* it lands on disk, which is what makes inline entropy checks and blocking possible.

**`$MFT`** — Master File Table. NTFS's index of every file, with timestamps.

**`$UsnJrnl:$J`** — The USN journal. Records every file change including renames, and **survives event log clearing**. Rolls over in hours on a busy volume, so preserve it early.

**Shadow copies (VSS)** — Windows point-in-time snapshots. Deleting them is a near-universal ransomware precursor and an early detection opportunity.

## Analysis

**Canary file** — A decoy no legitimate process should touch. The only non-statistical ransomware signal available.

**Carving** — Recovering files from raw data by their structure rather than filesystem metadata.

**IOC** — Indicator of Compromise: a hash, filename, IP. Ages fastest of anything in a threat report.

**Offset-addressed format** — A format whose internal pointers reference absolute positions (PST, MDF, VMDK, PDF). When recovering partially encrypted files you must **null** damaged regions rather than remove them, or every pointer after the first gap breaks.

**Sigma / YARA** — Rule formats. Sigma describes log-based behaviour; YARA matches file contents.
