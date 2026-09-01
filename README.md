# Data Science PDF Tutor Bot

Local Streamlit tutor for `Principles-of-Data-Science-WEB.pdf`.

The default `Tutor` mode lets the model decide whether each answer should be a direct explanation or Socratic guidance. It should label normal tutor responses with `Style: Explain` or `Style: Guide`. `Quiz` remains an explicit practice mode.

## Setup

```bash
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `KIMI_API_KEY`.

## Run

```bash
env/bin/streamlit run app.py
```

## Run with Datadog LLM Observability

Set `DD_API_KEY`, `DD_SITE`, and `DD_LLMOBS_ENABLED=1` in `.env`, then run the same local Streamlit command:

```bash
env/bin/streamlit run app.py
```

The app loads Datadog configuration from `.env` during startup and enables agentless LLM Observability before creating the OpenAI client. You do not need to use `ddtrace-run` for local development.

The Datadog instrumentation creates a manual LLM span for each answered question and records low-cardinality app metadata such as tutor mode, model, retrieved chunk count, selected `top_k`, whether OpenAI vector store file search was enabled, and token usage when the OpenAI response includes it. Each Streamlit browser session gets a generated Datadog session id, so multiple questions from the same tab can be grouped in Datadog. With `DD_LLMOBS_CAPTURE_IO=1`, it sends the user question as span input and the model answer as span output. It does not send the constructed prompt or retrieved PDF context.

On first run the app:

- extracts and caches local page-aware PDF chunks in `.tutor_index.json`
- uses Kimi through Moonshot's OpenAI-compatible Chat Completions endpoint
- answers questions with retrieved PDF context and tutor-oriented prompts

## Use

- Choose `Tutor` for normal questions. The bot decides whether to explain directly or guide step by step.
- Choose `Quiz` when you want practice questions from the retrieved PDF context.
- Ask chapter or concept questions such as "What is regression?" or "Can you help me solve this step by step?"

## Test

```bash
env/bin/python -m pytest
```
