#!/usr/bin/env python3
"""
parse_footer.py - Encrypted-file triage for ransomware incident response.

PURPOSE
    Given a file you believe was encrypted by ransomware, answer three questions
    without ever needing the sample that encrypted it:

        1. Is this actually encrypted, or just compressed / packed / random-looking?
        2. Was it FULLY encrypted, or INTERMITTENTLY encrypted (leaving recoverable
           plaintext), or HEADER-ONLY?
        3. Is there a wrapped-key blob appended to it, and how big is the asymmetric
           key that wrapped it?

    Question 2 decides whether partial file recovery is on the table.
    Question 3 tells you which asymmetric algorithm you are up against, which
    feeds directly into the recoverability verdict in Module 09.

WHAT THIS TOOL DOES NOT DO
    It does not decrypt anything and it cannot. Recovering the plaintext requires
    the symmetric key, which comes from memory forensics (Module 06), a flawed
    key-derivation scheme, or a published decryptor. This tool tells you what you
    are looking at so you know which of those to pursue.

USAGE
    python3 parse_footer.py <file>
    python3 parse_footer.py <directory> --recurse --limit 50
    python3 parse_footer.py <file> --json
    python3 parse_footer.py <file> --block 1024        # finer entropy resolution

    Stdlib only. Python 3.8+. Read-only; never writes to the target.

Part of Evil-Encryption-Academy, Module 02: The Hybrid Encryption Model.
MIT licensed.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import sys
from collections import Counter

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

BLOCK_DEFAULT = 4096          # entropy window, bytes
TAIL_SCAN = 4096              # how much of the tail to string-scan
HIGH_ENTROPY = 0.94           # normalized: block looks like ciphertext
LOW_ENTROPY = 0.80            # normalized: block looks like structured data
MIN_STRING = 5                # printable-run length for string extraction

# Trailing blob sizes that correspond to a raw asymmetric ciphertext.
# An RSA ciphertext is always exactly the modulus size.
RSA_TAIL_SIZES = {
    128: "RSA-1024 wrapped key",
    256: "RSA-2048 wrapped key",
    384: "RSA-3072 wrapped key",
    512: "RSA-4096 wrapped key",
}

# ECC schemes append an ephemeral public key, not a ciphertext.
ECC_TAIL_SIZES = {
    32: "X25519 / Curve25519 ephemeral public key",
    33: "SEC1 compressed P-256 point",
    64: "raw uncompressed P-256 coordinates",
    65: "SEC1 uncompressed P-256 point (0x04 prefix)",
}

# Structure magics worth finding anywhere in the file.
MAGICS = [
    (b"RSA1", "CNG BCRYPT_RSAPUBLIC_MAGIC / CAPI PUBLICKEYBLOB"),
    (b"RSA2", "CNG BCRYPT_RSAPRIVATE_MAGIC / CAPI PRIVATEKEYBLOB"),
    (b"RSA3", "CNG BCRYPT_RSAFULLPRIVATE_MAGIC"),
    (b"ECK1", "CNG BCRYPT_ECDH_PUBLIC_P256_MAGIC"),
    (b"ECK3", "CNG BCRYPT_ECDH_PUBLIC_P384_MAGIC"),
    (b"ECS1", "CNG BCRYPT_ECDSA_PUBLIC_P256_MAGIC"),
    (b"KDBM", "CNG BCRYPT_KEY_DATA_BLOB_MAGIC (exported symmetric key)"),
    (b"-----BEGIN PUBLIC KEY-----", "PEM SubjectPublicKeyInfo"),
    (b"-----BEGIN RSA PUBLIC KEY-----", "PEM PKCS#1 RSA public key"),
    (b"\x2a\x86\x48\x86\xf7\x0d\x01\x01\x01", "DER rsaEncryption OID (1.2.840.113549.1.1.1)"),
    (b"\x06\x03\x2b\x65\x6e", "DER X25519 OID (1.3.101.110)"),
]

PRINTABLE = re.compile(rb"[\x20-\x7e]{%d,}" % MIN_STRING)

# ---------------------------------------------------------------------------
# File format signatures
#
# Entropy alone CANNOT distinguish ciphertext from compressed or media data.
# A JPEG scores ~7.9 and an MP4 ~8.0, identical to AES output. Judging on
# entropy alone flags every photo and video on a file server as encrypted and
# produces a wildly inflated blast radius in exactly the moment it matters.
#
# The real signal is FORMAT MISMATCH: a file whose extension claims JPEG but
# whose JFIF header is gone has had its header encrypted. An intact header on a
# high-entropy file usually means the file is just... a photo.
# (offset, magic, format name, inherently high entropy)
# ---------------------------------------------------------------------------
FILE_SIGNATURES = [
    (0, b"\xff\xd8\xff", "JPEG", True),
    (0, b"\x89PNG\r\n\x1a\n", "PNG", True),
    (0, b"GIF87a", "GIF", True), (0, b"GIF89a", "GIF", True),
    (4, b"ftyp", "MP4/MOV", True),
    (0, b"RIFF", "RIFF (AVI/WAV/WEBP)", True),
    (0, b"\x1aE\xdf\xa3", "Matroska (MKV/WEBM)", True),
    (0, b"PK\x03\x04", "ZIP/OOXML", True), (0, b"PK\x05\x06", "ZIP/OOXML", True),
    (0, b"7z\xbc\xaf\x27\x1c", "7-Zip", True),
    (0, b"Rar!\x1a\x07", "RAR", True),
    (0, b"\x1f\x8b", "GZIP", True), (0, b"BZh", "BZIP2", True),
    (0, b"\xfd7zXZ\x00", "XZ", True),
    (0, b"ID3", "MP3", True), (0, b"OggS", "OGG", True), (0, b"fLaC", "FLAC", True),
    (0, b"%PDF-", "PDF", False),
    (0, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "MS Compound (legacy Office)", False),
    (0, b"MZ", "PE executable", False), (0, b"\x7fELF", "ELF", False),
    (0, b"SQLite format 3\x00", "SQLite", False),
    (0, b"-FVE-FS-", "BitLocker volume", False),
    (0, b"LUKS\xba\xbe", "LUKS volume", False),
]

EXT_FORMATS = {
    "jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "gif": "GIF",
    "mp4": "MP4/MOV", "mov": "MP4/MOV", "m4a": "MP4/MOV",
    "avi": "RIFF (AVI/WAV/WEBP)", "wav": "RIFF (AVI/WAV/WEBP)", "webp": "RIFF (AVI/WAV/WEBP)",
    "mkv": "Matroska (MKV/WEBM)", "webm": "Matroska (MKV/WEBM)",
    "zip": "ZIP/OOXML", "docx": "ZIP/OOXML", "xlsx": "ZIP/OOXML", "pptx": "ZIP/OOXML",
    "7z": "7-Zip", "rar": "RAR", "gz": "GZIP", "bz2": "BZIP2", "xz": "XZ",
    "mp3": "MP3", "ogg": "OGG", "flac": "FLAC", "pdf": "PDF",
    "doc": "MS Compound (legacy Office)", "xls": "MS Compound (legacy Office)",
    "ppt": "MS Compound (legacy Office)", "msg": "MS Compound (legacy Office)",
    "exe": "PE executable", "dll": "PE executable",
    "db": "SQLite", "sqlite": "SQLite", "sqlite3": "SQLite",
}

# Text-encoded footers. Some families store the wrapped key or the ephemeral
# public key as BASE64 behind ASCII delimiters rather than as a raw binary blob.
# The Gentlemen ransomware (MSTIC, May 2026) is the reference case: its footer is
#   --eph--<base64 ephemeral Curve25519 public key>--marker--GENTLEMEN
# Entropy-based tail detection MISSES this completely. Base64 uses only 64 symbols,
# so it scores around 6.0 bits/byte and never trips a "looks random" threshold.
B64_RUN = re.compile(rb"[A-Za-z0-9+/]{20,}={0,2}")
DELIMITER = re.compile(rb"[-=|*#~]{2,}[A-Za-z0-9_]{2,24}[-=|*#~]{2,}")

# Decoded blob sizes -> what the key material probably is
DECODED_SIZES = {
    32: "X25519/Curve25519 public key or a raw 256-bit symmetric key",
    33: "SEC1 compressed P-256 point",
    64: "raw P-256 coordinates or a 512-bit blob",
    65: "SEC1 uncompressed P-256 point",
    128: "RSA-1024 ciphertext", 256: "RSA-2048 ciphertext",
    384: "RSA-3072 ciphertext", 512: "RSA-4096 ciphertext",
}


# ---------------------------------------------------------------------------
# Entropy
# ---------------------------------------------------------------------------

def shannon(data: bytes) -> float:
    """Shannon entropy in bits per byte, 0.0 to 8.0."""
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


# Measured mean Shannon entropy of uniform-random data, by sample size.
# Generated with 400 trials per size over os.urandom(); see docs/entropy-calibration.md.
#
# This table exists because raw entropy is routinely misread. A 128-byte buffer
# of perfect ciphertext scores about 6.55, not 8.0, and not even the log2(128)=7.0
# "ceiling" you would get by assuming all symbols distinct. 128 samples simply
# cannot populate 256 symbols; most are missing by the coupon-collector argument.
# Judging a 128-byte wrapped-key blob against 8.0, or against 7.0, makes genuine
# ciphertext look non-random and you throw away the finding.
#
# Normalizing against MEASURED random behaviour makes a score of ~1.0 mean
# "indistinguishable from random at this sample size", at every sample size.
_RANDOM_BASELINE = [
    (32, 4.880), (33, 4.929), (64, 5.765), (65, 5.783), (128, 6.550),
    (256, 7.177), (384, 7.444), (512, 7.592), (1024, 7.809), (2048, 7.909),
    (4096, 7.954), (8192, 7.977), (16384, 7.989),
]


def expected_random_entropy(n: int) -> float:
    """Interpolate the expected entropy of n uniform-random bytes."""
    if n <= 0:
        return 0.0
    if n <= _RANDOM_BASELINE[0][0]:
        return math.log2(min(n, 256))
    if n >= _RANDOM_BASELINE[-1][0]:
        return 8.0
    for (x0, y0), (x1, y1) in zip(_RANDOM_BASELINE, _RANDOM_BASELINE[1:]):
        if x0 <= n <= x1:
            # interpolate in log-space; entropy grows logarithmically with n
            t = (math.log2(n) - math.log2(x0)) / (math.log2(x1) - math.log2(x0))
            return y0 + t * (y1 - y0)
    return 8.0


def max_entropy(n: int) -> float:
    """Retained for reporting the raw ceiling alongside the calibrated baseline."""
    return math.log2(min(n, 256)) if n > 0 else 0.0


def normalized(data: bytes) -> float:
    """
    Entropy relative to what random data of THIS length actually scores.

    ~1.00 means indistinguishable from random. Values can slightly exceed 1.0
    on small samples, which is expected variance, not a red flag.
    """
    baseline = expected_random_entropy(len(data))
    if baseline == 0:
        return 0.0
    return shannon(data) / baseline


def block_profile(data: bytes, block: int) -> list:
    """Normalized entropy for each block-sized window."""
    return [normalized(data[i:i + block]) for i in range(0, len(data), block)]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def runs(profile: list) -> list:
    """Collapse a block profile into ('high'|'mid'|'low', count) runs."""
    def band(v):
        if v >= HIGH_ENTROPY:
            return "high"
        if v <= LOW_ENTROPY:
            return "low"
        return "mid"

    out = []
    for v in profile:
        b = band(v)
        if out and out[-1][0] == b:
            out[-1][1] += 1
        else:
            out.append([b, 1])
    return [tuple(r) for r in out]


def classify(profile: list) -> dict:
    """
    Decide between full, intermittent, header-only, and not-encrypted.

    The intermittent-encryption signature is the useful one. Families that
    encrypt in stripes to cut I/O time leave alternating high/low entropy
    bands across the file. Every low band is plaintext that survived, which
    is exactly what makes partial recovery possible.
    """
    if not profile:
        return {"verdict": "empty file", "confidence": "n/a", "detail": ""}

    r = runs(profile)
    n = len(profile)
    high_blocks = sum(1 for v in profile if v >= HIGH_ENTROPY)
    low_blocks = sum(1 for v in profile if v <= LOW_ENTROPY)
    high_ratio = high_blocks / n

    high_runs = [c for b, c in r if b == "high"]
    low_runs = [c for b, c in r if b == "low"]

    # Single block: not enough resolution to say anything structural.
    if n == 1:
        v = "encrypted or compressed" if profile[0] >= HIGH_ENTROPY else "not encrypted"
        return {"verdict": v, "confidence": "low", "detail": "file smaller than one entropy window"}

    if high_ratio >= 0.95:
        return {
            "verdict": "FULL ENCRYPTION",
            "confidence": "high",
            "detail": f"{high_blocks}/{n} blocks at ciphertext entropy",
        }

    # Three encrypted regions at head/middle/tail is a distinct, documented design:
    # encrypt a percentage at the start, the midpoint and the end, which corrupts
    # file structure at a fraction of the I/O cost. The Gentlemen (MSTIC, May 2026)
    # uses exactly three chunks, defaulting to 9% each and as little as 0.3% each.
    if len(high_runs) == 3 and len(low_runs) == 2 and n >= 9:
        head, tail_ = r[0][0] == "high", r[-1][0] == "high"
        if head and tail_:
            return {
                "verdict": "DISTRIBUTED-CHUNK PARTIAL ENCRYPTION (candidate)",
                "confidence": "medium",
                "detail": (f"encrypted at head, midpoint and tail; "
                           f"{low_blocks}/{n} blocks ({low_blocks / n:.0%}) look like "
                           f"surviving plaintext - strong partial-recovery candidate"),
            }

    if len(high_runs) >= 2 and len(low_runs) >= 1 and high_blocks >= 2 and low_blocks >= 2:
        return {
            "verdict": "INTERMITTENT ENCRYPTION (candidate)",
            "confidence": "medium",
            "detail": (
                f"{len(high_runs)} encrypted bands, {len(low_runs)} plaintext bands; "
                f"{low_blocks}/{n} blocks ({low_blocks / n:.0%}) may be recoverable plaintext"
            ),
        }

    if r[0][0] == "high" and high_ratio < 0.5 and low_blocks > high_blocks:
        return {
            "verdict": "HEADER-ONLY ENCRYPTION (candidate)",
            "confidence": "medium",
            "detail": f"first {r[0][1]} block(s) encrypted, remainder appears plaintext",
        }

    if high_ratio < 0.2:
        return {
            "verdict": "NOT ENCRYPTED",
            "confidence": "high",
            "detail": "entropy consistent with ordinary structured data",
        }

    return {
        "verdict": "INCONCLUSIVE",
        "confidence": "low",
        "detail": f"{high_ratio:.0%} of blocks at high entropy; inspect manually",
    }


# ---------------------------------------------------------------------------
# Footer analysis
# ---------------------------------------------------------------------------

def footer_candidates(data: bytes) -> list:
    """
    Test each plausible wrapped-key size against the file tail.

    Supporting signal: if the file is (body + footer) and the body was
    encrypted with a 16-byte block cipher, then (filesize - footer) should be
    a multiple of 16. That alignment check separates real candidates from
    coincidence surprisingly well.
    """
    out = []
    size = len(data)
    for cand, label in sorted({**RSA_TAIL_SIZES, **ECC_TAIL_SIZES}.items()):
        if size <= cand + 16:
            continue
        tail = data[-cand:]
        out.append({
            "size": cand,
            "meaning": label,
            "entropy": round(shannon(tail), 3),
            "entropy_max": round(max_entropy(cand), 3),
            "random_baseline": round(expected_random_entropy(cand), 3),
            "normalized": round(normalized(tail), 3),
            "block_aligned": (size - cand) % 16 == 0,
            "looks_random": normalized(tail) >= HIGH_ENTROPY,
        })
    return out


MICRO = 512


def micro_stripe_fraction(data: bytes, sample: int = 300) -> float:
    """
    Fraction of 512-byte windows that look like ciphertext.

    Fine-grained striping hides from coarse entropy windows by dilution.
    DeadLock (MSTIC, Aug 2026) encrypts 512-byte blocks at computed intervals;
    inside a 4096-byte window that reads as mostly plaintext and the file is
    reported clean while a tenth of it is destroyed.
    """
    n = len(data)
    if n < MICRO * 8:
        return 0.0
    step = max(MICRO, n // sample)
    hits = checked = 0
    for off in range(0, n - MICRO, step):
        checked += 1
        if normalized(data[off:off + MICRO]) >= HIGH_ENTROPY:
            hits += 1
    return hits / checked if checked else 0.0


def detect_format(data: bytes):
    """Identify the container format from its header magic."""
    for off, magic, name, hot in FILE_SIGNATURES:
        if data[off:off + len(magic)] == magic:
            return {"format": name, "high_entropy_format": hot}
    return None


def format_analysis(path: str, data: bytes) -> dict:
    """
    Reconcile what the file CLAIMS to be against what its header SAYS it is.

    Three outcomes that matter:
      intact  - header matches the extension. A high-entropy score here is
                almost certainly just compression, not encryption.
      mismatch- extension claims a known format but the header is gone. The
                header was encrypted. Strong ransomware signal.
      unknown - no known format either way. Fall through to entropy analysis.
    """
    name = os.path.basename(path)
    parts = name.split(".")
    claimed_ext = appended_ext = None
    if len(parts) >= 3:
        claimed_ext, appended_ext = parts[-2].lower(), parts[-1].lower()
    elif len(parts) == 2:
        claimed_ext = parts[-1].lower()

    claimed = EXT_FORMATS.get(claimed_ext or "")
    # A recognized format in the OUTER position means no ransom extension was appended
    if appended_ext and EXT_FORMATS.get(appended_ext):
        claimed, appended_ext = EXT_FORMATS[appended_ext], None

    det = detect_format(data)
    detected = det["format"] if det else None
    hot = det["high_entropy_format"] if det else False

    if detected and claimed and detected == claimed:
        state = "intact"
    elif detected and not claimed:
        state = "intact"
    elif claimed and detected != claimed:
        state = "mismatch"
    else:
        state = "unknown"

    return {"claimed_ext": claimed_ext, "claimed_format": claimed,
            "appended_ext": appended_ext, "detected_format": detected,
            "high_entropy_format": hot, "state": state}


def reconcile(verdict: dict, fmt: dict, has_markers: bool) -> dict:
    """
    Correct an entropy verdict using format evidence.

    This exists because the entropy classifier, on its own, calls every JPEG
    and MP4 on a file server FULL ENCRYPTION at high confidence.
    """
    v = dict(verdict)

    # An UNRECOGNIZED outer extension means something was appended to the real
    # name. That is a ransom-extension signal and it overrides the intact-header
    # correction, otherwise header-preserving intermittent encryption (which is
    # exactly what fast families do) would be dismissed as a benign media file.
    ransom_ext = bool(fmt["appended_ext"])

    if ransom_ext and "NOT ENCRYPTED" in v["verdict"].upper():
        v["verdict"] = "SUSPECTED ENCRYPTION - appended extension"
        v["confidence"] = "medium"
        v["detail"] = (f"header is an intact {fmt['detected_format'] or 'unknown format'}, "
                       f"but '.{fmt['appended_ext']}' was appended to the filename. "
                       "Consistent with header-preserving or intermittent encryption. "
                       "Compare against a known-good copy before concluding.")
        return v

    if fmt["state"] == "intact" and fmt["high_entropy_format"] and not has_markers and not ransom_ext:
        if "ENCRYPTION" in v["verdict"]:
            v["verdict"] = f"NOT ENCRYPTED - intact {fmt['detected_format']}"
            v["confidence"] = "high"
            v["detail"] = (f"high entropy is expected for {fmt['detected_format']}; "
                           "header is present and matches the extension")
            v["corrected"] = True
        return v

    if fmt["state"] == "mismatch" and "ENCRYPT" in v["verdict"].upper():
        v["detail"] += (f" | FORMAT MISMATCH: extension claims "
                        f"{fmt['claimed_format']} but that header is absent - "
                        "consistent with an encrypted header")
        v["confidence"] = "high"

    if fmt["appended_ext"] and fmt["claimed_format"]:
        v["detail"] += (f" | appended extension '.{fmt['appended_ext']}' over a "
                        f"{fmt['claimed_format']} file")
    return v


def text_footer(data: bytes, window: int = TAIL_SCAN) -> dict:
    """
    Look for a TEXT-encoded footer: ASCII delimiters and base64 key blobs.

    This is the blind spot in pure entropy triage. A base64-encoded key sits at
    roughly 6.0 bits/byte, well under any ciphertext threshold, so a footer that
    is plainly visible as text will never appear in the entropy-based candidates.
    """
    tail = data[-window:] if len(data) > window else data
    base = len(data) - len(tail)

    delims = [{"text": m.group().decode("ascii", "replace"),
               "from_eof": len(data) - (base + m.start())}
              for m in DELIMITER.finditer(tail)]

    blobs = []
    for m in B64_RUN.finditer(tail):
        raw = m.group()
        try:
            dec = base64.b64decode(raw + b"=" * (-len(raw) % 4), validate=True)
        except Exception:
            continue
        if len(dec) < 16:
            continue
        blobs.append({
            "b64_len": len(raw),
            "decoded_len": len(dec),
            "from_eof": len(data) - (base + m.start()),
            "meaning": DECODED_SIZES.get(len(dec), f"{len(dec)}-byte blob (unrecognized size)"),
            "preview": raw[:32].decode("ascii", "replace"),
        })
    return {"delimiters": delims, "b64_blobs": blobs}


def find_magics(data: bytes) -> list:
    hits = []
    for needle, meaning in MAGICS:
        start = 0
        while True:
            idx = data.find(needle, start)
            if idx == -1:
                break
            hits.append({
                "offset": idx,
                "from_eof": len(data) - idx,
                "magic": needle.decode("latin-1", "replace")[:32],
                "meaning": meaning,
            })
            start = idx + 1
            if len(hits) > 40:
                return hits
    return hits


def tail_strings(data: bytes, window: int = TAIL_SCAN) -> list:
    """
    Printable runs near EOF. Families frequently leave a sentinel marker,
    a campaign ID, a victim ID, or a base64 blob in the footer. These are
    high-value attribution artifacts.
    """
    tail = data[-window:] if len(data) > window else data
    base = len(data) - len(tail)
    hits = [
        {"from_eof": len(data) - (base + m.start()),
         "text": m.group().decode("ascii", "replace")[:120]}
        for m in PRINTABLE.finditer(tail)
    ]
    # Nearest EOF first. Footer markers live at the very end, and file-order
    # sorting pushes them past any display limit behind random printable runs.
    return sorted(hits, key=lambda h: h["from_eof"])


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def size_delta(encrypted_size: int, original_path: str) -> dict:
    """
    Compare against a known-good copy of the same file.

    This is the one measurement that settles footer size beyond argument.
    In a real incident you almost always have a comparison candidate: a backup
    copy, the same file on an unencrypted host, or a default OS/application
    file that exists identically everywhere.
    """
    original_size = os.path.getsize(original_path)
    overhead = encrypted_size - original_size
    exact = None
    for cand, label in sorted(RSA_TAIL_SIZES.items()):
        if overhead == cand:
            exact = label
    for cand, label in sorted(ECC_TAIL_SIZES.items()):
        if overhead == cand:
            exact = label
    return {
        "original_path": original_path,
        "original_size": original_size,
        "overhead": overhead,
        "exact_match": exact,
    }


def analyze(path: str, block: int, original: str = None) -> dict:
    with open(path, "rb") as fh:
        data = fh.read()

    profile = block_profile(data, block)
    fmt = format_analysis(path, data)
    tf = text_footer(data)
    mg = find_magics(data)
    # Only STRONG marker evidence may override the format correction.
    #
    # A 4-byte magic occurs by chance roughly once per 4 GB of random data, so on
    # any large high-entropy file (video, archive, disk image) short magics WILL
    # hit eventually. Letting them veto the format verdict re-introduces exactly
    # the media false positive the format check exists to prevent.
    #
    # Strong = a text-encoded footer, or a long magic (PEM/DER structures), or a
    # magic sitting in the tail where real key material lives.
    strong_magics = [m for m in mg
                     if len(m["magic"]) >= 8 or m["from_eof"] <= TAIL_SCAN]
    has_markers = bool(tf["delimiters"] or tf["b64_blobs"] or strong_magics)
    verdict = reconcile(classify(profile), fmt, has_markers)

    # Multi-scale verification: never report "not encrypted" on the coarse pass
    # alone without checking for narrow stripes underneath it.
    micro = 0.0
    if "NOT ENCRYPTED" in verdict["verdict"].upper() or verdict["verdict"] == "INCONCLUSIVE":
        micro = micro_stripe_fraction(data)
        if micro >= 0.02 and not (fmt["state"] == "intact" and fmt["high_entropy_format"]):
            verdict = {
                "verdict": "FINE-GRAINED INTERMITTENT ENCRYPTION (candidate)",
                "confidence": "medium",
                "detail": (f"{micro:.1%} of {MICRO}-byte windows are at ciphertext entropy "
                           "while 4096-byte windows are not - consistent with narrow "
                           "stripes spread through the file. Coarse entropy triage misses "
                           "this. Confirm with recover_partial.py"),
            }
    result = {
        "path": path,
        "size": len(data),
        "overall_entropy": round(shannon(data), 3),
        "overall_normalized": round(normalized(data), 3),
        "block_size": block,
        "block_count": len(profile),
        "classification": verdict,
        "format": fmt,
        "micro_stripe_fraction": round(micro, 4),
        "footer_candidates": footer_candidates(data),
        "magics": mg,
        "text_footer": tf,
        "tail_strings": tail_strings(data),
        "profile_preview": [round(v, 3) for v in profile[:64]],
        "delta": size_delta(len(data), original) if original else None,
    }
    return result


def sparkline(profile: list) -> str:
    bars = "▁▂▃▄▅▆▇█"
    if not profile:
        return ""
    return "".join(bars[min(int(v * len(bars)), len(bars) - 1)] for v in profile[:120])


def report(r: dict, block: int) -> None:
    print("=" * 72)
    print(f"FILE     {r['path']}")
    print(f"SIZE     {r['size']:,} bytes")
    print(f"ENTROPY  {r['overall_entropy']:.3f} / 8.000   "
          f"(normalized {r['overall_normalized']:.3f})")
    print("-" * 72)

    f = r.get("format", {})
    if f.get("detected_format") or f.get("claimed_format"):
        det = f.get("detected_format") or "none recognized"
        cl = f.get("claimed_format") or "unknown"
        flag = {"intact": "header matches extension",
                "mismatch": "** MISMATCH - header absent **",
                "unknown": "no known format"}[f["state"]]
        print(f"FORMAT   header: {det}  |  extension implies: {cl}  ->  {flag}")

    c = r["classification"]
    print(f"VERDICT  {c['verdict']}   [confidence: {c['confidence']}]")
    if c.get("corrected"):
        print("         (entropy verdict CORRECTED by format evidence)")
    if c["detail"]:
        print(f"         {c['detail']}")

    with open(r["path"], "rb") as fh:
        prof = block_profile(fh.read(), block)
    if len(prof) > 1:
        print(f"\nENTROPY PROFILE ({block}-byte blocks, first {min(len(prof),120)} shown)")
        print(f"  {sparkline(prof)}")
        print("  low ▁▁▁ plaintext / structured      high ███ ciphertext")

    strong = [f for f in r["footer_candidates"] if f["looks_random"] and f["block_aligned"]]
    weak = [f for f in r["footer_candidates"] if f["looks_random"] and not f["block_aligned"]]

    print("\nFOOTER BLOB CANDIDATES")
    if strong:
        for f in strong:
            print(f"  [STRONG] last {f['size']:>3} bytes  norm-entropy {f['normalized']:.3f}  "
                  f"body 16-byte aligned")
            print(f"           -> {f['meaning']}")
    if weak:
        for f in weak:
            print(f"  [weak]   last {f['size']:>3} bytes  norm-entropy {f['normalized']:.3f}  "
                  f"body NOT 16-byte aligned -> {f['meaning']}")
    if not strong and not weak:
        print("  none - no high-entropy fixed-size tail matching a known key size")

    if r["magics"]:
        print("\nKEY STRUCTURE MAGICS")
        for m in r["magics"][:15]:
            print(f"  offset 0x{m['offset']:08x}  ({m['from_eof']:,} from EOF)  "
                  f"{m['magic']!r}")
            print(f"      -> {m['meaning']}")

    if strong:
        print("\n  NOTE: every suffix of a random footer also looks random, so smaller")
        print("        sizes will always co-flag. The largest STRONG candidate is the")
        print("        usual answer. To settle it definitively, use --original against")
        print("        a known-good copy of the same file from backup or another host.")

    if r.get("delta") is not None:
        d = r["delta"]
        print("\nSIZE DELTA vs ORIGINAL  (definitive footer sizing)")
        print(f"  original   {d['original_size']:,} bytes")
        print(f"  encrypted  {r['size']:,} bytes")
        print(f"  overhead   {d['overhead']:,} bytes")
        if d["exact_match"]:
            print(f"  -> matches {d['exact_match']}")
        else:
            print(f"  -> overhead = cipher padding + IV/nonce + wrapped key + metadata")
            for cand, label in sorted(RSA_TAIL_SIZES.items()):
                if d["overhead"] >= cand:
                    print(f"     if {label}: {d['overhead'] - cand:,} bytes of other overhead")

    tf = r.get("text_footer") or {}
    if tf.get("delimiters") or tf.get("b64_blobs"):
        print("\nTEXT-ENCODED FOOTER  <-- entropy triage cannot see this")
        for d in tf.get("delimiters", [])[:6]:
            print(f"  delimiter {d['text']!r} at -{d['from_eof']:,} from EOF")
        for b in tf.get("b64_blobs", [])[:6]:
            print(f"  base64 blob: {b['b64_len']} chars -> {b['decoded_len']} bytes "
                  f"at -{b['from_eof']:,} from EOF")
            print(f"      {b['preview']}...")
            print(f"      -> {b['meaning']}")
        print("  A base64 key blob scores ~6.0 bits/byte and never trips a")
        print("  ciphertext threshold. Always string-scan the tail as well.")

    if r["tail_strings"]:
        print("\nSTRINGS NEAR EOF (possible marker / victim ID / campaign ID)")
        for s in r["tail_strings"][:12]:
            print(f"  -{s['from_eof']:,} from EOF: {s['text']!r}")

    print("=" * 72)
    print()


def walk(root: str, recurse: bool, limit: int):
    if os.path.isfile(root):
        yield root
        return
    count = 0
    for dirpath, _, files in os.walk(root):
        for name in sorted(files):
            yield os.path.join(dirpath, name)
            count += 1
            if count >= limit:
                return
        if not recurse:
            return


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Triage a suspected ransomware-encrypted file.",
        epilog="Read-only. Does not decrypt and cannot. See Module 02 README.",
    )
    ap.add_argument("target", help="file or directory")
    ap.add_argument("--block", type=int, default=BLOCK_DEFAULT,
                    help=f"entropy window in bytes (default {BLOCK_DEFAULT})")
    ap.add_argument("--recurse", action="store_true", help="walk subdirectories")
    ap.add_argument("--limit", type=int, default=25, help="max files in directory mode")
    ap.add_argument("--original", metavar="PATH",
                    help="known-good copy of the same file, for definitive footer sizing")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not os.path.exists(args.target):
        print(f"error: no such path: {args.target}", file=sys.stderr)
        return 2
    if args.block < 64:
        print("error: --block below 64 gives meaningless entropy", file=sys.stderr)
        return 2

    results = []
    for path in walk(args.target, args.recurse, args.limit):
        try:
            r = analyze(path, args.block, args.original)
        except (OSError, PermissionError) as e:
            print(f"skip {path}: {e}", file=sys.stderr)
            continue
        results.append(r)
        if not args.json:
            report(r, args.block)

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
