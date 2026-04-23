from typing import Iterable, List

from sqlalchemy.orm import Session

from app import models
from app.nlp.clustering import cluster_texts
from app.nlp.pipeline import analyze


def ingest_one(db: Session, text: str, source: str = "manual") -> models.Threat:
    result = analyze(text)
    threat = models.Threat(
        source=source,
        raw_text=text,
        cleaned_text=result["cleaned_text"],
        category=result["category"],
        confidence=result["confidence"],
        severity=result["severity"],
        severity_score=result["severity_score"],
        summary=result["summary"],
    )
    for ent in result["entities"]:
        threat.entities.append(models.Entity(text=ent["text"], label=ent["label"]))
    for ioc in result["iocs"]:
        threat.iocs.append(models.IOC(value=ioc["value"], ioc_type=ioc["ioc_type"]))
    db.add(threat)
    db.commit()
    db.refresh(threat)
    return threat


def ingest_bulk(db: Session, items: Iterable[dict]) -> List[models.Threat]:
    created: List[models.Threat] = []
    for item in items:
        created.append(ingest_one(db, text=item["text"], source=item.get("source", "bulk")))
    recluster(db)
    return created


def recluster(db: Session) -> None:
    threats = db.query(models.Threat).all()
    texts = [t.cleaned_text for t in threats]
    labels = cluster_texts(texts)
    for t, cid in zip(threats, labels):
        t.cluster_id = cid
    db.commit()
