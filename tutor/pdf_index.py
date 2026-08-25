from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from .config import file_sha256, require_pdf


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_+-]*")


@dataclass(frozen=True)
class Chunk:
    id: str
    page: int
    text: str


def tokenize(text: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(text)}


def split_text(text: str, max_words: int = 220, overlap: int = 40) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for start in range(0, len(words), step):
        part = words[start : start + max_words]
        if part:
            chunks.append(" ".join(part))
        if start + max_words >= len(words):
            break
    return chunks


def extract_chunks(pdf_path: Path) -> list[Chunk]:
    require_pdf(pdf_path)
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("Install dependencies with `pip install -r requirements.txt`.") from exc

    reader = PdfReader(str(pdf_path))
    chunks: list[Chunk] = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = re.sub(r"\s+", " ", text).strip()
        for chunk_index, chunk_text in enumerate(split_text(text), start=1):
            chunks.append(
                Chunk(
                    id=f"p{page_index}-c{chunk_index}",
                    page=page_index,
                    text=chunk_text,
                )
            )
    return chunks


def load_or_build_index(pdf_path: Path, index_path: Path) -> list[Chunk]:
    pdf_hash = file_sha256(pdf_path)
    if index_path.exists():
        with index_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if payload.get("pdf_sha256") == pdf_hash:
            return [Chunk(**item) for item in payload.get("chunks", [])]

    chunks = extract_chunks(pdf_path)
    payload = {
        "pdf_sha256": pdf_hash,
        "chunk_count": len(chunks),
        "chunks": [asdict(chunk) for chunk in chunks],
    }
    with index_path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=True, indent=2)
    return chunks


def search_chunks(query: str, chunks: list[Chunk], limit: int = 5) -> list[Chunk]:
    query_terms = tokenize(query)
    if not query_terms:
        return chunks[:limit]

    scored: list[tuple[float, Chunk]] = []
    total = max(1, len(chunks))
    document_frequency = {
        term: sum(1 for chunk in chunks if term in tokenize(chunk.text))
        for term in query_terms
    }

    for chunk in chunks:
        chunk_terms = tokenize(chunk.text)
        overlap = query_terms & chunk_terms
        if not overlap:
            continue
        score = 0.0
        text_lower = chunk.text.lower()
        for term in overlap:
            term_frequency = text_lower.count(term)
            inverse_document_frequency = math.log((1 + total) / (1 + document_frequency[term])) + 1
            score += term_frequency * inverse_document_frequency
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in scored[:limit]]


def format_context(chunks: list[Chunk]) -> str:
    if not chunks:
        return "No local PDF context was retrieved."
    return "\n\n".join(
        f"[Source: page {chunk.page}, chunk {chunk.id}]\n{chunk.text}" for chunk in chunks
    )
