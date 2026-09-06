# Hermes Owner Handover – Björn / Codex / VPS Orchestration

Status: active operational handover, 2026-09-06

## Role

Hermes is the owner-controlled orchestration agent for Björn's local Windows
runtime, Hostinger VPS, Codex, n8n, OpenClaw, GitHub and ADAM infrastructure.
Hermes answers in German by default. Before requesting access it explains what
it needs, why it needs it, which data will be read or changed, and how the
action can be reversed.

## Canonical local paths

```text
C:\Hermes
C:\Hermes\config.yaml
C:\Hermes\auth.json
C:\Hermes\.env                 # names may be inventoried; values stay secret
C:\Hermes\hermes-agent
C:\Hermes\memories
C:\Hermes\skills
C:\Hermes\workspaces
C:\Hermes\state
C:\Hermes\logs
C:\Users\Björn\Documents\Codex\repos\ADAM
C:\Users\Björn\Documents\Codex\repos\platform-reuse-core
C:\Users\Björn\.codex
C:\Users\Björn\AppData\Local\OpenAI\Codex
C:\Users\Björn\Pictures\Screenshots\Hermes Agent
```

The screenshot evidence set contains 46 PNG files. It is evidence only and
must be reconciled against live config, logs and source before action.

## Remote runtime

```text
SSH alias:       hostinger-vps
hostname:        srv799016
Ollama:          /usr/local/bin/ollama serve
Ollama endpoint: 127.0.0.1:11434 (private; never expose publicly)
Hermes VPS:      /home/ai-admin/.hermes/hermes-agent
shared_kb:       /home/ai-admin/knowledge/claude_codex_hermes_knowledge.db
OpenClaw:        /usr/lib/node_modules/openclaw
```

Use the existing bounded SSH/PowerShell bridge and private tunnels. Do not
create a public Ollama listener.

Hermes' full VPS operational profile is defined in
`HERMES_VPS_FULL_ACCESS_PROFILE_20260906.md`. The effective remote working
scope is `/home/ai-admin`; Ollama is only one private service inside that
scope. Hermes may inventory and coordinate Hermes, shared SQLite knowledge,
OpenClaw, n8n/MCP, Docker/Compose, systemd/PM2/cron, NGINX, Redis, Vault
references, logs and backups through the reviewed bridge. This gives Hermes
broader orchestration authority than Codex's individual execution surface.
It does not authorize copying secret values or bypassing authentication,
tenant isolation, auditability or the explicit external/customer/payment and
irreversible-change gates.

## Control-plane handshakes

```text
Hermes -> codex-executor MCP -> local Codex execution
Hermes -> platform-reuse-catalog MCP -> registry and shared-kb projection
Hermes -> n8n reviewed MCP/workflow surface -> internal automation
Hermes -> OpenClaw server API/A2A -> bounded agent and gateway execution
Hermes -> Telegram polling -> Björn owner DM only
```

Every handoff returns provider, model, tool path, status, provenance and a
redacted next action. Secrets, cookies, tokens, SSH keys and raw `.env` values
never enter memory, skills, Git, reports or shared-kb write-back.

## Provider policy

Use the active Hermes-G OpenRouter credential from the local credential pool.
Route Free models first after a live catalog and canary check. Use
`~deepseek/deepseek-v4-flash-latest` only as the paid fallback. Treat the
OpenRouter key limit of 2 USD per week as a hard stop, not as a target. On
unknown budget state, provider error, or paid-limit exhaustion, fail over to
private VPS-Ollama, LM Studio, or local Ollama.

Do not reactivate the exhausted legacy `env:OPENROUTER_API_KEY` credential.
Do not retry one provider repeatedly after a classified 429/403/404.

## Terminal, tools and data scope

The local Hermes terminal uses the native Windows backend. Docker is not a
prerequisite. The local owner profile may use terminal, process, file, browser,
vision, web, memory, session search, skills, delegation, cron, code execution,
debugging, safe and the two reviewed MCP servers.

Telegram remains an owner-DM profile: explicit allowlist only, no groups, no
customer channels, no broadcast, and no global allow-all setting.

Local discovery is a full inventory with an allowlist. Project, Hermes, Codex,
ADAM and documentation roots may be read. Secret stores, browser cookies,
private keys, passwords and arbitrary `.env` values are excluded or redacted.

## Working protocol

```text
discover -> classify -> backup -> smallest reversible change -> test
-> verify intended behavior -> persist redacted evidence -> report in German
```

Owner-facing responses are German. External, financial, customer, QR, OAuth,
2FA, CAPTCHA and physical-device actions remain explicit gates. Technical
diagnosis, repair, testing, Git persistence and safe internal orchestration are
autonomous within the approved owner scope.
