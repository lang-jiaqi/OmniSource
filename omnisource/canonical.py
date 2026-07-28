"""Canonical-id resolution for cross-source dedup (dedup Layer 2).

Different sources wrap the same underlying artifact in different ids: a tweet,
a blog post, and the arXiv listing of one paper all look distinct. But the
tweet/blog usually *links* the canonical artifact (arXiv / GitHub / HF / DOI).
We extract that link and rewrite the signal's id to the canonical form, so the
merge step collapses them — and social mentions become buzz on the real item
instead of separate noise.
"""
from __future__ import annotations

import re

from .models import Signal

# arXiv id like 2606.21638 (optionally vN), from abs/pdf URLs, HF papers, or bare.
_ARXIV = re.compile(
    r"(?:arxiv\.org/(?:abs|pdf)/|huggingface\.co/papers/|ar5iv\.org/abs/|arxiv:)\s*"
    r"(\d{4}\.\d{4,5})(?:v\d+)?",
    re.IGNORECASE,
)
# github.com/owner/repo (stop before extra path segments)
_GITHUB = re.compile(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", re.IGNORECASE)
# DOI
_DOI = re.compile(r"(?:doi\.org/|doi:)\s*(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", re.IGNORECASE)

_GITHUB_TRAILING = re.compile(r"\.git$|[).,]+$")


def canonical_id(text: str) -> str | None:
    """Return a canonical id for the first artifact linked in text, or None."""
    m = _ARXIV.search(text)
    if m:
        return m.group(1)  # bare arXiv id matches ArxivSource / HFPapersSource
    m = _GITHUB.search(text)
    if m:
        repo = _GITHUB_TRAILING.sub("", m.group(1))
        # skip non-repo github paths
        if repo.split("/")[1] not in {"blog", "about", "features", "topics", "sponsors"}:
            return f"github:{repo}"
    m = _DOI.search(text)
    if m:
        return f"doi:{m.group(1).rstrip('.')}"
    return None


def canonicalize(signal: Signal) -> None:
    """Rewrite a signal's id to the canonical artifact it points to, if any.
    Papers/repos already use canonical ids; this mainly remaps blogs/social."""
    if signal.type in ("paper", "repo"):
        return  # already canonical from their source
    found = canonical_id(f"{signal.url} {signal.summary}")
    if found:
        signal.id = found
