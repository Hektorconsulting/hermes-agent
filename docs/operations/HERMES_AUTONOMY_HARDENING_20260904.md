# Hermes autonomy hardening — 2026-09-04

## Executive summary

The Hermes owner control path remains operational. This change set hardens the
existing shared knowledge bridge without rebuilding the verified Hermes →
Codex → n8n path. The canonical knowledge database remains on the VPS; local
files are mirrors or source artifacts only.

## Changed and verified

- Added a transport-neutral `TaskEnvelope` for task, session, run and
  provenance identity.
- Added additive `knowledge_tasks` persistence and indexes.
- Made event write-back ids content-addressed so retries do not create event
  duplicates.
- Added a privacy namespace to result records and filtered preflight results to
  the requesting namespace plus `global`; legacy results migrate additively to
  the `system` namespace.
- Updated session archives on every completed turn and at session end.
- Persisted delegation lineage through the shared knowledge provider.
- Expanded the source manifest with system classification, read status,
  provenance and conflict metadata while excluding generated and secret-like
  surfaces.
- Added the canonical owner autonomy policy in machine-readable and Markdown
  form.

## Current registry

| Component | Purpose | Runtime/path | Status | Dependencies | Risk / next action |
|---|---|---|---|---|---|
| Hermes Desktop/Gateway | Owner-facing orchestration and messaging runtime | `/home/ai-admin/.hermes/hermes-agent`; `hermes-gateway.service` | active after controlled restart | VPS, provider, shared_kb | Keep policy and task provenance aligned |
| shared_kb | Canonical preflight, archive and result persistence | `/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db` | PASS; integrity verified | SQLite, Hermes provider | Continue lifecycle reconciliation |
| Source Registry | Redacted source inventory | `knowledge_sources` in canonical DB | 23,025 entries after import | manifest builder/importer | Resolve future conflicts and stale entries |
| OpenClaw | Edge agent and messaging execution | `/usr/lib/node_modules/openclaw`; systemd launcher | version `2026.9.1`, latest registry version read back | Vault-backed secret, gateway | Mobile/Tailscale pairing remains external |
| n8n | Workflow execution and MCP workflow surface | existing VPS deployment | existing authenticated path reused | OAuth/MCP, credentials | Maintain reviewed workflow allowlist |
| Vault/secret authority | Raw secret source for runtime consumers | existing Vault-backed launcher | secret values not read or persisted | OpenClaw/Hermes consumers | Keep consumer references redacted |
| Backup/health automation | Recovery and runtime observation | existing Hermes backup and health timers | timers present and active | systemd, storage | Schedule a non-disruptive recovery rehearsal |
| UFW/exposure | Network boundary | VPS firewall | default deny inbound; Docker `DOCKER-USER` drops admin ports 81/8082; OpenClaw remains limited to Docker ranges | Cloudflare/NGINX/NPM policy | Tailscale login is still required for mobile route |

## Evidence and redaction

- Local targeted unit tests: `tests/shared_knowledge/test_bridge.py` passed
  with Python `unittest` (4 tests).
- Python compilation passed for all changed runtime modules.
- VPS runtime file SHA-256 values matched the local Git checkout.
- Fork persistence is configured as `origin=https://github.com/Hektorconsulting/hermes-agent.git`
  with `upstream=https://github.com/NousResearch/hermes-agent.git`; the current
  owner-fork head is `d96668ae4` and the deployed bridge hash is
  `71adb302f5e990eb477295649048a418a1741c7a19bf03746c9cccfff835ac5e`.
- VPS shared knowledge status: integrity `ok`; `knowledge_tasks` present;
  hardening and policy write-backs archived and redacted.
- Canonical DB status after the namespace migration and subsequent redacted
  write-backs: 23,025 sources, 9 sessions, 9 requirements, 9 results, 9
  events and 7 tasks; existing result rows are namespace-scoped.
- The namespace migration was backed up at
  `/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db.before-result-namespace-20260904.bak`;
  the gateway restarted successfully afterwards.
- The Docker exposure policy is now persisted by
  `hermes-docker-exposure-guard.service` plus its five-minute timer. IPv4
  allows for Docker networks `172.18.0.0/16` and `172.30.0.0/16` precede the
  OpenClaw 18789 drop; IPv6 administrative ports 18789, 8082 and 81 fail
  closed. The live service and timer are active.
- No credential values, tokens, passwords, API keys or `.env` values are part
  of this artifact.

## Remaining external gates

- OpenClaw mobile installation, smartphone pairing and device permissions.
- Tailscale account/device login if the private mobile route is used.
- Interactive Google OAuth consent, 2FA or CAPTCHA only when an existing
  authorized session cannot satisfy the requested scope.
- WhatsApp QR pairing and any real external/customer communication.

Technical failures remain engineering work. They are not owner gates unless
they require one of the external actions listed above.
