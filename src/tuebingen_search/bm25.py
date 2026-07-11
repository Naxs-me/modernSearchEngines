import json
import math
from collections import defaultdict
from pathlib import Path

from .text import tokenize

class BM25Index:
    def __init__(self, index_dir: str | Path, k1: float = 1.2, b: float = 0.75):
        index_dir = Path(index_dir)
        self.index = json.loads((index_dir / "index.json").read_text(encoding="utf-8"))
        self.docs = json.loads((index_dir / "docs.json").read_text(encoding="utf-8"))
        self.k1 = k1
        self.b = b
        self.N = self.index["num_docs"]
        self.avgdl = self.index["avgdl"]
        self.doc_lengths = self.index["doc_lengths"]
        self.df = self.index["df"]
        self.postings = self.index["postings"]

    def idf(self, term: str) -> float:
        df = self.df.get(term, 0)
        # BM25+ style smoothed IDF.
        return math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))

    def score_query(self, query: str, top_k: int = 100) -> list[dict]:
        terms = tokenize(query)
        if not terms:
            return []

        scores = defaultdict(float)

        for term in terms:
            if term not in self.postings:
                continue
            idf = self.idf(term)
            for doc_id, tf in self.postings[term].items():
                dl = self.doc_lengths.get(doc_id, self.avgdl)
                denom = tf + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl)
                scores[doc_id] += idf * ((tf * (self.k1 + 1.0)) / denom)

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for doc_id, score in ranked:
            doc = self.docs[doc_id]
            results.append({
                "doc_id": doc_id,
                "url": doc["url"],
                "title": doc.get("title", ""),
                "text": doc.get("text", ""),
                "headings": doc.get("headings", []),
                "meta_description": doc.get("meta_description", ""),
                "bm25_score": float(score),
            })
        return results
