from urllib.parse import urljoin, urlparse, urlunparse
import re

SKIP_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
    ".mp4", ".mp3", ".avi", ".mov", ".zip", ".tar", ".gz",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
}

def canonicalize_url(url: str, base_url: str | None = None) -> str | None:
    if base_url:
        url = urljoin(base_url, url)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None

    path = parsed.path or "/"
    lower_path = path.lower()
    if any(lower_path.endswith(ext) for ext in SKIP_EXTENSIONS):
        return None

    # Remove fragments and most query parameters to reduce duplicates.
    cleaned = parsed._replace(fragment="", query="")
    normalized = urlunparse(cleaned)

    # Remove trailing slash except domain root.
    if normalized.endswith("/") and len(path) > 1:
        normalized = normalized[:-1]
    return normalized

def same_or_related_domain(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    useful_domains = [
        "tuebingen.de",
        "tuebingen-info.de",
        "uni-tuebingen.de",
        "unimuseum.uni-tuebingen.de",
        "stadtmuseum-tuebingen.de",
        "neckar",
        "baden-wuerttemberg",
    ]
    return any(d in host for d in useful_domains)

def looks_tuebingen_related(url: str, text: str = "") -> bool:
    haystack = f"{url} {text}".lower()
    patterns = [
        "tuebingen", "tübingen", "hohentuebingen", "hohentübingen",
        "neckar", "baden-wuerttemberg", "baden württemberg",
        "university of tuebingen", "universität tübingen",
    ]
    return any(p in haystack for p in patterns)
