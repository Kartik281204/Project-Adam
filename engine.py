"""engine.py - Stage 8: one object that ties every stage together."""

from pathlib import Path

from indexer import build_index
from loader import load_all
from search import parse_query, search
from snippets import make_snippet
from storage import load_index, save_index

# __file__ is this file's own path, so these paths work no matter where you run from.
BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
CRAWLED_FILE = BASE_DIR / "crawled" / "pages.json"
INDEX_FILE = BASE_DIR / "index.json"


class SearchEngine:
    """Holds the documents and the index, and answers searches."""

    def __init__(self):
        self.documents = {}      # {doc_id: {"title", "url", "text"}}
        self.index = {}          # {term: {doc_id: count}}
        self.doc_lengths = {}    # {doc_id: number of tokens}

    def build(self, documents):
        """Build a fresh index from a corpus."""
        self.documents = documents
        self.index, self.doc_lengths = build_index(documents)

    def save(self, path):
        save_index(path, self.documents, self.index, self.doc_lengths)

    def load(self, path):
        self.documents, self.index, self.doc_lengths = load_index(path)

    def stats(self):
        """A few numbers about the index."""
        total_tokens = sum(self.doc_lengths.values())
        count = len(self.doc_lengths)
        return {
            "documents": count,
            "terms": len(self.index),
            "average_length": total_tokens / count if count else 0,
        }

    def search(self, query, mode="and", method="bm25", top_k=10):
        """Search and return everything an interface needs to show the results."""
        ranked = search(query, self.index, self.doc_lengths, mode, method)
        terms, _excluded = parse_query(query)

        results = []
        for doc_id, score in ranked[:top_k]:
            document = self.documents[doc_id]
            results.append({
                "doc_id": doc_id,
                "title": document["title"],
                "url": document["url"],
                "score": score,
                "snippet": make_snippet(document["text"], terms),
            })
        return {"terms": terms, "total": len(ranked), "results": results}


def load_engine(rebuild=False, index_file=INDEX_FILE,
                data_folder=DATA_FOLDER, crawled_file=CRAWLED_FILE):
    """Load the saved index if there is one; otherwise build it (and save it)."""
    index_file = Path(index_file)
    engine = SearchEngine()

    if index_file.exists() and not rebuild:
        engine.load(index_file)
        return engine

    documents = load_all(data_folder, crawled_file)
    engine.build(documents)
    engine.save(index_file)
    return engine
