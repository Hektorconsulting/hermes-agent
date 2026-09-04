# Hermes integration governance

This registry is the operating contract for the owner-controlled Hermes
infrastructure. It is intentionally separate from live credentials and from
historical handover prose. Current evidence is reused before a targeted
readback; absence in a new probe is not proof of absence in the system.

## Ownership and execution

| Area | Owner / executor | State | Operational rule |
|---|---|---|---|
| Hermes Core | Hermes Desktop / Hermes | VERIFIED_REUSED | Do not re-audit the verified owner-to-shared-kb chain without mutation. |
| shared_kb | Hermes | PASS | Canonical VPS DB is primary for local preflight/write-back; local SQLite is a synchronized cache/fallback; results are namespace-scoped and redacted. |
| n8n | Hermes | VERIFIED_REUSED | Reuse the authenticated MCP/workflow path and reviewed allowlist; n8n holds references, not raw secret authority. |
| Vault | Hermes | GOVERNED | Vault or the existing secret store is authoritative; never put values in logs, packs or write-backs. |
| Cloudflare / DNS / NGINX | Hermes | PASS_WITH_RETIRED_LEGACY_ROUTE | Keep public edge routes intentional and administrative surfaces private. The obsolete unauthenticated Hermes dashboard proxy is retired; port 81 is not publicly allowed by UFW and Docker `DOCKER-USER` policy is reconciled by a timer. |
| Backups / Docker / Watchtower | Hermes | PASS | Managed backup/timer, rollback paths and non-destructive restore rehearsal are complete. |
| OpenClaw | OpenClaw via Hermes | SERVER_READY / MOBILE_DEFERRED | Server runtime and Vault-backed launcher are technical scope; Tailscale login and device pairing are external gates. |
| Google Workspace | Hermes / n8n | CONSENT_CONDITIONAL | Reuse an existing authorized session; interactive OAuth, 2FA or CAPTCHA is an owner gate only when unavoidable. |
| ADAM / Supabase | Hermes | TARGET_GATED | Prove the effective external target and preserve owner/admin/customer isolation before data or RLS changes. |
| Paperclip | Paperclip / Hermes | GOVERNANCE_REQUIRED | Keep irreversible, elevated-risk, external and financial operations approval-gated. |
| Models / OpenRouter | Hermes | PASS_FREE_FIRST | Current tool-capable cost-efficient routing and fallbacks are catalog-verified; no paid benchmark required. |
| Windows / VS Code | Hermes | PASS_AUTOMATED_STARTUP | Startup, reconnect and exact project identity are engineering work; existing watchdog/recovery controls are active and physical sign-in remains a gate. |
| Knowledge lifecycle | Hermes | PASS | Maintain source registry, archive, task lineage, provenance and mirror; classify stale/conflicting sources during lifecycle review. |

## Required execution order

For reversible infrastructure work use:

```text
BACKUP -> CHANGE -> TEST -> VERIFY -> COMMIT -> PUSH -> DEPLOY -> KNOWLEDGE_WRITEBACK
```

The owner gate list is deliberately narrow:

- interactive OAuth consent, 2FA or CAPTCHA;
- physical smartphone installation, permissions, QR pairing or device approval;
- missing external account or organization permission;
- irreversible deletion without a verified restore path;
- real external customer/payment communication;
- new paid contracts or financial commitments.

Technical failures in the listed systems are assigned to Hermes unless they
fall into one of those explicit gates. OpenClaw mobile remains deferred and
must not block the Hermes-to-Codex or Hermes-to-n8n control plane.
