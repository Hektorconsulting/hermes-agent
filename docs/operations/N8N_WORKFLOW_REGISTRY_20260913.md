# n8n Workflow Registry — 2026-09-13

**Superseded for governance:** This initial MCP-only inventory is retained as
historical baseline. The current, VPS-admin-read governance registry with
formal Björn ownership, canonical allowlist, Canary evidence and the actual
execution-finalization gap is
[`N8N_WORKFLOW_GOVERNANCE_20260913.md`](N8N_WORKFLOW_GOVERNANCE_20260913.md).

| ID | Workflow | Active | Trigger count | MCP | Updated (UTC) | Owner | Purpose | Data / external effect | Classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `CAdlV88sxv3AXfjX` | Hermes Phase 2 Internal Receipt | no | 0 | yes | 2026-09-12T22:26:34.463Z | Hermes | Internal Phase 2 receipt test. Manual-only, no external effects. | Internal/no external stated | **DISABLED_RETAIN** |
| `global-e2e-canary-v1` | [GLOBAL-E2E] Synthetic ADAM Queue Canary | yes | 1 | no | 2026-08-31T22:26:38.014Z | ADAM | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `q3XX9KWOkBwxbcIz` | ADAM LIVE MCP Gateway v1 | yes | 1 | no | 2026-08-16T22:52:24.640Z | ADAM | Not documented | UNVERIFIED | **ACTIVE_RETAIN** |
| `tMxA9reSDQ39wqfo` | ADAM MCP Tool - Dead Letter Recorder v1 | yes | 0 | no | 2026-08-16T22:49:28.407Z | ADAM | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `fkKu4tvxLGnAFQjR` | ADAM MCP Tool - Event Intake & HMAC Guard v1 | yes | 0 | no | 2026-08-16T22:49:27.818Z | ADAM | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `Phavo7BpKQM8ebbX` | ADAM MCP Tool - Multimodal Intake Queue v1 | yes | 0 | no | 2026-08-16T22:49:27.413Z | ADAM | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `n6YE19rg68N8V0pW` | ADAM MCP Tool - Internal Signals & Daily Digest v1 | yes | 0 | no | 2026-08-16T22:47:33.376Z | ADAM | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `st2p1ATO2GAGkkn4` | ADAM LIVE Event Intake & HMAC Guard v1 | yes | 1 | yes | 2026-08-16T14:54:52.191Z | ADAM | Validates signed ADAM events, enforces idempotent persistence, and routes technical failures to the dead-letter queue. | UNVERIFIED; may touch communication/ingress | **ACTIVE_RETAIN** |
| `N0Po6Es788zBmaTf` | ADAM LIVE Multimodal Intake Queue v1 | yes | 1 | yes | 2026-08-16T14:54:17.476Z | ADAM | Queues validated ADAM multimodal intake envelopes for internal processing; it does not trigger external customer actions. | Internal/no external stated | **ACTIVE_RETAIN** |
| `WuLqHjDuFT1Pe6zE` | ADAM LIVE Internal Signals & Daily Digest v1 | yes | 1 | yes | 2026-08-16T14:51:57.496Z | ADAM | Produces ADAM internal signals and a daily digest for operational review; external delivery remains disabled. | Internal/no external stated | **ACTIVE_RETAIN** |
| `ADAMLiveDLQv1` | ADAM LIVE Dead Letter Recorder v1 | yes | 0 | yes | 2026-08-16T14:51:29.065Z | ADAM | Records ADAM workflow failures in the dead-letter queue for controlled diagnosis and recovery; no external customer action. | Internal/no external stated | **ACTIVE_RETAIN** |
| `E7ddKHglgvFWoald` | OpenClaw Staging - Codex Audit Result | no | 0 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `dTmssAZza32XXmL9` | TELEGRAM_VOICE_TO_OPENCLAW | yes | 1 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `Dhsdx52kLR7FE9Yr` | OpenClaw Staging - OpenClaw Request | no | 0 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `hmJUSgbSp6tkemvu` | MCP_HEALTHCHECK | no | 0 | no | 2026-08-16T14:49:47.426Z | UNVERIFIED | Not documented | UNVERIFIED | **DISABLED_RETAIN** |
| `Up2KXGgdexgPphYc` | OpenClaw Staging - Hermes Review | no | 0 | no | 2026-08-16T14:49:47.426Z | Hermes | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `cyPFrmAkjgB4LToA` | OpenClaw Staging - Approval Gate | no | 0 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `5fm9IEMlesp6Gn3l` | OpenClaw Staging - Execution Result | no | 0 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `uVOiqFgBF2Btin1m` | OpenClaw Staging - Ticket Intake | no | 0 | no | 2026-08-16T14:49:47.426Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `Xsp4uSwFDn3VVA8B` | HERMES_REVIEW_REQUEST | yes | 1 | no | 2026-08-16T14:49:32.088Z | Hermes | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `phase17b-datatable-setup-20260703` | Hermes Registry DataTable Setup | no | 0 | no | 2026-08-16T14:49:32.088Z | Hermes | Not documented | UNVERIFIED | **DISABLED_RETAIN** |
| `97c185e6-6eb4-44c0-a0dd-d5c5d8e649bd` | Hermes Secret Catalog Metadata - Draft | no | 0 | no | 2026-08-16T14:49:32.088Z | Hermes | Not documented | UNVERIFIED | **ARCHIVE_CANDIDATE** |
| `Fm0hdTSVGNqzFKIB` | PAPERCLIP_APPROVAL_GATE | yes | 1 | no | 2026-08-16T14:49:32.088Z | Legacy control-plane | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `MFogOoBYoERSVjxC` | OPENCLAW_TASK_INTAKE | yes | 1 | no | 2026-08-16T14:49:32.088Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `gJsPO2Fj7D3R7bGo` | OPENCLAW_TASK_STATUS | yes | 1 | no | 2026-08-16T14:49:32.088Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `gXVkwIZktCs1e6Fs` | TOPDEALS_AGENT_FACTORY_BOOTSTRAP | no | 0 | no | 2026-08-16T14:49:32.088Z | UNVERIFIED | Not documented | UNVERIFIED | **DISABLED_RETAIN** |
| `itFkmawSvgW0Iri7` | AGENT_CREATE_WORKFLOW_SANDBOX | yes | 1 | no | 2026-08-16T14:49:32.088Z | UNVERIFIED | Not documented | UNVERIFIED | **LEGACY_REVIEW** |
| `rjtQfIMvETlDp6dM` | TELEGRAM_TEXT_TO_OPENCLAW | yes | 1 | no | 2026-08-16T14:49:32.088Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `XiQ6UtOTr7mjti2i` | TELEGRAM_FILE_TO_OPENCLAW_INGESTION | yes | 1 | no | 2026-08-16T14:49:32.088Z | OpenClaw | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `4a783b34-5f02-4c85-9afe-85aac12a1f10` | Hermes Lovable Project Intake - Draft | yes | 1 | no | 2026-08-16T14:49:14.329Z | Hermes | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `2f4499ef-f0e4-4125-8b4a-401d18f6a826` | Hermes GitHub Repo Intake - Draft | yes | 1 | no | 2026-08-16T14:48:22.889Z | Hermes | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |
| `adamStagingMmV1` | ADAM-STAGING-MULTIMODAL-INTAKE-V1 | no | 0 | no | 2026-07-28T21:57:15.352Z | ADAM | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `adamDemoLeadSprint1` | ADAM DEMO · Lead Intake · DISABLED | no | 0 | no | 2026-07-26T11:13:35.625Z | ADAM | Not documented | UNVERIFIED; may touch communication/ingress | **ARCHIVE_CANDIDATE** |
| `adamDemoInvoiceS1` | ADAM DEMO · Invoice Guard · DISABLED | no | 0 | no | 2026-07-26T11:13:31.138Z | ADAM | Not documented | UNVERIFIED | **ARCHIVE_CANDIDATE** |
| `adamDemoCalendarS1` | ADAM DEMO · Calendar Preparation · DISABLED | no | 0 | no | 2026-07-26T11:13:26.393Z | ADAM | Not documented | UNVERIFIED | **ARCHIVE_CANDIDATE** |
| `yxZBu8zSEKCa40US` | 01 Strykly Event Intake | yes | 1 | no | 2026-07-12T23:35:51.029Z | UNVERIFIED | Not documented | UNVERIFIED; may touch communication/ingress | **LEGACY_REVIEW** |

## Classification summary

- CANONICAL: 0 (formal owner designation not yet recorded)
- ACTIVE_RETAIN: 5
- LEGACY_REVIEW: 16
- DISABLED_RETAIN: 4
- ARCHIVE_CANDIDATE: 11

## Next controlled action

For every LEGACY_REVIEW and ARCHIVE_CANDIDATE, record a named owner, current consumer, trigger route, rollback path, and whether external effects are possible. Only then propose a separate disable/archive change set.
