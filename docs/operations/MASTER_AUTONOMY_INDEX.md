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
| Shared knowledge | CURRENT | VPS source-of-truth has 23,087 sources; local mirror has the same source count. | `/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db` |
| Execution ledger | CURRENT | Deterministic checksum recall is bound to the VPS ledger. | `/home/ai-admin/.hermes/state/execution-ledger.sqlite3` |
| OpenClaw | CURRENT | `ai-admin` gateway edge; do not treat it as a control plane. | `/home/ai-admin/.hermes/hermes-agent/tools/openclaw_employee_bridge.py` |
| n8n | CURRENT runtime / OWNER_GATE auth | Container stack is healthy and loopback-bound; MCP OAuth needs live confirmation. | `https://n8n.chrissisfashionstore.de/mcp-server/http` |
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
| n8n MCP | OWNER_GATE | OAuth confirmation and read-only discovery required. |
| Google Drive | OWNER_GATE | No active Drive connector/source inventory is available. |
| ChatGPT Projects API | NOT_AVAILABLE | Use this index and shared_kb as the transition layer. |

## OPEN_GATES

1. **n8n OAuth:** the owner must complete any visible OAuth reconnect/consent
   screen. Afterwards run a read-only workflow discovery and persist the
   timestamp, scope metadata, and redacted event reference.
2. **Google Drive:** the owner must authorize the Drive connector. Afterwards
   inventory the available documents and add title, project, summary, date,
   status, source, relevance, and canonical link to this index or its linked
   structured registry.

No secrets, credential values, customer communications, payments, or device
pairing artifacts are stored in this index.
