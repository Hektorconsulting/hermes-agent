#!/usr/bin/env python3
"""Autonomous, evidence-producing recovery for the VPS runtime services.

The watchdog deliberately has a narrow boundary: it observes the canonical
Hermes gateway and the *user-owned* OpenClaw gateway, records a redacted
result, and restarts only the unhealthy owner unit.  systemd then provides
the scheduling, isolation, and journal/audit trail.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable


STATE_PATH = Path(os.environ.get("HERMES_RUNTIME_WATCHDOG_STATE", "/home/ai-admin/.hermes/state/runtime-watchdog.jsonl"))


def _user_runtime_env() -> dict[str, str]:
    import pwd  # Unix-only; kept local so source tests remain portable.

    uid = pwd.getpwnam("ai-admin").pw_uid
    runtime_dir = f"/run/user/{uid}"
    return {
        "XDG_RUNTIME_DIR": runtime_dir,
        "DBUS_SESSION_BUS_ADDRESS": f"unix:path={runtime_dir}/bus",
    }


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False, timeout=30)


def _unit_active(unit: str, *, user_unit: bool = False) -> bool:
    command = ["systemctl", "is-active", "--quiet", unit]
    if user_unit:
        command = ["runuser", "-u", "ai-admin", "--", "env", *[f"{key}={value}" for key, value in _user_runtime_env().items()], *command[:1], "--user", *command[1:]]
    return _run(command).returncode == 0


def _listener_reachable(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=3):
            return True
    except OSError:
        return False


def _restart(unit: str, *, user_unit: bool = False) -> bool:
    command = ["systemctl", "restart", unit]
    if user_unit:
        command = ["runuser", "-u", "ai-admin", "--", "env", *[f"{key}={value}" for key, value in _user_runtime_env().items()], *command[:1], "--user", *command[1:]]
    return _run(command).returncode == 0


def _wait_until(check: Callable[[], bool], deadline_seconds: float = 25.0) -> bool:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        if check():
            return True
        time.sleep(1)
    return check()


def _append_evidence(record: dict[str, object]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    os.chmod(STATE_PATH, 0o600)


def _check_service(name: str, unit: str, check: Callable[[], bool], *, user_unit: bool = False) -> dict[str, object]:
    healthy_before = check()
    repaired = False
    if not healthy_before:
        repaired = _restart(unit, user_unit=user_unit)
    healthy_after = healthy_before or (repaired and _wait_until(check))
    return {
        "name": name,
        "unit": unit,
        "user_unit": user_unit,
        "healthy_before": healthy_before,
        "restart_attempted": not healthy_before,
        "restart_accepted": repaired,
        "healthy_after": healthy_after,
    }


def main() -> int:
    hermes = _check_service("hermes", "hermes-gateway.service", lambda: _unit_active("hermes-gateway.service"))
    openclaw = _check_service(
        "openclaw",
        "openclaw-gateway.service",
        lambda: _unit_active("openclaw-gateway.service", user_unit=True) and _listener_reachable("127.0.0.1", 18789),
        user_unit=True,
    )
    record = {
        "at": datetime.now(UTC).isoformat(),
        "schema": "runtime-watchdog-v1",
        "services": [hermes, openclaw],
        "outcome": "healthy" if hermes["healthy_after"] and openclaw["healthy_after"] else "recovery_needed",
    }
    _append_evidence(record)
    print(json.dumps(record, sort_keys=True))
    return 0 if record["outcome"] == "healthy" else 1


if __name__ == "__main__":
    sys.exit(main())
