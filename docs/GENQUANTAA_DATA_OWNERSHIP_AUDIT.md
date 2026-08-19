# GenQuantaa Calling Agent — Data Ownership & Infrastructure Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document provides a comprehensive audit of the data layer components in GenQuantaa Calling Agent: PostgreSQL 17 (with `pgvector`), Redis 7, and MinIO S3 Object Storage.

---

## 2. PostgreSQL Infrastructure Audit

### 2.1 Database, Users & Credentials
- **Engine:** PostgreSQL 17 + `pgvector` vector extension (`pgvector/pgvector:pg17`).
- **Legacy Database Name:** `postgres`
- **Target GenQuantaa Database Name:** `genquantaa` (`GENQUANTAA_DB_NAME`)
- **Legacy User & Password:** `postgres` / `postgres`
- **Target GenQuantaa Credentials:** `GENQUANTAA_DB_USER` / `GENQUANTAA_DB_PASSWORD`
- **Connection Driver:** AsyncPG 0.30.0 (`postgresql+asyncpg://`)
- **ORM:** SQLAlchemy 2.0.43 (asyncio)

### 2.2 Relational Schema & Tables
- **`organizations`**: Multi-tenant organization boundaries, quotas (`CONCURRENT_CALL_LIMIT`), and integration configs.
- **`users`**: User identity records, password hashes (bcrypt), organization memberships.
- **`user_configurations`**: Per-user preferences and onboarding states.
- **`workflows`**: Agent flow entities containing workflow name, status (`active`, `archived`), and unique UUID.
- **`workflow_versions`**: Immutable snapshots of published agent flows (JSON payload of graph nodes, edges, prompt, LLM & TTS configuration).
- **`workflow_runs`**: Call execution sessions (`ari`, `telnyx`, `twilio`, `webrtc`), state (`initialized`, `running`, `completed`).
- **`call_logs`**: Detailed call records, transcripts, latency metrics, and audio recording S3 URIs.
- **`phone_numbers`**: Telecom DIDs assigned to organizations and workflows.
- **`telephony_configurations`**: Provider trunk credentials (Telnyx API keys, Twilio Account SIDs, Cloudonix trunks, Asterisk settings).
- **`campaigns` & `campaign_runs`**: Outbound call campaign batches and contact attempt state.
- **`knowledge_bases` & `knowledge_base_documents`**: Source PDF/Docx documents and 1536-dimensional vector embeddings (`pgvector`).
- **`tools`**: HTTP API tools and FastMCP catalog tools.
- **`agent_triggers`**: Webhook and scheduled trigger endpoints.

### 2.3 Alembic Migrations (`api/alembic/versions/*`)
- Migrations managed via `alembic` 1.16.5 + `alembic-postgresql-enum` 1.8.0.
- Migration runner reads `DATABASE_URL` at import time in `api/alembic/env.py`.

---

## 3. Redis Infrastructure Audit

### 3.1 Redis Usage & Driver
- **Engine:** Redis 7 (`redis:7`)
- **Python Driver:** `redis` 5.3.1
- **Target Namespace Prefix:** `GENQUANTAA_REDIS_PREFIX=gq:`

### 3.2 Asynchronous Job Queues (ARQ)
- **Queue Engine:** ARQ 0.26.3
- **Queue Keys:** `arq:queue` (Worker pool processes outbound calls, document parsing, and campaign batches).

### 3.3 Pub/Sub Channels
- **`campaign_events`**: Real-time campaign progress event stream broadcasted to UI.
- **`worker_sync`**: Inter-worker cache invalidation and credential sync protocol.

### 3.4 Key-Value Cache & Lock Patterns
- **Concurrent Call Counter:** `org:{id}:active_calls` -> Atomic integer lock.
- **Session Cache:** `session:{token_hash}` -> Serialized session state.
- **TTS Frame Cache:** `tts:{hash}` -> Synthesized audio cache to reduce latency and API costs.

---

## 4. MinIO / S3 Object Storage Audit

### 4.1 Storage Engine & Bucket Configuration
- **Engine:** MinIO (`minio/minio`) on port 9000 (API) and port 9001 (Console).
- **Legacy Bucket:** `voice-audio`
- **Target GenQuantaa Bucket:** `genquantaa-voice-audio` (`GENQUANTAA_MINIO_BUCKET`)
- **Python SDKs:** `minio` 7.2.16, `aioboto3` 15.1.0

### 4.2 Recording Storage Taxonomy
- **Audio Call Recordings:** `recordings/{org_id}/{workflow_run_id}.wav`
- **Knowledge Base Source Documents:** `knowledge_bases/{org_id}/{kb_id}/{doc_id}.pdf`
- **TTS Audio Clips:** `tts_cache/{hash}.mp3`

---

## 5. Component Dependency Matrix

| Service | Primary Consumers | Critical Dependencies |
| :--- | :--- | :--- |
| **PostgreSQL 17** | `genquantaa-api`, `alembic`, `ARQ workers` | Tenant metadata, agent graphs, call logs, vector embeddings (`pgvector`). |
| **Redis 7** | `genquantaa-api`, `ARQ workers`, `campaign_orchestrator` | ARQ job queue, active call locks, `campaign_events` pub/sub, worker sync. |
| **MinIO S3** | `genquantaa-api`, `pipeline_service`, Browser UI | Audio recordings, source PDF document uploads, audio presigned URLs. |
