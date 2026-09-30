"""Shared test setup: a tiny corpus with answers we can work out by hand."""

import pytest

from engine import SearchEngine


@pytest.fixture
def tiny_documents():
    return {
        "doc1.txt": {"title": "Python fun", "url": "", "text": "Python is a fun language to learn."},
        "doc2.txt": {"title": "Fast Python", "url": "", "text": "Learning Python is fun and Python is fast."},
        "doc3.txt": {"title": "Cats", "url": "", "text": "Cats are fun animals."},
    }


@pytest.fixture
def tiny_engine(tiny_documents):
    engine = SearchEngine()
    engine.build(tiny_documents)
    return engine
