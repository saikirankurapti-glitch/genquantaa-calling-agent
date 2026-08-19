# GenQuantaa Calling Agent — Turn Detection & Barge-In Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Specification  

---

## 1. Interruption & Turn Detection Lifecycle

```
[ User Speaks ]
       │
       │ Audio Frames
       ▼
┌────────────────────────────────────────────────────────┐
│  Silero VAD (`SileroVADAnalyzer`)                      │
│  - Threshold: 0.5 probability                          │
│  - Min speech duration: 250ms                          │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ `UserStartedSpeakingFrame`
                         ▼
┌────────────────────────────────────────────────────────┐
│  Interruption Handler (`pipeline_builder.py`)           │
│  - Cancels pending LLM token stream                    │
│  - Emits `TTSStoppedFrame` to halt audio output        │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ `UserStoppedSpeakingFrame` (Silence > 400ms)
                         ▼
┌────────────────────────────────────────────────────────┐
│  LLM Context Commit & Response Generation               │
└────────────────────────────────────────────────────────┘
```
