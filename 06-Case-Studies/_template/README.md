# Case Study — <Family> (<Actor>)

![Source](https://img.shields.io/badge/primary%20source-<vendor>%20<date>-blue.svg)

**Primary source:** <link>. State clearly what is sourced and what is your own analysis.

## 1. Operator and model
Actor tracking name, RaaS or closed, timeline, targeting, extortion model.

## 2. The cryptographic scheme
Bulk cipher, key wrap, per-file or per-session keys. A Mermaid diagram of the key flow.
**This section determines recoverability. It is the most important part of the study.**

## 3. Encryption paradigm
Full, intermittent, header-only or distributed-chunk. Percentages if published.
**Quantify surviving plaintext** — it is the partial-recovery lever.

## 4. Key storage layout
Footer, header or sidecar. Binary blob or text? Delimiters and markers.
Reconstruct a specimen and confirm `parse_footer.py` handles it. Report if it does not.

## 5. Analysis notes
Language and toolchain, obfuscation, packing, execution gating, extension and note names.

## 6. Detection and response
Anti-recovery behaviour, persistence, propagation. What artifacts survive log clearing.
Link to the source for IOCs rather than copying them — they age fast and the source is maintained.

## 7. Exercises

## 8. References
