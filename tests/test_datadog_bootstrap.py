import os

from tutor import datadog_bootstrap


class FakeLLMObs:
    enabled = False
    enable_kwargs = None

    @classmethod
    def enable(cls, **kwargs):
        cls.enabled = True
        cls.enable_kwargs = kwargs


def test_configure_datadog_skips_when_llmobs_is_disabled(monkeypatch) -> None:
    monkeypatch.delenv("DD_LLMOBS_ENABLED", raising=False)
    monkeypatch.setattr(datadog_bootstrap, "load_dotenv", lambda path: None)

    datadog_bootstrap.configure_datadog()

    assert "DD_LLMOBS_ML_APP" not in os.environ


def test_configure_datadog_sets_defaults_before_enabling(monkeypatch) -> None:
    FakeLLMObs.enabled = False
    FakeLLMObs.enable_kwargs = None

    monkeypatch.setenv("DD_LLMOBS_ENABLED", "1")
    monkeypatch.setenv("DD_API_KEY", "test-api-key")
    monkeypatch.setenv("DD_SITE", "us3.datadoghq.com")
    monkeypatch.delenv("DD_LLMOBS_ML_APP", raising=False)
    monkeypatch.delenv("DD_SERVICE", raising=False)
    monkeypatch.delenv("DD_ENV", raising=False)
    monkeypatch.setattr(datadog_bootstrap, "load_dotenv", lambda path: None)

    import builtins

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ddtrace.llmobs":
            class Module:
                LLMObs = FakeLLMObs

            return Module()
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    datadog_bootstrap.configure_datadog()

    assert os.environ["DD_APM_TRACING_ENABLED"] == "false"
    assert os.environ["DD_OPENAI_SPAN_PROMPT_COMPLETION_SAMPLE_RATE"] == "0"
    assert FakeLLMObs.enable_kwargs == {
        "ml_app": "data-science-tutor",
        "api_key": "test-api-key",
        "site": "us3.datadoghq.com",
        "env": "local",
        "service": "data-science-tutor",
        "agentless_enabled": True,
        "integrations_enabled": False,
    }
