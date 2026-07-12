# Meeting 12. July
# Ideas for implementation
## Crawling
 - Decide on target size of corpus
 - How to decide where to stop
 - How do we crawl the relevant documents (good seeds)

## Indexing
 - Common API
 - File Size and structure: 
   - JSON file should work for now
   - Efficency probably not an issue as we have 1 minute per query.
   - If needs better performance think about splitting index files, save more efficently
   - Rough estimate: 200 MB for 10 000 documents with JSON approach

## First-stage retrieval
 - Straight-forward, some classical approach is mandatory. Probably BM25

## Second-stage retrieval
 - Difficult
 - First do a classical approach
 - Then try other things
 - Measure quality of the results
 - Look for available tools
 - Maybe train a re-ranker

## User Interfacec
 - Web-page
 - Ideas for creative visualization:
   - Decision tree for topic domains
   - Spell check
   - Wikipedia 
   - Spider graph or Word Bubble to visualize topic
   - Similarity based spring loaded graph of documents
   - Summaries of documents
   