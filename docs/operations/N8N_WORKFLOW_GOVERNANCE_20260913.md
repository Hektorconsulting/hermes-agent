# n8n Workflow Governance & Safe Consolidation — 2026-09-13

## Entscheidungsstand

**Hermes Desktop** bleibt die führende Instanz. **Björn** ist der formelle
organisatorische Owner aller 36 n8n-Workflows. Namen wie ADAM, Hermes,
OpenClaw oder Paperclip bezeichnen technische Zielsysteme bzw. Adapter und
begründen keine abweichende Ownership.

Diese Abnahme hat keine Workflow-Löschung, Archivierung, Deaktivierung,
Veröffentlichung oder externe Kommunikation ausgelöst. Die vollständigen
Workflow-Definitionen wurden vorher auf dem VPS gesichert:

- Sicherung: `/home/ai-admin/.hermes/backups/n8n-governance-20260913/workflow-definitions.custom.dump`
- SHA-256: `48cdd84d977d402aaed4ee2f5b22e1fbed078db5fcac99a2761c1a93c3fdb067`
- Umfang: 36 Definitionen, inklusive Version-/Publikationshistorie.

## Kanonische Produktions-Allowlist

| Rolle | Workflow-ID | Flow | Zulässige Wirkung | Nachweis |
| --- | --- | --- | --- | --- |
| MCP-Gateway | `q3XX9KWOkBwxbcIz` | ADAM LIVE MCP Gateway v1 | Genau vier nachfolgende interne Tool-Wrapper | Graph aktuell gelesen; keine sonstigen Tool-Edges |
| Tool-Wrapper | `fkKu4tvxLGnAFQjR` | ADAM MCP Tool - Event Intake & HMAC Guard v1 | Signierter Aufruf an ADAM-LIVE Event-Contract | HMAC-Wrapper -> lokaler Webhook |
| Tool-Wrapper | `Phavo7BpKQM8ebbX` | ADAM MCP Tool - Multimodal Intake Queue v1 | Signierter Aufruf an ADAM-LIVE Multimodal-Contract | HMAC-Wrapper -> lokaler Webhook |
| Tool-Wrapper | `n6YE19rg68N8V0pW` | ADAM MCP Tool - Internal Signals & Daily Digest v1 | Ausschließlich interner Digest-Marker | `delivery=none`, `outbound_enabled=false` |
| Tool-Wrapper | `tMxA9reSDQ39wqfo` | ADAM MCP Tool - Dead Letter Recorder v1 | Redigierter interner DLQ-Record | interner Automation-Receiver |
| Live-Contract | `st2p1ATO2GAGkkn4` | ADAM LIVE Event Intake & HMAC Guard v1 | Signierter Receipt, keine Außenwirkung | HMAC, Schema, Retry x3, Error-Workflow |
| Live-Contract | `N0Po6Es788zBmaTf` | ADAM LIVE Multimodal Intake Queue v1 | Interne Queue, keine Kundenaktion | HMAC, `external_actions=0`, Retry x3, Error-Workflow |
| Live-Contract | `WuLqHjDuFT1Pe6zE` | ADAM LIVE Internal Signals & Daily Digest v1 | Interner Tagesmarker | Schedule, `delivery=none` |
| DLQ | `ADAMLiveDLQv1` | ADAM LIVE Dead Letter Recorder v1 | Redigierte Fehler-Metadaten, keine Außenwirkung | Error Trigger, interner Receiver, Retry x3 |

Die Gateway-Route verweist nachweislich exakt auf die vier Wrapper; diese
verweisen auf die vier ADAM-LIVE-Verträge. Das ist die komplette aktuelle
produktive Allowlist. Kein Telegram-, OpenClaw-, Paperclip-, Draft- oder
Strykly-Flow gehört dazu.

## Vollständige Registry

