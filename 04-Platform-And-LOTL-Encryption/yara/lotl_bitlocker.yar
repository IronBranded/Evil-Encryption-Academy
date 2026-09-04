/*
   Living-off-the-land encryption via BitLocker and other OS-native mechanisms.

   TRIAGE AID. Legitimate administrative scripts match these. Context decides.
   Where there is no malware to reverse, detection is behavioural - pair these
   with the Sigma logic in 11-Endpoint-Detection/sigma/.

   Reference: 04-Platform-And-LOTL-Encryption/README.md
*/

rule LOTL_BitLocker_Abuse_Script
{
    meta:
        description = "Script referencing BitLocker control interfaces used for volume encryption"
        reference   = "04-Platform-And-LOTL-Encryption"
        confidence  = "medium"
    strings:
        $wmi1 = "Win32_EncryptableVolume"         ascii wide nocase
        $wmi2 = "ProtectKeyWithNumericalPassword" ascii wide nocase
        $wmi3 = "ProtectKeyWithPassphrase"        ascii wide nocase
        $ps1  = "Enable-BitLocker"                ascii wide nocase
        $ps2  = "Remove-BitLockerKeyProtector"    ascii wide nocase
        $cli  = "manage-bde"                      ascii wide nocase
        $hostile1 = "DisableKeyProtectors"        ascii wide nocase
        $hostile2 = "-forcerecovery"              ascii wide nocase
        $reg  = "EnableBDEWithNoTPM"              ascii wide nocase
    condition:
        2 of ($wmi*, $ps*, $cli) and 1 of ($hostile*, $reg)
}

rule Encrypted_Volume_Container_Header
{
    meta:
        description = "Full-disk encryption container signatures"
        note        = "Presence is normal on encrypted volumes. Relevant when UNEXPECTED."
        reference   = "04-Platform-And-LOTL-Encryption"
        confidence  = "high"
    strings:
        $fve  = "-FVE-FS-"     ascii
        $luks = { 4C 55 4B 53 BA BE }
        $vera = "VERA"         ascii
    condition:
        any of them at 0 or $fve
}
