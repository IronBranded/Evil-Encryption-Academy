# Contributing

Contributions are welcome. Read [`SCOPE.md`](SCOPE.md) first — it defines what this repository will and will not accept, and why.

## Will be closed without merge

Anything from the omitted list in [`SCOPE.md`](SCOPE.md): encryptor code, target-selection logic, anti-recovery implementations, throughput optimization, evasion techniques, or working exploit code. Framing it as educational does not change what the code does once merged.

## Wanted

- **Detection content** — YARA, Sigma, hunting queries, behavioral analytics
- **Analysis and recovery tooling** — anything that reads and reports, or that helps a victim get data back
- **Case studies** grounded in primary sources, following [`06-Case-Studies/_template/`](06-Case-Studies/_template/)
- **Corrections** — especially to constants, event IDs, API details, and family attributions
- **Better explanations** — this is a teaching repository first

## Standards

**Code**
- Analysis tools are **stdlib-only** where possible, so they run on a locked-down forensic workstation with no package installs
- Tools are **read-only**. Nothing in this repository may modify, rename, or delete a target file
- Add a regression test in [`tests/`](tests/) for any behavior change. Every existing test is there because a real bug shipped
- `python -m unittest discover tests` must pass, and must pass **repeatedly**

**Flaky tests are bugs, not annoyances.** A test that failed 3 times in 60 runs led directly to finding a 3-byte signature in `parse_footer.py` that would have hit ~60 times by chance on a 1 GB file, silently re-introducing a fixed false positive. If a test is intermittent, find out why before you relax it:

```bash
for i in $(seq 1 60); do python3 tests/test_tools.py 2>&1 | grep -E "^(FAIL|ERROR):"; done | sort | uniq -c
```

**Content**
- Cite **primary sources**. Vendor writeups over summaries, and always link the original
- If sources conflict and there is no authoritative answer, **say so** rather than picking one. Module 04 does this with BitLocker event IDs
- Include a date on any claim about a family. Reporting ages fast
- Follow the module structure: layman analogy → mechanics → real-world usage → artifacts and detection → hands-on

## Verification discipline

Before claiming a tool handles a scheme, **reconstruct a specimen from the described layout and confirm it**. Doing this against The Gentlemen's footer exposed a blind spot that had shipped, and the fix is now covered by a test.

## Reporting a problem with the content

Wrong constants, incorrect event IDs, and stale family attributions are the highest-value bug reports. Open an issue with the primary source that contradicts what is written.
