# GenQuantaa Calling Agent — System Architecture & Technical Specifications

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architectural Specification  
**Target Platform:** GenQuantaa Calling Agent Enterprise Platform  

---

## 1. Executive Overview & System Objectives

GenQuantaa Calling Agent is an enterprise-grade, real-time voice AI platform for automated inbound and outbound calling, conversational AI workflows, and voice agent orchestration.

This repository (`c:\Users\raksh\GENQUANTAA\genquantaa-calling-agent`) is an independent fork of the open-source Dograh platform. The original repository at `c:\Users\raksh\GENQUANTAA\dograh` serves as a read-only reference and rollback system.

### Core System Capabilities
1. **Low-Latency Real-Time Voice Pipeline:** Under 500ms end-to-end voice latency over WebSockets and WebRTC.
2. **Multi-Carrier Telephony Integration:** Seamless connectivity with Telnyx, Twilio, Vonage, Plivo, Vobiz, Cloudonix, and Asterisk ARI.
3. **Visual Agent Workflow Canvas:** Drag-and-drop workflow execution engine built on Next.js, React, and `@xyflow/react`.
4. **Knowledge Retrieval (RAG):** Context injection using PostgreSQL `pgvector` vector similarity search.
5. **Provider Agnostic AI Integration:** Plug-and-play STT (Deepgram, Whisper, Speechmatics), LLMs (OpenAI, Gemini, Anthropic, Groq), and TTS (ElevenLabs, Cartesia, Sarvam, Rime).

---

## 2. Current vs. Target GenQuantaa Architecture

```
[ Current Dograh Fork Architecture ]
Browser / Client (Port 3010) ----> Dograh UI (Next.js 15 Standalone)
                                         |
                                         v
Telephony Carrier (Twilio/Telnyx) ---> Dograh API (FastAPI Port 8000)
                                         |
                       +-----------------+-----------------+
                       |                 |                 |
                       v                 v                 v
                PostgreSQL (5432)   Redis (6379)     MinIO S3 (9000)
                (pgvector 17)       (ARQ Queue)      (voice-audio)
                       |
                       +--------------> Pipecat Voice Pipeline (Submodule)
                                         |
                                (Deepgram/OpenAI/ElevenLabs)

==========================================================================

[ Target GenQuantaa Calling Agent Architecture ]
Browser / Mobile Client -------> GenQuantaa Web Console (Port 3010)
                                         | (OAuth2 / Custom JWT)
                                         v
PSTN / SIP / WebRTC ------------> GenQuantaa API Gateway (Port 8000)
                                         |
               +-------------------------+-------------------------+
               |                         |                         |
               v                         v                         v
   GenQuantaa Postgres (5432)   GenQuantaa Redis (6379)   GenQuantaa S3 Storage
   (pgvector + RAG Context)     (ARQ Queue + Pub/Sub)     (Recordings & TTS Cache)
               |                         |
               +-------------------------+
                         |
                         v
         GenQuantaa Orchestrator Engine (FastAPI Workers)
                         |
                         v
         GenQuantaa Pipecat Voice Pipeline Engine
                         |
   +---------------------+---------------------+
   |                     |                     |
   v                     v                     v
STT Engine           LLM Engine            TTS Engine
(Deepgram/Whisper)   (OpenAI/Gemini/Groq)  (ElevenLabs/Cartesia/Sarvam)
```

---

## 3. Detailed Component Architecture

### 3.1 Frontend Web Application (`/ui`)
- **Framework:** Next.js 15.3.3 (App Router, standalone deployment mode).
- **Runtime:** React 19.1.0, TypeScript 5.0, Node 22 Alpine.
- **UI & Layout:** Tailwind CSS v4 (`@tailwindcss/postcss`), Radix UI primitives, Lucide React icons, Next Themes, Sonner toasts.
- **Workflow Engine Canvas:** `@xyflow/react` v12.10.2, `@dagrejs/dagre`, `zundo` (undo/redo), `zustand` state management.
- **API Client:** Generated OpenAPI TS Client (`@hey-api/openapi-ts`) built from FastAPI OpenAPI spec.

### 3.2 Backend REST & WebSocket API (`/api`)
- **Framework:** FastAPI 0.135.3 running on Uvicorn 0.35.0 (Python 3.13).
- **Database ORM:** SQLAlchemy 2.0.43 (asyncio) + AsyncPG 0.30.0 + Alembic 1.16.5 migrations.
- **Task Worker Queue:** ARQ 0.26.3 backed by Redis 7.
- **Voice Agent Engine:** `tuner-pipecat-sdk` 0.2.4 + Pipecat AI submodule (`pipecat-ai`).
- **MCP Server:** FastMCP 3.2.4 for customer-provided MCP tools.

### 3.3 Infrastructure & Storage Services
- **Database:** PostgreSQL 17 with `pgvector` vector extension (`pgvector/pgvector:pg17`).
- **Cache & Pub/Sub:** Redis 7 with password authentication.
- **Object Storage:** MinIO (`minio/minio`) on port 9000 (API) and port 9001 (Console) / AWS S3 compatible.
- **WebRTC & TURN:** Coturn 4.8.0 (Ports 3478 UDP/TCP, 5349 UDP/TCP, 49152-49200 UDP).
- **Tunneling:** Cloudflare Tunnel (`cloudflared`) on port 2000 for quick-tunnel discovery during local development.

