# Hermes VPS Telegram Owner Allowlist

Status: configured and gateway-verified; external DM canary pending —
2026-09-06

The VPS Hermes Gateway now has an explicit `TELEGRAM_ALLOWED_USERS` entry for
the Owner identity already recorded in the local Hermes platform profile. The
value is intentionally not repeated in Git, reports or logs. The global
`GATEWAY_ALLOW_ALL_USERS` bypass is not set.

Evidence:

```text
owner allowlist variable       = present (value redacted)
global allow-all bypass        = absent
hermes-gateway.service         = active
post-restart allowlist warning = absent
groups/customer channels       = not enabled by this change
```

This change authorizes only the configured Owner identity at the gateway
boundary. It does not send a Telegram message, join a group, broadcast, or
alter customer channels. A real inbound/outbound private Owner-DM test is the
remaining external communication proof.
