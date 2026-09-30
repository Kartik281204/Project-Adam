import pytest

from indexer import build_index
from loader import load_crawled_pages, load_text_files


def test_load_text_files_uses_first_line_as_title(tmp_path):
    (tmp_path / "a.txt").write_text("My Title\nSome body text.", encoding="utf-8")
    documents = load_text_files(tmp_path)
    assert documents["a.txt"]["title"] == "My Title"
    assert "Some body text." in documents["a.txt"]["text"]


def test_load_text_files_empty_file_uses_file_name(tmp_path):
    (tmp_path / "blank.txt").write_text("", encoding="utf-8")
    assert load_text_files(tmp_path)["blank.txt"]["title"] == "blank"


def test_load_text_files_ignores_other_extensions(tmp_path):
    (tmp_path / "notes.md").write_text("hello", encoding="utf-8")
    assert load_text_files(tmp_path) == {}


def test_load_text_files_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_files(tmp_path / "nope")


def test_load_crawled_pages_missing_file_gives_empty_dict(tmp_path):
    assert load_crawled_pages(tmp_path / "nope.json") == {}


def test_build_index_counts_and_lengths(tiny_documents):
    index, doc_lengths = build_index(tiny_documents)
    assert index["python"] == {"doc1.txt": 1, "doc2.txt": 2}
    assert index["cat"] == {"doc3.txt": 1}                     # "Cats" was stemmed to "cat"
    assert index["learn"] == {"doc1.txt": 1, "doc2.txt": 1}    # learn + learning
    assert doc_lengths == {"doc1.txt": 4, "doc2.txt": 5, "doc3.txt": 3}


def test_build_index_empty_corpus():
    assert build_index({}) == ({}, {})
