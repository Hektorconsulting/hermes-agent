from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.execution_ledger import ExecutionLedger
from tools.task_envelope import TaskEnvelope


class ExecutionLedgerTests(unittest.TestCase):
    def test_idempotent_run_claim_transition_and_recovery_history(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger = ExecutionLedger(Path(directory) / "ledger.sqlite3")
            envelope = TaskEnvelope.new(
                task_id="task-control-plane", run_id="run-control-plane", project="system",
                target="vps", objective="repair the transport", capability_scope=("ssh", "mcp"),
            )
            first = ledger.create_run(envelope)
            duplicate = ledger.create_run(envelope)
            self.assertTrue(first["created"])
            self.assertFalse(duplicate["created"])
            self.assertTrue(ledger.claim_run(envelope.run_id, "codex", lease_seconds=90)["claimed"])
            self.assertFalse(ledger.claim_run(envelope.run_id, "hermes", lease_seconds=90)["claimed"])
            ledger.transition_run(envelope.run_id, "executing", actor="codex")
            repaired = ledger.transition_run(
                envelope.run_id, "repairing", actor="codex", payload={"secret": "must-not-persist", "reason": "test"},
            )
            self.assertEqual(repaired["state"], "repairing")
            run = ledger.read_run(envelope.run_id)
            self.assertEqual(run["recovery"][0]["detail"]["secret"], "[REDACTED]")
            self.assertEqual([event["event_type"] for event in run["events"]], ["run_created", "run_claimed", "state_transition", "state_transition"])

    def test_capability_handover_and_sqlite_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger = ExecutionLedger(root / "ledger.sqlite3")
            capability = ledger.register_capability({
                "capability_id": "control-plane-mcp", "capability_type": "mcp",
                "state": "verified", "authentication_state": "private-stdio",
                "evidence": {"run": "canary"}, "recovery": {"action": "restart"},
            })
            self.assertEqual(capability["state"], "verified")
            handover = ledger.record_handover("SYSTEM_HANDOVER_BLOCK_1", {"architecture": "v2"})
            verified = ledger.verify_handover("SYSTEM_HANDOVER_BLOCK_1", handover["checksum"], verifier="hermes")
            self.assertTrue(verified["matched"])
            backup = ledger.backup(root / "backup.sqlite3")
            self.assertTrue(Path(backup["path"]).exists())
            self.assertGreater(backup["bytes"], 0)

    def test_raw_v2_envelope_survives_an_older_task_envelope_runtime(self):
        class LegacyEnvelope:
            task_id = "legacy-task"
            run_id = "legacy-run"
            project = ""
            objective = ""
            execution_state = "received"
            assigned_to = "hermes"

            @classmethod
            def from_mapping(cls, _value):
                return cls()

            def to_dict(self):
                return {"task_id": self.task_id, "run_id": self.run_id, "objective": self.objective}

        with tempfile.TemporaryDirectory() as directory, patch("tools.execution_ledger.TaskEnvelope", LegacyEnvelope):
            ledger = ExecutionLedger(Path(directory) / "ledger.sqlite3")
            result = ledger.create_run({
                "task_id": "legacy-task", "run_id": "legacy-run", "generation": 2,
                "idempotency_key": "legacy-key", "project": "system", "target": "vps",
                "objective": "retain v2 data", "capability_scope": ["mcp"],
            })
            self.assertEqual(result["run"]["target"], "vps")
            self.assertEqual(result["run"]["envelope"]["capability_scope"], ["mcp"])


if __name__ == "__main__":
    unittest.main()
