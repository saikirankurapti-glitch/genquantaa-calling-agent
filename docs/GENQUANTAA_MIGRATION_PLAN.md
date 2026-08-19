# GenQuantaa Calling Agent — Phased Migration Plan

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Migration Blueprint  

---

## Executive Summary & Migration Roadmap

This document outlines the phased migration strategy to transform the forked Dograh repository into **GenQuantaa Calling Agent**, an independent enterprise voice AI platform.

The migration is divided into **11 execution phases (Phase 0 through Phase 10)** to guarantee zero-downtime development, clear boundary isolation, and risk-mitigated rollbacks.

---

## Phase Breakdown Specifications

### PHASE 0 — Baseline and Rollback
- **Objective:** Establish clean local baseline, git remotes, and automated rollback capability against reference `c:\Users\raksh\GENQUANTAA\dograh`.
- **Files/Modules Affected:** `.git/config`, `docs/DOGRAH_BASELINE.md`, `docs/GENQUANTAA_*`.
- **Dependencies Affected:** Git remotes pointing to `https://github.com/saikirankurapti-glitch/genquantaa-calling-agent.git`.
- **Database Changes:** None.
- **Docker Changes:** None. Verify running container baseline (`dograh-ui-1`, `dograh-api-1`, etc.).
- **Environment Variables:** None.
- **API Changes:** None.
- **UI Changes:** None.
- **Testing Required:** `git status`, `docker compose ps`, API `/api/v1/health` check.
- **Rollback Strategy:** Reset git working directory or revert to `dograh` baseline folder.
- **Estimated Effort:** 0.5 Hours (Completed).

---

### PHASE 1 — Branding and Configuration Ownership
- **Objective:** Re-brand UI elements, public embed scripts, documentation links, and metadata to GenQuantaa Calling Agent.
- **Files/Modules Affected:** `ui/src/app/layout.tsx`, `ui/public/favicon.ico`, `ui/public/embed/dograh-widget.js` -> `genquantaa-widget.js`, `ui/src/middleware.ts`, `ui/src/components/lead-forms/onboardingServiceClient.ts`.
- **Dependencies Affected:** UI asset references, cookie keys (`dograh_auth_token` -> `genquantaa_auth_token`).
- **Database Changes:** Update default organization name seeds in `api/db/init_db.py`.
- **Docker Changes:** Container name update in `docker-compose.yaml` (`genquantaa-ui`, `genquantaa-api`).
- **Environment Variables:** `NEXT_PUBLIC_APP_NAME="GenQuantaa Calling Agent"`, `NEXT_PUBLIC_ONBOARDING_API_URL`.
- **API Changes:** Update `/api/v1/config/version` to return GenQuantaa branding metadata.
- **UI Changes:** Logo swap, color palette refinement, document page title updates.
- **Testing Required:** Build Next.js UI (`npm run build`), verify favicon, logo, embed widget functionality.
- **Rollback Strategy:** Revert git commit for Phase 1 assets.
- **Estimated Effort:** 3.0 Hours.

---

