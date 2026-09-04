# Module 03 — Encryption Paradigms

![Difficulty](https://img.shields.io/badge/difficulty-intermediate-orange.svg)
![Focus](https://img.shields.io/badge/focus-how%20much%20got%20encrypted-red.svg)

> Not *whether* a file was encrypted, but *how much of it* — which is the number that decides recoverability.

**Prerequisites:** [Module 02](../02-Hybrid-Encryption-Model/).

---

## 1. Why attackers encrypt less than everything

Ransomware races detection. Encrypting a 10 TB file server completely takes hours, and hours is enough time to be caught, isolated, and stopped.

So operators encrypt **less**. The insight they exploit is that you do not need to encrypt a file to make it useless — you need to break its *structure*. A database with its header and a few interior pages destroyed will not mount. A VM disk with its descriptor damaged will not boot. The other 97% of the bytes are irrelevant to the victim's ability to use the file.

That is an attacker optimisation. It is also the single biggest recovery opportunity a responder has, because **those untouched bytes are still your data.**

---

## 2. The four paradigms

| Paradigm | What is encrypted | Entropy signature | Recovery outlook |
|---|---|---|---|
| **Full** | Everything | Uniformly high across the file | None without a key |
| **Header-only** | First N KB | High prefix, plaintext body | Often excellent |
| **Intermittent** | Alternating bands | Regular high/low striping | Good — proportional to gap size |
| **Distributed-chunk** | Head, midpoint, tail | High at three points, plaintext between | Often excellent |

```
FULL              ████████████████████████████████████████████████

HEADER-ONLY       ████····························································

INTERMITTENT      ████····████····████····████····████····████····████····

DISTRIBUTED-CHUNK ██······························██······························██
```

**Small files are usually fully encrypted regardless.** Fast modes typically apply only above a size threshold — commonly 1 MB — because the overhead of partial encryption is not worth it on a small file. So an incident often shows two paradigms at once, split by size. Reporting a single paradigm for the whole estate is a common and costly error.

---

## 3. Reading the paradigm from the ciphertext

You do not need the sample. [`parse_footer.py`](../02-Hybrid-Encryption-Model/labs/parse_footer.py) classifies all four from the file alone:

```bash
python3 02-Hybrid-Encryption-Model/labs/parse_footer.py /evidence/share --recurse
```

```
VERDICT  DISTRIBUTED-CHUNK PARTIAL ENCRYPTION (candidate)
         encrypted at head, midpoint and tail; 168/231 blocks (73%) look like
         surviving plaintext - strong partial-recovery candidate

ENTROPY PROFILE (4096-byte blocks)
  █▅█▅█▅█▅█
  low ▁▁▁ plaintext / structured      high ███ ciphertext
```

Generate practice specimens for all four with [`encryption_demo.py specimens`](../01-Symmetric-Cryptography/labs/).

### The trap

**High entropy is not encryption.** JPEGs score ~7.9, MP4s ~8.0 — identical to ciphertext. An entropy-only classifier calls every photo and video on a file server encrypted. The tool in this repository had exactly that bug; the fix was checking whether the file's **header still matches its extension**. See [`MYTHS.md`](../MYTHS.md).

---

## 4. Key models, and why they matter more than the paradigm

Independent of paradigm, a family uses either:

- **Session key** — one symmetric key for the whole host. Recovering it recovers **everything**.
- **Per-file keys** — a fresh key per file. Recovering one recovers **one file**.

This single fact reshapes the entire response. Determine it in the first hour:

```bash
for f in *.locked; do tail -c 512 "$f" | sha256sum | cut -d' ' -f1; done | sort -u | wc -l
# 1  -> session key
# N  -> per-file keys
```

Modern families overwhelmingly use per-file keys, frequently derived through per-file ephemeral ECDH ([Module 02](../02-Hybrid-Encryption-Model/)). Do not assume a session key because an old blog said so.

---

## 5. What the percentages are worth

Real published figures, from MSTIC's analysis of The Gentlemen:

| Mode | Encrypted | Surviving plaintext |
|---|---|---|
| default | ~27% | ~73% |
| `--fast` | ~9% | ~91% |
| `--superfast` | ~3% | ~97% |
| `--ultrafast` | ~0.9% | **~99%** |

Applied to files over 1 MB — databases, mail stores, VM disks, archives. The assets that matter most are the ones most likely to survive.

Turning that into recovered data is [Module 10](../10-Recovery-and-Decryption/). The critical technique is **offset preservation**: null the damaged regions rather than removing them, so internal pointers still resolve.

---

## 6. Detection implications

Partial encryption is not only a speed optimisation — it degrades detection:

- **Less I/O**, so file-modification-rate thresholds are slower to fire
- **Sampled entropy checks miss.** An EDR cannot score whole multi-gigabyte files at write time. At ultrafast percentages, a sampled block lands on plaintext ~99% of the time
- **File-level entropy barely moves** on header-only encryption

Which is why [Module 11](../11-Endpoint-Detection/) weights **format/extension mismatch** above entropy. Header-only encryption is nearly invisible to entropy and obvious to a format check.

---

## 7. Exercises

1. Generate all four paradigms and classify each without looking at the filenames.
2. At what intermittent gap size does the classifier stop distinguishing partial from full? Is it wrong, or is the question ill-posed?
3. A share shows two paradigms split at 1 MB. What does that tell you about the encryptor's configuration, and what should you check next?
4. Explain to a sceptical client why 97% of a file surviving does not mean 97% of it opens.

---

## 8. References

- [The Gentlemen case study](../06-Case-Studies/the-gentlemen/) — where the percentages come from
- [MSTIC ransomware coverage](https://www.microsoft.com/en-us/security/blog/threat-intelligence/ransomware/)
- [Module 10](../10-Recovery-and-Decryption/) — turning surviving plaintext into recovered data
- [Module 11](../11-Endpoint-Detection/) — why these paradigms exist from the detection side

---

| ◄ [Module 02: Hybrid Encryption](../02-Hybrid-Encryption-Model/) | [Module 04: Platform & LOTL](../04-Platform-And-LOTL-Encryption/) ► |
|---|---|
