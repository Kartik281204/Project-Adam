"""search.py - Stages 4 and 5: find matching documents, then rank them."""

import math

from processor import process

# BM25 settings. These are the standard defaults.
K1 = 1.5    # how quickly extra repeats of a word stop helping
B = 0.75    # how strongly document length is corrected (0 = ignore, 1 = fully)


def parse_query(query):
    """Split a raw query into (words to include, words to exclude).

    A word starting with '-' is excluded:  "python -snake"
    """
    include_text = []
    exclude_text = []
    for part in query.split():
        if part.startswith("-") and len(part) > 1:
            exclude_text.append(part[1:])
        else:
            include_text.append(part)

    # Queries go through the SAME pipeline as documents.
    include = process(" ".join(include_text))
    exclude = process(" ".join(exclude_text))
    return include, exclude


def docs_for_term(term, index):
    """The set of document ids that contain `term` (empty set if unknown)."""
    return set(index.get(term, {}))


def find_matches(include, exclude, index, mode="and"):
    """Return the set of document ids that match the query.

    mode "and": a document must contain ALL the words.
    mode "or":  a document must contain AT LEAST ONE of the words.
    """
    if not include:
        return set()

    matches = docs_for_term(include[0], index)
    for term in include[1:]:
        term_docs = docs_for_term(term, index)
        if mode == "and":
            matches = matches & term_docs      # keep only the overlap
        else:
            matches = matches | term_docs      # add everything

    for term in exclude:
        matches = matches - docs_for_term(term, index)   # remove unwanted docs
    return matches


def score_documents(terms, matches, index, doc_lengths, method="bm25"):
    """Give every matching document a relevance score. Returns {doc_id: score}."""
    scores = {doc_id: 0.0 for doc_id in matches}
    if not matches:
        return scores

    total_docs = len(doc_lengths)
    average_length = sum(doc_lengths.values()) / total_docs

    for term in terms:
        postings = index.get(term)
        if not postings:
            continue                                   # unknown word: skip it
        doc_freq = len(postings)                       # how many docs contain it

        if method == "tfidf":
            idf = math.log(total_docs / doc_freq)
        else:
            idf = math.log(1 + (total_docs - doc_freq + 0.5) / (doc_freq + 0.5))

        for doc_id in matches:
            count = postings.get(doc_id, 0)
            if count == 0:
                continue
            length = doc_lengths[doc_id]

            if method == "tfidf":
                scores[doc_id] += (count / length) * idf
            else:
                numerator = count * (K1 + 1)
                denominator = count + K1 * (1 - B + B * length / average_length)
                scores[doc_id] += idf * numerator / denominator

    return scores


def search(query, index, doc_lengths, mode="and", method="bm25"):
    """Full search. Returns [(doc_id, score), ...] with the best match first."""
    include, exclude = parse_query(query)
    matches = find_matches(include, exclude, index, mode)
    scores = score_documents(include, matches, index, doc_lengths, method)

    # Sort by score (highest first); break ties alphabetically so results are stable.
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
