# MiniSearch

A small but complete search engine written from scratch in Python, built as a learning project.

**To learn how it's built, read `BUILD_ALONG.md`** (a step-by-step tutorial with the code explained line by line).

## Quick start

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

python cli.py                       # search in the terminal
python app.py                       # web interface at http://127.0.0.1:5000
python -m pytest -q                 # run the 54 tests
```

## Crawl the practice website

```bash
python -m http.server 8000 --directory demo_site      # terminal 1
python crawler.py http://localhost:8000/ 10 0         # terminal 2
python cli.py --rebuild                               # include the crawled pages
```

When crawling real websites, keep the default 1-second delay, obey robots.txt (the crawler does), and only crawl sites you may crawl.

## Files

| File | Job |
|---|---|
| `loader.py` | read documents (text files, crawled pages) |
| `processor.py` | tokenise, remove stop words, stem |
| `indexer.py` | build the inverted index |
| `search.py` | AND / OR / NOT matching; TF-IDF and BM25 ranking |
| `snippets.py` | excerpts with highlighted words |
| `storage.py` | save / load the index as JSON |
| `engine.py` | the `SearchEngine` class that ties it together |
| `cli.py` | terminal interface |
| `crawler.py` | polite web crawler |
| `app.py` + `templates/` | Flask web interface |
| `tests/` | pytest test suite |

The first line of each `.txt` file in `data/` is its title. If you change the documents or `processor.py`, delete `index.json` (or run `python cli.py --rebuild`).
