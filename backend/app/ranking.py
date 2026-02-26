from typing import Any, Dict, List

import numpy as np


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def score_document(doc: Dict[str, Any], query: str) -> float:
    """
    Basic scoring function combining:
    - BM25 or text relevance score (from Elasticsearch `_score`)
    - Popularity (e.g. total_sales)
    - User behavior (e.g. click_through_rate)

    This is a simple ML-style handcrafted model; you can later
    replace it with a learned model (e.g. LambdaMART, neural ranker, etc.).
    """
    es_score = _safe_float(doc.get("_score"), 0.0)

    source = doc.get("_source", {})
    popularity = _safe_float(source.get("popularity", source.get("total_sales", 0.0)))
    ctr = _safe_float(source.get("click_through_rate", 0.0))
    rating = _safe_float(source.get("rating", 0.0))  # 0–5

    log_popularity = np.log1p(popularity)
    normalized_rating = rating / 5.0

    w_es = 1.0
    w_popularity = 0.4
    w_ctr = 0.7
    w_rating = 0.3

    score = (
        w_es * es_score
        + w_popularity * log_popularity
        + w_ctr * ctr
        + w_rating * normalized_rating
    )

    return float(score)


def rerank_hits(
    hits: List[Dict[str, Any]],
    query: str,
    top_k: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Re-rank a list of ES hits using `score_document`.
    Adds a `ranking_score` field to each hit and sorts by it.
    """
    for hit in hits:
        hit["ranking_score"] = score_document(hit, query)

    hits_sorted = sorted(hits, key=lambda h: h.get("ranking_score", 0.0), reverse=True)

    if top_k is not None:
        hits_sorted = hits_sorted[:top_k]

    return hits_sorted

