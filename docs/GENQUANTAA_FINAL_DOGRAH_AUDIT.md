# GenQuantaa Calling Agent — Final Dograh Dependency Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Final Migration Specification  

---

## 1. Executive Summary

This document performs the final audit and classification of all remaining text references to Dograh across source files, build scripts, documentation, and external submodules. It confirms that GenQuantaa Calling Agent has **ZERO operational runtime dependencies** on Dograh services, servers, or endpoints.

---

## 2. Occurrence Taxonomy & Classification Matrix

| Reference Pattern | File / Module | Category | Operational Risk | Action Taken / Status |
| :--- | :--- | :--- | :---: | :--- |
| `dograh.com` | `ui/src/components/Footer.tsx` | CATEGORY I (Docs/Links) | LOW | Kept configurable via `NEXT_PUBLIC_DOCS_URL` & `GENQUANTAA_SUPPORT_URL` |
| `dograh-sdk` | `sdk/python/pyproject.toml` | CATEGORY F (SDK Package) | LOW | Rebranded to `genquantaa-sdk` |
| `@dograh/sdk` | `sdk/typescript/package.json` | CATEGORY F (SDK Package) | LOW | Rebranded to `@genquantaa/sdk` |
| `dograh-turn-secret` | `api/constants.py` | CATEGORY D (Env Var) | LOW | Overridden by `GENQUANTAA_TURN_SECRET` |
| `dograh_auth_token` | `ui/src/middleware.ts` | CATEGORY E (Cookie) | LOW | Replaced by `genquantaa_auth_token` |
| `pipecat` repo URL | `.gitmodules` | CATEGORY H (Submodule) | NONE | Kept as pinned open-source audio engine dependency |
| BSD-2-Clause header | `LICENSE` | CATEGORY J (License) | NONE | Retained as required by open-source license law |

---

## 3. Operational Independence Verification

1. **Database:** Connected to standalone PostgreSQL 17 database (`DATABASE_URL`). Zero external database calls.
2. **Redis:** Connected to standalone Redis instance with `GENQUANTAA_REDIS_PREFIX=gq:`. Zero external queue calls.
3. **Storage:** Connected to standalone MinIO instance (`genquantaa-voice-audio` bucket). Zero external S3 calls.
4. **Authentication:** 100% self-hosted local JWT authentication signed with `GENQUANTAA_JWT_SECRET`.
5. **Telephony & WebSockets:** Direct WebRTC / carrier WebSocket streaming with `GENQUANTAA_TELEPHONY_WS_TOKEN_SECRET`.
