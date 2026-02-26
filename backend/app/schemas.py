from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str = Field(..., description="Document ID from Elasticsearch")
    score: float | None = Field(None, description="Raw ES relevance score")
    ranking_score: float | None = Field(
        None, description="Custom ranking score combining multiple signals"
    )
    source: Dict[str, Any] = Field(
        default_factory=dict, description="Original product document from ES"
    )


class SearchFilters(BaseModel):
    category: Optional[str] = None
    brand: Optional[str] = None


class SearchRequest(BaseModel):
    query: str = Field("", description="User's search query")
    size: int = Field(20, ge=1, le=100, description="Max number of results")
    filters: Optional[SearchFilters] = None


class SearchResponse(BaseModel):
    total: int
    items: List[Product]
    took_ms: int
    error: Optional[str] = None

