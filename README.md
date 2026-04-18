# DocuVerse

A self-hosted, RAG-powered document Q&A backend. Upload a PDF, ask questions, get answers grounded in the document — streamed token by token.

Built with FastAPI, Pinecone, NVIDIA NIM, and a parent-child chunking architecture designed for retrieval quality over raw recall.

---

## What It Does

- **Auth** — Email + OTP-verified registration, JWT access/refresh token lifecycle
- **Document Ingestion** — PDF → text extraction → parent/child chunking → dense embeddings → Pinecone upsert
- **Retrieval** — Dense vector search + FlashRank cross-encoder reranking → hydrated parent chunks
- **Chat** — Query expansion → hybrid retrieval → streaming SSE response via NVIDIA NIM LLM
- **Concurrency Safety** — Redis distributed lock per document prevents concurrent chat collisions across devices

---

## Architecture

```
User Query
    │
    ├─► Query Expansion (LLaMA 3.1 8B) — rephrase for better retrieval recall
    │
    ├─► Pinecone Dense Search (all-MiniLM-L6-v2, top_k=20, namespace=user_id)
    │
    ├─► FlashRank Cross-Encoder Reranking (ms-marco-MiniLM-L-12-v2, top_n=5)
    │
    ├─► Parent Chunk Hydration (MySQL — fetch full parent text by parent_index)
    │
    └─► LLM Answer Generation (Mistral Large, streaming SSE)
```

### Chunking Strategy

Documents are split into two levels stored separately:

| Level | Size | Purpose |
|---|---|---|
| **Parent chunks** | ~1000 chars | Stored in MySQL. Sent to LLM as context. Large enough for coherent answers. |
| **Sub-chunks** | ~200 chars | Embedded and indexed in Pinecone. Small enough for precise semantic retrieval. |

Sub-chunks carry a `parent_index` FK. After retrieval and reranking, the matched sub-chunks are used only to identify their parent — the full parent text is what reaches the LLM.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI + Uvicorn |
| **Database** | MySQL + SQLAlchemy ORM |
| **Vector Store** | Pinecone (dotproduct metric, 384-dim) |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` (local, CPU) |
| **Reranker** | FlashRank `ms-marco-MiniLM-L-12-v2` (local, CPU) |
| **LLM** | NVIDIA NIM — Mistral Large (generation), LLaMA 3.1 8B (query expansion) |
| **Storage** | AWS S3 (PDF storage) |
| **Cache / Lock** | Redis (distributed chat lock) |
| **Auth** | JWT (access + refresh tokens), bcrypt password hashing |
| **Package Manager** | `uv` |

---

## Prerequisites

- Python 3.12+
- MySQL running locally or remotely
- Redis running locally (`redis-cli ping` → `PONG`)
- AWS account with an S3 bucket
- NVIDIA NIM API key ([build.nvidia.com](https://build.nvidia.com))
- Pinecone account + index (dotproduct metric, 384 dimensions)

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd DocuVerse
uv sync
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/docuverse

# JWT
JWT_SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=your_bucket_name

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=docuverse-index

# NVIDIA NIM
NVIDIA_API_KEY=your_nvidia_api_key

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# App
ALLOWED_DOCUMENT_COUNT=10
LOG_LEVEL=INFO
LOG_TO_FILE=false
```

### 3. Set up the database

```bash
# Create the database
mysql -u root -p -e "CREATE DATABASE docuverse;"

# Run migrations (SQLAlchemy auto-creates tables on startup via base.py)
uv run python -c "from app.db.base import Base; from app.db.database import engine; Base.metadata.create_all(engine)"
```

### 4. Verify Pinecone index

Your Pinecone index must be created with:
- **Dimensions:** `384`
- **Metric:** `dotproduct`

```bash
uv run python -c "
from pinecone import Pinecone
from app.config.config import settings
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
print(pc.Index(settings.PINECONE_INDEX_NAME).describe_index_stats())
"
```

### 5. Run the server

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API is now available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Project Structure

