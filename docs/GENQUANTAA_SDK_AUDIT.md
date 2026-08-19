# GenQuantaa Calling Agent — API, SDK & CLI Layer Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits the FastAPI REST API contracts, the Next.js UI OpenAPI client generation pipeline, the Python SDK (`sdk/python`), the TypeScript SDK (`sdk/typescript`), and publishing scripts.

---

## 2. API & OpenAPI Client Architecture

### 2.1 FastAPI OpenAPI Endpoint (`api/app.py`)
- **Metadata Title:** `GenQuantaa Calling Agent API`
- **Description:** `API for the GenQuantaa Calling Agent Platform`
- **Version:** `1.0.0`
- **Schema Location:** `/api/v1/openapi.json`
- **Interactive Documentation:** `/docs` (Swagger UI) & `/redoc` (ReDoc)

### 2.2 UI Generated Client (`ui/src/client/*`)
- **Generator Engine:** `@hey-api/openapi-ts` 0.53.11 via `openapi-ts.config.ts`.
- **Target Location:** `ui/src/client/` (`client.gen.ts`, `sdk.gen.ts`, `types.gen.ts`).
- **Fetch Runtime:** `@hey-api/client-fetch` using `getServerBackendUrl()` / `getBrowserBackendUrl()`.
- **Runtime Origin:** Container-to-container `http://api:8000`, Browser `http://localhost:8000`.

---

## 3. SDK & Package Taxonomy

### 3.1 Python SDK (`sdk/python`)
- **Package Name:** `dograh-sdk` (PyPI metadata)
- **Target GenQuantaa Package Name:** `genquantaa-sdk`
- **Module Namespace:** `genquantaa_sdk` (Aliased with `dograh_sdk` for legacy client scripts)
- **Codegen Script:** `python -m genquantaa_sdk.codegen`

### 3.2 TypeScript SDK (`sdk/typescript`)
- **Package Name:** `@dograh/sdk` (NPM metadata in `sdk/typescript/package.json`)
- **Target GenQuantaa Package Name:** `@genquantaa/sdk`
- **Examples Location:** `examples/typescript/package.json`

### 3.3 CLI Evaluation
- **Status:** No production CLI binary (`dograh-cli`) is required or used in the core Docker runtime stack.

---

## 4. Backward Compatibility Strategy

1. **Endpoint Paths:** Preserve all existing REST endpoints (`/api/v1/workflows`, `/api/v1/calls`, `/api/v1/health`).
2. **OpenAPI Schema Generation:** Regenerate `ui/src/client` using `@hey-api/openapi-ts` against `http://localhost:8000/api/v1/openapi.json`.
3. **No Unnecessary PyPI/NPM Publishing:** Prevent publishing dummy/stub packages to PyPI or NPM registries.
