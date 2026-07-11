# 4-page report outline

## Page 1: Problem and architecture

- Goal: English search engine for Tübingen-related content.
- Architecture diagram:
  - crawler
  - document store
  - inverted index
  - BM25 retrieval
  - semantic/diversity re-ranker
  - UI and batch output
- Corpus statistics:
  - number of crawled URLs
  - number of indexed English documents
  - top domains
  - average document length

## Page 2: Crawling, preprocessing, and BM25

- Seed URLs
- Restartable frontier
- English filtering
- Tübingen relevance filtering
- Tokenization
- Umlaut normalization
- BM25 formula
- Field boosts:
  - title
  - headings
  - meta description
  - body
  - URL

## Page 3: Retrieval innovation

- First stage: BM25 implemented ourselves.
- Second stage: LSA semantic re-ranking.
- Score combination:
  - 0.70 normalized BM25
  - 0.20 semantic LSA score
  - 0.10 title/heading overlap
- Diversity step:
  - penalize repeated domains
  - reduce near-duplicate clusters
- Explain why this helps over BM25 alone.

## Page 4: UI, evaluation, and limitations

- UI screenshots
- Result explanation feature
- Category tabs
- Batch TSV output format
- Runtime per query
- Manual evaluation on:
  - tübingen attractions
  - food and drinks
- Limitations and future improvements
