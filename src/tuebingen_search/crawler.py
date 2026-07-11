import argparse
import hashlib
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

from .language_filter import looks_english
from .url_utils import canonicalize_url, looks_tuebingen_related, same_or_related_domain

HEADERS = {
    "User-Agent": "ModernSearchEnginesCourseCrawler/0.1 (+student project; polite crawler)"
}

def load_lines(path: str | Path) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

def read_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def extract_page(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        tag.decompose()

    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    meta = ""
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        meta = desc.get("content", "").strip()

    headings = [
        h.get_text(" ", strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])
        if h.get_text(" ", strip=True)
    ]

    # Try main/article first, otherwise full body.
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text(" ", strip=True)
    text = " ".join(text.split())

    links = []
    for a in soup.find_all("a", href=True):
        href = canonicalize_url(a["href"], base_url=url)
        if href:
            links.append(href)

    return {
        "url": url,
        "title": title,
        "meta_description": meta,
        "headings": headings[:30],
        "text": text,
        "links": sorted(set(links)),
    }

def make_doc_id(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]

def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def crawl(
    seeds: Iterable[str],
    output_docs: str | Path,
    state_dir: str | Path,
    max_pages: int = 500,
    delay: float = 0.5,
    timeout: float = 12,
) -> None:
    output_docs = Path(output_docs)
    state_dir = Path(state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)

    frontier_path = state_dir / "frontier.json"
    visited_path = state_dir / "visited.json"
    failed_path = state_dir / "failed.json"

    if frontier_path.exists():
        frontier = deque(read_json(frontier_path, []))
    else:
        frontier = deque(canonicalize_url(s) for s in seeds)
        frontier = deque(u for u in frontier if u)

    visited = set(read_json(visited_path, []))
    failed = set(read_json(failed_path, []))

    indexed_count = 0

    while frontier and indexed_count < max_pages:
        url = frontier.popleft()

        if not url or url in visited or url in failed:
            continue

        if not same_or_related_domain(url) and not looks_tuebingen_related(url):
            continue

        print(f"[crawl] {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            if response.status_code >= 400:
                failed.add(url)
                continue

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                failed.add(url)
                continue

            html = response.text
            page = extract_page(html, url)

            if len(page["text"]) < 400:
                visited.add(url)
                continue

            full_text_for_filters = " ".join([
                page["title"],
                page["meta_description"],
                " ".join(page["headings"]),
                page["text"][:3000],
            ])

            if not looks_english(full_text_for_filters, html):
                visited.add(url)
                continue

            if not looks_tuebingen_related(url, full_text_for_filters):
                visited.add(url)
                continue

            doc = {
                "doc_id": make_doc_id(url),
                "url": url,
                "title": page["title"],
                "meta_description": page["meta_description"],
                "headings": page["headings"],
                "text": page["text"],
                "crawl_time": datetime.now(timezone.utc).isoformat(),
            }
            append_jsonl(output_docs, doc)
            indexed_count += 1
            visited.add(url)

            for link in page["links"]:
                if link not in visited and link not in failed and looks_tuebingen_related(link):
                    frontier.append(link)

        except Exception as exc:
            print(f"[crawl:failed] {url}: {exc}")
            failed.add(url)

        write_json(frontier_path, list(dict.fromkeys(frontier)))
        write_json(visited_path, sorted(visited))
        write_json(failed_path, sorted(failed))

        time.sleep(delay)

    print(f"Done. Added {indexed_count} new documents.")
    print(f"Frontier left: {len(frontier)} | Visited: {len(visited)} | Failed: {len(failed)}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="data/seeds.txt")
    parser.add_argument("--output", default="data/processed/documents.jsonl")
    parser.add_argument("--state-dir", default="data/crawler_state")
    parser.add_argument("--max-pages", type=int, default=500)
    parser.add_argument("--delay", type=float, default=0.5)
    args = parser.parse_args()

    crawl(
        seeds=load_lines(args.seeds),
        output_docs=args.output,
        state_dir=args.state_dir,
        max_pages=args.max_pages,
        delay=args.delay,
    )

if __name__ == "__main__":
    main()
