# Hermes Provider-Routing-Reconciliation — 2026-09-06

> **Laufzeit-Nachtrag, 2026-09-06 15:20 UTC:** Dieser Abschnitt ersetzt
> frühere PASS-Aussagen zu VPS-OpenRouter-Fallbacks. Er basiert auf dem
> produktiven `hermes-gateway.service`, nicht nur auf Desktop- oder
> Standalone-Resolver-Tests.

## Verifizierter VPS-Incident und Reparatur

Der VPS-Gateway lief auf Hermes Agent **v0.13.0**, während der lokale
Desktop-/Fork-Stand v0.21.0 ist. Der Gateway las beim Start
`/home/ai-admin/.hermes/.env` mit Überschreibrecht. Dort stand noch die
veraltete Variable `HERMES_INFERENCE_PROVIDER`; sie zwang jeden
Gateway-Agenten auf OpenRouter und überstimmte die konfigurierte private
VPS-Ollama-Verbindung.

Die Ursache ist behoben und reversibel dokumentiert:

```text
1. Sicherung erzeugt:
   /home/ai-admin/.hermes/state/config-backups/
2. model.provider präzisiert:
   custom:vps-ollama
3. agent.api_max_retries:
   1 (statt 3)
4. Ausschließlich die veraltete Provider-Variable aus .env entfernt.
5. hermes-gateway.service kontrolliert neu gestartet.
6. Gateway-Resolver danach:
   provider=custom, base_url=http://127.0.0.1:11434/v1
```

Der aktuelle Gateway ist nach der Reparatur aktiv. Der private VPS-Ollama-
Endpoint ist erreichbar. Ein vollwertiger Hermes-One-Shot-Canary der alten
v0.13-Laufzeit wurde nach einem unverhältnismäßig langen Lauf kontrolliert
abgebrochen; daraus wird **kein** Agenten-E2E-PASS abgeleitet.

## Aktueller OpenRouter-Befund

Das Hermes-G-Credential ist im geschützten Credential-Pool vorhanden und die
Key-Metadaten konnten ohne Ausgabe von Secretwerten abgefragt werden. Die
Free-Fallback-Kette ist jedoch derzeit **nicht nutzbar**:

```text
Grund: OpenRouter-Konto-/Guardrail-Policies
  - Free-model-training nicht erlaubt
  - Zero-Data-Retention für nicht passende Endpoints erzwungen

Folgen:
  - mehrere :free-Modelle liefern HTTP 404 wegen Policy-Filterung;
  - z-ai/glm-5.2:free ist nicht mehr als Free-Slug verfügbar;
  - die alte Kette wiederholte jeden Fehler dreimal.
```

Der Retry-Sturm ist durch `agent.api_max_retries: 1` begrenzt. Die
OpenRouter-Privacy-/Guardrail-Einstellungen werden **nicht** automatisch
gelockert: Das wäre eine eigenständige Datenverarbeitungsentscheidung. Bis
zu einer expliziten Owner-Entscheidung bleibt VPS-Ollama der belastbare
Primärpfad; OpenRouter-Free-Einträge sind lediglich konfiguriert, nicht als
gesund bestätigt.

## Ergebnis

Der OpenRouter-Fehler aus der Hermes-Desktop-Anzeige war kein Beleg für
verbrauchten OpenRouter-Tokenbestand. Die Laufzeitauflösung war durch einen
redundanten OPENROUTER_BASE_URL-Override blockiert. Der Override zeigte zwar
auf die offizielle OpenRouter-URL, wurde von Hermes aber als Custom-Endpoint
interpretiert und verhinderte dadurch die Verwendung des Credential-Pools.

Zusätzlich lag auf dem VPS ein anderer, als exhausted markierter
OpenRouter-Credential im aktiven Pool. Dieser wurde durch den bereitgestellten
Hermes-G-Credential ersetzt. Der Credentialwert steht ausschließlich in
geschützten Laufzeitdateien und nicht in diesem Dokument.

## Aktiver Routingzustand

