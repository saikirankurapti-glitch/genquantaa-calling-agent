# GenQuantaa Calling Agent — Telephony Security & Network Architecture

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Security Specification  

---

## 1. Telephony Media WebSocket Capability Token Security

### 1.1 HMAC Token Verification
- **Secret Variable:** `GENQUANTAA_TELEPHONY_WS_TOKEN_SECRET`
- **Enforcement Variable:** `GENQUANTAA_TELEPHONY_WS_TOKEN_ENFORCE` (`true` / `false`)
- **Token Minting:** `mint_ws_token()` calculates HMAC-SHA256 over canonical ID string `workflow_id:organization_id:workflow_run_id`.
- **Carrier Transport:** Token is appended as a trailing path segment:
  `/api/v1/telephony/ws/{workflow_id}/{organization_id}/{workflow_run_id}/{hmac_token}`
- **Constant-Time Verification:** `verify_ws_token()` uses `hmac.compare_digest()` to prevent timing side-channel attacks.

---

## 2. Coturn TURN Server Architecture

### 2.1 WebRTC NAT Traversal Configuration
- **Server:** Coturn 4.8.0 (`coturn/coturn:4.8.0`)
- **Host Variable:** `GENQUANTAA_TURN_HOST` (Fallback: `TURN_HOST`)
- **Secret Variable:** `GENQUANTAA_TURN_SECRET` (Fallback: `TURN_SECRET`)
- **Ports:** `3478` (STUN/TURN UDP & TCP), `5349` (TURNS TLS), `49152-49200/udp` (RTP media relay range).
- **Credentials:** Time-limited REST API credentials generated via HMAC-SHA1 signature over `username:timestamp`.

---

## 3. Ingress & Tunnel Architecture

### 3.1 Cloudflare Tunnel (`cloudflared`)
- **Role:** Optional ingress helper for local development and carrier webhook routing behind NAT/firewalls.
- **Routing:** Public HTTPS URL -> `http://api:8000`.
- **Production Mode:** Optional; production deployments run behind standalone Nginx / HAProxy / AWS ALB with public TLS certificates.
