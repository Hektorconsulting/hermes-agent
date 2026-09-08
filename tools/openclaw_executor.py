#!/usr/bin/env python3
"""Authenticated, non-delivery OpenClaw executor for TaskEnvelope runs.

It is intentionally a native CLI adapter instead of an HTTP imitation: the
running OpenClaw gateway owns authentication and execution.  Task text travels
through a mode-0600 temporary file, never command-line arguments or ledger
events.  The ledger receives a compact, hash-based execution result.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

try:
    from tools.execution_ledger import ExecutionLedger
except ModuleNotFoundError:  # Direct VPS script execution.
    from execution_ledger import ExecutionLedger


OPENCLAW_CONFIG = Path(os.environ.get("OPENCLAW_CONFIG", "/home/ai-admin/.openclaw/openclaw.json"))
OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "/usr/bin/openclaw")
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _require_safe_id(value: str, field: str) -> str:
    result = str(value or "").strip()
    if not SAFE_ID.fullmatch(result):
        raise ValueError(f"{field} must be a bounded safe identifier")
    return result


def _gateway_token(config_path: Path = OPENCLAW_CONFIG) -> str:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    token = ((data.get("gateway") or {}).get("auth") or {}).get("token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("OpenClaw gateway token is unavailable through its private configuration")
    return token


def _result_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    encoded = json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "openclaw_run_id": str(payload.get("runId") or ""),
        "status": str(payload.get("status") or ""),
        "has_error": bool(payload.get("error")),
        "result_sha256": hashlib.sha256(encoded).hexdigest(),
        "timeout_phase": str(payload.get("timeoutPhase") or ""),
    }


class OpenClawExecutor:
    def __init__(self, *, config_path: Path = OPENCLAW_CONFIG, executable: str = OPENCLAW_BIN, ledger: ExecutionLedger | None = None) -> None:
        self.config_path = config_path
        self.executable = executable
        self.ledger = ledger or ExecutionLedger()

    def execute(self, *, run_id: str, message: str, agent: str = "main", timeout_seconds: int = 120) -> dict[str, Any]:
        run_id = _require_safe_id(run_id, "run_id")
        agent = _require_safe_id(agent, "agent")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("message is required")
        timeout_seconds = max(15, min(int(timeout_seconds), 900))
        # The OpenClaw CLI resolves this private credential from its own config;
        # validate that the authenticated gateway route exists without exposing
        # or injecting the credential into a command line or child environment.
        _gateway_token(self.config_path)
        session_key = f"agent:{agent}:{run_id}"
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, prefix="openclaw-task-", suffix=".txt") as handle:
                handle.write(message)
                temp_path = Path(handle.name)
            os.chmod(temp_path, 0o600)
            command = [
                self.executable, "agent", "--agent", agent, "--session-key", session_key,
                "--message-file", str(temp_path), "--json", "--timeout", str(timeout_seconds),
            ]
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds + 30, check=False)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)
        if result.returncode != 0:
            raise RuntimeError(f"OpenClaw executor failed with exit code {result.returncode}")
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError("OpenClaw executor returned non-JSON output") from exc
        if not isinstance(payload, Mapping) or payload.get("error"):
            raise RuntimeError("OpenClaw executor returned an execution error")
        summary = _result_summary(payload)
        self.ledger.transition_run(run_id, "verifying", actor="openclaw", payload={"executor": "openclaw", **summary})
        self.ledger.transition_run(run_id, "succeeded", actor="openclaw", verification={"executor": "openclaw", **summary})
        return summary


def _cli() -> int:
    request = json.loads(sys.stdin.read() or "{}")
    summary = OpenClawExecutor().execute(
        run_id=str(request.get("run_id") or ""),
        message=str(request.get("message") or ""),
        agent=str(request.get("agent") or "main"),
        timeout_seconds=int(request.get("timeout_seconds") or 120),
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
