---
name: Tool bug
about: A tool gives a wrong or unstable result
labels: bug
---

**Tool and command**
```
```

**Expected vs actual**

**Is it intermittent?**
Flaky results are treated as bugs here — an intermittent failure previously
revealed a signature short enough to hit by chance on any large file.
```bash
for i in $(seq 1 60); do python3 tests/test_tools.py 2>&1 | grep -E "^(FAIL|ERROR):"; done | sort | uniq -c
```

**Input characteristics**
Size, format, and how it was generated. Do NOT attach malware or client data.
