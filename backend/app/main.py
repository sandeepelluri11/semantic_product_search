from contextlib import asynccontextmanager
from typing import AsyncIterator

import orjson
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

from .config import get_settings
from .schemas import SearchRequest, SearchResponse, Product
from .search import semantic_search


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Place for startup/shutdown logic (warm up models, ES health checks, etc.)
    yield


app = FastAPI(
    title="AI Semantic Product Search",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api")


@router.post("/search", response_model=SearchResponse)
async def search_products(payload: SearchRequest) -> SearchResponse:
    filters_dict = payload.filters.dict(exclude_none=True) if payload.filters else {}

    raw = semantic_search(
        query=payload.query,
        size=payload.size,
        filters=filters_dict,
    )

    products = [
        Product(
            id=item["id"],
            score=item.get("score"),
            ranking_score=item.get("ranking_score"),
            source=item.get("source", {}),
        )
        for item in raw.get("items", [])
    ]

    return SearchResponse(
        total=raw.get("total", 0),
        items=products,
        took_ms=raw.get("took_ms", 0),
        error=raw.get("error"),
    )


@router.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(router)

