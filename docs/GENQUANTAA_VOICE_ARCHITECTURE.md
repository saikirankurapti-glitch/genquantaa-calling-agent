# GenQuantaa Calling Agent — Voice Pipeline Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document describes the architectural boundaries between GenQuantaa-owned business logic, the GenQuantaa Voice Adapter (`api/services/pipecat`), external AI service providers, and the upstream Pipecat audio processing pipeline.

---

## 2. Component Ownership Topology

```
                  GENQUANTAA OWNED
                         │
                         ▼
             FastAPI Telephony Gateway
                         │
                         ▼
             Voice Pipeline Orchestrator
           (`api/services/pipecat/run_pipeline.py`)
                         │
                         ▼
             GenQuantaa Voice Adapter
           (`api/services/pipecat/service_factory.py`)
                         │
                         ▼
                 EXTERNAL DEPENDENCY
                         │
                         ▼
                 Pipecat Submodule
                (`pipecat/` commit `2b2b9d52`)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   STT Providers    LLM Providers    TTS Providers
  (Deepgram, etc.) (OpenAI, etc.)   (ElevenLabs, etc.)
```

---

## 3. Ownership Classification Matrix

- **GENQUANTAA OWNED:** FastAPI Telephony Gateway, `run_pipeline.py`, `pipeline_builder.py`, `service_factory.py`, `event_handlers.py`, tool execution engine, recording router processor, MinIO audio storage.
- **EXTERNAL DEPENDENCY (PINNED):** `pipecat/` git submodule (v1.1.0 pinned).
- **OPTIONAL AI PROVIDERS:** Deepgram, OpenAI, Anthropic, Gemini, ElevenLabs, Cartesia, Sarvam AI.
