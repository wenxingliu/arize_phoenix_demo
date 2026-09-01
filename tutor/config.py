from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
PDF_PATH = ROOT_DIR / "Principles-of-Data-Science-WEB.pdf"
STATE_PATH = ROOT_DIR / ".tutor_state.json"
INDEX_PATH = ROOT_DIR / ".tutor_index.json"


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    provider: str
    base_url: str | None
    pdf_path: Path
    state_path: Path
    index_path: Path


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    provider = os.getenv("LLM_PROVIDER", "kimi").lower()
    if provider == "kimi":
        api_key = os.getenv("KIMI_API_KEY") or os.getenv("MOONSHOT_API_KEY")
        model = os.getenv("KIMI_MODEL", "kimi-k2.6")
        base_url = os.getenv("KIMI_BASE_URL") or os.getenv("MOONSHOT_BASE_URL") or "https://api.moonshot.ai/v1"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        base_url = os.getenv("OPENAI_BASE_URL")

    return Settings(
        api_key=api_key,
        model=model,
        provider=provider,
        base_url=base_url,
        pdf_path=PDF_PATH,
        state_path=STATE_PATH,
        index_path=INDEX_PATH,
    )


def require_pdf(path: Path = PDF_PATH) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected PDF at {path}")
    if not path.is_file():
        raise FileNotFoundError(f"PDF path is not a file: {path}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
