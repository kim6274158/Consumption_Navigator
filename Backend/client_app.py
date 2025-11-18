#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI client that connects to the Transaction MCP server via langchain-mcp-adapters
and reproduces the LangChain-based consumption analysis API.
"""
from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.types import CallToolResult, Content
from pydantic import BaseModel
import uvicorn

from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "소비 내역 분석 API (MCP Client)"
APP_DESCRIPTION = (
    "LangChain + langchain-mcp-adapters를 사용하여 MCP 서버로부터 "
    "거래 데이터를 가져와 분석합니다."
)

MCP_SERVER_ID = "transaction_db"
MCP_TRANSPORT = os.getenv("MCP_CLIENT_TRANSPORT", "stdio")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MCP_SERVER_PATH = os.path.join(BASE_DIR, "mcp_server.py")

# Configure MCP connection
if MCP_TRANSPORT == "streamable_http":
    SERVER_CONNECTIONS = {
        MCP_SERVER_ID: {
            "transport": "streamable_http",
            "url": os.getenv("MCP_SERVER_URL", "http://localhost:3000/mcp"),
            "headers": json.loads(os.getenv("MCP_SERVER_HEADERS", "{}")),
        }
    }
else:
    MCP_COMMAND = os.getenv("MCP_SERVER_COMMAND", "python")
    MCP_ARGS = json.loads(
        os.getenv("MCP_SERVER_ARGS", f'["{DEFAULT_MCP_SERVER_PATH}"]')
    )
    SERVER_CONNECTIONS = {
        MCP_SERVER_ID: {
            "transport": "stdio",
            "command": MCP_COMMAND,
            "args": MCP_ARGS,
            "env": {
                "PYTHONPATH": os.getenv("PYTHONPATH", ""),
            },
        }
    }


class ConsumptionAnalysisRequest(BaseModel):
    account_id: Optional[int] = None
    fintech_use_num: Optional[str] = None


class MCPToolInvoker:
    """
    Helper to call MCP server tools using a shared MultiServerMCPClient.
    """

    def __init__(self, client: MultiServerMCPClient, server_id: str):
        self.client = client
        self.server_id = server_id
        self._lock = asyncio.Lock()

    @asynccontextmanager
    async def session(self):
        async with self.client.session(self.server_id) as session:
            yield session

    async def call_tool(self, tool_name: str, **arguments) -> Any:
        async with self._lock:
            async with self.session() as session:
                result = await session.call_tool(tool_name, arguments=arguments)
                return self._extract_content(result)

    @staticmethod
    def _extract_content(result: CallToolResult) -> Any:
        contents: List[Any] = []
        for item in getattr(result, "content", []):
            contents.append(MCPToolInvoker._decode_content(item))

        if not contents:
            return None
        if len(contents) == 1:
            return contents[0]
        return contents

    @staticmethod
    def _decode_content(item: Content) -> Any:
        if hasattr(item, "text") and item.text is not None:
            text = item.text.strip()
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return text
        if hasattr(item, "json") and getattr(item, "json") is not None:
            json_attr = getattr(item, "json")
            if callable(json_attr):
                raw = json_attr()
            else:
                raw = json_attr
            return raw
        if hasattr(item, "data"):
            return item.data
        return None


mcp_client = MultiServerMCPClient(SERVER_CONNECTIONS)
mcp_invoker = MCPToolInvoker(mcp_client, MCP_SERVER_ID)

llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY"),
)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_account(account_id: Optional[int], fintech_use_num: Optional[str]) -> Optional[Dict[str, Any]]:
    args: Dict[str, Any] = {"limit": 1}
    if account_id is not None:
        args["account_id"] = account_id
    if fintech_use_num:
        args["fintech_use_num"] = fintech_use_num

    records = await mcp_invoker.call_tool("get_account_balance_records", **args)
    if isinstance(records, list) and records:
        return records[0]
    if isinstance(records, dict):
        return records
    return None


async def fetch_transactions(fintech_use_num: str, limit: int = 100) -> List[Dict[str, Any]]:
    args = {"fintech_use_num": fintech_use_num, "limit": limit}
    records = await mcp_invoker.call_tool("get_transaction_records", **args)
    if isinstance(records, list):
        return records
    if records is None:
        return []
    return [records]


async def get_basic_analysis(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not transactions:
        return {
            "total_transactions": 0,
            "total_income": 0,
            "total_expense": 0,
            "message": "거래 내역이 없습니다.",
        }

    total_income = 0
    total_expense = 0
    income_count = 0
    expense_count = 0

    for t in transactions:
        amt = t.get("tran_amt") or 0
        inout_type = t.get("inout_type", "")

        if inout_type == "입금":
            total_income += amt
            income_count += 1
        elif inout_type == "출금":
            total_expense += amt
            expense_count += 1

    return {
        "total_transactions": len(transactions),
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "income_count": income_count,
        "expense_count": expense_count,
    }


def build_prompts(account_info: Dict[str, Any], transactions: List[Dict[str, Any]]) -> Dict[str, str]:
    account_summary = (
        "계좌 정보:\n"
        f"- 은행: {account_info.get('bank_name', 'N/A')}\n"
        f"- 상품명: {account_info.get('product_name', 'N/A')}\n"
        f"- 잔액: {account_info.get('balance_amt', '0')}원\n"
        f"- 출금가능액: {account_info.get('available_amt', '0')}원\n"
        f"- 계좌유형: {account_info.get('account_type', 'N/A')}\n"
    )

    transaction_text = "\n".join(
        [
            f"- {t.get('tran_date', '')} {t.get('tran_time', '')}: "
            f"{t.get('inout_type', '')} {t.get('tran_type', '')} "
            f"{t.get('printed_content', '')} {t.get('tran_amt', 0)}원"
            for t in transactions[:50]
        ]
    )

    system_prompt = """당신은 금융 데이터 분석 전문가입니다.
