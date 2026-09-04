#!/usr/bin/env python3
"""
identify_crypto.py - Identify cryptographic algorithms by their fingerprints.

WHY THIS WORKS
    Cipher implementations cannot hide. Almost every algorithm requires
    hardcoded tables, initialization vectors, or derived constants that must
    exist verbatim in the binary. AES needs its S-box. SHA-256 needs its round
    constants. ChaCha20 needs the ASCII string "expand 32-byte k". These are
    mathematically required, not stylistic, so they survive obfuscation of
    names, stripped symbols, and static linking.

    This is the fallback when there is no import table to read - which is the
    normal case for Rust and Go ransomware families.

WHAT IT SCANS
    PE/ELF binaries, memory dumps, raw volumes, encrypted files, scripts.

USAGE
    python3 identify_crypto.py sample.exe
    python3 identify_crypto.py memdump.raw --min-confidence high
    python3 identify_crypto.py /dev/sdb1 --categories container
    python3 identify_crypto.py sample.exe --json

    Stdlib only. Read-only.

LIMITS
    A hit proves the constant is present, not that the algorithm is USED.
    Statically linked runtimes drag in crypto the malware never calls. Treat
    output as leads to confirm in a disassembler, never as a verdict.

Part of Evil-Encryption-Academy. See references/CIPHER-IDENTIFICATION.md.
MIT licensed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Signature database
#   (name, category, pattern, confidence, note)
# Multi-byte integer constants are given in little-endian memory order, which
# is how they appear in a compiled x86/x64 image.
# ---------------------------------------------------------------------------

SIGS = [
    # --- Block ciphers -----------------------------------------------------
    ("AES S-box", "symmetric",
     bytes.fromhex("637c777bf26b6fc53001672bfed7ab76"), "high",
     "Forward S-box. Present in nearly every software AES."),
    ("AES inverse S-box", "symmetric",
     bytes.fromhex("52096ad53036a538bf40a39e81f3d7fb"), "high",
     "Inverse S-box. Its presence means DECRYPTION is implemented too."),
    ("AES Te0 table", "symmetric",
     bytes.fromhex("a56363c6847c7cf8997777ee8d7b7bf6"), "high",
     "T-table AES (OpenSSL-style). Speed-optimized implementation."),
    ("AES Rcon", "symmetric",
     bytes.fromhex("01020408102040801b36"), "medium",
     "Round constants. Short, so prone to coincidence."),
    ("Blowfish P-array (pi digits)", "symmetric",
     bytes.fromhex("886a3f24d308a385"), "high",
     "Blowfish/bcrypt initialization from pi."),
    ("Twofish q0 table", "symmetric",
     bytes.fromhex("a967b3e804fda376"), "medium", "Twofish permutation table."),
    ("TEA/XTEA delta", "symmetric",
     bytes.fromhex("b979379e"), "low",
     "0x9E3779B9, the golden ratio. Also in Serpent, RC5/RC6, and many hashes."),
    ("RC5/RC6 P32", "symmetric",
     bytes.fromhex("6351e1b7"), "medium", "0xB7E15163. Pair with Q32 to confirm."),
    ("DES initial permutation", "symmetric",
     bytes.fromhex("3a322a221a120a02"), "medium", "Legacy. Rare in modern families."),
    ("CAST-128 S-box head", "symmetric",
     bytes.fromhex("d2c4a3f430a8b19c"), "low", "Uncommon."),

    # --- Stream ciphers ----------------------------------------------------
    ("ChaCha/Salsa sigma (256-bit)", "symmetric",
     b"expand 32-byte k", "high",
     "ChaCha20 or Salsa20 with a 256-bit key. Very strong indicator."),
    ("ChaCha/Salsa tau (128-bit)", "symmetric",
     b"expand 16-byte k", "high", "128-bit key variant."),
    ("ChaCha sigma as dwords", "symmetric",
     bytes.fromhex("617078653320646e79622d326b206574"), "high",
     "Same constant compiled as four dwords rather than a string."),
    ("XChaCha20 (extended-nonce ChaCha)", "symmetric",
     b"expand 32-byte k", "high",
     "Shares ChaCha20's sigma. Distinguish by NONCE SIZE: 24 bytes (XChaCha20) "
     "vs 12 (ChaCha20 IETF) vs 8 (original). XChaCha20 derives a subkey via HChaCha20."),
    ("Poly1305 clamp", "aead",
     bytes.fromhex("ffffff0ffcffff0ffcffff0ffcffff0f"), "high",
     "ChaCha20-Poly1305 AEAD. Pair with the sigma constant."),
    ("HC-128 init", "symmetric",
     bytes.fromhex("965fa1f2"), "low", "Rare eSTREAM cipher."),

    # --- Hashes and KDFs ---------------------------------------------------
    ("MD5 init state", "hash",
     bytes.fromhex("0123456789abcdeffedcba9876543210"), "high", "MD5 or MD4."),
    ("SHA-1 init state", "hash",
     bytes.fromhex("0123456789abcdeffedcba9876543210f0e1d2c3"), "high",
     "SHA-1 (MD5 state plus a fifth word)."),
    ("SHA-256 init state", "hash",
     bytes.fromhex("67e6096a85ae67bb72f36e3c3af54fa5"), "high",
     "SHA-256. Also the IV for BLAKE2s and BLAKE3."),
    ("SHA-256 round constants", "hash",
     bytes.fromhex("982f8a4291443771cffbc0b5a5dbb5e9"), "high", "SHA-256 K table."),
    ("SHA-512 init state", "hash",
     bytes.fromhex("08c9bcf367e6096a3ba7ca8485ae67bb"), "high",
     "SHA-512/384. Also the BLAKE2b IV."),
    ("SHA-3 / Keccak round constants", "hash",
     bytes.fromhex("01000000000000008200000000000000"), "medium", "Keccak iota."),
    ("CRC32 table", "hash",
     bytes.fromhex("00000000963007772c610eeeba510999"), "high",
     "Not cryptographic. Often used for file integrity marking."),
    ("bcrypt magic", "kdf",
     b"OrpheanBeholderScryDoubt", "high", "bcrypt password hashing."),
    ("scrypt identifier", "kdf", b"scrypt", "low", "String reference only."),
    ("Argon2 identifier", "kdf", b"argon2", "medium", "Modern password KDF."),
    ("PBKDF2 identifier", "kdf", b"PBKDF2", "medium",
     "Password-derived key. If the password is in the note, recovery may be possible."),

    # --- Asymmetric --------------------------------------------------------
    ("RSA public exponent 65537", "asymmetric",
     bytes.fromhex("010001"), "low",
     "Three bytes, extremely common by chance. Corroborate before reporting."),
    ("secp256k1 generator Gx", "asymmetric",
     bytes.fromhex("79be667ef9dcbbac55a06295ce870b07"), "high",
     "Bitcoin curve. Sometimes reused for key exchange."),
    ("NIST P-256 prime", "asymmetric",
     bytes.fromhex("ffffffff00000001000000000000000000000000ffffffff"), "high",
     "secp256r1 / prime256v1."),
    ("Curve25519 a24 constant", "asymmetric",
     bytes.fromhex("41db0100"), "medium",
     "121665. X25519 key agreement, used by many modern families."),
    ("Ed25519 / X25519 string", "asymmetric", b"25519", "medium", "Library reference."),
    ("DER rsaEncryption OID", "asymmetric",
     bytes.fromhex("2a864886f70d010101"), "high",
     "1.2.840.113549.1.1.1. An embedded RSA key structure."),
    ("DER id-ecPublicKey OID", "asymmetric",
     bytes.fromhex("2a8648ce3d0201"), "high", "1.2.840.10045.2.1."),
    ("PEM public key header", "asymmetric",
     b"-----BEGIN PUBLIC KEY-----", "high",
     "Embedded attacker public key. Extract it - it is a campaign identifier."),
    ("PEM RSA public key header", "asymmetric",
     b"-----BEGIN RSA PUBLIC KEY-----", "high", "PKCS#1 form."),
    ("CNG BCRYPT_RSAPUBLIC_MAGIC", "asymmetric", b"RSA1", "medium",
     "Also the CAPI PUBLICKEYBLOB magic."),
    ("CNG BCRYPT_RSAPRIVATE_MAGIC", "asymmetric", b"RSA2", "medium", ""),
    ("CNG BCRYPT_ECDH_P256_MAGIC", "asymmetric", b"ECK1", "medium", ""),
    ("CNG key data blob magic", "asymmetric", b"KDBM", "medium",
     "Exported symmetric key blob."),

    # --- Windows crypto API surface ---------------------------------------
    ("CNG BCryptGenerateSymmetricKey", "winapi", b"BCryptGenerateSymmetricKey", "high",
     "pbSecret parameter holds the PLAINTEXT key. Prime breakpoint."),
    ("CNG BCryptEncrypt", "winapi", b"BCryptEncrypt", "high", ""),
    ("CNG BCryptImportKeyPair", "winapi", b"BCryptImportKeyPair", "high",
     "Loads the attacker public key."),
    ("CNG BCryptGenRandom", "winapi", b"BCryptGenRandom", "medium", "CSPRNG key source."),
    ("CNG BCryptExportKey", "winapi", b"BCryptExportKey", "medium", ""),
    ("CAPI CryptAcquireContext", "winapi", b"CryptAcquireContext", "high", "Legacy CAPI."),
    ("CAPI CryptExportKey", "winapi", b"CryptExportKey", "high",
     "With a public key handle this call IS the hybrid key wrap."),
    ("CAPI CryptEncrypt", "winapi", b"CryptEncrypt", "high", ""),
    ("CAPI CryptGenKey", "winapi", b"CryptGenKey", "medium", ""),
    ("MS_ENH_RSA_AES_PROV", "winapi", b"Microsoft Enhanced RSA and AES", "high",
     "The CSP used for hybrid AES+RSA under CAPI. WannaCry-era marker."),
    ("CNG chaining mode (wide)", "winapi",
     "ChainingMode".encode("utf-16-le"), "high", "Reveals CBC vs GCM vs CTR."),

    # --- Platform / living-off-the-land -----------------------------------
    ("BitLocker FVE signature", "container", b"-FVE-FS-", "high",
     "BitLocker volume metadata. Present on any BitLocker-encrypted volume."),
    ("BitLocker manage-bde", "lotl", b"manage-bde", "high",
     "BitLocker CLI. In a ransomware context this is the encryptor itself."),
    ("BitLocker PowerShell cmdlet", "lotl", b"Enable-BitLocker", "high",
     "Native encryption via PowerShell."),
    ("BitLocker protector removal", "lotl", b"Remove-BitLockerKeyProtector", "high",
     "Destroys recovery paths. Strongly hostile in context."),
    ("Win32_EncryptableVolume", "lotl", b"Win32_EncryptableVolume", "high",
     "WMI BitLocker control class. ShrinkLocker's primary interface."),
    ("EFS cipher.exe", "lotl", b"cipher.exe", "medium",
     "Encrypting File System CLI. /W also wipes free space."),
    ("LUKS header magic", "container", b"LUKS\xba\xbe", "high",
     "Linux dm-crypt. Relevant for ESXi and NAS targets."),
    ("VeraCrypt/TrueCrypt header", "container", b"VERA", "medium",
     "Legitimate FDE tool sometimes deployed as an encryptor."),
    ("DiskCryptor reference", "lotl", b"dcrypt", "medium",
     "Open-source FDE abused by several groups."),
    ("7-Zip AES marker", "container", b"7z\xbc\xaf\x27\x1c", "medium",
     "Archive with optional AES-256. Used for exfil and for crude encryption."),
    ("RAR5 signature", "container", b"Rar!\x1a\x07\x01\x00", "medium", ""),

    # --- Build toolchain (context, not crypto) ---
    ("Go build ID", "toolchain", b"Go build ID:", "high",
     "Go binary. Statically linked - expect NO crypto imports. Constant-scan instead."),
    ("Go runtime", "toolchain", b"runtime.gcbits", "medium", "Go runtime present."),
    ("Garble obfuscation", "toolchain", b"garble", "medium",
     "Go obfuscator. Strips package paths and mangles names. Used by The Gentlemen."),
    ("Rust panic machinery", "toolchain", b"called `Option::unwrap()`", "high",
     "Rust binary. Statically linked. Consider Microsoft's RIFT for triage."),
    ("Rust core library path", "toolchain", b"/rustc/", "medium", "Rust build path."),

    # --- Known family footer markers ---
    ("Text footer delimiter '--marker--'", "family", b"--marker--", "medium",
     "ASCII footer delimiter. Used by The Gentlemen, but NOT exclusive to it - "
     "delimiters are copied between families. Confirm before attributing."),
    ("Text footer delimiter '--eph--'", "family", b"--eph--", "medium",
     "Precedes a base64 ephemeral public key. Indicates per-file ECDH key storage."),
    ("Gentlemen family tag", "family", b"GENTLEMEN", "high",
     "Explicit family name in footer / note (README-GENTLEMEN.txt). Stronger than a delimiter."),

    # --- Encoding ----------------------------------------------------------
    ("Base64 alphabet", "encoding",
     b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/", "medium",
     "Encoding, NOT encryption. Common for key blobs and C2."),
    ("Base64 URL-safe alphabet", "encoding",
     b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_", "medium", ""),
]

CATEGORY_ORDER = ["symmetric", "aead", "asymmetric", "hash", "kdf",
                  "winapi", "lotl", "container", "family", "toolchain", "encoding"]

CATEGORY_LABEL = {
    "symmetric": "SYMMETRIC CIPHERS      (bulk file encryption)",
    "aead":      "AUTHENTICATED MODES    (encryption + integrity)",
    "asymmetric": "ASYMMETRIC / KEY WRAP  (why you cannot decrypt)",
    "hash":      "HASHES                 (integrity, IDs, KDF internals)",
    "kdf":       "KEY DERIVATION         (possible recovery path)",
    "winapi":    "WINDOWS CRYPTO API     (call surface)",
    "lotl":      "LIVING OFF THE LAND    (OS-native encryption abuse)",
    "container": "CONTAINER / VOLUME     (full-disk and archive formats)",
    "family":    "KNOWN FAMILY MARKERS   (footer tags, note names)",
    "toolchain": "BUILD TOOLCHAIN        (drives your analysis strategy)",
    "encoding":  "ENCODING               (not encryption)",
}

CONF_RANK = {"low": 0, "medium": 1, "high": 2}


def scan(data: bytes, min_conf: str, categories: list) -> list:
    out = []
    floor = CONF_RANK[min_conf]
    for name, cat, pat, conf, note in SIGS:
        if CONF_RANK[conf] < floor:
            continue
        if categories and cat not in categories:
            continue
        offsets, start = [], 0
        while len(offsets) < 6:
            i = data.find(pat, start)
            if i == -1:
                break
            offsets.append(i)
            start = i + 1
        if offsets:
            out.append({"name": name, "category": cat, "confidence": conf,
                        "note": note, "hits": len(offsets), "offsets": offsets})
    return out


def interpret(found: list, min_conf: str = "low") -> list:
    """Turn raw hits into the conclusions an analyst actually needs."""
    names = {f["name"] for f in found}
    cats = {f["category"] for f in found}
    notes = []

    sym = any(n.startswith(("AES", "ChaCha", "XChaCha", "Blowfish", "Twofish", "RC5", "TEA"))
              for n in names)
    asym_hits = [f for f in found if f["category"] == "asymmetric"]
    asym = any(f["confidence"] == "high" for f in asym_hits)
    asym_weak = bool(asym_hits) and not asym

    if sym and asym_weak:
        # Medium-confidence asymmetric evidence is still evidence. Reporting
        # "no asymmetric material" here would be flatly false and would point a
        # responder toward a decryptor that cannot exist.
        found_names = ", ".join(f["name"] for f in asym_hits[:3])
        notes.append(
            f"POSSIBLE HYBRID SCHEME. A bulk cipher is present alongside "
            f"medium/low confidence asymmetric markers ({found_names}). That is "
            "consistent with an asymmetric key wrap, which would mean no "
            "cryptographic recovery path. CONFIRM IN A DISASSEMBLER before giving "
            "any recoverability verdict either way.")

    if sym and asym:
        notes.append(
            "HYBRID SCHEME LIKELY. Both a bulk cipher and asymmetric key material are "
            "present. This is the standard ransomware construction: files encrypted "
            "symmetrically, the symmetric key wrapped asymmetrically. See Module 02.")
    elif sym and not asym and not asym_weak:
        if min_conf != "low":
            # Concluding "no asymmetric material" while a confidence filter is
            # active means concluding from evidence the user hid. Asymmetric
            # markers such as the Curve25519 a24 constant are medium confidence,
            # so --min-confidence high suppresses exactly what this claim needs.
            notes.append(
                f"INCONCLUSIVE ON KEY WRAPPING. A bulk cipher is present, but this scan "
                f"ran with --min-confidence {min_conf}, which suppresses medium and low "
                "confidence asymmetric markers (Curve25519, ECC curve constants). "
                "RE-RUN WITH --min-confidence low BEFORE CONCLUDING ANYTHING ABOUT "
                "RECOVERABILITY.")
        else:
            notes.append(
                "SYMMETRIC ONLY, no asymmetric material found at any confidence level. "
                "If that survives manual review, the key may be embedded, derived, or "
                "recoverable - a decryptor becomes plausible. Verify before promising "
                "anything.")

    if "AES inverse S-box" in names:
        notes.append(
            "Inverse S-box present: decryption is implemented in this binary. Common "
            "when the sample doubles as the operator's decryptor.")
    elif "AES S-box" in names and "AES inverse S-box" not in names:
        notes.append(
            "Forward AES S-box only, no inverse table. Consistent with an "
            "encrypt-only build, which is what a deployed encryptor looks like.")

    if "lotl" in cats:
        notes.append(
            "LIVING-OFF-THE-LAND ENCRYPTION INDICATORS. The host OS may be doing the "
            "encrypting. Pivot to command-line, WMI, and event-log evidence - there "
            "may be no crypto implementation to reverse at all. See Module 04.")

    if "BitLocker FVE signature" in names:
        notes.append(
            "BitLocker volume metadata found. CHECK KEY ESCROW FIRST (AD "
            "msFVE-RecoveryInformation, Entra ID, MBAM). Recovery may be immediate.")

    if any(f["category"] == "kdf" for f in found):
        notes.append(
            "Key-derivation function present. If the key derives from a password or a "
            "predictable seed rather than a CSPRNG, that is a recovery avenue. "
            "Weak-seed bugs are how most public decryptors get built.")

    if any(f["category"] == "toolchain" for f in found):
        tn = {f["name"] for f in found if f["category"] == "toolchain"}
        if any("Go" in x or "Garble" in x for x in tn) or any("Rust" in x for x in tn):
            notes.append(
                "STATICALLY LINKED BINARY (Go or Rust). There will be no useful import "
                "table and the crypto library is compiled in, so expect constant hits for "
                "algorithms the malware never calls. Confirm which are reachable from the "
                "encryption routine before drawing conclusions.")

    if any(f["category"] == "family" for f in found):
        notes.append(
            "KNOWN FAMILY MARKER PRESENT. Check for published analysis and an existing "
            "decryptor before any recovery work. See references/PRIMARY_SOURCES.md.")

    if not found:
        notes.append(
            "No known constants found. Consider: packed or encrypted binary (unpack "
            "first), hardware AES-NI with no tables, a custom or XOR-based scheme, or "
            "OS-delegated encryption. Absence of evidence is not evidence of absence.")

    return notes


def main() -> int:
    ap = argparse.ArgumentParser(description="Identify crypto algorithms by constants.")
    ap.add_argument("target")
    ap.add_argument("--min-confidence", choices=["low", "medium", "high"], default="low")
    ap.add_argument("--categories", nargs="*", default=[],
                    help=f"filter: {' '.join(CATEGORY_ORDER)}")
    ap.add_argument("--max-bytes", type=int, default=256 * 1024 * 1024)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not os.path.isfile(args.target):
        print(f"error: not a file: {args.target}", file=sys.stderr)
        return 2

    with open(args.target, "rb") as fh:
        data = fh.read(args.max_bytes)

    found = scan(data, args.min_confidence, args.categories)
    notes = interpret(found, args.min_confidence)

    if args.json:
        print(json.dumps({"target": args.target, "size": len(data),
                          "findings": found, "assessment": notes}, indent=2))
        return 0

    print("=" * 74)
    print(f"  CRYPTO IDENTIFICATION - {args.target}")
    print(f"  {len(data):,} bytes scanned | {len(found)} signature(s) matched")
    print("=" * 74)

    for cat in CATEGORY_ORDER:
        rows = [f for f in found if f["category"] == cat]
        if not rows:
            continue
        print(f"\n{CATEGORY_LABEL[cat]}")
        for f in sorted(rows, key=lambda r: -CONF_RANK[r["confidence"]]):
            tag = {"high": "[HIGH]  ", "medium": "[MEDIUM]", "low": "[LOW]   "}[f["confidence"]]
            locs = ", ".join(f"0x{o:x}" for o in f["offsets"][:3])
            more = f" (+{f['hits'] - 3} more)" if f["hits"] > 3 else ""
            print(f"  {tag} {f['name']}")
            print(f"           at {locs}{more}")
            if f["note"]:
                print(f"           {f['note']}")

    print("\n" + "=" * 74)
    print("  ASSESSMENT")
    print("=" * 74)
    for n in notes:
        print(f"\n  * {n}")
    print("\n  Constants prove PRESENCE, not USE. Statically linked runtimes carry")
    print("  crypto the malware never calls. Confirm in a disassembler.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
