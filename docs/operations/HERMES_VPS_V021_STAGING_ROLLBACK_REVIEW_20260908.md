# Hermes VPS v0.21.0: unabhängige Staging- und Rollback-Gegenprüfung

**Prüfmodus:** ausschließlich read-only über lokale Dateien und SSH nach
`hostinger-vps`.

**Prüfzeitpunkt:** 2026-09-08 (Europe/Berlin). Der Produktionsprozess war bei
der Prüfung aktiv. Es erfolgten kein Servicewechsel, kein Upgrade, kein
`git pull`, keine Änderung an systemd, Konfiguration, `.env`, Credentials,
Datenbanken oder Netzwerkfreigaben. Dieser Bericht enthält keine Secret-Werte.

## Kurzurteil

Ein In-Place-Upgrade ist **ausgeschlossen**. Der Produktions-Checkout und der
lokale v0.21.0-Fork besitzen keinen gemeinsamen Merge-Commit. Außerdem hat die
Produktionsinstanz lokale, nicht versionierte Anpassungen. Das sichere Zielbild
ist daher ein **versioniertes Release neben der Produktion**, mit frischem venv,
separatem `HERMES_HOME` für den Canary und einem erst danach möglichen,
reversiblen systemd-Switch.

Ein paralleler Canary darf weder denselben Telegram-Bot pollen noch den
bestehenden Webhook oder eine bereits belegte Listener-Adresse übernehmen.
Seine Konfiguration muss diese Adapter vor dem ersten Start ausdrücklich
deaktivieren.

## Evidenz

| Bereich | Live-/Dateibefund | Bewertung |
|---|---|---|
| Produktionsservice | `hermes-gateway.service` ist stabil aktiv, läuft als `ai-admin` aus dem v0.13-venv und verwendet `HERMES_HOME=/home/ai-admin/.hermes`. | **PASS** |
| VPS-Release | Checkout `/home/ai-admin/.hermes/hermes-agent`: v0.13.0, eigener historischer Git-Strang, mit lokalen Deltas. | **PASS** für Bestandsdiagnose |
| Lokales Zielrelease | `C:\Hermes\hermes-agent`: v0.21.0, Branch `codex/hermes-autonomy-initialization-20260906`. | **PASS** |
| Git-Verwandtschaft | `git merge-base` liefert keinen Commit; keine Seite ist Vorfahr der anderen. | **BLOCKED** für Pull/Fast-forward; **PASS** für den separaten Release-Ansatz |
| Lokale VPS-Anpassungen | Zwei geänderte und zehn unversionierte Einträge in Provider-, Shared-KB- und Bridge-Flächen. | **PARTIAL**: Delta-/Patch-Matrix nötig |
| Python | Produktion nutzt Python 3.11.15; Zielversion unterstützt Python 3.11. | **PASS** |
| venv-Abhängigkeiten | Der v0.13-venv ist ein alter Editable-Install; seine MCP-Version weicht von v0.21 ab. | **PARTIAL**: alten venv nicht wiederverwenden |
| Build-Werkzeug | `uv` ist im Benutzerkontext des VPS verfügbar. | **PASS** |
| Provider-Konfiguration | Primärwahl `custom:vps-ollama`, private Base-URL, Modell `gemma4:e2b`, Kontext 131072, `api_max_retries=1`. | **PASS** |
| Provider-.env-Import | Der schädliche `HERMES_INFERENCE_PROVIDER`-Override ist entfernt. Ein Modell-Variablenname existiert weiter und wird im Canary gegen die effektive Auflösung geprüft. | **PASS/PARTIAL** |
| Fallbacks | OpenRouter-Free-Modelle und ein VPS-Ollama-Pfad sind konfiguriert. | **PARTIAL**: Konfiguration ist kein E2E-Nachweis |
| Externe Adapter | Produktionskonfiguration enthält Telegram und Webhook. | **BLOCKED** für einen unveränderten parallelen Canary |
| Isolation | Mehrere `HERMES_HOME`-Profile sind technisch möglich. | **PASS** für Möglichkeit; **PARTIAL** bis Canary-Profil besteht |
| Listenerlage | Ollama ist intern loopback-gebunden; andere Dienste belegen Produktionsports. | **PARTIAL**: Canary muss Port- und Adapterkonflikte vermeiden |

## Technische Schlussfolgerungen

1. Kein `git pull`, kein Reset und kein Kopieren über den laufenden v0.13-
   Checkout.
2. `HERMES_HOME` ist eine harte Laufzeitgrenze. Ein Canary darf nicht die
   produktive `.env`, Credentials, Datenbank, Scheduler-, PID- oder Telegram-
   Zustände verwenden.
3. Der entfernte `HERMES_INFERENCE_PROVIDER`-Override darf aus keinem Template
   zurückkehren. Der verbliebene Modellvariablenname wird nur nach explizitem
   Resolver-Test in den Canary übernommen oder verworfen.
4. Der Produktionsbefehl `gateway run --replace` ist kein Canary-Mechanismus.
   Ein Canary startet adapterlos, in separatem Home und ohne `--replace`.

## Risikoarmer Staging-Plan

### Phase A — Snapshot und Patch-Matrix

