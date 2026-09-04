# Labs

**Read [`SAFE_LAB_SETUP.md`](SAFE_LAB_SETUP.md) before handling any live sample.** It is referenced as mandatory from several modules for a reason: ransomware is the one malware class where an analysis mistake destroys data immediately and irreversibly.

## You probably do not need a live sample

Every lab in this repository can be completed with synthetic specimens:

```bash
python3 ../01-Symmetric-Cryptography/labs/encryption_demo.py specimens --outdir ./lab-samples
python3 ../capstone/generate_incident.py --outdir ./incident-alpha
```

Neither contains malware. The capstone's "encryptor" is an inert file of crypto constants with no code, and encrypted specimens are produced by overwriting regions with random bytes — no key exists, so nothing can be decrypted. That is deliberate: the exercises ask what is *recoverable*, and the answer never depends on obtaining a key.

Synthetic specimens are also **better for practice**, because you know the ground truth and can check your answers.

## When you do need a live sample

| Need | Live sample required? |
|---|---|
| Entropy, triage, paradigm identification | No |
| Constant hunting, static analysis | No |
| Footer and key-model determination | No |
| Partial recovery | No |
| API call traces, runtime behaviour | Yes |
| Memory key recovery | Yes — or suspend a VM running the demo |
| Persistence, propagation artifacts | Yes |

Modules 00–04 and most of 08 need no detonation at all.

## Contents

| | |
|---|---|
| [`SAFE_LAB_SETUP.md`](SAFE_LAB_SETUP.md) | **Mandatory.** Isolation, snapshots, ransomware-specific precautions |
| [`SAMPLE_SOURCING.md`](SAMPLE_SOURCING.md) | Obtaining samples legitimately, and the rules around handling them |

## The one rule

Never store samples, specimens, or VM disks in a synced folder, a repository, or anywhere with an automatic backup job. The repository [`.gitignore`](../.gitignore) blocks the obvious cases, but it cannot protect you from OneDrive.
