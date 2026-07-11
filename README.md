# Tübingen Search Tool

Starter implementation for the INFO4271 Modern Search Engines group project.

It contains:

- restartable polite crawler
- local JSONL document storage
- inverted index
- BM25 first-stage retrieval implemented in Python
- second-stage LSA semantic re-ranker
- diversity-aware ranking
- query result explanations
- Streamlit UI with category tabs
- batch output in the required TSV format

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For tests:

```bash
pip install pytest
pytest
```

## 2. Crawl pages

```bash
python -m tuebingen_search.crawler \
  --seeds data/seeds.txt \
  --output data/processed/documents.jsonl \
  --state-dir data/crawler_state \
  --max-pages 500 \
  --delay 0.5
```

The crawler saves:

```text
data/processed/documents.jsonl
data/crawler_state/frontier.json
data/crawler_state/visited.json
data/crawler_state/failed.json
```

You can stop and restart it. It will continue from the saved frontier.

## 3. Build the index

```bash
python -m tuebingen_search.indexer \
  --docs data/processed/documents.jsonl \
  --index data/index
```

This creates:

```text
data/index/index.json
data/index/docs.json
data/index/semantic_lsa.joblib
```

## 4. Search manually

```bash
python -m tuebingen_search.search \
  --index data/index \
  --query "tübingen attractions" \
  --top-k 10
```

## 5. Produce batch output

```bash
python -m tuebingen_search.batch \
  --queries data/queries.tsv \
  --index data/index \
  --output data/results.tsv \
  --top-k 100
```

Required output format:

```text
query_number<TAB>rank<TAB>document_url<TAB>relevance_score
```

Example:

```text
1    1    https://www.tuebingen.de/en/3521.html    0.725000
```

## 6. Run the UI

```bash
streamlit run src/tuebingen_search/ui_app.py -- --index data/index
```

UI features:

- result cards
- snippets
- result explanations
- category tabs
- score breakdown

## Retrieval pipeline

```text
Query
  ↓
BM25 first-stage retrieval, implemented manually
  ↓
Top 300 candidate documents
  ↓
LSA semantic re-ranking
  ↓
Title/heading overlap bonus
  ↓
Domain diversity / near-duplicate reduction
  ↓
Top 100 results
```

Final score:

```text
0.70 * normalized BM25
+ 0.20 * semantic LSA score
+ 0.10 * title/heading overlap
```

Then an MMR-like diversity step is applied.

## Team division

### Member 1: Crawler and corpus

Files:

```text
src/tuebingen_search/crawler.py
src/tuebingen_search/url_utils.py
src/tuebingen_search/language_filter.py
```

Tasks:

- improve seed URLs
- improve English filtering
- improve Tübingen relevance filtering
- remove duplicates
- collect corpus statistics

### Member 2: Indexing and BM25

Files:

```text
src/tuebingen_search/indexer.py
src/tuebingen_search/bm25.py
src/tuebingen_search/text.py
```

Tasks:

- verify BM25 correctness
- tune field boosts
- improve tokenization
- add tests

### Member 3: Innovation and evaluation

Files:

```text
src/tuebingen_search/reranker.py
src/tuebingen_search/batch.py
src/tuebingen_search/ndcg.py
```

Tasks:

- tune final score weights
- improve semantic re-ranking
- improve diversity ranking
- manually evaluate known queries

### Member 4: UI, report, integration

Files:

```text
src/tuebingen_search/ui_app.py
report/REPORT_OUTLINE.md
README.md
```

Tasks:

- improve Streamlit UI
- take screenshots
- write report
- prepare demo
- freeze final repository branch

## Important limitations

This is a strong starter, not the final submission.

Before submission, you should:

- crawl more high-quality English pages
- manually inspect top results
- tune ranking weights
- write tests for BM25
- check that `data/results.tsv` has exactly 100 results per query where possible
- freeze a final branch after the deadline