~~~
Lokaler Hermes-Primärprovider:
  provider  = custom
  model     = gemma4:e2b
  endpoint  = http://127.0.0.1:11435/v1
  transport = OpenAI-compatible chat completions
  context   = 131072 (vom Ollama-Modell gemeldet)

VPS-Hermes-Primärprovider:
  provider  = custom:vps-ollama
  model     = gemma4:e2b
  endpoint  = http://127.0.0.1:11434/v1
  context   = 131072

OpenRouter-Fallback:
  credential = Hermes-G
  endpoint   = https://openrouter.ai/api/v1
  credential metadata = verified without secret output
  paid budget limit   = 2 USD (period semantics require separate verification)
~~~

## Reproduzierte Befunde

### Screenshots

Die beiden Desktop-Screenshots zeigen:

~~~
No usable credentials found for openrouter.
setup.status reports configured credentials, but runtime resolution still failed.
~~~

Das ist ein Setup-/Runtime-Resolution-Fehler. Die Bilder zeigen keine
Usage-Zahl und beweisen keinen Tokenverbrauch.

### Lokaler Resolver

Vor der Korrektur:

~~~
provider = openrouter
base_url = https://openrouter.ai/api/v1
api_key  = absent
source   = env/config
~~~

Nach Entfernung des redundanten URL-Overrides:

~~~
provider = openrouter
base_url = https://openrouter.ai/api/v1
api_key  = present
source   = manual
fingerprint = 912b323c9058
~~~

Nach Umschalten des Primärproviders:

~~~
default resolver      = custom / http://127.0.0.1:11435/v1
explicit OpenRouter   = openrouter / https://openrouter.ai/api/v1
credential source     = manual / Hermes-G
~~~

### Canary-Ergebnisse

~~~
VPS Ollama /v1/models                 = PASS
VPS Ollama task-managed chat          = PASS
Hermes local primary via VPS Ollama  = PASS
VPS Gateway resolver via VPS Ollama   = PASS (nach .env-Override-Reparatur)
Hermes OpenRouter Free fallback        = BLOCKED (Guardrail-/Privacy-Policy)
OpenRouter credential metadata        = PASS (redigiert)
DeepSeek paid live canary              = NOT RUN (kein Kosten-/Policy-Nachweis behauptet)
~~~

Die lokale Ollama-Verbindung läuft über eine private SSH-Weiterleitung:

~~~
127.0.0.1:11435 -> hostinger-vps:127.0.0.1:11434
~~~

Ollama wurde nicht öffentlich exponiert.

## Behobene Laufzeitfehler

1. Lokaler OPENROUTER_BASE_URL-Benutzeroverride auf der kanonischen
   OpenRouter-URL wurde entfernt. Die Konfiguration bleibt in
   C:\Hermes\config.yaml die maßgebliche Endpointquelle.
2. Lokaler Hermes-Primärprovider wurde auf den verifizierten VPS-Ollama-Pfad
   gesetzt.
3. Der private SSH-Tunnel wurde task-sicher gemacht. Das PowerShell-Skript
   hält ssh jetzt im Scheduled-Task-Prozess und startet nicht nur einen
   kurzlebigen Detached-Wrapper. Der Task darf auch im Batteriebetrieb laufen.
4. Auf dem VPS wurde der stale Runtime-Override
   `HERMES_INFERENCE_PROVIDER` aus der geschützten `.env` entfernt. Er hatte
   den Gateway auf OpenRouter festgelegt und war die direkte Ursache dafür,
   dass `gemma4:e2b` als OpenRouter-Modell angefragt wurde.
5. Der Primary wurde von dem mehrdeutigen `custom` auf den gespeicherten
   Namen `custom:vps-ollama` präzisiert; der Gateway-Resolver bestätigt
   danach die private Ollama-Basis-URL.
6. Die Retries pro Provider wurden auf einen Versuch begrenzt.
7. Der VPS-Hermes-Arbeitsbereich ist /home/ai-admin. Die redigierte
   Besitzer-/Pfadübergabe liegt unter /home/ai-admin/AGENTS.md.

Die Resolveränderung ist durch gezielte Regressionstests abgesichert:

