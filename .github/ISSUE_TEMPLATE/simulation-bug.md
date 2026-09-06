---
name: Simulation not working
about: A simulation on a module page misbehaves or does not render
labels: bug
---

**Which page and simulation**

**Browser and version**
Simulations use the Web Crypto API, which requires a secure context — they will not run from a
`file://` URL. Confirm you are viewing over http(s).

**Expected vs actual**

**Console errors**
```
```

**Is it intermittent?**
Flaky behaviour is treated as a bug here, not noise.
