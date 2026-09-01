from __future__ import annotations

import os
from typing import Callable, TypeVar


try:
    from ddtrace.llmobs import LLMObs
    from ddtrace.llmobs.decorators import llm
except ImportError:  # pragma: no cover - allows tests before optional env install
    LLMObs = None
    llm = None


T = TypeVar("T")


def _llmobs_enabled() -> bool:
    return (
        LLMObs is not None
        and llm is not None
        and bool(getattr(LLMObs, "enabled", False))
        and os.getenv("DD_LLMOBS_ENABLED", "").lower() in {"1", "true", "yes"}
    )


def _capture_io_enabled() -> bool:
    return os.getenv("DD_LLMOBS_CAPTURE_IO", "").lower() in {"1", "true", "yes"}


def _usage_metrics(response: object) -> dict[str, int]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}

    metrics = {}
    for metric_name, usage_attr in (
        ("input_tokens", "input_tokens"),
        ("input_tokens", "prompt_tokens"),
        ("output_tokens", "output_tokens"),
        ("output_tokens", "completion_tokens"),
        ("total_tokens", "total_tokens"),
    ):
        if metric_name in metrics:
            continue
        value = getattr(usage, usage_attr, None)
        if isinstance(value, int):
            metrics[metric_name] = value
    return metrics


def _output_text(response: object) -> str | None:
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str):
        return output_text

    choices = getattr(response, "choices", None)
    if not choices:
        return None
    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    return None


def call_with_llm_trace(
    call: Callable[[], T],
    *,
    input_data: str,
    mode: str,
    model: str,
    retrieved_chunk_count: int,
    top_k: int | None,
    vector_store_enabled: bool,
    session_id: str | None = None,
) -> T:
    if not _llmobs_enabled():
        return call()

    tags = {
        "component": "data_science_tutor",
        "tutor.mode": mode,
        "tutor.vector_store_enabled": str(vector_store_enabled).lower(),
        "tutor.retrieved_chunk_count": str(retrieved_chunk_count),
    }
    if top_k is not None:
        tags["tutor.top_k"] = str(top_k)

    @llm(model_name=model, model_provider="openai", name="tutor.answer_question", session_id=session_id)
    def traced_call() -> T:
        response = call()
        annotate_kwargs = {
            "metadata": {
                "mode": mode,
                "retrieved_chunk_count": retrieved_chunk_count,
                "top_k": top_k,
                "vector_store_enabled": vector_store_enabled,
            },
            "metrics": _usage_metrics(response),
            "tags": tags,
        }
        if _capture_io_enabled():
            annotate_kwargs["input_data"] = input_data
            annotate_kwargs["output_data"] = _output_text(response)
        LLMObs.annotate(**annotate_kwargs)
        return response

    return traced_call()
