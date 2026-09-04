/*
   Hybrid encryption call profile and embedded public key material.

   TRIAGE AIDS, NOT VERDICTS. Chrome, Office and every VPN client will match the
   first rule. Use them to prioritise a queue, never to convict a binary.

   Reference: 02-Hybrid-Encryption-Model/README.md
*/

rule Hybrid_Crypto_CNG_Profile
{
    meta:
        description = "PE importing the CNG call set typical of a hybrid encryption scheme"
        reference   = "02-Hybrid-Encryption-Model"
        confidence  = "low"
    strings:
        $sym1 = "BCryptGenerateSymmetricKey" ascii
        $sym2 = "BCryptGenRandom"            ascii
        $sym3 = "BCryptEncrypt"              ascii
        $asy1 = "BCryptImportKeyPair"        ascii
        $asy2 = "BCryptExportKey"            ascii
        $alg1 = "ChainingModeCBC"            wide
        $alg2 = "ChainingModeGCM"            wide
        $alg3 = "RSAPUBLICBLOB"              wide
    condition:
        uint16(0) == 0x5A4D
        and 2 of ($sym*)
        and 1 of ($asy*)
        and 1 of ($alg*)
}

rule CAPI_Hybrid_KeyWrap
{
    meta:
        description = "CAPI hybrid scheme. CryptExportKey with a public key handle IS the key wrap."
        reference   = "02-Hybrid-Encryption-Model"
        confidence  = "medium"
    strings:
        $ctx  = "CryptAcquireContext" ascii
        $gen  = "CryptGenKey"         ascii
        $exp  = "CryptExportKey"      ascii
        $enc  = "CryptEncrypt"        ascii
        $prov = "Microsoft Enhanced RSA and AES" ascii wide
    condition:
        uint16(0) == 0x5A4D and $exp and 2 of ($ctx, $gen, $enc, $prov)
}

rule Embedded_Asymmetric_Public_Key_In_PE
{
    meta:
        description = "Public key material embedded in a PE - the hybrid scheme's build-time artifact"
        note        = "Extract it. The key is a durable campaign identifier, unlike a hash."
        reference   = "02-Hybrid-Encryption-Model"
        confidence  = "high"
    strings:
        $pem_spki  = "-----BEGIN PUBLIC KEY-----"     ascii
        $pem_pkcs1 = "-----BEGIN RSA PUBLIC KEY-----" ascii
        $cng_rsa1  = { 52 53 41 31 }
        $cng_eck1  = { 45 43 4B 31 }
        $der_oid   = { 2A 86 48 86 F7 0D 01 01 01 }
    condition:
        uint16(0) == 0x5A4D and any of them
}

rule Text_Encoded_Key_Footer
{
    meta:
        description = "ASCII footer delimiters used to store base64 key material"
        note        = "Entropy triage CANNOT see base64 key blobs - it scores ~6.0 bits/byte."
        reference   = "06-Case-Studies"
        confidence  = "medium"
    strings:
        $eph    = "--eph--"    ascii
        $marker = "--marker--" ascii
    condition:
        any of them
}
