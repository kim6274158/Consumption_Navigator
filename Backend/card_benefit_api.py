#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid (dense + sparse) Milvus search API for card benefits.

Steps:
1. On startup, connect to Milvus and make sure the collection exists.
2. If empty, read card_data/cardgorilla_top100_detailed.json,
   embed each benefits_text with BGEM3 (dense + sparse) and insert.
3. Expose POST /search to embed a user query and run hybrid search.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    AnnSearchRequest,
    RRFRanker,
)
from pymilvus.model.hybrid import BGEM3EmbeddingFunction

import json

# Ensure Hugging Face cache persists locally to avoid repeated downloads
_hf_cache = os.getenv("HF_HOME") or os.getenv("TRANSFORMERS_CACHE")
if not _hf_cache:
    _hf_cache = (Path.cwd() / ".hf_cache").as_posix()
    os.environ.setdefault("HF_HOME", _hf_cache)
    os.environ.setdefault("TRANSFORMERS_CACHE", _hf_cache)
Path(_hf_cache).mkdir(parents=True, exist_ok=True)

CARD_JSON = Path("card_data/cardgorilla_top100_detailed.json")
COLLECTION_NAME = "card_benefits_hybrid"
DENSE_FIELD = "benefit_dense"
SPARSE_FIELD = "benefit_sparse"
MAX_VARCHAR = 2048

DEFAULT_MILVUS_URI = (Path.cwd() / "card_benefits.db").as_posix()
MILVUS_URI = os.getenv("MILVUS_URI", DEFAULT_MILVUS_URI)

embedding_fn = BGEM3EmbeddingFunction(
    use_fp16=False, device=os.getenv("BGE_DEVICE", "cpu"))


def connect_milvus():
    connections.connect(alias="default", uri=MILVUS_URI)


def create_collection_if_needed() -> Collection:
    fields = [
        FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema("rank", DataType.INT64),
        FieldSchema("name", DataType.VARCHAR, max_length=256),
        FieldSchema("issuer", DataType.VARCHAR, max_length=256),
        FieldSchema("event_text", DataType.VARCHAR, max_length=MAX_VARCHAR),
        FieldSchema("benefits_raw", DataType.VARCHAR, max_length=MAX_VARCHAR),
        FieldSchema(DENSE_FIELD, DataType.FLOAT_VECTOR,
                    dim=embedding_fn.dim["dense"]),
        FieldSchema(SPARSE_FIELD, DataType.SPARSE_FLOAT_VECTOR),
    ]
    schema = CollectionSchema(
        fields, description="Card benefits hybrid embeddings")

    if utility.has_collection(COLLECTION_NAME):
        collection = Collection(COLLECTION_NAME)
    else:
        collection = Collection(name=COLLECTION_NAME, schema=schema)

    # Create indexes (AUTOINDEX dense + sparse inverted)
    if not any(idx.field_name == DENSE_FIELD for idx in collection.indexes):
        collection.create_index(
            DENSE_FIELD,
            index_params={"metric_type": "IP", "index_type": "AUTOINDEX"},
        )

    if not any(idx.field_name == SPARSE_FIELD for idx in collection.indexes):
        collection.create_index(
            SPARSE_FIELD,
            index_params={"index_type": "SPARSE_INVERTED_INDEX"},
        )

    collection.load()
    return collection


def load_cards_from_json() -> List[dict]:
    if not CARD_JSON.exists():
        raise FileNotFoundError(f"{CARD_JSON} not found.")
    return json.loads(CARD_JSON.read_text(encoding="utf-8"))


def ingest_if_empty(collection: Collection):
    if collection.num_entities > 0:
        return

    cards = load_cards_from_json()
    texts = []
    ranks = []
    names = []
    issuers = []
    events = []
    benefits_raw = []

    for card in cards:
        benefits = card.get("description_text", {}).get(
            "benefits_text", []) or []
        text = "; ".join(benefits)
        texts.append(text)
        ranks.append(card.get("rank") or 0)
        names.append(card.get("name", ""))
        issuers.append(card.get("issuer", ""))
        events.append(card.get("event_text") or "")
        benefits_raw.append(text)

    embeddings = embedding_fn.encode_documents(texts)
    dense_vectors = [vec.tolist() for vec in embeddings["dense"]]
    sparse_matrix = embeddings["sparse"].tocsr()

    collection.insert(
        [
            ranks,
            names,
            issuers,
            events,
            benefits_raw,
            dense_vectors,
            sparse_matrix,
        ]
    )
    collection.flush()


def ensure_ready() -> Collection:
    connect_milvus()
    collection = create_collection_if_needed()
    ingest_if_empty(collection)
    collection.load()
    return collection


collection = None
_collection_lock = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


app = FastAPI(
    title="Card Benefit Hybrid Search API",
    description="Find the closest card benefits using Milvus hybrid search.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_collection() -> Collection:
    global collection, _collection_lock
    if collection is not None:
        return collection

    import threading

    if _collection_lock is None:
        _collection_lock = threading.Lock()

    with _collection_lock:
        if collection is None:
            collection = ensure_ready()
    return collection


def build_hybrid_requests(query: str, top_k: int) -> List[AnnSearchRequest]:
    emb = embedding_fn.encode_queries([query])
    dense = [[value for value in emb["dense"][0]]]
    sparse_matrix = emb["sparse"].tocsr()

    dense_req = AnnSearchRequest(
        data=dense,
        anns_field=DENSE_FIELD,
        param={"metric_type": "IP"},
        limit=max(top_k * 2, top_k),
    )
    sparse_req = AnnSearchRequest(
        data=sparse_matrix,
        anns_field=SPARSE_FIELD,
        param={},
        limit=max(top_k * 2, top_k),
    )
    return [dense_req, sparse_req]


@app.on_event("startup")
def _startup_event():
    get_collection()


@app.post("/search")
def search_benefits(request: SearchRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="query must not be empty")

    collection = get_collection()

    hybrid_reqs = build_hybrid_requests(request.query, request.top_k)

    results = collection.hybrid_search(
        hybrid_reqs,
        rerank=RRFRanker(),
        limit=request.top_k,
        output_fields=["rank", "name", "issuer", "event_text", "benefits_raw"],
    )

    hits = results[0]
    response = []
    for hit in hits:
        response.append(
            {
                "score": hit.score,
                "rank": hit.entity.get("rank"),
                "name": hit.entity.get("name"),
                "issuer": hit.entity.get("issuer"),
                "event_text": hit.entity.get("event_text"),
                "benefits_text": hit.entity.get("benefits_raw"),
            }
        )

    return {"query": request.query, "results": response}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(
        os.getenv("CARD_API_PORT", "9800")))
