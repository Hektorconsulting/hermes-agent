# OpenClaw server-side finalization evidence

Status: verified server-side, mobile deferred, 2026-09-04

This artifact records the current OpenClaw/Hermes backend proof without
sending Telegram, WhatsApp or customer messages.

## Runtime and ownership

- OpenClaw: v2026.9.1 (`ad6fe23`), active through the `ai-admin` user systemd
  unit and the Vault-backed watchdog launcher.
- Hermes integration configuration identifies Hermes as the master controller
  and OpenClaw as the managed execution integration.
- The disabled root OpenClaw unit is not the active runtime authority.
- OpenClaw self-heal, session-guard, upstream-watch and Telegram-canary timers
  are active.

## Available server paths

The existing FastAPI backend exposes the following internal control-plane
paths:

| Capability | Path | Evidence |
|---|---|---|
| Model routing | `POST /models/route` | read-only request returned `openrouter/free`, `allow_paid=false` |
| Runtime health | `GET /health/detailed` | FastAPI and Redis `healthy` |
| n8n MCP | `GET /mcp/health` | configured, file-backed token source present |
| Telegram backend | `GET /telegram/health` | text and voice enabled; bounded duration and file limits |
| Task intake | `POST /telegram/voice-task` | internal voice fixture returned HTTP 200 and `accepted=true` |
| Result return | `POST /execution-results` | authenticated internal read-only proof returned HTTP 200 |
| Agent cards | `GET /a2a/agent-card/{agent_id}` | all three normalized cards returned HTTP 200 |
| Integration discovery | `GET /integrations/status` | authenticated read-only response returned HTTP 200 |
| Agent readiness | `GET /agents/readiness` | authenticated read-only response returned HTTP 200 |

## Safety boundary

The internal voice fixture used a redacted test user and synthetic transcript.
It did not call Telegram send, WhatsApp send, customer messaging or a paid
model. Paperclip returned `auto_approve` only for that low-risk internal
ingestion fixture. External messages, QR pairing, OAuth and paid actions
remain blocked by policy.

## Corrective change

The three A2A card URLs previously pointed to non-existent `/a2a/openclaw`,
`/a2a/hermes` and `/a2a/paperclip-lite` paths. They now point to the
implemented normalized card endpoints and were backed up before the change.
