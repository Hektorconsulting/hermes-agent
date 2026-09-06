# Hermes ↔ OpenClaw: Mitarbeiter-Handschlag und Telegram-Befund

Stand: 2026-09-06 08:18 Europe/Berlin

## Ergebnis

Der OpenClaw-Server ist auf dem Hostinger-VPS erreichbar. Ein vollständiger
Hermes-zu-OpenClaw-Agenten-Handschlag ist dagegen noch nicht nachgewiesen.
Hermes darf OpenClaw deshalb derzeit als erreichbare interne Zielkomponente
behandeln, nicht als bereits konfigurierten autonomen Mitarbeiter.

## Nachgewiesene Fakten

- OpenClaw lauscht auf dem VPS auf `0.0.0.0:18789`.
- `http://127.0.0.1:18789/health` antwortet als Benutzer `ai-admin` mit
  `ok=true` und `status=live`.
- Der laufende OpenClaw-Prozess wird aktuell durch den Watchdog gestartet;
  der systemd-Dienst `openclaw-gateway.service` ist weiterhin inaktiv. Eine
  Aktivierung ohne kontrollierte Übernahme wäre wegen möglicher doppelter
  Listener nicht sicher.
- Die OpenClaw-CLI kann den Gateway-WebSocket erreichen, verweigert aber
  weitergehende Diagnostik ohne Geräteidentität beziehungsweise RPC-Token.
- Hermes kennt im Sourcebestand OpenClaw-Migration und Dokumentation, aber
  keine verifizierte aktive OpenClaw-Employee-Route.

## Telegram-Befund

- Die Owner-ID `8196825649` ist zusätzlich in Hermes’
  `platforms.telegram.allow_from` hinterlegt.
- Die gleiche ID steht als `TELEGRAM_ALLOWED_USERS` in der VPS-`.env`; Werte
  werden nicht in Reports übernommen.
- `GATEWAY_ALLOW_ALL_USERS` wurde nicht gesetzt.
- Der aktuelle VPS-Hermes-Gateway startet aktiv. Historische Telegram-Warnungen
  aus älteren Starts sind nicht als aktueller Betriebsnachweis zu werten.
- Der VPS-Hermes-Bot-Token ist in der aktuellen Untersuchung nicht als
  verwendeter Secret-Wert ausgegeben oder bestätigt worden. Die sichtbaren
  Telegram-Screenshots sind Belege für einen früheren beziehungsweise anderen
  laufenden Hermes-Kanal, nicht automatisch für den aktuellen VPS-Prozess.

## Nächster sicherer Integrationsschritt

1. OpenClaw-RPC- beziehungsweise Geräteidentität aus dem bestehenden Secret-
   Consumer nachweisen, ohne den Wert offenzulegen.
2. Eine read-only Hermes-zu-OpenClaw-Health-Canary über den privaten
   Loopback-Pfad ausführen.
3. Erst danach eine synthetische Agenten-Anfrage ohne externe Zustellung testen.
4. Telegram ausschließlich als private Owner-DM mit `8196825649` prüfen.
5. Keine Gruppen, Kundenkanäle, externen Nachrichten oder öffentlichen
   OpenClaw-Ports aktivieren.

## Nicht behaupten

`OPENCLAW HEALTH = VERIFIED` ist belegt. `HERMES OPENCLAW EMPLOYEE ACCESS =
VERIFIED` ist noch offen. `TELEGRAM E2E CURRENT VPS BOT = VERIFIED` ist noch
offen, solange der aktuelle Hermes-Bot-Secret-Consumer und eine neue private
Canary nicht eindeutig dem laufenden VPS-Gateway zugeordnet sind.
