import re
from collections import Counter
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?", re.IGNORECASE)

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "he", "in", "is", "it", "its", "of", "on", "or",
    "that", "the", "this", "to", "was", "were", "will", "with", "you",
    "your", "we", "our", "their", "they", "there", "here", "about",
}

def normalize_umlauts(text: str) -> str:
    # Use German transliterations so Tübingen and Tuebingen match.
    return (
        text.replace("Ä", "Ae").replace("Ö", "Oe").replace("Ü", "Ue")
            .replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
            .replace("ß", "ss")
    )

def tokenize(text: str, remove_stopwords: bool = True) -> list[str]:
    text = normalize_umlauts(text or "").lower()
    tokens = TOKEN_RE.findall(text)
    if remove_stopwords:
        tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return tokens

def term_counts(text: str) -> Counter:
    return Counter(tokenize(text))

def short_text(doc: dict, max_chars: int = 2500) -> str:
    parts = [
        doc.get("title", ""),
        " ".join(doc.get("headings", []) or []),
        doc.get("meta_description", ""),
        doc.get("text", ""),
    ]
    return " ".join(p for p in parts if p)[:max_chars]

def make_snippet(text: str, query_terms: Iterable[str], max_len: int = 260) -> str:
    text = " ".join((text or "").split())
    if not text:
        return ""
    lower = normalize_umlauts(text).lower()
    positions = []
    for term in query_terms:
        term = normalize_umlauts(term).lower()
        idx = lower.find(term)
        if idx >= 0:
            positions.append(idx)
    start = max(0, min(positions) - 80) if positions else 0
    snippet = text[start:start + max_len]
    if start > 0:
        snippet = "..." + snippet
    if start + max_len < len(text):
        snippet += "..."
    return snippet
