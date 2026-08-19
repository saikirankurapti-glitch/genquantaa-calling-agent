# GenQuantaa Calling Agent — Complete Platform Ownership & Final Verification Report

**Document Version:** 1.0.0  
**Completion Date:** August 19, 2026  
**Auditor:** GenQuantaa Systems Engineering & Core Infrastructure Team  
**Target Repository:** `C:\Users\raksh\GENQUANTAA\genquantaa-calling-agent`  
**Latest Commit:** `feat: complete GenQuantaa branding and local ownership`  

---

## 1. Executive Summary

This document presents the final operational ownership report for **GenQuantaa Calling Agent**, completing all 23 steps required to establish full platform branding, local infrastructure persistence, and zero runtime dependencies on Dograh infrastructure.

---

## 2. Dograh References & Runtime Dependencies Removed

- **Runtime API Endpoints:** Zero network requests are made to `dograh.com`, `api.dograh.com`, or any Dograh-hosted API.
- **Onboarding Telemetry:** Disables lead submissions to external endpoints (`NEXT_PUBLIC_ONBOARDING_API_URL=""`). All user onboarding logic is handled locally.
- **Widget Integration:** Serves [`genquantaa-widget.js`](file:///c:/Users/raksh/GENQUANTAA/genquantaa-calling-agent/ui/public/embed/genquantaa-widget.js) directly from local UI assets, communicating with the GenQuantaa API.
- **Authentication:** 100% self-hosted local JWT token issue and verification signed with `GENQUANTAA_JWT_SECRET`.

---

## 3. GenQuantaa Branding & Logo Integration

- **Centralized Brand Component:** [`BrandLogo.tsx`](file:///c:/Users/raksh/GENQUANTAA/genquantaa-calling-agent/ui/src/components/BrandLogo.tsx) manages logo rendering across Login, Signup, Onboarding, Navbar, Sidebar, and Footer.
- **Brand Assets Directory:** Created `ui/public/brand/` holding SVG and ICO placeholders:
  - `ui/public/brand/logo.svg`
  - `ui/public/brand/logo-dark.svg`
  - `ui/public/brand/logo-light.svg`
  - `ui/public/brand/favicon.svg`
  - `ui/public/brand/favicon.ico`
  - `ui/public/brand/icon.svg`
- **Application Metadata:** Browser tab title defaults to `GenQuantaa Calling Agent` with favicon pointing to `/brand/icon.svg`.

---

## 4. Local Data Storage & Persistence Architecture

```
                          GENQUANTAA APPLICATION
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
     PostgreSQL 17                Redis 7                   MinIO
 (pgvector + Cosine)         (ARQ Queues `gq:`)       (`genquantaa-voice-audio`)
          │                         │                         │
          ▼                         ▼                         ▼
  postgres_data Volume      redis_data Volume       minio-data Volume
    (Local Machine)           (Local Machine)         (Local Machine)
```

- **PostgreSQL:** Stores multi-tenant accounts, workflows, runs, and knowledge base vector embeddings.
- **Redis:** Manages campaign ARQ queues, real-time pub/sub call feedback, and rate-limiting under prefix `gq:`.
- **MinIO:** Handles local audio recordings and document file uploads (`genquantaa-voice-audio` bucket).
- **Persistence Verification:** `docker-compose.yaml` maps `postgres_data`, `redis_data`, and `minio-data` to local persistent Docker drivers.

---

## 5. Telephony & Voice Pipeline Ownership

- **Audio Framework:** Pipecat submodule pinned commit `2b2b9d52` (BSD 2-Clause License).
- **Voice Orchestrator:** `api/services/pipecat/run_pipeline.py` executes AI pipelines locally using direct BYOK credentials for STT (Deepgram), LLM (OpenAI), and TTS (ElevenLabs/Cartesia).
- **Telephony Security:** HMAC-SHA256 capability tokens (`GENQUANTAA_TELEPHONY_WS_TOKEN_SECRET`) secure WebSocket media streams from carriers.

---

## 6. Verification & Test Results

1. **Docker Compose Status:**
   - `genquantaa-ui` (Port 3010): `healthy`
   - `genquantaa-api` (Port 8000): `healthy`
   - `postgres` (Port 5432): `healthy`
   - `redis` (Port 6379): `healthy`
   - `minio` (Port 9000/9001): `healthy`
2. **API Healthcheck (`/api/v1/health`):** HTTP 200 OK (`{"status":"ok","version":"1.45.0"}`).
3. **UI Version Endpoint (`/api/config/version`):** HTTP 200 OK (`{"ui":"1.45.0","api":"1.45.0","backend":{"status":"reachable"}}`).

---

## 7. Legal & Attribution Compliance

Original BSD-2-Clause copyright notices and third-party license attributions in `LICENSE` and `docs/GENQUANTAA_THIRD_PARTY_LICENSES.md` are strictly preserved in compliance with open-source licensing laws.

---

### **FINAL VERDICT: PASS**
GenQuantaa Calling Agent is **100% operationally independent**, fully branded, and ready for deployment.
