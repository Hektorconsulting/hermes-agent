# Hermes wöchentliche Skill-/MCP-/Tool-Recherche

Hermes führt mindestens einmal pro Woche eine Capability-Recherche aus. Ziel ist nicht, möglichst viele der mehr als 95.000 Skills einzuschalten, sondern relevante Verbesserungen für Björns konkrete Infrastruktur zu finden.

## Recherchequellen

- Hermes-Source, installierte Skills und lokale Skill-Metadaten;
- offizieller Hermes Skills Hub und offizielle Hermes-MCP-Dokumentation;
- aktive MCP-Kataloge und Tool-Surfaces;
- OpenRouter-/Provider-Modellkataloge und aktuelle Routingdokumentation;
- relevante offizielle Dokumentation für OpenClaw, n8n, Telegram, Codex und VPS-Komponenten.

## Bewertung pro Kandidat

`Problemnutzen → Toolbedarf → Dateizugriff → Netzwerkzugriff → Secretbedarf → Kosten → Mutationsrisiko → Telegram-/Owner-Tauglichkeit → Testbarkeit → Rollback`

## Ergebnis

Hermes speichert einen redigierten, deduplizierten Wochenbericht in Memory/shared_kb und fragt Björn nur bei einer sinnvollen Entscheidung. Jede Empfehlung erhält genau eine Einstufung:

- `IGNORE` – kein relevanter Nutzen;
- `RESEARCH` – weitere Belege fehlen;
- `SANDBOX_TEST` – isolierter Read-only-/Dry-Run-Test sinnvoll;
- `PROPOSE_ACTIVATION` – konkreter Owner-Entscheid erforderlich.

Automatische Installation, Aktivierung, externe Anmeldung, QR-/2FA-Schritte, Kostenänderungen und Kunden-/Produktionsaktionen sind ausdrücklich nicht Bestandteil dieses Jobs.
