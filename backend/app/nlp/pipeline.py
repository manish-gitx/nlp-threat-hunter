"""High-level orchestrator for the NLP threat analysis pipeline."""
from typing import Dict

from app.nlp.classifier import classify
from app.nlp.iocs import extract_iocs
from app.nlp.ner import extract_entities
from app.nlp.preprocessing import clean_text, summarize
from app.nlp.severity import score_severity


def analyze(text: str) -> Dict:
    cleaned = clean_text(text)
    category, confidence = classify(cleaned)
    iocs = extract_iocs(cleaned)
    entities = extract_entities(cleaned)
    severity, severity_score = score_severity(cleaned, category, len(iocs))
    return {
        "cleaned_text": cleaned,
        "category": category,
        "confidence": round(float(confidence), 3),
        "severity": severity,
        "severity_score": severity_score,
        "summary": summarize(cleaned),
        "entities": entities,
        "iocs": iocs,
    }
