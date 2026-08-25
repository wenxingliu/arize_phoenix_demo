from pathlib import Path

import pytest

from tutor.config import require_pdf
from tutor.pdf_index import Chunk, search_chunks, split_text


def test_require_pdf_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        require_pdf(tmp_path / "missing.pdf")


def test_split_text_overlaps_chunks() -> None:
    chunks = split_text(" ".join(str(number) for number in range(12)), max_words=5, overlap=2)
    assert chunks == ["0 1 2 3 4", "3 4 5 6 7", "6 7 8 9 10", "9 10 11"]


def test_search_chunks_ranks_relevant_content() -> None:
    chunks = [
        Chunk(id="p1-c1", page=1, text="Regression predicts numerical values from features."),
        Chunk(id="p2-c1", page=2, text="Classification predicts categories and labels."),
        Chunk(id="p3-c1", page=3, text="Data visualization uses charts."),
    ]

    results = search_chunks("How does regression prediction work?", chunks, limit=1)

    assert results[0].id == "p1-c1"
