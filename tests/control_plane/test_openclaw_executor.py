from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.execution_ledger import ExecutionLedger
from tools.openclaw_executor import OpenClawExecutor


class OpenClawExecutorTests(unittest.TestCase):
    def test_uses_message_file_and_records_hash_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "openclaw.json"
            config.write_text(json.dumps({"gateway": {"auth": {"token": "private-token"}}}), encoding="utf-8")
            ledger = ExecutionLedger(root / "ledger.sqlite3")
            ledger.create_run({"run_id": "run-openclaw", "goal_id": "goal", "idempotency_key": "once", "state": "queued"})
            ledger.claim_run("run-openclaw", "codex")
            ledger.transition_run("run-openclaw", "executing", actor="codex")
            seen: dict[str, object] = {}

            def fake_run(command, **kwargs):
                seen["command"] = command
                seen["message_path"] = command[command.index("--message-file") + 1]
                return type("Result", (), {"returncode": 0, "stdout": json.dumps({"runId": "oc-1", "status": "completed", "result": "safe"})})()

            with patch("tools.openclaw_executor.subprocess.run", side_effect=fake_run):
                summary = OpenClawExecutor(config_path=config, executable="openclaw", ledger=ledger).execute(
                    run_id="run-openclaw", message="private task content", agent="main", timeout_seconds=30
                )
            self.assertIn("--message-file", seen["command"])
            self.assertNotIn("private task content", seen["command"])
            self.assertFalse(Path(str(seen["message_path"])).exists())
            self.assertEqual(summary["status"], "completed")
            run = ledger.read_run("run-openclaw")
            self.assertEqual(run["state"], "succeeded")
            self.assertNotIn("private task content", json.dumps(run))

    def test_rejects_unsafe_executor_identity(self) -> None:
        with self.assertRaises(ValueError):
            OpenClawExecutor().execute(run_id="bad id", message="x")
