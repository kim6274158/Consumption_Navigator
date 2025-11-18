#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph 기반 단기/장기 메모리가 결합된 챗봇 API.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from pydantic import BaseModel

load_dotenv()


# ---------------- Long-term memory manager ---------------- #
class LongTermMemoryManager:
    """
    매우 단순한 JSON 기반 장기 기억 저장소.
    실제 서비스라면 Postgres/Mongo 등을 사용하는 것이 권장된다.
    """

    def __init__(self, path: str = "long_term_memory.json", max_entries: int = 20):
        self.path = Path(path)
        self.max_entries = max_entries
        self._lock = threading.Lock()
        self._store: Dict[str, List[Dict[str, str]]] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._store = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._store = {}
        else:
            self._store = {}

    def _save(self) -> None:
        self.path.write_text(json.dumps(
            self._store, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_context(self, user_id: str) -> str:
        with self._lock:
            entries = self._store.get(user_id, [])
            if not entries:
                return ""
            return "\n".join(
                f"- 사용자: {item['user']}\n  응답: {item['assistant']}"
                for item in entries
            )

    def append(self, user_id: str, user_message: str, assistant_message: str) -> None:
        with self._lock:
            history = self._store.setdefault(user_id, [])
            history.append(
                {"user": user_message, "assistant": assistant_message})
            if len(history) > self.max_entries:
                del history[:-self.max_entries]
            self._save()


long_term_memory = LongTermMemoryManager()


# ---------------- LangGraph setup ---------------- #
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY"),
)

checkpointer = InMemorySaver()


def build_graph():
    builder = StateGraph(MessagesState)

    def call_model(state: MessagesState, config: Optional[dict] = None):
        config = config or {}
        thread_id = config.get("configurable", {}).get(
            "thread_id", "anonymous")

        long_term_context = long_term_memory.get_context(thread_id)
        enriched_messages = list(state["messages"])
        if long_term_context:
            enriched_messages = [
                SystemMessage(
                    content=(
                        "아래는 사용자의 장기 기억입니다. 해당 내용이 대화와 관련 있다면 활용하세요.\n"
                        f"{long_term_context}"
                    )
                )
            ] + enriched_messages

        response = llm.invoke(enriched_messages)

        user_utterance = ""
        for msg in reversed(state["messages"]):
            if isinstance(msg, HumanMessage):
                user_utterance = msg.content
                break
        long_term_memory.append(thread_id, user_utterance, response.content)

        return {"messages": response}

    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile(checkpointer=checkpointer)


graph = build_graph()


# ---------------- FastAPI ---------------- #
app = FastAPI(
    title="LangGraph Memory Chatbot",
    description="단기 메모리(스레드) + 장기 메모리를 지원하는 LangGraph 챗봇 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message가 비어있습니다.")

    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = graph.invoke(
        {"messages": [HumanMessage(content=request.message)]}, config)
    reply = result["messages"][-1].content

    return {
        "thread_id": request.thread_id,
        "reply": reply,
        "short_term_memory": "active",
        "long_term_context": long_term_memory.get_context(request.thread_id),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(
        os.getenv("CHATBOT_PORT", "9700")))
