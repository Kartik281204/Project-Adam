import processor
from processor import process, remove_stop_words, stem, tokenize


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Hello, World!!") == ["hello", "world"]


def test_tokenize_handles_extra_spaces_and_empty_text():
    assert tokenize("   lots   of   spaces  ") == ["lots", "of", "spaces"]
    assert tokenize("") == []


def test_tokenize_joins_apostrophes_and_keeps_digits():
    assert tokenize("Don't stop, it’s T20!") == ["dont", "stop", "its", "t20"]


def test_tokenize_splits_on_dashes_and_slashes():
    assert tokenize("well-known/popular") == ["well", "known", "popular"]


def test_remove_stop_words():
    assert remove_stop_words(["python", "is", "a", "fun", "language"]) == ["python", "fun", "language"]


def test_stem_common_endings():
    assert stem("learning") == "learn"
    assert stem("learned") == "learn"
    assert stem("learns") == "learn"
    assert stem("running") == "run"
    assert stem("programming") == "program"
    assert stem("snakes") == "snake"


def test_stem_leaves_short_or_special_words_alone():
    assert stem("is") == "is"
    assert stem("bus") == "bus"
    assert stem("class") == "class"
    assert stem("focus") == "focus"
    assert stem("speed") == "speed"


def test_process_full_pipeline():
    assert process("The Quick brown FOX, jumped!") == ["quick", "brown", "fox", "jump"]


def test_process_without_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", False)
    assert process("Learning Python is fun") == ["learning", "python", "fun"]


def test_process_with_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", True)
    assert process("Learning Python is fun") == ["learn", "python", "fun"]
