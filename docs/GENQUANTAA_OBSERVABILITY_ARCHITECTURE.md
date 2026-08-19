# GenQuantaa Calling Agent — Observability & Telemetry Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document details the first-party GenQuantaa analytics pipeline and external optional integrations (Langfuse, PostHog, Sentry).

---

## 2. Observability Provider Classification

| Provider | Type | Data Sent | Environment Variables | Optional / Required | Runtime Impact if Missing |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **GenQuantaa DB** | Primary | Call logs, metrics, recordings | `DATABASE_URL` | **REQUIRED** | System cannot run |
| **Langfuse** | Tracing | LLM prompts, STT/TTS latency, token counts | `LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY` | **OPTIONAL** | None (Fails silently) |
| **PostHog** | Analytics | Product usage events, pageviews | `POSTHOG_API_KEY`, `POSTHOG_HOST` | **OPTIONAL** | None (Fails silently) |
| **Sentry** | Error Tracking | Frontend JavaScript exceptions | `SENTRY_DSN`, `NEXT_PUBLIC_SENTRY_DSN` | **OPTIONAL** | None (Fails silently) |

---

## 3. First-Party Analytics Pipeline

```
┌────────────────────────────────────────────────────────┐
│  GenQuantaa Telephony & Voice Pipeline                 │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Event Emissions
                         ▼
┌────────────────────────────────────────────────────────┐
│  PostgreSQL 17 (`workflow_runs`, `campaign_runs`)     │
│  MinIO Storage (`genquantaa-voice-audio`)              │
│  Redis `gq:` Pub/Sub (`campaign_events`)               │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Analytics API Queries
                         ▼
┌────────────────────────────────────────────────────────┐
│  GenQuantaa Dashboard & Reporting UI                  │
└────────────────────────────────────────────────────────┘
```
