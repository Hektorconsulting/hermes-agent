# System Autonomy Ready — 2026-09-04

Status: READY for owner-goal-driven technical operation.

## Operating contract

```text
OWNER GOAL
  -> KNOWLEDGE RETRIEVAL (canonical VPS shared_kb)
  -> PLAN / DELEGATE
  -> EXECUTE (Codex, n8n, OpenClaw, VPS/SSH, APIs or MCP)
  -> VERIFY
  -> SELF-REPAIR / FALLBACK
  -> SYNTHESIZE
  -> PERSIST (Git, registry and shared_kb)
  -> REPORT
```

Hermes Desktop uses the shared-kb provider for new sessions. On the local
Windows runtime, the provider calls the canonical VPS bridge through the fixed
PowerShell SSH wrapper first; the local SQLite file remains a synchronized
cache/fallback. Completed turns, session boundaries and delegations use the
same TaskEnvelope and redacted write-back path.

## Current technical state

- One active governance policy: `canonical-owner-autonomy-policy.json`.
- Hermes Core, Codex, n8n, synthesis, TaskEnvelope, provenance, namespace
  isolation, Git persistence and owner-fork parity are verified and reused.
- Hermes Desktop model routing is free-first, catalog-valid and tool-capable
  with loaded fallbacks.
- VPS Hermes, active OpenClaw user runtime, health/self-healing timers,
  backup timer and Docker exposure guard are active.
- Control-plane backup and isolated restore rehearsal are complete; measured
  rehearsal RTO is `4,008 ms`.
- The obsolete unauthenticated public Hermes dashboard proxy is retired;
  the dashboard remains managed on loopback.
- OpenClaw server-side integration, A2A/result return, Telegram audio fixture
  and bounded backend paths are ready without external sends.

## Final operational proof

The canonical provider path was exercised with one redacted synthetic task:

```text
local Hermes shared_kb provider
  -> canonical VPS preflight = received
  -> canonical VPS write-back = PASS
  -> local mirror write-back = PASS
```

The existing verified Hermes Desktop -> Codex -> n8n -> Synthesis path is
reused as current evidence. No real customer, Telegram or WhatsApp message
was sent.

## Remaining owner interactions

Each item is external or physical and has no remaining technical preparation:

| ACTION | WHERE | WHAT TO CLICK/SCAN | EXPECTED RESULT |
|---|---|---|---|
| Install OpenClaw Mobile | Smartphone app store | Install the OpenClaw app | App is installed |
| Pair the device | OpenClaw Mobile and Gateway | Scan/approve the displayed pairing or QR flow | Device is authenticated |
| Enable private mobile route | Tailscale on smartphone | Sign in and approve the device | Private route is reachable |
| Grant device permissions | Smartphone settings | Allow only required microphone/notification permissions | Audio and notifications work |
| Pair WhatsApp when desired | WhatsApp/GOWA pairing screen | Scan the displayed QR code | WhatsApp session becomes connected |
| Complete provider consent if prompted | Google/provider login page | Approve OAuth, 2FA or CAPTCHA manually | Authorized session is available |
| Confirm ADAM external data target when needed | Supabase project/owner context | Confirm the intended external project and scope | Any later RLS or real-data operation has an authorized target |
| Activate real external communication | Respective channel | Explicitly enable/send the intended message | External delivery occurs under owner control |

These actions do not block the Hermes Desktop -> Codex/n8n control plane.
