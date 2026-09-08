# Hermes VPS: aktuelle Integrations-Handshake-Matrix — 2026-09-08

## Prüfgrenze

Diese Prüfung lief read-only im effektiven Gateway-Kontext auf dem VPS. Sie
hat keine Nachricht versendet, keinen Workflow ausgeführt, keine Zugangsdaten
ausgegeben und keine Integration verändert. Ein `PASS` beschreibt nur die in
der Tabelle genannte Schicht, nicht eine pauschale Gesamtfreigabe.

| Verbindung | Konfiguriert | Geladen / Transport | Erreichbar | Authentisiert | Discovery / Lesen | Write-Grenze | Gesamtstatus |
|---|---|---|---|---|---|---|---|
| Hermes → Platform-Reuse Catalog | PASS | PASS | PASS | lokaler stdio-Trust | 12 Tools; `platform_reuse_status` erfolgreich | Oberfläche nur Metadaten, keine externen Writes | **PASS (read-only)** |
| Hermes → Shared Knowledge / SQLite | PASS | PASS | PASS | lokaler `ai-admin`-Dateizugriff | 4 Tools; redigierter Status erfolgreich | `knowledge_writeback` und `knowledge_register_source` sichtbar, Approval-Pfad noch nicht als Gateway-Tool ausgeführt | **PASS lesen / PARTIAL schreiben** |
| Hermes → OpenClaw Employee Bridge | PASS | PASS | PASS | Bridge meldet `authenticated_read_only` | `openclaw_health` und `openclaw_readiness` erfolgreich | Nur zwei Health-/Readiness-Tools; keine Execute-/Send-Tools | **PASS (read-only)** |
| Hermes → Codex Executor | NEIN | — | Codex CLI vorhanden, aber keine Hermes-MCP-Brücke | — | — | Kein Zielpfad | **PENDING** |
| Hermes → n8n | NEIN | n8n-Container healthy, Loopback-Health erfolgreich | PASS für Dienst | anonymer API-Read korrekt 401 | Kein Hermes-n8n-MCP geladen | Credentials und Workflow-Ausführung bleiben getrennt | **PENDING** |
| Hermes → OpenClaw A2A/MCP nativ | PARTIAL | Health-/Readiness-Pfad erreichbar | PASS für Health | nicht als A2A/MCP bewiesen | keine Agent-Card-/Result-Return-Discovery | nicht geprüft | **PARTIAL** |

## Korrigierte Bestandsfakten

- Das aktive Hermes-Gateway läuft als `ai-admin` im Runtime-Root
  `/home/ai-admin/.hermes/hermes-agent`.
- Die aktive OpenClaw-Instanz ist der User-systemd-Service
  `/home/ai-admin/.config/systemd/user/openclaw-gateway.service`; ein
  gleichnamiger globaler Systemdienst ist nicht der laufende Dienst.
- Frühere Fehler von Shared-Knowledge/OpenClaw stammten teilweise aus einem
  für `ai-admin` unlesbaren Root-Arbeitsverzeichnis, nicht aus einer defekten
  effektiven Bridge.
- n8n besitzt eine interne MCP-URL, aber daraus folgt nicht, dass Hermes
  automatisch einen authentisierten n8n-MCP geladen hat.
- OpenClaw lauscht aktuell auf `0.0.0.0:18789`. Der lokale Health-Nachweis
  sagt nichts über Firewall, Reverse Proxy oder öffentliche Erreichbarkeit aus.

## Nächste technische Schritte

1. Für Codex prüfen, ob ein vorhandener, supporteter Executor-MCP existiert
   und welche lokale/vps-seitige Laufzeit er tatsächlich bedienen kann. Nicht
   aus der bloßen Codex-CLI-Installation einen MCP erfinden.
2. Für n8n eine scoped MCP-Verbindung mit vorhandener Credential-Referenz
   vorbereiten, zunächst ausschließlich für authentisierte Read-only-
   Discovery. Kein Workflow wird dadurch automatisch freigeschaltet.
3. Die Gateway-gebundene Provenienz von Platform-Reuse durch einen echten,
   redigierten Session-Canary belegen.
4. Für OpenClaw Agent-Card, A2A/MCP-Protokoll und Result-Return als separate
   E2E-Schichten prüfen. Health-HTTP ist kein Ersatz.
5. Vor jeder Erweiterung der OpenClaw-Toolfläche den Netzwerk-Rand, die
   Authentifizierung und die konkreten Mutationsmethoden inventarisieren.

## Redaction

Diese Matrix enthält nur Pfade, Diensttypen, Toolanzahlen, Zustände und
Capability-Grenzen. Keine Schlüssel, Tokens, Cookie-Werte, privaten Schlüssel,
unredigierten API-Antworten oder n8n-Credential-Werte wurden übernommen.
