"""Populate the database with a handful of realistic SOC-style events so the
dashboard has something to render on first load. Safe to run multiple times —
it will only insert if the DB is empty.

Usage:
    python seed.py
"""
from app.database import SessionLocal, init_db
from app import models
from app.services import threat_service


SAMPLES = [
    ("EDR detected Cobalt Strike beacon on host WIN-DC01 beaconing to 185.23.12.44 over port 443", "edr"),
    ("User reported phishing email from it-helpdesk@microsft-secure.com with link to fake O365 login", "email_gateway"),
    ("500+ failed SSH authentications from 45.77.12.5 targeting root on bastion-01", "auth_logs"),
    ("APT29 TTPs observed: WMI persistence and PowerShell Empire activity on finance-03, MITRE T1059.001", "threat_intel"),
    ("8.4 GB outbound transfer from db-prod-02 to 193.142.58.10 during off-hours", "netflow"),
    ("Ransomware encryption: files on hr-share renamed with .locked extension, note dropped", "edr"),
    ("SYN flood of 12 Mpps targeting www.example.com from distributed botnet", "ddos_mitigation"),
    ("Malicious macro observed in invoice.xlsm, SHA256 a3f5...b91c, dropped Emotet loader", "sandbox"),
    ("Password spraying against O365 using Common2024! from residential proxy range", "identity"),
    ("Nightly backup of app-cluster completed successfully, 2.1 TB transferred", "backup"),
    ("Developer pushed AWS credentials to public GitHub repo acme/internal-tools", "dlp"),
    ("Exploit attempt against CVE-2024-12345 on edge appliance blocked by WAF", "waf"),
]


def main() -> None:
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(models.Threat).count()
        if existing:
            print(f"Skipping seed — {existing} threat record(s) already present.")
            return
        for text, source in SAMPLES:
            threat_service.ingest_one(db, text=text, source=source)
        threat_service.recluster(db)
        print(f"Inserted {len(SAMPLES)} sample threats.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
