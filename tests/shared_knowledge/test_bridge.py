from pathlib import Path
import tempfile
import unittest

from tools.shared_knowledge.bridge import KnowledgeBridge, redact


class SharedKnowledgeTests(unittest.TestCase):
    def test_redaction_never_keeps_secret_value(self):
        self.assertNotIn("secret-value", redact("api_key=secret-value"))
        self.assertIn("[REDACTED]", redact("api_key=secret-value"))

    def test_writeback_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = KnowledgeBridge(str(Path(directory) / "knowledge.db"))
            payload = {
                "task_id": "task-1", "session_id": "session-1", "channel": "test",
                "archive": "requirement", "requirement": {"objective": "use knowledge"},
                "result": {"status": "draft", "summary": "stored"},
            }
            first = bridge.writeback(payload)
            second = bridge.writeback(payload)
            self.assertEqual(first["status"], second["status"])
            self.assertEqual(bridge.status()["counts"]["knowledge_sessions"], 1)
            self.assertEqual(bridge.status()["counts"]["knowledge_requirements"], 1)
            self.assertEqual(bridge.status()["counts"]["knowledge_results"], 1)
