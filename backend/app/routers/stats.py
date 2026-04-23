from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=schemas.StatsResponse)
def stats(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Threat.id)).scalar() or 0

    category_rows = (
        db.query(models.Threat.category, func.count(models.Threat.id))
        .group_by(models.Threat.category)
        .all()
    )
    by_category = {cat: count for cat, count in category_rows}

    severity_rows = (
        db.query(models.Threat.severity, func.count(models.Threat.id))
        .group_by(models.Threat.severity)
        .all()
    )
    by_severity = {sev: count for sev, count in severity_rows}

    # Daily counts for the last 7 days.
    cutoff = datetime.utcnow() - timedelta(days=7)
    recent = (
        db.query(models.Threat.created_at, models.Threat.severity)
        .filter(models.Threat.created_at >= cutoff)
        .all()
    )
    day_counts: dict[str, dict] = {}
    for i in range(7):
        d = (datetime.utcnow() - timedelta(days=6 - i)).strftime("%Y-%m-%d")
        day_counts[d] = {"date": d, "count": 0, "critical": 0, "high": 0}
    for created, sev in recent:
        key = created.strftime("%Y-%m-%d")
        if key in day_counts:
            day_counts[key]["count"] += 1
            if sev in ("critical", "high"):
                day_counts[key][sev] += 1
    recent_series = list(day_counts.values())

    ioc_rows = db.query(models.IOC.value, models.IOC.ioc_type).all()
    ioc_counter = Counter((v, t) for v, t in ioc_rows)
    top_iocs = [
        {"value": v, "ioc_type": t, "count": c}
        for (v, t), c in ioc_counter.most_common(10)
    ]

    ent_rows = db.query(models.Entity.text, models.Entity.label).all()
    ent_counter = Counter((v, t) for v, t in ent_rows)
    top_entities = [
        {"text": v, "label": t, "count": c}
        for (v, t), c in ent_counter.most_common(10)
    ]

    cluster_count = (
        db.query(func.count(func.distinct(models.Threat.cluster_id)))
        .filter(models.Threat.cluster_id >= 0)
        .scalar()
        or 0
    )

    return schemas.StatsResponse(
        total_threats=total,
        by_category=by_category,
        by_severity=by_severity,
        recent_7d=recent_series,
        top_iocs=top_iocs,
        top_entities=top_entities,
        cluster_count=cluster_count,
    )
