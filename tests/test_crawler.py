import functools
import http.server
import threading
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

import crawler

DEMO_SITE = Path(__file__).resolve().parent.parent / "demo_site"


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def demo_url():
    """Serve the demo_site folder on a free local port for the tests."""
    handler = functools.partial(QuietHandler, directory=str(DEMO_SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()


def test_clean_url():
    assert crawler.clean_url("https://x.com/page.html#top") == "https://x.com/page.html"
    assert crawler.clean_url("https://x.com/docs/index.html") == "https://x.com/docs/"


def test_same_domain():
    assert crawler.same_domain("https://a.com/x", "https://a.com/")
    assert not crawler.same_domain("https://b.com/x", "https://a.com/")


def test_extract_links_makes_urls_absolute_and_filters_junk():
    html = """
      <a href="/about">a</a> <a href="page2.html#top">b</a> <a href="https://other.com/x">c</a>
      <a href="photo.jpg">d</a> <a href="mailto:me@x.com">e</a> <a href="javascript:void(0)">f</a>
    """
    soup = BeautifulSoup(html, "html.parser")
    links = crawler.extract_links(soup, "https://site.com/dir/start.html")
    assert links == {"https://site.com/about", "https://site.com/dir/page2.html", "https://other.com/x"}


def test_extract_text_removes_scripts_and_styles():
    soup = BeautifulSoup("<p>Hello</p><script>var x = 1;</script><style>p{}</style><p>World</p>", "html.parser")
    assert crawler.extract_text(soup) == "Hello World"


def test_crawl_demo_site(demo_url):
    pages = crawler.crawl(demo_url, max_pages=20, delay=0)
    urls = set(pages)
    assert urls == {demo_url, demo_url + "tomatoes.html", demo_url + "herbs.html", demo_url + "compost.html"}
    assert not any("private" in url for url in urls)                # robots.txt obeyed
    assert "ignore this script text" not in pages[demo_url]["text"]  # scripts stripped
    assert pages[demo_url + "tomatoes.html"]["title"] == "How to Grow Tomatoes"


def test_crawl_respects_max_pages(demo_url):
    assert len(crawler.crawl(demo_url, max_pages=2, delay=0)) == 2


def test_crawl_survives_unreachable_site():
    assert crawler.crawl("http://127.0.0.1:9/", max_pages=3, delay=0) == {}


def test_save_pages_then_load_them(tmp_path):
    from loader import load_crawled_pages
    pages = {"http://x/": {"title": "T", "url": "http://x/", "text": "hello"}}
    path = tmp_path / "sub" / "pages.json"
    crawler.save_pages(pages, path)
    assert load_crawled_pages(path) == pages
