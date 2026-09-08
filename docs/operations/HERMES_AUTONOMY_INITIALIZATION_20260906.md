# Hermes Autonomy Initialization – Implementation Record

## Scope

This record is the implementation companion to the owner handover. It covers
local Windows, VPS, Codex, n8n, OpenClaw, OpenRouter, Telegram, MCP, skills,
memory and GitHub persistence. It does not contain secrets.

## Verbindliche Zielerweiterung — 2026-09-08

Der vollständige Owner-Plan **„Hermes Provider-Routing- und
OpenRouter-Reparatur mit VPS-Ollama-Prüfung“** ist verbindlicher Bestandteil
dieser Initialisierung. Ein späterer Kurztext zur Autonomie oder
Orchestrierung ersetzt ihn nicht. Die maßgebliche Abnahme- und
Statusmatrix steht in
`HERMES_PROVIDER_ROUTING_RECONCILIATION_20260906.md`.

Sie verlangt insbesondere: getrennte Root-Cause-Klassifikation für
OpenRouter, unabhängige Provider-Fallbacks, private VPS-Ollama- und
LM-Studio-Benchmarks, begrenzte Paid-Tests, Auxiliary-/Subagent-Routing,
neue Sessions nach Routingwechsel und eine deutsche, belegbare
Statusauskunft durch Hermes. Vollständige Autonomie bedeutet dabei
kontinuierliche, redigierte Inventur und Verbesserung innerhalb der
verifizierten lokalen und VPS-Arbeitsbereiche — nicht das Erfinden von
Integrationen oder das Kopieren von Secrets in den Wissensspeicher.

## Screenshot reconciliation

The evidence folder contains 46 screenshots. The reviewed evidence confirms:

- Hermes Desktop is operating with OpenRouter provider sessions and local
  session/terminal surfaces.
- Capabilities currently expose Hermes skills, tools and two enabled MCP
  servers: Codex Executor and Platform-Reuse Catalog.
- Artifacts expose `USER.md`, `SOUL.md`, `MEMORY.md`, a current-system
  manifest and an inventory artifact.
- System logs showed the old OpenRouter 429 path, missing Docker executable,
  unavailable browser-dependent tools, unavailable Nous auxiliary auth and a
  `/plan` skill name collision with the Hermes core command.
- Gateway settings currently use a local connection surface and the runtime
  must use native Windows terminal execution when Docker is absent.

The screenshot claims remain evidence and are reconciled with live probes before
being treated as PASS.

## Required verification sequence

1. Validate YAML and credential-pool selection without exposing values.
2. Validate one Free OpenRouter canary and the DeepSeek latest alias.
3. Verify fallback classification for 429, 403, 404 and budget exhaustion.
4. Verify VPS-Ollama through the private SSH path.
5. Verify LM Studio and record local Ollama availability.
6. Verify the two MCP servers and their visible tool counts.
7. Verify shared-kb preflight/write-back with redacted synthetic data.
8. Verify OpenClaw health, agent cards and result-return endpoints.
9. Verify Telegram polling, allowlist and owner-DM round trip.
10. Start a new Hermes session and confirm Memory, Skills, MCP and routing.

## Acceptance state

The system may only be reported as `SYSTEM AUTONOMY READY = YES` after every
item above has a current PASS or an explicitly documented external gate. A
configured endpoint, a healthy container, a masked key, or a running process
alone is not an end-to-end PASS.
