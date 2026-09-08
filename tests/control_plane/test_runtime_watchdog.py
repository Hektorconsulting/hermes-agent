from __future__ import annotations

import unittest
from unittest.mock import patch

from tools import runtime_watchdog


class RuntimeWatchdogTests(unittest.TestCase):
    def test_check_service_repairs_then_verifies(self) -> None:
        checks = iter((False, True))
        with patch.object(runtime_watchdog, "_restart", return_value=True) as restart:
            record = runtime_watchdog._check_service("openclaw", "openclaw-gateway.service", lambda: next(checks), user_unit=True)
        self.assertTrue(record["restart_attempted"])
        self.assertTrue(record["healthy_after"])
        restart.assert_called_once_with("openclaw-gateway.service", user_unit=True)

    def test_check_service_does_not_restart_healthy_unit(self) -> None:
        with patch.object(runtime_watchdog, "_restart") as restart:
            record = runtime_watchdog._check_service("hermes", "hermes-gateway.service", lambda: True)
        self.assertFalse(record["restart_attempted"])
        self.assertTrue(record["healthy_after"])
        restart.assert_not_called()
