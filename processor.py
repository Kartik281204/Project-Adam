"""processor.py - Stage 2: turn raw text into a clean list of tokens."""

# Very common words that carry little meaning. A set makes "is this word in the
# list?" checks very fast.
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "he", "her", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "of", "on", "or", "our", "she", "so", "such", "than", "that",
    "the", "their", "them", "then", "there", "these", "they", "this", "to",
    "was", "we", "were", "what", "when", "which", "who", "will", "with", "you",
    "your",
}

# Stemming is a switch. If you change it, delete index.json so the index is
# rebuilt with the new setting (documents and queries must be processed the same way).
USE_STEMMING = True


def tokenize(text):
    """Lowercase the text and split it into a list of words (no punctuation)."""
    text = text.lower()
    text = text.replace("'", "").replace("’", "")   # don't -> dont

    cleaned = []
    for character in text:
        if character.isalnum():          # a letter or a digit: keep it
            cleaned.append(character)
        else:                            # anything else becomes a space
            cleaned.append(" ")
    return "".join(cleaned).split()


def remove_stop_words(tokens):
    """Return the tokens with every stop word removed."""
    kept = []
    for token in tokens:
        if token not in STOP_WORDS:
            kept.append(token)
    return kept


def undouble(word):
    """runn -> run, but fall stays fall (we leave l, s and z doubled)."""
    if len(word) >= 3 and word[-1] == word[-2] and word[-1] not in "lsz":
        return word[:-1]
    return word


def stem(word):
    """Chop common endings so learning, learned and learns all become learn."""
    if len(word) > 5 and word.endswith("ing"):
        return undouble(word[:-3])
    if len(word) > 5 and word.endswith("ed"):
        return undouble(word[:-2])
    if len(word) > 3 and word.endswith("s") and not word.endswith(("ss", "us", "is")):
        return word[:-1]
    return word


def process(text):
    """The full pipeline: raw text in, list of clean tokens out."""
    tokens = tokenize(text)
    tokens = remove_stop_words(tokens)
    if USE_STEMMING:
        stemmed = []
        for token in tokens:
            stemmed.append(stem(token))
        tokens = stemmed
    return tokens
