"""loader.py - Stage 1: read documents from disk into one dictionary.

Every document is a small dictionary:
    {"title": "...", "url": "...", "text": "..."}
and the whole collection (the corpus) is {doc_id: document}.
"""

import json
from pathlib import Path


def load_text_files(folder):
    """Read every .txt file in `folder`. The first line of a file is its title."""
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(
            f"Folder not found: {folder}. Are you running from the project folder?"
        )

    documents = {}
    for path in sorted(folder.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        lines = text.strip().splitlines()
        if lines:
            title = lines[0].strip()
        else:
            title = path.stem                      # empty file: use the file name
        documents[path.name] = {"title": title, "url": "", "text": text}
    return documents


def load_crawled_pages(path):
    """Read pages saved by the crawler (a JSON file). Returns {} if there is none."""
    path = Path(path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_all(data_folder, crawled_file):
    """Combine local text files and crawled pages into one corpus."""
    documents = load_text_files(data_folder)
    documents.update(load_crawled_pages(crawled_file))
    return documents
