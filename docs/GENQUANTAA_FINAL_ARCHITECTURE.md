# GenQuantaa Calling Agent — Production Architecture Blueprint

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architectural Baseline  

---

## 1. Executive Summary

This document specifies the complete independent operational architecture of **GENQUANTAA CALLING AGENT**, representing the final state after Phase 1 through Phase 9 migrations.

---

## 2. Complete Independent Architecture Topology

```
                         INTERNET / PSTN CARRIERS
                                    │
                             ┌──────▼──────┐
                             │ GenQuantaa  │
                             │ Platform    │
                             └──────┬──────┘
                                    │
                             ┌──────▼──────┐
                             │  Next.js    │
                             │ GenQuantaa  │
                             │     UI      │
                             └──────┬──────┘
                                    │
                             ┌──────▼──────┐
                             │  FastAPI    │
                             │ GenQuantaa  │
                             │    API      │
                             └──────┬──────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
     PostgreSQL                   Redis                     MinIO
    pgvector 17             ARQ Queues / gq:           Audio Storage
  (Multi-Tenant DB)        (Concurrency & Pub/Sub)  (`genquantaa-voice-audio`)
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                         Voice Orchestrator
                       (`run_pipeline.py`)
                                    │
                                 Pipecat
                         (Pinned AI Audio Engine)
                                    │
                ┌───────────────────┼───────────────────┐
                ▼                   ▼                   ▼
           STT Services        LLM Services        TTS Services
         (Deepgram, etc.)     (OpenAI, etc.)     (ElevenLabs, etc.)
```

---

## 3. Operational Independence Checklist

- **Branding:** 100% GenQuantaa Calling Agent interface, page titles, favicons, logos, and OpenAPI specs.
- **Database:** PostgreSQL 17 + `pgvector` (`GENQUANTAA_DB_*` credentials).
- **Caching & Queues:** Redis 7 with `GENQUANTAA_REDIS_PREFIX=gq:`.
- **Object Storage:** MinIO `genquantaa-voice-audio` bucket with automatic bucket provisioner.
- **Authentication:** Local JWT tokens (`genquantaa_auth_token`, `genquantaa_auth_user`, `GENQUANTAA_JWT_SECRET`).
- **SDKs:** Python `genquantaa-sdk` and TypeScript `@genquantaa/sdk`.
- **Telephony & TURN:** `GENQUANTAA_TELEPHONY_WS_TOKEN_SECRET` & `GENQUANTAA_TURN_SECRET`.
- **Zero External Dograh Calls:** Completely standalone containerized stack.
