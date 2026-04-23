"""Rule-based analyst assistant.

Deliberately implemented without an external LLM so the project runs without
extra API keys. It answers questions the abstract mentions (trend, top threat
categories, IOC lookups) by querying the existing DB.
"""
import re
from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.nlp.pipeline import analyze

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _top_category(db: Session) -> tuple[str, int] | None:
    row = (
        db.query(models.Threat.category, func.count(models.Threat.id).label("c"))
        .group_by(models.Threat.category)
        .order_by(desc("c"))
        .first()
    )
    if not row:
        return None
    return row[0], int(row[1])


def _critical_count(db: Session, days: int = 7) -> int:
    cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(func.count(models.Threat.id))
        .filter(models.Threat.severity == "critical")
        .filter(models.Threat.created_at >= cutoff)
        .scalar()
        or 0
    )


def _lookup_ioc(db: Session, needle: str) -> list[dict]:
    rows = (
        db.query(models.IOC, models.Threat)
        .join(models.Threat, models.IOC.threat_id == models.Threat.id)
        .filter(models.IOC.value.ilike(f"%{needle}%"))
        .limit(5)
        .all()
    )
    return [
        {
            "ioc": r[0].value,
            "type": r[0].ioc_type,
            "threat_id": r[1].id,
            "category": r[1].category,
            "severity": r[1].severity,
        }
        for r in rows
    ]


@router.post("", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    msg = payload.message.strip()
    low = msg.lower()

    # Classify the user's message for analysis queries.
    if low.startswith("analyze ") or low.startswith("classify "):
        target = msg.split(" ", 1)[1].strip()
        result = analyze(target)
        return schemas.ChatResponse(
            reply=(
                f"Classified as **{result['category']}** "
                f"(confidence {result['confidence']:.2f}, severity {result['severity']}). "
                f"Found {len(result['iocs'])} IOCs and {len(result['entities'])} entities."
            ),
            context=result,
        )

    if any(k in low for k in ("top threat", "most common", "biggest threat")):
        top = _top_category(db)
        if top:
            return schemas.ChatResponse(
                reply=f"The most common threat category is **{top[0]}** with {top[1]} event(s)."
            )
        return schemas.ChatResponse(reply="No threats have been ingested yet.")

    if any(k in low for k in ("critical", "how many critical")):
        count = _critical_count(db)
        return schemas.ChatResponse(
            reply=f"There have been {count} critical threat(s) in the last 7 days."
        )

    if "trend" in low or "last 7" in low or "weekly" in low:
        cutoff = datetime.utcnow() - timedelta(days=7)
        rows = (
            db.query(models.Threat.category, func.count(models.Threat.id).label("c"))
            .filter(models.Threat.created_at >= cutoff)
            .group_by(models.Threat.category)
            .order_by(desc("c"))
            .limit(5)
            .all()
        )
        if not rows:
            return schemas.ChatResponse(reply="No activity in the last 7 days.")
        top = ", ".join(f"{c} ({n})" for c, n in rows)
        return schemas.ChatResponse(reply=f"Last 7 days top categories: {top}.")

    # Treat anything that looks like an IOC as a lookup.
    ioc_match = re.search(r"[a-f0-9]{32,64}|\b\d{1,3}(?:\.\d{1,3}){3}\b|\bCVE-\d{4}-\d+\b", msg, re.IGNORECASE)
    if ioc_match:
        results = _lookup_ioc(db, ioc_match.group(0))
        if results:
            lines = [
                f"- {r['ioc']} ({r['type']}) → threat #{r['threat_id']} [{r['category']}/{r['severity']}]"
                for r in results
            ]
            return schemas.ChatResponse(
                reply=f"Found {len(results)} match(es):\n" + "\n".join(lines),
                context={"matches": results},
            )
        return schemas.ChatResponse(reply=f"No matches for `{ioc_match.group(0)}` in the indexed IOCs.")

    total = db.query(func.count(models.Threat.id)).scalar() or 0
    return schemas.ChatResponse(
        reply=(
            "I can help with: top threat categories, critical-alert counts, 7-day trends, "
            "IOC lookups (paste an IP/hash/CVE), and live classification (start with "
            "`analyze <text>`). "
            f"The database currently holds {total} threat record(s)."
        )
    )
