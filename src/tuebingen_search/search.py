import argparse
from pathlib import Path

from .bm25 import BM25Index
from .reranker import ReRanker
from .text import make_snippet, tokenize

class SearchEngine:
    def __init__(self, index_dir: str | Path):
        self.index_dir = Path(index_dir)
        self.bm25 = BM25Index(self.index_dir)
        self.reranker = ReRanker(self.index_dir)

    def search(self, query: str, top_k: int = 100, first_stage_k: int = 300) -> list[dict]:
        candidates = self.bm25.score_query(query, top_k=first_stage_k)
        results = self.reranker.rerank(query, candidates, top_k=top_k, use_mmr=True)
        q_terms = tokenize(query)

        for rank, r in enumerate(results, start=1):
            r["rank"] = rank
            r["snippet"] = make_snippet(r.get("text", ""), q_terms)
        return results

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--index", default="data/index")
    parser.add_argument("--top-k", type=int, default=10)
    args = parser.parse_args()

    engine = SearchEngine(args.index)
    for r in engine.search(args.query, top_k=args.top_k):
        print(f"{r['rank']:>2}. {r['title'] or '(no title)'}")
        print(f"    {r['url']}")
        print(f"    score={r['score']:.4f} bm25={r['bm25_score']:.4f} category={r['category']}")
        print(f"    why: {r['explanation']}")
        print(f"    {r['snippet']}")
        print()

if __name__ == "__main__":
    main()
