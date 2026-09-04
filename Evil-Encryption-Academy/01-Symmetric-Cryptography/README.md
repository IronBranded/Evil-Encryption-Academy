# Module 01 — Symmetric Cryptography

![Difficulty](https://img.shields.io/badge/difficulty-beginner--intermediate-yellowgreen.svg)
![Labs](https://img.shields.io/badge/labs-runnable-brightgreen.svg)

> The speed engines. What actually encrypts the bytes.

**Prerequisites:** [Module 00](../00-Foundations/).

---

## 1. Why symmetric ciphers do the work

Asymmetric cryptography is roughly four orders of magnitude slower and can only encrypt a few hundred bytes per operation. Nothing encrypts a 10 TB file server except a symmetric cipher.

Two families matter in practice:

| | Block ciphers | Stream ciphers |
|---|---|---|
| Example | AES | ChaCha20, XChaCha20 |
| Operates on | Fixed 16-byte blocks | A keystream XORed with data |
| Output size | Padded to a block multiple | Identical to input |
| Speed | 1–5 GB/s **with AES-NI hardware** | 1–3 GB/s **in pure software** |
| Chosen when | Hardware acceleration available | Cross-platform, no hardware assumptions |

**That last row explains the current landscape.** Rust and Go families overwhelmingly pick ChaCha20 or XChaCha20 because it is fast without hardware support and has no cache-timing side channels. Both [DeadLock](../06-Case-Studies/deadlock/) and [The Gentlemen](../06-Case-Studies/the-gentlemen/) use XChaCha20.

## 2. Start with the labs

**[`labs/`](labs/) is the part of this module that exists and runs.** Five demos, no malware:

```bash
python3 labs/encryption_demo.py modes        # why ECB is broken, visually
python3 labs/encryption_demo.py hexdump      # before/after, entropy, histograms
python3 labs/encryption_demo.py avalanche    # one bit in, half the output changes
python3 labs/encryption_demo.py specimens    # safe practice files for later modules
python3 labs/encryption_demo.py roundtrip    # proof it is reversible
```

Do `modes` first. It shows an image surviving AES-ECB intact — same structure, different shades — while scoring 6.68 entropy. Seeing that once permanently fixes the "high entropy means secure" misconception.

## 3. Modes matter more than the cipher

AES is not broken. AES-ECB is. The mode decides whether a correct cipher produces a secure result.

| Mode | Recognise it by | Note |
|---|---|---|
| **ECB** | **Repeating 16-byte ciphertext blocks** | Broken. Leaks structure. Repeated ciphertext maps to repeated plaintext |
| **CBC** | 16-byte IV, size a multiple of 16, PKCS#7 padding | Most common in ransomware |
| **CTR** | Output identical in size to input, no padding | Allows random access — suits partial encryption |
| **GCM** | 12-byte nonce, **16-byte tag appended** | The tag is diagnostic |
| **XTS** | Sector-based | Full-disk encryption. BitLocker's default |

From ciphertext alone: a multiple of 16 with padding suggests CBC or ECB; identical size to the original suggests a stream cipher or CTR; a consistent 16-byte overhead suggests an AEAD tag.

## 4. Recognising ciphers in a binary

Modern samples are statically linked with no import table, so **constants are the primary route**:

| Cipher | Signature |
|---|---|
| AES | S-box `63 7c 77 7b f2 6b 6f c5 ...` |
| AES (hardware) | **No tables at all** — look for `AESENC`, `AESKEYGENASSIST` |
| ChaCha20 / Salsa20 | The ASCII string `expand 32-byte k` |
| XChaCha20 | **Same constant as ChaCha20** — distinguish by 24-byte nonce |
| RC4 | No constants; identify by the KSA loop filling 0..255 |

```bash
python3 ../tools/identify_crypto.py sample.exe
```

Full catalog: [`references/CIPHER-IDENTIFICATION.md`](../references/CIPHER-IDENTIFICATION.md). Disassembler workflow: [Module 08](../08-Reverse-Engineering/).

## 5. Planned expansion

Deeper written treatment of block cipher internals, the ChaCha quarter-round, and the CAPI/CNG call surfaces. The labs, the catalog, and [Module 02, section 5](../02-Hybrid-Encryption-Model/) already cover the practically useful subset.

---

| ◄ [Module 00: Foundations](../00-Foundations/) | [Module 02: Hybrid Encryption](../02-Hybrid-Encryption-Model/) ► |
|---|---|