사용자의 계좌 잔액과 거래 내역을 분석하여 소비 패턴을 파악하고
유용한 인사이트를 제공해야 합니다.

다음 항목들을 분석해주세요:
1. 소비 패턴 (주요 지출 카테고리, 빈도, 특징)
2. 수입 패턴 (주요 수입원, 빈도)
3. 잔액 변화 추이
4. 개선 제안사항 및 절약 팁

한국어로 친절하고 구체적으로 답변해주세요.
분석 결과를 자연스러운 문장으로 작성해주세요."""

    user_prompt = (
        f"{account_summary}\n\n최근 거래 내역:\n{transaction_text}\n\n"
        "위 정보를 바탕으로 현재 소비 내역을 분석하고 인사이트를 제공해주세요."
    )

    return {"system": system_prompt, "user": user_prompt}


async def run_reflexion_cycle(
    account_info: Dict[str, Any],
    transactions: List[Dict[str, Any]],
    prompts: Dict[str, str],
) -> Dict[str, str]:
    """Run a single Reflexion-style refinement loop (draft -> reflect -> revise)."""
    base_messages = [
        SystemMessage(content=prompts["system"]),
        HumanMessage(content=prompts["user"]),
    ]

    draft_response = await llm.ainvoke(base_messages)
    draft_text = getattr(draft_response, "content", str(draft_response))

    reflection_system = (
        "너는 엄격한 금융 데이터 리뷰어다. 아래 초안을 보고 잘된 점과 부족한 점을 "
        "명시적으로 지적하고, 누락된 통찰·숫자·근거를 제안하라. 반드시 JSON으로 반환하라."
    )
    reflection_user = json.dumps(
        {
            "account_info": account_info,
            "sample_transactions": transactions[:20],
            "draft": draft_text,
            "required_topics": [
                "소비 패턴 품질",
                "수입 패턴 품질",
                "잔액 추이 분석",
                "개선 제안 구체성",
            ],
        },
        ensure_ascii=False,
    )
    reflection = await llm.ainvoke(
        [
            SystemMessage(content=reflection_system),
            HumanMessage(content=reflection_user),
        ]
    )
    reflection_text = getattr(reflection, "content", str(reflection))

    revision_system = (
        "너는 금융 컨설턴트다. 아래 기초 데이터와 초안, 그리고 리뷰어 피드백을 바탕으로 "
        "최종 보고서를 다시 작성하라. 피드백의 개선 사항을 모두 반영하고, 필요한 숫자를 "
        "거래 데이터에서 찾아 정리하라."
    )
    revision_user = json.dumps(
        {
            "account_info": account_info,
            "transactions": transactions[:50],
            "draft": draft_text,
            "reflection": reflection_text,
        },
        ensure_ascii=False,
    )
    revised = await llm.ainvoke(
        [
            SystemMessage(content=revision_system),
            HumanMessage(content=revision_user),
        ]
    )
    final_text = getattr(revised, "content", str(revised))

    return {
        "draft": draft_text,
        "reflection": reflection_text,
        "final": final_text,
    }


@app.post("/analyze")
async def analyze_consumption(request: ConsumptionAnalysisRequest):
    account_info = await fetch_account(request.account_id, request.fintech_use_num)
    if not account_info:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다.")

    fintech_use_num = account_info.get("fintech_use_num")
    transactions = await fetch_transactions(fintech_use_num, limit=100)

    prompts = build_prompts(account_info, transactions)

    try:
        reflexion_outputs = await run_reflexion_cycle(
            account_info, transactions, prompts
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=f"LLM 분석 오류: {exc}") from exc

    basic_stats = await get_basic_analysis(transactions)

    return {
        "account_info": {
            "bank_name": account_info.get("bank_name"),
            "product_name": account_info.get("product_name"),
            "balance_amt": account_info.get("balance_amt"),
            "available_amt": account_info.get("available_amt"),
        },
        "transaction_count": len(transactions),
        "basic_analysis": basic_stats,
        "llm_analysis": {
            "draft": reflexion_outputs["draft"],
            "reflection": reflexion_outputs["reflection"],
            "final": reflexion_outputs["final"],
        },
        "methodology": "Reflexion loop inspired by LangChain reflection agents",
    }


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "9600")))
