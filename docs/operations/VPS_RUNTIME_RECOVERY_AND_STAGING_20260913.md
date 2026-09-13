# VPS Runtime Recovery and Staging — 2026-09-13

## Scope

This record closes two recoverability defects without replacing the running
VPS runtime: mixed file ownership and an unsafe direct-pull assumption.
Hermes Desktop remains the leading control plane.

## Verified repair

- The running checkout is `/home/ai-admin/.hermes/hermes-agent` at
  `9e005d6779433255722cbb40e0f982abf1610c6b` and is 19,624 commits behind
  `origin/main`. A direct production pull would therefore be a major upgrade,
  not a hygiene operation.
- Before change, a recovery bundle was made at
  `/home/ai-admin/.hermes/backups/n8n-exec-finalization-20260913/vps-runtime-prepull`.
  It contains porcelain state, a binary tracked-file patch, an untracked-file
  archive, and the pre-repair Git ownership manifest.
- Git metadata had 276 entries not owned by `ai-admin` (264 Git objects).
  All `.git` metadata and the explicitly inventoried untracked Runtime files
  now belong to `ai-admin`; fetch, object validation, and a clean checkout are
  again possible.
- A detached, clean staging checkout of `origin/main` exists at
  `/home/ai-admin/.hermes/staging/hermes-agent-origin-main-20260913`, commit
  `0520da23c7eefe1b05c21351629e94410e50c1b3`. Its Git status is empty.

## Deliberate boundary

The 21 legacy overlay candidates are backed up and preserved in the dedicated
remote branch `recovery/vps-runtime-prepull-20260913` at
`7afd0b95244e41f6126c9a6078011efa0049db6e`. A redacted static scan found no
API-key, private-key, or password literal; the only literal token default is
an empty string and all other token values are runtime-derived. The running
legacy checkout is therefore clean again. This recovery branch is not an
upgrade branch and must not be merged into `main` without targeted review.

## Upgrade rule

The controlled release cutover completed after focused runtime tests,
read-only OpenClaw health, and MCP handshake verification. The active systemd
gateway now runs the release at
`/home/ai-admin/.hermes/releases/hermes-vps-cutover-20260913`, commit
`4302074af66e1e061fb25b84bf4cd4abecc5ab53`. Its two internal bridges run the
release source while retaining the explicit legacy MCP adapter interpreter;
this is a deliberate, tested compatibility boundary, not an untracked drift.

The service, OpenClaw loopback boundary, n8n containers, shared_kb readback,
and ledger readback all passed after the cutover. Rollback remains the
immutable recovery bundle plus restoration of the prior systemd drop-in and
`config.yaml` copies under
`/home/ai-admin/.hermes/backups/hermes-vps-cutover-20260913-attempt3`.
