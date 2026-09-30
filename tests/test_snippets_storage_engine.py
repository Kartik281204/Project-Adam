from engine import SearchEngine, load_engine
from snippets import highlight, highlight_parts, make_snippet


def test_snippet_is_centred_on_the_first_match():
    text = "word " * 50 + "needle " + "word " * 50
    snippet = make_snippet(text, ["needle"], width=60)
    assert "needle" in snippet
    assert snippet.startswith("...") and snippet.endswith("...")
    assert len(snippet) <= 66


def test_snippet_without_match_uses_the_beginning():
    assert make_snippet("Short text here.", ["zzz"]) == "Short text here."


def test_highlight_wraps_whole_words_starting_with_a_term():
    assert highlight("Learning is fun to learn", ["learn"]) == "**Learning** is fun to **learn**"


def test_highlight_without_terms_changes_nothing():
    assert highlight("Nothing to see", []) == "Nothing to see"
    assert highlight_parts("Nothing to see", []) == [("Nothing to see", False)]


def test_highlight_parts_flags_matches():
    assert highlight_parts("a cat sat", ["cat"]) == [("a ", False), ("cat", True), (" sat", False)]


def test_save_and_load_round_trip(tiny_engine, tmp_path):
    path = tmp_path / "index.json"
    tiny_engine.save(path)
    loaded = SearchEngine()
    loaded.load(path)
    assert loaded.index == tiny_engine.index
    assert loaded.doc_lengths == tiny_engine.doc_lengths
    assert loaded.documents == tiny_engine.documents


def test_load_engine_builds_then_reuses_saved_index(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_text("Apples\nApples are red fruit.", encoding="utf-8")
    index_file = tmp_path / "index.json"
    kwargs = dict(index_file=index_file, data_folder=data, crawled_file=tmp_path / "none.json")

    first = load_engine(**kwargs)
    assert index_file.exists()

    (data / "b.txt").write_text("Bananas\nBananas are yellow.", encoding="utf-8")
    assert load_engine(**kwargs).stats()["documents"] == 1          # loaded the saved index
    assert load_engine(rebuild=True, **kwargs).stats()["documents"] == 2   # rebuilt


def test_engine_search_returns_everything_an_interface_needs(tiny_engine):
    response = tiny_engine.search("python fun")
    assert response["terms"] == ["python", "fun"]
    assert response["total"] == 2
    top = response["results"][0]
    assert set(top) == {"doc_id", "title", "url", "score", "snippet"}


def test_engine_search_top_k_limits_results_but_not_total(tiny_engine):
    response = tiny_engine.search("fun", mode="or", top_k=1)
    assert len(response["results"]) == 1
    assert response["total"] == 3


def test_stats(tiny_engine):
    stats = tiny_engine.stats()
    assert stats["documents"] == 3
    assert stats["terms"] > 0
    assert SearchEngine().stats() == {"documents": 0, "terms": 0, "average_length": 0}
