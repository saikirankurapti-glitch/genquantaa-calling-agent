# GenQuantaa Calling Agent — Telephony Architecture Specification

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Telephony Specification  

---

## 1. Executive Summary

This document defines the real-time telephony, WebSockets audio transport, WebRTC relay, and call control architecture for **GenQuantaa Calling Agent**.

The platform supports high-concurrency, low-latency inbound and outbound voice calls across multiple telecom carriers and custom SIP trunks.

---

## 2. End-to-End Telephony Call Flow

```
[ Inbound Call Flow ]
PSTN Phone ---> Telecom Carrier (Telnyx/Twilio/Vonage)
                    │
                    │ 1. HTTP POST Webhook
                    ▼
          GenQuantaa Ingress API (/api/v1/telephony/webhook/{provider})
                    │
                    │ 2. DID Lookup & Workflow Resolution
                    │ 3. Generate HMAC Signed WebSocket URL
                    ▼
          Returns Carrier TwiML / TeXML Response:
          <Response><Connect><Stream url="wss://api.genquantaa.com/api/v1/ws/call/{run_id}?token={hmac}" /></Connect></Response>
                    │
                    │ 4. WebSocket Upgrade Handshake
                    ▼
          GenQuantaa Pipecat Voice Pipeline Engine (Audio Frame Exchange)

================================================================================

[ Outbound Call Flow ]
GenQuantaa Campaign / REST API Trigger (/api/v1/calls/outbound)
                    │
                    │ 1. Validate Org Concurrency & Phone Number
                    │ 2. Create Workflow Run (State: Initialized)
                    ▼
          Carrier Outbound API (Telnyx Call Control / Twilio REST API)
                    │
                    │ 3. Dial PSTN Target -> Answer Event
                    ▼
          Carrier Connects Call to Signed GenQuantaa WebSocket Endpoint
```

---

## 3. Supported Telephony Providers & Trunks

### 3.1 Carrier Feature Integration Matrix

| Carrier / Protocol | Inbound Webhooks | Outbound Dialing | WebSockets Audio Stream | Call Transfer Method |
| :--- | :--- | :--- | :--- | :--- |
| **Telnyx** | TeXML Webhook | Call Control API | Bidirectional WebSocket (Mulaw 8kHz) | Telnyx Transfer API Command |
| **Twilio** | TwiML Webhook | REST Calls API | Bidirectional Media Streams | `<Redirect>` / `<Refer>` |
| **Vonage** | NCCO Webhook | Voice API | WebSocket Audio Stream | NCCO Transfer Action |
| **Plivo** | PHLO / XML | Call API | WebSocket Stream | XML `<Redirect>` |
| **Cloudonix** | SIP / REST | Outbound Trunk | WebSockets Audio | SIP REFER |
| **Vobiz** | Webhook | REST Dial | Media WebSocket | Call Transfer Webhook |
| **Asterisk ARI** | Stasis App | ARI Originate | External Media Socket | ARI Bridge / Channel Transfer |

---

## 4. Audio Pipeline & WebSocket Protocol

### 4.1 WebSocket URL HMAC Signing (`TELEPHONY_WS_TOKEN_SECRET`)
To prevent unauthorized socket connections, all carrier audio streams require a signed token in the WebSocket connection URL:

$$\text{Token} = \text{HMAC-SHA256}(\text{TELEPHONY\_WS\_TOKEN\_SECRET}, \text{workflow\_run\_id} \mathbin{\Vert} \text{timestamp})$$

- Configured via `TELEPHONY_WS_TOKEN_SECRET` and enforced when `TELEPHONY_WS_TOKEN_ENFORCE="true"`.

### 4.2 Audio Encoding & Frame Formats
- **Default Telephony Codec:** G.711 Mu-Law (PCMU) 8,000 Hz, 8-bit mono (20ms frame chunks = 160 bytes per packet).
- **WebRTC Codec:** Opus 48,000 Hz / PCM 16,000 Hz 16-bit mono.
- **Resampling Engine:** High-fidelity audio resampling using `soxr` and `resampy` to bridge 8kHz telephony audio to 16kHz STT/TTS models.

---

## 5. WebRTC & NAT Traversal Architecture (Coturn)

For browser-based agent testing, direct WebRTC audio streams require STUN/TURN servers to traverse NATs and firewalls.

### 5.1 Coturn TURN Server Configuration
- **Docker Service:** `coturn` (`coturn/coturn:4.8.0`)
- **Listening Ports:** `3478` (STUN/TURN UDP/TCP), `5349` (TURNS TLS), Relay UDP Range `49152-49200`.
- **Authentication:** Dynamic REST API credentials generated with SHA-1 HMAC based on `TURN_SECRET`.

```env
ENABLE_COTURN=true
TURN_HOST=turn.genquantaa.com
TURN_SECRET=genquantaa-turn-secret-production
FORCE_TURN_RELAY=false
```

---

## 6. Call Transfer Architecture

GenQuantaa supports live human transfer during an active AI call via function tool calls (`transfer_call`):

1. **AI Decides Transfer:** LLM emits a function call tool execution `transfer_call(phone_number="+15550199")`.
2. **Execution Handler:**
   - **Twilio:** Sends TwiML `<Response><Dial>+15550199</Dial></Response>`.
   - **Telnyx:** Calls Telnyx Call Control API `POST /v2/calls/{call_control_id}/actions/transfer`.
   - **Asterisk ARI:** Executes channel redirect to Asterisk dialplan context or bridges channel to external SIP extension.
3. **Session Teardown:** Pipeline gracefully closes STT/TTS streams, logs call transfer status, and updates `call_logs` state.

---

## 7. Public Reachability & Inbound Webhooks

### 7.1 Cloudflare Tunnel (`cloudflared`) — Local Development
- For local dev behind NATs, `cloudflared` creates a secure tunnel pointing to `http://api:8000`.
- Metrics endpoint on `http://127.0.0.1:2000` allows the API to automatically discover ephemeral `*.trycloudflare.com` URLs for incoming carrier webhooks.

### 7.2 Production Ingress (Nginx Proxy + SSL)
- In production, incoming carrier webhooks land on `nginx` (Ports 80/443).
- Nginx terminates TLS using Let's Encrypt / custom certs and proxies requests to FastAPI Uvicorn workers on port 8000.
