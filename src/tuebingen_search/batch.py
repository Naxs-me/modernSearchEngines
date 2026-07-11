import argparse
from pathlib import Path

from .search import SearchEngine

def read_queries(path: str | Path) -> list[tuple[str, str]]:
    queries = []
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split("\t", maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Bad query line, expected <qid> TAB <query>: {line!r}")
            queries.append((parts[0], parts[1]))
    return queries

def write_batch_results(engine: SearchEngine, queries_path: str | Path, output_path: str | Path, top_k: int = 100) -> None:
    queries = read_queries(queries_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as out:
        for qid, query in queries:
            results = engine.search(query, top_k=top_k)
            for result in results[:top_k]:
                out.write(
                    f"{qid}\t{result['rank']}\t{result['url']}\t{result['score']:.6f}\n"
                )

    print(f"Wrote {output_path}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default="data/queries.tsv")
    parser.add_argument("--index", default="data/index")
    parser.add_argument("--output", default="data/results.tsv")
    parser.add_argument("--top-k", type=int, default=100)
    args = parser.parse_args()

    engine = SearchEngine(args.index)
    write_batch_results(engine, args.queries, args.output, top_k=args.top_k)

if __name__ == "__main__":
    main()
