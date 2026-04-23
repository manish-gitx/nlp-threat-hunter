from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class EntityOut(BaseModel):
    text: str
    label: str

    class Config:
        from_attributes = True


class IOCOut(BaseModel):
    value: str
    ioc_type: str

    class Config:
        from_attributes = True


class ThreatSummary(BaseModel):
    id: int
    source: str
    category: str
    confidence: float
    severity: str
    severity_score: float
    cluster_id: int
    summary: str
    created_at: datetime

    class Config:
        from_attributes = True


class ThreatDetail(ThreatSummary):
    raw_text: str
    cleaned_text: str
    entities: List[EntityOut] = []
    iocs: List[IOCOut] = []


class IngestItem(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = "manual"


class IngestBulk(BaseModel):
    items: List[IngestItem]


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class AnalyzeResponse(BaseModel):
    category: str
    confidence: float
    severity: str
    severity_score: float
    summary: str
    entities: List[EntityOut]
    iocs: List[IOCOut]
    cleaned_text: str


class StatsResponse(BaseModel):
    total_threats: int
    by_category: dict
    by_severity: dict
    recent_7d: List[dict]
    top_iocs: List[dict]
    top_entities: List[dict]
    cluster_count: int


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    context: Optional[dict] = None


class ReportResponse(BaseModel):
    generated_at: datetime
    period_days: int
    total_threats: int
    by_category: dict
    by_severity: dict
    top_iocs: List[dict]
    narrative: str
    recommendations: List[str]
