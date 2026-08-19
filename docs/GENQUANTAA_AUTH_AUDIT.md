# GenQuantaa Calling Agent — Authentication & Organization Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits the complete authentication, session, cookie, user model, organization multi-tenancy, and authorization framework of GenQuantaa Calling Agent, establishing full GenQuantaa ownership while preserving the lightweight, high-performance local auth mechanism.

---

## 2. Authentication Architecture Audit

### 2.1 Login Flow
- **Endpoint:** `POST /api/v1/auth/login` (`api/routes/auth.py`)
- **Credentials:** Email + bcrypt password verification (`api/utils/auth.py`).
- **Token Generation:** Mints HS256 JWT signed with `GENQUANTAA_JWT_SECRET`.
- **Frontend Storage:** Next.js Route Handler `POST /api/auth/session` sets HttpOnly `genquantaa_auth_token` and `genquantaa_auth_user` cookies.

### 2.2 Signup Flow
- **Endpoint:** `POST /api/v1/auth/signup` (`api/routes/auth.py`)
- **User Creation:** Inserts `users` record with `is_superuser`, hashes password via bcrypt.
- **Organization Bootstrapping:** Provisions default organization (`OrganizationModel`), assigns `user.selected_organization_id`, and runs `ensure_organization_bootstrapped()`.

### 2.3 Logout Flow
- **Endpoint:** `POST /api/auth/logout` (Next.js Route Handler)
- **Action:** Clears `genquantaa_auth_token` and `genquantaa_auth_user` cookies with `maxAge: 0`.

### 2.4 JWT Tokens & Validation
- **Secret Key:** `GENQUANTAA_JWT_SECRET` (Fallback: `OSS_JWT_SECRET`)
- **Algorithm:** HS256
- **Payload:** `{"sub": user_id, "email": email, "exp": timestamp, "iat": timestamp}`
- **Validation:** `decode_jwt_token()` in `api/utils/auth.py` and `_handle_oss_auth()` in `api/services/auth/depends.py`.

### 2.5 Middleware & Client Session State
- **Middleware:** `ui/src/middleware.ts` checks `genquantaa_auth_token` cookie for all non-public routes.
- **Public Routes:** `/auth/login`, `/auth/signup`, `/embed`, `/api/config/*`.
- **Client Auth Provider:** `LocalProviderWrapper` (`ui/src/components/auth/LocalProviderWrapper.tsx`) syncs token state with React Query API client (`apiClient.ts`).

---

## 3. Data Models & Authorization

### 3.1 User Model (`users` Table / `UserModel`)
- `id` (BigInteger, Primary Key)
- `email` (String, Indexed, Unique)
- `password_hash` (String)
- `provider_id` (String, Unique)
- `is_superuser` (Boolean, Default: False)
- `selected_organization_id` (Integer, Foreign Key -> `organizations.id`)
- `created_at`, `updated_at` (DateTime UTC)

### 3.2 Organization Model (`organizations` Table / `OrganizationModel`)
- `id` (BigInteger, Primary Key)
- `name` (String)
- `provider_id` (String, Unique)
- `concurrent_call_limit` (Integer, Quota)
- `created_at`, `updated_at` (DateTime UTC)

### 3.3 Roles & Permissions Hierarchy
- **OWNER**: Full administrative control over organization, billing, API keys, and workflow deletion.
- **ADMIN**: Can manage workflows, telephony trunks, tools, knowledge bases, and campaign runs.
- **MEMBER**: Can view and trigger existing agent workflows.
- **VIEWER**: Read-only access to call logs and reporting dashboards.

### 3.4 API Authorization Scoping
- All FastAPI dependencies (`get_user`, `get_user_with_selected_organization`, `get_superuser`) extract identity from `Authorization: Bearer <JWT>` or `X-API-Key` headers.
- Multi-tenant query isolation is enforced server-side via `user.selected_organization_id`.
