"""Shared canonical KnowledgeProvider for Hermes/OpenClaw sessions."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from agent.memory_provider import MemoryProvider
from tools.shared_knowledge.bridge import KnowledgeBridge
from tools.task_envelope import TaskEnvelope


class SharedKnowledgeProvider(MemoryProvider):
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.bridge: KnowledgeBridge | None = None
        self.session_id = ""
        self.platform = ""
        self.context: Dict[str, Any] = {}

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
        if not path:
            try:
                from hermes_cli.config import load_config
                memory = load_config().get("memory", {})
                provider_config = memory.get("shared_kb", {}) if isinstance(memory, dict) else {}
                path = provider_config.get("db_path") if isinstance(provider_config, dict) else None
            except Exception:
                path = None
        self.bridge = KnowledgeBridge(path)

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
        result = self.bridge.preflight({
            **envelope.to_dict(),
            "task_id": session_id or self.session_id,
            "session_id": session_id or self.session_id,
            "channel": self.platform,
            "agent_id": "hermes",
            "objective": query,
            "requested_scope": query,
            "privacy_scope": "system",
        })
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
        self.bridge.writeback({
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
        self.bridge.writeback({
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
        self.bridge.writeback({
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
            return json.dumps(self.bridge.preflight({"task_id": self.session_id, "session_id": self.session_id, "channel": self.platform, "agent_id": "hermes", "objective": args.get("objective", ""), "requested_scope": args.get("objective", ""), "privacy_scope": args.get("privacy_scope", "system")}), ensure_ascii=False)
        if tool_name == "shared_knowledge_writeback":
            return json.dumps(self.bridge.writeback({"task_id": self.session_id, "session_id": self.session_id, "channel": self.platform, "agent_id": "hermes", "privacy_scope": "system", "objective": args.get("objective", ""), "requirement": {"objective": args.get("objective", ""), "status": args.get("status", "draft")}, "result": {"summary": args.get("summary", ""), "status": args.get("status", "draft")}}), ensure_ascii=False)
        return json.dumps({"status": "FAIL", "error": "unknown_tool"})

    def shutdown(self) -> None:
        self.bridge = None


def register(ctx) -> None:
    ctx.register_memory_provider(SharedKnowledgeProvider())
