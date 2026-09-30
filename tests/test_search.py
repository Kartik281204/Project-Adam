import math

from search import find_matches, parse_query, score_documents, search


def test_parse_query_splits_included_and_excluded_words():
    assert parse_query("Python -snakes Fun") == (["python", "fun"], ["snake"])


def test_parse_query_all_stop_words_gives_nothing():
    assert parse_query("the is a") == ([], [])


def test_and_search_needs_every_word(tiny_engine):
    assert find_matches(["python", "fun"], [], tiny_engine.index, "and") == {"doc1.txt", "doc2.txt"}
    assert find_matches(["cat", "python"], [], tiny_engine.index, "and") == set()


def test_or_search_needs_any_word(tiny_engine):
    assert find_matches(["cat", "python"], [], tiny_engine.index, "or") == {"doc1.txt", "doc2.txt", "doc3.txt"}


def test_exclude_removes_documents(tiny_engine):
    assert find_matches(["fun"], ["cat"], tiny_engine.index, "and") == {"doc1.txt", "doc2.txt"}


def test_unknown_words_and_empty_queries(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    assert search("zzzz", index, lengths) == []
    assert search("", index, lengths) == []
    assert search("the", index, lengths) == []
    assert search("python zzzz", index, lengths, mode="and") == []
    assert [d for d, _ in search("python zzzz", index, lengths, mode="or")] == ["doc2.txt", "doc1.txt"]


def test_queries_are_case_insensitive_and_stemmed(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    assert search("PYTHON", index, lengths) == search("python", index, lengths)
    assert {d for d, _ in search("learning", index, lengths)} == {"doc1.txt", "doc2.txt"}


def test_tfidf_matches_hand_calculation(tiny_engine):
    # "python" is in 2 of 3 docs, so idf = ln(3/2). doc2 has it 2 times in 5 words.
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    scores = score_documents(["python"], {"doc1.txt", "doc2.txt"}, index, lengths, "tfidf")
    expected_doc2 = (2 / 5) * math.log(3 / 2)                   # = 0.162
    assert math.isclose(scores["doc2.txt"], expected_doc2)


def test_word_in_every_document_has_zero_tfidf(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    scores = score_documents(["fun"], set(lengths), index, lengths, "tfidf")
    assert all(score == 0 for score in scores.values())


def test_bm25_gives_positive_scores_and_sorted_results(tiny_engine):
    ranked = search("python", tiny_engine.index, tiny_engine.doc_lengths, method="bm25")
    scores = [score for _, score in ranked]
    assert all(score > 0 for score in scores)
    assert scores == sorted(scores, reverse=True)


def test_rare_word_outranks_common_word(tiny_engine):
    # doc3 is the only one with "cat" (rare); every doc has "fun" (common).
    ranked = search("fun cat", tiny_engine.index, tiny_engine.doc_lengths, mode="or")
    assert ranked[0][0] == "doc3.txt"


def test_real_sample_data_finds_expected_documents():
    from engine import DATA_FOLDER
    from engine import SearchEngine
    from loader import load_text_files

    engine = SearchEngine()
    engine.build(load_text_files(DATA_FOLDER))
    both = [d for d, _ in search("python beginners", engine.index, engine.doc_lengths)]
    assert set(both) == {"python_programming.txt", "chess.txt"}
    assert [d for d, _ in search("snakes", engine.index, engine.doc_lengths)] == ["python_snakes.txt"]
    no_snakes = [d for d, _ in search("python -snake", engine.index, engine.doc_lengths)]
    assert "python_snakes.txt" not in no_snakes and "python_programming.txt" in no_snakes
