#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP server exposing transaction DB tables as queryable tools.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence

import pymysql
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

DB_CONFIG = {
    "host": os.getenv(
        "DB_HOST", "zini-deploy.cx802ygucfor.ap-northeast-2.rds.amazonaws.com"
    ),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "nice1234!!"),
    "database": os.getenv("DB_NAME", "transaction_mockup"),
    "charset": "utf8mb4",
    "port": int(os.getenv("DB_PORT", "3306")),
}

mcp = FastMCP("TransactionDB")


def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


def run_query(sql: str, params: Sequence[Any]) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            return [normalize_row(row) for row in rows]
    finally:
        conn.close()


def normalize_row(row: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, bytes):
            normalized[key] = value.decode("utf-8")
        elif hasattr(value, "isoformat"):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized


def build_limit_clause(limit: Optional[int], default: int = 50) -> int:
    if limit is None:
        return default
    if limit <= 0:
        raise ValueError("limit must be a positive integer")
    return min(limit, 500)


@mcp.tool()
async def get_account_balance_records(
    account_id: Optional[int] = None,
    fintech_use_num: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve rows from the account_balance table.
    """
    params: List[Any] = []
    filters: List[str] = []

    if account_id is not None:
        filters.append("id = %s")
        params.append(account_id)

    if fintech_use_num:
        filters.append("fintech_use_num = %s")
        params.append(fintech_use_num)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    limited = build_limit_clause(limit, default=10)

    sql = f"""
        SELECT *
        FROM account_balance
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
    """
    params.append(limited)

    return run_query(sql, params)


@mcp.tool()
async def get_transaction_records(
    fintech_use_num: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve rows from the transactions table ordered by tran_datetime DESC.
    """
    params: List[Any] = []
    where_clause = ""
    if fintech_use_num:
        where_clause = "WHERE fintech_use_num = %s"
        params.append(fintech_use_num)

    limited = build_limit_clause(limit, default=50)
    params.append(limited)

    sql = f"""
        SELECT *
        FROM transactions
        {where_clause}
        ORDER BY tran_datetime DESC
        LIMIT %s
    """

    return run_query(sql, params)


@mcp.tool()
async def get_card_basic_info(
    fintech_use_num: Optional[str] = None,
    card_num: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve rows from the card_basic_info table.
    """
    params: List[Any] = []
    filters: List[str] = []

    if fintech_use_num:
        filters.append("fintech_use_num = %s")
        params.append(fintech_use_num)

    if card_num:
        filters.append("card_num = %s")
        params.append(card_num)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    limited = build_limit_clause(limit, default=5)
    params.append(limited)

    sql = f"""
        SELECT *
        FROM card_basic_info
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
    """

    return run_query(sql, params)


@mcp.tool()
async def get_card_list(
    fintech_use_num: Optional[str] = None,
    card_status: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Retrieve rows from the card_list table.
    """
    params: List[Any] = []
    filters: List[str] = []

    if fintech_use_num:
        filters.append("fintech_use_num = %s")
        params.append(fintech_use_num)

    if card_status:
        filters.append("card_status = %s")
        params.append(card_status)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    limited = build_limit_clause(limit, default=10)
    params.append(limited)

    sql = f"""
        SELECT *
        FROM card_list
        {where_clause}
        ORDER BY created_at DESC
        LIMIT %s
    """

    return run_query(sql, params)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")

    if transport == "streamable_http":
        port = int(os.getenv("MCP_HTTP_PORT", "3000"))
        host = os.getenv("MCP_HTTP_HOST", "0.0.0.0")
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        mcp.run()
