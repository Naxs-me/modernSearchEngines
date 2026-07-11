import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import joblib
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer

from .text import tokenize, short_text

FIELD_BOOSTS = {
    "title": 3.0,
    "headings": 2.0,
    "meta_description": 1.5,
    "text": 1.0,
    "url": 1.2,
}

def load_docs(path: str | Path) -> list[dict]:
    docs = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                docs.append(json.loads(line))
    return docs

def count_weighted_terms(doc: dict) -> Counter:
    counts = Counter()
    fields = {
        "title": doc.get("title", ""),
        "headings": " ".join(doc.get("headings", []) or []),
        "meta_description": doc.get("meta_description", ""),
        "text": doc.get("text", ""),
        "url": doc.get("url", ""),
    }
    for field, value in fields.items():
        boost = FIELD_BOOSTS.get(field, 1.0)
        for term, c in Counter(tokenize(value)).items():
            counts[term] += c * boost
    return counts

def build_index(docs: list[dict], index_dir: str | Path) -> None:
    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)

    postings: dict[str, dict[str, float]] = defaultdict(dict)
    doc_lengths: dict[str, int] = {}
    doc_store: dict[str, dict] = {}

    seen_urls = set()
    unique_docs = []
    for doc in docs:
        if doc.get("url") in seen_urls:
            continue
        seen_urls.add(doc.get("url"))
        unique_docs.append(doc)

    for doc in unique_docs:
        doc_id = doc["doc_id"]
        doc_store[doc_id] = {
            "doc_id": doc_id,
            "url": doc.get("url", ""),
            "title": doc.get("title", ""),
            "meta_description": doc.get("meta_description", ""),
            "headings": doc.get("headings", []) or [],
            "text": doc.get("text", ""),
        }

        body_tokens = tokenize(" ".join([
            doc.get("title", ""),
            " ".join(doc.get("headings", []) or []),
            doc.get("text", ""),
        ]))
        doc_lengths[doc_id] = max(1, len(body_tokens))

        counts = count_weighted_terms(doc)
        for term, tf in counts.items():
            postings[term][doc_id] = float(tf)

    df = {term: len(doc_map) for term, doc_map in postings.items()}
    avgdl = sum(doc_lengths.values()) / max(1, len(doc_lengths))

    index = {
        "num_docs": len(doc_store),
        "avgdl": avgdl,
        "doc_lengths": doc_lengths,
        "df": df,
        "postings": postings,
        "field_boosts": FIELD_BOOSTS,
    }

    (index_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    (index_dir / "docs.json").write_text(json.dumps(doc_store, ensure_ascii=False), encoding="utf-8")

    build_semantic_index(list(doc_store.values()), index_dir)

    print(f"Indexed {len(doc_store)} documents.")
    print(f"Vocabulary size: {len(postings)}")
    print(f"Average document length: {avgdl:.2f}")

def build_semantic_index(docs: list[dict], index_dir: Path) -> None:
    texts = [short_text(d) for d in docs]
    doc_ids = [d["doc_id"] for d in docs]

    if len(docs) < 3:
        print("Semantic index skipped: need at least 3 documents.")
        return

    n_components = min(96, max(2, len(docs) - 1))
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        max_features=20000,
        ngram_range=(1, 2),
        min_df=1,
    )

    # LSA: TF-IDF -> low-dimensional latent space -> normalize.
    model = make_pipeline(
        vectorizer,
        TruncatedSVD(n_components=n_components, random_state=42),
        Normalizer(copy=False),
    )

    matrix = model.fit_transform(texts)

    joblib.dump(
        {
            "doc_ids": doc_ids,
            "model": model,
            "matrix": matrix,
        },
        index_dir / "semantic_lsa.joblib",
    )
    print(f"Built semantic LSA re-ranker with {n_components} dimensions.")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="data/processed/documents.jsonl")
    parser.add_argument("--index", default="data/index")
    args = parser.parse_args()

    docs = load_docs(args.docs)
    build_index(docs, args.index)

if __name__ == "__main__":
    main()
