# GenQuantaa Calling Agent — Telephony Infrastructure Audit

**Document Version:** 1.0.0  
**Date:** August 19, 2026  
**Status:** Approved Audit Specification  

---

## 1. Executive Summary

This document audits the telephony providers, PSTN carrier webhooks, WebRTC media streams, Asterisk ARI integrations, DTMF processing, call transfer protocol, and audio recording flow in GenQuantaa Calling Agent.

---

## 2. Telephony Provider Support Matrix

| Provider | Inbound | Outbound | Webhook Endpoint | Media Stream Transport | Auth Method | Recording | Transfer | DTMF | Production Readiness | Local Test Status |
| :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Twilio** | YES | YES | `/api/v1/telephony/twilio/webhook` | TwiML `<Connect><Stream>` | Account SID + Auth Token / HMAC | YES | YES | YES | READY | Unconfigured |
| **Telnyx** | YES | YES | `/api/v1/telephony/telnyx/webhook` | TeXML / Call Control WS | API Key + Public Key | YES | YES | YES | READY | Unconfigured |
| **Vonage** | YES | YES | `/api/v1/telephony/vonage/webhook` | NCCO WebSocket | Application ID + Private Key | YES | YES | YES | READY | Unconfigured |
| **Plivo** | YES | YES | `/api/v1/telephony/plivo/webhook` | XML `<Stream>` | Auth ID + Auth Token | YES | YES | YES | READY | Unconfigured |
| **Vobiz** | YES | YES | `/api/v1/telephony/vobiz/webhook` | SIP/RTP Stream | SIP Trunk Credentials | YES | YES | YES | READY | Unconfigured |
| **Cloudonix** | YES | YES | `/api/v1/telephony/cloudonix/webhook` | SIP CXML | Domain Token / API Key | YES | YES | YES | READY | Unconfigured |
| **Asterisk ARI** | YES | YES | Stasis Application (`/ari/events`) | External Media Channel (`unicast`) | HTTP Basic Auth + WebSocket | YES | YES | YES | READY | Local Test Path |
| **WebRTC / SIP** | YES | YES | Browser PeerConnection | WebSockets + TURN (`coturn`) | JWT Session Token | YES | N/A | YES | READY | TESTED & READY |

---

## 3. Telephony Subsystem Components

1. **Carrier Inbound Router:** `api/routes/telephony.py` maps carrier webhook payloads to target workflows via DID or SIP header matching.
2. **Outbound Dispatcher:** `api/services/telephony/factory.py` instantiates provider clients based on `telephony_configurations`.
3. **Media WebSocket Server:** `api/routes/telephony.py` (`/api/v1/telephony/ws/{workflow_id}/{organization_id}/{workflow_run_id}`) handles dual-channel PCM 16kHz audio exchange.
4. **Call Transfer Manager:** `api/services/telephony/call_transfer_manager.py` executes SIP REFER or carrier REST transfer primitives (`blind`, `attended`).
5. **Coturn TURN Server:** `coturn/coturn:4.8.0` provides WebRTC NAT traversal and ICE candidate relay over UDP/TCP ports 3478 & 5349.
