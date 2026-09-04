# Primary Sources

Ground every claim in this repository in primary reporting. Secondary sources drift, and AI-generated security content increasingly does not survive contact with the vendor documentation it claims to summarize.

---

## Tier 1 — the anchor feed

### [Microsoft Security Blog — Ransomware](https://www.microsoft.com/en-us/security/blog/threat-intelligence/ransomware/)

**This is the primary reference feed for this curriculum.** MSTIC publishes full encryptor teardowns including cryptographic scheme, footer layout, command-line surface, IOCs, Defender detections, and KQL hunting queries. Very few sources give you the crypto design at that level.

Check it before writing or updating any module. Case studies here are built from it, and the family table in [`CIPHER-IDENTIFICATION.md`](CIPHER-IDENTIFICATION.md) is a hypothesis set that this feed supersedes.

**Articles mapped to modules:**

| Article | Date | Relevance |
|---|---|---|
| [DeadLock ransomware: Breaking down a Rust-based encryptor with decentralized recovery infrastructure](https://www.microsoft.com/en-us/security/blog/2026/08/10/deadlock-ransomware-breaking-down-a-rust-based-encryptor-with-decentralized-recovery-infrastructure/) | Aug 2026 | Rust encryptor; decentralized victim-communication and leak infrastructure. **Written up: [`06-Case-Studies/deadlock/`](../06-Case-Studies/deadlock/)** |
| [The Gentlemen ransomware: Dissecting a self-propagating Go encryptor](https://www.microsoft.com/en-us/security/blog/2026/05/28/the-gentlemen-ransomware-dissecting-a-self-propagating-go-encryptor/) | May 2026 | Per-file ephemeral Curve25519 + XChaCha20. **Written up: [`06-Case-Studies/the-gentlemen/`](../06-Case-Studies/the-gentlemen/)** |
| [Exposing Fox Tempest: A malware-signing service operation](https://www.microsoft.com/en-us/security/blog/2026/05/19/exposing-fox-tempest-a-malware-signing-service-operation/) | May 2026 | Malware-signing-as-a-service. Why code signing is weak evidence of trust |
| [Storm-1175 focuses gaze on vulnerable web-facing assets in high-tempo Medusa ransomware operations](https://www.microsoft.com/en-us/security/blog/2026/04/06/storm-1175-focuses-gaze-on-vulnerable-web-facing-assets-in-high-tempo-medusa-ransomware-operations/) | Apr 2026 | Medusa operations; vulnerability-driven initial access |
| [Investigating active exploitation of CVE-2025-10035 GoAnywhere MFT vulnerability](https://www.microsoft.com/en-us/security/blog/2025/10/06/investigating-active-exploitation-of-cve-2025-10035-goanywhere-managed-file-transfer-vulnerability/) | Oct 2025 | Managed file transfer as an access vector |
| [Storm-0501's evolving techniques lead to cloud-based ransomware](https://www.microsoft.com/en-us/security/blog/2025/08/27/storm-0501s-evolving-techniques-lead-to-cloud-based-ransomware/) | Aug 2025 | **Cloud-native ransomware.** Directly supports [Module 04](../04-Platform-And-LOTL-Encryption/) |
| [Unveiling RIFT: Enhancing Rust malware analysis through pattern matching](https://www.microsoft.com/en-us/security/blog/2025/06/27/unveiling-rift-enhancing-rust-malware-analysis-through-pattern-matching/) | Jun 2025 | Open-source tooling for Rust malware. **Addresses the statically-linked-binary problem flagged in [`identify_crypto.py`](../tools/identify_crypto.py) — evaluate for Module 08** |
| [Exploitation of CLFS zero-day leads to ransomware activity](https://www.microsoft.com/en-us/security/blog/2025/04/08/exploitation-of-clfs-zero-day-leads-to-ransomware-activity/) | Apr 2025 | Privilege escalation preceding deployment |
| [Ransomware operators exploit ESXi hypervisor vulnerability for mass encryption](https://www.microsoft.com/en-us/security/blog/2024/07/29/ransomware-operators-exploit-esxi-hypervisor-vulnerability-for-mass-encryption/) | Jul 2024 | Hypervisor-level mass encryption. Supports [Module 04](../04-Platform-And-LOTL-Encryption/) |
| [Storm-0501: Ransomware attacks expanding to hybrid cloud environments](https://www.microsoft.com/en-us/security/blog/2024/09/26/storm-0501-ransomware-attacks-expanding-to-hybrid-cloud-environments/) | Sep 2024 | Hybrid cloud targeting |

> Two of the above post-date this repository's last full review. Re-read the feed before treating any module as current.

---

## Tier 1 — other primary reporting

| Source | What it gives you |
|---|---|
| [CISA #StopRansomware](https://www.cisa.gov/stopransomware) | Joint advisories with per-family IOCs and mitigations |
| [The DFIR Report](https://thedfirreport.com/) | Full intrusion timelines at artifact level, with timestamps |
| Kaspersky Securelist | Original ShrinkLocker analysis; deep technical teardowns |
| [Bitdefender Business Insights](https://www.bitdefender.com/en-us/blog/businessinsights/) | ShrinkLocker analysis and decryptor |
| [No More Ransom](https://www.nomoreransom.org/) | **Check before declaring anything unrecoverable** |
| Microsoft Learn | CNG, CryptoAPI, BitLocker, VSS documentation |

---

## How to read a threat-intel report for this curriculum

Most reports are written for detection engineers, not cryptographers. Extract in this order:

1. **The cryptographic scheme.** Which bulk cipher, which key wrap, per-file or per-session keys. This determines recoverability and is often buried mid-article.
2. **The footer or key-storage layout.** Binary blob or text? Which delimiters? This tells you whether your triage tooling can even see it.
3. **The encryption paradigm.** Full, intermittent, or distributed chunks, and at what percentage. This tells you how much plaintext survives.
4. **Anti-recovery behavior.** Which logs cleared, which backups targeted. This tells you which artifacts you can still trust.
5. **IOCs last.** They age fastest and are the least transferable part of any report.

Steps 1–3 are what this repository teaches and what most readers skip.

### Verification discipline

- **Prefer the vendor's own writeup** over any summary of it.
- **Check dates.** A 2023 scheme description may not describe the variant in front of you.
- **Reconstruct, do not assume.** Build a specimen matching the described layout and confirm your tools handle it. Doing this for The Gentlemen exposed a real blind spot in `parse_footer.py`.
- **Treat family-to-algorithm tables as hypotheses.** Builders leak, affiliates recompile, variants diverge.
- **Be wary of low-quality aggregators.** While researching Module 04, several sites gave contradictory meanings for the same BitLocker event IDs, disagreeing with Microsoft's own documentation. Where sources conflict and no authoritative answer exists, the module says so and tells the reader to enumerate their own environment rather than shipping a confident guess.
