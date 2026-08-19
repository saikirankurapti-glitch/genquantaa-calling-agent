# GenQuantaa Calling Agent — Complete Call Lifecycle

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Complete Call Execution Lifecycle

```
[ PSTN Caller / WebRTC Browser ]
               │
               │ 1. Inbound Webhook / Outbound API Trigger
               ▼
┌────────────────────────────────────────────────────────┐
│  FastAPI Telephony Router (`api/routes/telephony.py`)  │
│  - Endpoint: `POST /api/v1/telephony/{provider}/webhook`│
│  - Resolves DID -> `WorkflowModel` & `organization_id` │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 2. Create `WorkflowRunModel` & Mint HMAC Token
                         ▼
┌────────────────────────────────────────────────────────┐
│  Media WebSocket Gateway                               │
│  - Endpoint: `/api/v1/telephony/ws/{wf}/{org}/{run}`   │
│  - Verifies `GENQUANTAA_TELEPHONY_WS_TOKEN_SECRET`     │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 3. Audio Streams (16kHz PCM / mulaw)
                         ▼
┌────────────────────────────────────────────────────────┐
│  Pipecat Audio Pipeline (`api/services/pipecat`)       │
│  - STT: Deepgram / AssemblyAI / Whisper                │
│  - LLM: OpenAI / Anthropic / Gemini                    │
│  - TTS: ElevenLabs / Cartesia / Deepgram               │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 4. Post-Call Audio Export
                         ▼
┌────────────────────────────────────────────────────────┐
│  MinIO Object Storage (`genquantaa-voice-audio`)       │
│  - Path: `recordings/{org_id}/{workflow_run_id}.wav`   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Audio Codec & Frame Transport

- **PSTN Carrier Media Streams:** 8,000 Hz mu-law / a-law (PCMU/PCMA) base64 encoded inside WebSocket text frames.
- **WebRTC Browser Streams:** Opus / 16,000 Hz PCM audio frames over WebRTC PeerConnection or WebSocket.
- **Pipecat Resampling:** Internal audio pipelines resample to 16,000 Hz 16-bit mono PCM for optimal STT transcription accuracy.
