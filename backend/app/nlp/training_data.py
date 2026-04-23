"""Seed corpus for the threat classifier.

Labels intentionally cover the threat categories called out in the project
abstract (malware, phishing, APT) plus a few operationally useful extras so
the classifier can distinguish common SOC alert types.
"""

TRAINING_SAMPLES: list[tuple[str, str]] = [
    # --- malware ---
    ("Endpoint detected Emotet loader dropping payload from 185.23.12.44", "malware"),
    ("TrickBot banking trojan observed beaconing to command and control server", "malware"),
    ("Suspicious executable with MD5 d41d8cd98f00b204e9800998ecf8427e quarantined", "malware"),
    ("Ransomware encryption activity: files renamed with .locked extension", "malware"),
    ("Cobalt Strike beacon identified on host WIN-DC01 communicating over HTTPS", "malware"),
    ("Malicious DLL side-loading detected via signed binary proxy execution", "malware"),
    ("AV engine blocked RedLine Stealer sample SHA256 from user download", "malware"),
    ("Worm propagating through SMB shares, spreading laterally across subnet", "malware"),

    # --- phishing ---
    ("User reported suspicious email with spoofed domain paypa1-secure.com and credential harvesting link", "phishing"),
    ("Spear phishing email targeting finance team with invoice-themed Office macro", "phishing"),
    ("Email gateway quarantined message impersonating IT help desk requesting MFA reset", "phishing"),
    ("Credential phishing landing page cloning Microsoft 365 login discovered", "phishing"),
    ("Fake DocuSign notification delivered malicious link to external SharePoint", "phishing"),
    ("Business email compromise attempt requesting urgent wire transfer to new account", "phishing"),
    ("Smishing campaign observed sending fake bank one-time password confirmation texts", "phishing"),

    # --- apt ---
    ("APT29 TTPs observed: WMI persistence and PowerShell Empire framework usage", "apt"),
    ("Lazarus group toolkit detected with custom implant matching MITRE T1059.001", "apt"),
    ("Long-dwell intrusion with living-off-the-land binaries and Kerberoasting on domain controller", "apt"),
    ("Advanced persistent threat leveraging supply-chain compromise of update server", "apt"),
    ("State-sponsored actor exploiting zero-day CVE-2024-12345 in edge appliance", "apt"),
    ("FIN7 operators deploying Carbanak backdoor via malicious USB devices", "apt"),

    # --- brute_force ---
    ("500 failed SSH login attempts from IP 45.77.12.5 targeting root account", "brute_force"),
    ("Password spraying observed against Office 365 from distributed residential proxies", "brute_force"),
    ("Repeated RDP authentication failures followed by successful login from unusual geo", "brute_force"),
    ("Credential stuffing attack using leaked credentials against customer portal", "brute_force"),
    ("SMB brute-force attempts saturating authentication logs on file server", "brute_force"),

    # --- ddos ---
    ("Volumetric UDP flood saturating 10 Gbps uplink on edge router", "ddos"),
    ("SYN flood distributed denial of service targeting public-facing web application", "ddos"),
    ("DNS amplification attack using open resolvers against customer API endpoint", "ddos"),
    ("Layer 7 HTTP flood exhausting application worker pool on checkout service", "ddos"),

    # --- data_exfiltration ---
    ("Large outbound transfer of 8 GB from database server to unknown external IP", "data_exfiltration"),
    ("DNS tunneling pattern observed: high volume of TXT record queries to suspicious domain", "data_exfiltration"),
    ("Sensitive HR files uploaded to personal cloud storage by privileged user", "data_exfiltration"),
    ("Staging of customer PII into archive prior to upload to Mega.nz", "data_exfiltration"),
    ("Unusual SMTP traffic with attachments leaving finance VLAN overnight", "data_exfiltration"),

    # --- insider_threat ---
    ("Terminated employee accessed shared drive and copied proprietary source code", "insider_threat"),
    ("Privileged admin created rogue local account on production database host", "insider_threat"),
    ("Developer pushed credentials-containing code to public GitHub repository", "insider_threat"),
    ("Contractor downloaded customer list outside normal working hours from VPN", "insider_threat"),

    # --- benign (negatives — reduce over-classification) ---
    ("Scheduled nightly backup completed successfully on database cluster", "benign"),
    ("Routine system update patch applied to workstation fleet", "benign"),
    ("User logged in from expected location during business hours", "benign"),
    ("Disk usage alert resolved after log rotation executed", "benign"),
    ("Antivirus definitions updated to version 2026.04.23 across endpoints", "benign"),
    ("Firewall rule change approved and deployed as part of change ticket", "benign"),
]
