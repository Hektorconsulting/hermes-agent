from pathlib import Path
import tempfile
import unittest

from tools.shared_knowledge.bridge import KnowledgeBridge, redact
from tools.task_envelope import TaskEnvelope


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

    def test_task_envelope_is_persisted_and_preflight_returns_it(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = KnowledgeBridge(str(Path(directory) / "knowledge.db"))
            request = TaskEnvelope.new(session_id="s-1", objective="inspect backups", channel="cli").to_dict()
            result = bridge.preflight(request)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["task_envelope"]["session_id"], "s-1")
            self.assertEqual(bridge.status()["counts"]["knowledge_tasks"], 1)

    def test_writeback_updates_full_session_and_event_retry_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = KnowledgeBridge(str(Path(directory) / "knowledge.db"))
            payload = {
                "task_id": "task-2", "session_id": "session-2", "run_id": "run-2",
                "archive": [{"role": "user", "content": "first"}],
                "result": {"result_id": "task-2:result", "summary": "ok", "status": "completed"},
            }
            first = bridge.writeback(payload)
            payload["archive"].append({"role": "assistant", "content": "second"})
            second = bridge.writeback(payload)
            self.assertNotEqual(first["event_id"], second["event_id"])
            self.assertEqual(bridge.status()["counts"]["knowledge_sessions"], 1)
            self.assertEqual(bridge.status()["counts"]["knowledge_results"], 1)

    def test_preflight_keeps_results_namespace_scoped(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = KnowledgeBridge(str(Path(directory) / "knowledge.db"))
            bridge.writeback({
                "task_id": "private-task", "session_id": "private-session",
                "privacy_scope": "private", "archive": "private",
                "result": {"result_id": "private-result", "summary": "private"},
            })
            bridge.writeback({
                "task_id": "system-task", "session_id": "system-session",
                "privacy_scope": "system", "archive": "system",
                "result": {"result_id": "system-result", "summary": "system"},
            })
            result = bridge.preflight({
                "task_id": "new-system-task", "session_id": "new-system-session",
                "privacy_scope": "system", "objective": "read recent results",
            })
            summaries = [item.get("summary") for item in result["context_bundle"]["recent_results"]]
            self.assertIn("system", summaries)
            self.assertNotIn("private", summaries)

    def test_preflight_quotes_hyphenated_fts_terms(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = KnowledgeBridge(str(Path(directory) / "knowledge.db"))
            with bridge._connection() as connection:
                connection.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(content, corpus_path UNINDEXED)")
                connection.execute(
                    "INSERT INTO chunks_fts(content, corpus_path) VALUES(?, ?)",
                    ("run autonomy phase2 e2e receipt", "phase2.txt"),
                )
            result = bridge.preflight({
                "task_id": "phase2-test",
                "privacy_scope": "system",
                "objective": "run-autonomy-phase2-e2e-20260913",
            })
            self.assertEqual(result["status"], "PASS")
