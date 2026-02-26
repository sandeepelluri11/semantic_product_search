from typing import Any, Dict, List

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from elasticsearch.exceptions import NotFoundError

from .config import get_settings
from .ranking import rerank_hits


def get_es_client() -> Elasticsearch:
    settings = get_settings()
    if settings.es_username and settings.es_password:
        return Elasticsearch(
            settings.es_host,
            basic_auth=(settings.es_username, settings.es_password),
        )
    return Elasticsearch(settings.es_host)


def semantic_search(
    query: str,
    size: int = 20,
    filters: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Execute a semantic-style search query against Elasticsearch and
    rerank the results using our ranking module.
    """
    settings = get_settings()
    client = get_es_client()

    must_clauses: List[Dict[str, Any]] = []

    if query:
        must_clauses.append(
            {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",
                        "name^3",
                        "description^1",
                        "category^1",
                        "tags^2",
                    ],
                    "type": "best_fields",
                    "fuzziness": "AUTO",
                }
            }
        )

    filter_clauses: List[Dict[str, Any]] = []
    filters = filters or {}

    for key, value in filters.items():
        if value is None or value == "":
            continue
        filter_clauses.append({"term": {key: value}})

    body: Dict[str, Any] = {
        "query": {
            "bool": {
                "must": must_clauses or [{"match_all": {}}],
                "filter": filter_clauses,
            }
        },
        "size": size,
    }

    try:
        response = client.search(index=settings.es_index, body=body)
    except NotFoundError:
        return {
            "total": 0,
            "items": [],
            "took_ms": 0,
            "error": f"Index '{settings.es_index}' not found.",
        }
    except ESConnectionError:
        return {
            "total": 0,
            "items": [],
            "took_ms": 0,
            "error": "Unable to connect to Elasticsearch. Is it running?",
        }

    hits = response.get("hits", {}).get("hits", [])
    took_ms = response.get("took", 0)

    reranked = rerank_hits(hits, query)

    items = [
        {
            "id": hit.get("_id"),
            "score": hit.get("_score"),
            "ranking_score": hit.get("ranking_score"),
            "source": hit.get("_source", {}),
        }
        for hit in reranked
    ]

    total_value = response.get("hits", {}).get("total", 0)
    if isinstance(total_value, dict):
        total = total_value.get("value", 0)
    else:
        total = int(total_value)

    return {
        "total": total,
        "items": items,
        "took_ms": took_ms,
        "error": None,
    }

