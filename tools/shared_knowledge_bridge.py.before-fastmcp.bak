#!/usr/bin/env python3
"""CLI and stdio MCP server for the canonical Hermes knowledge bridge."""
from __future__ import annotations
import argparse, json, sys
from shared_knowledge.bridge import KnowledgeBridge

def build_server():
    from mcp.server import MCPServer
    server = MCPServer(
        "hermes-shared-knowledge",
        instructions=("Canonical redacted Hermes/OpenClaw knowledge bridge. "
                      "Use preflight before operational work and writeback after it. "
                      "Never persist secrets or business-row values."),
    )
    bridge = KnowledgeBridge()
    def knowledge_status(): return bridge.status()
    def knowledge_preflight(request_json: str = "{}"): return bridge.preflight(json.loads(request_json))
    def knowledge_writeback(payload_json: str = "{}"): return bridge.writeback(json.loads(payload_json))
    def knowledge_register_source(source_json: str = "{}"): return bridge.register_source(json.loads(source_json))
    for handler, name, description in (
        (knowledge_status, "knowledge_status", "Return canonical knowledge bridge status."),
        (knowledge_preflight, "knowledge_preflight", "Retrieve namespace-scoped context before a task."),
        (knowledge_writeback, "knowledge_writeback", "Archive a redacted session and write a task result."),
        (knowledge_register_source, "knowledge_register_source", "Register a redacted source with provenance."),
    ):
        try: server.add_tool(handler, name=name, description=description)
        except TypeError: server.tool(name=name, description=description)(handler)
    return server

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("action", nargs="?", choices=("status", "preflight", "writeback", "source", "mcp"), default="mcp")
    p.add_argument("--json", default="{}")
    p.add_argument("--stdin", action="store_true", help="Read JSON payload from stdin")
    args = p.parse_args()
    if args.action == "mcp":
        build_server().run()
        return 0
    bridge = KnowledgeBridge()
    if args.stdin:
        args.json = sys.stdin.read()
    if args.action == "status": out = bridge.status()
    elif args.action == "preflight": out = bridge.preflight(json.loads(args.json))
    elif args.action == "writeback": out = bridge.writeback(json.loads(args.json))
    else: out = bridge.register_source(json.loads(args.json))
    print(json.dumps(out, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
