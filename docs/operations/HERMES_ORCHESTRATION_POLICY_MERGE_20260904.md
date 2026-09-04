# Hermes orchestration policy merge — 2026-09-04

## Decision

The current owner goal is the only governing autonomy policy for this run.
The local `hermes-orchestration` skill remains available as a technical
reference with its historical approval restrictions deactivated. The
machine-readable owner policy in this repository is canonical.

## Rule classification

| Source / rule | Classification | Canonical treatment |
|---|---|---|
| Skill D01: inspect current state first | KEEP | Evidence-first execution |
| Skill D02: separate Windows, VPS, n8n, GitHub, Google, Cloudflare and messaging | KEEP | Surface-specific registry |
| Skill D03: maintain a tool-registry row | KEEP | Registry and knowledge lifecycle |
| Skill D04: Vault is raw secret authority; n8n uses references | MERGE_INTO_CANONICAL_POLICY | Secret authority invariant |
| Skill D05: never print secret values | KEEP | Security invariant |
| Skill D06: classify mutation before execution | KEEP | Change provenance |
| Skill D07: deploy/DNS/credentials require approval | SUPERSEDED_BY_OWNER_POLICY | Reversible owner-infrastructure work is autonomous |
| Skill D08: durable artifacts, redaction and handoff sync | MERGE_INTO_CANONICAL_POLICY | Required write-back and documentation |
| Skill G01: no restart/firewall/delete/DNS without separate approval | SUPERSEDED_BY_OWNER_POLICY | Only canonical external/physical/irreversible gates remain |
| Skill G02: authenticated webhook gate | KEEP | Security and fail-closed behavior |
| Skill G03: treat logged-in browser sessions as high risk | KEEP | Credential/session safety |
| Skill G04: prefer PRs and avoid direct `main` | SUPERSEDED_BY_OWNER_POLICY | Owner fork may receive direct validated push |
| Skill G05: distinguish Lovable inventory from mutation | KEEP | Surface and scope clarity, not a human gate |
| Skill G06: verify VPS before changing Docker/NGINX/systemd | KEEP | Targeted evidence check |
| Repo `AGENTS.md`: narrow core, plugin seams, cache/message invariants | KEEP | Project engineering constraints |
| Repo `AGENTS.md`: CI/test and source-quality rules | KEEP | Technical quality constraints |
| Repo `AGENTS.md`: upstream maintainer review preferences | KEEP | Applies to upstream contribution quality, not owner autonomy |
| `apps/desktop/AGENTS.md`: authority, scope, retries and connection behavior | KEEP | Desktop engineering invariants |
| Canonical owner policy: external/interactive/physical/irreversible/payment gates | MERGE_INTO_CANONICAL_POLICY | Sole gate definition |

## Replaced/deactivated content

The local skill's former blanket approval language has been replaced by a
non-governing reference notice. No technical topology or safety invariant was
removed. The previous skill file was backed up before replacement at:

`C:\Hermes\backups\hardening-20260904-054724\hermes-orchestration-SKILL.before-owner-policy-20260904.md`

The repository `AGENTS.md` and desktop engineering guide are not autonomy
policies. They remain because they encode code-level invariants, profile
isolation, bounded retries, testing behavior and UI/backend authority. Where a
contribution preference conflicts with the current owner goal, the owner policy
controls the operational action.

## Canonical execution rule

```text
DISCOVER -> REUSE EVIDENCE -> BACKUP -> FIX -> TEST -> DEPLOY -> VERIFY
-> COMMIT -> PUSH -> KNOWLEDGE WRITEBACK
```

Technical failures are assigned to Codex/Hermes. Stop only for the six gates in
`canonical-owner-autonomy-policy.json`.
