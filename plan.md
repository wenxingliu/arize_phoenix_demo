# Data Science PDF Tutor Bot

## Summary

Build a local Streamlit chat app that tutors from `Principles-of-Data-Science-WEB.pdf` using the OpenAI API. The bot will answer conceptual questions, automatically decide whether to explain directly or guide Socratically, and ground responses in the PDF through OpenAI file search plus a local PDF-text fallback.

Use the OpenAI Responses API and vector stores/file search, consistent with current OpenAI docs:

- https://platform.openai.com/docs/quickstart/make-your-first-api-request
- https://platform.openai.com/docs/api-reference/vector-stores

## Key Changes

- Add a Python app with:
  - `streamlit` UI for chat, chapter/topic selection, an automatic tutor mode, and an explicit quiz mode.
  - `openai` SDK integration using `OPENAI_API_KEY`.
  - `pypdf` local extraction for PDF text fallback and lightweight page/chunk lookup.
  - `python-dotenv` for `.env` loading.
- Add setup/config files:
  - `requirements.txt`
  - `.env.example`
  - `.gitignore` excluding `env/`, `.env`, caches, and generated local indexes.
  - `README.md` with install, indexing, and run instructions.
- Default runtime:
  - Model: configurable `OPENAI_MODEL`, default `gpt-5-mini`.
  - Retrieval: upload `Principles-of-Data-Science-WEB.pdf` once to an OpenAI vector store, persist IDs in a local ignored state file such as `.tutor_state.json`.
  - Fallback: extract PDF text locally into page-aware chunks and run simple lexical retrieval if OpenAI file search is unavailable or returns weak context.

## Tutor Behavior

- System prompt defines the bot as a data science tutor, not just a Q&A assistant.
- Answers should:
  - Explain concepts from the PDF in plain language.
  - Automatically choose `Style: Explain` for definition requests, broad concept questions, confusion, or first exposure.
  - Automatically choose `Style: Guide` for homework-like questions, "help me solve" prompts, reasoning tasks, or cases where the student should work through steps.
  - Show the selected style at the top of normal tutor responses.
  - Ask one useful follow-up question or offer a practice prompt when appropriate.
  - Use short retrieved snippets/source labels for grounding.
  - Say when the PDF does not appear to cover the question instead of inventing content.
- UI modes:
  - `Tutor`: default mode; the model decides between direct explanation and Socratic guidance for each question.
  - `Quiz`: explicit practice mode; generate 3-5 practice questions from the retrieved topic.
- Session state keeps chat history, selected mode, and vector-store readiness.

## Implementation Details

- `app.py` owns the Streamlit UI and calls tutor services.
- A small internal package, for example `tutor/`, owns:
  - `openai_client.py`: Responses API calls and vector store setup.
  - `pdf_index.py`: local extraction, chunking, and fallback search.
  - `prompts.py`: tutor instructions, automatic Explain/Guide selection rules, and quiz prompt fragments.
  - `config.py`: env vars, paths, and defaults.
- On first run:
  - Validate the PDF exists.
  - Validate `OPENAI_API_KEY` exists.
  - Upload the PDF to OpenAI file/vector store if no saved vector store state exists.
  - Build local extracted text cache from the PDF.
- Public command:
  - `streamlit run app.py`

## Test Plan

- Add focused `pytest` tests for:
  - PDF existence/path validation.
  - Local chunk creation includes page numbers and non-empty text.
  - Fallback lexical search returns relevant chunks for known data science terms.
  - Prompt builder includes grounding constraints, automatic Explain/Guide criteria, visible style-label requirements, and distinct Quiz behavior.
- Manual acceptance tests:
  - Ask "What is data science?" and verify a grounded answer with `Style: Explain`.
  - Ask "Can you help me solve this step by step?" and verify a grounded answer with `Style: Guide`.
  - Select `Quiz` and verify the bot generates practice questions from retrieved PDF context.
  - Ask an unrelated question and verify the bot says it is outside the PDF.
  - Disable/remove `OPENAI_API_KEY` and verify the app shows a clear setup error.

## Assumptions

- The PDF may be uploaded to OpenAI for retrieval.
- Quiz remains a manual mode; Explain and Guide are automatically selected by the tutor in normal chat.
- The UI should show which response style the tutor chose.
- Exact page-number citations are not required for v1; section snippets/source labels are enough.
- The repository is intentionally empty except for the PDF and existing `env/`, so this will be a fresh Python/Streamlit implementation.
- Network access will be needed during implementation to install Python packages and to call the OpenAI API.
