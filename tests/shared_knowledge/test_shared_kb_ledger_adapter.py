import json
import os
import tempfile
import unittest
from pathlib import Path

from plugins.memory.shared_kb import SharedKnowledgeProvider
from tools.execution_ledger import ExecutionLedger


class SharedKnowledgeLedgerAdapterTests(unittest.TestCase):
    def test_reads_and_checksum_verifies_a_persistent_handover(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger_path = root / "execution-ledger.sqlite3"
            knowledge_path = root / "knowledge.sqlite3"
            previous = os.environ.get("HERMES_EXECUTION_LEDGER")
            os.environ["HERMES_EXECUTION_LEDGER"] = str(ledger_path)
            try:
                ledger = ExecutionLedger(ledger_path)
                recorded = ledger.record_handover("SYSTEM_HANDOVER_BLOCK_TEST", {"role": "operational_partner"})
                provider = SharedKnowledgeProvider({"db_path": str(knowledge_path), "execution_ledger_path": str(ledger_path)})
                provider.initialize("test-session", platform="cli")
                names = {schema["name"] for schema in provider.get_tool_schemas()}
                self.assertTrue({"execution_ledger_read_handover", "execution_ledger_read_run", "execution_ledger_verify_handover"} <= names)
                recalled = json.loads(provider.handle_tool_call("execution_ledger_read_handover", {"block_id": "SYSTEM_HANDOVER_BLOCK_TEST"}))
                self.assertEqual(recalled["status"], "PASS")
                self.assertEqual(recalled["handover"]["checksum"], recorded["checksum"])
                verified = json.loads(provider.handle_tool_call("execution_ledger_verify_handover", {"block_id": "SYSTEM_HANDOVER_BLOCK_TEST", "checksum": recorded["checksum"]}))
                self.assertEqual(verified["status"], "PASS")
                self.assertTrue(verified["verification"]["matched"])
            finally:
                if previous is None:
                    os.environ.pop("HERMES_EXECUTION_LEDGER", None)
                else:
                    os.environ["HERMES_EXECUTION_LEDGER"] = previous
