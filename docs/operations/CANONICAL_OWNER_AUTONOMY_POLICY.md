# Canonical Owner Autonomy Policy

This policy replaces older project-specific autonomy and human-gate notes for
the authorized Hermes owner infrastructure. Platform security rules, provider
terms, authentication requirements, tenant isolation, and data-protection
requirements remain in force.

## Autonomous scope

Hermes/Codex may inspect, repair, test, document, commit, push and deploy
reversible technical changes in the authorized Hermes environment. Every
change follows:

`BACKUP → CHANGE → TEST → VERIFY → COMMIT → PUSH → DEPLOY → KNOWLEDGE_WRITEBACK`

This includes code, internal registries, shared knowledge, runtime
configuration, Docker/proxy configuration, n8n workflow mechanics, model
routing, backups, monitoring and OpenClaw server-side integration.

## Hard stops

Only the following remain owner/physical gates: interactive OAuth consent,
2FA/CAPTCHA, physical smartphone or QR pairing, irreversible deletion without
restore, real external customer/payment communication, and a new paid
contract or financial commitment. A technical error, timeout, DNS defect,
missing configuration or deployment failure is an engineering issue and must
be diagnosed and repaired autonomously.

## Security invariants

Secrets are never printed or persisted in logs, context packs or knowledge
entries. Vault or the existing secret store is authoritative for secret
values; n8n and other consumers use references. Authentication, RLS/tenant
boundaries, backups, rollback and provenance may not be weakened.

The machine-readable policy is
`docs/operations/canonical-owner-autonomy-policy.json`.
