from tutor import config


def test_load_settings_uses_kimi_defaults(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda path: None)
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("KIMI_API_KEY", "kimi-key")
    monkeypatch.delenv("KIMI_MODEL", raising=False)
    monkeypatch.delenv("KIMI_BASE_URL", raising=False)
    monkeypatch.delenv("MOONSHOT_BASE_URL", raising=False)

    settings = config.load_settings()

    assert settings.api_key == "kimi-key"
    assert settings.provider == "kimi"
    assert settings.model == "kimi-k2.6"
    assert settings.base_url == "https://api.moonshot.ai/v1"


def test_load_settings_does_not_use_openai_key_for_kimi(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda path: None)
    monkeypatch.setenv("LLM_PROVIDER", "kimi")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.delenv("KIMI_API_KEY", raising=False)
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)

    settings = config.load_settings()

    assert settings.api_key is None


def test_load_settings_keeps_openai_provider_supported(monkeypatch) -> None:
    monkeypatch.setattr(config, "load_dotenv", lambda path: None)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    settings = config.load_settings()

    assert settings.api_key == "openai-key"
    assert settings.provider == "openai"
    assert settings.model == "gpt-5-mini"
    assert settings.base_url == "https://api.openai.com/v1"