---

## 4. End-to-End Runtime Lifecycle Trace

```
Customer Phone / Browser
     │
     │  1. Inbound Call / WebRTC Connection Request
     ▼
Telephony Carrier (Telnyx / Twilio / Vonage / Cloudonix / ARI)
     │
     │  2. Webhook / SIP Invite to /api/v1/telephony/webhook
     ▼
GenQuantaa Backend API
     │  3. Lookup Phone DID -> Resolve Organization & Workflow
     │  4. Generate Telephony Signed WebSocket Token
     │  5. Spawn ARQ Worker / Task for Workflow Session
     ▼
Workflow Run / Session Initialized
     │
     │  6. WebSocket Handshake Established
     ▼
Pipecat Voice Pipeline Engine
     │
     ├─► Customer Speaks -> Audio Frames (Mulaw 8kHz / PCM 16kHz)
     │        │
     │        ▼
     ├─► 7. STT Provider (Deepgram / Whisper) -> Transcribes Speech to Text
     │        │
     │        ▼
     ├─► 8. RAG / Knowledge Context Retrieval
     │        │    Queries pgvector table knowledge_base_documents via Cosine Similarity
     │        │    Injects top matching chunks into System Prompt
     │        ▼
     ├─► 9. LLM Engine (OpenAI / Gemini / Anthropic)
     │        │    Evaluates Prompt + Conversation History + RAG Context
     │        │    Emits text tokens + triggers function calls (if configured)
     │        ▼
     ├─► 10. Function / Tool Execution (If Tool Call Requested)
     │        │    Invokes HTTP API / MCP Tool / End Call / Transfer Call
     │        │    Appends Tool Result back to LLM context
     │        ▼
     ├─► 11. TTS Engine (ElevenLabs / Cartesia / Sarvam)
     │        │    Converts LLM text stream to synthesized PCM audio stream
     │        ▼
     └─► 12. Audio Streaming to Customer via WebSocket / Telephony Carrier
```

---

## 5. UI Lifecycle Trace

```
1. User Authentication & Login
   - User inputs credentials at /login.
   - Auth server verifies JWT / Session token and sets security cookies.

2. Organization Dashboard (/dashboard)
   - Fetches organization metrics, active call counts, concurrent limit status.

3. Agent Creation Canvas (/workflows/new)
   - User opens workflow graph editor built on @xyflow/react.
   - Configures agent persona, system prompt, and node execution paths.

4. Voice & Knowledge Base Configuration
   - Selects TTS Provider (ElevenLabs/Cartesia/Sarvam) and voice ID.
   - Attaches Knowledge Base (PDFs, docs) parsed and indexed in pgvector.

5. Phone Number & Telephony Binding
   - Assigns DID phone number from Telnyx / Twilio integration to workflow.

6. WebRTC Test Call Execution
   - Click "Test Agent" -> WebRTC widget connects directly to backend API.
   - Tests speech latency, prompt accuracy, and tool calls in browser.

7. Production Execution & Analytics
   - Inbound/Outbound campaign starts -> Active call logs streamed via WebSockets.
   - Transcripts, audio recordings, and telemetry pushed to dashboard.
```

---

## 6. Codebase Classification & Reuse Matrix

| Category | Component Description | Current Files / Locations | Target Action in GenQuantaa |
| :--- | :--- | :--- | :--- |
| **Reuse Unchanged** | Canvas Graph Editor & Flow Nodes | `ui/src/components/flow/*`, `ui/src/components/workflow/*` | Keep core layout, update branding colors & labels. |
| **Reuse Unchanged** | Database Models & Alembic Schema | `api/db/*`, `api/alembic/*` | Retain schema structure, update default org names. |
| **Must Replace** | Onboarding Service Client | `ui/src/components/lead-forms/onboardingServiceClient.ts` | Replace `api-leads.dograh.com` with GenQuantaa API. |
| **Must Replace** | Telemetry & Analytics | `api/app.py`, `ui/Dockerfile`, `docker-compose.yaml` | Remove PostHog key `phc_ItizB1dP6...`, replace with custom telemetry. |
| **Must Replace** | Cookie Secrets & Auth Tokens | `ui/src/middleware.ts`, `ui/src/lib/auth/server.ts` | Rename `dograh_auth_token` -> `genquantaa_auth_token`. |
| **Should Rewrite** | OpenAPI Client Generator | `ui/scripts/generate-client.mjs`, `ui/package.json` | Re-point to GenQuantaa API spec & package namespace `@genquantaa/sdk`. |
| **Should Rewrite** | Branding Assets & Embed Script | `ui/public/embed/dograh-widget.js`, `ui/public/*` | Rename to `genquantaa-widget.js`, update logo SVGs & metadata. |
| **Temp Dependent** | Pipecat AI Submodule | `pipecat/` (`https://github.com/dograh-hq/pipecat.git`) | Fork `pipecat` to `github.com/genquantaa/pipecat` in Phase 5. |
