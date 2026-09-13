# Hermes Production Hardening — 2026-09-13

## Result

**PARTIAL_READINESS_PASS.** The OpenClaw ownership, recoverability, and
network-exposure defects are remediated. n8n is classified without mutation.
Communication and physical-voice acceptance retain explicit human gates.

## OpenClaw ownership and recovery

| Property | Verified state |
| --- | --- |
| Canonical runtime | `/etc/systemd/system/openclaw-gateway.service` with `User=ai-admin` |
| Legacy runtime | `~/.config/systemd/user/openclaw-gateway.service` disabled and failure state reset; it is retained only as a reversible legacy artifact. |
| Listener | `127.0.0.1:18789` and `[::1]:18789`; no LAN wildcard listener remains. |
| Internal access | Authenticated `openclaw_employee_bridge.py` health read passes at `ws://127.0.0.1:18789`. |
| Restart | Systemd restart passes. |
| Crash recovery | Main process was deliberately killed. Systemd started a new main PID; listener and bridge health returned PASS. |
| Backup | `/home/ai-admin/.hermes/backups/production-hardening-20260913/openclaw-prechange/` |

The system service is a single canonical service even though systemd owns it;
the process itself runs as `ai-admin`. This is intentional and avoids a second
user-service gateway competing for the same OpenClaw state directory.

## Network decision

The active OpenClaw configuration was changed from LAN binding to loopback
binding. No active n8n environment variable or Hermes bridge reference required
a LAN endpoint. The Hermes bridge uses local authenticated access. Reversal is
available from the pre-change backup, followed by a system-service restart.

## n8n workflow hygiene

See [N8N_WORKFLOW_REGISTRY_20260913.md](N8N_WORKFLOW_REGISTRY_20260913.md).

| Classification | Count | Change made |
| --- | ---: | --- |
| ACTIVE_RETAIN | 5 | None |
| LEGACY_REVIEW | 16 | None |
| DISABLED_RETAIN | 4 | None |
| ARCHIVE_CANDIDATE | 11 | None |

No n8n flow was run, published, disabled, deleted, or archived. A separate
change set must establish owner, consumer, trigger, rollback, and external
effect before any candidate is modified.

## Communication and voice acceptance

| Surface | Configured | Internal health | Inbound / processing | Outbound | Recovery | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Telegram | OpenClaw channel configuration exists | Gateway health PASS | OWNER_GATE: real owner message required | OWNER_GATE: no test message sent | Gateway recovery PASS | PARTIAL |
| WhatsApp / GOWA | GOWA container healthy; OpenClaw WhatsApp channel not configured | `/health` returned success | OWNER_GATE: QR/device pairing required | Not tested | Container health PASS | PARTIAL |
| Voice | STT enabled; Speaches container healthy | `/health` returned success | OWNER_GATE: microphone capture required | OWNER_GATE: speaker playback required | Container health PASS | PARTIAL |

## Provider resilience

| Path | Evidence | Result |
| --- | --- | --- |
| Primary OpenRouter | One-shot internal canary returned the expected response. | PASS |
| Local Ollama fallback | Local endpoint exposed the configured model; a direct local canary returned the expected response. | PASS |
| Automatic chain | No forced primary failure was injected into an active Hermes runtime. | PARTIAL |

## Residual risks and next action

1. Complete the three physical/interactive acceptance tests only when desired:
   Telegram owner inbound round trip, WhatsApp QR pairing, and German
   microphone-to-STT-to-TTS-to-speaker loop.
2. Review the 27 n8n legacy/archive candidates in a separate reversible change
   set. Do not bulk-delete them.
3. Run an explicitly instrumented automatic provider-failover test in a
   disposable session before relying on it for unattended critical work.
4. Correct or archive the invalid OpenClaw workspace skill and resolve the
   two workspace-vs-bundled skill precedence collisions. They did not block
   the gateway recovery but are logged startup hygiene issues.

No credentials, tokens, message content, payment data, or customer data are
contained in this record.
