from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models
from app.database import get_db

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("")
def list_entities(db: Session = Depends(get_db)):
    rows = db.query(models.Entity.text, models.Entity.label).all()
    counter = Counter((v, l) for v, l in rows)
    return {
        "total": sum(counter.values()),
        "unique": len(counter),
        "items": [
            {"text": v, "label": l, "count": c}
            for (v, l), c in counter.most_common(100)
        ],
    }


@router.get("/iocs")
def list_iocs(db: Session = Depends(get_db)):
    rows = db.query(models.IOC.value, models.IOC.ioc_type).all()
    counter = Counter((v, t) for v, t in rows)
    by_type: dict[str, int] = {}
    for (_, t), c in counter.items():
        by_type[t] = by_type.get(t, 0) + c
    return {
        "total": sum(counter.values()),
        "unique": len(counter),
        "by_type": by_type,
        "items": [
            {"value": v, "ioc_type": t, "count": c}
            for (v, t), c in counter.most_common(200)
        ],
    }