~~~
3 passed, 64 deselected
~~~

## Konfigurierte und effektive Fallback-Reihenfolge

~~~
Konfiguriert:
1. VPS Ollama (Primärprovider)
2. OpenRouter :free-Modelle (derzeit durch Account-Policies blockiert)
3. VPS-Ollama-Duplikat als letzte Rettung

Effektiv verifiziert:
1. VPS Ollama (Primärprovider)

Nicht als PASS behauptet:
- OpenRouter-Free-Modelle, solange deren Privacy-/Guardrail-Filter aktiv ist
- DeepSeek V4 Flash Latest, solange kein kostenbewusster Test mit eindeutigem
  Budget-/Privacy-Nachweis erfolgte
- LM Studio und lokales Ollama als Remote-Gateway-Fallback
~~~

Die Paid-Stufe bleibt durch das OpenRouter-Key-Limit von 2 USD technisch
begrenzt. Eine wöchentliche Budgetauswertung ist davon zu unterscheiden: Die
OpenRouter-Key-API weist hier ein Key-Limit aus, keine separat verifizierte
Wochenabrechnung. Hermes darf daher bei unbekanntem Budget nicht eigenständig
auf Paid-Modelle hochstufen.

## Noch offen

~~~
Telegram Owner-DM inbound E2E      = PENDING (live Owner-Testnachricht fehlt)
Telegram Bot API / Long Polling    = PASS; Allowlist und Runtime-Umgebung stimmen überein
OpenClaw Employee Bridge            = PASS (authentifizierter read-only Canary)
OpenClaw A2A/MCP Gateway           = PARTIAL (HTML-Fallback ist kein Protokollnachweis)
VPS OpenRouter Free fallback       = BLOCKED (Privacy-/Guardrail-Policy)
VPS Hermes-Version                 = OUTDATED (v0.13.0; Upgrade separat stagen)
Desktop UI screenshot refresh      = requires reopening/reloading the view
Full 46-screenshot file inventory  = independently re-counted (46 PNGs)
Full screenshot semantic review    = evidence register exists; no executable instructions inferred
Weekly capability research         = scheduled job exists; output audit open
~~~

Die offene Telegram-Zeile bedeutet nicht, dass der Bot nicht verbunden ist:
der VPS-Gateway-Prozess hält eine aktive Verbindung zu Telegram. Es fehlt nur
noch ein neuer Owner-Eingang als unabhängiger Nachweis für die komplette
Inbound-/Antwortstrecke. Der alte ungültige Token ist nicht mehr aktiv; der
aktuelle Token wurde am VPS mit `getMe` gegen `hektor_hermes_agent_bot`
verifiziert. OpenClaw verwendet eine andere Bot-Identität und ist daher nicht
die Ursache eines Same-Bot-Polling-Konflikts.

## Aktueller Telegram-Nachweis

Bot-API, Long-Polling-Verbindung und genau eine Owner-Allowlist-Identität
sind bestätigt. Ein vollständiger Inbound-/Antwort-Nachweis erfordert eine
neu eingehende, erlaubte Owner-Nachricht und wird nicht durch unaufgeforderte
externe Testnachrichten ersetzt. Deshalb bleibt Telegram Owner-DM inbound E2E
bewusst `PENDING`.

## Reproduzierbare Prüfpfade

~~~
Local config:
  C:\Hermes\config.yaml

Local credential pool:
  C:\Hermes\auth.json

Tunnel:
  C:\Hermes\ops\Start-HermesVpsOllamaTunnel.ps1
  Task: Hermes-VPS-Ollama-Tunnel

VPS config:
  /home/ai-admin/.hermes/config.yaml

VPS credential pool:
  /home/ai-admin/.hermes/auth.json

VPS owner scope:
  /home/ai-admin/AGENTS.md

VPS shared knowledge:
  /home/ai-admin/knowledge/claude_codex_hermes_knowledge.db
~~~

Secrets, Tokens, Cookies, private Schlüssel und unredigierte Logs gehören
nicht in dieses Repository.
