# Myths and Anti-Patterns

Common beliefs that are wrong, and what is true instead. Several of these have cost real victims real data.

---

### "High entropy means it's securely encrypted"

**Wrong.** AES-ECB scores around 6.7 on the [Module 01 demo](01-Symmetric-Cryptography/labs/) and leaks the file's structure completely — you can see the image through the ciphertext. Entropy measures *randomness of byte distribution*, not security.

The measurement that catches ECB is **distinct 16-byte block count**. In the demo, ECB collapses to 15 distinct blocks out of 128 while CBC gives 128 of 128. If you ever find repeating 16-byte blocks in a ciphertext body, repeated ciphertext maps directly to repeated plaintext, and partial recovery may be possible with no key at all.

### "A high entropy score means the file is encrypted"

**Wrong, and this one produces bad blast-radius numbers.** JPEGs score ~7.9 and MP4s ~8.0. An entropy-only tool flags every photo and video on a file server as encrypted. `parse_footer.py` had exactly this bug.

The real signal is **format mismatch**: a file whose extension claims JPEG but whose JFIF header is gone has had its header encrypted. An intact header on a high-entropy file usually means it is just a photo.

### "Entropy should be 8.0 if it's random"

**Only for large samples.** 128 bytes of perfect ciphertext scores about 6.55, and not even the log2(128)=7.0 "ceiling" — 128 samples cannot populate 256 symbols. Judging a small wrapped-key blob against 8.0 makes genuine ciphertext look non-random and you discard the finding. Normalize against measured random behaviour at that sample size.

### "Reboot it to be safe"

**This is the sentence that ends recoveries.** The plaintext key is in RAM. Powering off destroys the only copy you can reach.

Isolate by pulling the network cable or using an EDR containment action that leaves the host running. That stops spread *and* preserves the evidence. See [Module 07](07-Memory-Forensics/).

### "Encryption damaged the files"

**No.** Encryption is a reversible transformation. The file is fully intact and simply unreadable without the key — [Demo 5](01-Symmetric-Cryptography/labs/) proves this with matching SHA-256 hashes before and after. Nothing was deleted or corrupted.

This matters for client communication. "Your data is intact but locked" is accurate and very different from "your data is destroyed."

### "We can brute-force the key"

**No.** One flipped input bit changes ~50% of output bits (the avalanche effect, measured at 48.6% in [Demo 3](01-Symmetric-Cryptography/labs/)). There is no partial progress and no "close enough." Guessing 255 of 256 key bits correctly gets you exactly nothing.

Recovery comes from memory forensics, key escrow, a flawed scheme, weak key derivation, or a published decryptor. Never from brute force against the cipher.

### "The ransom note says military-grade RSA-4048, so it must be sophisticated"

**RSA-4048 is not a real key size.** Real moduli are 1024, 2048, 3072, and 4096 bits. When you see 4048 in a note it is a typo or a bluff — and it is worth recording as an attribution signal. Ransom notes are marketing copy, not technical documentation.

### "It's all encrypted, so nothing is recoverable"

**Check the encryption paradigm first.** Fast families encrypt only a fraction of large files. The Gentlemen at `--ultrafast` encrypts roughly 0.9% of a large file, leaving **~99% as plaintext** — and large files are exactly the databases, VM disks, and mail stores those modes target.

Determining the mode is an early, high-value triage task. See [the case study](06-Case-Studies/the-gentlemen/).

### "One recovered key unlocks everything"

**Only with a session-key design.** Per-file keys mean one recovered key decrypts one file. Check before you promise anything:

```bash
for f in *.locked; do tail -c 512 "$f" | sha256sum | cut -d' ' -f1; done | sort -u | wc -l
```

`1` means session key. `N` means per-file.

### "Paying guarantees we get the data back"

**It does not.** Decryptors are frequently buggy, slow, or incomplete, and some actors never deliver. Payment decisions are legal, regulatory, and commercial — not technical — and sanctions exposure is real in some jurisdictions. Your job is to give an accurate technical picture of what is recoverable without payment. Say what you know and flag what you do not.

### "We found a decryptor online, let's run it"

**Verify it first.** Fake decryptors exist, some of which are themselves ransomware. Before running anything on client data: obtain it from a known source such as No More Ransom or the vendor directly, test it in an isolated VM, and **always work on copies**. "We ran the tool and it ate the last good copy" is a real failure mode.

### "Static analysis is risky"

**Static analysis never executes anything.** Strings, entropy, constant hunting, and disassembly are safe on any machine. `parse_footer.py` and `identify_crypto.py` are read-only and stdlib-only. Modules 00–04 and most of 08 need no detonation at all. Reserve the isolated VM for when you genuinely need runtime behaviour.

### "The sample needs a password, so it can't run accidentally"

**The gate is operator convenience, not a safety feature.** MSTIC notes The Gentlemen's password check is a static comparison, identifiable and bypassable through static analysis. Treat a gated sample as fully live — including while experimenting with command-line arguments.

### "No crypto imports means no encryption"

**Go and Rust binaries link statically.** There is no import table to read. Pivot to constant hunting with [`identify_crypto.py`](tools/identify_crypto.py). And AES-NI implementations have no lookup tables at all, so constant scanning misses them too — look for `AESENC` and `AESKEYGENASSIST` instructions instead.

### "This family uses AES, the blog said so"

**Reporting ages badly.** Variants diverge, builders leak and get modified, affiliates recompile. The family table in [`references/CIPHER-IDENTIFICATION.md`](references/CIPHER-IDENTIFICATION.md) is explicitly a hypothesis set, not a conclusion. Confirm per sample. A wrong scheme assumption produces a confidently incorrect recoverability verdict, which is the worst deliverable in this field.
