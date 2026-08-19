# GenQuantaa Calling Agent — Campaign Engine & Queue Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document specifies the Campaign Execution Engine (`api/services/campaign`), ARQ background task queues, Redis key namespacing (`gq:`), and circuit breaker concurrency control in GenQuantaa Calling Agent.

---

## 2. Campaign Execution Stack

```
[ GenQuantaa UI / API ]
          │
          │ 1. Create & Schedule Campaign (`POST /api/v1/campaigns`)
          ▼
┌────────────────────────────────────────────────────────┐
│  Campaign Orchestrator (`campaign_orchestrator.py`)    │
│  - Polls active campaigns from PostgreSQL              │
│  - Evaluates concurrency limit per organization        │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 2. Enqueue Job (`arq:queue`)
                         ▼
┌────────────────────────────────────────────────────────┐
│  ARQ Background Worker (`api/services/campaign/runner`) │
│  - Redis Namespace: `GENQUANTAA_REDIS_PREFIX=gq:`       │
│  - Lock: Sorted set concurrency locks                  │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 3. Execute Outbound Call
                         ▼
┌────────────────────────────────────────────────────────┐
│  Call Dispatcher & Telephony Carrier                   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Redis Queue & Key Catalog

- **ARQ Queue:** `arq:queue` (Background job processing)
- **Namespaced Prefix:** `gq:` (`GENQUANTAA_REDIS_PREFIX`)
- **Pub/Sub Channels:** `campaign_events` (Real-time SSE progress updates), `worker_sync` (Worker status heartbeats).
- **Concurrency Locks:** Redis sorted set keys `gq:concurrency:{org_id}` for rate-limiting active calls.
