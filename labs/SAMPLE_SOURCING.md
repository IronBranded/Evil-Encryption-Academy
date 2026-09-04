# Sample Sourcing

**This repository hosts no samples and no direct sample links.** Read [`SAFE_LAB_SETUP.md`](SAFE_LAB_SETUP.md) before obtaining any.

## You may not need one

Synthetic specimens cover most labs and give you ground truth to check your answers against:

```bash
python3 ../01-Symmetric-Cryptography/labs/encryption_demo.py specimens --outdir ./lab-samples
```

Live samples are needed only for runtime behavior: API traces, memory key recovery, persistence, propagation.

## Legitimate sources

| Source | Access | Notes |
|---|---|---|
| **MalwareBazaar** (abuse.ch) | Free, no account for browsing | Well-tagged by family. Most accessible starting point |
| **VirusTotal** | Paid API for downloads | Enterprise-grade. Retrohunt is excellent for finding variants |
| **VirusShare** | Free, invite-based | Large historical archive |
| **MalShare** | Free API key | Good daily feeds |
| **theZoo** / vx-underground | Public repositories | Curated, includes historical families |
| **Your own IR engagements** | With written client authorization | The most relevant samples you will ever have |

## Rules

- **Written authorization first** on any employer equipment or network.
- **Verify the hash** against the source's published value before and after transfer.
- **Never redistribute.** Sharing samples outside a controlled channel can be an offence.
- **Never upload client samples to public services.** VirusTotal submissions are visible to subscribers, and a sample can leak an engagement, a victim identity, or embedded credentials. This has ended careers.
- Check your jurisdiction. Some restrict possession of malicious code.

## Choosing a sample for a module

| Module | What you need |
|---|---|
| 01–03 | Nothing live. Synthetic specimens are better — you know the ground truth |
| 04 | A BitLocker-abusing script sample, or reproduce the technique yourself in a lab VM |
| 06 | The specific family the case study covers |
| 07 | A memory image captured mid-encryption. Suspend the VM to produce one safely |
| 08 | Any packed or Go/Rust-compiled family, for constant hunting |
