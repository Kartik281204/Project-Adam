"""snippets.py - Stage 6: short text excerpts with the matching words highlighted."""

import re


def make_snippet(text, terms, width=160):
    """Cut a short excerpt of `text` around the first query word that appears."""
    text = " ".join(text.split())          # collapse newlines and repeated spaces
    lowered = text.lower()

    position = -1
    for term in terms:
        found = lowered.find(term)         # -1 means "not found"
        if found != -1 and (position == -1 or found < position):
            position = found

    if position == -1:                     # no match in the text: use the beginning
        start = 0
    else:
        start = max(0, position - width // 3)
    end = min(len(text), start + width)

    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def highlight_parts(text, terms):
    """Split `text` into [(piece, is_match), ...] so callers can style the matches."""
    if not terms:
        return [(text, False)]

    # Matches a word that STARTS with any query term (so "learn" matches "learning").
    pattern = r"\b(?:" + "|".join(re.escape(term) for term in terms) + r")\w*"
    pieces = re.split("(" + pattern + ")", text, flags=re.IGNORECASE)

    # re.split puts matches at the odd positions: text, match, text, match, ...
    parts = []
    for position, piece in enumerate(pieces):
        if piece != "":
            parts.append((piece, position % 2 == 1))
    return parts


def highlight(text, terms, start="**", end="**"):
    """Return `text` with every matching word wrapped in `start` and `end`."""
    result = ""
    for piece, is_match in highlight_parts(text, terms):
        if is_match:
            result += start + piece + end
        else:
            result += piece
    return result
