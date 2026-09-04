# Hermes recovery defaults

Status: active operational baseline, 2026-09-04

This runbook records the recovery defaults for the owner-controlled Hermes
runtime. It is deliberately operational rather than a claim that a complete
restore rehearsal has already been performed.

## Recovery ownership

- Hermes Desktop is the owner-facing control and orchestration layer.
- Hermes VPS services are the backend/runtime layer.
- The VPS shared knowledge database is canonical; local copies are mirrors or
  backups.
- Vault or the already configured secret store is authoritative for runtime
  secret values. Backups and logs contain references and metadata only.
- OpenClaw's active user systemd unit is authoritative. The separate root
  `openclaw-gateway.service` is disabled/inactive legacy configuration and is
  not part of the active start path.

## Current recovery controls

| Control | Current state | Recovery behavior |
|---|---|---|
| Hermes gateway | `Restart=always`, bounded start/stop timeouts | systemd restarts the service after failure |
| OpenClaw gateway | active user unit, `Restart=always`, 120-second watchdog | watchdog launcher checks readiness and systemd restarts on failure |
| OpenClaw guards | self-heal, session-guard, upstream-watch and Telegram-canary timers active | timer-driven checks and corrective actions remain bounded by their scripts |
| Docker exposure | `hermes-docker-exposure-guard.service` plus five-minute timer active | private gateway allows are reconciled before public drops; admin ports 81/8082 fail closed |
| Control-plane backup | existing `hektor-control-plane-backup.sh` and backup timer | creates chmod-600 archives containing runtime metadata, databases, NPM state and Vault snapshot |
| Health observation | existing Hermes stack health service/timer | emits bounded service and endpoint observations for recovery handling |
| Knowledge persistence | canonical SQLite database plus local mirror | write-back is redacted, namespace-scoped and content-addressed for retry safety |

## Defaults

These are working defaults for future Hermes automation. They may be tightened
by a current owner directive or by a service-specific contract.

```json
{
  "backup_retention_count": 7,
  "backup_file_mode": "0600",
  "rpo_target": "last successful scheduled backup",
  "rto_target": "bounded service restart first; restore only after an isolated recovery decision",
  "restore_mode": "non-destructive rehearsal or explicit rollback target",
  "secret_policy": "restore references and secret-store bindings, never literal secret values",
  "knowledge_policy": "write-back with task/session/run provenance and namespace scope",
  "network_policy": "public edge only for intentional 80/443 routes; admin and gateway paths private",
  "restart_policy": "systemd-managed, bounded and observable",
  "escalate_only_for": [
    "interactive OAuth, 2FA or CAPTCHA",
    "physical device or QR pairing",
    "missing external permission",
    "irreversible deletion without verified restore",
    "real customer/payment communication",
    "new paid commitment"
  ]
}
```

## Recovery sequence

For a technical failure Hermes should use:

```text
DETECT -> LOG(redacted) -> RETRY boundedly -> SELF-HEAL -> VERIFY -> WRITE-BACK
```

If a service cannot recover, preserve the current evidence and use the newest
known-good backup or configuration snapshot. A production restore is not
silently substituted for a rehearsal: an isolated restore target or a clearly
identified rollback target must be selected so the canonical runtime is not
overwritten accidentally.

## Rollback inventory

The 2026-09-04 hardening backups include the pre-change Hermes orchestration
skill, Docker exposure rules, the shared knowledge database state, and the
OpenClaw systemd units. Their exact paths and hashes remain in the task
write-back and source registry; this document intentionally does not contain
secret values.

## Known follow-up

The remaining reliability improvement is a non-destructive, isolated restore
rehearsal that measures actual RTO. It is not required for ordinary service
restart recovery and must not overwrite the canonical VPS database.
