# Autonomous control plane

## Durable authority

The canonical task-state store is the VPS SQLite ledger at
`/home/ai-admin/.hermes/state/execution-ledger.sqlite3`.  It is intentionally
separate from `shared_kb`: the ledger records executable state and evidence;
`shared_kb` remains the durable redacted knowledge authority.

`tools/execution_ledger.py` is the native Hermes/VPS CLI.  The Codex-side
`tools/remote_execution_ledger.py` sends base64-framed JSON only through the
fixed Hostinger wrapper, so task material is not shell-interpolated and the
database never leaves the VPS.  `tools/control_plane_mcp.py` exposes the same
operations to Codex as a stdio MCP.

The ledger supports idempotent run creation, leased claims, append-only
events, recovery/retry/reconfiguration/redeployment states, dynamic capability
registration, the two persistent handover checksums, and SQLite online backup.
Sensitive mapping keys are redacted before they are written.

## Normal execution and recovery

Every material technical operation records a `TaskEnvelope v2` and proceeds:

`precheck -> state capture -> change -> deploy -> verify -> diagnose -> repair
-> retry -> alternative/reconfigure/redeploy -> verify`.

Rollback is recorded and kept restorable, but is selected only when continued
repair is unsafe or technically inferior.  Claim conflicts, idempotency
duplicates, and recovery paths are events, not lost work.

## Runtime ownership and self-healing

The service ownership model is deliberate:

- `hermes-gateway.service` is a system service.
- `openclaw-gateway.service` is an `ai-admin` user service.  The historical
  system unit is not its active owner.
- `autonomous-runtime-watchdog.timer` invokes
  `tools/runtime_watchdog.py` every five minutes.  It checks the real owner
  unit and the loopback OpenClaw listener, restarts only the unhealthy owner,
  rechecks within a bounded time budget, and appends redacted evidence to
  `/home/ai-admin/.hermes/state/runtime-watchdog.jsonl`.

The unit files live in `deploy/systemd/`; deploy them with `systemctl
daemon-reload` and enable the timer.  The watchdog does not expose a new port,
does not store credentials, and leaves systemd journal evidence for every
repair.

## Capability adoption

New technical capabilities are adopted through
`DISCOVER -> VERIFY -> AUTHENTICATE -> REGISTER -> EXECUTE`.  The registry is
evidence-bearing rather than an allowlist: it records observed authentication
state, risk, performance, cost/contract implications, and recovery behaviour.
Any paid commitment, fresh credential consent, identity verification, or
intentional external business effect remains an owner action.
