#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain을 활용한 잔액조회 기반 소비 내역 분석 API 서버
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import pymysql
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# DB 설정
DB_CONFIG = {
    "host": "zini-deploy.cx802ygucfor.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "nice1234!!",
    "database": "transaction_mockup",
    "charset": "utf8mb4",
    "port": 3306,
}

# FastAPI 앱 초기화
app = FastAPI(
    title="소비 내역 분석 API",
    description="LangChain을 활용한 잔액조회 기반 소비 내역 분석 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangChain LLM 초기화 - GPT-4o 모델 사용
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.3,
    api_key=os.getenv("OPENAI_API_KEY")
)
print("✅ LangChain LLM 초기화 완료 (GPT-4o)")

# Pydantic 모델


class AccountBalanceResponse(BaseModel):
    id: int
    fintech_use_num: Optional[str]
    bank_name: Optional[str]
    product_name: Optional[str]
    balance_amt: Optional[str]
    available_amt: Optional[str]
    account_type: Optional[str]
    last_tran_date: Optional[str]


class TransactionResponse(BaseModel):
    id: int
    tran_date: Optional[str]
    tran_time: Optional[str]
    inout_type: Optional[str]
    tran_type: Optional[str]
    printed_content: Optional[str]
    tran_amt: Optional[int]
    after_balance_amt: Optional[int]
    branch_name: Optional[str]


class ConsumptionAnalysisRequest(BaseModel):
    fintech_use_num: Optional[str] = None
    account_id: Optional[int] = None


class ConsumptionAnalysisResponse(BaseModel):
    account_info: Dict[str, Any]
    transactions: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    summary: str


# DB 연결 헬퍼 함수
def get_db_connection():
    """DB 연결 반환"""
    return pymysql.connect(**DB_CONFIG)


# 잔액조회 데이터 조회
def get_account_balance(fintech_use_num: Optional[str] = None, account_id: Optional[int] = None):
    """잔액조회 데이터 조회"""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            if account_id:
                sql = "SELECT * FROM account_balance WHERE id = %s"
                cur.execute(sql, (account_id,))
            elif fintech_use_num:
                sql = "SELECT * FROM account_balance WHERE fintech_use_num = %s ORDER BY created_at DESC LIMIT 1"
                cur.execute(sql, (fintech_use_num,))
            else:
                sql = "SELECT * FROM account_balance ORDER BY created_at DESC LIMIT 1"
                cur.execute(sql)

            result = cur.fetchone()
            return result
    finally:
        conn.close()


# 거래내역 조회
def get_transactions(fintech_use_num: Optional[str] = None, limit: int = 50):
    """거래내역 조회"""
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            if fintech_use_num:
                sql = """
                    SELECT * FROM transactions 
                    WHERE fintech_use_num = %s 
                    ORDER BY tran_datetime DESC 
                    LIMIT %s
                """
                cur.execute(sql, (fintech_use_num, limit))
            else:
                sql = """
                    SELECT * FROM transactions 
                    ORDER BY tran_datetime DESC 
                    LIMIT %s
                """
                cur.execute(sql, (limit,))

            results = cur.fetchall()
            return results
    finally:
        conn.close()


