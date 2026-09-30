import pytest

from app import create_app


@pytest.fixture
def client(tiny_engine):
    return create_app(tiny_engine).test_client()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Search 3 documents" in response.get_data(as_text=True)


def test_search_shows_results_with_highlights(client):
    html = client.get("/search?q=python").get_data(as_text=True)
    assert "2 results for" in html
    assert "<mark>Python</mark>" in html


def test_search_with_no_results(client):
    html = client.get("/search?q=zzzz").get_data(as_text=True)
    assert "No results for" in html


def test_empty_query_asks_for_input(client):
    assert "Type something to search" in client.get("/search").get_data(as_text=True)


def test_or_mode_finds_more(client):
    assert "3 results" in client.get("/search?q=python+cats&mode=or").get_data(as_text=True)


def test_user_input_is_escaped(client):
    html = client.get("/search?q=<script>alert(1)</script>").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html


def test_document_page_and_404(client):
    assert client.get("/doc/doc3.txt").status_code == 200
    assert client.get("/doc/missing.txt").status_code == 404
