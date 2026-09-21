"""Regression coverage for the explicit VPS-only model boundary."""

from unittest.mock import patch

import agent.auxiliary_client as auxiliary_client


def test_vps_only_policy_is_opt_in(monkeypatch):
    monkeypatch.delenv("HERMES_VPS_ONLY", raising=False)
    with patch("hermes_cli.config.load_config_readonly", return_value={}):
        assert auxiliary_client._vps_only_inference_required() is False


def test_vps_only_policy_accepts_explicit_local_vps_ollama(monkeypatch):
    monkeypatch.delenv("HERMES_VPS_ONLY", raising=False)
    with patch(
        "hermes_cli.config.load_config_readonly",
        return_value={"vps_only": True},
    ):
        assert auxiliary_client._vps_only_inference_required() is True
        assert auxiliary_client._vps_only_provider_allowed(
            "custom:vps-ollama",
            "http://127.0.0.1:11434/v1",
        ) is True
        assert auxiliary_client._vps_only_provider_allowed(
            "openrouter",
            "https://openrouter.ai/api/v1",
        ) is False
        assert auxiliary_client._vps_only_provider_allowed(
            "custom",
            "http://127.0.0.1:11435/v1",
        ) is False


def test_vps_only_router_rejects_external_provider_before_auth(monkeypatch):
    monkeypatch.setattr(auxiliary_client, "_vps_only_inference_required", lambda: True)
    with patch.object(auxiliary_client, "_validate_proxy_env_urls"):
        client, model = auxiliary_client.resolve_provider_client(
            "openrouter",
            model="some-model",
            explicit_base_url="https://openrouter.ai/api/v1",
        )
    assert client is None
    assert model is None