# 기본 분석 (LLM 없이)
def get_basic_analysis(account_info: Dict, transactions: List[Dict]) -> Dict[str, Any]:
    """기본 통계 분석"""
    if not transactions:
        return {
            "total_transactions": 0,
            "total_income": 0,
            "total_expense": 0,
            "message": "거래 내역이 없습니다."
        }

    total_income = 0
    total_expense = 0
    income_count = 0
    expense_count = 0
    expense_categories = {}

    for t in transactions:
        amt = t.get('tran_amt', 0) or 0
        inout_type = t.get('inout_type', '')

        if inout_type == '입금':
            total_income += amt
            income_count += 1
        elif inout_type == '출금':
            total_expense += amt
            expense_count += 1
            # 지출 카테고리 분류
            content = t.get('printed_content', '')
            if content:
                category = categorize_expense(content)
                expense_categories[category] = expense_categories.get(
                    category, 0) + amt

    # 상위 지출 카테고리
    top_categories = sorted(
        expense_categories.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    return {
        "total_transactions": len(transactions),
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "income_count": income_count,
        "expense_count": expense_count,
        "top_expense_categories": [{"category": k, "amount": v} for k, v in top_categories],
        "average_expense": total_expense / expense_count if expense_count > 0 else 0,
        "average_income": total_income / income_count if income_count > 0 else 0,
    }


def categorize_expense(content: str) -> str:
    """거래 내용을 기반으로 카테고리 분류"""
    content_lower = content.lower()

    if any(word in content_lower for word in ['급여', '월급', '연봉']):
        return "급여"
    elif any(word in content_lower for word in ['월세', '전세', '임대료', '관리비']):
        return "주거비"
    elif any(word in content_lower for word in ['통신비', '전화', '인터넷']):
        return "통신비"
    elif any(word in content_lower for word in ['보험료', '보험']):
        return "보험"
    elif any(word in content_lower for word in ['카드', '결제', '신용카드']):
        return "카드결제"
    elif any(word in content_lower for word in ['이체', '송금']):
        return "이체"
    elif any(word in content_lower for word in ['atm', '출금']):
        return "현금출금"
    elif any(word in content_lower for word in ['공과금', '전기', '가스', '수도']):
        return "공과금"
    else:
        return "기타"


# API 엔드포인트 - 소비 내역 분석 API 하나만 제공
@app.post("/analyze")
async def analyze_consumption(
    account_id: Optional[int] = None,
    fintech_use_num: Optional[str] = None
):
    """
    잔액조회 기반 소비 내역 분석 API

    - account_id: 계좌 ID (선택사항)
    - fintech_use_num: 핀테크이용번호 (선택사항)

    둘 다 없으면 최근 계좌를 조회합니다.
    """
    # 계좌 정보 조회
    account_info = get_account_balance(
        fintech_use_num=fintech_use_num,
        account_id=account_id
    )

    if not account_info:
        raise HTTPException(status_code=404, detail="계좌를 찾을 수 없습니다.")

    # 거래내역 조회
    fintech_use_num = account_info.get('fintech_use_num')
    transactions = get_transactions(fintech_use_num=fintech_use_num, limit=100)

    # GPT-4o로 소비 패턴 분석
    if not llm:
        raise HTTPException(status_code=500, detail="LLM이 초기화되지 않았습니다.")

    # 거래내역을 텍스트로 변환
    transaction_text = "\n".join([
        f"- {t.get('tran_date', '')} {t.get('tran_time', '')}: "
        f"{t.get('inout_type', '')} {t.get('tran_type', '')} "
        f"{t.get('printed_content', '')} {t.get('tran_amt', 0):,}원"
        for t in transactions[:50]  # 최근 50건 분석
    ])

    # 계좌 정보 요약
    account_summary = f"""
계좌 정보:
- 은행: {account_info.get('bank_name', 'N/A')}
- 상품명: {account_info.get('product_name', 'N/A')}
- 잔액: {account_info.get('balance_amt', '0')}원
- 출금가능액: {account_info.get('available_amt', '0')}원
- 계좌유형: {account_info.get('account_type', 'N/A')}
"""

    # GPT-4o 프롬프트
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

    user_prompt = f"""
{account_summary}

최근 거래 내역:
{transaction_text}

위 정보를 바탕으로 현재 소비 내역을 분석하고 인사이트를 제공해주세요.
"""

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        response = llm.invoke(messages)

        # 응답 추출
        if hasattr(response, 'content'):
            analysis_text = response.content
        else:
            analysis_text = str(response)

        return {
            "account_info": {
                "bank_name": account_info.get('bank_name'),
                "product_name": account_info.get('product_name'),
                "balance_amt": account_info.get('balance_amt'),
                "available_amt": account_info.get('available_amt'),
            },
            "transaction_count": len(transactions),
            "analysis": analysis_text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9500)
