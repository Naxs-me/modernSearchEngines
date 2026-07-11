from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import joblib
import numpy as np

from .text import tokenize, short_text

def cosine_matrix_vector(matrix, vector):
    # LSA pipeline already normalizes. Clip to keep scores stable.
    sims = matrix @ vector.reshape(-1, 1)
    return np.asarray(sims).ravel().clip(-1, 1)

def minmax(values: list[float]) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return arr
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.ones_like(arr)
    return (arr - lo) / (hi - lo)

def domain_of(url: str) -> str:
    return urlparse(url).netloc.lower().replace("www.", "")

def title_heading_bonus(query: str, result: dict) -> float:
    q_terms = set(tokenize(query))
    title_terms = set(tokenize(result.get("title", "")))
    heading_terms = set(tokenize(" ".join(result.get("headings", []) or [])))
    if not q_terms:
        return 0.0

    title_overlap = len(q_terms & title_terms) / len(q_terms)
    heading_overlap = len(q_terms & heading_terms) / len(q_terms)
    return min(1.0, 0.7 * title_overlap + 0.3 * heading_overlap)

def categorize_result(result: dict) -> str:
    text = " ".join([
        result.get("title", ""),
        " ".join(result.get("headings", []) or []),
        result.get("meta_description", ""),
        result.get("text", "")[:500],
    ]).lower()

    categories = [
        ("Food & drinks", ["restaurant", "café", "cafe", "bar", "food", "drink", "wine", "beer", "breakfast"]),
        ("Attractions", ["attraction", "sight", "castle", "museum", "old town", "tour", "neckar", "garden"]),
        ("University", ["university", "faculty", "research", "study", "student", "campus"]),
        ("Events", ["event", "festival", "concert", "calendar", "exhibition"]),
        ("Accommodation", ["hotel", "hostel", "guesthouse", "accommodation", "stay"]),
        ("Transport", ["bus", "train", "parking", "station", "transport"]),
    ]

    for label, keywords in categories:
        if any(k in text for k in keywords):
            return label
    return "General"

def explain_result(query: str, result: dict, semantic_score: float | None = None) -> str:
    q_terms = set(tokenize(query))
    title_terms = set(tokenize(result.get("title", "")))
    heading_terms = set(tokenize(" ".join(result.get("headings", []) or [])))
    body_terms = set(tokenize(result.get("text", "")[:2000]))

    reasons = []
    title_matches = sorted(q_terms & title_terms)
    heading_matches = sorted(q_terms & heading_terms)
    body_matches = sorted(q_terms & body_terms)

    if title_matches:
        reasons.append("title matches: " + ", ".join(title_matches[:4]))
    if heading_matches:
        reasons.append("heading matches: " + ", ".join(heading_matches[:4]))
    if body_matches:
        reasons.append("body matches: " + ", ".join(body_matches[:4]))
    if semantic_score is not None and semantic_score > 0.35:
        reasons.append("high latent-semantic similarity")
    if not reasons:
        reasons.append("matched by BM25 term frequency")

    return "; ".join(reasons)

class ReRanker:
    def __init__(self, index_dir: str | Path):
        self.index_dir = Path(index_dir)
        self.semantic = None
        semantic_path = self.index_dir / "semantic_lsa.joblib"
        if semantic_path.exists():
            self.semantic = joblib.load(semantic_path)
            self.doc_id_to_row = {
                doc_id: i for i, doc_id in enumerate(self.semantic["doc_ids"])
            }

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 100,
        use_mmr: bool = True,
    ) -> list[dict]:
        if not candidates:
            return []

        bm25_norm = minmax([c.get("bm25_score", 0.0) for c in candidates])
        title_norm = np.asarray([title_heading_bonus(query, c) for c in candidates])

        semantic_scores = np.zeros(len(candidates), dtype=float)
        candidate_vectors = None

        if self.semantic is not None:
            q_vec = self.semantic["model"].transform([query])[0]
            rows = [self.doc_id_to_row.get(c["doc_id"]) for c in candidates]
            valid = [i for i, r in enumerate(rows) if r is not None]
            if valid:
                matrix = self.semantic["matrix"]
                candidate_vectors = np.zeros((len(candidates), matrix.shape[1]), dtype=float)
                for i, row in enumerate(rows):
                    if row is not None:
                        candidate_vectors[i] = matrix[row]
                semantic_scores = cosine_matrix_vector(candidate_vectors, q_vec)
                semantic_scores = minmax(semantic_scores.tolist())

        combined = (
            0.70 * bm25_norm
            + 0.20 * semantic_scores
            + 0.10 * title_norm
        )

        for i, c in enumerate(candidates):
            c["semantic_score"] = float(semantic_scores[i])
            c["title_heading_score"] = float(title_norm[i])
            c["score"] = float(combined[i])
            c["category"] = categorize_result(c)
            c["explanation"] = explain_result(query, c, c["semantic_score"])

        if not use_mmr or len(candidates) <= top_k:
            return sorted(candidates, key=lambda x: x["score"], reverse=True)[:top_k]

        return self._mmr_select(candidates, candidate_vectors, top_k)

    def _mmr_select(self, candidates: list[dict], vectors, top_k: int, lambda_: float = 0.85) -> list[dict]:
        selected = []
        remaining = list(range(len(candidates)))
        domains_seen = {}

        while remaining and len(selected) < top_k:
            best_idx = None
            best_score = -1e9

            for idx in remaining:
                c = candidates[idx]
                relevance = c["score"]
                domain_penalty = 0.04 * domains_seen.get(domain_of(c["url"]), 0)

                similarity_penalty = 0.0
                if vectors is not None and selected:
                    selected_indices = [candidates.index(s) for s in selected]
                    sims = vectors[selected_indices] @ vectors[idx]
                    similarity_penalty = max(0.0, float(np.max(sims))) * 0.12

                mmr_score = lambda_ * relevance - (1 - lambda_) * similarity_penalty - domain_penalty

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            chosen = candidates[best_idx]
            selected.append(chosen)
            domains_seen[domain_of(chosen["url"])] = domains_seen.get(domain_of(chosen["url"]), 0) + 1
            remaining.remove(best_idx)

        # Reassign ranks according to selection order.
        return selected
