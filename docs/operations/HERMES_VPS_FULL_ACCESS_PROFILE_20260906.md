# Hermes VPS Full Operational Access Profile

Status: active, owner-controlled, redacted — 2026-09-06

## Purpose

Hermes is the lead orchestrator for Björn’s private Hostinger runtime. The
scope is the complete operational area under `/home/ai-admin`, not merely the
Ollama model endpoint. Hermes may coordinate the local Windows runtime, the VPS,
Codex, shared SQLite knowledge, OpenClaw, n8n/MCP and the Hermes gateway as one
system.

## Canonical transport

```text
SSH alias:        hostinger-vps
Host:             srv799016
Remote root:      /home/ai-admin
Local bridge:     C:\Hermes\ops\Invoke-HostingerCommand.ps1
Ollama:           127.0.0.1:11434 (private; reached by SSH tunnel)
OpenClaw:         127.0.0.1:18789 (private; server health endpoint)
Shared KB:        /home/ai-admin/knowledge/claude_codex_hermes_knowledge.db
VPS Hermes:       /home/ai-admin/.hermes/hermes-agent
OpenClaw install: /usr/lib/node_modules/openclaw
```

The bridge uses bounded, non-interactive SSH and passes commands through
stdin. Hermes must use it, or an equally bounded reviewed transport, rather
than inventing an untracked public ingress. Ollama is never exposed publicly
just to simplify access.

## Authorized operational scope

The following actions are within the autonomous owner-infrastructure scope when
they are reversible, auditable and tested:

1. inventory and read files, directories, processes, ports, systemd units,
   Docker/Compose projects, NGINX sites, PM2/cron jobs, logs, health endpoints
   and configuration metadata under `/home/ai-admin`;
2. inspect Hermes, shared knowledge, OpenClaw, n8n, MCP, Redis and service
   relationships and update redacted registries/runbooks;
3. run bounded diagnostics, canaries, backups, syntax checks and healthchecks;
4. repair or update internal Hermes orchestration code/configuration, restart a
   private owner service when required, and verify the same intended behavior;
5. use SSH forwarding or an internal VPS route for private Ollama/OpenClaw
   access and benchmark the configured models;
6. write deduplicated, redacted facts to the approved shared knowledge path;
7. commit and push redacted Hermes documentation/code to the owner fork and
   deploy approved reversible owner-infrastructure changes with rollback.

Hermes has broader coordination authority than Codex as the lead operator. The
authority is operational, not permission to bypass authentication, tenant
isolation, auditability or secret handling.

## Service and path inventory targets

| Area | Canonical target | Hermes use |
|---|---|---|
| Hermes VPS | `/home/ai-admin/.hermes/hermes-agent` | runtime, skills, state, logs and gateway diagnostics |
| Shared knowledge | `/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db` | redacted SQLite knowledge projection and write-back |
| OpenClaw | `/usr/lib/node_modules/openclaw` and its active service/config references | server-side gateway and agent inventory; current routes must be live-verified |
| Ollama | `/usr/local/bin/ollama`, `127.0.0.1:11434` | private inference, model inventory and benchmark |
| n8n/MCP | discovered under `/home/ai-admin`, Docker/Compose and service metadata | internal workflow/MCP discovery and controlled execution |
| Docker/Compose | discovered projects and manifests | container status, dependency and recovery diagnostics |
| systemd/PM2/cron | user/system service metadata and timers | start method, health, restart and recovery mapping |
| NGINX/SSL | site config and certificate metadata | private/public boundary and routing diagnosis |
| Redis/Vault | service metadata and consumer references | dependency inventory; never extract secret values |
| logs/backups | owner paths below `/home/ai-admin` | incident evidence, provenance and rollback readiness |

The inventory is live state, not a promise that every target exists. Hermes must
report `VERIFIED`, `CONFIGURED`, `PARTIAL`, `FAILED` or `UNKNOWN` separately.

## Secret and external-effect contract

Hermes may detect that a credential, token, key or secret reference is required,
but may not persist or repeat its value. Reports contain only the variable name,
credential label, owning service, path, digest where appropriate and status.

Still gated for Björn are external/customer messages, payments or new paid
commitments, public service exposure, interactive OAuth/2FA/CAPTCHA/QR pairing,
irreversible deletion without verified restore, and customer-tenant changes.
Internal inspection, reversible repair, controlled restart, testing, Git
documentation and redacted knowledge write-back are not ordinary human gates
when already covered by the owner directive.

## Required evidence for “VPS access ready”

Hermes must not report readiness from SSH configuration alone. It must capture,
without secret values:

```text
SSH reachability and authenticated identity
hostname and OS/runtime facts
read access to /home/ai-admin
discovery of Hermes, shared_kb, Ollama and OpenClaw
service/process and port state
redacted Docker/systemd/n8n/MCP inventory
private Ollama canary through the tunnel
shared_kb read/write-back provenance (redacted)
rollback/backup status for any mutation
```

If a probe is unavailable, Hermes records the exact missing capability and the
smallest next action. A healthy container, HTTP health response or configured
path alone is not an end-to-end PASS.

## Learning loop

The hourly refresh reads changed allowlisted metadata and deduplicates facts.
The daily reconciliation reads the complete redacted handover and rechecks VPS
state. The weekly capability review researches new skills/MCP/tools and makes
recommendations; it does not silently install risky or paid capabilities.
Facts go to memory/shared_kb, procedures go to skills, and secrets go nowhere in
the knowledge layer.

