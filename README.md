# Data Science PDF Tutor Bot

Local Streamlit tutor for `Principles-of-Data-Science-WEB.pdf`.

The default `Tutor` mode lets the model decide whether each answer should be a direct explanation or Socratic guidance. It should label normal tutor responses with `Style: Explain` or `Style: Guide`. `Quiz` remains an explicit practice mode.

## Setup

```bash
source env/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

## Run

```bash
env/bin/streamlit run app.py
```

On first run the app:

- extracts and caches local page-aware PDF chunks in `.tutor_index.json`
- uploads the PDF to an OpenAI vector store and caches IDs in `.tutor_state.json`
- answers questions with retrieved PDF context and tutor-oriented prompts

## Use

- Choose `Tutor` for normal questions. The bot decides whether to explain directly or guide step by step.
- Choose `Quiz` when you want practice questions from the retrieved PDF context.
- Ask chapter or concept questions such as "What is regression?" or "Can you help me solve this step by step?"

## Test

```bash
env/bin/python -m pytest
```
