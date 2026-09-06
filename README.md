# Evil Encryption Academy

**[→ ironbranded.github.io/Evil-Encryption-Academy](https://ironbranded.github.io/Evil-Encryption-Academy/)**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Modules](https://img.shields.io/badge/modules-11%20%2B%20reference-brightgreen.svg)
![Simulations](https://img.shields.io/badge/simulations-Web%20Crypto-orange.svg)
![Build](https://img.shields.io/badge/build-static%2C%20no%20dependencies-lightgrey.svg)

A course on encryption, and how ransomware uses it.

Ransomware is an applied cryptography problem wearing a Windows costume. Strip away the delivery
and the extortion and every family reduces to four decisions: which cipher encrypts the data, which
one protects the key, how much of each file gets touched, and whether one key is used or thousands.

This site explains those decisions from first principles — what encryption is, how the ciphers
work, how they combine, and how to tell one scheme apart from another using nothing but the
encrypted output.

## Scope

**Concepts only.** There is no tooling here, no malware, no recovery procedures and no operational
material of any kind. Every simulation runs in the reader's browser using the standard Web Crypto
API, and every key is fixed and printed on screen — nothing is secret and nothing is irreversible.

The site treats encryption as a neutral mechanism. The same hybrid construction that locks a file
server also secures a banking session. What changes is not the mathematics but who holds the key.

## The modules

| # | Module | The idea |
|---|---|---|
| | **Foundations** | |
| 01 | What encryption is | Four operations people confuse, and the one that actually locks something |
| 02 | Keys and randomness | Where keys come from, and why that origin decides everything |
| 03 | Hashing and integrity | Proving data has not changed, which is a different problem from hiding it |
| | **The two families** | |
| 04 | Symmetric encryption | AES rounds and key schedule; the ChaCha20 state |
| 05 | Modes of operation | Where a correct cipher still produces a broken result |
| 06 | Asymmetric encryption | RSA arithmetic, capacity limits, elliptic curves, key agreement |
| | **Ransomware encryption** | |
| 07 | The hybrid scheme | The construction behind essentially every family |
| 08 | How much gets encrypted | Full, header-only, intermittent, chunked |
| 09 | Key models | Session keys, per-file keys, ephemeral key agreement |
| 10 | OS-native encryption | When the operating system does the encrypting |
| | **Putting it together** | |
| 11 | Telling them apart | Identifying a scheme from its output alone |
| — | Reference | Sizes, constants, glossary, common misconceptions |

## Simulations

Every module carries at least one, and they run real cryptography rather than mock-ups:

- The same image encrypted with AES-ECB and AES-CBC under an identical key, showing the picture
  survive one of them intact
- A working RSA keypair with small primes, refusing to encrypt anything larger than its modulus
- A key generated securely and a key seeded from the clock, which look identically random
- Coverage patterns drawn across a file, with entropy measured per slice
- An identification quiz answerable from encrypted output alone

Web Crypto deliberately omits ECB, so the ECB demonstration encrypts each 16-byte block under a
zero IV — mathematically identical, and it shows the genuine failure rather than an illustration
of one.

## Building

The site is static HTML with no build dependencies. Pages are generated from a single template so
navigation, metadata and structure stay consistent.

```bash
python3 engine.py            # regenerate every page from pages.py
python3 make_structure.py    # regenerate STRUCTURE.txt from the tree
python3 -m unittest discover tests
```

| File | Purpose |
|---|---|
| `engine.py` | Page template engine |
| `pages.py` | All page content |
| `svg_diagrams.py` | SVG diagram components, theme-aware |
| `assets/academy.css` | Styles, including dark mode |
| `assets/academy.js` | Crypto helpers, progress tracking, theme, keyboard navigation |

## Tests

Every test guards against something that actually went wrong during development — a JavaScript
escape that silently broke a page, a structure map that drifted to describe a different project, a
module that fell below a word floor. They are not coverage for its own sake.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Corrections to the cryptography are the most valuable
contributions; explanations that make an idea land better are a close second.

## License

MIT. See [LICENSE](LICENSE).
