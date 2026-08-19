# GenQuantaa Calling Agent — Call Recording & Storage Pipeline

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document traces the complete lifecycle of call audio recording, from WebRTC / SIP RTP packet capture to object storage in GenQuantaa MinIO (`genquantaa-voice-audio`) and database URL metadata persistence in PostgreSQL.

---

## 2. Complete Call Recording Lifecycle

```
[ Carrier / WebRTC Client ]
         │
         │ (RTP Audio / WebRTC Stream)
         ▼
┌────────────────────────────────────────────────────────┐
│  Pipecat Call Pipeline (FastAPI / PyAudio / WebRTC)    │
│  - Captures dual-channel inbound/outbound PCM audio    │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Audio Buffer (WAV / MP3)
                         ▼
┌────────────────────────────────────────────────────────┐
│  Storage Service (`api/services/storage.py`)           │
│  - MinIO S3 Client (`MinioFileSystem`)                 │
│  - Target Bucket: `GENQUANTAA_MINIO_BUCKET`            │
│    ("genquantaa-voice-audio")                          │
│  - Key Path: `recordings/{org_id}/{run_id}.wav`        │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Presigned S3 URI / Storage Key
                         ▼
┌────────────────────────────────────────────────────────┐
│  PostgreSQL Database (`call_logs` & `workflow_runs`)   │
│  - Updates `recording_url` column                      │
│  - Updates `recording_s3_key` column                   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Storage Configuration & Credentials

### 3.1 Environment Variables
- `GENQUANTAA_MINIO_BUCKET`: `genquantaa-voice-audio` (Fallback: `MINIO_BUCKET`)
- `MINIO_ENDPOINT`: `minio:9000` (Docker internal) / `localhost:9000` (Host)
- `MINIO_PUBLIC_ENDPOINT`: `http://localhost:8000` (Browser presigned URL endpoint)
- `MINIO_ACCESS_KEY`: Defined in `.env` (`MINIO_ROOT_USER`)
- `MINIO_SECRET_KEY`: Defined in `.env` (`MINIO_ROOT_PASSWORD`)

---

## 4. Verification Procedures

1. **Upload Verification:** Presigned put_object URL generation uploads WAV file to `genquantaa-voice-audio`.
2. **Retrieval Verification:** FastAPI endpoint `/api/v1/workflow-runs/{id}/recording` generates browser-accessible GET presigned URL.
3. **Deletion Verification:** Call run deletion triggers idempotent bucket object removal via `MinioFileSystem.delete()`.
