"""storage.py - Stage 7: save the index to disk and load it back."""

import json


def save_index(path, documents, index, doc_lengths):
    """Write everything the engine needs to one JSON file."""
    data = {
        "documents": documents,
        "index": index,
        "doc_lengths": doc_lengths,
    }
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file)


def load_index(path):
    """Read the JSON file back. Returns (documents, index, doc_lengths)."""
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data["documents"], data["index"], data["doc_lengths"]
