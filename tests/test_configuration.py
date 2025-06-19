import os
import pytest
from backend.config import get_config, reload_config
from backend.config.schema import Environment
from pydantic import ValidationError

def test_config_loading():
    config = get_config()
    assert config.app_name == "Echo"
    assert config.environment in Environment
    assert hasattr(config, "openai")
    assert hasattr(config, "mcp")
    assert hasattr(config, "web")
    assert config.openai.model == "gpt-4o-mini"
    assert config.mcp.discovery_timeout > 0
    assert config.web.rate_limit > 0

def test_config_validation():
    from backend.config.schema import OpenAIConfig
    with pytest.raises(ValidationError):
        OpenAIConfig(api_key="test", max_tokens=-1)

def test_environment_override(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("DEBUG", "false")
    config = reload_config()
    assert config.environment == Environment.PRODUCTION
    assert config.debug is False
    monkeypatch.delenv("ENVIRONMENT")
    monkeypatch.delenv("DEBUG")
    reload_config()  # Reset
