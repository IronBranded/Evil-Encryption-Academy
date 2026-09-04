/*
   ChaCha20 / Salsa20 / XChaCha20 constants.

   The sigma constant is one of the strongest single indicators available: it is
   required by the algorithm, it is ASCII, and it survives everything short of
   packing. Modern Rust and Go ransomware overwhelmingly uses this family.

   IMPORTANT: these rules CANNOT distinguish ChaCha20 from XChaCha20. Both use
   the identical sigma constant; only the nonce size differs (24 bytes for
   XChaCha20, 12 or 8 for ChaCha20). Determine that in a disassembler.

   Reference: references/CIPHER-IDENTIFICATION.md
*/

rule ChaCha_Salsa_Sigma
{
    meta:
        description = "ChaCha20/Salsa20/XChaCha20 sigma constant, 256-bit key"
        reference   = "01-Symmetric-Cryptography"
        confidence  = "high"
    strings:
        $sigma_str = "expand 32-byte k" ascii
        $sigma_dw  = { 61 70 78 65 33 20 64 6E 79 62 2D 32 6B 20 65 74 }
        $tau       = "expand 16-byte k" ascii
    condition:
        any of them
}

rule Poly1305_AEAD
{
    meta:
        description = "Poly1305 clamp constant. Indicates an AEAD construction."
        note        = "With sigma: ChaCha20-Poly1305. NaCl crypto_box uses XSalsa20-Poly1305."
        reference   = "01-Symmetric-Cryptography"
        confidence  = "high"
    strings:
        $clamp = { FF FF FF 0F FC FF FF 0F FC FF FF 0F FC FF FF 0F }
    condition:
        $clamp
}

rule ChaCha_With_Curve25519
{
    meta:
        description = "Stream cipher plus Curve25519 - the modern per-file ephemeral ECDH pattern"
        note        = "Seen in The Gentlemen and DeadLock. Implies no cryptographic recovery path."
        reference   = "06-Case-Studies"
        confidence  = "medium"
    strings:
        $sigma = "expand 32-byte k" ascii
        $a24   = { 41 DB 01 00 }
        $x255  = "25519" ascii
    condition:
        $sigma and ($a24 or $x255)
}
