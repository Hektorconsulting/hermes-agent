import os
import tempfile
import unittest
from pathlib import Path

from tools.execution_ledger import ExecutionLedger
from tools.hermes_handover_recall import recall_handover


class HermesHandoverRecallTests(unittest.TestCase):
    def test_fresh_runtime_reconstructs_and_verifies_handover(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger_path = root / "execution-ledger.sqlite3"
            knowledge_path = root / "knowledge.sqlite3"
            old_ledger = os.environ.get("HERMES_EXECUTION_LEDGER")
            old_knowledge = os.environ.get("HERMES_KNOWLEDGE_DB")
            os.environ["HERMES_EXECUTION_LEDGER"] = str(ledger_path)
            os.environ["HERMES_KNOWLEDGE_DB"] = str(knowledge_path)
            try:
                ledger = ExecutionLedger(ledger_path)
                ledger.create_run({"run_id": "run-test", "task_id": "run-test", "objective": "test", "idempotency_key": "run-test"})
                ledger.transition_run("run-test", "succeeded", actor="test")
                recorded = ledger.record_handover("BLOCK_TEST", {
                    "owner_authority": "CURRENT OWNER OBJECTIVE",
                    "roles": {"codex": "primary", "hermes": "operational partner, never approval authority"},
                    "sources_of_truth": {"shared_kb": "knowledge authority"},
                    "runtime": {"services": "active", "openclaw": "verified", "a2a": "verified"},
                    "recovery": ["backup"], "gaps": [], "next_action": "continue",
                })
                recalled = recall_handover("BLOCK_TEST", "run-test")
                self.assertEqual(recalled["checksum"], recorded["checksum"])
                self.assertEqual(recalled["completed_e2e_run"]["state"], "succeeded")
                self.assertEqual(recalled["handshake"], "PASS")
            finally:
                if old_ledger is None:
                    os.environ.pop("HERMES_EXECUTION_LEDGER", None)
                else:
                    os.environ["HERMES_EXECUTION_LEDGER"] = old_ledger
                if old_knowledge is None:
                    os.environ.pop("HERMES_KNOWLEDGE_DB", None)
                else:
                    os.environ["HERMES_KNOWLEDGE_DB"] = old_knowledge
