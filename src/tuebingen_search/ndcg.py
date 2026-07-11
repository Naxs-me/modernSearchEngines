import math
from pathlib import Path

def dcg(relevances: list[float], k: int) -> float:
    return sum(
        rel / math.log2(i + 2)
        for i, rel in enumerate(relevances[:k])
    )

def ndcg(relevances: list[float], k: int = 10) -> float:
    ideal = sorted(relevances, reverse=True)
    denom = dcg(ideal, k)
    if denom == 0:
        return 0.0
    return dcg(relevances, k) / denom

def read_manual_qrels(path: str | Path) -> dict[str, dict[str, float]]:
    # Expected format: qid<TAB>url<TAB>relevance
    qrels = {}
    with Path(path).open(encoding="utf-8") as f:
        for line in f:
            qid, url, rel = line.rstrip("\n").split("\t")
            qrels.setdefault(qid, {})[url] = float(rel)
    return qrels
