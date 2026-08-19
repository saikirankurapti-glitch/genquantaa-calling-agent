# GenQuantaa Calling Agent — Data Architecture & Schema Specification

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Data Specification  

---

## 1. Executive Summary

This document defines the comprehensive data architecture for **GenQuantaa Calling Agent**, covering the relational PostgreSQL database, the `pgvector` vector store, the Redis cache & message bus, and object storage systems.

---

## 2. PostgreSQL Relational Database Schema

The database uses PostgreSQL 17 managed via SQLAlchemy (AsyncIO) and Alembic migrations (`api/alembic/versions/*`).

```
                    +-------------------+
                    |   organizations   |
                    +---------+---------+
                              | 1
                              |
                              | N
                    +---------v---------+
                    |       users       |
                    +-------------------+

                    +-------------------+
                    |     workflows     |
                    +---------+---------+
                              | 1
                              |
             +----------------+----------------+
             | N                               | N
   +---------v---------+             +---------v---------+
   | workflow_versions |             |   workflow_runs   |
   +-------------------+             +---------+---------+
                                               | 1
                                               |
                                               | N
                                     +---------v---------+
                                     |    call_logs      |
                                     +-------------------+

                    +-------------------+
                    |  knowledge_bases  |
                    +---------+---------+
                              | 1
                              | N
                    +---------v---------+
                    |  kb_documents     | (pgvector 1536d)
                    +-------------------+
```

### Core Schema Tables

#### 2.1 Organizations & User Access
- **`organizations`**: Stores tenant identity, billing tier, concurrent call limits (`CONCURRENT_CALL_LIMIT`), telephony configuration (`TELEPHONY_CONFIGURATION`), and model settings.
- **`users`**: User profile, password hash (bcrypt), organization relationship, role (admin, member), and email verification status.
- **`user_configurations`**: Key-value JSON storage for per-user preferences and onboarding step states.

#### 2.2 Workflows & Agent Definitions
- **`workflows`**: Agent flow entity containing metadata, name, status (`active`, `archived`), and unique workflow UUID.
- **`workflow_versions`**: Immutable snapshots of published agent flow graphs. Contains JSON graph payload (`nodes`, `edges`, system prompt, LLM parameters, TTS parameters, attached tools).
- **`agent_triggers`**: Event triggers (inbound webhook, API call, schedule) associated with a workflow.

#### 2.3 Call Execution & History
- **`workflow_runs`**: Real-time call session state. Tracks `run_mode` (`ari`, `telnyx`, `twilio`, `webrtc`), state (`initialized`, `running`, `completed`), status, duration, start/end timestamps.
- **`call_logs`**: Detailed per-call analytics, turn-by-turn transcripts, latency measurements (STT latency, LLM TTFT, TTS latency), error stack traces, and S3 audio recording URIs.
- **`phone_numbers`**: DID phone numbers assigned to organizations and mapped to specific active workflows.
- **`telephony_configurations`**: Credentials for carrier trunks (Telnyx API keys, Twilio Account SIDs, Cloudonix trunks, Asterisk ARI settings).

#### 2.4 Campaign Management
- **`campaigns`**: Outbound calling batch jobs containing campaign schedule, target phone numbers list, and assigned workflow version.
- **`campaign_runs`**: Individual contact attempt executions within an outbound campaign.

---

## 3. Vector Database & RAG Architecture (`pgvector`)

### 3.1 Embedding Storage (`knowledge_base_documents`)
RAG (Retrieval-Augmented Generation) context injection is powered by the `pgvector` extension (v0.4.2 / PostgreSQL 17).

- **Table:** `knowledge_base_documents`
- **Vector Column:** `embedding vector(1536)` (Optimized for OpenAI `text-embedding-3-small` 1536-dimensional embeddings).
- **Metadata Columns:** `id`, `knowledge_base_id`, `file_name`, `chunk_index`, `content_text` (text chunk payload), `created_at`.

### 3.2 Indexing Strategy & Vector Similarity Queries
- **Index Type:** Hierarchical Navigable Small World (**HNSW**) cosine distance index.
```sql
CREATE INDEX idx_kb_documents_embedding_hnsw 
ON knowledge_base_documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```
- **Vector Search Execution:** During an active call, user speech is transcribed, converted to a query vector, and matched using cosine distance (`<=>` operator):
```sql
SELECT content_text, 1 - (embedding <=> :query_vector) AS similarity
FROM knowledge_base_documents
WHERE knowledge_base_id = :kb_id
ORDER BY embedding <=> :query_vector
LIMIT 3;
```

---

## 4. Redis Architecture & Data Structures

Redis 7 serves as the high-throughput cache, state lock manager, and asynchronous job broker.

### 4.1 Pub/Sub Channels
- **`campaign_events`**: Real-time progress updates for outbound campaign orchestrator broadcasted to UI via WebSockets.
- **`worker_sync`**: Cluster worker synchronization and concurrent call limit cache invalidation.

### 4.2 ARQ Task Queue (`api/tasks/*`)
- **Queue Key Prefix:** `arq:queue`
- **Task Types:** `process_outbound_call`, `execute_campaign_batch`, `parse_knowledge_base_document`, `generate_call_transcript_summary`.
- **Job Expiration & Retry:** Default job timeout 300s, max retries 3 with exponential backoff.

### 4.3 Key-Value Caching Patterns
- **Concurrent Call Lock:** `org:{org_id}:active_calls` (Atomic integer counter incremented/decremented on call start/stop).
- **Session Cache:** `session:{token_hash}` -> Serialized user session JSON with 24-hour TTL.
- **TTS Cache:** `tts:{provider}:{voice_id}:{text_hash}` -> Cached synthesized audio frames to reduce latency & API costs.

---

## 5. Object Storage Architecture (MinIO / S3)

### 5.1 Storage Bucket Configuration
- **Primary Bucket Name:** `genquantaa-voice-audio` (Legacy reference: `voice-audio`).
- **Storage Driver:** MinIO (Local OSS deployment) / AWS S3 (Production cloud deployment).

### 5.2 Folder Taxonomy
```
genquantaa-voice-audio/
├── recordings/
│   └── {org_id}/
│       └── {workflow_run_id}.wav      # Raw dual-channel call recording
├── knowledge_bases/
│   └── {org_id}/
│       └── {kb_id}/
│           └── {doc_id}.pdf            # Original source PDF/Docx files
└── tts_cache/
    └── {hash}.mp3                      # Pre-rendered prompt audio clips
```

### 5.3 Security & Presigned URLs
- **Presigned Expiry:** 3600 seconds (1 hour) for secure browser playback in dashboard call logs.
- **S3 Signing:** S3 SigV4 signature format with configurable `S3_ADDRESSING_STYLE="path"`.

---

## 6. Target GenQuantaa Schema Isolation & Migrations

To completely isolate GenQuantaa Calling Agent from the legacy fork:
1. **Alembic Migration Tag:** Add Alembic migration `V2.0.0__genquantaa_rebrand.py` updating default organization seeds.
2. **PostgreSQL Database Rename:** Change default database name from `postgres` to `genquantaa_db`.
3. **Redis Key Namespacing:** Prefix all Redis keys with `gq:` (e.g. `gq:org:{id}:active_calls`).
4. **MinIO Bucket Isolation:** Create bucket `genquantaa-voice-audio` on container startup via `run_dograh_init.sh` -> `run_genquantaa_init.sh`.
