/*
   AES implementation constants.

   These tables are mathematically required by any software AES, so they survive
   stripping, static linking and symbol obfuscation. They are the primary route
   when a Go or Rust binary offers no import table.

   TRIAGE AID, NOT A VERDICT. Any binary bundling a crypto library will match.
   Constants prove PRESENCE, not USE.

   Blind spot: an AES-NI implementation has NO lookup tables. It will not match
   any rule here. Search for AESENC / AESKEYGENASSIST instructions instead.

   Reference: references/CIPHER-IDENTIFICATION.md
*/

rule AES_SBox_Forward
{
    meta:
        description = "AES forward S-box. Present in nearly every software AES."
        reference   = "01-Symmetric-Cryptography"
        confidence  = "high"
    strings:
        $sbox = { 63 7C 77 7B F2 6B 6F C5 30 01 67 2B FE D7 AB 76 }
    condition:
        $sbox
}

rule AES_SBox_Inverse
{
    meta:
        description = "AES inverse S-box. Its presence means DECRYPTION is implemented."
        note        = "An encrypt-only deployed encryptor often ships without this."
        reference   = "01-Symmetric-Cryptography"
        confidence  = "high"
    strings:
        $rsbox = { 52 09 6A D5 30 36 A5 38 BF 40 A3 9E 81 F3 D7 FB }
    condition:
        $rsbox
}

rule AES_TTables
{
    meta:
        description = "T-table AES (OpenSSL style). Speed-optimized implementation."
        reference   = "01-Symmetric-Cryptography"
        confidence  = "high"
    strings:
        $te0 = { A5 63 63 C6 84 7C 7C F8 99 77 77 EE 8D 7B 7B F6 }
    condition:
        $te0
}

rule AES_Encrypt_Only_Build
{
    meta:
        description = "Forward AES tables with no inverse table - consistent with an encrypt-only build"
        note        = "Weak signal alone. Useful for prioritising a triage queue."
        reference   = "01-Symmetric-Cryptography"
        confidence  = "low"
    strings:
        $fwd  = { 63 7C 77 7B F2 6B 6F C5 30 01 67 2B FE D7 AB 76 }
        $inv  = { 52 09 6A D5 30 36 A5 38 BF 40 A3 9E 81 F3 D7 FB }
    condition:
        $fwd and not $inv
}