| ID | Workflow | Aktiv | Trigger/Verbraucher | Daten- und Außenwirkung | Fehler/Idempotenz | Klassifikation |
| --- | --- | ---: | --- | --- | --- | --- |
| `CAdlV88sxv3AXfjX` | Hermes Phase 2 Internal Receipt | nein | Manual | interner Receipt | keine externe Wirkung | DISABLED_RETAIN |
| `global-e2e-canary-v1` | [GLOBAL-E2E] Synthetic ADAM Queue Canary | ja | Header-geschützter Webhook -> `backend-fastapi` | interne technische Queue | kein DLQ-Verweis gelesen | ACTIVE_RETAIN |
| `q3XX9KWOkBwxbcIz` | ADAM LIVE MCP Gateway v1 | ja | MCP `/adam-live` -> 4 Wrapper | ausschließlich Allowlist-Routing | Timeout 60 s | CANONICAL |
| `tMxA9reSDQ39wqfo` | ADAM MCP Tool - Dead Letter Recorder v1 | ja | Execute-Workflow-Trigger -> intern | redigierter DLQ-Eintrag | siehe DLQ | CANONICAL |
| `fkKu4tvxLGnAFQjR` | ADAM MCP Tool - Event Intake & HMAC Guard v1 | ja | Execute-Workflow-Trigger -> lokaler Contract | signierter interner Receipt | HMAC / Live-Contract | CANONICAL |
| `Phavo7BpKQM8ebbX` | ADAM MCP Tool - Multimodal Intake Queue v1 | ja | Execute-Workflow-Trigger -> lokaler Contract | interne Queue | HMAC / Live-Contract | CANONICAL |
| `n6YE19rg68N8V0pW` | ADAM MCP Tool - Internal Signals & Daily Digest v1 | ja | Execute-Workflow-Trigger | interner Marker | keine Außenwirkung | CANONICAL |
| `st2p1ATO2GAGkkn4` | ADAM LIVE Event Intake & HMAC Guard v1 | ja | POST `adam-live-events-v1` -> ADAM intern | Receipt, `external_effect=none` | HMAC, UUID, Idempotenz, Retry x3, DLQ | CANONICAL |
| `N0Po6Es788zBmaTf` | ADAM LIVE Multimodal Intake Queue v1 | ja | POST `adam-live-multimodal-v1` -> ADAM intern | Queue-only, `external_actions=0` | HMAC, Retry x3, DLQ | CANONICAL |
| `WuLqHjDuFT1Pe6zE` | ADAM LIVE Internal Signals & Daily Digest v1 | ja | täglicher Schedule | interner Marker | `delivery=none` | CANONICAL |
| `ADAMLiveDLQv1` | ADAM LIVE Dead Letter Recorder v1 | ja | Error Trigger -> ADAM intern | redigierte Fehlerdaten | Retry x3; Abschlussstatus derzeit offen | CANONICAL |
| `E7ddKHglgvFWoald` | OpenClaw Staging - Codex Audit Result | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `dTmssAZza32XXmL9` | TELEGRAM_VOICE_TO_OPENCLAW | ja | Webhook -> `backend-fastapi` | Kommunikationskante | keine aktuelle E2E-Abnahme | LEGACY_REVIEW |
| `Dhsdx52kLR7FE9Yr` | OpenClaw Staging - OpenClaw Request | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `hmJUSgbSp6tkemvu` | MCP_HEALTHCHECK | nein | kein aktiver Trigger | technischer Check | nicht erneut ausgeführt | DISABLED_RETAIN |
| `Up2KXGgdexgPphYc` | OpenClaw Staging - Hermes Review | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `cyPFrmAkjgB4LToA` | OpenClaw Staging - Approval Gate | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `5fm9IEMlesp6Gn3l` | OpenClaw Staging - Execution Result | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `uVOiqFgBF2Btin1m` | OpenClaw Staging - Ticket Intake | nein | kein aktiver Trigger | historisches Staging | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `Xsp4uSwFDn3VVA8B` | HERMES_REVIEW_REQUEST | ja | Webhook `hermes-review-request` | technischer Review-Eingang | kein DLQ-Verweis | LEGACY_REVIEW |
| `phase17b-datatable-setup-20260703` | Hermes Registry DataTable Setup | nein | kein aktiver Trigger | interne Tabelle | nicht erneut ausgeführt | DISABLED_RETAIN |
| `97c185e6-6eb4-44c0-a0dd-d5c5d8e649bd` | Hermes Secret Catalog Metadata - Draft | nein | kein aktiver Trigger | historischer Metadatenentwurf | nicht erneut ausgeführt | ARCHIVE_CANDIDATE |
| `Fm0hdTSVGNqzFKIB` | PAPERCLIP_APPROVAL_GATE | ja | Webhook `paperclip-approval-gate` | technische Approval-Kante | kein DLQ-Verweis | LEGACY_REVIEW |
| `MFogOoBYoERSVjxC` | OPENCLAW_TASK_INTAKE | ja | Webhook `openclaw-task-intake` | technischer Intake | kein DLQ-Verweis | LEGACY_REVIEW |
| `gJsPO2Fj7D3R7bGo` | OPENCLAW_TASK_STATUS | ja | Webhook `openclaw-task-status` | technischer Status | kein DLQ-Verweis | LEGACY_REVIEW |
| `gXVkwIZktCs1e6Fs` | TOPDEALS_AGENT_FACTORY_BOOTSTRAP | nein | kein aktiver Trigger | historischer Bootstrap | nicht erneut ausgeführt | DISABLED_RETAIN |
| `itFkmawSvgW0Iri7` | AGENT_CREATE_WORKFLOW_SANDBOX | ja | Webhook `agent-create-workflow-sandbox` | technische Sandbox-Antwort | kein DLQ-Verweis | LEGACY_REVIEW |
| `rjtQfIMvETlDp6dM` | TELEGRAM_TEXT_TO_OPENCLAW | ja | Webhook -> `backend-fastapi` | Kommunikationskante | keine aktuelle E2E-Abnahme | LEGACY_REVIEW |
| `XiQ6UtOTr7mjti2i` | TELEGRAM_FILE_TO_OPENCLAW_INGESTION | ja | Webhook -> `backend-fastapi` | Kommunikationskante | keine aktuelle E2E-Abnahme | LEGACY_REVIEW |
| `4a783b34-5f02-4c85-9afe-85aac12a1f10` | Hermes Lovable Project Intake - Draft | ja | Header-geschützter Webhook -> DataTable | interne Registry | kein DLQ-Verweis | LEGACY_REVIEW |
| `2f4499ef-f0e4-4125-8b4a-401d18f6a826` | Hermes GitHub Repo Intake - Draft | ja | Header-geschützter Webhook -> DataTable | interne Registry | kein DLQ-Verweis | LEGACY_REVIEW |
| `adamStagingMmV1` | ADAM-STAGING-MULTIMODAL-INTAKE-V1 | nein | Staging / Schedule | historische interne Audio-Pipeline | HMAC, Idempotenz im Entwurf | ARCHIVE_CANDIDATE |
| `adamDemoLeadSprint1` | ADAM DEMO · Lead Intake · DISABLED | nein | Manual | Demo ohne Außenwirkung | inaktiv | ARCHIVE_CANDIDATE |
| `adamDemoInvoiceS1` | ADAM DEMO · Invoice Guard · DISABLED | nein | Manual | Demo ohne Außenwirkung | inaktiv | ARCHIVE_CANDIDATE |
| `adamDemoCalendarS1` | ADAM DEMO · Calendar Preparation · DISABLED | nein | Manual | Demo ohne Google-Aufruf | inaktiv | ARCHIVE_CANDIDATE |
| `yxZBu8zSEKCa40US` | 01 Strykly Event Intake | ja | POST `strykly/events` | HMAC-Eingang, nur Antwort-Node | kein DLQ-/Retry-Nachweis | LEGACY_REVIEW |

