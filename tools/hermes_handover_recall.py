#!/usr/bin/env python3
"""Deterministically reconstruct a Hermes handover from durable state.

This is the non-LLM control-plane counterpart to a fresh ``hermes chat``
session.  It uses the active Hermes shared-kb provider and its native ledger
tools, so a weaker conversational model cannot turn a cryptographic handover
test into a generic answer.  It never writes source-of-truth payloads; the
only permitted mutation is the ledger's explicit checksum-verification mark.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any


_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from plugins.memory.shared_kb import SharedKnowledgeProvider
from tools.shared_knowledge.bridge import redact


def _tool(provider: SharedKnowledgeProvider, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(provider.handle_tool_call(name, arguments))
    if result.get("status") != "PASS":
        raise RuntimeError(f"{name}: {result.get('error', 'unknown failure')}")
    return result


def recall_handover(block_id: str, run_id: str) -> dict[str, Any]:
    provider = SharedKnowledgeProvider()
    session_id = f"hermes-handover-recall-{uuid.uuid4().hex}"
    provider.initialize(session_id, platform="cli", agent_context="fresh_runtime_recall")
    try:
        # This call is deliberately retained as an independent shared_kb
        # proof.  The authoritative structured reconstruction comes from the
        # ledger, which prevents retrieval-ranking changes from changing a
        # handover checksum.
        knowledge = _tool(provider, "shared_knowledge_preflight", {"objective": block_id, "privacy_scope": "system"})
        handover = _tool(provider, "execution_ledger_read_handover", {"block_id": block_id})["handover"]
        run = _tool(provider, "execution_ledger_read_run", {"run_id": run_id})["run"]
        verification = _tool(
            provider,
            "execution_ledger_verify_handover",
            {"block_id": block_id, "checksum": handover["checksum"]},
        )["verification"]
        payload = handover["payload"]
        roles = payload.get("roles") or {}
        runtime = payload.get("runtime") or {}
        required = bool(
            verification.get("matched")
            and payload.get("owner_authority")
            and roles.get("codex")
            and roles.get("hermes")
            and run.get("state") == "succeeded"
        )
        return redact({
            "block_id": handover["block_id"],
            "checksum": handover["checksum"],
            "owner_authority": payload.get("owner_authority", "UNVERIFIED"),
            "codex_role": roles.get("codex", "UNVERIFIED"),
            "hermes_role": roles.get("hermes", "UNVERIFIED"),
            "ledger_path": str(provider.ledger.path) if provider.ledger else "UNVERIFIED",
            "shared_kb_role": (
                (payload.get("sources_of_truth") or {}).get("shared_kb")
                or (payload.get("sources_of_truth") or {}).get("knowledge")
                or "UNVERIFIED"
            ),
            "services": runtime.get("services", runtime),
            "openclaw": runtime.get("openclaw", "UNVERIFIED"),
            "a2a": runtime.get("a2a", "UNVERIFIED"),
            "completed_e2e_run": {"run_id": run.get("run_id"), "state": run.get("state"), "events": len(run.get("events") or [])},
            "recovery": payload.get("recovery", []),
            "genuine_human_gates": payload.get("gaps", []),
            "next_autonomous_action": payload.get("next_action", "UNVERIFIED"),
            "knowledge_preflight": {"status": knowledge.get("status"), "source": "shared_kb"},
            "fresh_runtime_session_id": session_id,
            "handshake": "PASS" if required else "FAIL",
        })
    finally:
        provider.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description="Recall and checksum-verify a persistent Hermes handover.")
    parser.add_argument("--block-id", default="SYSTEM_HANDOVER_BLOCK_1")
    parser.add_argument("--run-id", default="run-autofinal-openclaw-adapter-20260908")
    args = parser.parse_args()
    try:
        print(json.dumps(recall_handover(args.block_id, args.run_id), ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"handshake": "FAIL", "error": type(exc).__name__, "detail": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
