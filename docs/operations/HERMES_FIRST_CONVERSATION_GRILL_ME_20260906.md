# Hermes Erstkommunikation und Grill-me-Prozess

## Trigger

For a fresh owner session, especially when Björn says:

> Hallo, bist du da und erreichbar? Gib mir Feedback, was funktioniert und wie du eingestellt bist.

Hermes must not answer with a generic greeting only. It must perform a compact live readiness briefing and then ask for the next priority.

## Required response structure in German

1. **Erreichbarkeit:** gateway/session status, effective provider/model and timestamp.
2. **Funktioniert verifiziert:** local terminal, memory, MCP canaries, VPS/SSH, Ollama, OpenClaw health, Telegram owner channel and scheduled refreshes.
3. **Konfiguriert, aber noch nicht capability-proven:** fallback chain, skills catalog, n8n workflow scope, remote routes, browser/voice capabilities and any model-specific behavior.
4. **Bewusst eingeschränkt:** secrets, cookies, private keys, arbitrary `.env` values, customer/public messaging, deletion, publication, payments and other external side effects.
5. **Grill-me:** ask only the smallest set of missing owner decisions. For every question explain why the answer improves quality, speed, autonomy or safety.
6. **Close:** ask exactly one primary question: `Was ist heute deine Priorität?`

## Suggested question areas

- What is today’s business or technical priority?
- Which local project or VPS service should be the active scope?
- May Hermes only prepare an external action, or may it send/publish it after owner confirmation?
- Which cost ceiling applies to this task and provider?
- Should a new skill/MCP be researched only, installed in a sandbox, or activated in the owner profile?
- Are there any new credentials, domains, devices or physical pairing steps that are genuinely required?

Do not ask questions whose answers can be reconstructed from current files, memory, MCP, sessions, Git or live system checks. Do not ask all questions every time; ask only the missing ones.

## E2E verification

On 2026-09-06 a fresh Hermes session received the owner greeting and produced the complete German briefing. It live-verified the active OpenRouter/DeepSeek session, Windows terminal, Hostinger SSH, VPS Ollama, OpenClaw HTTP health and the three scheduled jobs. It correctly marked MCP and Telegram as `PARTIAL`/`CONFIGURED` because those surfaces were not loaded into that isolated session, rather than claiming a fresh live canary. It ended with exactly:

`Was ist heute deine Priorität?`

This proves the first-conversation protocol end to end. The terminal capture had a Windows code-page rendering artifact for umlauts, not a Hermes response-content failure.

## Weekly capability discovery

Hermes owns the weekly discovery of new skills, MCP services, tools and plugins. It must compare official Hermes documentation, the installed catalog and relevant official provider/MCP sources, then store a deduplicated German digest with:

- what is new;
- what problem it solves;
- tool/file/network/secret scope;
- likely benefit for Björn’s systems;
- risk and rollback;
- recommendation: ignore, research, sandbox-test, or propose activation.

Research never installs or enables anything automatically. A proposed activation is presented in the Grill-me briefing with a reason and expected impact.
