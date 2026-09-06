# Contributing

This is a teaching site about encryption. The bar for a change is whether it helps a reader
understand something they did not understand before.

## Scope

**Concepts only.** This site explains how encryption schemes work and how to recognise them from
their output. It does not contain, and will not accept:

- Encryption or decryption tooling of any kind
- Malware, or code derived from it
- Data recovery procedures
- Operational or incident-response material
- Anything that reads as a set of instructions rather than an explanation

The line is not about difficulty or sensitivity. It is that this is a course about how the
mathematics works, and material that is operational belongs somewhere else.

## Most valuable contributions

1. **Corrections to the cryptography.** A wrong size, a mischaracterised algorithm, an
   oversimplification that becomes false. These matter most because people learn from this.
2. **Explanations that land better.** If an idea can be made clearer with a better analogy, a
   worked example or a diagram, that is a real improvement.
3. **Simulations.** Anything that turns an abstract claim into something a reader can operate.

## Standards

**Content**
- Explain the mechanism, not just the name. "It uses AES-256" teaches nothing on its own.
- Prefer a worked example over an assertion.
- Where a claim is commonly stated and wrong, say so and say why.
- Keep modules above the word floor the tests enforce — a thin module is worse than no module.

**Code**
- Simulations use the standard Web Crypto API. Real cryptography, never a mock-up.
- Keys are fixed and printed on screen. Nothing on this site should be secret or irreversible.
- No build step and no runtime dependencies. It must work from a static file server.

**Before opening a pull request**

```bash
python3 engine.py            # pages are generated, never edited directly
python3 make_structure.py
python3 -m unittest discover tests
```

All three must succeed. Edit `pages.py`, not the HTML — hand edits are overwritten on the next
build, and a test checks that the checked-in pages match a fresh build exactly.

## Flaky tests are bugs

If a test passes intermittently, find out why before relaxing it. An intermittent failure here
once revealed a signature short enough to match by chance on any large input.

```bash
for i in $(seq 1 60); do python3 -m unittest discover tests 2>&1 | grep -E "^(FAIL|ERROR):"; done | sort | uniq -c
```
