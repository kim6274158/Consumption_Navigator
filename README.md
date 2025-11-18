# Unified Transaction APIs

`main_api.py` exposes three previously separate FastAPI services on a single
Uvicorn process (`0.0.0.0:9600` by default):

1. 소비 내역 분석 API (`client_app.py`)
2. 카드 혜택 하이브리드 검색 API (`card_benefit_api.py`)
3. LangGraph 메모리 챗봇 API (`chatbot_api.py`)

이 문서는 각 API의 핵심 기능, 주요 환경 변수, 그리고 Request/Response 예시를 정리합니다.

---

## 1. 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 필요 환경 변수 (예: OpenAI, MCP 등)
export OPENAI_API_KEY=sk-...
export MCP_SERVER_COMMAND=python
export MCP_SERVER_ARGS='["mcp_server.py"]'

# 통합 서버 실행
python main_api.py
# 또는
uvicorn main_api:app --host 0.0.0.0 --port 9600 --reload
```

Swagger UI: `http://<호스트>:9600/docs`  
ReDoc: `http://<호스트>:9600/redoc`

---

## 2. 소비 내역 분석 API (`POST /analyze`)

- MCP 서버를 통해 계좌·거래 정보를 가져와 LangChain Reflexion 루프(초안 → 리뷰 → 수정)로 인사이트를 생성합니다.
- LLM 없이도 기본 통계(거래 수, 총입·출금 등)를 포함합니다.

### Request Body

```json
{
  "account_id": 1,
  "fintech_use_num": "120190910000000000000001"
}
```

둘 중 하나만 제공해도 됩니다. `account_id` 가 우선 사용되며, 없으면 `fintech_use_num`로 조회합니다.

### Response 예시

```json
{
  "account_info": {
    "bank_name": "오픈은행",
    "product_name": "자유입출금통장",
    "balance_amt": "2547800",
    "available_amt": "2547800"
  },
  "transaction_count": 47,
  "basic_analysis": {
    "total_transactions": 47,
    "total_income": 3500000,
    "total_expense": 952200,
    "net_balance": 2547800,
    "income_count": 5,
    "expense_count": 42
  },
  "llm_analysis": {
    "draft": "...첫 번째 LLM 결과...",
    "reflection": "...JSON 피드백...",
    "final": "...수정된 최종 보고서..."
  },
  "methodology": "Reflexion loop inspired by LangChain reflection agents"
}
```

### 필수 환경 변수

- `OPENAI_API_KEY` – LangChain `ChatOpenAI` 호출용
- `MCP_CLIENT_TRANSPORT`, `MCP_SERVER_COMMAND`, `MCP_SERVER_ARGS` – MCP 연결 설정

---

## 3. 카드 혜택 하이브리드 검색 API (`POST /search`)

- `card_data/cardgorilla_top100_detailed.json` 데이터를 BGEM3(FP32)로 임베딩하여 Milvus Lite에 저장합니다.
- Dense + Sparse 하이브리드 검색과 RRF 재정렬을 통해 카드 혜택 문장을 찾아줍니다.
- Hugging Face 캐시는 `.hf_cache/`에 유지되어 최초 1회만 모델 파일을 다운로드합니다.

### Request Body

```json
{
  "query": "대중교통 할인 카드 추천",
  "top_k": 5
}
```

### Response 예시

```json
{
  "query": "대중교통 할인 카드 추천",
  "results": [
    {
      "score": 0.67,
      "rank": 1,
      "name": "모빌리티 Special",
      "issuer": "OO카드",
      "event_text": "신규 발급 이벤트 중...",
      "benefits_text": "대중교통 10% 할인; 택시 5% 적립; ..."
    }
  ]
}
```

### 관련 환경 변수

- `MILVUS_URI` (기본: `./card_benefits.db`)
- `BGE_DEVICE` (예: `"cuda"` 또는 `"cpu"`)
- `HF_HOME`, `TRANSFORMERS_CACHE` (지정하지 않으면 `.hf_cache/` 사용)

---

## 4. LangGraph 메모리 챗봇 API (`POST /chat`)

- LangGraph `StateGraph` 를 사용해 단기 메모리(대화 스레드)와 JSON 기반 장기 메모리를 결합합니다.
- `thread_id` 를 키로 하여 과거 대화 히스토리를 로딩/저장합니다.

### Request Body

```json
{
  "thread_id": "user-123",
  "message": "오늘 저녁 뭐 먹을까?"
}
```

### Response 예시

```json
{
  "thread_id": "user-123",
  "reply": "지난 번에 파스타를 좋아하셨으니...",
  "short_term_memory": "active",
  "long_term_context": "- 사용자: 지난 주엔 파스타 먹었다..."
}
```

### 관련 파일

- 장기 기억 저장소: `long_term_memory.json` (최대 20개 대화 저장)

---

## 5. Health Check

`GET /healthz` → `{"status": "ok"}`  
통합 서버의 기본 상태를 확인할 수 있습니다.

---

## 6. Troubleshooting

- **`Fetching 30 files` 가 오래 걸림**: BGEM3 모델 다운로드 중이며, `.hf_cache/` 디렉터리가 유지되면 재실행 시 발생하지 않습니다.
- **Milvus Lite 파일 잠금 오류**: `card_benefit_api` 는 FastAPI `startup` 이벤트에서만 Milvus 연결을 열도록 구성되어 있으니, `--reload` 모드에서도 단일 워커만 DB 파일을 잡습니다.
- **`/docs` 접근 불가**: `uvicorn main_api:app --host 0.0.0.0 --port 9600` 처럼 외부에서 접근 가능한 호스트로 실행하세요.

필요시 `README_API.md`의 소비 분석 세부 설명을 참고해 더 많은 파라미터를 확인할 수 있습니다.


