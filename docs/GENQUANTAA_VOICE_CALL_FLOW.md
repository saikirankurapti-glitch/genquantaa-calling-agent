# GenQuantaa Calling Agent — Complete Voice Call Flow

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Call Trace  

---

## 1. Step-by-Step Code Path Trace

```
1. Telephony Webhook / WebRTC Dial
   │  Source: `api/routes/telephony.py` & `api/routes/workflow_run.py`
   │  Input: Call Trigger / Carrier HTTP POST
   ▼
2. Media WebSocket Establishment
   │  Source: `api/routes/telephony.py` (`_handle_telephony_websocket`)
   │  Input: Dual-channel audio socket connection
   ▼
3. Pipeline Runner Initialization
   │  Source: `api/services/pipecat/run_pipeline.py` (`run_pipeline_task`)
   │  Input: `workflow_run_id`, `organization_id`, agent config
   ▼
4. Transport & VAD Frame Setup
   │  Source: `api/services/pipecat/pipeline_builder.py`
   │  Component: `SileroVADAnalyzer` + Audio Transport
   ▼
5. Speech-to-Text (STT) Processing
   │  Source: `api/services/pipecat/service_factory.py` (`create_stt_service`)
   │  Input: Audio PCM frames -> Output: Text Transcript
   ▼
6. Conversation Context & LLM Ingestion
   │  Source: `api/services/pipecat/run_pipeline.py` & `event_handlers.py`
   │  Input: System prompt + User message -> Output: LLM Token Stream
   ▼
7. Tool / Function Calling (If Triggered)
   │  Source: `api/services/pipecat/event_handlers.py` (`handle_tool_call`)
   │  Input: Tool arguments -> Output: JSON result returned to LLM
   ▼
8. Text-to-Speech (TTS) Synthesis
   │  Source: `api/services/pipecat/service_factory.py` (`create_tts_service`)
   │  Input: Text tokens -> Output: Synthesized Audio PCM frames
   ▼
9. Audio Playback to Carrier / Client
   │  Source: `api/services/pipecat/pipeline_builder.py`
   │  Output: Audio returned to WebRTC / Telephony socket
   ▼
10. Recording & Call Log Metadata
   │  Source: `api/services/pipecat/recording_router_processor.py`
   │  Output: WAV file upload to MinIO (`genquantaa-voice-audio`)
```
