# Hermes ↔ OpenClaw: Mitarbeiter-Handschlag und Telegram-Befund

Stand: 2026-09-06 08:18 Europe/Berlin

## Ergebnis

Der OpenClaw-Server ist auf dem Hostinger-VPS erreichbar. Der read-only
Hermes-zu-OpenClaw-Mitarbeiterkanal ist jetzt über einen VPS-MCP-Adapter
konfiguriert und als Prozess unter dem Hermes-Gateway nachgewiesen. Ein
mutierender Agentenkanal ist bewusst weiterhin nicht exponiert.

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
- Mit dem serverseitig aus der OpenClaw-Secret-Quelle geladenen Token konnte
  `gateway call health` erfolgreich über WebSocket ausgeführt werden; der
  Tokenwert wurde nicht ausgegeben.
- Hermes kennt im Sourcebestand OpenClaw-Migration und Dokumentation, aber
  keine eingebaute OpenClaw-Route. Dafür ist jetzt der lokale VPS-MCP-Adapter
  `hermes-openclaw-employee` aktiv.

## Aktiver read-only Employee-Adapter

```text
Hermes-Gateway (ai-admin)
  └─ MCP stdio child: /home/ai-admin/.hermes/hermes-agent/tools/openclaw_employee_bridge.py
       └─ authenticated WebSocket → ws://127.0.0.1:18789
```

Die erlaubten Werkzeuge sind ausschließlich `openclaw_health` und
`openclaw_readiness`. Der Adapter gibt keine Werkzeuge zum Senden von
Telegram-Nachrichten, Starten von OpenClaw-Agenten, Ändern von Konfigurationen
oder Neustarten von Diensten frei. Der OpenClaw-Token wird nur im VPS-Prozess
verwendet.

Der direkte MCP-Canary (`initialize`, `tools/list`, `openclaw_readiness`) ist
erfolgreich. Der separate interaktive Befehl `hermes mcp test` beendet sich in
dieser VPS-Umgebung weiterhin nach rund zehn Sekunden mit `Connection closed`;
das widerspricht nicht dem aktiven Child-Prozess unter dem laufenden Gateway,
ist aber als eigenständiger CLI-Test kein PASS.

## Telegram-Befund

- Die Owner-ID `8196825649` ist zusätzlich in Hermes’
  `platforms.telegram.allow_from` hinterlegt.
- Die gleiche ID steht als `TELEGRAM_ALLOWED_USERS` in der VPS-`.env`; Werte
  werden nicht in Reports übernommen.
- `GATEWAY_ALLOW_ALL_USERS` wurde nicht gesetzt.
- Der aktuelle VPS-Hermes-Gateway startet aktiv. Historische Telegram-Warnungen
  aus älteren Starts sind nicht als aktueller Betriebsnachweis zu werten.
- Der OpenClaw-Gateway meldet Telegram über seinen authentifizierten Health-Call
  als `configured`, `running`, `connected`, `polling` und `tokenStatus=available`.
  Die aktive Telegram-Session des Owners `8196825649` ist in der OpenClaw-
  Sessionliste vorhanden. Das ist ein OpenClaw-Telegram-Nachweis, nicht der
  Nachweis eines separaten Hermes-Bot-Tokens.
- Der aktuelle VPS-Hermes-Token wurde anschließend aus dem lokalen Hermes-
  Secret-Store über stdin in die geschützte VPS-`.env` übertragen. Der
  redigierte Hash stimmt auf beiden Seiten überein; ein VPS-`getMe` bestätigt
  `hektor_hermes_agent_bot` (Hermes Agent).
- Der lokale Windows-Hermes-Poller wurde beendet, weil derselbe Bot nicht
  gleichzeitig lokal und auf dem VPS per `getUpdates` pollen darf.
- Die früheren `InvalidToken`- und Conflict-Zeilen gehören zum Start vor der
  Tokenkorrektur. Seit dem korrigierten Neustart und dem Stop des lokalen
  Pollers wurden keine neuen Telegram-Fehler oder Polling-Konflikte geloggt.

## Nächster sicherer Integrationsschritt

1. Eine synthetische Agenten-Anfrage ohne externe Zustellung über den
   authentifizierten Employee-Kanal prüfen.
2. Telegram ausschließlich als private Owner-DM mit `8196825649` prüfen.
3. Keine Gruppen, Kundenkanäle, externen Nachrichten oder öffentlichen
   OpenClaw-Ports aktivieren.

## Nicht behaupten

`OPENCLAW HEALTH = VERIFIED` ist belegt. `HERMES OPENCLAW READ-ONLY EMPLOYEE
ACCESS = VERIFIED` ist durch den aktiven MCP-Child-Prozess, dessen
MCP-Handshake und den authentifizierten Health-Call belegt. Ein mutierender
OpenClaw-Agentenkanal bleibt absichtlich nicht freigeschaltet. `TELEGRAM E2E
OPENCLAW OWNER CHANNEL = VERIFIED`; `TELEGRAM CURRENT VPS HERMES BOT =
VERIFIED` für Bot-Identität, Secret-Zuordnung, Allowlist und konfliktfreien
laufenden Poller. Eine vom Owner gesendete neue Chatnachricht wurde in diesem
Schritt nicht künstlich erzeugt; daher ist die vollständige Inbound-Agent-
Antwort als separater E2E-Test noch ausstehend.
