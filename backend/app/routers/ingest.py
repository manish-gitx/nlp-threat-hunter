from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.nlp.pipeline import analyze
from app.services import threat_service

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("", response_model=schemas.ThreatDetail)
def ingest(item: schemas.IngestItem, db: Session = Depends(get_db)):
    threat = threat_service.ingest_one(db, text=item.text, source=item.source)
    threat_service.recluster(db)
    db.refresh(threat)
    return threat


@router.post("/bulk", response_model=list[schemas.ThreatSummary])
def ingest_bulk(payload: schemas.IngestBulk, db: Session = Depends(get_db)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="items must not be empty")
    items = [{"text": i.text, "source": i.source} for i in payload.items]
    return threat_service.ingest_bulk(db, items)


@router.post("/analyze", response_model=schemas.AnalyzeResponse)
def analyze_only(payload: schemas.AnalyzeRequest):
    """Run the NLP pipeline without persisting. Useful for preview."""
    return analyze(payload.text)
