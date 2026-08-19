# GenQuantaa Calling Agent — Call Initiation Architecture & CORS Debug Guide

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Auditor:** GenQuantaa Systems Engineering & Lead API Infrastructure Team  
**Target Repository:** `C:\Users\raksh\GENQUANTAA\genquantaa-calling-agent`  

---

## 1. Issue Summary & Root Cause Analysis

### Reported Problem
Clicking "Start Call" in the frontend phone call modal (`http://localhost:3010`) failed with the browser console error:
```
Access to fetch at 'http://localhost:8000/api/v1/telephony/initiate-call'
from origin 'http://localhost:3010'
has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### Root Cause
In `api/app.py`, when `DEPLOYMENT_MODE == "oss"`, CORS origins were previously configured as `["*"]` with `cors_allow_credentials = False`. When the browser makes a credentialed request (sending cookies or Authorization headers) from `http://localhost:3010` to `http://localhost:8000`, the browser rejects wildcard origins or uncredentialed CORS headers.

### Resolution Implemented
1. Updated `api/app.py` CORS middleware to explicitly allow `http://localhost:3010`, `http://127.0.0.1:3010`, `http://localhost:8000`, `http://127.0.0.1:8000`, and any `CORS_ALLOWED_ORIGINS` / `PUBLIC_BASE_URL`.
2. Set `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
3. Added `build: context: . dockerfile: ./api/Dockerfile` to `docker-compose.yaml` to ensure local API source changes compile directly into the `genquantaa-api` container image.

---

## 2. Full Call Initiation Execution Path

```
                                    BROWSER
                         (http://localhost:3010)
                                    │
                                    │ 1. OPTIONS Preflight
                                    ▼
                         FASTAPI CORS MIDDLEWARE
                           (`CORSMiddleware`)
                                    │
                                    │ 2. 200 OK (ACAO: http://localhost:3010, ACAC: true)
                                    ▼
                         FASTAPI ROUTER & AUTH
                       (`Depends(get_user)` JWT)
                                    │
                                    │ 3. Validated UserModel
                                    ▼
                        INITIATE CALL ENDPOINT
               (`api/routes/telephony.py:initiate_call`)
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   DB Telephony Lookup       Workflow Resolution       Quota Authorization
(`get_default_telephony_`)  (`db_client.get_workflow`) (`authorize_workflow_run`)
          │                         │                         │
          └─────────────────────────┼─────────────────────────┘
                                    │
                                    ▼
                         OUTBOUND TELEPHONY PROVIDER
                        (Cloudonix / Telnyx / Twilio)
                                    │
                                    ▼
                         CARRIER OUTBOUND DISPATCH
                                    │
                                    ▼
                            PSTN PHONE / WEBRTC
                                    │
                                    ▼
                       MEDIA WEBHOOK & STREAMING
                 (`/api/v1/telephony/ws/{provider}`)
                                    │
                                    ▼
                          PIPECAT VOICE PIPELINE
```

---

## 3. Step-by-Step Subsystem Breakdowns

### Step 1: Browser Origin & Request
- Frontend UI runs at `http://localhost:3010`.
- User clicks "Start Call" inside the agent call modal.
- Browser dispatches an HTTP `OPTIONS` preflight request followed by `POST http://localhost:8000/api/v1/telephony/initiate-call` with headers `Content-Type: application/json` and `Authorization: Bearer <jwt>`.

### Step 2: CORS Preflight & Header Matching
- FastAPI `CORSMiddleware` in `api/app.py` intercepts `OPTIONS` preflight request.
- Checks request origin (`http://localhost:3010`) against `cors_origins` allowlist.
- Returns HTTP 200 OK with:
  - `Access-Control-Allow-Origin: http://localhost:3010`
  - `Access-Control-Allow-Credentials: true`
  - `Access-Control-Allow-Headers: content-type,authorization`
  - `Access-Control-Allow-Methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT`

### Step 3: FastAPI Routing & Authentication
- FastAPI routes request to `POST /api/v1/telephony/initiate-call` in `api/routes/telephony.py`.
- Dependency `get_user` parses JWT token from Authorization header or cookie.
- Validates user identity and resolves `user.selected_organization_id`.

### Step 4: Initiate Call Endpoint Logic
- Resolves telephony configuration via `get_telephony_provider_by_id` or default org provider.
- Validates provider setup (`provider.validate_config()`).
- Resolves destination `phone_number` and target `workflow`.
- Checks organization concurrency limits (`call_concurrency.acquire_org_slot`).
- Creates `workflow_run` record in PostgreSQL (`workflow_runs` table).
- Evaluates quota authorization (`authorize_workflow_run_start`).

### Step 5: Provider Integration & Outbound Dispatch
- Constructs carrier webhook URL:  
  `https://<backend>/api/v1/telephony/<provider_webhook>?workflow_id=<id>&workflow_run_id=<run_id>&organization_id=<org_id>`
- Invokes provider outbound call method (`provider.initiate_call`).
- Cloudonix / Carrier dispatches SIP / PSTN call to target phone number.

### Step 6: Webhook & Media Pipeline Launch
- When phone connects, carrier opens media WebSocket stream (`WS /api/v1/telephony/ws/<provider>`).
- FastAPI launches Pipecat voice pipeline (`api/services/pipecat/run_pipeline.py`).
- Audio flows bidirectionally between caller and AI engine (STT -> LLM -> TTS).

---

## 4. Verification Commands & Preflight Results

```powershell
curl.exe -i -X OPTIONS "http://localhost:8000/api/v1/telephony/initiate-call" `
  -H "Origin: http://localhost:3010" `
  -H "Access-Control-Request-Method: POST" `
  -H "Access-Control-Request-Headers: content-type,authorization"
```

**Verified Response:**
```http
HTTP/1.1 200 OK
date: Wed, 19 Aug 2026 10:25:45 GMT
server: uvicorn
vary: Origin
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
access-control-max-age: 600
access-control-allow-credentials: true
access-control-allow-origin: http://localhost:3010
access-control-allow-headers: content-type,authorization
content-length: 2
content-type: text/plain; charset=utf-8

OK
```

---

## 5. Potential Telephony Error Diagnostics

Once CORS preflight succeeds, if `POST /api/v1/telephony/initiate-call` fails, inspect `docker compose logs --tail=200 api` for the following specific error codes:

| Detail / Error String | Root Cause | Remediation |
| :--- | :--- | :--- |
| `telephony_not_configured` | No default outbound telephony provider configured in organization settings. | Configure Cloudonix / Twilio / Telnyx settings under Organization Settings -> Telephony. |
| `telephony_configuration_not_found` | Explicit `telephony_configuration_id` does not exist or belong to org. | Select a valid active telephony configuration in the test modal. |
| `Phone number must be provided...` | Destination phone number field is empty and no default test number set. | Enter a valid target phone number in E.164 format (e.g. `+14155552671`). |
| `Workflow not found` | The `workflow_id` in request body is invalid or deleted. | Save and select an active workflow before placing a call. |
| `Concurrent call limit reached` | Active call limit for organization reached. | Wait for existing call to terminate or increase org concurrency limit. |
| `Failed to initiate call: ...` | Carrier API rejected outbound request (invalid credentials / SIP trunk error). | Check carrier API key, trunk domain, and subscriber credentials. |

---

## 6. Conclusion & Status

- **CORS Status:** **FIXED & VERIFIED**. Preflight OPTIONS request returns `Access-Control-Allow-Origin: http://localhost:3010` and `Access-Control-Allow-Credentials: true`.
- **API Status:** Healthy (`http://localhost:8000/api/v1/health` returning HTTP 200 OK).
- **Security Guardrail:** Zero secrets or credentials exposed in logs or documentation.
