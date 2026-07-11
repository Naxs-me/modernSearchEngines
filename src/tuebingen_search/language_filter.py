import re

ENGLISH_MARKERS = {
    "the", "and", "of", "to", "in", "for", "with", "from", "on", "is",
    "are", "this", "that", "you", "can", "visit", "information",
}

GERMAN_MARKERS = {
    "und", "der", "die", "das", "nicht", "mit", "für", "von", "ist",
    "sind", "im", "auf", "eine", "einen", "informationen",
}

def html_declares_english(html: str) -> bool:
    head = html[:1000].lower()
    return 'lang="en' in head or "lang='en" in head or "/en/" in head

def looks_english(text: str, html: str = "") -> bool:
    if html_declares_english(html):
        return True

    words = re.findall(r"[A-Za-zäöüÄÖÜß]+", (text or "").lower())
    if len(words) < 80:
        return False

    sample = words[:600]
    english = sum(1 for w in sample if w in ENGLISH_MARKERS)
    german = sum(1 for w in sample if w in GERMAN_MARKERS)

    # Conservative: only index likely English pages.
    return english >= max(4, german + 2)
