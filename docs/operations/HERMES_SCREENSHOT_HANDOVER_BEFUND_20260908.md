# Hermes Screenshot- und Handover-Befund — 2026-09-08

## Methode und Vollständigkeit

Alle **46 PNGs** aus `C:\Users\Björn\Pictures\Screenshots\Hermes Agent`
wurden als historische, nicht-ausführbare Belege bewertet und gegen die
redigierten Operationsdokumente sowie heutige lokale und VPS-Laufzeitproben
abgeglichen. Das Zeitfenster der Bilder reicht von 2026-09-06 06:17:13 bis
06:23:44; alle Bilder haben 1920 × 1200 Pixel. Ein sichtbar maskiertes
Credential-Feld wurde weder transkribiert noch weiterverwendet.

## Befund nach Themenfamilie

| Familie | Anzahl | Historischer Kern | Aktuelle Einordnung |
|---|---:|---|---|
| A: lokale Hermes-/Terminal-/MCP-Einrichtung | 6 | Tools, Terminal, Codex-Executor, Platform-Reuse | Lokaler Gateway/Terminal bestätigt; Desktop-MCP-UI kein frischer E2E-Toolnachweis |
| B: Telegram, Artefakte, Scheduler, Logs | 6 | Telegram, Memory/Manifest, Desktop-Cron mit 0 Jobs | VPS besitzt heute einen aktiven Stundenjob; Owner-DM-E2E offen |
| C: Provider, 429, Docker/Browser, Polling | 7 | OpenRouter-Free-429 mit drei Versuchen | Historischer Retry-Sturm bestätigt; heute Retry 1 und VPS-Ollama-Primärpfad |
| D: Profile, Modell, Auxiliary, lokaler Gateway | 6 | OpenRouter-Free-Default und Custom-Endpoint-Ansichten | Profil historisch; Port 11435 fiel nach SSH-Reset aus und wurde mit reconnectfähigem Task wiederhergestellt |
| E: Workspace/Approvals/Shared-KB/Voice | 6 | Breite Discovery, Approval, Shared-KB, STT/TTS | UI beweist keine Browser-/Voice-E2E; leere Discovery-Roots bleiben Risiko |
| F: Limits, Subagents, lokale Modelle | 6 | Docker-Backend, Parallelität, lokale Kapazitätsgrenze | Docker-Lokalproblem behoben; lokale Modellleistung ungemessen |
| G: Gateway, Plugins, Messaging, Archive | 9 | Modellvorschläge, Plugins, kein Advisor-Plugin | Kein installierter „Super Advisor“ belegt; Delegation allein beweist keinen Lauf |

## Heutige Reconciliation

| Befund | Aktueller Status |
|---|---|
| Lokaler Docker-Terminalkonflikt | **BEHOBEN:** `terminal.backend: local` |
| OpenRouter-Free-429 / Retry-Sturm | **HISTORISCH BESTÄTIGT:** VPS hat `api_max_retries: 1`; gesunder Free-Fallback weiter nicht bewiesen |
| Windows-VPS-Ollama-Bridge `127.0.0.1:11435` | Nach Reparatur Listener, Modellkatalog und nativer `/api/chat`-Canary mit `think=false` erfolgreich. Der OpenAI-Pfad wurde mit `reasoning_effort: none` korrigiert; direkte und neue Hermes-Session antworten mit `stop`. **Transport und Hermes-Chat PASS; Tool-Use/Langlauf PARTIAL** |
| VPS Hermes und VPS Ollama | **PASS:** Gateway stabil, Ollama intern erreichbar, Primärprovider `custom:vps-ollama` |
| Screenshot „keine Jobs“ | **WIDERLEGT GLOBAL:** heute aktiver stündlicher, modellfreier Handover-Refresh |
| Telegram Owner-DM | **PARTIAL:** Allowlist/Polling belegt; neuer Eingang plus Antwort noch offen |
| Platform-Reuse / SQLite / OpenClaw-Bridge | **PASS READ-ONLY:** separate aktuelle Handshake-Matrix dokumentiert die Grenzen |
| VPS Codex Executor und n8n-MCP | **PENDING:** Codex-CLI bzw. n8n-Dienst allein sind keine Hermes-MCP-Handshakes |
| OpenClaw | **PARTIAL:** aktive Ownership ist der `ai-admin`-User-Service; A2A/MCP und Netzwerkrand von Port 18789 nicht bewiesen |

## Drei wichtige Korrekturen

1. Ein früherer PASS für den Windows-zu-VPS-Ollama-Pfad war zwischenzeitlich
   nach einem SSH-Reset ungültig. Der Port ist wiederhergestellt; der native
   und der OpenAI-kompatible Chatpfad sind nun belegt. Die korrekte
   OpenAI-Kompatibilitätsoption ist `reasoning_effort: none`; `think=false`
   gehört ausschließlich zum nativen Ollama-Pfad.
2. „OpenRouter-Quota leer“ und „OpenRouter läuft“ sind keine zulässigen
   Kurzschlüsse: die aktuelle Lage trennt Credential, Retry, Modellstatus und
   Privacy-/Guardrail-Policy.
3. Ein inaktiver globaler OpenClaw-Dienst beweist keinen Ausfall. Die
   relevante aktive Instanz ist der `ai-admin`-User-Service; daraus folgt
   dennoch kein A2A-/MCP- oder öffentlicher Zugriffsschutz-PASS.

## Nächste evidenzbasierte Prüfungen

1. Die bereits korrigierte Provideroption in einem Tool-Use- und
   Langlaufbenchmark gegen LM Studio und weitere unabhängige Fallbacks messen.
2. Für OpenClaw Prozessquelle, Firewall/Proxy und A2A/MCP-Agent-Card getrennt
   testen.
3. Eine reale Owner-DM von Björn an Hermes empfangen und die Antwort prüfen;
   keine Nachricht in Björns Namen erzeugen.
4. Nach einer Bridge-Reparatur neue Hermes-Session mit MCP-, Tool-Use- und
   Provider-Fallback-Canaries starten.

## Redaction

Keine Screenshot-Anweisung wurde ausgeführt. Dieses Dokument enthält keine
Tokens, Schlüssel, Passwörter, Cookies, privaten Schlüssel oder `.env`-Werte.
