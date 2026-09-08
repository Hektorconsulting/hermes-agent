from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from tools.remote_execution_ledger import RemoteExecutionLedger


class RemoteExecutionLedgerTests(unittest.TestCase):
    def test_create_uses_fixed_wrapper_and_base64_framed_payload(self):
        bridge = RemoteExecutionLedger(
            host_alias="hostinger-vps", wrapper="C:/Hermes/ops/Invoke-HostingerCommand.ps1",
            remote_script="/home/ai-admin/.hermes/hermes-agent/tools/execution_ledger.py",
            remote_db="/home/ai-admin/.hermes/state/execution-ledger.sqlite3",
        )
        completed = type("Completed", (), {"returncode": 0, "stdout": json.dumps({"ok": True, "stdout": '{"created":true}'}), "stderr": ""})()
        with patch("tools.remote_execution_ledger.shutil.which", return_value="powershell.exe"), patch(
            "tools.remote_execution_ledger.subprocess.run", return_value=completed
        ) as run:
            result = bridge.create_run({"run_id": "r-1", "objective": "repair bridge"})
        self.assertTrue(result["created"])
        command = run.call_args.args[0]
        payload = command[command.index("-Payload") + 1]
        self.assertIn("base64 -d", payload)
        self.assertNotIn("repair bridge", payload)
        self.assertIn("HERMES_EXECUTION_LEDGER=", payload)


if __name__ == "__main__":
    unittest.main()
