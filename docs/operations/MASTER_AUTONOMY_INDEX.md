# Master Autonomy Index

**Status:** CURRENT snapshot, 2026-09-13  
**Authority:** Björn owner objective; Hermes Desktop is the sole Chief and
Dispatcher. The VPS provides runtime, canonical knowledge, recovery, and
required gateways only.

This is the canonical transition index for the autonomy stack. It links to
the source systems and preserves their classification; it is not a duplicate
knowledge store. Current claims must be re-read from runtime before use.

## CURRENT_STATE

| Surface | Classification | Current evidence | Canonical reference |
| --- | --- | --- | --- |
| Hermes Desktop | CURRENT | Leading control plane; Desktop shared-kb preflight reaches VPS knowledge. | `C:\Hermes\config.yaml` |
| Hermes VPS | CURRENT | `hermes-gateway.service` and watchdog active; gateway loopback-only. | `/home/ai-admin/.hermes/` |
| Shared knowledge | CURRENT | VPS source-of-truth has 23,089 sources; local mirror is a fallback rather than an authority. | `/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db` |
| Execution ledger | CURRENT | Deterministic checksum recall is bound to the VPS ledger. | `/home/ai-admin/.hermes/state/execution-ledger.sqlite3` |
| OpenClaw | CURRENT / HARDENED | Exactly one canonical systemd path (`User=ai-admin`) owns the gateway; listener is loopback-only and restart recovery was tested. | `/etc/systemd/system/openclaw-gateway.service` |
| Hermes VPS release | CURRENT / RUNTIME COMPATIBILITY PASS | Gateway, shared_kb bridge and OpenClaw bridge run from one versioned release environment: Python 3.13.15, MCP 2.0.0 and SQLite 3.53.1; deterministic ledger recall is active. | `/home/ai-admin/.hermes/releases/hermes-vps-ledger-recall-20260913` |
| n8n | CURRENT runtime / CURRENT auth | Container stack is healthy and loopback-bound; OAuth-backed MCP discovery returned 36 workflows. | `https://n8n.chrissisfashionstore.de/mcp-server/http` |
| Google Drive | CURRENT auth / CURRENT read | OAuth-backed profile, listing, recent-document read, and focused project discovery succeeded. | `MASTER AUTONOMY INDEX — CURRENT 2026-09-13` |
| ADAM | CURRENT project source | Canonical workspace; preserve its worktree boundary. | `C:\Users\Björn\Documents\Codex\repos\ADAM` |

## ARCHITECTURE_DECISIONS

1. Hermes Desktop is the only Chief/Dispatcher. VPS Hermes is restricted to
   runtime, knowledge, recovery, and gateway responsibilities.
2. `shared_kb` is VPS-first. A local database is a mirror/fallback and does
   not supersede the VPS knowledge database.
3. Codex is the technical executor. n8n is the deterministic workflow layer;
   OpenClaw is the communication and device edge.
4. Completion persistence requires a redacted write-back followed by a fresh
   VPS and local read-back. Checksum-backed ledger recall is required for
   material Hermes handovers.
5. The owner-policy JSON is the governing policy. Historical
   `hermes-orchestration` material is retained only as technical provenance.

## HISTORY_INDEX

| Class | Scope | Handling |
| --- | --- | --- |
| HISTORY | Earlier handovers, reports, backups, and source imports | Evidence only; never override current runtime readback. |
| SUPERSEDED | Legacy blanket-approval and duplicate-control-plane rules | Non-governing; retain when needed for traceability and recovery. |
| OUT_OF_SCOPE | Imported fixtures, examples, vendor material | Keep classified in shared_kb; do not operationalize. |

The canonical knowledge store currently classifies 22,800 sources as
`DISCOVERED`, 62 as `VERIFIED`, and 225 as `OUT_OF_SCOPE`. Treat this index as
navigation, not a claim that every discovered source is current.

## PROJECT_INDEX

| Project | Source system | Canonical location | Role |
| --- | --- | --- | --- |
| Hermes | Hermes | `C:\Hermes\hermes-agent` | Runtime, bridge, operations documentation. |
| Hermes Desktop | Windows | `C:\Hermes` | Sole control plane and local configuration. |
| ADAM | Git / local workspace | `C:\Users\Björn\Documents\Codex\repos\ADAM` | Independent owner objective; do not mutate a dirty checkout without scoped work. |
| Platform Reuse | Git / local workspace | `C:\Users\Björn\Documents\Codex\repos\platform-reuse-core` | Reuse inventory and compact control-plane mirror. |
| OpenClaw | VPS edge | `/home/ai-admin/.hermes/hermes-agent` | Authenticated communications/device edge. |
| n8n | VPS Docker | `127.0.0.1:5678` | Workflows and controlled integrations. |

## INTEGRATION_REGISTRY

