#!/usr/bin/env python3
"""Durable, append-only execution state for Codex, Hermes and adapters.

The ledger deliberately stores task state separately from ``shared_kb``.  It
is SQLite-backed so the canonical VPS copy can be backed up and recovered with
the existing Hermes control-plane workflow, while local and test instances can
use the same transport-neutral contract.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Iterator, Mapping

# Allow this module to run as a direct CLI from the ``tools`` directory on the
# VPS while resolving the repository's ``tools`` package consistently.
_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from tools.task_envelope import TaskEnvelope


ACTIVE_STATES = {
    "queued", "claimed", "prechecked", "executing", "verifying", "repairing",
    "retrying", "reconfiguring", "redeploying",
}
TERMINAL_STATES = {"succeeded", "rolled_back", "failed", "blocked_waiting_owner"}
VALID_STATES = ACTIVE_STATES | TERMINAL_STATES
SENSITIVE_KEY_PARTS = ("secret", "token", "password", "api_key", "apikey", "authorization")


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_path() -> Path:
    home = os.environ.get("HERMES_HOME")
    if home:
        return Path(home) / "state" / "execution-ledger.sqlite3"
    return Path.home() / ".hermes" / "state" / "execution-ledger.sqlite3"


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _safe(value: Any) -> Any:
    """Redact secret-shaped mapping values before durable evidence is written."""
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if any(part in str(key).lower() for part in SENSITIVE_KEY_PARTS)
            else _safe(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_safe(item) for item in value]
    return value


def _parse_json(value: str | Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    parsed = json.loads(value)
    if not isinstance(parsed, Mapping):
        raise ValueError("expected a JSON object")
    return dict(parsed)


class ExecutionLedger:
    """SQLite ledger with transactional claims and append-only run events."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path or os.environ.get("HERMES_EXECUTION_LEDGER") or _default_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA foreign_keys=ON")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    project TEXT NOT NULL DEFAULT '',
                    target TEXT NOT NULL DEFAULT '',
                    objective TEXT NOT NULL DEFAULT '',
                    generation INTEGER NOT NULL DEFAULT 1,
                    idempotency_key TEXT NOT NULL UNIQUE,
                    state TEXT NOT NULL,
                    assigned_to TEXT NOT NULL DEFAULT '',
                    lease_expires_at TEXT NOT NULL DEFAULT '',
                    envelope_json TEXT NOT NULL,
                    verification_json TEXT NOT NULL DEFAULT '{}',
                    recovery_json TEXT NOT NULL DEFAULT '[]',
                    rollback_ref TEXT NOT NULL DEFAULT '',
                    handover_checksum TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS run_events (
                    event_seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    event_type TEXT NOT NULL,
                    state TEXT NOT NULL,
                    actor TEXT NOT NULL DEFAULT '',
                    payload_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS run_events_run_created_idx
                    ON run_events(run_id, created_at);
                CREATE TABLE IF NOT EXISTS capabilities (
                    capability_id TEXT PRIMARY KEY,
                    capability_type TEXT NOT NULL,
                    state TEXT NOT NULL,
                    authentication_state TEXT NOT NULL DEFAULT '',
                    risk TEXT NOT NULL DEFAULT '',
                    evidence_json TEXT NOT NULL DEFAULT '{}',
                    recovery_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS handovers (
                    block_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    persisted_at TEXT NOT NULL,
                    verified_by TEXT NOT NULL DEFAULT '',
                    verified_at TEXT NOT NULL DEFAULT ''
                );
                """
            )

    def _event(
        self, connection: sqlite3.Connection, run_id: str, event_type: str,
        state: str, actor: str = "", payload: Mapping[str, Any] | None = None,
    ) -> None:
        connection.execute(
            """INSERT INTO run_events(event_id,run_id,event_type,state,actor,payload_json,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (f"evt-{uuid.uuid4().hex}", run_id, event_type, state, actor, _json(_safe(payload or {})), _utc_now()),
        )

    @staticmethod
    def _run_from_row(row: sqlite3.Row, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        result = dict(row)
        for name in ("envelope_json", "verification_json", "recovery_json"):
            result[name.removesuffix("_json")] = json.loads(result.pop(name))
        if events is not None:
            result["events"] = events
        return result

    def create_run(self, envelope: Mapping[str, Any] | TaskEnvelope, *, actor: str = "codex") -> dict[str, Any]:
        raw_envelope = envelope.to_dict() if isinstance(envelope, TaskEnvelope) else dict(envelope)
        task = TaskEnvelope.from_mapping(raw_envelope)
        # Keep v2 fields even while an older TaskEnvelope implementation exists
        # on a staged remote runtime. The ledger is the compatibility boundary.
        data = _safe({**task.to_dict(), **raw_envelope})
        run_id = str(raw_envelope.get("run_id") or task.run_id)
        task_id = str(raw_envelope.get("task_id") or task.task_id)
        generation = max(1, int(raw_envelope.get("generation") or getattr(task, "generation", 1)))
        idempotency_seed = {
            "task_id": task_id,
            "generation": generation,
            "objective": raw_envelope.get("objective") or task.objective,
        }
        idempotency_key = str(
            raw_envelope.get("idempotency_key")
            or getattr(task, "idempotency_key", "")
            or f"idem-{hashlib.sha256(_json(idempotency_seed).encode('utf-8')).hexdigest()[:20]}"
        )
        project = str(raw_envelope.get("project") or task.project)
        target = str(raw_envelope.get("target") or getattr(task, "target", ""))
        objective = str(raw_envelope.get("objective") or task.objective)
        assigned_to = str(raw_envelope.get("assigned_to") or task.assigned_to)
        verification = raw_envelope.get("verification") or getattr(task, "verification", {})
        recovery_history = raw_envelope.get("recovery_history") or getattr(task, "recovery_history", ())
        rollback_ref = str(raw_envelope.get("rollback_ref") or getattr(task, "rollback_ref", ""))
        handover_checksum = str(raw_envelope.get("handover_checksum") or getattr(task, "handover_checksum", ""))
        state = str(raw_envelope.get("execution_state") or task.execution_state)
        state = state if state in VALID_STATES else "queued"
        if state == "received":
            state = "queued"
        now = _utc_now()
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM runs WHERE idempotency_key=?", (idempotency_key,)
            ).fetchone()
            if existing:
                connection.execute("COMMIT")
                return {"created": False, "run": self._run_from_row(existing)}
            connection.execute(
                """INSERT INTO runs(run_id,task_id,project,target,objective,generation,idempotency_key,state,
                   assigned_to,lease_expires_at,envelope_json,verification_json,recovery_json,rollback_ref,
                   handover_checksum,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    run_id, task_id, project, target, objective, generation, idempotency_key, state,
                    assigned_to if assigned_to != "hermes" else "", "", _json(data),
                    _json(_safe(verification)), _json(_safe(recovery_history)), rollback_ref,
                    handover_checksum, now, now,
                ),
            )
            self._event(connection, run_id, "run_created", state, actor, {"task_id": task_id})
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            connection.execute("COMMIT")
            return {"created": True, "run": self._run_from_row(row)}

    def claim_run(self, run_id: str, executor: str, *, lease_seconds: int = 900) -> dict[str, Any]:
        if not executor.strip():
            raise ValueError("executor is required")
        lease_seconds = max(30, min(int(lease_seconds), 86_400))
        now = datetime.now(UTC)
        lease_until = (now + timedelta(seconds=lease_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                connection.execute("ROLLBACK")
                raise KeyError(run_id)
            current = self._run_from_row(row)
            if current["state"] in TERMINAL_STATES:
                connection.execute("COMMIT")
                return {"claimed": False, "reason": "terminal", "run": current}
            current_lease = current["lease_expires_at"]
            lease_live = bool(current_lease and current_lease > now.replace(microsecond=0).isoformat().replace("+00:00", "Z"))
            if current["assigned_to"] and current["assigned_to"] != executor and lease_live:
                connection.execute("COMMIT")
                return {"claimed": False, "reason": "leased", "run": current}
            connection.execute(
                "UPDATE runs SET assigned_to=?, lease_expires_at=?, state='claimed', updated_at=? WHERE run_id=?",
                (executor, lease_until, _utc_now(), run_id),
            )
            self._event(connection, run_id, "run_claimed", "claimed", executor, {"lease_seconds": lease_seconds})
            claimed = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            connection.execute("COMMIT")
            return {"claimed": True, "run": self._run_from_row(claimed)}

    def transition_run(
        self, run_id: str, state: str, *, actor: str, payload: Mapping[str, Any] | None = None,
        verification: Mapping[str, Any] | None = None, rollback_ref: str | None = None,
    ) -> dict[str, Any]:
        if state not in VALID_STATES:
            raise ValueError(f"unsupported state: {state}")
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                connection.execute("ROLLBACK")
                raise KeyError(run_id)
            current = self._run_from_row(row)
            if current["state"] in TERMINAL_STATES and state not in {"repairing", "retrying"}:
                connection.execute("ROLLBACK")
                raise ValueError(f"terminal run cannot transition from {current['state']} to {state}")
            recovery = list(current["recovery"])
            if state in {"repairing", "retrying", "reconfiguring", "redeploying", "rolled_back"}:
                recovery.append({"state": state, "actor": actor, "at": _utc_now(), "detail": _safe(payload or {})})
            next_verification = _safe(verification if verification is not None else current["verification"])
            next_rollback = rollback_ref if rollback_ref is not None else current["rollback_ref"]
            connection.execute(
                """UPDATE runs SET state=?, verification_json=?, recovery_json=?, rollback_ref=?,
                   updated_at=? WHERE run_id=?""",
                (state, _json(next_verification), _json(recovery), next_rollback, _utc_now(), run_id),
            )
            self._event(connection, run_id, "state_transition", state, actor, payload)
            updated = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            connection.execute("COMMIT")
            return self._run_from_row(updated)

    def read_run(self, run_id: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
            if not row:
                raise KeyError(run_id)
            event_rows = connection.execute(
                "SELECT * FROM run_events WHERE run_id=? ORDER BY event_seq", (run_id,)
            ).fetchall()
            events = []
            for event in event_rows:
                item = dict(event)
                item["payload"] = json.loads(item.pop("payload_json"))
                events.append(item)
            return self._run_from_row(row, events)

    def list_runs(self, *, limit: int = 50) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [self._run_from_row(row) for row in rows]

    def register_capability(self, capability: Mapping[str, Any], *, actor: str = "codex") -> dict[str, Any]:
        capability_id = str(capability.get("capability_id") or capability.get("name") or "").strip()
        if not capability_id:
            raise ValueError("capability_id or name is required")
        now = _utc_now()
        data = _safe(capability)
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO capabilities(capability_id,capability_type,state,authentication_state,risk,
                   evidence_json,recovery_json,created_at,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(capability_id) DO UPDATE SET capability_type=excluded.capability_type,
                   state=excluded.state, authentication_state=excluded.authentication_state, risk=excluded.risk,
                   evidence_json=excluded.evidence_json, recovery_json=excluded.recovery_json,
                   updated_at=excluded.updated_at""",
                (
                    capability_id, str(data.get("capability_type") or "tool"), str(data.get("state") or "verified"),
                    str(data.get("authentication_state") or ""), str(data.get("risk") or ""),
                    _json(data.get("evidence") or {}), _json(data.get("recovery") or {}), now, now,
                ),
            )
            row = connection.execute("SELECT * FROM capabilities WHERE capability_id=?", (capability_id,)).fetchone()
            result = dict(row)
            result["evidence"] = json.loads(result.pop("evidence_json"))
            result["recovery"] = json.loads(result.pop("recovery_json"))
            result["registered_by"] = actor
            return result

    def record_handover(self, block_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        clean = _safe(payload)
        checksum = hashlib.sha256(_json(clean).encode("utf-8")).hexdigest()
        now = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO handovers(block_id,payload_json,checksum,persisted_at)
                   VALUES(?,?,?,?)
                   ON CONFLICT(block_id) DO UPDATE SET payload_json=excluded.payload_json,
                   checksum=excluded.checksum,persisted_at=excluded.persisted_at,verified_by='',verified_at=''""",
                (block_id, _json(clean), checksum, now),
            )
        return {"block_id": block_id, "checksum": checksum, "persisted_at": now}

    def verify_handover(self, block_id: str, checksum: str, *, verifier: str) -> dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM handovers WHERE block_id=?", (block_id,)).fetchone()
            if not row:
                raise KeyError(block_id)
            matched = row["checksum"] == checksum
            now = _utc_now()
            if matched:
                connection.execute(
                    "UPDATE handovers SET verified_by=?,verified_at=? WHERE block_id=?",
                    (verifier, now, block_id),
                )
            return {"block_id": block_id, "matched": matched, "checksum": row["checksum"], "verified_at": now if matched else ""}

    def backup(self, destination: str | os.PathLike[str]) -> dict[str, Any]:
        target = Path(destination)
        target.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as source:
            destination_connection = sqlite3.connect(target)
            try:
                source.backup(destination_connection)
                destination_connection.commit()
            finally:
                destination_connection.close()
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        return {"path": str(target), "sha256": digest, "bytes": target.stat().st_size}


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Hermes execution ledger CLI")
    parser.add_argument("action", choices=("create", "claim", "transition", "read", "list", "capability", "handover", "verify-handover", "backup"))
    parser.add_argument("--db", default="")
    parser.add_argument("--json", default="{}")
    parser.add_argument("--stdin", action="store_true")
    args = parser.parse_args()
    raw = sys.stdin.read() if args.stdin else args.json
    data = _parse_json(raw)
    ledger = ExecutionLedger(args.db or None)
    if args.action == "create":
        result = ledger.create_run(data.get("envelope") or data, actor=str(data.get("actor") or "codex"))
    elif args.action == "claim":
        result = ledger.claim_run(str(data["run_id"]), str(data["executor"]), lease_seconds=int(data.get("lease_seconds") or 900))
    elif args.action == "transition":
        result = ledger.transition_run(str(data["run_id"]), str(data["state"]), actor=str(data.get("actor") or "executor"), payload=data.get("payload") or {}, verification=data.get("verification"), rollback_ref=data.get("rollback_ref"))
    elif args.action == "read":
        result = ledger.read_run(str(data["run_id"]))
    elif args.action == "list":
        result = ledger.list_runs(limit=int(data.get("limit") or 50))
    elif args.action == "capability":
        result = ledger.register_capability(data.get("capability") or data, actor=str(data.get("actor") or "codex"))
    elif args.action == "handover":
        result = ledger.record_handover(str(data["block_id"]), data.get("payload") or {})
    elif args.action == "verify-handover":
        result = ledger.verify_handover(str(data["block_id"]), str(data["checksum"]), verifier=str(data.get("verifier") or "executor"))
    else:
        result = ledger.backup(str(data["destination"]))
    print(_json(_safe(result)))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
