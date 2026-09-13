#!/usr/bin/env python3
"""Read-only Hermes -> OpenClaw employee bridge.

The gateway token is read locally from OpenClaw's private config and is never
returned by any tool. This bridge intentionally exposes health/readiness only;
it cannot send messages, run agents, mutate config, or restart services.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except ModuleNotFoundError:
    from mcp.server import MCPServer as FastMCP


OPENCLAW_CONFIG = Path("/home/ai-admin/.openclaw/openclaw.json")
OPENCLAW_URL = os.environ.get("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789")
OPENCLAW_BIN = "/usr/bin/openclaw"

server = FastMCP("hermes-openclaw-employee")


def _token() -> str:
    data = json.loads(OPENCLAW_CONFIG.read_text(encoding="utf-8"))
    value = data.get("gateway", {}).get("auth", {}).get("token", "")
    if not isinstance(value, str) or not value:
        raise RuntimeError("OpenClaw gateway token is not available through the configured secret source")
    return value


def _call(method: str, timeout: int = 8) -> dict[str, Any]:
    token = _token()
    result = subprocess.run(
        [
            OPENCLAW_BIN,
            "gateway",
            "call",
            method,
            "--json",
            "--token",
            token,
            "--url",
            OPENCLAW_URL,
            "--timeout",
            str(timeout * 1000),
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 3,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"OpenClaw read-only call failed: {method} (exit {result.returncode})")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenClaw returned non-JSON for read-only call: {method}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"OpenClaw returned an unexpected payload for: {method}")
    return payload


@server.tool()
def openclaw_health() -> dict[str, Any]:
    """Read the authenticated OpenClaw gateway health snapshot."""
    payload = _call("health")
    return {
        "bridge": "hermes-openclaw-employee",
        "access": "authenticated_read_only",
        "gateway_url": OPENCLAW_URL,
        "health": payload,
    }


@server.tool()
def openclaw_readiness() -> dict[str, Any]:
    """Return a compact readiness view for internal Hermes coordination."""
    payload = _call("health")
    telegram = payload.get("channels", {}).get("telegram", {})
    return {
        "bridge": "hermes-openclaw-employee",
        "access": "authenticated_read_only",
        "gateway_url": OPENCLAW_URL,
        "gateway_health": "ok" if payload.get("ok") is True else "degraded",
        "telegram": {
            "configured": telegram.get("configured"),
            "running": telegram.get("running"),
            "connected": telegram.get("connected"),
            "mode": telegram.get("mode"),
            "token_status": telegram.get("tokenStatus"),
            "last_error": telegram.get("lastError"),
        },
        "mutation_tools_exposed": False,
        "external_message_tools_exposed": False,
        "agent_execution_tools_exposed": False,
    }


if __name__ == "__main__":
    server.run(transport="stdio")
