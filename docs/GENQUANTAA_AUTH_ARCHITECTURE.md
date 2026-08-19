# GenQuantaa Calling Agent — Authentication & Authorization Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Architecture Specification  

---

## 1. Executive Summary

This document describes the end-to-end authentication, session state management, JWT signing, multi-tenant organization authorization, and security isolation framework for GenQuantaa Calling Agent.

---

## 2. Authentication & Authorization Pipeline

```
[ Browser / API Client ]
          │
          │ 1. Credentials / API Key / Cookie
          ▼
┌────────────────────────────────────────────────────────┐
│  Next.js Middleware (`ui/src/middleware.ts`)          │
│  - Inspects `genquantaa_auth_token` HttpOnly Cookie   │
│  - Passes public paths (`/auth/*`, `/embed/*`)         │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 2. Forwarded Authorization: Bearer <JWT>
                         ▼
┌────────────────────────────────────────────────────────┐
│  FastAPI Security Layer (`api/services/auth/depends`) │
│  - Decodes JWT using `GENQUANTAA_JWT_SECRET`          │
│  - Resolves `UserModel` & `selected_organization_id`   │
└────────────────────────┬───────────────────────────────┘
                         │
                         │ 3. Server-Side Scoped Database Queries
                         ▼
┌────────────────────────────────────────────────────────┐
│  PostgreSQL 17 Database (`users`, `organizations`)     │
│  - Enforces tenant isolation on `organization_id`      │
└────────────────────────────────────────────────────────┘
```

---

## 3. Key Lifecycle Specifications

### 3.1 Token Lifecycle
1. **Creation:** Issued upon successful `POST /api/v1/auth/login` or `signup`. Signed with `GENQUANTAA_JWT_SECRET` (HS256).
2. **Expiration:** Configurable via `GENQUANTAA_ACCESS_TOKEN_EXPIRY_HOURS` (Default: 720 hours / 30 days).
3. **Validation:** Validated on every protected endpoint via `decode_jwt_token()`.

### 3.2 Cookie Lifecycle
- `genquantaa_auth_token`: Stores HS256 JWT string. Options: `HttpOnly: true`, `SameSite: Lax`, `Path: /`, `Secure` in production.
- `genquantaa_auth_user`: Stores JSON stringified user metadata for client-side navbar rendering.

### 3.3 Multi-Tenant Organization Boundary
- Every `UserModel` references a `selected_organization_id`.
- FastAPI endpoints enforce server-side query filtering on `organization_id=user.selected_organization_id`.
- Client-supplied `organization_id` parameters are never trusted without backend validation.

---

## 4. Security & Environment Configuration

### 4.1 Environment Variables
```env
GENQUANTAA_JWT_SECRET=GenQuantaaLocalJwtSecret_2026_Strong_9xK7mP2qL8vR
GENQUANTAA_ACCESS_TOKEN_EXPIRY_HOURS=720
GENQUANTAA_AUTH_COOKIE_NAME=genquantaa_auth_token
GENQUANTAA_SESSION_COOKIE_NAME=genquantaa_session
```

### 4.2 Security Rules
1. **No Credentials in Logs:** Passwords (hashed with bcrypt) and JWT secrets are excluded from loguru output.
2. **Server-Side Authorization:** Role and organization checks are evaluated exclusively inside FastAPI handlers.
3. **Invalid Token Rejection:** Expired or tampered JWTs immediately return `HTTP 401 Unauthorized`.
