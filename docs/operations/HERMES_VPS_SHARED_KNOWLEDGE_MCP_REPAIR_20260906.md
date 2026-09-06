# Hermes VPS Shared-Knowledge MCP Repair

Status: repaired and loaded in the running VPS Gateway — 2026-09-06

## Root cause

The canonical SQLite database was healthy, but the MCP child could not be
started by the `ai-admin` Hermes Gateway. The runtime log showed:

```text
can't open file .../shared_knowledge_bridge.py: [Errno 13] Permission denied
```

The bridge had been owned by `root:root` with mode `0700`. A direct root test
therefore obscured the real service failure.

The bridge also imported the removed `MCPServer` symbol. The installed VPS MCP
SDK exposes `FastMCP`.

## Repair performed

1. Preserved the pre-change bridge backup on the VPS.
2. Replaced the obsolete import/registration path with the installed
   `mcp.server.fastmcp.FastMCP` API and `run(transport="stdio")`.
3. Set the exact runtime file to `ai-admin:ai-admin`, mode `0750`.
4. Added the legacy MCP protocol mode to the VPS Hermes server entry.
5. Restarted `hermes-gateway.service`.

## Current proof

```text
hermes-gateway.service      = active
MCP child                   = running as ai-admin
Bridge owner/mode           = ai-admin:ai-admin / 750
Bridge SHA-256              = abf3139a05b377066096251053d9f2942dc612ebb4e664d9785580f032654a9e
SQLite status               = PASS, redacted counts returned
MCP initialize              = PASS
MCP tools/list              = PASS
Gateway tools/list log      = PASS
```

The canonical database remains:

```text
/home/ai-admin/knowledge/claude_codex_hermes_knowledge.db
```

No secret values were read or persisted. The separate short-lived CLI probe
still has a shorter timeout than the Gateway; the authoritative readiness
evidence is the live Gateway child process plus its `tools/list` event.
