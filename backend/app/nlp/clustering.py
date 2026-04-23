from typing import List, Sequence

import numpy as np
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def cluster_texts(texts: Sequence[str], max_clusters: int = 8) -> List[int]:
    """Cluster cleaned threat texts into groups of related incidents.

    Returns a list of cluster IDs aligned with the input order. If there are
    fewer than 3 texts we skip clustering and return all -1.
    """
    if len(texts) < 3:
        return [-1] * len(texts)

    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)
    try:
        X = vectorizer.fit_transform(texts)
    except ValueError:
        return [-1] * len(texts)

    k = max(2, min(max_clusters, int(np.sqrt(len(texts)))))
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(X)
    return [int(x) for x in labels]