### PHASE 2 — Own Database, Storage & Redis Infrastructure
- **Objective:** Establish isolated database credentials, MinIO buckets, and Redis password configuration owned by GenQuantaa.
- **Files/Modules Affected:** `docker-compose.yaml`, `.env`, `api/db/session.py`, `api/services/storage.py`.
- **Dependencies Affected:** PostgreSQL (`genquantaa_postgres`), Redis (`genquantaa_redis`), MinIO (`genquantaa_minio`).
- **Database Changes:** Provision `genquantaa` database user & schema.
- **Docker Changes:** Rename Docker volumes (`genquantaa_postgres_data`, `genquantaa_redis_data`, `genquantaa_minio_data`).
- **Environment Variables:** `POSTGRES_USER=genquantaa`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_BUCKET="genquantaa-voice-audio"`.
- **API Changes:** Storage service initialization logic updated for `genquantaa-voice-audio` bucket.
- **UI Changes:** None.
- **Testing Required:** Alembic migrations `alembic upgrade head`, MinIO health check, Redis ping.
- **Rollback Strategy:** Re-attach original docker volume mounts.
- **Estimated Effort:** 2.5 Hours.

---

### PHASE 3 — Own Authentication & User Management
- **Objective:** Decouple from legacy Dograh auth cookies and implement GenQuantaa JWT authentication and user management.
- **Files/Modules Affected:** `api/routes/auth.py`, `api/services/auth.py`, `ui/src/lib/auth/*`, `ui/src/middleware.ts`.
- **Dependencies Affected:** JWT token verification logic, bcrypt hashing.
- **Database Changes:** Add `user_sessions` and `oauth_providers` schema tables if expanding auth.
- **Docker Changes:** None.
- **Environment Variables:** `GENQUANTAA_JWT_SECRET="<strong-random-key>"`, `JWT_ALGORITHM="HS256"`.
- **API Changes:** Update auth endpoints `/api/v1/auth/login`, `/api/v1/auth/me`, `/api/v1/auth/refresh`.
- **UI Changes:** Login page redesign, session refresh hook, token storage in `genquantaa_auth_token` cookie.
- **Testing Required:** User signup, login, session expiry test, protected route access test.
- **Rollback Strategy:** Fallback to OSS dev mode auth middleware.
- **Estimated Effort:** 4.0 Hours.

---

### PHASE 4 — Own Agent Management & Workflow Engine
- **Objective:** Refactor agent creation, workflow graph serialization, node types, and prompt execution engine.
- **Files/Modules Affected:** `api/routes/workflows.py`, `api/services/workflow_service.py`, `ui/src/components/workflow/*`, `ui/src/components/flow/*`.
- **Dependencies Affected:** Workflow schema definitions, `@xyflow/react` node state handlers.
- **Database Changes:** `workflows` and `workflow_versions` migration for GenQuantaa custom node parameters.
- **Docker Changes:** None.
- **Environment Variables:** `DEFAULT_WORKFLOW_CONCURRENCY_LIMIT=10`.
- **API Changes:** `/api/v1/workflows` CRUD endpoints, `/api/v1/workflows/{id}/publish`.
- **UI Changes:** Graph node palette updates, prompt template manager, node connection validation.
- **Testing Required:** Create, edit, publish, and duplicate visual workflow graphs.
- **Rollback Strategy:** Revert workflow schema migration and UI node components.
- **Estimated Effort:** 6.0 Hours.

---

### PHASE 5 — Own Voice Pipeline & Pipecat Engine
- **Objective:** Decouple Pipecat submodule from `dograh-hq/pipecat` and configure GenQuantaa voice pipeline wrappers.
- **Files/Modules Affected:** `.gitmodules`, `pipecat/`, `api/services/pipeline_service.py`, `api/tasks/call_tasks.py`.
- **Dependencies Affected:** `tuner-pipecat-sdk`, `pipecat-ai` submodule repository.
- **Database Changes:** `workflow_runs` state tracking for pipeline latency metrics.
- **Docker Changes:** Update Dockerfile to build custom Pipecat dependencies.
- **Environment Variables:** `PIPECAT_LOG_LEVEL="INFO"`, `ENABLE_SMART_TURN_ANALYZER=true`.
- **API Changes:** WebSocket pipeline runner endpoint `/api/v1/ws/call/{run_id}`.
- **UI Changes:** Real-time speech latency indicator in test call modal.
- **Testing Required:** WebRTC audio loopback test, latency measurement (<500ms target).
- **Rollback Strategy:** Re-point git submodule to reference Pipecat commit.
- **Estimated Effort:** 8.0 Hours.

---

### PHASE 6 — Own Telephony & Carrier Infrastructure
- **Objective:** Own telephony webhooks, DID routing, SIP trunks, and call transfer handlers for Telnyx, Twilio, and ARI.
- **Files/Modules Affected:** `api/routes/telephony.py`, `api/services/telephony/*`, `ui/src/components/telephony/*`.
- **Dependencies Affected:** Telnyx SDK, Twilio SDK, Asterisk ARI manager.
- **Database Changes:** `phone_numbers` and `telephony_configurations` model enhancements.
- **Docker Changes:** Coturn TURN server configuration update (`TURN_SECRET`).
- **Environment Variables:** `TELNYX_API_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `ENABLE_ARI_MANAGER=true`.
- **API Changes:** `/api/v1/telephony/webhooks/{provider}`, `/api/v1/telephony/numbers/assign`.
- **UI Changes:** Telephony provider configuration modal, DID number purchasing & mapping UI.
- **Testing Required:** Inbound PSTN call test, outbound campaign call test, SIP call transfer test.
- **Rollback Strategy:** Revert webhook route handlers.
- **Estimated Effort:** 7.0 Hours.

---

### PHASE 7 — Own RAG & Knowledge Retrieval System
- **Objective:** Refactor knowledge base parsing, chunking, vector indexing (`pgvector`), and context injection into prompts.
- **Files/Modules Affected:** `api/routes/knowledge_base.py`, `api/services/knowledge_service.py`, `ui/src/components/knowledge/*`.
- **Dependencies Affected:** OpenAI Embeddings (`text-embedding-3-small`), `pgvector`, PyPDF/Docx parsers.
- **Database Changes:** `knowledge_bases` and `knowledge_base_documents` pgvector HNSW index optimization.
- **Docker Changes:** Ensure PostgreSQL container includes `pgvector/pgvector:pg17`.
- **Environment Variables:** `EMBEDDING_MODEL="text-embedding-3-small"`, `RAG_TOP_K=3`.
- **API Changes:** `/api/v1/knowledge-base/upload`, `/api/v1/knowledge-base/search`.
- **UI Changes:** File upload drag-and-drop zone, document parsing status progress bar, chunk inspector.
- **Testing Required:** PDF document upload, vector similarity query execution, LLM prompt context injection check.
- **Rollback Strategy:** Revert knowledge service methods to standard SQL query fallback.
- **Estimated Effort:** 5.0 Hours.

---

### PHASE 8 — Own Analytics & Call Records Pipeline
- **Objective:** Implement self-hosted call logging, transcript storage, audio recording playback, and metrics dashboard.
- **Files/Modules Affected:** `api/routes/calls.py`, `api/services/call_service.py`, `ui/src/app/(dashboard)/calls/*`.
- **Dependencies Affected:** PostHog removal, MinIO presigned URL generator for audio playback.
- **Database Changes:** Add `call_transcripts` and `call_metrics` tables with execution duration & cost metrics.
- **Docker Changes:** None.
- **Environment Variables:** `RECORDING_STORAGE_EXPIRY_SECONDS=86400`.
- **API Changes:** `/api/v1/calls`, `/api/v1/calls/{id}/transcript`, `/api/v1/calls/{id}/recording-url`.
- **UI Changes:** Call history log table, audio waveform player, transcript turn-by-turn inspector.
- **Testing Required:** Verify audio recording presigned URL generation, test transcript playback synchronization.
- **Rollback Strategy:** Revert call routes to standard database response format.
- **Estimated Effort:** 4.5 Hours.

---

### PHASE 9 — Remove Residual Dograh Dependencies
- **Objective:** Scour and purge all legacy Dograh strings, telemetry keys, branding, and API endpoints from codebase.
- **Files/Modules Affected:** All `*.py`, `*.ts`, `*.tsx`, `*.json`, `Dockerfile`, `docker-compose.yaml` files.
- **Dependencies Affected:** Purge `phc_ItizB1dP...`, `api-leads.dograh.com`, `@dograh/sdk`.
- **Database Changes:** Clean up legacy organization bootstrap keys in database.
- **Docker Changes:** Update all image build contexts and tag labels to `genquantaa/*`.
- **Environment Variables:** Remove legacy `DOGRAH_*` variables, replace with `GENQUANTAA_*`.
- **API Changes:** Replace `X-Dograh-Devops-Secret` header validation with `X-GenQuantaa-Devops-Secret`.
- **UI Changes:** Ensure 0 occurrences of "Dograh" in user-facing UI and document titles.
- **Testing Required:** Repository-wide grep search for `dograh` (must return 0 operational matches).
- **Rollback Strategy:** Restore from Phase 8 commit.
- **Estimated Effort:** 3.5 Hours.

---

### PHASE 10 — Production Hardening & Security Audit
- **Objective:** Implement rate limiting, TLS termination, CORS hardening, secret rotation, and deployment scripts.
- **Files/Modules Affected:** `nginx/`, `deploy/`, `scripts/`, `api/logging_config.py`.
- **Dependencies Affected:** Nginx SSL certs, Coturn TURN credentials, Docker production stack.
- **Database Changes:** Database backup automation script & connection pool tuning.
- **Docker Changes:** Production Compose stack (`docker-compose.prod.yaml`) with health check retries.
- **Environment Variables:** `ENVIRONMENT="production"`, `LOG_LEVEL="INFO"`, `CORS_ORIGINS`.
- **API Changes:** Global rate limiting middleware (`slowapi` / Redis rate limiter).
- **UI Changes:** Security header setup in `ui/next.config.ts`.
- **Testing Required:** Automated end-to-end call test, load test (concurrency limit check), SSL rating check.
- **Rollback Strategy:** Rollback to development compose stack.
- **Estimated Effort:** 5.0 Hours.

---

## Technical Risk Assessment & Timelines

### Recommended Implementation Order
1. **Phase 0 & Phase 1** (Baseline, Branding & Config Ownership)
2. **Phase 2 & Phase 3** (Database, Storage, Auth & User Management)
3. **Phase 4 & Phase 5** (Agent Canvas & Pipecat Voice Pipeline Engine)
4. **Phase 6 & Phase 7** (Telephony Integrations & RAG Knowledge Engine)
5. **Phase 8 & Phase 9** (Analytics, Call Logs & Dograh Dependency Removal)
6. **Phase 10** (Production Hardening & Deployment)

### Critical Risks & Mitigations

| Critical Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Pipecat Submodule Breaking Changes** | High | Pin `pipecat` submodule commit hash; test voice pipeline after any upstream sync. |
| **WebSockets Token Hijacking** | Critical | Enforce `TELEPHONY_WS_TOKEN_SECRET` HMAC signing on all telephony WebSocket endpoints. |
| **Audio Latency Spikes in RAG Query** | High | Implement vector search timeout (max 150ms) and asynchronous parallel prompt assembly. |
| **PSTN Call Transfer Failures** | Medium | Provide fallback SIP REFER and Twilio `<Redirect>` transfer handlers. |

### Single Developer Timeline (AI / Vibe Coding Mode)
- **Total Estimated Effort:** ~50 Hours of focused development.
- **Full Project Completion:** 6 to 8 Working Days.

### What Can Realistically Be Completed in 2 Days (48 Hours)
- **Phase 0:** Baseline audit & verification.
- **Phase 1:** Complete UI re-branding, logo replacement, metadata titles, and cookie key updates.
- **Phase 2:** Isolated GenQuantaa Postgres, Redis, and MinIO storage configuration.
- **Phase 3:** Custom JWT authentication middleware and user session management.
- **Phase 9 (Partial):** Hardcoded PostHog telemetry removal and domain URL updates.

### What CANNOT Realistically Be Completed in 2 Days
- Complete custom fork and independent maintenance of the Pipecat voice engine (Phase 5).
- Multi-carrier telephony PSTN testing across all 7 carriers (Phase 6).
- Full production load testing and TURN relay NAT traversal validation in live telecom environments (Phase 10).
