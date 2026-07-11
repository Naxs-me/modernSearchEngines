from tuebingen_search.text import tokenize

def test_umlaut_normalization():
    assert tokenize("Tübingen")[0] == "tuebingen"

def test_stopword_removal():
    assert "the" not in tokenize("the castle of Tübingen")
    assert "castle" in tokenize("the castle of Tübingen")
