# GenQuantaa Calling Agent — TTS Provider Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Provider Specification  

---

## 1. Supported TTS Providers

| TTS Provider | Service Class | Output Sample Rate | Streaming | Fallback | Local Test Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **ElevenLabs** | `ElevenLabsTTSService` | 16,000 Hz / 24,000 Hz | YES | Enabled | TESTED & READY |
| **Cartesia** | `CartesiaTTSService` | 16,000 Hz / 24,000 Hz | YES | Enabled | Supported |
| **Deepgram** | `DeepgramTTSService` | 16,000 Hz | YES | Enabled | Supported |
| **Sarvam AI** | `SarvamTTSService` | 16,000 Hz | YES | Enabled | Supported |
| **Rime** | `RimeTTSService` | 16,000 Hz | YES | Enabled | Supported |
| **Minimax** | `MinimaxTTSService` | 16,000 Hz | YES | Enabled | Supported |
