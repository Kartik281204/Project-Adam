"""crawler.py - Stage 9: collect web pages by following links.

Run:  python crawler.py <seed_url> [max_pages] [delay_seconds]
e.g.  python crawler.py https://quotes.toscrape.com 20

Be polite: keep the delay at 1 second or more for real websites.
"""

import json
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from engine import CRAWLED_FILE

USER_AGENT = "MiniSearchBot/0.1 (a learning project)"
SKIP_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".svg", ".pdf", ".zip",
                   ".css", ".js", ".ico", ".mp4", ".mp3")


def clean_url(url):
    """Give every page ONE canonical address, so we never index it twice.

    page.html#top  ->  page.html       (drop the #fragment)
    /docs/index.html  ->  /docs/       (index.html is the folder's default page)
    """
    url, _fragment = urldefrag(url)
    if url.endswith("/index.html"):
        url = url[: -len("index.html")]
    return url


def same_domain(url, seed_url):
    """True if both URLs are on the same website."""
    return urlparse(url).netloc == urlparse(seed_url).netloc


def extract_links(soup, page_url):
    """Find every link on a page and return them as clean, absolute URLs."""
    links = set()
    for tag in soup.find_all("a", href=True):
        absolute = clean_url(urljoin(page_url, tag["href"]))
        if not absolute.startswith(("http://", "https://")):
            continue                                   # skip mailto:, javascript:, ...
        if urlparse(absolute).path.lower().endswith(SKIP_EXTENSIONS):
            continue                                   # skip images, PDFs, ...
        links.add(absolute)
    return links


def extract_text(soup):
    """Return the visible text of a page as one tidy string."""
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()                                # remove invisible junk
    return " ".join(soup.get_text(separator=" ").split())


def extract_title(soup, fallback):
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return fallback


def load_robots(seed_url):
    """Download and parse the site's robots.txt rules."""
    parts = urlparse(seed_url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    parser = RobotFileParser()
    try:
        response = requests.get(robots_url, timeout=10,
                                headers={"User-Agent": USER_AGENT})
    except requests.RequestException:
        parser.parse([])                               # could not fetch: no rules
        return parser

    if response.status_code == 200:
        parser.parse(response.text.splitlines())
    elif response.status_code in (401, 403):
        parser.parse(["User-agent: *", "Disallow: /"])  # site says keep out
    else:
        parser.parse([])                               # no robots.txt: no rules
    return parser


def fetch(url):
    """Download a page. Returns the response, or None if anything went wrong."""
    try:
        return requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
    except requests.RequestException as error:
        print(f"  could not fetch {url}: {error}")
        return None


def crawl(seed_url, max_pages=20, delay=1.0):
    """Visit pages breadth-first, starting at seed_url. Returns {url: document}."""
    robots = load_robots(seed_url)
    seed_url = clean_url(seed_url)

    queue = deque([seed_url])       # URLs waiting to be visited
    seen = {seed_url}               # every URL we have ever added to the queue
    pages = {}                      # results: {url: {"title", "url", "text"}}

    while queue and len(pages) < max_pages:
        url = queue.popleft()

        if not robots.can_fetch(USER_AGENT, url):
            print(f"  skipped (robots.txt): {url}")
            continue

        response = fetch(url)
        time.sleep(delay)                              # be polite: pause between requests
        if response is None:
            continue

        content_type = response.headers.get("Content-Type", "")
        if response.status_code != 200 or "text/html" not in content_type:
            print(f"  skipped (status {response.status_code}, {content_type or 'unknown type'}): {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        links = extract_links(soup, url)               # links first, before text cleaning
        pages[url] = {
            "title": extract_title(soup, url),
            "url": url,
            "text": extract_text(soup),
        }
        print(f"  [{len(pages)}/{max_pages}] {url}")

        for link in sorted(links):
            if same_domain(link, seed_url) and link not in seen:
                seen.add(link)
                queue.append(link)

    return pages


def save_pages(pages, path=CRAWLED_FILE):
    """Write the crawled pages to a JSON file for the loader to pick up."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(pages, file, indent=2)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    seed_url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    delay = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

    print(f"Crawling {seed_url} (max {max_pages} pages, {delay}s delay)")
    pages = crawl(seed_url, max_pages, delay)
    save_pages(pages)
    print(f"Saved {len(pages)} pages to {CRAWLED_FILE}")
    print("Now rebuild the index:  python cli.py --rebuild")


if __name__ == "__main__":
    main()
