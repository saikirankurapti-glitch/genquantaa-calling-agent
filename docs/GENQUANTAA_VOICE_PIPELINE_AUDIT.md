# GenQuantaa Calling Agent — Voice Pipeline Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document provides a comprehensive audit of the GenQuantaa voice AI execution engine (`api/services/pipecat`), tracing the orchestration boundary between GenQuantaa business logic and the underlying Pipecat audio processing pipeline.

---

## 2. Voice Pipeline Architecture

- **Orchestrator Module:** `api/services/pipecat/run_pipeline.py`
- **Pipeline Builder:** `api/services/pipecat/pipeline_builder.py`
- **Provider Factory:** `api/services/pipecat/service_factory.py`
- **Tool Execution Adapter:** `api/services/pipecat/event_handlers.py`
- **Audio Configuration:** `api/services/pipecat/audio_config.py` (16,000 Hz, 16-bit mono PCM).

---

## 3. Subsystem Breakdown

1. **Input Transport Layer:** WebRTC / Telephony WebSocket streams audio frames into `Pipecat` transport handlers.
2. **Silero VAD & Turn Detection:** Detects speech boundaries and manages user interruption / barge-in.
3. **Speech-to-Text (STT):** Converts inbound audio frames to text transcripts.
4. **LLM Context Manager:** Injects system prompts, conversation history, and tool definitions into the LLM stream.
5. **Tool Execution Engine:** Intercepts LLM tool call requests, executes Python/HTTP/MCP actions, and feeds results back to the LLM.
6. **Text-to-Speech (TTS):** Synthesizes LLM response text streams into 16kHz PCM audio buffers.
7. **Audio Recording Processor:** Asynchronously buffers PCM streams and writes finished WAV files to MinIO (`genquantaa-voice-audio`).