| Integration | State | Boundary / next evidence |
| --- | --- | --- |
| Shared-KB remote bridge | PASS | Windows wrapper → VPS bridge → canonical DB; redacted preflight and write-back tested. |
| Execution-ledger recall | PASS | VPS ledger path and checksum recall verified. |
| OpenClaw A2A | PASS historical + current process evidence | Preserve loopback/auth boundary; no external delivery test. |
| n8n MCP | PASS | OAuth session and live read-only workflow discovery verified; 36 workflows are visible. |
| n8n workflow registry | PASS | All 36 live MCP-visible workflows are classified without mutation; legacy candidates require a separate change set. | `docs/operations/N8N_WORKFLOW_REGISTRY_20260913.md` |
| Google Drive | PASS | OAuth session plus live profile/list/read/search verification completed; curated technical sources are indexed in the native Google Drive master index. |
| n8n Contract Memory | CURRENT | Machine-readable endpoint, schema, HMAC-reference, UUID/idempotency and canonical-route registry. Contract facts are reused without re-discovery absent a relevant mutation. | `docs/operations/N8N_CONTRACT_REGISTRY.json` |
| ChatGPT Projects API | NOT_AVAILABLE | Use this index and shared_kb as the transition layer. |
| n8n governance / allowlist | PASS (retested) | Björn owns all 36 flows; a verified 9-flow canonical ADAM route is documented. HMAC and idempotent receipt canaries pass. Fresh metadata-only readback found no running or waiting executions in the Event-Intake or DLQ flows; earlier execution IDs have been finalized/retained away. | `docs/operations/N8N_WORKFLOW_GOVERNANCE_20260913.md` |
| Hermes runtime compatibility | PASS | MCP2 bridge handshake, shared_kb synthetic write/read-back, authenticated read-only OpenClaw health, and read-only integrity checks for the four Hermes SQLite databases passed. | `docs/operations/HERMES_RUNTIME_COMPATIBILITY_CLOSURE_20260913.md` |
| Architecture handover map | CURRENT / VERIFIED | Three versioned Mermaid maps, a machine-readable component/edge registry, glossary and evidence matrix now describe the actual Desktop/VPS runtime, data/recovery and integration boundaries. A manually started root SSH OpenClaw bridge found during mapping was stopped only after the canonical `ai-admin` release bridge was verified; exactly one canonical bridge remains. | `docs/architecture/` |
| Autonomy operating contract | CURRENT / VERIFIED | Reuse rule, authority boundaries, recovery/rollback evidence, provider-failover test boundary and the remaining human gates are consolidated. Fresh runtime checks found both gateway services active, all three n8n containers healthy and the n8n custom backup catalog readable. | `docs/operations/HERMES_AUTONOMY_OPERATING_CONTRACT.md` |

## OPEN_GATES

No owner authentication gate is currently open for n8n or Google Drive.

The remaining technical capability boundary is **ChatGPT Projects API**: no
direct API connector is available in this runtime. The Google Drive master
index and shared_kb remain the governed transition layer. A new interactive
gate arises only if a future operation requires OAuth re-consent, CAPTCHA/2FA,
device/QR pairing, payment, customer communication, or an external message.

## PRODUCTION_HARDENING_20260913

- **OpenClaw ownership and exposure:** PASS. The systemd unit running as
  `ai-admin` is the sole canonical gateway path. The obsolete failed user-unit
  was disabled and reset; it no longer competes for the state directory.
  OpenClaw now listens only on `127.0.0.1` and `::1`. A controlled `SIGKILL`
  recovery test created a new main PID, restored the listener, and passed the
  authenticated Hermes employee-bridge health read.
- **n8n:** PASS for OAuth-backed discovery and registry. The registry has five
  `ACTIVE_RETAIN`, sixteen `LEGACY_REVIEW`, four `DISABLED_RETAIN`, and eleven
  `ARCHIVE_CANDIDATE` workflows. No workflow was changed.
- **Communications and voice:** PARTIAL by design. GOWA and Speaches internal
  health checks pass. Telegram inbound/outbound, WhatsApp QR pairing, and
  physical microphone-to-speaker E2E remain explicit human-interaction tests.
- **Providers:** PARTIAL. Primary OpenRouter canary and local Ollama fallback
  canary pass; an automatic failover-chain injection has not been performed.

## AUTONOMY_OPERATING_CONTRACT_20260914

`HERMES_AUTONOMY_OPERATING_CONTRACT.md` is the governing execution agreement
for future autonomous technical work. Its key rule is
`VERIFIED + NO RELEVANT MUTATION = REUSE`; therefore it replaces repetitive
full rechecks with contract-targeted verification after relevant mutations.
It records a fresh non-interactive recovery check: the retained n8n custom dump
was catalog-read successfully without a restore, and the project-bound provider
failover suite passed 47 tests. A forced failure in the live gateway remains
intentionally unperformed; repeat it only in a disposable session after a
provider-chain change.

No secrets, credential values, customer communications, payments, or device
pairing artifacts are stored in this index.
