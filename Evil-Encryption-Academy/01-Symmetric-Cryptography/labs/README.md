# Module 01 Labs — Seeing Encryption Happen

`encryption_demo.py` exists because entropy scores are meaningless until you have watched data turn into noise once.

It also solves a practical problem: Module 02 asks you to triage encrypted files, but you should not be handling live ransomware to get practice material. Demo 4 generates safe specimens instead.

```bash
pip install cryptography
python3 encryption_demo.py hexdump      # before/after: bytes, entropy, histogram
python3 encryption_demo.py modes        # why ECB is broken
python3 encryption_demo.py avalanche    # one bit in, half the output changes
python3 encryption_demo.py specimens    # lab files for parse_footer.py
python3 encryption_demo.py roundtrip    # prove it is reversible
python3 encryption_demo.py all
```

## Why this is a demo and not an encryptor

Four properties, all deliberate:

| Property | This tool | Ransomware |
|---|---|---|
| Key origin | Fixed, hardcoded, **printed on every run** | Random per file or per host, never shown |
| Key protection | None. It is public | Wrapped under the attacker's public key |
| Key lifetime | Permanent | Wiped from RAM after use |
| Original file | Never touched. Output is a new file | Overwritten or deleted |
| Asymmetric ops | **None. No RSA, no public key** | RSA/ECC wrap is the whole mechanism |

Ransomware is defined by irreversibility for the victim. Remove the random key, the asymmetric wrap, and the key destruction, and what remains is a cryptography tutorial. Demo 5 decrypts everything it encrypts, which is the point.

The 256-byte "footer" in Demo 4 is random filler sized like an RSA-2048 ciphertext, so `parse_footer.py` has a realistic tail to identify. It is not a wrapped key. This script performs no asymmetric operations at all.

---

## Demo 1 — Before and after

Same data, twice. Encryption does not compress or shuffle; it maps structure onto noise.

```
BEFORE - plaintext                          AFTER - AES-256-CBC
00000000  49 4e 56 4f 49 43 45 20            00000000  01 fa 9b 39 dc 10 c6 f2
          |INVOICE #2024-04|                           |...9....=.@.}.6.|

  entropy 5.122 / 8.000                       entropy 7.593 / 8.000

  |      █                         |          |███ ██████ ████████ ██ ███ ███ |
  |      █       █                 |          |████████████████████████████████|
  | █  █ ████  ███                 |          |████████████████████████████████|
  | █  ███████ ███                 |          |████████████████████████████████|
  +--------------------------------+          +--------------------------------+
   0x00                       0xFF             0x00                       0xFF
   spiky: ASCII clusters                       flat: every value equally likely
```

That flat histogram **is** the entropy score `parse_footer.py` reports. Once you have seen it, 7.99 stops being a number and becomes a shape.

## Demo 2 — Why mode of operation matters

Each 16-byte AES block is drawn as one uniform shade keyed to its contents. Same shade means byte-identical block.

```
PLAINTEXT BLOCKS                            AES-256-ECB  <-- shape leaks through
                                            ++++++++++++++++++++++++++++++++
        ████████████████%%%%%%%%%%%%        ++++++++++++++++################
        ++++++++++++++++++++++++++++        ++++++++++++++++%%%%%%%%%%%%%%%%
        ================████████████        ++++++++++++++++    @@@@@@@@@@@@
        ****************++++++++++++        ++++++++++++++++****############
%%%%%%%%::::::::::::::::::::::::::::        ----------------================
%%%%%%%%@@@@@@@@@@@@········::::::::        ----------------%%%%%%@@@@@@%%%%
%%%%%%%%████████████::::::::::::::::        ----------------██████::::::%%%%
```

The padlock survives ECB. Different shades, identical structure. ECB encrypts each block independently, so identical plaintext blocks always produce identical ciphertext blocks and every uniform region stays uniform.

```
    plaintext entropy    0.935
    ECB entropy          6.684
    CBC entropy          7.905

    distinct 16-byte blocks, ECB:  15 of 128
    distinct 16-byte blocks, CBC: 128 of 128
```

