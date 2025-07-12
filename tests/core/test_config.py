# --- tests/core/test_config.py ---
import os
import pytest
from src.sfmc_client.core.config import Config


def test_config_loads_env(monkeypatch):
    monkeypatch.setenv("SFMC_CLIENT_ID", "abc")
    monkeypatch.setenv("SFMC_CLIENT_SECRET", "xyz")
    monkeypatch.setenv("SFMC_TENANT_SUBDOMAIN", "testsub")
    monkeypatch.setenv("SFMC_ACCOUNT_IDS", '{"default": "acct123"}')

    cfg = Config()

    assert cfg.client_id == "abc"
    assert cfg.client_secret == "xyz"
    assert cfg.tenant_subdomain == "testsub"
    assert cfg.account_id == "acct123"


def test_invalid_account_ids(monkeypatch):
    monkeypatch.setenv("SFMC_ACCOUNT_IDS", "bad-json")
    with pytest.raises(ValueError):
        Config()


def test_missing_fields(monkeypatch):
    monkeypatch.delenv("SFMC_CLIENT_ID", raising=False)
    monkeypatch.delenv("SFMC_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("SFMC_TENANT_SUBDOMAIN", raising=False)
    monkeypatch.setenv("SFMC_ACCOUNT_IDS", '{}')
    with pytest.raises(ValueError):
        Config()
