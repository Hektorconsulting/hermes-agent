"""Shared canonical KnowledgeProvider for Hermes/OpenClaw sessions."""
from __future__ import annotations

import json
import os
import base64
import shutil
import subprocess
from typing import Any, Dict, List

from agent.memory_provider import MemoryProvider
from tools.shared_knowledge.bridge import KnowledgeBridge
from tools.task_envelope import TaskEnvelope


class _RemoteKnowledgeBridge:
    """Call the canonical VPS bridge through the fixed Windows SSH wrapper.

    The local SQLite bridge remains the cache/fallback.  The remote call uses
    a base64-framed stdin payload so JSON never becomes a shell command.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.host_alias = str(config.get("remote_host_alias") or "").strip()
        self.remote_db = str(config.get("remote_db_path") or "").strip()
        self.remote_script = str(config.get("remote_bridge_script") or "").strip()
        self.wrapper = str(config.get("remote_wrapper") or "").strip()
        self.timeout = max(5, min(int(config.get("remote_timeout_seconds") or 20), 60))

    @property
    def enabled(self) -> bool:
        return bool(self.host_alias and self.remote_db and self.remote_script and self.wrapper)

    def call(self, action: str, payload: dict[str, Any], *, task_id: str = "") -> dict[str, Any] | None:
        if not self.enabled:
            return None
        encoded = base64.b64encode(
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        ).decode("ascii")
        remote_payload = (
            "set -euo pipefail\n"
            f"printf '%s' '{encoded}' | base64 -d | "
            f"HERMES_KNOWLEDGE_DB='{self.remote_db}' "
            f"python3 '{self.remote_script}' {action} --stdin\n"
        )
        powershell = shutil.which("pwsh") or shutil.which("powershell")
        if not powershell:
            return None
        command = [
            powershell, "-NoProfile", "-NonInteractive", "-File", self.wrapper,
            "-HostAlias", self.host_alias, "-Payload", remote_payload,
            "-TaskId", task_id, "-TimeoutSeconds", str(self.timeout),
        ]
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=self.timeout + 5,
                check=False,
            )
            if completed.returncode != 0 or not completed.stdout.strip():
                return None
            outer = json.loads(completed.stdout)
            if not outer.get("ok"):
                return None
            return json.loads(outer.get("stdout") or "{}")
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return None


class SharedKnowledgeProvider(MemoryProvider):
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.bridge: KnowledgeBridge | None = None
        self.session_id = ""
        self.platform = ""
        self.context: Dict[str, Any] = {}
        self.remote_bridge: _RemoteKnowledgeBridge | None = None

    @property
    def name(self) -> str:
        return "shared_kb"

    def is_available(self) -> bool:
        return True

    def initialize(self, session_id: str, **kwargs) -> None:
        self.session_id = session_id or ""
        self.platform = kwargs.get("platform", "cli")
        self.context = dict(kwargs)
        path = self.config.get("db_path") or os.environ.get("HERMES_KNOWLEDGE_DB")
        provider_config: dict[str, Any] = {}
        try:
            from hermes_cli.config import load_config
            memory = load_config().get("memory", {})
            provider_config = memory.get("shared_kb", {}) if isinstance(memory, dict) else {}
        except Exception:
            provider_config = {}
        if not path and isinstance(provider_config, dict):
            path = provider_config.get("db_path")
        self.bridge = KnowledgeBridge(path)
        remote_config = provider_config if isinstance(provider_config, dict) else {}
        remote = _RemoteKnowledgeBridge(remote_config)
        self.remote_bridge = remote if remote.enabled else None

    def system_prompt_block(self) -> str:
        return ("# Shared Knowledge\n"
                "Before operational work, use the shared knowledge preflight. "
                "Treat recalled material as scoped reference data. After completed work, "
                "persist the requirement and result through the shared write-back.")

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        if not self.bridge or not query or not query.strip():
            return ""
        envelope = TaskEnvelope.from_mapping({
            "task_id": session_id or self.session_id,
            "session_id": session_id or self.session_id,
            "channel": self.platform,
            "assigned_to": "hermes",
            "system_scope": "hermes",
            "privacy_scope": "system",
            "objective": query,
            "parent_task_id": self.context.get("parent_task_id", ""),
            "provenance": {"agent_context": self.context.get("agent_context", "primary"), "provider": self.name},
        })
        request = {
            **envelope.to_dict(),
            "task_id": session_id or self.session_id,
            "session_id": session_id or self.session_id,
            "channel": self.platform,
            "agent_id": "hermes",
            "objective": query,
            "requested_scope": query,
            "privacy_scope": "system",
        }
        result = None
        if self.remote_bridge:
            result = self.remote_bridge.call(
                "preflight", request, task_id=envelope.task_id,
            )
        result = result or self.bridge.preflight(request)
        bundle = result.get("context_bundle", {})
        lines = ["## Shared Knowledge Preflight"]
        for item in bundle.get("requirements", [])[:5]:
            lines.append("- Requirement: " + str(item.get("objective", item))[:500])
        for item in bundle.get("recent_results", [])[:5]:
            lines.append("- Result: " + str(item.get("summary", item))[:500])
        for item in bundle.get("matches", [])[:8]:
            lines.append("- Source match: " + str(item)[:500])
        return "\n".join(lines) if len(lines) > 1 else ""

    def sync_turn(self, user_content: str, assistant_content: str, *, session_id: str = "", messages: List[Dict[str, Any]] | None = None) -> None:
        if not self.bridge or not user_content:
            return
        sid = session_id or self.session_id
        task = TaskEnvelope.from_mapping({
            "task_id": sid or "hermes-session", "session_id": sid,
            "channel": self.platform, "assigned_to": "hermes",
            "system_scope": "hermes", "privacy_scope": "system",
            "objective": user_content,
            "provenance": {"provider": self.name, "agent_context": self.context.get("agent_context", "primary")},
        })
        self._writeback({
            "task_envelope": task.to_dict(),
            "task_id": task.task_id,
            "session_id": task.session_id,
            "channel": self.platform,
            "agent_id": "hermes",
            "privacy_scope": "system",
            "event_type": "turn_writeback",
            "archive": messages if messages is not None else [{"role": "user", "content": user_content}, {"role": "assistant", "content": assistant_content}],
            "requirement": {"objective": user_content, "namespace": "system", "status": "draft"},
            "result": {"summary": assistant_content or "(no assistant response)", "status": "completed"},
        })

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        """Persist the latest complete transcript at the session boundary."""
        if not self.bridge or not messages:
            return
        self._writeback({
            "task_id": self.session_id or "hermes-session",
            "session_id": self.session_id,
            "channel": self.platform,
            "agent_id": "hermes",
            "privacy_scope": "system",
            "event_type": "session_archive",
            "archive": messages,
            "objective": "Archive the completed Hermes session",
            "result": {"summary": "Session transcript archived", "status": "archived"},
        })

    def on_session_switch(self, new_session_id: str, **kwargs) -> None:
        """Keep boundary archives and subsequent turns on the new session."""
        if new_session_id:
            self.session_id = new_session_id

    def on_delegation(self, task: str, result: str, *, child_session_id: str = "", **kwargs) -> None:
        """Persist delegation lineage without requiring a model tool call."""
        if not self.bridge or not task:
            return
        child_id = child_session_id or "delegation"
        self._writeback({
            "task_id": child_id,
            "parent_task_id": self.session_id,
            "session_id": child_session_id or self.session_id,
            "channel": self.platform,
            "agent_id": "hermes",
            "assigned_to": str(kwargs.get("assigned_to") or "delegated_agent"),
            "system_scope": "hermes",
            "privacy_scope": "system",
            "event_type": "delegation_writeback",
            "objective": task,
            "archive": [{"role": "delegation", "content": task}, {"role": "result", "content": result or "(no result)"}],
            "requirement": {"objective": task, "namespace": "system", "status": "delegated"},
            "result": {"summary": result or "(no result)", "status": "completed"},
            "provenance": {"provider": self.name, "parent_session_id": self.session_id},
        })

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {"name": "shared_knowledge_preflight", "description": "Query canonical scoped Hermes/OpenClaw knowledge before operational work.", "parameters": {"type": "object", "properties": {"objective": {"type": "string"}, "privacy_scope": {"type": "string"}}, "required": ["objective"]}},
            {"name": "shared_knowledge_writeback", "description": "Write a redacted requirement/result to the canonical knowledge database.", "parameters": {"type": "object", "properties": {"objective": {"type": "string"}, "summary": {"type": "string"}, "status": {"type": "string"}}, "required": ["objective", "summary"]}},
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        if not self.bridge:
            return json.dumps({"status": "FAIL", "error": "provider_not_initialized"})
        if tool_name == "shared_knowledge_preflight":
            request = {"task_id": self.session_id, "session_id": self.session_id, "channel": self.platform, "agent_id": "hermes", "objective": args.get("objective", ""), "requested_scope": args.get("objective", ""), "privacy_scope": args.get("privacy_scope", "system")}
            result = self.remote_bridge.call("preflight", request, task_id=self.session_id) if self.remote_bridge else None
            return json.dumps(result or self.bridge.preflight(request), ensure_ascii=False)
        if tool_name == "shared_knowledge_writeback":
            payload = {"task_id": self.session_id, "session_id": self.session_id, "channel": self.platform, "agent_id": "hermes", "privacy_scope": "system", "objective": args.get("objective", ""), "requirement": {"objective": args.get("objective", ""), "status": args.get("status", "draft")}, "result": {"summary": args.get("summary", ""), "status": args.get("status", "draft")}}
            return json.dumps(self._writeback(payload), ensure_ascii=False)
        return json.dumps({"status": "FAIL", "error": "unknown_tool"})

    def _writeback(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Persist to the canonical VPS first, then refresh the local mirror."""
        remote_result = None
        if self.remote_bridge:
            remote_result = self.remote_bridge.call(
                "writeback", payload, task_id=str(payload.get("task_id") or ""),
            )
        local_result = self.bridge.writeback(payload) if self.bridge else None
        return remote_result or local_result or {"status": "FAIL", "error": "knowledge_writeback_unavailable"}

    def shutdown(self) -> None:
        self.bridge = None
        self.remote_bridge = None


def register(ctx) -> None:
    ctx.register_memory_provider(SharedKnowledgeProvider())