**ECB scores 6.68 entropy and is still completely broken.** High entropy means "looks random". It does not mean "secure". This is the single most common misreading of an entropy number in DFIR work, and the block-count line is the measurement that actually catches it.

Practical consequence: if you ever find an encrypted file whose 16-byte blocks repeat, you are looking at ECB, and repeated ciphertext blocks map directly to repeated plaintext. That leaks file structure and sometimes enables partial recovery without any key at all.

## Demo 3 — Avalanche

Flip one bit of a 80-byte plaintext:

```
  bytes changed : 80 of 80
  bits changed  : 311 of 640 (48.6%)
```

Roughly half of every output bit changed. There is no partial progress against a cipher and no "close enough" key. Guessing 255 of 256 key bits correctly gets you exactly nothing, which is why brute force is not a recovery strategy and why memory forensics is.

## Demo 4 — Lab specimens

```bash
python3 encryption_demo.py specimens --outdir ./lab-samples
python3 ../../02-Hybrid-Encryption-Model/labs/parse_footer.py ./lab-samples --recurse
```

Generates three specimens plus the untouched original:

| File | Entropy | Expected verdict |
|---|---|---|
| `invoice.xlsx` | 4.951 | NOT ENCRYPTED |
| `invoice.xlsx.full-enc` | 7.996 | FULL ENCRYPTION |
| `invoice.xlsx.intermittent` | 7.316 | INTERMITTENT (≈44% recoverable) |
| `invoice.xlsx.header-only` | 5.713 | HEADER-ONLY |

**Predict each verdict before running the triage tool.** Then work out why you were wrong where you were.

The intermittent specimen is the one to sit with. Its profile looks like this:

```
ENTROPY PROFILE (4096-byte blocks)
  █▅█▅█▅█▅█
  low ▁▁▁ plaintext / structured      high ███ ciphertext
```

Every `▅` is plaintext that survived. That is what makes partial recovery possible against fast-encryption families, and reading that pattern correctly is a billable skill.

Then settle the footer size:

```bash
python3 ../../02-Hybrid-Encryption-Model/labs/parse_footer.py \
    ./lab-samples/invoice.xlsx.full-enc --original ./lab-samples/invoice.xlsx
```
```
  overhead   272 bytes
     if RSA-2048 wrapped key: 16 bytes of other overhead
```

272 = 256-byte footer + 16 bytes of PKCS#7 padding. Every byte accounted for.

## Demo 5 — Roundtrip

```
  byte-for-byte identical: True
  sha256 before: dc985401a68faff03051c78bbf32bb2fd27ba216b0dba19b050b936d534b8ba9
  sha256 after:  dc985401a68faff03051c78bbf32bb2fd27ba216b0dba19b050b936d534b8ba9
```

Encryption is a reversible transformation. It is not damage and it is not deletion. An encrypted file is fully intact and simply unreadable without the key.

A ransomware victim sits in exactly this position with one difference: the key is not printed at the top of the screen. It was random, it was wrapped under a public key whose private half lives on attacker infrastructure, and it was wiped from RAM.

That gap — between a key you have and a key you do not — is the entire incident. It is also the whole argument for capturing memory before the host is rebooted. See [Module 02, section 6](../../02-Hybrid-Encryption-Model/README.md#6-recovering-the-key-from-memory).

---

## Exercises

1. Change `DEMO_PASSPHRASE`. Does the entropy of the output change? Should it?
2. Run `modes` twice. Why is the ECB output identical across runs, and what does that imply about a family that uses a fixed key?
3. Modify the intermittent specimen to encrypt 1 KB in every 16 KB. At what ratio does `parse_footer.py` stop calling it intermittent, and is the tool wrong or is the question ill-posed?
4. The `--original` delta gave 272 bytes. Construct a specimen where the delta is ambiguous between two key sizes. What extra evidence would resolve it in a real incident?
