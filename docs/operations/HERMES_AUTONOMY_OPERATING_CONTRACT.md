# Hermes Autonomy Operating Contract

**Status:** CURRENT — 2026-09-14  
**Organisational owner:** Björn  
**Control-plane authority:** Hermes Desktop is the only Chief and Dispatcher.  
**Execution scope:** VPS services, OpenClaw, n8n, shared knowledge and the
execution ledger are managed runtime capabilities. They never become a second
Hermes decision authority.

## Purpose

This contract converts the verified operating state into a repeatable working
agreement. It prevents rediscovery loops: a previously verified contract is
reused unless a relevant component, route, credential reference, workflow,
runtime release or network boundary changed.

`VERIFIED + NO RELEVANT MUTATION = REUSE`

Every material change follows this sequence:

`scope -> read current state -> backup -> change -> internal test -> rollback
proof -> commit/push -> deployed-state verification -> registry/shared_kb/ledger
writeback`.

## Authority and hard boundaries

| Area | Autonomous action | Hard boundary |
| --- | --- | --- |
| Hermes Desktop | Documentation, local tooling, tests and bounded control-plane improvements | Desktop remains the sole dispatcher; do not create a VPS brain. |
| VPS / OpenClaw | Read, backup, repair, deploy and verify canonical `ai-admin` runtime paths | Never stop a live path before a tested replacement is healthy. |
| n8n | Read registry, preserve exports, improve canonical internal contracts and run only safe synthetic tests | No customer messages, payment, shipping, bulk action, deletion, archive or production deactivation without a scoped backup/change/rollback proof. |
| Knowledge and ledger | Redacted writeback followed by deterministic readback and checksum recall | VPS `shared_kb` and `ai-admin` ledger are canonical; local stores are fallbacks only. |
| Providers | Local and simulated failover checks, config validation and observability | No secret disclosure, paid commitment or unbounded external provider test. |
| Communication / voice | Health, configuration and internal non-delivery checks | Real delivery, OAuth/2FA/CAPTCHA, QR/device pairing, microphone or speaker acceptance require the owner. |

## Canonical operating contracts

| Contract | Canonical route / state | Reuse condition | Reopen trigger |
| --- | --- | --- | --- |
| OpenClaw ownership | `openclaw-gateway.service`, process user `ai-admin`, loopback `127.0.0.1:18789` and `[::1]:18789` | service, unit and listener unchanged | unit, wrapper, listener, bridge or release mutation |
| Hermes runtime | `hermes-gateway.service`, versioned `ai-admin` release | service and release unchanged | release, unit, config or gateway mutation |
| n8n governance | 36-flow registry and canonical allowlist | workflow, n8n/runners and route configuration unchanged | workflow, queue/runtime, webhook, credential-reference or consumer mutation |
| n8n recovery | verified custom-format backup catalog; restore only in a controlled maintenance change | backup remains present and catalog-readable | workflow mutation or backup/restore procedure mutation |
| Provider resilience | configured fallback structure plus 47 isolated failover tests | provider/fallback configuration and runtime code unchanged | provider, model, fallback-chain or credential-reference mutation |
| Knowledge handover | VPS-first `shared_kb` and deterministic `ai-admin` ledger recall | bridge, DB schema and release unchanged | bridge, database, ledger, release or schema mutation |
| Shell test tooling | user-global `hermes-pytest` command backed by a managed Python 3.11 Hermes test runtime | command and managed runtime remain healthy | toolchain, Python compatibility or dependency-manifest mutation |

## Fresh non-interactive acceptance — 2026-09-14

| Check | Result | Evidence |
| --- | --- | --- |
| Hermes / OpenClaw runtime | PASS | Both system services were `active`; OpenClaw still owns only the two loopback listeners. |
| n8n runtime | PASS | `n8n`, `n8n-runners` and `n8n-postgres` each reported `healthy`. |
| n8n recovery artifact | PASS | `/home/ai-admin/.hermes/backups/n8n-governance-20260913/workflow-definitions.custom.dump` exists and `pg_restore -l` read its catalog from an isolated temporary container copy. No database was restored or changed. |
| Fallback implementation | PASS | Project-bound test environment: 47 provider-fallback, authentication-failover and failover-identity tests passed. |
| Runtime fallback declaration | PASS (structural) | The active Hermes configuration contains `fallback_providers`; values and credential material were not read or exposed. |
| Forced live-provider failure | PARTIAL by design | No active gateway was deliberately pointed at a failing provider, because that could create an external request or disrupt live work. The isolated test proves behavior; an instrumented disposable-session test is required after any provider-chain mutation. |
| System-shell test entry point | PASS | `hermes-pytest` is available from a fresh PowerShell and runs the managed Python 3.11 test runtime. The relevant provider-failover block passed 47 tests through that command. |

## Evidence, records and rollback

1. Records of operational completion are redacted, written via the active
   VPS-first `shared_kb` bridge, then read back.
2. Material handovers also require an `ai-admin` ledger entry and a deterministic
   checksum recall. A successful process, HTTP health response or registration
   alone is not an E2E acceptance claim.
3. Before changing OpenClaw, n8n, a gateway or a workflow: capture the exact
   unit/override/wrapper or versioned workflow export. Do not overwrite backups.
4. OpenClaw rollback restores the saved unit/wrapper/configuration and then
   restarts the canonical system service only after its replacement path is
   validated.
5. n8n rollback stops the stack only in a scoped maintenance change, restores
   the preserved custom dump with `pg_restore`, starts the stack, then rereads
   allowlist, versions, triggers and health. This contract does not authorize
   such a restore merely to test it.
6. Provider rollback returns the prior declared provider/fallback configuration,
   restarts only the affected controlled runtime and performs a local or
   simulated no-delivery check.

## Required owner interactions (not autonomous)

| Gate | Exact owner action | Acceptance evidence |
| --- | --- | --- |
| Telegram E2E | Send one agreed synthetic token from the owner account to the bot and permit one reply to the same owner account. | Inbound, processing, outbound and ledger correlation; no third-party delivery. |
| WhatsApp | Complete QR/device pairing for the owner account, then permit one self-canary only. | Pairing state plus bounded owner-only round trip. |
| Voice | Approve one local German microphone-to-STT-to-TTS-to-speaker test. | Capture, transcription, synthesized playback and local health trace. |
| OAuth / 2FA / CAPTCHA | Complete the provider's interactive page when it is actually presented. | Fresh authorized read/write evidence for the requested connector only. |

## Continuous autonomy rules

- Prefer targeted verification over repeated full audits.
- Maintain a tool/route registry with purpose, owner, start method, boundary,
  dependencies, evidence date, risk and rollback reference.
- Treat UUIDs, HMAC references, correlation IDs, workflow IDs and credential
  **names** as contracts: store redacted references in the n8n registry and
  shared knowledge; never persist or print secret values.
- A missing evidence layer is reported as `PARTIAL`, never upgraded by prose.
- Commit and push only verified documentation or code/configuration changes;
  verify the remote revision after push.
- Keep the global shell entry point thin and reproducible: `hermes-pytest`
  delegates to the managed compatible Python 3.11 runtime. Do not force the
  Hermes dependency set into an unsupported Python 3.14 interpreter merely to
  make a generic command succeed.

## Current closure status

The autonomous technical operating baseline is **PASS**. The system is ready
for bounded unattended internal work under this contract. It is **PARTIAL** for
real communication and physical voice solely because the explicit owner actions
above have not been performed. ChatGPT Projects remains a handover consumer via
the Google Drive master index and `shared_kb`; there is no direct Projects
content API in this runtime.
