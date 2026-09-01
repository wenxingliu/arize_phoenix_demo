from tutor import observability


class FakeLLMObs:
    enabled = True
    annotations = []

    @classmethod
    def annotate(cls, **kwargs):
        cls.annotations.append(kwargs)


class FakeUsage:
    input_tokens = 10
    output_tokens = 20
    total_tokens = 30


class FakeResponse:
    usage = FakeUsage()
    output_text = "A concise answer."


class FakeLLMDecorator:
    def __init__(self) -> None:
        self.calls = []

    def __call__(
        self,
        *,
        model_name: str,
        model_provider: str,
        name: str,
        session_id: str | None = None,
    ):
        self.calls.append(
            {
                "model_name": model_name,
                "model_provider": model_provider,
                "name": name,
                "session_id": session_id,
            }
        )

        def decorate(func):
            def wrapper():
                return func()

            return wrapper

        return decorate


def test_call_with_llm_trace_records_manual_llm_span_metadata(monkeypatch) -> None:
    fake_llm = FakeLLMDecorator()
    FakeLLMObs.enabled = True
    FakeLLMObs.annotations = []
    monkeypatch.setattr(observability, "LLMObs", FakeLLMObs)
    monkeypatch.setattr(observability, "llm", fake_llm)
    monkeypatch.setenv("DD_LLMOBS_ENABLED", "1")

    response = observability.call_with_llm_trace(
        lambda: FakeResponse(),
        input_data="What is data science?",
        mode="Tutor",
        model="gpt-5-mini",
        retrieved_chunk_count=5,
        top_k=5,
        vector_store_enabled=True,
        session_id="session-123",
    )

    assert isinstance(response, FakeResponse)
    assert fake_llm.calls == [
        {
            "model_name": "gpt-5-mini",
            "model_provider": "openai",
            "name": "tutor.answer_question",
            "session_id": "session-123",
        }
    ]
    assert FakeLLMObs.annotations == [
        {
            "metadata": {
                "mode": "Tutor",
                "retrieved_chunk_count": 5,
                "top_k": 5,
                "vector_store_enabled": True,
            },
            "metrics": {
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
            },
            "tags": {
                "component": "data_science_tutor",
                "tutor.mode": "Tutor",
                "tutor.vector_store_enabled": "true",
                "tutor.retrieved_chunk_count": "5",
                "tutor.top_k": "5",
            },
        }
    ]


def test_call_with_llm_trace_records_inputs_outputs_when_enabled(monkeypatch) -> None:
    fake_llm = FakeLLMDecorator()
    FakeLLMObs.enabled = True
    FakeLLMObs.annotations = []
    monkeypatch.setattr(observability, "LLMObs", FakeLLMObs)
    monkeypatch.setattr(observability, "llm", fake_llm)
    monkeypatch.setenv("DD_LLMOBS_ENABLED", "1")
    monkeypatch.setenv("DD_LLMOBS_CAPTURE_IO", "1")

    observability.call_with_llm_trace(
        lambda: FakeResponse(),
        input_data="What is data science?",
        mode="Tutor",
        model="gpt-5-mini",
        retrieved_chunk_count=5,
        top_k=5,
        vector_store_enabled=True,
        session_id="session-123",
    )

    assert FakeLLMObs.annotations[0]["input_data"] == "What is data science?"
    assert FakeLLMObs.annotations[0]["output_data"] == "A concise answer."


def test_call_with_llm_trace_is_noop_when_llmobs_is_disabled(monkeypatch) -> None:
    fake_llm = FakeLLMDecorator()
    FakeLLMObs.enabled = False
    FakeLLMObs.annotations = []
    monkeypatch.setattr(observability, "LLMObs", FakeLLMObs)
    monkeypatch.setattr(observability, "llm", fake_llm)
    monkeypatch.setenv("DD_LLMOBS_ENABLED", "1")

    response = observability.call_with_llm_trace(
        lambda: FakeResponse(),
        input_data="What is data science?",
        mode="Tutor",
        model="gpt-5-mini",
        retrieved_chunk_count=5,
        top_k=5,
        vector_store_enabled=True,
        session_id="session-123",
    )

    assert isinstance(response, FakeResponse)
    assert fake_llm.calls == []
    assert FakeLLMObs.annotations == []
