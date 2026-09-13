# Architecture evidence matrix

**Snapshot:** 2026-09-13 20:05 UTC. Evidence is deliberately separated from
historical documentation. No diagram contains credentials, customer content or
unredacted configuration.

| ID | Claim | Classification | Fresh evidence | Restriction / next trigger |
| --- | --- | --- | --- | --- |
| E-001 | Hermes Desktop is the only Chief/Dispatcher. | CURRENT_VERIFIED | `MASTER_AUTONOMY_INDEX.md`, owner policy, current registry. | VPS may execute/recover/gateway only. |
| E-002 | Hermes release is active as `ai-admin` from the versioned release path. | CURRENT_VERIFIED | `systemctl show hermes-gateway.service`, 2026-09-13 20:05 UTC. | Reread after deploy/restart. |
| E-003 | OpenClaw listens only on `127.0.0.1` and `::1` port 18789. | CURRENT_VERIFIED | `ss -ltnp`, 2026-09-13 20:05 UTC. | Any proxy/firewall/routing change requires reread. |
| E-004 | One canonical OpenClaw bridge remains. | CURRENT_VERIFIED | Canonical release child count = 1 after controlled removal of root SSH child; both gateways active. | Reopen if a second process appears. |
| E-005 | shared_kb is VPS-first and has deterministic write/read/recall evidence. | CURRENT_VERIFIED | Runtime compatibility closure and current release bridge child. | Local cache is fallback only. |
| E-006 | Ledger supports idempotent run creation and checksum handover recall. | CURRENT_VERIFIED | `execution_ledger.py`, handover closure checksum evidence. | Verify again for material handover. |
| E-007 | FTS retrieval exists in shared_kb. | CURRENT_VERIFIED | `tools/shared_knowledge/bridge.py` uses `chunks_fts`. | No vector/embedding quality claim. |
| E-008 | n8n runtime is healthy and loopback-bound. | CURRENT_VERIFIED | `n8n`, `n8n-runners`, `n8n-postgres` Docker health; listener 127.0.0.1:5678. | Recheck after compose/runtime mutation. |
| E-009 | n8n canonical event contracts have HMAC, UUID, idempotency, retry and DLQ rules. | CURRENT_VERIFIED | `N8N_CONTRACT_REGISTRY.json`, verified 2026-09-13T11:52:11Z. | Secret values intentionally unavailable. |
| E-010 | GOWA is runtime-healthy. | CURRENT_PARTIAL | healthy Docker container and loopback port 18082. | QR/device pairing and external E2E are owner gates. |
| E-011 | Voice runtime containers exist. | OWNER_GATE | Speaches containers running. | Physical microphone/speaker acceptance not run. |
| E-012 | Google Drive index has authenticated current read/write evidence. | CURRENT_VERIFIED | Master index current state. | OAuth re-consent would reopen a human gate. |
| E-013 | A2A is not a current deployed boundary. | NOT_APPLICABLE | Current ownership uses TaskEnvelope/ledger/MCP; no required independent AgentCard boundary. | Reassess only for a real independent agent integration. |
| E-014 | FastAPI requires no new deployment. | CURRENT_PARTIAL | Dependency present; historical OpenClaw control-plane evidence. | Prove an unmet API need before adding a service. |
| E-015 | ChatGPT Projects has no direct runtime API. | NOT_AVAILABLE | Current master index. | Drive + shared_kb are documented transition layers. |

## Protocol research assessment

| Topic | Primary-source finding | System decision |
| --- | --- | --- |
| MCP | MCP uses UTF-8 JSON-RPC; standard transports are stdio and Streamable HTTP. Stdio is a client-launched subprocess; Streamable HTTP must validate Origin, use localhost when local, and authenticate. | Retain current local stdio bridges and loopback boundary. Do not expose a remote MCP endpoint without a concrete client, Origin validation and authentication design. |
| A2A | A2A standardizes discovery, task lifecycle and secure collaboration for independent opaque agents. | Do not install it merely as a trend: current same-owner dispatcher/executor path already has TaskEnvelope, ledger and MCP. |
| OpenAI tools | OpenAI’s current platform documentation supports custom tools, remote MCP and Agents SDK orchestration. | Retain explicit tool allowlists and human gates; no provider-specific new control plane is necessary. |
| Retrieval | Current shared_kb proof is lexical FTS. | Retain. Add semantic/vector retrieval only after a measured retrieval-quality and access-control gap. |

Sources: [MCP transports specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports), [A2A specification](https://github.com/a2aproject/A2A/blob/main/docs/specification.md), [OpenAI developer quickstart and tools](https://developers.openai.com/quickstart/), [OpenAI practical agent guide](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/).

## Registry/diagram consistency check

`diagram_edge_inventory` in the registry records every direct Mermaid edge:
`EDGE-001…016`, `EDGE-101…112`, and `EDGE-201…217`. Each entry names both
endpoints, protocol, authentication reference, allowed effect, evidence/status
and the exact Mermaid edge reference. The richer top-level `edges` records
retain the ten principal machine-integration contracts with their full
data-class and rollback detail.
