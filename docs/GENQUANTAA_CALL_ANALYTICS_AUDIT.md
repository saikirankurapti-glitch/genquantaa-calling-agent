# GenQuantaa Calling Agent — Call Analytics Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits call lifecycle telemetry, database models, metrics collection, transcript storage, audio recording access, and call outcome dispositions in GenQuantaa Calling Agent.

---

## 2. Call Data Models & Tables

- **Primary Table:** `workflow_runs` (`api/db/models.py`)
- **Recorded Fields:**
  - `id` (Integer, Primary Key)
  - `workflow_run_id` (UUID string, Unique, Indexed)
  - `organization_id` (Integer, Foreign Key -> `organizations.id`, Indexed)
  - `workflow_id` (Integer, Foreign Key -> `workflows.id`)
  - `state` (`WorkflowRunState`: `pending`, `running`, `completed`, `failed`, `cancelled`)
  - `call_type` (`CallType`: `inbound`, `outbound`, `web_test`)
  - `phone_number` (String, E.164 caller/callee number)
  - `duration_seconds` (Integer)
  - `started_at`, `ended_at` (DateTime UTC)
  - `recording_url` (String, MinIO path `genquantaa-voice-audio/recordings/{org_id}/{run_id}.wav`)
  - `call_summary` (Text, Auto-generated LLM summary)
  - `transcript` (JSON string, Conversation turn log)
  - `disposition` (String, Call outcome status)

---

## 3. Metrics Matrix

| Metric | Source | Real-Time / Historical | Tenant Scoped |
| :--- | :--- | :---: | :---: |
| **Total Calls** | `COUNT(workflow_runs.id)` | Historical | YES |
| **Success / Failure Rate** | `workflow_runs.state` | Historical | YES |
| **Average Call Duration** | `AVG(workflow_runs.duration_seconds)` | Historical | YES |
| **Inbound vs Outbound Ratio** | `workflow_runs.call_type` | Historical | YES |
| **STT / LLM / TTS Latency** | `workflow_run_artifacts` & Langfuse | Real-Time / Historical | YES |
| **Active Concurrent Calls** | Redis `gq:` concurrency keys | Real-Time | YES |
