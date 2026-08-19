# GenQuantaa Calling Agent — Voice Latency & Performance Baseline

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Baseline Measurement  

---

## 1. Subsystem Latency Metrics

- **VAD End-of-Speech Detection:** ~300 ms – 450 ms
- **STT Transcription Latency (Deepgram Nova-2):** ~150 ms – 250 ms
- **LLM First-Token Time (OpenAI GPT-4o-mini):** ~200 ms – 350 ms
- **TTS First-Audio-Chunk Time (ElevenLabs / Cartesia):** ~180 ms – 300 ms
- **Total Turn-Around Latency (Speech-to-Speech):** ~850 ms – 1,350 ms
