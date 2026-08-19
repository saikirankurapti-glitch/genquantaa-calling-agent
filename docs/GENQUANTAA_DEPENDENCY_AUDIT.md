# GenQuantaa Calling Agent — Dependency & Compliance Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Baseline  
**Scope:** Complete Codebase Scan of `c:\Users\raksh\GENQUANTAA\genquantaa-calling-agent`  

---

## 1. Executive Summary

This document details every external dependency, hardcoded domain, third-party service credential, package registry reference, branding artifact, and licensing requirement inherited from the Dograh open-source fork.

All items listed here must be systematically remediated, replaced, or migrated to GenQuantaa-owned infrastructure according to the [GenQuantaa Migration Plan](file:///c:/Users/raksh/GENQUANTAA/genquantaa-calling-agent/docs/GENQUANTAA_MIGRATION_PLAN.md).

---

## 2. Comprehensive Dograh External Dependencies Audit

### 2.1 Dograh Hosted Domains & Service Endpoints
The codebase contains hardcoded references to Dograh hosted services:

| Domain / Endpoint | File Location | Purpose | Remediation Plan |
| :--- | :--- | :--- | :--- |
| `https://chat.dograh.com` | `ui/Dockerfile` | Chatwoot live support integration | Replace with GenQuantaa Chatwoot instance or remove. |
| `https://api-leads.dograh.com` | `ui/src/components/lead-forms/onboardingServiceClient.ts` | Public onboarding lead generation API | Replace with `https://api-leads.genquantaa.com` or custom backend endpoint. |
| `https://docs.dograh.com` | `ui/src/components/flow/AddNodePanel.tsx`, `ui/src/components/MCPSection.tsx` | User documentation links | Redirect to `https://docs.genquantaa.com`. |
| `https://app.dograh.com` | `ui/src/lib/utils.ts` | Multi-tenant auth redirect domain | Update to `https://app.genquantaa.com`. |
| `https://github.com/dograh-hq/dograh.git` | `docker-compose.yaml`, `.gitmodules` | Main repository & git submodules | Update git remote & submodules to `genquantaa` GitHub org. |
| `https://github.com/dograh-hq/pipecat.git` | `.gitmodules` | Voice pipeline engine submodule | Fork `pipecat` to `github.com/genquantaa/pipecat`. |

### 2.2 Telemetry, Analytics & Monitoring Secrets
The application ships with hardcoded third-party telemetry keys pointing to Dograh analytics accounts:

| Telemetry Service | Hardcoded Key / Value | Location | Remediation Plan |
| :--- | :--- | :--- | :--- |
| **PostHog Project Key** | `phc_ItizB1dP6yv7ZYobbcqrpxTdbomDA8hJFSEmAMdYvIr` | `docker-compose.yaml` (API & UI), `api/constants.py`, `ui/Dockerfile` | Replace with GenQuantaa PostHog key or disable telemetry. |
| **PostHog Host** | `https://us.posthog.com` / `https://us.i.posthog.com` | `docker-compose.yaml`, `ui/Dockerfile` | Re-point to GenQuantaa PostHog instance. |
| **Sentry Organization** | `dograh` | `ui/next.config.ts`, `ui/sentry.*.config.ts` | Update Sentry organization & DSN to GenQuantaa. |
| **Chatwoot Token** | `3fkFx2mCEjNHjM9gaNc4A82X` | `ui/Dockerfile` | Replace with GenQuantaa Chatwoot widget token. |

### 2.3 Authentication, Security & Cookie Secrets
Default security secrets and cookie keys contain Dograh identifiers:

| Secret / Identifier | Location | Default Value | Target Action |
| :--- | :--- | :--- | :--- |
| **Auth JWT Secret** | `.env`, `docker-compose.yaml` | `DograhLocalJwtSecret_2026_Strong_9xK7mP2qL8vR` | Generate random secret per deployment via `GENQUANTAA_JWT_SECRET`. |
| **Devops Secret Header** | `api/constants.py`, `api/routes/ops.py` | `X-Dograh-Devops-Secret` | Rename header to `X-GenQuantaa-Devops-Secret`. |
| **Auth Token Cookie** | `ui/src/middleware.ts`, `ui/src/lib/auth/server.ts` | `dograh_auth_token` | Change cookie key to `genquantaa_auth_token`. |
| **Auth User Cookie** | `ui/src/middleware.ts`, `ui/src/lib/auth/server.ts` | `dograh_auth_user` | Change cookie key to `genquantaa_auth_user`. |
| **Release Version Key**| `ui/src/hooks/useLatestReleaseVersion.ts` | `dograh-latest-release` | Update local storage key to `genquantaa-latest-release`. |

### 2.4 Package Registries & Container Images

| Registry / Package | Current Reference | Target Package Namespace |
| :--- | :--- | :--- |
| **Docker API Image** | `dograhai/dograh-api:latest` in `docker-compose.yaml` | `genquantaa/calling-agent-api:latest` |
| **NPM Client Package** | `@dograh/sdk` in `examples/typescript/package.json` | `@genquantaa/sdk` |
| **PyPI Voice SDK** | `tuner-pipecat-sdk==0.2.4` in `api/requirements.txt` | `genquantaa-pipecat-sdk` / custom PyPI wheel |
| **Embed Widget Script** | `/public/embed/dograh-widget.js` | `/public/embed/genquantaa-widget.js` |

### 2.5 UI Branding & Graphic Assets

- **Browser Favicons & Icons:** `ui/public/favicon.ico`, `ui/public/dograh-logo.png`, `ui/public/apple-icon.png`
- **Metadata Titles:** Next.js root metadata titled `"Dograh - Voice AI Platform"`
- **Inline Widget Branding:** CSS classes `.dograh-chat-panel`, `.dograh-chat-inline-cta` in `ui/public/embed/dograh-widget.js`
- **Telephony Form Placeholders:** `"dograh-carrier"`, `"dograh-app"` in `ui/src/components/telephony/*`

---

## 3. Licensing, Compliance & Commercialization Analysis

### 3.1 Open Source Licenses Inspection
The codebase incorporates components subject to open-source software licenses:

1. **Main Repository (`genquantaa-calling-agent`):**
   - **License:** BSD 2-Clause License
   - **Copyright Holder:** Copyright (c) 2025, Zansat Technologies Private Limited
2. **Pipecat AI Submodule (`pipecat/`):**
   - **License:** BSD 2-Clause License
   - **Copyright Holder:** Copyright (c) 2024–2026, Daily

### 3.2 BSD 2-Clause License Terms & Commercial Rights

> **Compliance Assessment:**  
> The BSD 2-Clause license is a **permissive open-source license**. Commercialization, proprietary distribution, modification, and re-branding of the source code are fully permitted under law.

#### Mandatory Compliance Requirements:
1. **Source Code Retention:** Any redistribution of modified or unmodified source code must retain the original copyright notice (`Copyright (c) 2025, Zansat Technologies Private Limited`) in header files where original code exists.
2. **Binary Distribution Notice:** Redistributions in binary or compiled form must reproduce the copyright notice and disclaimer in documentation or accompanying materials.
3. **No Trademark Grant:** The BSD 2-Clause license does **NOT** grant trademark rights. Using the name "Dograh", Dograh logos, or claiming official affiliation with Zansat Technologies is prohibited. Complete re-branding to **GenQuantaa Calling Agent** is required for commercial launch.

### 3.3 Third-Party Dependency License Breakdown

| Library / Component | License Type | Commercial Use Permitted? | Special Conditions |
| :--- | :--- | :--- | :--- |
| **Next.js 15** | MIT | Yes | None. |
| **React 19** | MIT | Yes | None. |
| **FastAPI** | MIT | Yes | None. |
| **PostgreSQL & pgvector** | PostgreSQL License (MIT-style) / PostgreSQL | Yes | Retain copyright notice. |
| **Redis 7** | RSALv2 / SSPLv1 (Dual) | Yes (for self-hosting application backend) | Cannot sell Redis itself as a managed database service. |
| **MinIO** | AGPLv3 | Yes (Network deployment behind API boundaries) | Do not modify MinIO source code directly; use official MinIO Docker container. |
| **Coturn** | BSD 3-Clause | Yes | Retain copyright notice. |

---

## 4. Remediation Checklist for Commercialization

- [ ] Audit and remove all hardcoded PostHog project keys from `docker-compose.yaml` and `api/constants.py`.
- [ ] Replace `chat.dograh.com` and `api-leads.dograh.com` endpoints with GenQuantaa domain URLs.
- [ ] Update `ui/src/middleware.ts` cookie names to `genquantaa_auth_token`.
- [ ] Replace all logo files in `ui/public/` with GenQuantaa brand identity assets.
- [ ] Update Docker Compose service image names to `genquantaa/calling-agent-api`.
- [ ] Update `.gitmodules` URL to point to GenQuantaa's GitHub repository org.
- [ ] Add explicit GenQuantaa copyright headers to all new modules while preserving original BSD notices in inherited files.
