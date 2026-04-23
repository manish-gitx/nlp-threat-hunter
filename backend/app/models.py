from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Threat(Base):
    __tablename__ = "threats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64), default="manual")
    raw_text: Mapped[str] = mapped_column(Text)
    cleaned_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    severity: Mapped[str] = mapped_column(String(16), index=True, default="low")
    severity_score: Mapped[float] = mapped_column(Float, default=0.0)
    cluster_id: Mapped[int] = mapped_column(Integer, default=-1, index=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="threat", cascade="all, delete-orphan"
    )
    iocs: Mapped[list["IOC"]] = relationship(
        "IOC", back_populates="threat", cascade="all, delete-orphan"
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    threat_id: Mapped[int] = mapped_column(ForeignKey("threats.id"), index=True)
    text: Mapped[str] = mapped_column(String(256))
    label: Mapped[str] = mapped_column(String(64), index=True)

    threat: Mapped[Threat] = relationship("Threat", back_populates="entities")


class IOC(Base):
    __tablename__ = "iocs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    threat_id: Mapped[int] = mapped_column(ForeignKey("threats.id"), index=True)
    value: Mapped[str] = mapped_column(String(512))
    ioc_type: Mapped[str] = mapped_column(String(32), index=True)

    threat: Mapped[Threat] = relationship("Threat", back_populates="iocs")


class IngestBatch(Base):
    __tablename__ = "ingest_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(64))
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
