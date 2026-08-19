# GenQuantaa Calling Agent — STT Provider Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Provider Specification  

---

## 1. Supported STT Providers

| STT Provider | Service Class | Streaming Support | Configured | Local Test Status |
| :--- | :--- | :---: | :---: | :---: |
| **Deepgram** | `DeepgramSTTService` | WebSockets (Nova-2 / Nova-3) | YES | TESTED & READY |
| **AssemblyAI** | `AssemblyAISTTService` | WebSockets | YES | Supported |
| **Whisper** | `WhisperSTTService` | Batch / Local | YES | Supported |
| **Azure Speech** | `AzureSTTService` | WebSockets | YES | Supported |
| **Google Speech** | `GoogleSTTService` | gRPC Streaming | YES | Supported |
| **Sarvam AI** | `SarvamSTTService` | WebSockets (Saaras v1/v2) | YES | Supported |
| **Speechmatics**| `SpeechmaticsSTTService` | WebSockets | YES | Supported |