## Frische Canary-Nachweise

| Test | Ergebnis | Beweis |
| --- | --- | --- |
| ungültige Signatur | PASS | 401 `signature_invalid`; `external_effect=none` |
| ungültige `event_id` | PASS | 400 `invalid_record`; Schema erzwingt UUID; `external_effect=none` |
| gültiger interner Eingang | PASS | POST zum lokalen n8n-Webhook: 202 `accepted`, `outbound_enabled=false` |
| Replay / Idempotenz | PASS | gleicher Envelope: 200 `duplicate`, keine zweite Außenwirkung |
| Fehlerpfad / DLQ-Readback | PARTIAL | Error Trigger wurde für die kontrollierten Schema-Fehler gestartet, aber die beiden DLQ-Executions bleiben `running`; kein finaler DLQ-Persistenzabschluss nachgewiesen |

## Wesentlicher Befund und kontrollierter Rollback

Die erfolgreiche Receipt-Ausführung bleibt in n8n ebenfalls als `running`
sichtbar, obwohl der HTTP-Antwortvertrag 202/200 vollständig durchlief. Das
ist ein Recoverability-Defekt der n8n-Ausführungsfinalisierung bzw. des
Runner-/Error-Trigger-Pfads. Er darf nicht durch manuelles Datenbank-Löschen
verdeckt werden.

Rollback für künftige Governance-Änderungen: erst n8n anhalten, den obigen
Custom-Dump über `pg_restore` gezielt wiederherstellen, n8n starten, Anzahl,
Versionen und Allowlist erneut lesen. In dieser Abnahme war kein Rollback
erforderlich, weil keine Workflow-Definition geändert wurde.

## Nächster technischer Auftrag

`n8n Execution Finalization & DLQ Recovery`: Ursache der hängenden
Ausführungen in n8n/runners/queue ermitteln, die korrekte Finalisierung
nachweisen und anschließend einen redigierten DLQ-Record mit Readback testen.
Bis dahin bleiben alle LEGACY_REVIEW-Flows unverändert, aktiv aber nicht Teil
der produktiven Hermes-Allowlist.

## Retest: Execution-Finalisierung 2026-09-13

Der obige Befund ist historischer Canary-Kontext und kein aktueller
Runtime-Status mehr. Eine frische, metadata-only n8n-Abfrage (ohne
Ausführungsdaten oder Header) ergab für `st2p1ATO2GAGkkn4` und
`ADAMLiveDLQv1` jeweils **0** Executions mit Status `running` oder `waiting`.
Die früher referenzierten IDs sind nicht mehr abrufbar. Die noch am selben Tag
sichtbaren Event-Intake-Canaries `531` und `533` sind sauber als `error` mit
`stoppedAt` finalisiert; sie waren kontrollierte Negativtests und erzeugten
keine Außenwirkung.

**Aktueller Status:** PASS für Execution-Finalisierung und fehlende hängende
Runs. Der nächste Auftrag aus dem vorigen Abschnitt ist damit geschlossen.
Eine erneute DLQ-Fehler-Injektion ist nicht erforderlich, solange weder der
kanonische Flow noch n8n-Runtime/Queue-Konfiguration relevant verändert wird.
