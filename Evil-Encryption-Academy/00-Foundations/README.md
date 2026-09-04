# Module 00 — Foundations

![Difficulty](https://img.shields.io/badge/difficulty-beginner-brightgreen.svg)
![Prereq](https://img.shields.io/badge/prerequisites-none-lightgrey.svg)

> Enough cryptography to read everything that follows. No more than that.

**Start here if you have never done this before.** You need no maths background and no prior security experience.

---

## 1. The four things people confuse

This is the most important section in the module, because getting these wrong makes everything downstream incoherent.

| | What it does | Reversible? | Example |
|---|---|---|---|
| **Encoding** | Changes representation for transport | **Yes, by anyone** | Base64, URL encoding |
| **Obfuscation** | Makes something hard to read | Yes, with effort | Packed binaries, renamed variables |
| **Hashing** | Produces a fixed-size fingerprint | **No, ever** | SHA-256, MD5 |
| **Encryption** | Makes data unreadable without a key | **Yes, with the key** | AES, ChaCha20 |

**Base64 is not encryption.** It has no key and anyone can decode it. If a ransom note or a footer contains base64, that is *storage*, not protection.

**Hashing is not encryption.** A hash cannot be reversed even by the person who made it. Hashes identify files and verify integrity; they never lock anything.

**Encryption is not damage.** This one matters when you talk to a victim. An encrypted file is *fully intact* and simply unreadable without the key. Nothing was deleted. [`MYTHS.md`](../MYTHS.md) covers why this distinction changes the conversation.

## 2. XOR: the atom of every cipher

XOR compares two bits and returns 1 if they differ:

```
  0 ⊕ 0 = 0      1 ⊕ 0 = 1
  0 ⊕ 1 = 1      1 ⊕ 1 = 0
```

The property that matters: **XOR is its own inverse.**

```
  data ⊕ key = ciphertext
  ciphertext ⊕ key = data
```

Every cipher in this curriculum is, at the final step, XOR against something. AES and ChaCha20 differ in *how they generate the thing you XOR with*, not in the combining operation. If XOR makes sense, the shape of every cipher makes sense.

Weak ransomware sometimes uses XOR alone with a short repeating key. That is trivially breakable and is a genuine recovery path — see [Module 10](../10-Recovery-and-Decryption/).

## 3. Symmetric vs asymmetric

**Symmetric** — one key locks and unlocks. Like a house key. Fast enough to encrypt terabytes.

**Asymmetric** — two keys. A public key locks; only the matching private key unlocks. Like a post box: anyone can post, only the owner can empty it. Roughly 10,000× slower.

Ransomware uses **both**, and the reason it works is entirely in that combination — covered in [Module 02](../02-Hybrid-Encryption-Model/).

## 4. Entropy: measuring randomness

Shannon entropy scores byte distribution from **0.0** (totally predictable) to **8.0** (perfectly uniform). Encrypted data lands near 8.0.

**Three things almost everyone gets wrong:**

1. **High entropy ≠ encrypted.** JPEGs score ~7.9, MP4s ~8.0, ZIPs high too — because compression also produces uniform-looking bytes. You cannot separate ciphertext from a photo on entropy alone.
2. **High entropy ≠ secure.** AES-ECB scores ~6.7 and leaks the image straight through. You can *see* the picture in the ciphertext.
3. **Small samples never reach 8.0.** 128 bytes of perfect ciphertext scores about 6.55, because 128 samples cannot populate 256 possible values. Judging a small key blob against 8.0 makes real ciphertext look non-random.

All three are demonstrated with runnable code in [`01-Symmetric-Cryptography/labs/`](../01-Symmetric-Cryptography/labs/). **Do that before continuing** — these stop being abstract once you have watched them.

## 5. Randomness and keys

A **CSPRNG** (cryptographically secure random number generator) produces keys an attacker cannot predict. On Windows that is `BCryptGenRandom`.

A plain **PRNG** — `rand()`, or anything seeded from the clock — is predictable. If ransomware seeds a key from `time()`, the key space collapses to something searchable.

**Almost every public ransomware decryptor exists because of this class of bug**, not because anyone broke AES. When you analyse a sample, the highest-value question is: *where did the key come from?*

## 6. What you should now be able to do

- Explain why base64 in a ransom note is not protection
- Say why a 7.9 entropy score does not mean a file is encrypted
- Explain to a client that their files are intact but unreadable
- Recognise that "we'll brute-force the key" is not a plan

---

## Next

1. **Run the demos** — [`01-Symmetric-Cryptography/labs/`](../01-Symmetric-Cryptography/labs/). Watch encryption happen.
2. **Then [Module 02](../02-Hybrid-Encryption-Model/)** — the hinge of the whole curriculum.
3. Keep [`GLOSSARY.md`](../GLOSSARY.md) open.

---

| [Repository index](../README.md) | [Module 01: Symmetric Cryptography](../01-Symmetric-Cryptography/) ► |
|---|---|
