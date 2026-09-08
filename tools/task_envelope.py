"""Shared task identity and provenance envelope.

The envelope is deliberately transport-neutral: Hermes, Codex, n8n and
OpenClaw can serialize the same shape without sharing runtime state.  It is
used by the knowledge bridge as the durable join key for a request, its
delegations, and the resulting evidence.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Mapping


def _stable_id(prefix: str, value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode()
    return f"{prefix}-{hashlib.sha256(raw).hexdigest()[:20]}"


@dataclass(frozen=True)
class TaskEnvelope:
    """Canonical identity carried across agent and tool boundaries."""

    task_id: str
    parent_task_id: str = ""
    session_id: str = ""
    run_id: str = ""
    requested_by: str = "owner"
    assigned_to: str = "hermes"
    channel: str = ""
    project: str = ""
    system_scope: str = "system"
    privacy_scope: str = "system"
    objective: str = ""
    context_refs: tuple[str, ...] = field(default_factory=tuple)
    required_tools: tuple[str, ...] = field(default_factory=tuple)
    execution_state: str = "received"
    result_refs: tuple[str, ...] = field(default_factory=tuple)
    provenance: Mapping[str, Any] = field(default_factory=dict)
    schema_version: int = 2
    generation: int = 1
    idempotency_key: str = ""
    target: str = ""
    capability_scope: tuple[str, ...] = field(default_factory=tuple)
    executor_history: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    deployment_refs: tuple[str, ...] = field(default_factory=tuple)
    verification: Mapping[str, Any] = field(default_factory=dict)
    recovery_history: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    rollback_ref: str = ""
    handover_checksum: str = ""

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "TaskEnvelope":
        data = dict(value or {})
        task_id = str(data.get("task_id") or data.get("session_id") or _stable_id("task", data))
        run_id = str(data.get("run_id") or _stable_id("run", {"task_id": task_id, "objective": data.get("objective", "")}))
        def _tuple(name: str) -> tuple[str, ...]:
            raw = data.get(name, ())
            if isinstance(raw, str):
                return (raw,) if raw else ()
            return tuple(str(item) for item in raw if item)
        provenance = data.get("provenance") or {}
        if not isinstance(provenance, Mapping):
            provenance = {"value": str(provenance)}
        verification = data.get("verification") or {}
        if not isinstance(verification, Mapping):
            verification = {"value": str(verification)}
        recovery_raw = data.get("recovery_history") or ()
        if isinstance(recovery_raw, Mapping):
            recovery_raw = (recovery_raw,)
        recovery_history = tuple(
            dict(item) if isinstance(item, Mapping) else {"value": str(item)}
            for item in recovery_raw
        )
        generation = max(1, int(data.get("generation") or 1))
        idempotency_key = str(data.get("idempotency_key") or _stable_id("idem", {
            "task_id": task_id,
            "generation": generation,
            "objective": data.get("objective") or "",
        }))
        return cls(
            task_id=task_id,
            parent_task_id=str(data.get("parent_task_id") or ""),
            session_id=str(data.get("session_id") or ""),
            run_id=run_id,
            requested_by=str(data.get("requested_by") or "owner"),
            assigned_to=str(data.get("assigned_to") or "hermes"),
            channel=str(data.get("channel") or ""),
            project=str(data.get("project") or ""),
            system_scope=str(data.get("system_scope") or data.get("system") or "system"),
            privacy_scope=str(data.get("privacy_scope") or "system"),
            objective=str(data.get("objective") or ""),
            context_refs=_tuple("context_refs"),
            required_tools=_tuple("required_tools"),
            execution_state=str(data.get("execution_state") or "received"),
            result_refs=_tuple("result_refs"),
            provenance=dict(provenance),
            schema_version=max(2, int(data.get("schema_version") or 2)),
            generation=generation,
            idempotency_key=idempotency_key,
            target=str(data.get("target") or ""),
            capability_scope=_tuple("capability_scope"),
            executor_history=_tuple("executor_history"),
            evidence_refs=_tuple("evidence_refs"),
            deployment_refs=_tuple("deployment_refs"),
            verification=dict(verification),
            recovery_history=recovery_history,
            rollback_ref=str(data.get("rollback_ref") or ""),
            handover_checksum=str(data.get("handover_checksum") or ""),
        )

    @classmethod
    def new(cls, **kwargs: Any) -> "TaskEnvelope":
        kwargs.setdefault("task_id", f"task-{uuid.uuid4().hex[:20]}")
        kwargs.setdefault("run_id", f"run-{uuid.uuid4().hex[:20]}")
        return cls.from_mapping(kwargs)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        for key in (
            "context_refs", "required_tools", "result_refs", "capability_scope",
            "executor_history", "evidence_refs", "deployment_refs",
        ):
            result[key] = list(result[key])
        result["recovery_history"] = [dict(item) for item in result["recovery_history"]]
        return result


__all__ = ["TaskEnvelope"]
