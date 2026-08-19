# GenQuantaa Calling Agent — API, SDK & Client Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document outlines the API, OpenAPI client generation, Python SDK (`genquantaa-sdk`), TypeScript SDK (`@genquantaa/sdk`), and UI client architecture for GenQuantaa Calling Agent.

---

## 2. API & Client Architecture Stack

```
┌────────────────────────────────────────────────────────┐
│  Next.js 15 UI Client (`ui/src/app/*`)                  │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Generated Types & Functions (`ui/src/client/*`)
                         ▼
┌────────────────────────────────────────────────────────┐
│  @hey-api/client-fetch Runtime (`ui/src/lib/apiClient`)│
│  - Headers: `Authorization: Bearer <genquantaa_token>` │
│  - Headers: `X-API-Key: <key>`                         │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ REST API Calls (`/api/v1/*`)
                         ▼
┌────────────────────────────────────────────────────────┐
│  FastAPI Application (`api/app.py` & `api/routes/*`)   │
│  - OpenAPI Specs: `/api/v1/openapi.json`               │
│  - Docs: `/docs` (Swagger UI)                          │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ Async Business Logic
                         ▼
┌────────────────────────────────────────────────────────┐
│  Services / Models (`api/services/*` & `api/db/*`)     │
└────────────────────────────────────────────────────────┘
```

---

## 3. SDK & Package Specifications

### 3.1 Python SDK (`genquantaa-sdk`)
- **Location:** `sdk/python/pyproject.toml`
- **Module:** `genquantaa_sdk` (with `dograh_sdk` backwards-compatible alias)
- **Codegen Tool:** `python -m genquantaa_sdk.codegen`

### 3.2 TypeScript SDK (`@genquantaa/sdk`)
- **Location:** `sdk/typescript/package.json`
- **Target Import:** `import { GenQuantaaClient, Workflow } from "@genquantaa/sdk";`

### 3.3 UI OpenAPI Client Generation Pipeline
- **Command:** `npm run generate-client` inside `ui/`
- **Config File:** `ui/openapi-ts.config.ts`
- **Source:** `${BACKEND_URL}/api/v1/openapi.json`
- **Output:** `ui/src/client/` (`client.gen.ts`, `sdk.gen.ts`, `types.gen.ts`)
