# Hermes model-routing policy

Status: active cost-control baseline, 2026-09-04

Hermes owns model selection for owner-controlled orchestration. The policy
keeps the verified control path independent from paid benchmark activity and
does not store provider credentials or secret values.

## Routing tiers

1. Use the active, currently available, tool-capable model already configured
   for Hermes Desktop/OpenRouter.
2. Prefer a free or lowest-cost model for read-only inspection, registry
   lookup, knowledge preflight and synthesis when it supports the required
   context and tools.
3. Use a more capable model only when the task requires it, with the same
   TaskEnvelope, privacy scope and provenance.
4. On provider/model failure, use a configured compatible fallback and record
   the routing decision; do not run an unnecessary benchmark.

## Guardrails

- Never print or persist API keys, bearer tokens or provider secret values.
- Never infer model readiness from configuration alone: the active model must
  be available to the configured provider and compatible with the requested
  tool path.
- Keep a paid-model route disabled unless it is already authorized and within
  the owner’s cost policy. A new paid commitment remains an owner gate.
- Record provider, model identifier, cost tier, fallback and reason in
  redacted operational provenance.
- Do not retest the verified Hermes -> Codex -> n8n -> Synthesis -> shared_kb
  chain unless a model or routing mutation affects it.

## Operational gap

The remaining optimization is a configuration/catalog reconciliation: compare
the active Hermes Desktop model identifier with the current provider catalog,
then change only an invalid identifier to an available, tool-capable,
cost-efficient model. This is a technical fix when the provider session is
already authorized; interactive provider consent or a new paid commitment is
not automated.