```
DocuVerse/
├── main.py                        # Entry point — Uvicorn + logging setup
├── app/
│   ├── app.py                     # FastAPI app factory, router registration
│   ├── config/
│   │   └── config.py              # Pydantic settings (reads .env)
│   ├── db/
│   │   ├── database.py            # SQLAlchemy engine + session
│   │   └── base.py                # Declarative base (imports all models)
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── audit_base.py          # created_at, updated_at, created_by, updated_by
│   │   ├── user_model.py
│   │   ├── otp_model.py
│   │   ├── document_model.py
│   │   ├── document_chunk_model.py  # Parent chunks (MySQL)
│   │   └── chat_model.py
│   ├── repositories/              # DB access layer (raw SQLAlchemy queries)
│   │   ├── user_repository.py
│   │   ├── otp_repository.py
│   │   ├── document_repository.py
│   │   ├── document_chunk_repository.py
│   │   └── chat_repository.py
│   ├── services/                  # Business logic layer
│   │   ├── user_service.py
│   │   ├── otp_service.py
│   │   ├── file_service.py        # S3 upload/download
│   │   ├── document_service.py    # Ingestion pipeline orchestration
│   │   ├── embedding_service.py   # Encode + Pinecone upsert/delete
│   │   ├── reranker_service.py    # FlashRank cross-encoder
│   │   ├── retrieval_service.py   # Full retrieval pipeline
│   │   ├── llm_service.py         # NVIDIA NIM — query expansion + generation
│   │   └── chat_service.py        # Stream orchestration + Redis lock
│   ├── routing/                   # FastAPI routers
│   │   ├── user_router.py
│   │   ├── otp_router.py
│   │   ├── file_upload_router.py
│   │   ├── document_router.py
│   │   └── hello_router.py
│   ├── schemas/                   # Pydantic request/response models
│   │   ├── user_schemas.py
│   │   ├── otp_schemas.py
│   │   ├── document_schemas.py
│   │   ├── chunk_schemas.py
│   │   ├── vector_schemas.py
│   │   ├── retrieval_schemas.py
│   │   ├── rerank_schemas.py
│   │   ├── chat_schemas.py
│   │   └── base_response.py
│   ├── exceptions/                # Typed app exceptions + global handler
│   │   ├── base_exception.py
│   │   ├── user_exceptions.py
│   │   ├── document_exception.py
│   │   ├── chat_exception.py
│   │   ├── otp_exception.py
│   │   ├── s3_exceptions.py
│   │   ├── common_exception.py
│   │   └── handler.py
│   ├── enums/
│   │   ├── chat_roles.py
│   │   ├── jwt_enums.py
│   │   ├── otp_operation_type.py
│   │   ├── row_status.py
│   │   └── user_types.py
│   ├── utils/
│   │   ├── chunking_utils.py      # Parent + sub-chunk splitting
│   │   ├── pdf_utils.py           # PDF → text (via presigned S3 URL)
│   │   ├── s3_utils.py            # Presigned URL generation
│   │   ├── jwt_utils.py           # Token encode/decode
│   │   ├── password_utils.py      # bcrypt hash/verify
│   │   ├── redis_utils.py         # Distributed chat lock (acquire/release)
│   │   ├── logging_utils.py       # Centralised logging setup
│   │   └── string_generation.py   # OTP generation
│   └── api/
│       └── dependency.py          # FastAPI auth dependency (JWT extraction)
├── pyproject.toml
└── uv.lock
```

---

## API Overview

Full documentation → [`API_DOCUMENTATION.md`](./API_DOCUMENTATION.md)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/user/register` | No | Register a new user |
| `POST` | `/user/login` | No | Login, receive JWT tokens |
| `POST` | `/user/refresh` | Refresh token | Rotate tokens |
| `GET` | `/user/profile` | Access token | Get current user |
| `POST` | `/otp/request-otp` | No | Send OTP to email |
| `POST` | `/otp/verify` | No | Verify OTP, activate account |
| `POST` | `/upload/` | Access token | Upload PDF to S3 |
| `GET` | `/upload/presigned-url` | Access token | Get temporary file URL |
| `POST` | `/document/` | Access token | Ingest document (triggers full pipeline) |
| `POST` | `/chat/{document_id}/stream` | Access token | Stream SSE answer |
| `GET` | `/chat/{document_id}/history` | Access token | Fetch chat history |

### SSE Stream Events

The chat endpoint returns a `text/event-stream` response. Parse `data:` prefixed lines:

| Token | Meaning |
|---|---|
| Any text | Append to AI bubble |
| `[DONE]` | Stream complete |
| `[LOCKED] ...` | Another device is using this chat |
| `[ERROR] ...` | Server-side failure — show retry |

---

## Key Design Decisions

### Dense-Only Pinecone Retrieval

Sparse BM25 vectors are stored at upsert time using per-batch corpus indices (positions 0..n-1). These indices cannot be reproduced at query time without the exact same corpus, making hybrid Pinecone queries unreliable across batches. The sparse scores would be meaningless noise. Dense-only retrieval is used instead — the FlashRank cross-encoder reranker compensates for the recall gap that sparse search would have provided.

**Upgrade path:** Replace `rank_bm25` with Pinecone's `BM25Encoder` (pinecone-text), which maintains a persistent vocabulary and produces stable sparse indices across batches.

### Parent-Child Chunking (Small-to-Big Retrieval)

Retrieval precision and generation quality pull in opposite directions. Small chunks retrieve precisely; large chunks give the LLM enough context to answer well. The two-level split resolves this: sub-chunks handle precision at search time, parent chunks handle quality at generation time.

### Redis Chat Lock

Only one active streaming session is permitted per `document_id` at a time. The lock is a UUID-valued Redis key with a 120s TTL. UUID ownership prevents a race where one session releases another session's lock. TTL prevents permanent lock if the server crashes mid-stream. The lock is always released in a `finally` block.

### Atomic DB Commit

User message and assistant message are both written in the same transaction, committed only after the full response is accumulated. If generation fails mid-stream, both messages are rolled back together — no orphaned user messages without a corresponding AI response.

---

## Development Notes

```bash
# Run with auto-reload
uv run uvicorn main:app --reload

# Check Redis connection
redis-cli -a your_password ping

# Check Pinecone index stats
uv run python -c "
from app.services.embedding_service import _index
print(_index.describe_index_stats())
"

# Interactive API docs
open http://localhost:8000/docs
```

---

## Known Limitations

- **No document deletion endpoint** — orphan vectors remain in Pinecone after a document is deleted from MySQL. `EmbeddingService.delete_document_vectors()` exists and can be wired to a DELETE route.
- **Single-user Pinecone namespace per user** — all documents for a user share one namespace. Cross-document search is possible but not exposed in the current API.
- **PDF only** — other document types (DOCX, TXT) are not supported in the current ingestion pipeline.
- **No password reset flow** — OTP infrastructure supports it (`operation_type` enum is extensible) but the endpoint is not implemented.

---

*DocuVerse Backend — FastAPI / Python 3.12*