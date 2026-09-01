from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "").lower() in {"1", "true", "yes"}


def configure_datadog() -> None:
    load_dotenv(ROOT_DIR / ".env")

    if not _env_enabled("DD_LLMOBS_ENABLED"):
        return

    os.environ.setdefault("DD_LLMOBS_AGENTLESS_ENABLED", "1")
    os.environ.setdefault("DD_LLMOBS_ML_APP", "data-science-tutor")
    os.environ.setdefault("DD_SERVICE", "data-science-tutor")
    os.environ.setdefault("DD_ENV", "local")
    os.environ.setdefault("DD_APM_TRACING_ENABLED", "false")
    os.environ.setdefault("DD_OPENAI_SPAN_PROMPT_COMPLETION_SAMPLE_RATE", "0")
    os.environ.setdefault("DD_OPENAI_LOGS_ENABLED", "false")

    if not os.getenv("DD_API_KEY") or not os.getenv("DD_SITE"):
        return

    try:
        from ddtrace.llmobs import LLMObs
    except ImportError:
        return

    if LLMObs.enabled:
        return

    LLMObs.enable(
        ml_app=os.getenv("DD_LLMOBS_ML_APP"),
        api_key=os.getenv("DD_API_KEY"),
        site=os.getenv("DD_SITE"),
        env=os.getenv("DD_ENV"),
        service=os.getenv("DD_SERVICE"),
        agentless_enabled=True,
        integrations_enabled=False,
    )
