# Hermes Runtime Compatibility Closure — 2026-09-13

## Outcome

**PASS with one tracked, pre-existing test defect.** Hermes VPS runs the
versioned release `4302074af66e1e061fb25b84bf4cd4abecc5ab53` from
`/home/ai-admin/.hermes/releases/hermes-vps-runtime-compatibility-20260913`.
The gateway and both internal bridges now use Python 3.13.15, MCP 2.0.0, and
SQLite 3.53.1. Hermes Desktop remains the sole leading dispatcher.

## Verified runtime state

| Area | Result | Evidence |
| --- | --- | --- |
| Gateway ownership | PASS | `hermes-gateway.service` is active; its `ExecStart` and working directory both resolve to the versioned compatibility release. |
| MCP runtime | PASS | `hermes-shared-knowledge` and `hermes-openclaw-employee` are direct child processes of the gateway and both run from the same release Python environment. |
| MCP2 bridge contract | PASS | Both bridges completed an MCP `2025-11-25` handshake and exposed only their expected tool allowlists. |
| Shared knowledge | PASS | Staging preflight, redacted synthetic write-back and read-back completed through the shared knowledge bridge with `external_effect=none`. |
| OpenClaw boundary | PASS | The staging and active bridge both completed authenticated, read-only gateway health; no send, agent-execution, configuration, or restart tool is exposed. |
| SQLite runtime | PASS | Python 3.13.15 embeds SQLite 3.53.1. Read-only `PRAGMA integrity_check` returned `ok` for `state.db`, `cron/executions.db`, `kanban.db`, and the canonical execution ledger. |
| Regression tests | PARTIAL | 165 targeted tests passed. Two `EventBridge` baseline-poll tests fail identically under the preceding Python 3.11.15 / SQLite 3.50.4 runtime; they are a pre-existing test defect, not a compatibility regression. |

## Change and rollback

1. The former release remains intact at
   `/home/ai-admin/.hermes/releases/hermes-vps-cutover-20260913`.
2. The immediate rollback bundle is
   `/home/ai-admin/.hermes/backups/hermes-runtime-sqlite-cutover-20260913T171341Z`.
   It contains the preceding `config.yaml` and systemd drop-ins.
3. The compatibility staging worktree remains isolated at
   `/home/ai-admin/.hermes/staging/hermes-runtime-sqlite-20260913` for
   repeatable diagnosis; it is not an authority or a second control plane.
4. `platform-reuse-catalog` deliberately retains its separate legacy adapter;
   it was not in scope for this MCP2 bridge closure and was not changed.

## Residual risk and next action

- The two `EventBridge` tests should be repaired in a separately scoped source
  change with a deterministic file-change clock or polling trigger. Do not
  change the live gateway merely to force those assertions green.
- The provider warning for no-key-required VPS Ollama mode and human-operated
  messaging/device acceptance boundaries remain separate from this closure.
- Future runtime updates must repeat the narrow `SQLite version + integrity +
  MCP bridge handshake + shared_kb write/read-back` evidence set before
  promotion.
