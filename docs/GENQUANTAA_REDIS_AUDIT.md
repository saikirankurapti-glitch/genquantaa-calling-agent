# GenQuantaa Calling Agent — Redis Architecture & Namespace Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits all Redis keys, job queues, pub/sub channels, locks, and cache structures used across GenQuantaa Calling Agent, establishing the `GENQUANTAA_REDIS_PREFIX=gq:` namespacing rule for multi-tenant isolation and data ownership.

---

## 2. Redis Key & Channel Catalog

### 2.1 Asynchronous Job Queues (ARQ)
- **Engine:** ARQ 0.26.3
- **Queue Key:** `arq:queue`
- **Job Result Keys:** `arq:result:{job_id}`
- **In-flight Keys:** `arq:in-progress:{job_id}`
- **ARQ Worker Tasks:**
  - `start_workflow_run`: Asynchronously spawns Pipecat call runner.
  - `process_knowledge_base_document`: Vectorizes PDF/Docx files into PostgreSQL `pgvector`.
  - `execute_campaign_batch`: Triggers outbound campaign call batches.

### 2.2 Pub/Sub Channels
- **`campaign_events`**: Real-time event bus broadcasting campaign call status updates (`dialing`, `connected`, `completed`, `failed`) to FastAPI WebSocket consumers and UI dashboards.
- **`worker_sync`**: Cross-worker synchronization channel used to invalidate shared in-memory caches (e.g. Langfuse credentials, organization settings) across multi-pod API deployments.

### 2.3 Rate Limiter & Concurrency Lock Keys
- **Organization Concurrent Calls:** `org:{id}:active_calls` -> Sorted set (`ZADD` / `ZCOUNT`) tracking active calls per tenant.
- **Fleet-Wide Active Calls:** `fleet:active_calls` -> Global sorted set tracking system-wide call capacity.
- **Carrier Rate Limiters:** `ratelimit:{trunk_id}:{timestamp}` -> Sliding window counter.
- **Public Embed Rate Limiter:** `embed_limit:{ip}:{window}` -> Rate limiter for embedded script widgets.

### 2.4 Circuit Breaker State Keys
- **Service Circuit Breakers:** `circuit_breaker:{service_name}` -> Sliding window hash set tracking error rates for external APIs (e.g. Deepgram, ElevenLabs, OpenAI).

---

## 3. GenQuantaa Namespacing Strategy (`gq:`)

To avoid collision on shared Redis instances in production while preserving compatibility with ARQ's internal Lua scripts:

1. **Prefix Configuration Variable:** `GENQUANTAA_REDIS_PREFIX=gq:`
2. **Application Keys (Prefix Enabled):**
   - `gq:org:{id}:active_calls`
   - `gq:fleet:active_calls`
   - `gq:circuit_breaker:{name}`
   - `gq:embed_limit:{ip}`
3. **ARQ & Protocol Keys (Standard Unprefixed):**
   - `arq:queue` (ARQ requires strict `arq:` prefix for Lua script execution).
   - `campaign_events` (Pub/Sub channel name).
   - `worker_sync` (Pub/Sub channel name).
