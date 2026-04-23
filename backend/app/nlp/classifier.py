import os
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.config import get_settings
from app.nlp.training_data import TRAINING_SAMPLES

_pipeline: Optional[Pipeline] = None
_MODEL_FILE = "threat_classifier.joblib"


def _train() -> Pipeline:
    texts = [t for t, _ in TRAINING_SAMPLES]
    labels = [y for _, y in TRAINING_SAMPLES]
    pipe = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95,
                    sublinear_tf=True,
                    lowercase=True,
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000, C=2.0, class_weight="balanced")),
        ]
    )
    pipe.fit(texts, labels)
    return pipe


def _cache_path() -> Path:
    settings = get_settings()
    cache_dir = Path(settings.model_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / _MODEL_FILE


def get_classifier() -> Pipeline:
    global _pipeline
    if _pipeline is not None:
        return _pipeline
    path = _cache_path()
    if path.exists():
        try:
            _pipeline = joblib.load(path)
            return _pipeline
        except Exception:
            # Corrupted cache — retrain.
            os.remove(path)
    _pipeline = _train()
    try:
        joblib.dump(_pipeline, path)
    except Exception:
        pass
    return _pipeline


def classify(text: str) -> tuple[str, float]:
    pipe = get_classifier()
    probs = pipe.predict_proba([text])[0]
    idx = int(np.argmax(probs))
    label = pipe.classes_[idx]
    return str(label), float(probs[idx])
