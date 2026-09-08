#!/usr/bin/env python3
"""Private stdio MCP surface for the Hermes execution ledger."""
from __future__ import annotations

import json
import os

from tools.execution_ledger import ExecutionLedger
from tools.remote_execution_ledger import RemoteExecutionLedger


def _object(raw: str) -> dict:
    value = json.loads(raw or "{}")
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object")
    return value


def build_server(db_path: str | None = None):
    from mcp.server import MCPServer

    ledger = RemoteExecutionLedger.from_environment() if os.environ.get("HERMES_EXECUTION_LEDGER_REMOTE_HOST") else ExecutionLedger(db_path)
    server = MCPServer(
        "hermes-control-plane",
        instructions=(
            "Private durable execution-state control plane. Create a run before technical work, "
            "record meaningful state transitions and recovery evidence, register verified capabilities, "
            "and verify only the two major handover blocks. Never persist secrets."
        ),
    )

    def run_create(envelope_json: str = "{}"):
        return ledger.create_run(_object(envelope_json), actor="codex")

    def run_claim(run_id: str, executor: str, lease_seconds: int = 900):
        return ledger.claim_run(run_id, executor, lease_seconds=lease_seconds)

    def run_transition(run_id: str, state: str, actor: str, payload_json: str = "{}"):
        return ledger.transition_run(run_id, state, actor=actor, payload=_object(payload_json))

    def run_read(run_id: str):
        return ledger.read_run(run_id)

    def run_list(limit: int = 50):
        return ledger.list_runs(limit=limit)

    def capability_register(capability_json: str = "{}", actor: str = "codex"):
        return ledger.register_capability(_object(capability_json), actor=actor)

    def handover_record(block_id: str, payload_json: str = "{}"):
        return ledger.record_handover(block_id, _object(payload_json))

    def handover_verify(block_id: str, checksum: str, verifier: str):
        return ledger.verify_handover(block_id, checksum, verifier=verifier)

    def ledger_backup(destination: str):
        """Create a restorable ledger backup at a controlled runtime location."""
        return ledger.backup(destination)

    tools = (
        (run_create, "run_create", "Create an idempotent TaskEnvelope v2 execution run."),
        (run_claim, "run_claim", "Claim an active execution run with a renewable lease."),
        (run_transition, "run_transition", "Append a durable state, verification, or recovery transition."),
        (run_read, "run_read", "Read a run and its append-only event history."),
        (run_list, "run_list", "List recent durable runs."),
        (capability_register, "capability_register", "Register a discovered and verified capability."),
        (handover_record, "handover_record", "Persist one major Hermes handover block."),
        (handover_verify, "handover_verify", "Verify a persisted handover checksum from a fresh executor."),
        (ledger_backup, "ledger_backup", "Create and hash a restorable execution-ledger backup."),
    )
    for handler, name, description in tools:
        try:
            server.add_tool(handler, name=name, description=description)
        except TypeError:
            server.tool(name=name, description=description)(handler)
    return server


def main() -> int:
    build_server().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
