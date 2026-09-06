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

## Current reconciliation

The live local configuration uses OpenRouter explicitly with the redacted
credential-pool label `Hermes-G`. The primary route is a verified free,
tool-capable OpenRouter model; the configured fallback sequence contains
additional free models, `~deepseek/deepseek-v4-flash-latest`, LM Studio and a
private local-compatible endpoint. The old `env:OPENROUTER_API_KEY` pool entry
was removed from Hermes rotation after it produced the wrong-account 402
behavior; the value remains intentionally undisclosed and is not re-added.

Paid OpenRouter requests are bounded by `model.context_length: 32768` so a
large theoretical provider context cannot request an uncontrolled output
budget. Full handover material remains available through the local files,
SQLite knowledge projection and VPS shared-KB bridge and is read
incrementally. Auxiliary traffic remains `free_only: true`.

The current provider state must still be reported live because OpenRouter
free quota and key budget are volatile. A 429 or 402 is classified and routed
to an independent private fallback rather than retried through another
OpenRouter-free model indefinitely.
