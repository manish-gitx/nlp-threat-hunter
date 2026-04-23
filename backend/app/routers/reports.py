from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])


_RECOMMENDATIONS = {
    "malware": [
        "Isolate affected endpoints and run full EDR sweep.",
        "Block observed hashes and C2 domains at the proxy and firewall.",
        "Review AV exclusions and patch level on impacted hosts.",
    ],
    "phishing": [
        "Pull matching messages from all mailboxes and block the sender domain.",
        "Reset credentials for any user that interacted with the link.",
        "Refresh phishing-awareness training for the targeted department.",
    ],
    "apt": [
        "Engage incident response and preserve forensic evidence before remediation.",
        "Hunt for the actor's TTPs across the environment, not just the alerting host.",
        "Rotate privileged credentials and review domain-level persistence.",
    ],
    "brute_force": [
        "Enforce MFA on any exposed authentication surface.",
        "Rate-limit and geo-restrict access at the edge.",
        "Lock and review any accounts showing successful logins after failures.",
    ],
    "ddos": [
        "Engage upstream scrubbing provider and enable traffic filtering.",
        "Scale critical services horizontally and enable rate limiting.",
    ],
    "data_exfiltration": [
        "Block the destination and review DLP logs for scope of data movement.",
        "Involve legal/privacy if regulated data may have left the environment.",
    ],
    "insider_threat": [
        "Suspend access for the involved identity pending investigation.",
        "Preserve endpoint, email, and cloud audit logs.",
    ],
}


@router.get("/generate", response_model=schemas.ReportResponse)
def generate_report(
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90),
):
    cutoff = datetime.utcnow() - timedelta(days=days)
    threats = db.query(models.Threat).filter(models.Threat.created_at >= cutoff).all()

    by_category = Counter(t.category for t in threats)
    by_severity = Counter(t.severity for t in threats)

    ioc_counter: Counter = Counter()
    for t in threats:
        for ioc in t.iocs:
            ioc_counter[(ioc.value, ioc.ioc_type)] += 1
    top_iocs = [
        {"value": v, "ioc_type": tp, "count": c}
        for (v, tp), c in ioc_counter.most_common(10)
    ]

    total = len(threats)
    critical_count = by_severity.get("critical", 0)
    high_count = by_severity.get("high", 0)
    top_cats = ", ".join(f"{c} ({n})" for c, n in by_category.most_common(3)) or "none"

    narrative = (
        f"Over the last {days} day(s) the platform ingested {total} security event(s). "
        f"{critical_count} were classified critical and {high_count} high severity. "
        f"The most common categories were: {top_cats}. "
        f"{len(top_iocs)} unique indicators of compromise were extracted."
    )

    recs: list[str] = []
    for category, _ in by_category.most_common():
        recs.extend(_RECOMMENDATIONS.get(category, []))
    # Deduplicate while preserving order.
    seen: set[str] = set()
    dedup_recs: list[str] = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            dedup_recs.append(r)

    return schemas.ReportResponse(
        generated_at=datetime.utcnow(),
        period_days=days,
        total_threats=total,
        by_category=dict(by_category),
        by_severity=dict(by_severity),
        top_iocs=top_iocs,
        narrative=narrative,
        recommendations=dedup_recs[:8],
    )
