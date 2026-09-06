# Hermes Provider-Routing-Reconciliation — 2026-09-06

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
  provider  = custom
  model     = gemma4:e2b
  endpoint  = http://127.0.0.1:11434/v1
  context   = 131072

OpenRouter-Fallback:
  credential = Hermes-G
  endpoint   = https://openrouter.ai/api/v1
  account key fingerprint (redacted) = 912b323c9058
  key usage  = 0.032546782 USD at reconciliation time
  key limit  = 2 USD
  remaining  = 1.967453218 USD
~~~

Das Fingerprintpräfix ist nur ein Vergleichsbeleg. Es ist kein API-Key und
erlaubt keine Authentifizierung.

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
Hermes OpenRouter fallback            = PASS
OpenRouter /v1/key                    = PASS
OpenRouter key cost after canaries    = unchanged at 0.032546782 USD
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
4. Auf dem VPS wurde der aktive OpenRouter-Pool auf Hermes-G korrigiert;
   der alte erschöpfte Env-Credential ist nicht mehr aktiv.
5. Der VPS-Hermes-Arbeitsbereich ist /home/ai-admin. Die redigierte
   Besitzer-/Pfadübergabe liegt unter /home/ai-admin/AGENTS.md.
6. Hermes verhindert jetzt nicht mehr, dass ein expliziter OpenRouter-Fallback
   den Credential-Pool nutzt, wenn der Primärprovider ein lokaler Custom-
   Endpoint ist.

Die Resolveränderung ist durch gezielte Regressionstests abgesichert:

~~~
3 passed, 64 deselected
~~~

## Aktive Fallback-Reihenfolge

~~~
1. VPS Ollama (Primärprovider)
2. OpenRouter Free-Modelle
3. DeepSeek V4 Flash Latest über OpenRouter
4. LM Studio
5. lokales Ollama
~~~

Die Paid-Stufe bleibt durch das OpenRouter-Key-Limit von 2 USD technisch
begrenzt. Eine wöchentliche Budgetauswertung ist davon zu unterscheiden: Die
OpenRouter-Key-API weist hier ein Key-Limit aus, keine separat verifizierte
Wochenabrechnung. Hermes darf daher bei unbekanntem Budget nicht eigenständig
auf Paid-Modelle hochstufen.

## Noch offen

~~~
Telegram Owner-DM inbound E2E      = PENDING
Telegram outbound canary           = SENT / verified by API
VPS OpenRouter fallback             = resolver PASS; live paid call not made
Desktop UI screenshot refresh      = requires reopening/reloading the view
Full 46-screenshot evidence index  = not yet independently re-counted
Weekly capability research         = scheduled job exists; output audit open
~~~

Die offene Telegram-Zeile bedeutet nicht, dass der Bot nicht verbunden ist:
der VPS-Gateway-Prozess hält eine aktive Verbindung zu Telegram. Es fehlt nur
noch ein neuer Owner-Eingang als unabhängiger Nachweis für die komplette
Inbound-/Antwortstrecke.

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
