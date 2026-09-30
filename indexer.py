"""indexer.py - Stage 3: build the inverted index."""

from processor import process


def build_index(documents):
    """Build the inverted index from {doc_id: document}.

    Returns two things:
      index       {term: {doc_id: how many times the term appears in that doc}}
      doc_lengths {doc_id: number of tokens in that doc}
    """
    index = {}
    doc_lengths = {}

    for doc_id, document in documents.items():
        tokens = process(document["text"])
        doc_lengths[doc_id] = len(tokens)

        # Count the words of THIS document (a fresh dictionary each time).
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1

        # Copy the counts into the big index, word by word.
        for term, count in counts.items():
            if term not in index:
                index[term] = {}
            index[term][doc_id] = count

    return index, doc_lengths
