# GenQuantaa Calling Agent — Pipecat Submodule & Dependency Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits the Pipecat git submodule (`pipecat/`), pinned commit revisions, build container installation, local modifications, and evaluates whether a separate Pipecat source fork is required for GenQuantaa.

---

## 2. Submodule & Build Audit

1. **Git Submodule:** `.gitmodules` points to `pipecat` at commit `2b2b9d5281a548ac1f8aa415c018b804c0cbc05b`.
2. **Container Installation:** `api/Dockerfile` binds `pipecat/` and runs:
   `uv pip install '/tmp/pipecat[cartesia,deepgram,openai,elevenlabs,groq,google,azure,sarvam,soundfile,silero,webrtc,speechmatics,openrouter,camb,mcp,inworld,smallest]'`
3. **Local Commit Analysis:** Commit log includes custom patches:
   - `fix: sarvam add _SpeakableTextFilter`
   - `fix: demote errors to warning to handle reporting using ErrorFrame`
   - `fix: prevent bargein after tool call response`
   - `Fire MockTransport on_client_disconnected only from disconnect_client()`

---

## 3. Fork Decision Matrix

- **Question:** Does GenQuantaa actually require creating a separate Pipecat source fork repository right now?
- **Decision:** **NO for Phase 6.**
- **Rationale:** The local `pipecat/` submodule directory is already checked into the `genquantaa-calling-agent` repository tree and compiled directly inside `api/Dockerfile`. Keeping Pipecat pinned as a local submodule/dependency prevents code fragmentation while maintaining 100% control over pipeline execution.