1. Unit, Drop-ins, Metadaten, Release-Commit, Paketliste und ein
   Hash-Manifest der produktiven Hermes-Dateien sichern. Secret-Dateien werden
   weder ausgegeben noch in Git übernommen.
2. Die zwölf VPS-Deltas als Matrix aus `Pfad`, `Zweck`, `Owner`,
   `v0.21-Kompatibilität`, `Test` und `Übernahmeform` klassifizieren.
3. Einen neuen Releasepfad wie
   `/home/ai-admin/releases/hermes-v0.21.0-<UTC-Zeitstempel>/` anlegen. Der
   alte Checkout bleibt unverändert und ist der Rollback-Anker.

### Phase B — Versionierter Release und frischer venv

1. Den überprüften lokalen v0.21-Commit als neues Release-Artefakt übertragen
   oder exakt auschecken — ohne Merge in v0.13.
2. Einen frischen venv mit Python 3.11.15 und dem v0.21-Lockfile erstellen.
3. Ohne Gatewaystart Python, Lock-Auflösung, `pip check`, Kernimports,
   `hermes --help` und Konfigurationsparser prüfen.

### Phase C — isoliertes Canary-Home

1. `/home/ai-admin/.hermes-canary-v021/` mit eigener Konfiguration,
   Datenbank, PID-/Control-/Log-Verzeichnissen und Scheduler anlegen.
2. Nur nicht-sensitive Runtime-Struktur spiegeln: `custom:vps-ollama`,
   private Loopback-Base-URL, Tool-/Skill-Subset und Dispatch-Optionen.
3. Telegram und Webhook entfernen oder deaktivieren; Dispatch im Gateway
   deaktivieren. Damit gibt es keine doppelte Polling-Session, keine echten
   Nachrichten und keinen Webhook-Listener.
4. Falls ein Credential-File zwingend nötig ist, nur geschützt lokal mit 0600
   kopieren; nie anzeigen, loggen oder versionieren.

### Phase D — Canarystart und Nachweis

1. Einen getrennten `ai-admin`-Prozess mit Canary-Home und neuem Release
   starten, ohne `--replace`.
2. Vorher bestätigen, dass keine portbindenden Plattformadapter aktiviert
   sind; ein etwaiger Testserver bleibt loopback und nutzt einen freien,
   expliziten Port.
3. Erfolgsnachweise: stabiler Prozess, keine zusätzliche Telegram-Verbindung,
   keine Bindung an Produktionsports, kein Zugriff auf die Produktions-DB,
   korrekte Resolver-Ausgabe, Ollama-Healthcheck, model-freie MCP/Skill-
   Discovery und Redaction-Scan der Logs.
4. Bei Exception, Adapteraktivierung, Produktionsdatei-Berührung oder
   Portkonflikt nur den Canary stoppen; Produktion bleibt unverändert.

### Phase E — Produktionswechsel (separater Schritt)

Erst wenn Phase A–D vollständig PASS sind, wird ein nummeriertes systemd-
Drop-in erstellt, das ausschließlich WorkingDirectory und ExecStart auf den
versionierten Release zeigt. Die Basisunit wird nicht überschrieben. Danach
folgen neue Session, Providerauflösung, Ollama-Canary, Owner-Telegram-Eingang
und die einzelnen Integrationsnachweise.

## Rollback

1. Fehlerkriterien: inaktiver Dienst, Restart-Schleife, Resolver-Abweichung,
   Telegram-Verlust, DB- oder Portkonflikt.
2. Nur die neue Release-Referenz stoppen und den neuen Drop-in entfernen bzw.
   deaktivieren.
3. `systemctl daemon-reload`, kontrollierter Start des unveränderten v0.13-
   Checkout und erneute Prüfung von PID, Restarts, Providerauflösung,
   Ollama-Loopback und Telegram-Polling.
4. Fehlgeschlagenes v0.21-Release und Canary-Home forensisch aufbewahren,
   bis Ursache, Redaction-Scan und Entsorgungsfreigabe dokumentiert sind.

## Freigabe- und Restlücken

| Voraussetzung vor Produktionsswitch | Status | Nächste sichere Evidenz |
|---|---|---|
| Versionierter Pfad statt Pull | **PASS** | Separaten Release verwenden |
| Sicherung und Delta-Patch-Matrix | **PARTIAL** | Snapshot und Klassifizierung erstellen |
| Frischer v0.21-venv | **PARTIAL** | Im neuen Release bauen und prüfen |
| Isoliertes Home | **PARTIAL** | Canary-Home ohne Produktions-DB erstellen |
| Keine doppelte externe Kommunikation | **BLOCKED** | Adapter im Canary vor Start deaktivieren |
| Effektive Modellauflösung | **PARTIAL** | Modelloverride gegen YAML prüfen |
| Gateway-Canary | **PARTIAL** | Getrennten Prozess ohne `--replace` nachweisen |
| Produktionswechsel | **BLOCKED** | Erst nach allen Canary-Prüfungen |
| Rollback | **PARTIAL** | Praktischen Drill nach dem Canary durchführen |

## Redaction-Check

**PASS.** Der Bericht enthält Versions-, Commit-, Pfad-, Dienst- und
Konfigurationsstrukturmetadaten, aber keine Token-, Key-, Passwort-, Cookie-,
privaten Schlüssel- oder `.env`-Werte.
