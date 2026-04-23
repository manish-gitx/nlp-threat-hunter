from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/threats", tags=["threats"])


@router.get("", response_model=list[schemas.ThreatSummary])
def list_threats(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    q = db.query(models.Threat)
    if category:
        q = q.filter(models.Threat.category == category)
    if severity:
        q = q.filter(models.Threat.severity == severity)
    q = q.order_by(desc(models.Threat.created_at)).offset(offset).limit(limit)
    return q.all()


@router.get("/{threat_id}", response_model=schemas.ThreatDetail)
def get_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat


@router.delete("/{threat_id}")
def delete_threat(threat_id: int, db: Session = Depends(get_db)):
    threat = db.query(models.Threat).filter(models.Threat.id == threat_id).first()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    db.delete(threat)
    db.commit()
    return {"ok": True}
