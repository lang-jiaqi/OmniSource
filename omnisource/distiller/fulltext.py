"""Full-text and PDF-derived presentation signals."""
from __future__ import annotations

import io
import re

import requests

from .models import FullTextSignals

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_FIGURE_RE = re.compile(r"\b(fig\.?|figure)\s*\d*", re.IGNORECASE)
_TABLE_RE = re.compile(r"\btable\s*\d*", re.IGNORECASE)
_FORMULA_RE = re.compile(r"(\$[^$]+\$|\\begin\{equation\}|equation\s*:|[A-Za-z]\s*=\s*[^.\n]+)", re.IGNORECASE)
_SECTION_RE = re.compile(r"^\s*(abstract|introduction|method|approach|experiment|evaluation|result|conclusion)s?\b", re.IGNORECASE | re.MULTILINE)


class FullTextSignalExtractor:
    def from_text(self, text: str | None) -> FullTextSignals:
        text = text or ""
        word_count = len(_WORD_RE.findall(text))
        figure_count = len(_FIGURE_RE.findall(text))
        table_count = len(_TABLE_RE.findall(text))
        formula_count = len(_FORMULA_RE.findall(text))
        section_count = len(_SECTION_RE.findall(text))
        presentation_bonus = min(
            0.16,
            0.015 * min(figure_count, 4)
            + 0.015 * min(table_count, 4)
            + 0.02 * min(formula_count, 3)
            + 0.01 * min(section_count, 6)
            + (0.02 if word_count >= 1200 else 0.0),
        )
        return FullTextSignals(
            word_count=word_count,
            figure_count=figure_count,
            table_count=table_count,
            formula_count=formula_count,
            section_count=section_count,
            presentation_bonus=round(presentation_bonus, 4),
        )


class PDFFullTextFetcher:
    """Best-effort PDF text fetcher.

    The distiller can use PDF/full text when available, but it does not make PDF
    parsing a hard dependency for metadata-only or dry-run workflows.
    """

    def __init__(self, timeout: int = 30, reader_loader=None):
        self.timeout = timeout
        self.reader_loader = reader_loader

    def require_pdf_parser(self):
        if self.reader_loader is not None:
            try:
                return self.reader_loader()
            except ModuleNotFoundError as exc:
                raise RuntimeError("Install pypdf to enable --fetch-pdf-text PDF extraction") from exc
        try:
            from pypdf import PdfReader  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install pypdf to enable --fetch-pdf-text PDF extraction") from exc
        return PdfReader

    def fetch_text(self, pdf_url: str) -> str:
        PdfReader = self.require_pdf_parser()
        response = requests.get(pdf_url, timeout=self.timeout)
        response.raise_for_status()
        reader = PdfReader(io.BytesIO(response.content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)


def attach_full_text_signals(candidate, extractor: FullTextSignalExtractor | None = None):
    extractor = extractor or FullTextSignalExtractor()
    candidate.full_text_signals = extractor.from_text(candidate.full_text or candidate.abstract)
    return candidate
