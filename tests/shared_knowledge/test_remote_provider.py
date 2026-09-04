import base64
import json
import unittest
from unittest.mock import patch

from plugins.memory.shared_kb import _RemoteKnowledgeBridge


class RemoteKnowledgeBridgeTests(unittest.TestCase):
    def test_call_uses_fixed_wrapper_and_base64_stdin_payload(self):
        bridge = _RemoteKnowledgeBridge({
            "remote_host_alias": "hostinger-vps",
            "remote_db_path": "/home/ai-admin/knowledge/canonical.sqlite3",
            "remote_bridge_script": "/home/ai-admin/hermes-bridge.py",
            "remote_wrapper": r"C:\Hermes\ops\Invoke-HostingerCommand.ps1",
            "remote_timeout_seconds": 20,
        })
        payload = {"objective": "quote $(safe) and backticks", "privacy_scope": "system"}
        outer = {"ok": True, "stdout": json.dumps({"status": "PASS"})}
        completed = type("Completed", (), {"returncode": 0, "stdout": json.dumps(outer)})()

        with patch("plugins.memory.shared_kb.shutil.which", return_value="powershell.exe"), patch(
            "plugins.memory.shared_kb.subprocess.run", return_value=completed
        ) as run:
            result = bridge.call("preflight", payload, task_id="task-1")

        self.assertEqual(result, {"status": "PASS"})
        command = run.call_args.args[0]
        self.assertEqual(command[:4], ["powershell.exe", "-NoProfile", "-NonInteractive", "-File"])
        remote_payload = command[command.index("-Payload") + 1]
        self.assertIn("base64 -d", remote_payload)
        self.assertIn("python3 '/home/ai-admin/hermes-bridge.py' preflight --stdin", remote_payload)
        encoded = remote_payload.split("printf '%s' '", 1)[1].split("' | base64", 1)[0]
        self.assertEqual(json.loads(base64.b64decode(encoded)), payload)
        self.assertNotIn(payload["objective"], remote_payload)

    def test_call_fails_closed_on_wrapper_failure(self):
        bridge = _RemoteKnowledgeBridge({
            "remote_host_alias": "hostinger-vps",
            "remote_db_path": "/canonical.sqlite3",
            "remote_bridge_script": "/bridge.py",
            "remote_wrapper": r"C:\Hermes\ops\Invoke-HostingerCommand.ps1",
        })
        completed = type("Completed", (), {"returncode": 1, "stdout": ""})()
        with patch("plugins.memory.shared_kb.shutil.which", return_value="powershell.exe"), patch(
            "plugins.memory.shared_kb.subprocess.run", return_value=completed
        ):
            self.assertIsNone(bridge.call("preflight", {"objective": "x"}))


if __name__ == "__main__":
    unittest.main()
