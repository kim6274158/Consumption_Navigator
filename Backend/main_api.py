#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified FastAPI entrypoint that exposes all project APIs on port 9600.

It aggregates:
- client_app (소비 내역 분석)
- card_benefit_api (카드 혜택 하이브리드 검색)
- chatbot_api (LangGraph 메모리 챗봇)
"""
from __future__ import annotations

import os
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the existing FastAPI apps
from client_app import app as consumption_app
from card_benefit_api import app as card_benefit_app
from chatbot_api import app as chatbot_app


def create_app() -> FastAPI:
    """Build a FastAPI instance that exposes every router on a single port."""
    app = FastAPI(
        title="Unified Transaction APIs",
        description=(
            "거래 데이터 분석, 카드 혜택 검색, LangGraph 챗봇 API를 하나의 FastAPI "
            "인스턴스(포트 9600)에 통합 제공합니다."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Apply uniform CORS rules (individual apps attached as routers won't bring theirs)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Reuse routers from the standalone apps so their endpoints remain the same.
    app.include_router(
        consumption_app.router,
        tags=["consumption-analysis"],
    )
    app.include_router(
        card_benefit_app.router,
        tags=["card-benefits"],
    )
    app.include_router(
        chatbot_app.router,
        tags=["chatbot"],
    )

    @app.get("/healthz", tags=["meta"])
    def healthz() -> Dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "9600")),
        reload=bool(os.getenv("UVICORN_RELOAD", "")),
    )
