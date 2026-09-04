# Module 06 — Case Studies

![Status](https://img.shields.io/badge/status-1%20written-yellow.svg)

> Reading a threat-intel report and extracting the cryptographic scheme from it.

## Written

- **[DeadLock](deadlock/)** — XChaCha20 + NaCl `crypto_box`, 512-byte fine striping, resource-aware throttling, Polygon/Session infrastructure. Source: MSTIC, Aug 2026. **Its striping broke our tooling; the fix is documented there.**
- **[The Gentlemen (Storm-2697)](the-gentlemen/)** — per-file ephemeral Curve25519 + XChaCha20, distributed-chunk encryption, Go/Garble. Source: MSTIC, May 2026. This is the reference case study; follow its structure.

## Queued

| Family | Why it matters | Source |
|---|---|---|
| WannaCry | AES-128-CBC + RSA-2048 via CAPI. The canonical hybrid teaching case | Multiple |
| Ryuk / Conti | Hardcoded public keys, leaked source | Multiple |
| LockBit | Speed claims vs measured throughput | CISA advisories |
| BlackCat / ALPHV | Rust, selectable ChaCha20 or AES | MSTIC, CISA |
| ShrinkLocker | BitLocker abuse. Covered in [Module 04](../04-Platform-And-LOTL-Encryption/) | Kaspersky, Bitdefender |

See [`../references/PRIMARY_SOURCES.md`](../references/PRIMARY_SOURCES.md) for the source feed.

## How to write one

Use [`_template/`](_template/). Extract in this order: **cryptographic scheme → key storage layout → encryption paradigm → anti-recovery behaviour → IOCs last.** The first three determine recoverability and are what most readers skip.

Reconstruct a specimen matching the described footer layout and confirm the repository tooling handles it. Doing this for The Gentlemen exposed a real blind spot.

---

| Back to [repository index](../README.md) |
|---|
