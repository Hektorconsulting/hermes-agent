"""Private VPS transport for the canonical execution ledger.

The Codex-side MCP process uses the established fixed SSH wrapper. Payloads
are base64 framed on stdin so task material is never interpolated into a shell
command, and the remote VPS database remains the sole execution-state source.
"""
from __future__ import annotations

import base64
import json
import os
import shlex
import shutil
import subprocess
from typing import Any, Mapping


class RemoteExecutionLedger:
    def __init__(self, *, host_alias: str, wrapper: str, remote_script: str, remote_db: str, timeout: int = 30) -> None:
        self.host_alias = host_alias
        self.wrapper = wrapper
        self.remote_script = remote_script
        self.remote_db = remote_db
        self.timeout = max(10, min(int(timeout), 120))
        if not all((self.host_alias, self.wrapper, self.remote_script, self.remote_db)):
            raise ValueError("remote execution ledger configuration is incomplete")

    @classmethod
    def from_environment(cls) -> "RemoteExecutionLedger":
        return cls(
            host_alias=os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_HOST", ""),
            wrapper=os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_WRAPPER", ""),
            remote_script=os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_SCRIPT", ""),
            remote_db=os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_DB", ""),
            timeout=int(os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_TIMEOUT", "30")),
        )

    def _call(self, action: str, payload: Mapping[str, Any]) -> Any:
        if action not in {"create", "claim", "transition", "read", "list", "capability", "handover", "verify-handover", "backup"}:
            raise ValueError(f"unsupported remote ledger action: {action}")
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            raise RuntimeError("PowerShell is required for the private VPS ledger transport")
        encoded = base64.b64encode(json.dumps(dict(payload), ensure_ascii=False, separators=(",", ":")).encode("utf-8")).decode("ascii")
        remote_payload = (
            "set -euo pipefail\n"
            f"printf '%s' '{encoded}' | base64 -d | "
            f"HERMES_EXECUTION_LEDGER={shlex.quote(self.remote_db)} "
            f"python3 {shlex.quote(self.remote_script)} {action} --stdin\n"
        )
        command = [
            powershell, "-NoProfile", "-NonInteractive", "-File", self.wrapper,
            "-HostAlias", self.host_alias, "-Payload", remote_payload,
            "-TaskId", str(payload.get("run_id") or payload.get("task_id") or "control-plane"),
            "-TimeoutSeconds", str(self.timeout),
        ]
        completed = subprocess.run(
            command, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=self.timeout + 10, check=False,
        )
        if completed.returncode != 0 or not completed.stdout.strip():
            raise RuntimeError("private VPS ledger transport failed")
        wrapper_result = json.loads(completed.stdout)
        if not wrapper_result.get("ok"):
            raise RuntimeError("private VPS ledger command failed")
        return json.loads(wrapper_result.get("stdout") or "{}")

    def create_run(self, envelope: Mapping[str, Any], *, actor: str = "codex") -> dict[str, Any]:
        return self._call("create", {"envelope": dict(envelope), "actor": actor})

    def claim_run(self, run_id: str, executor: str, *, lease_seconds: int = 900) -> dict[str, Any]:
        return self._call("claim", {"run_id": run_id, "executor": executor, "lease_seconds": lease_seconds})

    def transition_run(self, run_id: str, state: str, *, actor: str, payload: Mapping[str, Any] | None = None, verification: Mapping[str, Any] | None = None, rollback_ref: str | None = None) -> dict[str, Any]:
        request: dict[str, Any] = {"run_id": run_id, "state": state, "actor": actor, "payload": dict(payload or {})}
        if verification is not None:
            request["verification"] = dict(verification)
        if rollback_ref is not None:
            request["rollback_ref"] = rollback_ref
        return self._call("transition", request)

    def read_run(self, run_id: str) -> dict[str, Any]:
        return self._call("read", {"run_id": run_id})

    def list_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        return self._call("list", {"limit": limit})

    def register_capability(self, capability: Mapping[str, Any], *, actor: str = "codex") -> dict[str, Any]:
        return self._call("capability", {"capability": dict(capability), "actor": actor})

    def record_handover(self, block_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self._call("handover", {"block_id": block_id, "payload": dict(payload)})

    def verify_handover(self, block_id: str, checksum: str, *, verifier: str) -> dict[str, Any]:
        return self._call("verify-handover", {"block_id": block_id, "checksum": checksum, "verifier": verifier})

    def backup(self, destination: str) -> dict[str, Any]:
        """Create a VPS-side SQLite backup without copying ledger data through Codex."""
        return self._call("backup", {"destination": destination})
