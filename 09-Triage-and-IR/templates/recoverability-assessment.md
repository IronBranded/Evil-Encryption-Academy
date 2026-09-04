# Recoverability Assessment — <CLIENT> — <DATE>

> Client-facing. One page. An executive must be able to act on this without a translator.
> Delete the guidance in blockquotes before sending.

## Bottom line

<One paragraph. What is recoverable, what is not, and what you need to decide next.
Lead with the answer, not the methodology.>

**Example:** *Your data is intact but unreadable without a decryption key. Nothing was
deleted. We expect to recover approximately 91% of the content of large files
(databases, mail archives, VM images) without any key, using surviving unencrypted
portions. Files under 1 MB were fully encrypted and are not recoverable by this method.
We are still assessing backup viability, which is the fastest route to full recovery.*

## What we have confirmed

| Finding | Basis |
|---|---|
| <e.g. Per-file encryption keys> | <e.g. Footer comparison across 40 samples; all distinct> |
| <e.g. ~9% of each large file encrypted> | <e.g. Entropy region mapping, 12 files sampled> |
| <e.g. Files under 1 MB fully encrypted> | <e.g. Consistent across all 18 small files examined> |

> Every row needs a basis. "Unfortunately not recoverable" with no basis is not an
> assessment, it is a guess, and it will be challenged.

## Recovery routes assessed

| Route | Status | Notes |
|---|---|---|
| Backups (offline / immutable) | ☐ Viable ☐ Not viable ☐ **Unverified** | |
| Key escrow (AD / Entra / MBAM) | ☐ Recovered ☐ Not configured ☐ N/A | |
| Published decryptor | ☐ Available ☐ None known | |
| Key recovery from memory | ☐ Recovered ☐ Attempted, unsuccessful ☐ **Not possible — hosts rebooted** | |
| Partial recovery from surviving data | ☐ Viable — __% ☐ Not viable | |

> Mark anything unverified as unverified. Do not let an unchecked box read as a negative.

## What we do not yet know

- <Be explicit. List the open questions and when you will have answers.>

> An early confident wrong answer about recoverability is more damaging than an
> honest unknown, because irreversible decisions get made on it.

## What we need from you

- <Decisions, access, authority. Be specific and give deadlines.>

## Important caveats

- Encrypted originals are being **preserved**. All recovery work is performed on copies.
- Recovery percentages describe **content volume**, not necessarily usable files. Damaged
  file structure may still require format repair.
- <Exfiltration status — this drives legal and notification obligations and is often a
  bigger exposure than the encryption.>

---
*Prepared by <name>, <role>. Basis: <evidence set>. Next update: <when>.*
