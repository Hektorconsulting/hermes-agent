# Hermes architecture glossary

**Scope:** current architecture handover, generated from fresh runtime evidence
on 2026-09-13. A term is not a deployment claim unless marked
`CURRENT_VERIFIED` in the registry.

| Term | Meaning in this system | Status / boundary |
| --- | --- | --- |
| Hermes Desktop | The one owner-facing Chief and Dispatcher. It decides; it does not create a second VPS brain. | `CURRENT_VERIFIED` |
| Codex | Technical executor acting within a Hermes/owner TaskEnvelope. | `CURRENT_VERIFIED` |
| VPS runtime | Versioned `ai-admin` release started by `hermes-gateway.service`. | `CURRENT_VERIFIED` |
| OpenClaw edge | Loopback-only communication/device gateway on port 18789, owned by `openclaw-gateway.service` under `ai-admin`. | `CURRENT_VERIFIED` |
| shared_kb | VPS-first, redacted durable knowledge database. Desktop storage is mirror/fallback, not an authority. | `CURRENT_VERIFIED` |
| Execution ledger | Separate VPS SQLite evidence store for idempotent runs, events, handovers and checksum recall. | `CURRENT_VERIFIED` |
| TaskEnvelope | Typed work envelope with stable task and idempotency identities. It creates a deterministic evidence trail; it is not an autonomous second agent. | `CURRENT_VERIFIED` |
| FTS retrieval | `chunks_fts` lexical retrieval in shared_kb. No vector/embedding retrieval claim is made. | `CURRENT_VERIFIED` |
| MCP stdio | Local client launches a subprocess and exchanges JSON-RPC through stdin/stdout. This is the transport used by the documented bridge processes. | `CURRENT_VERIFIED` |
| Streamable HTTP | Standard MCP HTTP transport. It is a protocol option, not asserted as the deployed transport for the local bridges. | `PROPOSED` only if a concrete remote-client need emerges |
| n8n canonical route | HMAC-protected ADAM workflow route with UUID/event and idempotency contracts, retry and DLQ. | `CURRENT_VERIFIED` |
| HMAC | A request-integrity/authentication control. Registry holds only the secret reference and header/schema rule; values are runtime-only. | `CURRENT_VERIFIED` |
| A2A | Agent-to-agent standard for independent opaque agent systems. Current map does not install or require it. | `NOT_APPLICABLE` |
| FastAPI | Dependency and historically evidenced control-plane implementation. No new FastAPI layer is added by this handover. | `CURRENT_PARTIAL` |
| GOWA / WhatsApp | Internal communication edge with health evidence. Device/QR pairing and external E2E remain human gates. | `CURRENT_PARTIAL` / `OWNER_GATE` |
| Voice | Speaches runtime containers are present; microphone-to-speaker acceptance needs a physical owner test. | `OWNER_GATE` |
| Google Drive master index | Human-readable transition documentation; it is not a replacement for the canonical ledger or shared_kb. | `CURRENT_VERIFIED` |
| ChatGPT Projects API | No direct API is available in this runtime. | `NOT_AVAILABLE` |

## Classification contract

- `CURRENT_VERIFIED`: current targeted runtime or authenticated readback evidence.
- `CURRENT_PARTIAL`: a real component exists, but a stated proof layer is absent.
- `HISTORICAL`: retained provenance; never current truth without a targeted reread.
- `PROPOSED`: evaluated option, not a deployment instruction.
- `OWNER_GATE`: OAuth/2FA/CAPTCHA, QR/device pairing, physical E2E, payment or external communication requires the owner.
- `NOT_AVAILABLE`: capability is absent in the current runtime.

## Source-selection rule

Use `HERMES_ARCHITECTURE_REGISTRY.json` for machine interpretation, the
Mermaid files for relationships, and `ARCHITECTURE_EVIDENCE_MATRIX.md` for
proof. Reuse `CURRENT_VERIFIED` facts until an affected mutation, endpoint
change, runtime restart/deploy, or concrete failure requires a targeted reread.
