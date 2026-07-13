"""Proposal for the APIs"""

from dataclasses import dataclass

# type definition for document ID, could be changed
DocID = str | int

# 1. Crawling
def document_ids() -> list[DocID]:
    """Return List of all document IDs.

    Returns:
        list[DocID]: List of all document IDs
    """
    return NotImplemented


@dataclass
class Document:
    # fields could be changed
    id: DocID
    text: str
    length: int
    url: str
    title: str
    headings: list[str]
    ...

# alternativ approach: as a dictionary
example_document_dict: dict = {
    "id": "xy",
    "text": "Lorem ipsum",
    "length": 2
    # etc
}
# then
# Document = dict[str, str | int | list[str]]

def get_document(id: DocID) -> Document:
    """Get a preprocessed document by its ID.

    The returned document datastructure must include
     - the plain text
     - url
     - title
     - length

    Args:
        id (DocID): Document Id

    Returns:
        Document: Document wrapper datastructure
    """
    return NotImplemented



# 2. Indexing
def tokenize(text: str) -> list[str]:
    """Tokenize a text. Applicable to documents and queries.

    Args:
        text (str): A text to be tokenized

    Returns:
        list[str]: List of the tokens in the text
    """
    return NotImplemented


def inverse_document_frequency(token: str) -> float:
    """Returns the inverse document frequency of a token across the corpus.

    The IDF values should be pre-calculated.

    Args:
        token (str): A token.

    Returns:
        float: IDF of that token in regards to the corpus.
    """
    return NotImplemented


def get_documents_with_token(token: str) -> list[tuple[DocID, int]]:
    """Find all documents with a token occurs and the number of occurences.

    For each document the return list has a tuple with 
     - the document id
     - the number of occurances of this token in the document

    Args:
        token (str): A token.

    Returns:
        list[tuple[DocID, int]]: List of document-id token-occurances pairs.
    """
    return NotImplemented


# 3. First stage ranking
def get_first_stage_results(query: str, k: int) -> list[tuple[DocID, float]]:
    """Retrieve k best results for the query.

    Must use a classical approach. Maybe BM25.

    Returns the calculated relevance score as well. (Should it?)

    Discuss if `query` should be original query string or token list. 

    Args:
        query (str): The query. (As string or token list?)
        k (int): Number of results to retrieve

    Returns:
        list[tuple[DocID, float]]: Best documents and their relevance scores, sorted descending by relevance score
    """
    return NotImplemented


# 4. Second stage ranking
def rerank(query: str, documents: list[DocID]) -> list[tuple[DocID, float]]:
    """Rerank given documents in regards to the query.

    May use more advanced techniques.

    Maybe calculate a relevance score and return it with the document ids.

    Args:
        query (str): Query string
        documents (list[DocID]): list of relevant document ids

    Returns:
        list[tuple[DocID, float]]: Descending list of relevant document ids (and their relevance score)
    """
    return NotImplemented


# 5. Integration
def search(query: str, k: int) -> list[tuple[DocID, float]]:
    """Executes a search.

    Args:
        query (str): Query string
        k (int): Number of results to return

    Returns:
        list[tuple[DocID, float]]: Final ranking of best k documents and their relevance score
    """
    relevant_docs = [docid for docid, _ in get_first_stage_results(query, 500)]
    return rerank(query, relevant_docs)[:k]


# 6. User Interface
def start_ui() -> None:
    """Start the user interface.""" 
