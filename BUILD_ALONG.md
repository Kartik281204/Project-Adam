# Build MiniSearch: a step-by-step build-along

**Build a complete search engine in Python, one small piece at a time, with the full code, explained line by line.**

By the end you will have a working project: it reads documents, cleans and indexes them, ranks results with **BM25**, crawls websites politely, saves its index, and has both a terminal interface and a web interface. It comes with **54 automated tests**.

---

## Read this first

### How to use this tutorial

The best way to learn from this is to **build it alongside me**:

1. Every step starts with the **goal in plain English**.
2. Then comes a **⏸ Pause and try** box. Spend 10 to 20 minutes attempting it yourself first. Even a wrong attempt teaches you what the solution is solving.
3. Then I show **the code I wrote**, with an explanation of what each part does and *why*.
4. Then you **type it in** (don't paste!) and run the **Try it** block. Your output should match mine.
5. Each step ends with a **✅ Checkpoint** and a suggested Git commit.

If you get stuck, jump to the [troubleshooting table](#appendix-b-troubleshooting) at the end.

### What is real in this tutorial

Everything you see here was actually run:

- Every code block is copied **straight from the tested source files**, so it can't have typos.
- Every output block (the `>>>` sessions and terminal output) is the **real output** from running that code.
- The project passes its own test suite (you'll see it in Step 12).

One honest limit: my environment could only reach a restricted set of websites, so I tested the crawler against a **local practice website** (included in the project as `demo_site/`) rather than live sites like `quotes.toscrape.com`. The crawler logic is the same, but if a live site behaves oddly, that's the first place to look.

### The map: what we're building

```
minisearch/
├── data/                 12 sample documents (Step 1)
├── demo_site/            a tiny website to practise crawling on (Step 10)
├── templates/            HTML pages for the web interface (Step 11)
├── tests/                automated tests (Step 12)
│
├── loader.py             Step 2   read documents from disk
├── processor.py          Step 3   clean text into tokens (tokenise, stop words, stemming)
├── indexer.py            Step 4   build the inverted index
├── search.py             Steps 5-6 find matches (AND/OR/NOT) and rank them (TF-IDF, BM25)
├── snippets.py           Step 7   excerpts with highlighted words
├── storage.py            Step 8   save/load the index (JSON)
├── engine.py             Step 8   one class that ties it all together
├── cli.py                Step 9   search from the terminal
├── crawler.py            Step 10  collect web pages by following links
└── app.py                Step 11  search from a web browser (Flask)
```

**How data flows** (the same picture as in the concepts guide):

```
 files / crawler ──▶ loader ──▶ processor ──▶ indexer ──▶ index (saved as JSON)
                                                              │
   you type a query ──▶ processor ──▶ search (AND/OR/NOT) ──▶ ranking ──▶ snippets ──▶ results
```

### A note on the concepts

This tutorial focuses on **building**. When a concept is new (inverted index, TF-IDF, BM25, robots.txt), I explain the essentials where you need it. For the deeper "what and why" and a Python crash course, see the companion **`README.md`** learning guide.

One difference from that guide: here I turn **stemming on** (so "learning" also finds "learn"), because it makes the results feel much smarter.

---

# Step 0: Set up your workspace

**Goal:** an empty project folder with an isolated Python environment, ready for code.

### 0.1 Check Python

Open a terminal and run:

```bash
python --version
```

You need Python 3.9 or newer (this was tested on 3.12). On Mac/Linux you may need `python3` instead of `python`. Use whichever works, everywhere.

### 0.2 Create the folder and a virtual environment

```bash
mkdir minisearch
cd minisearch
python -m venv venv
```

Activate it (you must do this **every time you open a new terminal** for this project):

| System | Command |
|---|---|
| Windows (Command Prompt) | `venv\Scripts\activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Mac / Linux | `source venv/bin/activate` |

Your prompt should now start with `(venv)`.

> **Why a virtual environment?** It gives this project its own private set of packages, so installing something here can't break another project (or your system Python).

### 0.3 Create the small config files

Create `requirements.txt`, the list of outside packages we use:

```text
requests
beautifulsoup4
flask
pytest
```

Install them:

```bash
pip install -r requirements.txt
```

- `requests` downloads web pages (crawler)
- `beautifulsoup4` reads HTML (crawler)
- `flask` runs the web interface
- `pytest` runs our tests

Create `.gitignore`, which tells Git which files *not* to save (the environment, caches, and files our program generates):

```text
venv/
__pycache__/
*.pyc
.pytest_cache/
index.json
crawled/
```

Create `pytest.ini`, which tells pytest where the tests live and where to find our modules:

```ini
[pytest]
testpaths = tests
pythonpath = .
```

Now create the empty folders `data`, `tests`, and `templates`, and start Git:

```bash
mkdir data tests templates
git init
git add .
git commit -m "Step 0: project setup"
```

### ✅ Checkpoint

`python -c "import flask, requests, bs4; print('ready')"` prints `ready`.

---

# Step 1: Create sample documents

**Goal:** give the search engine something to search: 12 short text files on different topics.

### The convention

> **The first line of every `.txt` file is its title. The rest is the body.**

We decide this now so results can show nice titles later. It's a tiny file format we invented, and that's a normal thing to do in a project.

### Why these documents?

They're written to make search *interesting*:

- **"python" is ambiguous.** It appears in a programming document *and* a snake document, so we'll see how ranking sorts them.
- **"beginners" and "learn" show up in several documents** (chess, yoga, machine learning...), so we can test AND vs OR, and stemming.
- Some documents are unrelated to everything else (coffee, cricket, monsoon), so we can confirm search *doesn't* return them.

### Create these 12 files inside `data/`

Type each into a file with exactly the name above its box. (Copying these particular files is fine. They're data, not code.)

**`data/python_programming.txt`**

```text
Python Programming for Beginners
Python is a popular programming language that is easy to read and easy to learn. Beginners use Python to build websites, analyse data and write small games. Python has a large standard library, so many common tasks need only a few lines of code. Learning Python is a great first step towards machine learning.
```

**`data/python_snakes.txt`**

```text
Pythons: The Giant Snakes
A python is a large non-venomous snake found in Africa, Asia and Australia. Pythons kill their prey by squeezing, and a big python can grow longer than six metres. Snakes like the reticulated python are among the longest animals in the world.
```

**`data/machine_learning.txt`**

```text
Introduction to Machine Learning
Machine learning is a way of teaching computers to learn patterns from data instead of following fixed rules. Popular tools such as Python libraries make it easier to train models. Learning from examples lets a model recognise images, translate languages and recommend songs.
```

**`data/search_engines.txt`**

```text
How Search Engines Work
A search engine collects pages with a crawler, cleans the text, and builds an index. The index maps every word to the documents that contain it, so a search can be answered quickly. Ranking algorithms such as BM25 then sort the results so the most relevant pages appear first.
```

**`data/cricket.txt`**

```text
The Basics of Cricket
Cricket is a bat and ball game played between two teams of eleven players. A batter scores runs by hitting the ball and running between the wickets, while the bowlers try to take wickets. Matches can last a few hours in the T20 format or up to five days in a Test match.
```

**`data/dal_recipe.txt`**

```text
How to Cook Dal at Home
Dal is a comforting Indian dish made from lentils. Wash the lentils, boil them with turmeric until soft, then add a tempering of cumin, garlic and chilli. Serve the dal hot with rice or roti. Cooking dal at home is cheap, quick and healthy.
```

**`data/solar_system.txt`**

```text
Our Solar System
The solar system has eight planets that orbit the Sun. Mercury is the closest to the Sun and Neptune is the farthest. Jupiter is the largest planet, and Earth is the only planet known to support life. Astronomers learn about distant planets using powerful telescopes.
```

**`data/delhi_metro.txt`**

```text
The Delhi Metro
The Delhi Metro is a rapid transit system serving Delhi and nearby cities. Millions of people use the metro every day to travel to work and school. Trains are fast, clean and usually on time, which makes the metro a popular way to avoid traffic.
```

**`data/monsoon.txt`**

```text
Understanding the Monsoon
The monsoon is a seasonal wind pattern that brings heavy rain to India between June and September. Farmers depend on the monsoon to grow rice and other crops. A weak monsoon can cause drought, while a strong monsoon can cause floods.
```

**`data/chess.txt`**

```text
Chess Strategy for Beginners
Chess is a board game for two players. Beginners should learn to control the centre, develop their pieces early and protect the king. Learning basic tactics, such as forks and pins, helps players win material. Many players use Python programs to analyse their games.
```

**`data/coffee.txt`**

```text
The Story of Coffee
Coffee beans are the seeds of a fruit that grows on coffee trees in warm countries. The beans are roasted, ground and brewed with hot water. Many people drink coffee every morning to feel awake, and coffee is one of the most traded products in the world.
```

**`data/yoga.txt`**

```text
Yoga for Everyday Life
Yoga combines stretching, breathing and meditation. Practising yoga every morning can improve flexibility and help people feel calm. Beginners can start with simple poses and learn breathing techniques slowly. Many people practise yoga at home with a short video.
```

### ✅ Checkpoint

You have 12 `.txt` files in `data/`. Each starts with a title line. Commit: `git add . && git commit -m "Step 1: sample data"`.

> **Make it yours:** later, replace these with your own notes, articles, or anything. The engine works on whatever `.txt` files you put in `data/`.

---

# Step 2: Load documents (`loader.py`)

**Goal:** read every `.txt` file in a folder into **one Python dictionary** that the rest of the program can use.

### The data shape we'll use everywhere

```python
{
    "yoga.txt": {"title": "Yoga for Everyday Life", "url": "", "text": "Yoga for Everyday Life\nYoga combines ..."},
    "chess.txt": {...},
}
```

- The **key** (`"yoga.txt"`) is the document's **id**, the unique name we use to refer to it.
- The **value** is a small dictionary holding `title`, `url`, and the full `text`.

Why a dictionary inside a dictionary, when `{name: text}` would do? Because we'll soon need each document's **title** and **URL** (web pages have one, files don't). Deciding the shape up front means the crawler in Step 10 can produce the *exact same shape* and plug straight in.

> **⏸ Pause and try (15 min).** Create `loader.py` and write a function `load_text_files(folder)` that returns a dictionary like the one above.
> Hints: `from pathlib import Path`, `Path(folder).glob("*.txt")`, `path.read_text(encoding="utf-8")`, `.splitlines()`. Test it in the Python prompt (`python`) with `load_text_files("data")`.

### My solution

Start the file with a docstring and imports:

```python
"""loader.py - Stage 1: read documents from disk into one dictionary.

Every document is a small dictionary:
    {"title": "...", "url": "...", "text": "..."}
and the whole collection (the corpus) is {doc_id: document}.
"""

import json
from pathlib import Path
```

(`json` isn't used until Step 10, when the crawler arrives. Importing it now saves a trip back.)

Now the function:

```python
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
```

### What each part does

- **`folder = Path(folder)`**: `Path` is a smart file-path object. Wrapping the text in `Path(...)` lets us ask questions like "is this a folder?" and search inside it.
- **`if not folder.is_dir(): raise FileNotFoundError(...)`**: if the folder doesn't exist we **stop with a clear message** instead of silently returning an empty result. Failing loudly with a helpful message is a habit worth building. (An f-string, `f"..."`, drops the variable `{folder}` into the message.)
- **`sorted(folder.glob("*.txt"))`**: `glob("*.txt")` finds every file ending in `.txt`; the `*` means "anything". `sorted` puts them in alphabetical order so the program behaves the same every run.
- **`path.read_text(encoding="utf-8")`**: reads the whole file as one string. The `encoding` argument avoids strange errors with special characters.
- **`text.strip().splitlines()`**: `strip()` removes blank space at both ends; `splitlines()` cuts the text into a list of lines. `lines[0]` is then the first line, our title.
- **`if lines: ... else: ...`**: an empty list counts as False, so an **empty file** falls through to `path.stem` (the file name without `.txt`) as its title. Without this, `lines[0]` would crash with an `IndexError`.
- **`documents[path.name] = {...}`**: file name as the id; `url` is `""` because a local file has no web address.

### Try it

Open the Python prompt in your project folder (`python`) and try these lines:

```pycon
>>> from loader import load_text_files
>>> docs = load_text_files("data")
>>> len(docs)
12
>>> list(docs)[:3]
['chess.txt', 'coffee.txt', 'cricket.txt']
>>> docs["yoga.txt"]["title"]
'Yoga for Everyday Life'
>>> docs["yoga.txt"]["text"][:60]
'Yoga for Everyday Life\nYoga combines stretching, breathing a'
```

### ✅ Checkpoint

You see `12` documents and correct titles. Commit: `git commit -am "Step 2: loader"` (use `git add .` first for new files).

*(We'll add two more functions to `loader.py` in Step 10, when the crawler arrives.)*

---

# Step 3: Clean the text (`processor.py`)

**Goal:** turn messy human text into a tidy list of **tokens** (standardised words), so that `"Python"`, `"python"`, and `"Python,"` all become the same thing.

### The rule that prevents most search bugs

> **Documents and queries must go through the exact same cleaning pipeline.**

If we index `"python"` but the user's `"Python"` isn't cleaned the same way, nothing matches. Everything in this step is built as functions we'll reuse in both places.

Our pipeline, in order:

```
raw text ─▶ lowercase ─▶ remove punctuation ─▶ split into words ─▶ drop stop words ─▶ stem ─▶ tokens
```

We'll build it in four small pieces. Create `processor.py`.

---

### 3.1 Tokenising

> **⏸ Pause and try.** Write `tokenize(text)` so that `tokenize("Hello, World!!")` returns `['hello', 'world']`. Don't use any libraries. Think about how to go through the text one character at a time.

```python
"""processor.py - Stage 2: turn raw text into a clean list of tokens."""

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
```

**How it works:**

- `text.lower()` makes everything lowercase. Remember: string methods **return a new string**. That's why we write `text = text.lower()` and not just `text.lower()`.
- The two `.replace(...)` calls delete apostrophes, so `don't` becomes `dont` instead of splitting into `don` and `t`. (There are two kinds: the straight `'` and the curly `’` that word processors and web pages use.) **This is a design decision, not a law**, so if you prefer another choice, change it and note it in your diary.
- The loop looks at each `character`. `character.isalnum()` is True for letters and digits. Those we keep; **everything else** (commas, dashes, brackets, even `₹` and `—`) becomes a space.
- `"".join(cleaned)` glues the list of characters back into one string, and `.split()` (with no argument) cuts on any run of spaces, so `"hello   world"` gives two words, no empty ones.

Try it (Python prompt):

```pycon
>>> from processor import tokenize
>>> tokenize("Hello, World!!")
['hello', 'world']
>>> tokenize("Don't stop — it’s T20 time.")
['dont', 'stop', 'its', 't20', 'time']
>>> tokenize("   lots   of   spaces   ")
['lots', 'of', 'spaces']
>>> tokenize("")
[]
```

---

### 3.2 Stop words

**Stop words** are extremely common words (`the`, `is`, `of`...) that appear in almost every document, so they can't help decide which document is relevant. Removing them also makes the index smaller.

```python
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

def remove_stop_words(tokens):
    """Return the tokens with every stop word removed."""
    kept = []
    for token in tokens:
        if token not in STOP_WORDS:
            kept.append(token)
    return kept
```

- `STOP_WORDS` is a **set**, not a list. Asking "is this word in the set?" is very fast in a set and slow-ish in a long list.
- The function loops over the tokens and keeps only those **not in** the set. (A shorter way to write this is `[t for t in tokens if t not in STOP_WORDS]`, a *list comprehension*. Same result; use whichever you understand.)

```pycon
>>> from processor import tokenize, remove_stop_words
>>> remove_stop_words(tokenize("The quick brown fox is fast"))
['quick', 'brown', 'fox', 'fast']
```

---

### 3.3 Stemming

**Stemming** chops word endings so related words match: `learning`, `learned` and `learns` should all match a search for `learn`.

Real stemmers (like the Porter stemmer) contain dozens of carefully tested rules. We'll write a **tiny** one to understand the idea:

```python
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
```

- Words ending in `ing` or `ed` lose that ending, but **only if the word is longer than 5 letters**. That protects short words like `sing`, `bed`, `speed`.
- `undouble` fixes the leftover double letter: `running` → `runn` → `run`, `programming` → `programm` → `program`. (We leave doubled `l`, `s`, `z` alone, so `falling` → `fall`, not `fal`.)
- A trailing `s` is removed (`snakes` → `snake`) unless the word ends in `ss`, `us` or `is` (so `class`, `focus`, `analysis` survive).
- `endswith(("ss", "us", "is"))` accepts a **tuple** of endings and checks all of them at once.

Try it, and look at where it goes wrong on purpose:

```pycon
>>> from processor import stem
>>> [stem(w) for w in ["learning", "learned", "learns", "running", "programming", "snakes"]]
['learn', 'learn', 'learn', 'run', 'program', 'snake']
>>> [stem(w) for w in ["class", "focus", "speed", "bus"]]
['class', 'focus', 'speed', 'bus']
>>> [stem(w) for w in ["libraries", "boxes", "string"]]
['librarie', 'boxe', 'str']
```

The last line shows the flaws: `libraries` → `librarie`, `boxes` → `boxe`, `string` → `str`. **That's fine**, and it's the lesson. A stemmer doesn't need to produce real words; it only needs to be *consistent* (the same input always gives the same stem, for documents and queries). It also shows why professionals use the real Porter stemmer. (You can swap it in later: `pip install nltk`, then `from nltk.stem import PorterStemmer`.)

---

### 3.4 The full pipeline

```python
# Stemming is a switch. If you change it, delete index.json so the index is
# rebuilt with the new setting (documents and queries must be processed the same way).
USE_STEMMING = True

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
```

- `USE_STEMMING` is an on/off switch. Because the index must be built with the same settings as queries, **if you change it, delete `index.json` so the index is rebuilt.** (We'll meet that file in Step 8.)
- Stop words are removed **before** stemming, because our stop-word list contains whole words like `is`, not stems.

```pycon
>>> from processor import process
>>> process("Learning Python is fun and Python is fast.")
['learn', 'python', 'fun', 'python', 'fast']
>>> process("The Quick brown FOX, jumped!")
['quick', 'brown', 'fox', 'jump']
```

### Your complete `processor.py`

If yours differs from the steps above, compare with the full listing in [Appendix A](#appendix-a-complete-code).

### ✅ Checkpoint

`process("Learning Python is fun and Python is fast.")` gives `['learn', 'python', 'fun', 'python', 'fast']`. Commit: `git add . && git commit -m "Step 3: text processing"`.

---

# Step 4: Build the inverted index (`indexer.py`)

**Goal:** build the lookup table at the heart of every search engine: **word → the documents that contain it (and how often).**

### The idea in one picture

Right now each document *contains* words. We flip that around:

```
BEFORE (what we have)                 AFTER (the inverted index)
yoga.txt   → [yoga, everyday, life,   yoga    → {yoga.txt: 4}
              yoga, combine, ...]     chess   → {chess.txt: 2}
chess.txt  → [chess, strategy,        python  → {python_programming.txt: 5,
              beginner, chess, ...]                python_snakes.txt: 5, ...}
```

To find "python" we no longer scan every document. We do **one dictionary lookup**. That is why search is fast, and it is exactly the index at the back of a textbook.

We build **two** things:

| Name | Shape | Used for |
|---|---|---|
| `index` | `{term: {doc_id: count}}` | Finding documents, and counting how often a word appears |
| `doc_lengths` | `{doc_id: number_of_tokens}` | Ranking (a word appearing 5 times in a 30-word document is a stronger signal than 5 times in 3,000 words) |

> **⏸ Pause and try (20 to 30 min).** Create `indexer.py` with `build_index(documents)` returning `(index, doc_lengths)`.
> Work on **one** document first. Count its words with a dictionary (`counts[word] = counts.get(word, 0) + 1`), print the result, and only then extend to all documents.
> The classic trap: the first time you see a word, `index[word]` doesn't exist yet, so you get a `KeyError`. How will you create it?

### My solution

```python
"""indexer.py - Stage 3: build the inverted index."""

from processor import process
```

```python
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
```

### Walking through it

1. **`for doc_id, document in documents.items()`**: `.items()` gives each key and value together, as a pair we *unpack* into two variables.
2. **`tokens = process(document["text"])`**: our Step 3 pipeline. Notice we index `text`, which includes the title line, so title words are searchable too.
3. **`doc_lengths[doc_id] = len(tokens)`**: record the document length.
4. **`counts = {}`**: a **brand new** dictionary for *each* document. (If you create it once outside the loop, counts from earlier documents leak into later ones, a very common bug.)
5. **`counts[token] = counts.get(token, 0) + 1`**: "look up the current count (or 0 if we've never seen the word), add 1, store it back."
6. **`if term not in index: index[term] = {}`**: this is the `KeyError` guard. Create the inner dictionary the first time a word appears, then store this document's count in it.

(Python has a shortcut, `collections.Counter`, that does step 5 for you. Writing it by hand first means you know what `Counter` is doing.)

### Try it: first the tiny example we've used in the concepts guide

```pycon
>>> from indexer import build_index
>>> tiny = {
...     "doc1": {"text": "Python is a fun language to learn."},
...     "doc2": {"text": "Learning Python is fun and Python is fast."},
...     "doc3": {"text": "Cats are fun animals."},
... }
>>> index, doc_lengths = build_index(tiny)
>>> index
{'python': {'doc1': 1, 'doc2': 2}, 'fun': {'doc1': 1, 'doc2': 1, 'doc3': 1}, 'language': {'doc1': 1}, 'learn': {'doc1': 1, 'doc2': 1}, 'fast': {'doc2': 1}, 'cat': {'doc3': 1}, 'animal': {'doc3': 1}}
>>> doc_lengths
{'doc1': 4, 'doc2': 5, 'doc3': 3}
```

Check it against the paper version: `python` appears **once in doc1 and twice in doc2**; `fun` is in all three; `learn` (from *learn* **and** *learning*, thanks to the stemmer) is in doc1 and doc2. Doing this trace by hand is the best debugging habit you can build.

Now the real data:

```pycon
>>> from loader import load_text_files
>>> from indexer import build_index
>>> docs = load_text_files("data")
>>> index, doc_lengths = build_index(docs)
>>> len(index)
266
>>> index["python"]
{'chess.txt': 1, 'machine_learning.txt': 1, 'python_programming.txt': 5, 'python_snakes.txt': 5}
>>> index["snake"]
{'python_snakes.txt': 3}
>>> index["learn"]
{'chess.txt': 2, 'machine_learning.txt': 4, 'python_programming.txt': 3, 'solar_system.txt': 1, 'yoga.txt': 1}
>>> doc_lengths["yoga.txt"]
35
```

`index["python"]` shows four documents: the programming page (5 mentions), the snake page (5 mentions), and two that mention Python in passing (machine learning and chess). That's the raw material for search.

### ✅ Checkpoint

`index["python"]` lists the right documents and counts. Commit: `git add . && git commit -m "Step 4: inverted index"`.

---

# Step 5: Find matching documents (`search.py`, part 1)

**Goal:** given what the user typed, return the **set of documents that match**. Ranking comes in the next step.

### Three kinds of matching

| Style | Meaning | Example | Set operation |
|---|---|---|---|
| **AND** (our default) | document must contain **all** the words | `python beginners` | intersection `&` |
| **OR** | document must contain **at least one** word | `python beginners` | union `\|` |
| **NOT** | document must **not** contain a word | `python -snake` | difference `-` |

This is exactly why sets exist in Python: the three operations above are single symbols.

> **⏸ Pause and try.** Write `find_matches(include, exclude, index, mode)`. Plan: get the set of documents for the first word; for each next word, combine with `&` or `|`; finally subtract the documents of every excluded word. What should happen if `include` is empty?

### My solution

Create `search.py`. Start with the imports (we'll use `math` in Step 6):

```python
"""search.py - Stages 4 and 5: find matching documents, then rank them."""

import math

from processor import process
```

First, turn the raw query into words. Note the **same `process()`** pipeline from Step 3:

```python
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
```

- `query.split()` cuts the text into pieces on spaces.
- `part.startswith("-") and len(part) > 1` detects an exclusion like `-snake`. The `len(part) > 1` check ignores a lone `-`.
- Included and excluded pieces are each glued back together and cleaned by `process()`, so `-Snakes` becomes the stem `snake`, matching how documents were indexed.

Next, the lookup for a single word:

```python
def docs_for_term(term, index):
    """The set of document ids that contain `term` (empty set if unknown)."""
    return set(index.get(term, {}))
```

- `index.get(term, {})` returns the term's postings, or an **empty dictionary** if we've never seen the word (instead of crashing with `KeyError`).
- `set(some_dict)` makes a set of the dictionary's **keys**, which here are the document ids.

And the combining logic:

```python
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
```

Walk through `python beginners` with mode `and`: `matches` starts as the documents containing *python* (4 documents). Then we combine it with the documents containing *beginner* using `&`, keeping **only the overlap**. In `or` mode we use `|` and add everything instead.

Two edge cases are handled deliberately: an **empty `include`** (for example the query was only stop words like `the`) returns an empty set immediately, and an **unknown word** in AND mode gives an empty result (correct, since no document can contain it).

### Try it

```pycon
>>> from loader import load_text_files
>>> from indexer import build_index
>>> from search import parse_query, find_matches
>>> index, doc_lengths = build_index(load_text_files("data"))
>>> parse_query("Python -snakes beginners")
(['python', 'beginner'], ['snake'])
>>> include, exclude = parse_query("python beginners")
>>> sorted(find_matches(include, exclude, index, "and"))
['chess.txt', 'python_programming.txt']
>>> sorted(find_matches(include, exclude, index, "or"))
['chess.txt', 'machine_learning.txt', 'python_programming.txt', 'python_snakes.txt', 'yoga.txt']
>>> include, exclude = parse_query("python -snake")
>>> sorted(find_matches(include, exclude, index))
['chess.txt', 'machine_learning.txt', 'python_programming.txt']
>>> include, exclude = parse_query("the")
>>> sorted(find_matches(include, exclude, index))
[]
```

(We wrap results in `sorted(...)` only because sets have no order, and sorting makes the printout predictable.)

Notice `python -snake` gave the python documents **except** the snake one. 🎉 *You now have a working search engine* (unranked). Everything from here makes it better.

### ✅ Checkpoint

AND finds 2 documents, OR finds 5, NOT removes the snake page. Commit: `git add . && git commit -m "Step 5: matching"`.

---

# Step 6: Rank the results (`search.py`, part 2)

**Goal:** put the **most relevant** matches first by giving each one a **score**.

### The two ideas behind good scores

1. **Term frequency (TF):** the more often a word appears in a document, the more relevant it probably is. But divide by the document's length, or long documents always win.
2. **Inverse document frequency (IDF):** a **rare** word is more informative than a common one. If every document contains `fun`, matching `fun` tells you nothing; matching `snake` tells you a lot.

### Formula 1: TF-IDF (the classic)

```
score = Σ over query words of   (count / document_length)  ×  ln(N / df)

N  = number of documents in total
df = number of documents that contain the word
```

### Formula 2: BM25 (what real engines use)

BM25 improves TF-IDF in two ways: extra repeats of a word count for **less and less** (1 mention → 2 matters a lot; 50 → 51 barely matters), and document length is compared against the **average** length.

```
                      count × (K1 + 1)
score = IDF ×  ─────────────────────────────────────────
                count + K1 × (1 − B + B × length / average_length)

IDF = ln( 1 + (N − df + 0.5) / (df + 0.5) )      K1 = 1.5,  B = 0.75
```

You don't need to memorise these. **Translate them into code one variable at a time**, which is exactly what we'll do.

> **⏸ Pause and try (30+ min, this is the hardest step).** In `search.py`, write `score_documents(terms, matches, index, doc_lengths, method)` returning `{doc_id: score}`.
> Start with **TF-IDF only**. Check your answer against this hand calculation: with the three-document example, `python` is in 2 of 3 documents, so `IDF = ln(3/2) = 0.405`. In doc2, `python` appears 2 times in 5 words, so `score = (2/5) × 0.405 = 0.162`.
> Then add BM25 as a second branch.

### My solution

First, the two BM25 settings as named constants at the top of the file, so they're easy to find and tweak:

```python
# BM25 settings. These are the standard defaults.
K1 = 1.5    # how quickly extra repeats of a word stop helping

B = 0.75    # how strongly document length is corrected (0 = ignore, 1 = fully)
```

Then the scoring function:

```python
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
```

### Walking through it

- **`scores = {doc_id: 0.0 for doc_id in matches}`**: a *dictionary comprehension*: "make a dictionary with every matching document starting at score 0".
- **`if not matches: return scores`**: nothing to score. Returning early also avoids dividing by zero on an empty corpus.
- **`average_length`** is the mean document length; BM25 needs it.
- **Outer loop over `terms`**, inner loop over `matches`: each query word adds its contribution to each document's running total. That's what `+=` does: it *accumulates*.
- **`postings = index.get(term)`**, then `if not postings: continue`: skip words we've never seen. (`continue` jumps to the next word.)
- **`doc_freq = len(postings)`**: how many documents contain the word. This feeds IDF.
- **`if method == "tfidf": ... else: ...`**: two formulas, one function. The BM25 lines are the formula above, split into `numerator` and `denominator` so each piece is readable.

### Putting it together: `search()`

```python
def search(query, index, doc_lengths, mode="and", method="bm25"):
    """Full search. Returns [(doc_id, score), ...] with the best match first."""
    include, exclude = parse_query(query)
    matches = find_matches(include, exclude, index, mode)
    scores = score_documents(include, matches, index, doc_lengths, method)

    # Sort by score (highest first); break ties alphabetically so results are stable.
    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
```

- It chains three steps: parse → find matches → score.
- **`sorted(..., key=lambda item: (-item[1], item[0]))`** is the trickiest line. `scores.items()` gives `(doc_id, score)` pairs. `key=` says *what to sort by*. `lambda item: ...` is a tiny nameless function; `item[1]` is the score and `item[0]` the document id. We sort by **negative score** (so the *highest* score comes first) and break ties by document id, alphabetically, so results are always in a stable order.

### Try it

```pycon
>>> from loader import load_text_files
>>> from indexer import build_index
>>> from search import search
>>> index, doc_lengths = build_index(load_text_files("data"))
>>> for doc_id, score in search("python", index, doc_lengths):
...     print(f"{score:.3f}  {doc_id}")
... 
2.063  python_snakes.txt
1.959  python_programming.txt
1.062  machine_learning.txt
1.048  chess.txt
>>> for doc_id, score in search("python", index, doc_lengths, method="tfidf"):
...     print(f"{score:.3f}  {doc_id}")
... 
0.177  python_snakes.txt
0.134  python_programming.txt
0.033  machine_learning.txt
0.032  chess.txt
```

Interesting: the **snake** page outranks the **programming** page for `python`. Is that a bug? No. Both mention "python" 5 times, but the snake page is *shorter* (31 words vs 41), so "python" makes up a bigger share of it. The engine does exactly what the formula says; it just can't know which meaning of "python" you wanted. (That ambiguity is precisely the problem that AI-based *semantic* search attacks. See Step 13.)

Now check your code against the **hand calculation** from the "Pause and try" box:

```pycon
>>> import math
>>> from indexer import build_index
>>> from search import search
>>> tiny = {
...     "doc1": {"text": "Python is a fun language to learn."},
...     "doc2": {"text": "Learning Python is fun and Python is fast."},
...     "doc3": {"text": "Cats are fun animals."},
... }
>>> tiny_index, tiny_lengths = build_index(tiny)
>>> (2 / 5) * math.log(3 / 2)
0.16218604324326577
>>> search("python fun", tiny_index, tiny_lengths, method="tfidf")
[('doc2', 0.16218604324326577), ('doc1', 0.1013662770270411)]
>>> search("python", tiny_index, tiny_lengths, method="bm25")
[('doc2', 0.6214924023084107), ('doc1', 0.4700036292457356)]
```

The TF-IDF score for doc2 matches your hand calculation (**0.162**), and `fun` contributes nothing because it's in *every* document (IDF = 0). That's the formula working as intended.

### ✅ Checkpoint

Scores match the hand calculation and results come out sorted, best first. Commit: `git add . && git commit -m "Step 6: ranking"`.

---

# Step 7: Snippets and highlighting (`snippets.py`)

**Goal:** show a short **excerpt** of each result with the matching words highlighted, so users can see *why* it matched.

> **⏸ Pause and try.** Write `make_snippet(text, terms, width)` that returns about `width` characters of `text` around the first query word. Hints: `text.lower().find(word)` returns the position of a word, or `-1` if it isn't there. `text[start:end]` slices.

### My solution

```python
"""snippets.py - Stage 6: short text excerpts with the matching words highlighted."""

import re
```

```python
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
```

- `" ".join(text.split())` is a neat trick: `split()` cuts on *any* whitespace (spaces, tabs, newlines) and `join` glues the pieces back with single spaces, tidying the text.
- We look for **every** query term and keep the **earliest** position (`position == -1` means "none found yet").
- `max(0, position - width // 3)`: start a little *before* the match, but never before position 0. `//` is whole-number division.
- `min(len(text), start + width)`: don't run past the end of the text.
- `...` is added on the sides where we cut text off.

Now highlighting. We need to find every word that *starts with* a query term (so the stem `learn` highlights `Learning` too). That's a job for a **regular expression** (regex), a mini-language for describing text patterns:

```python
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
```

Plain-English tour of the regex pieces (you don't need to master regex to follow along):

| Piece | Means |
|---|---|
| `\b` | a word boundary: the match must start at the beginning of a word |
| `(?:a\|b\|c)` | "a or b or c" (the `\|` is "or") |
| `\w*` | followed by any number of further letters/digits, so we highlight the **whole word** |
| `re.escape(term)` | makes sure special characters in a term are treated as plain text |
| `re.IGNORECASE` | ignore capitals |

`re.split` with brackets around the pattern returns the text **and** the matches, alternating: text, match, text, match... So matches are always at **odd positions**, which is what `position % 2 == 1` checks. We return a list of `(piece, is_match)` pairs: an interface-neutral format. The terminal can add `**` around matches; the web page can add `<mark>` tags.

```python
def highlight(text, terms, start="**", end="**"):
    """Return `text` with every matching word wrapped in `start` and `end`."""
    result = ""
    for piece, is_match in highlight_parts(text, terms):
        if is_match:
            result += start + piece + end
        else:
            result += piece
    return result
```

### Try it

```pycon
>>> from loader import load_text_files
>>> from snippets import make_snippet, highlight, highlight_parts
>>> docs = load_text_files("data")
>>> text = docs["yoga.txt"]["text"]
>>> make_snippet(text, ["beginner"])
'...g can improve flexibility and help people feel calm. Beginners can start with simple poses and learn breathing techniques slowly. Many people practise yoga at h...'
>>> highlight("Learning is fun. Let us learn!", ["learn"])
'**Learning** is fun. Let us **learn**!'
>>> highlight_parts("a cat sat", ["cat"])
[('a ', False), ('cat', True), (' sat', False)]
```

### ✅ Checkpoint

`highlight("Learning is fun. Let us learn!", ["learn"])` wraps both `Learning` and `learn`. Commit: `git add . && git commit -m "Step 7: snippets"`.

---

# Step 8: Save the index, and tie it all together (`storage.py`, `engine.py`)

**Goal:** (1) save the index to disk so we don't rebuild it every run, and (2) create **one object** that the terminal and web interfaces can both use.

### 8.1 Saving and loading (`storage.py`)

Variables live in memory and vanish when the program ends. **JSON** is a plain-text format that maps neatly onto Python dictionaries and lists, so saving is two lines:

```python
"""storage.py - Stage 7: save the index to disk and load it back."""

import json
```

```python
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
```

- `json.dump(data, file)` writes the dictionary as text; `json.load(file)` reads it back.
- We save the **documents too** (not just the index) because we need each document's text to make snippets.
- Watch out: opening a file in `"w"` mode **erases it first**.

### 8.2 The `SearchEngine` class (`engine.py`)

So far we've passed `index`, `doc_lengths` and `documents` between functions by hand. A **class** bundles that data with the functions that use it, so we can just say `engine.search("python")`.

> **Classes in 60 seconds.** A class is a blueprint. `SearchEngine()` creates an *object* from the blueprint. Inside the class, functions (called *methods*) take `self` as their first parameter, which means "this particular object". `self.index` is *this engine's* index. Every method can see it.

```python
"""engine.py - Stage 8: one object that ties every stage together."""

from pathlib import Path

from indexer import build_index
from loader import load_all
from search import parse_query, search
from snippets import make_snippet
from storage import load_index, save_index
```

First, file locations:

```python
# __file__ is this file's own path, so these paths work no matter where you run from.
BASE_DIR = Path(__file__).resolve().parent

DATA_FOLDER = BASE_DIR / "data"

CRAWLED_FILE = BASE_DIR / "crawled" / "pages.json"

INDEX_FILE = BASE_DIR / "index.json"
```

`__file__` is the path of the file being run. `Path(__file__).resolve().parent` is "the folder this file lives in". By building every path from it, the program works **no matter which folder you launch it from**, which prevents the classic `FileNotFoundError` mystery. (The `/` operator on a `Path` joins path pieces.)

Now the class:

```python
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
```

- **`__init__`** runs when you create the object and sets up three empty containers.
- **`build`** stores the corpus and builds the index (Step 4). **`save`/`load`** use Step 8.1.
- **`stats`** returns a few numbers about the index. Note `if count else 0` protects against dividing by zero on an empty engine.
- **`search`** runs Step 5 and 6, then adds what an interface needs to *display* each result: title, url, score, and a snippet. It returns a dictionary with the results **and** the total number of matches **and** the processed query terms (for highlighting). `ranked[:top_k]` keeps only the top results, but `total` still reports how many matched overall.

Finally, a helper that decides between "load the saved index" and "build a new one":

```python
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
```

The parameters have **default values**, so normal code just calls `load_engine()`, while our tests can pass in temporary paths.

### Try it

```pycon
>>> from engine import load_engine
>>> engine = load_engine()
>>> engine.stats()
{'documents': 12, 'terms': 266, 'average_length': 33.083333333333336}
>>> response = engine.search("python beginners")
>>> response["total"]
2
>>> response["terms"]
['python', 'beginner']
>>> response["results"][0]["title"]
'Python Programming for Beginners'
>>> response["results"][0]["snippet"]
'Python Programming for Beginners Python is a popular programming language that is easy to read and easy to learn. Beginners use Python to build websites, analys...'
>>> same = load_engine()
>>> same.stats() == engine.stats()
True
>>> import os
>>> os.path.getsize("index.json")
14739
```

The first `load_engine()` built the index and saved `index.json` next to your code; the second one **loaded** it. Open `index.json` in your editor to see your index as text. If you ever edit the documents or change `processor.py`, delete `index.json` (or run the CLI with `--rebuild`) to force a fresh build.

### ✅ Checkpoint

`engine.search("python beginners")` returns 2 results and an `index.json` file appears. Commit: `git add . && git commit -m "Step 8: storage and engine"`.

---

# Step 9: A terminal interface (`cli.py`)

**Goal:** a friendly prompt where you type searches and see ranked, highlighted results.

> **⏸ Pause and try.** Write a loop that repeatedly asks `search> `, runs `engine.search(...)` and prints the results, until the user types `:quit`. Hints: `while True:`, `input("search> ")`, `break`.

### My solution

Create `cli.py`. First the imports and the help text:

```python
"""cli.py - a search prompt for your terminal.

Run:  python cli.py            (loads the saved index, or builds it the first time)
      python cli.py --rebuild  (throw the saved index away and build a new one)
"""

import sys

from engine import load_engine
from snippets import highlight

HELP = """Type words to search. Commands:
  -word           exclude a word          (python -snake)
  :mode and|or    all words / any word    (default: and)
  :method bm25|tfidf   ranking formula    (default: bm25)
  :stats          show index statistics
  :help           show this help
  :quit           leave"""
```

- `sys.argv` is the list of words typed on the command line: `python cli.py --rebuild` gives `["cli.py", "--rebuild"]`. That's how we detect the `--rebuild` flag.

Printing one response nicely:

```python
def show_results(response, query, mode, method):
    """Print one search response nicely."""
    total = response["total"]
    print(f"\n{total} result(s) for '{query}'  [mode={mode}, method={method}]\n")

    for rank, result in enumerate(response["results"], start=1):
        source = result["url"] or result["doc_id"]
        print(f"{rank}. {result['title']}   (score {result['score']:.3f})")
        print(f"   {source}")
        print("   " + highlight(result["snippet"], response["terms"]))
        print()
```

- `enumerate(..., start=1)` counts results from 1 instead of 0.
- `result['url'] or result['doc_id']`: `or` returns the first "truthy" value. A file has an empty `url`, so we show its name instead.
- `f"{result['score']:.3f}"` prints the score with 3 decimal places.
- `highlight(...)` from Step 7 wraps matches in `**`.

The main loop:

```python
def main():
    rebuild = "--rebuild" in sys.argv
    engine = load_engine(rebuild=rebuild)

    stats = engine.stats()
    print(f"MiniSearch ready: {stats['documents']} documents, {stats['terms']} unique terms.")
    print("Type :help for help.\n")

    mode = "and"
    method = "bm25"

    while True:
        try:
            query = input("search> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query == "":
            continue

        if query.startswith(":"):
            parts = query.split()
            command = parts[0]
            if command in (":quit", ":q"):
                break
            elif command == ":help":
                print(HELP)
            elif command == ":stats":
                print(engine.stats())
            elif command == ":mode" and len(parts) == 2 and parts[1] in ("and", "or"):
                mode = parts[1]
                print(f"mode = {mode}")
            elif command == ":method" and len(parts) == 2 and parts[1] in ("bm25", "tfidf"):
                method = parts[1]
                print(f"method = {method}")
            else:
                print("Unknown command. Type :help")
            continue

        response = engine.search(query, mode=mode, method=method, top_k=5)
        show_results(response, query, mode, method)
```

- **`try / except (EOFError, KeyboardInterrupt)`**: `input()` raises `KeyboardInterrupt` if you press Ctrl+C and `EOFError` if input ends. We catch both so the program exits politely instead of showing a scary error.
- **`if query.startswith(":")`**: lines beginning with `:` are *commands* (`:mode or`, `:method tfidf`, `:stats`, `:help`, `:quit`), while everything else is a search. Using a prefix means no command can clash with a real search word.
- **`continue`** jumps back to the top of the loop, skipping the search code below.
- The `mode` and `method` variables live **outside** the loop, so a command like `:mode or` changes them for all later searches.

And the last two lines, which run `main()` only when you start this file directly:

```python
if __name__ == "__main__":
    main()
```

### Try it

```bash
python cli.py
```

A sample session (yours will match):

```text
$ python cli.py
MiniSearch ready: 12 documents, 266 unique terms.
Type :help for help.

search> python beginners

2 result(s) for 'python beginners'  [mode=and, method=bm25]

1. Python Programming for Beginners   (score 3.700)
   python_programming.txt
   **Python** Programming for **Beginners** **Python** is a popular programming language that is easy to read and easy to learn. **Beginners** use **Python** to build websites, analys...

2. Chess Strategy for Beginners   (score 2.906)
   chess.txt
   Chess Strategy for **Beginners** Chess is a board game for two players. **Beginners** should learn to control the centre, develop their pieces early and protect the kin...

search> :mode or
mode = or
search> snakes chess

2 result(s) for 'snakes chess'  [mode=or, method=bm25]

1. Pythons: The Giant Snakes   (score 3.657)
   python_snakes.txt
   Pythons: The Giant **Snakes** A python is a large non-venomous **snake** found in Africa, Asia and Australia. Pythons kill their prey by squeezing, and a big python can...

2. Chess Strategy for Beginners   (score 3.058)
   chess.txt
   **Chess** Strategy for Beginners **Chess** is a board game for two players. Beginners should learn to control the centre, develop their pieces early and protect the kin...

search> python -snake

3 result(s) for 'python -snake'  [mode=or, method=bm25]

1. Python Programming for Beginners   (score 1.959)
   python_programming.txt
   **Python** Programming for Beginners **Python** is a popular programming language that is easy to read and easy to learn. Beginners use **Python** to build websites, analys...

2. Introduction to Machine Learning   (score 1.062)
   machine_learning.txt
   ...tead of following fixed rules. Popular tools such as **Python** libraries make it easier to train models. Learning from examples lets a model recognise images, tran...

3. Chess Strategy for Beginners   (score 1.048)
   chess.txt
   ...d pins, helps players win material. Many players use **Python** programs to analyse their games.

search> :quit
```

Things to notice: `python beginners` in the default AND mode finds only the 2 pages containing both words. After `:mode or`, a query needs to match just one word, so `snakes chess` finds the snake page *and* the chess page (stemming turned `snakes` into `snake`). And `python -snake` returns every page that mentions Python **except** the snake page.

### ✅ Checkpoint

You can search from the terminal and switch between `and`/`or` and `bm25`/`tfidf`. Commit: `git add . && git commit -m "Step 9: command-line interface"`.

---

# Step 10: The crawler (`crawler.py`)

**Goal:** collect web pages automatically by **following links**, and feed them into the same index.

### How a crawler works (the 60-second version)

```
1. Put a starting ("seed") URL in a queue.
2. Take the next URL from the queue and download the page.
3. Save its text. Find its links; add NEW ones to the queue.
4. Repeat until the queue is empty or we hit a page limit.
```

Two data structures make it work: a **queue** (`collections.deque`) of URLs to visit, and a **`seen` set** so we never visit (or queue) the same URL twice. Visiting the oldest queued URL first is called *breadth-first* crawling.

### Crawler manners (not optional)

A crawler is a robot that visits other people's servers, so we follow rules:

1. **Obey `robots.txt`**, the file where a site says which paths bots may not visit.
2. **Pause between requests** (`time.sleep`), so we never hammer a server.
3. **Identify ourselves** with a `User-Agent`.
4. **Always limit the crawl** (a maximum number of pages).
5. **Stay on one website** and skip files that aren't web pages.
6. **Only crawl sites you have a right to**, and never private or login-protected pages.

### Step 10.0: build a practice website first

Learning to crawl on someone else's server is rude *and* unreliable. So let's crawl **our own** tiny website. Create a folder `demo_site/` with these files.

**`demo_site/index.html`**: notice the links: a duplicate, a PDF, a private page, an outside site, an email link, plus a `<script>` whose text should be ignored.

```html
<!DOCTYPE html>
<html>
<head><title>Garden Notes - Home</title><style>body{color:red}</style></head>
<body>
  <h1>Garden Notes</h1>
  <p>Welcome to a tiny practice website about gardening and growing food.</p>
  <ul>
    <li><a href="tomatoes.html">How to grow tomatoes</a></li>
    <li><a href="/herbs.html">Herbs for a sunny windowsill</a></li>
    <li><a href="compost.html#steps">Composting kitchen waste</a></li>
    <li><a href="compost.html">Composting again (duplicate link)</a></li>
    <li><a href="guide.pdf">Download the PDF guide</a></li>
    <li><a href="private/secret.html">Private notes</a></li>
    <li><a href="https://example.com/elsewhere">An outside website</a></li>
    <li><a href="mailto:hello@example.com">Email us</a></li>
  </ul>
  <script>var tracking = "ignore this script text";</script>
</body>
</html>
```

**`demo_site/tomatoes.html`** (it has a link to a page that doesn't exist, on purpose):

```html
<!DOCTYPE html>
<html>
<head><title>How to Grow Tomatoes</title></head>
<body>
  <h1>How to Grow Tomatoes</h1>
  <p>Tomatoes need six hours of sun every day. Plant seedlings deep, water them regularly and add compost to the soil. Pick the tomatoes when they are fully red.</p>
  <p><a href="index.html">Back to home</a> | <a href="herbs.html">Herbs</a> | <a href="missing.html">A broken link</a></p>
</body>
</html>
```

**`demo_site/herbs.html`**

```html
<!DOCTYPE html>
<html>
<head><title>Herbs for a Sunny Windowsill</title></head>
<body>
  <h1>Herbs for a Sunny Windowsill</h1>
  <p>Basil, mint and coriander grow well in small pots. Water herbs when the soil feels dry, and pinch off the tips to keep the plants bushy. Fresh herbs make cooking with tomatoes even better.</p>
  <p><a href="index.html">Back to home</a></p>
</body>
</html>
```

**`demo_site/compost.html`**

```html
<!DOCTYPE html>
<html>
<head><title>Composting Kitchen Waste</title></head>
<body>
  <h1 id="steps">Composting Kitchen Waste</h1>
  <p>Compost turns vegetable scraps and dry leaves into rich soil. Keep the pile damp, turn it every week, and avoid meat or oil. After a few months you can use the compost to feed tomatoes and herbs.</p>
  <p><a href="index.html">Back to home</a></p>
</body>
</html>
```

**`demo_site/private/secret.html`** (a page our robots.txt forbids):

```html
<!DOCTYPE html>
<html>
<head><title>Private Notes</title></head>
<body><h1>Private Notes</h1><p>This page is disallowed by robots.txt, so a polite crawler never reads it.</p></body>
</html>
```

**`demo_site/robots.txt`**: the rules. `Disallow: /private/` means "bots, stay out of this folder":

```text
User-agent: *
Disallow: /private/
```

### Step 10.1: teach the loader about crawled pages

The crawler will save pages to `crawled/pages.json` in the **same shape** as our text documents. Add these two functions to `loader.py` (the imports are already there from Step 2):

```python
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
```

`load_all` merges both sources. Because crawled pages use their URL as their id, ids never clash with file names. This is where choosing the dictionary-of-dictionaries shape in Step 2 pays off: **no other code has to change.**

### Step 10.2: the crawler, piece by piece

Create `crawler.py`.

> **⏸ Pause and try.** Before reading on, write just `extract_links(soup, page_url)`. Hints: BeautifulSoup's `soup.find_all("a", href=True)` finds links; `urllib.parse.urljoin(page_url, href)` turns a relative link like `/about` into a full URL.

**Imports and settings:**

```python
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
```

**Tidying URLs.** Two different addresses can lead to the same page (`page.html#top` and `page.html`, or `/` and `/index.html`). If we treat them as different, we index the page twice. (I learned this the hard way while testing: my first crawl visited the home page twice!) `clean_url` gives every page one canonical address:

```python
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
```

- `urldefrag` cuts off the `#fragment`.
- `urlparse(url).netloc` is the website part (`localhost:8000`). Comparing two of them tells us whether a link stays on the same site.

**Pulling links and text out of a page:**

```python
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
```

- We return a **set** of links, which removes duplicates for free.
- `startswith(("http://", "https://"))` drops `mailto:` and `javascript:` links.
- `soup(["script", "style", "noscript"])` finds those tags; `.decompose()` deletes them, so code and CSS don't become "text".
- `get_text(separator=" ")` collects all visible text, and `" ".join(text.split())` tidies the spacing.

Try these helpers on a scrap of HTML:

```pycon
>>> from bs4 import BeautifulSoup
>>> from crawler import extract_links, extract_text, clean_url
>>> html = '<p>Hi</p><a href="/about">About</a> <a href="page2.html#top">Two</a> <a href="photo.jpg">Photo</a> <a href="mailto:me@x.com">Mail</a><script>var x = 1;</script>'
>>> soup = BeautifulSoup(html, "html.parser")
>>> sorted(extract_links(soup, "https://site.com/dir/start.html"))
['https://site.com/about', 'https://site.com/dir/page2.html']
>>> extract_text(soup)
'Hi About Two Photo Mail'
>>> clean_url("https://x.com/docs/index.html#top")
'https://x.com/docs/'
```

**Reading `robots.txt`:**

```python
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
```

Python's `RobotFileParser` understands the rules format. We download the file ourselves (so we control the timeout and `User-Agent`), then hand its lines to `parser.parse(...)`. The status code decides what to do: `200` means "here are the rules", `401`/`403` means "keep out" (so we obey by disallowing everything), and anything else (like `404` = no robots.txt) means there are no rules.

**Downloading one page safely:**

```python
def fetch(url):
    """Download a page. Returns the response, or None if anything went wrong."""
    try:
        return requests.get(url, timeout=10, headers={"User-Agent": USER_AGENT})
    except requests.RequestException as error:
        print(f"  could not fetch {url}: {error}")
        return None
```

`timeout=10` is essential: without it a slow server can freeze your program forever. The network fails all the time (no internet, bad domain, server down), so we **catch** `requests.RequestException` and return `None` rather than crash the whole crawl.

**The crawl loop itself:**

```python
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
```

Follow one round of the `while` loop:

1. `queue.popleft()` takes the **oldest** URL (first in, first out).
2. `robots.can_fetch(...)` asks "am I allowed?" If not, skip it.
3. `fetch(url)`, then `time.sleep(delay)`: the polite pause.
4. Skip anything that isn't a successful (`200`) HTML page.
5. Parse it, **save** `{"title", "url", "text"}` in `pages`.
6. For every link on the page that is on the **same site** and **not seen before**, add it to `seen` and to the `queue`. `sorted(links)` makes the crawl order the same every run.
7. The loop stops when the queue is empty **or** `len(pages) < max_pages` becomes false. This is your safety brake.

**Saving and the command-line entry point:**

```python
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
```

`path.parent.mkdir(parents=True, exist_ok=True)` creates the `crawled/` folder if it doesn't exist (and doesn't complain if it does).

### Try it: crawl your own website

Open **two** terminals (both in the project folder, environment active).

**Terminal 1**: serve the practice site:

```bash
python -m http.server 8000 --directory demo_site
```

**Terminal 2**: crawl it (10 pages max, no delay, since it's your own server):

```text
$ python crawler.py http://localhost:8000/ 10 0
Crawling http://localhost:8000/ (max 10 pages, 0.0s delay)
  [1/10] http://localhost:8000/
  [2/10] http://localhost:8000/compost.html
  [3/10] http://localhost:8000/herbs.html
  skipped (robots.txt): http://localhost:8000/private/secret.html
  [4/10] http://localhost:8000/tomatoes.html
  skipped (status 404, text/html;charset=utf-8): http://localhost:8000/missing.html
Saved 4 pages to minisearch/crawled/pages.json
Now rebuild the index:  python cli.py --rebuild
```

Look at what the crawler did:

- ✅ visited the home page (once!), `compost.html`, `herbs.html`, `tomatoes.html`
- ✅ **skipped** `private/secret.html` because of `robots.txt`
- ✅ **skipped** `missing.html`, the broken link (status 404)
- ✅ ignored the PDF, the email link, and the outside website

Now rebuild the index so the crawled pages are included, and search them:

```text
$ python cli.py --rebuild
MiniSearch ready: 16 documents, 326 unique terms.
Type :help for help.

search> tomatoes compost

3 result(s) for 'tomatoes compost'  [mode=and, method=bm25]

1. How to Grow Tomatoes   (score 4.186)
   http://localhost:8000/tomatoes.html
   How to Grow **Tomatoes** How to Grow **Tomatoes** **Tomatoes** need six hours of sun every day. Plant seedlings deep, water them regularly and add **compost** to the soil. Pick...

2. Composting Kitchen Waste   (score 4.163)
   http://localhost:8000/compost.html
   **Composting** Kitchen Waste **Composting** Kitchen Waste **Compost** turns vegetable scraps and dry leaves into rich soil. Keep the pile damp, turn it every week, and avoi...

3. Garden Notes - Home   (score 3.542)
   http://localhost:8000/
   ...ebsite about gardening and growing food. How to grow **tomatoes** Herbs for a sunny windowsill **Composting** kitchen waste **Composting** again (duplicate link) Download t...

search> :quit
```

The new results show a **URL** where local files show a file name, and the snippet came from a web page.

### Try it on a real practice site

When you're comfortable, crawl a site that *exists to be crawled*. Keep the default delay (**1 second**) and a small limit:

```bash
python crawler.py https://quotes.toscrape.com 20
python cli.py --rebuild
```

(`books.toscrape.com` is another good one.) If a real site doesn't behave, check `robots.txt`, your internet connection, and whether the site uses JavaScript to show content: our crawler only reads the HTML the server sends.

### ✅ Checkpoint

The crawl skips `private/`, saves `crawled/pages.json`, and searching finds crawled content. Commit: `git add . && git commit -m "Step 10: crawler"`.

---

# Step 11: A web interface (`app.py`)

**Goal:** search from a browser, with highlighted snippets.

### Flask in 60 seconds

**Flask** is a small Python tool for making web apps. Three ideas:

- A **route** connects a URL to a Python function. Visiting `/search` runs the function under `@app.route("/search")`. (`@...` lines are *decorators*: "attach this behaviour to the function below". Just use them like a recipe for now.)
- **`request.args.get("q")`** reads the `?q=python` part of a URL, which is how the search form sends what you typed.
- A **template** is an HTML file with blanks that Python fills in. `render_template("results.html", query=query)` fills the blanks.

> **⏸ Pause and try.** Write a minimal `app.py` with one route `/` returning `"Hello, search engine!"`, run it and open http://127.0.0.1:5000.

### The app (`app.py`)

```python
"""app.py - Stage 10: a web interface for the search engine.

Run:  python app.py      then open http://127.0.0.1:5000
"""

from flask import Flask, abort, render_template, request

from engine import load_engine
from snippets import highlight_parts
```

```python
def create_app(engine=None):
    """Build the web app. Tests pass in a small engine; normally we load the real one."""
    app = Flask(__name__)
    if engine is None:
        engine = load_engine()

    @app.route("/")
    def home():
        return render_template("home.html", stats=engine.stats())

    @app.route("/search")
    def search_page():
        query = request.args.get("q", "").strip()
        mode = request.args.get("mode", "and")
        if mode not in ("and", "or"):
            mode = "and"

        response = None
        if query:
            response = engine.search(query, mode=mode)
            for result in response["results"]:
                result["parts"] = highlight_parts(result["snippet"], response["terms"])
        return render_template("results.html", query=query, mode=mode, response=response)

    @app.route("/doc/<doc_id>")
    def view_document(doc_id):
        document = engine.documents.get(doc_id)
        if document is None:
            abort(404)
        return render_template("document.html", doc_id=doc_id, document=document)

    return app
```

- **Why a function that *builds* the app (`create_app`)?** So tests can hand it a small, fake engine, while normal use loads the real one. It's a very common Flask pattern. The route functions are defined *inside* `create_app`, so they can see the `engine` variable.
- **`home`** shows the welcome page with statistics.
- **`search_page`** reads `q` and `mode` from the URL, validates `mode` (never trust input from a browser!), runs the search, and attaches `parts` to each result: the snippet split into `(piece, is_match)` pairs from Step 7.
- **`view_document`** shows a whole local document. `abort(404)` returns the standard "not found" error when the id is unknown.

```python
if __name__ == "__main__":
    create_app().run(debug=True)
```

`debug=True` gives you automatic reloading and helpful error pages while developing. **Never leave it on for a public website.**

### The templates

Create the folder `templates/` and add four files. Flask looks there automatically.

**`templates/base.html`**: the shared page frame (header with the search form, plus a bit of CSS). Pages *extend* it, so we write the layout once:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}MiniSearch{% endblock %}</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 0 auto; padding: 1rem; line-height: 1.5; color: #222; }
    header { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
    .logo { font-weight: 700; font-size: 1.3rem; text-decoration: none; color: #1a56db; }
    form { display: flex; gap: .5rem; flex: 1; }
    input[type=text] { flex: 1; padding: .5rem; font-size: 1rem; }
    select, button { padding: .5rem; font-size: 1rem; }
    article { margin: 1.5rem 0; }
    article h3 { margin: 0; }
    .source { color: #2f7d32; font-size: .85rem; }
    .meta { color: #666; }
    mark { background: #fff3a3; }
    pre { white-space: pre-wrap; font-family: inherit; }
  </style>
</head>
<body>
  <header>
    <a class="logo" href="{{ url_for('home') }}">MiniSearch</a>
    <form action="{{ url_for('search_page') }}" method="get">
      <input type="text" name="q" value="{{ query | default('') }}" placeholder="Search..." autofocus>
      <select name="mode">
        <option value="and" {% if mode | default('and') == 'and' %}selected{% endif %}>all words</option>
        <option value="or" {% if mode | default('and') == 'or' %}selected{% endif %}>any word</option>
      </select>
      <button type="submit">Search</button>
    </form>
  </header>
  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

Jinja (Flask's template language) has two kinds of markers: `{{ something }}` **prints** a value, and `{% something %}` runs **logic** (`if`, `for`, `block`). `{% block content %}` is a hole that child pages fill. `url_for('home')` builds a URL from a function name, so links never break if you rename a route.

**`templates/home.html`**

```html
{% extends "base.html" %}

{% block content %}
  <h1>Search {{ stats.documents }} documents</h1>
  <p class="meta">{{ stats.terms }} unique words are in the index. Try <em>python beginners</em>,
     <em>snakes</em>, or <em>learning -python</em> (a minus sign excludes a word).</p>
{% endblock %}
```

**`templates/results.html`**: the interesting one:

```html
{% extends "base.html" %}

{% block title %}{{ query }} - MiniSearch{% endblock %}

{% block content %}
  {% if not response %}
    <p class="meta">Type something to search.</p>
  {% elif response.total == 0 %}
    <p>No results for <strong>{{ query }}</strong>. Try fewer words, or switch to "any word".</p>
  {% else %}
    <p class="meta">{{ response.total }} result{{ "" if response.total == 1 else "s" }} for <strong>{{ query }}</strong></p>
    {% for r in response.results %}
      <article>
        <h3>
          {% if r.url %}
            <a href="{{ r.url }}">{{ r.title }}</a>
          {% else %}
            <a href="{{ url_for('view_document', doc_id=r.doc_id) }}">{{ r.title }}</a>
          {% endif %}
        </h3>
        <div class="source">{{ r.url or r.doc_id }} &middot; score {{ "%.3f" | format(r.score) }}</div>
        <p>{% for piece, is_match in r.parts %}{% if is_match %}<mark>{{ piece }}</mark>{% else %}{{ piece }}{% endif %}{% endfor %}</p>
      </article>
    {% endfor %}
  {% endif %}
{% endblock %}
```

Read it top to bottom:

- `{% if not response %}` (no query yet) → a hint; `{% elif response.total == 0 %}` → "no results"; `{% else %}` → show results.
- `{% for r in response.results %}` loops over results, and `r.title`, `r.url` read the fields of each result dictionary.
- Local files have no `url`, so `{% if r.url %}` picks between an external link and our own `/doc/...` page.
- The line with `{% for piece, is_match in r.parts %}` loops over the highlighted pieces and wraps matches in `<mark>`.

> **Security lesson.** Notice we never build HTML by pasting strings together. Jinja **escapes** everything printed with `{{ ... }}`, so if someone searches for `<script>alert(1)</script>`, the browser shows it as harmless text. Our tests check this. Building highlights from `(piece, is_match)` pairs, instead of inserting `<mark>` into a string, is what keeps it safe.

**`templates/document.html`**

```html
{% extends "base.html" %}

{% block title %}{{ document.title }} - MiniSearch{% endblock %}

{% block content %}
  <h1>{{ document.title }}</h1>
  <p class="meta">{{ doc_id }}</p>
  <pre>{{ document.text }}</pre>
{% endblock %}
```

### Try it

Start the server from your project folder:

```text
$ python app.py
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Debugger is active!
127.0.0.1 - - [30/Sep/2026 10:32:46] "GET /search?q=python+beginners HTTP/1.1" 200 -

(then, in the browser: GET /search?q=python+beginners -> HTTP 200)
Result titles on that page: Python Programming for Beginners; Chess Strategy for Beginners
```

Open **http://127.0.0.1:5000** and try: `python beginners`, then switch the dropdown to "any word", `snakes`, and `python -snake`. Click a local result to see the full document; click a crawled one to go to its web address. Stop the server with `Ctrl+C`.

### ✅ Checkpoint

The site loads, searches work, matches are highlighted, and `python -snake` hides the snake page. Commit: `git add . && git commit -m "Step 11: web interface"`.

---

# Step 12: Automated tests (`tests/`)

**Goal:** a safety net: a suite of tests that proves every part works and **tells you instantly** if a future change breaks something.

### How tests work

A test is a function whose name starts with `test_` that uses **`assert`**: `assert 2 + 2 == 4` does nothing if true and raises an error if false. **pytest** finds every `test_*` function in `tests/`, runs it, and reports the results.

Three pytest features we use:

- **Fixtures** (in `tests/conftest.py`) are reusable set-up. A test that lists a fixture as a parameter receives its value.
- **`tmp_path`** gives each test a fresh temporary folder, so tests never touch your real files.
- **`monkeypatch`** temporarily changes something (like our `USE_STEMMING` switch) and automatically restores it.

**`tests/conftest.py`**: the shared tiny corpus, whose answers we can calculate by hand:

```python
"""Shared test setup: a tiny corpus with answers we can work out by hand."""

import pytest

from engine import SearchEngine


@pytest.fixture
def tiny_documents():
    return {
        "doc1.txt": {"title": "Python fun", "url": "", "text": "Python is a fun language to learn."},
        "doc2.txt": {"title": "Fast Python", "url": "", "text": "Learning Python is fun and Python is fast."},
        "doc3.txt": {"title": "Cats", "url": "", "text": "Cats are fun animals."},
    }


@pytest.fixture
def tiny_engine(tiny_documents):
    engine = SearchEngine()
    engine.build(tiny_documents)
    return engine
```

**`tests/test_processor.py`**

```python
import processor
from processor import process, remove_stop_words, stem, tokenize


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Hello, World!!") == ["hello", "world"]


def test_tokenize_handles_extra_spaces_and_empty_text():
    assert tokenize("   lots   of   spaces  ") == ["lots", "of", "spaces"]
    assert tokenize("") == []


def test_tokenize_joins_apostrophes_and_keeps_digits():
    assert tokenize("Don't stop, it’s T20!") == ["dont", "stop", "its", "t20"]


def test_tokenize_splits_on_dashes_and_slashes():
    assert tokenize("well-known/popular") == ["well", "known", "popular"]


def test_remove_stop_words():
    assert remove_stop_words(["python", "is", "a", "fun", "language"]) == ["python", "fun", "language"]


def test_stem_common_endings():
    assert stem("learning") == "learn"
    assert stem("learned") == "learn"
    assert stem("learns") == "learn"
    assert stem("running") == "run"
    assert stem("programming") == "program"
    assert stem("snakes") == "snake"


def test_stem_leaves_short_or_special_words_alone():
    assert stem("is") == "is"
    assert stem("bus") == "bus"
    assert stem("class") == "class"
    assert stem("focus") == "focus"
    assert stem("speed") == "speed"


def test_process_full_pipeline():
    assert process("The Quick brown FOX, jumped!") == ["quick", "brown", "fox", "jump"]


def test_process_without_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", False)
    assert process("Learning Python is fun") == ["learning", "python", "fun"]


def test_process_with_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", True)
    assert process("Learning Python is fun") == ["learn", "python", "fun"]
```

The other test files follow the same pattern. Type them from the listings in [Appendix A](#appendix-a-complete-code): `test_loader_indexer.py`, `test_search.py`, `test_snippets_storage_engine.py`, `test_crawler.py` and `test_app.py`.

Two tests are worth studying:

- **`test_tfidf_matches_hand_calculation`** (in `test_search.py`) checks our scoring against the paper calculation from Step 6, which proves the maths is right, not just "runs without crashing".
- **`test_crawl_demo_site`** (in `test_crawler.py`) starts a real web server on a spare port, serving your `demo_site/`, and crawls it. The test proves `robots.txt` is obeyed and scripts are ignored, with no internet needed.

### Run everything

```text
$ python -m pytest -q
......................................................                   [100%]
54 passed in 1.23s
```

### A true story about failing tests

When I first ran this suite, **3 tests failed**. The code was fine. My *tests* were wrong: I'd forgotten that stemming turns `jumped` into `jump`, and I'd assumed a document's title was part of its text in the test data. That's normal. When a test fails, the question is: **is the code wrong, or is my expectation wrong?** Read the message, work out which, and fix it.

> **⏸ Try this.** Break something on purpose: in `processor.py`, delete the line `text = text.lower()`. Run `pytest`, and watch several tests turn red. Then undo it. That's the safety net working.

### ✅ Checkpoint

`pytest` shows all tests passing. Commit: `git add . && git commit -m "Step 12: tests"`.

---

# Step 13: Make it yours (and the road to AI)

You've built a complete search engine. Here's where to go next, from easiest to hardest.

### Small upgrades (an evening each)

1. **Skip the title in snippets.** Right now the excerpt begins with the title line again. Change `make_snippet` to skip the first line.
2. **Pagination.** Show results 1 to 10, then add a "Next" link (`?page=2`).
3. **Title boost.** Make matches in the title count double. Hint: in `build_index`, count title tokens twice.
4. **Your own documents.** Put your own notes in `data/`, delete `index.json`, and search them.
5. **More commands** for the CLI: `:top 10` to change the number of results.

### Medium (a weekend each)

6. **Phrase search** (`"machine learning"`): store word *positions* in the index and require them to be consecutive.
7. **"Did you mean...?"** using *edit distance* (how many letter changes turn one word into another).
8. **Real stemmer:** replace `stem()` with NLTK's `PorterStemmer` and compare results using your tests.
9. **Measure quality:** write 10 test queries with the documents you *expect* to win, and compute **precision** and **recall** (see Stage 9 in the concepts guide). Compare TF-IDF vs BM25 with real numbers.
10. **Incremental indexing:** add a new document without rebuilding everything.

### Bigger (the AI direction)

Your engine matches **words**. Searching `automobile` won't find a page about `cars`, and searching `python` can't tell snakes from code. AI-based search matches **meaning**:

1. Learn what an **embedding** is: a list of numbers representing the *meaning* of a text.
2. Write **cosine similarity** yourself (about 8 lines of Python).
3. Use `sentence-transformers` to embed every document and the query, then rank by similarity.
4. Combine that with the BM25 score you built into **hybrid search**.
5. Feed the top results to a language model to *answer* questions: **RAG** (retrieval-augmented generation). The engine you just built *is* the retrieval half.

The concepts guide (`README.md`, Stage 10) walks through steps 1 to 5 with the maths worked out by hand.

### A closing thought

You didn't follow a tutorial to *the end*; you built a system, piece by piece, and you can explain each piece. The next time you want to build something, use the same method: **state the goal in plain English, shrink it to the smallest piece, get that piece working, test it, commit, repeat.**

---

# Appendix A: Complete code

Every file of the project, exactly as tested. (The `data/` and `demo_site/` files are listed in Steps 1 and 10.)

### `processor.py`

```python
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
```

### `loader.py`

```python
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
```

### `indexer.py`

```python
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
```

### `search.py`

```python
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
```

### `snippets.py`

```python
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
```

### `storage.py`

```python
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
```

### `engine.py`

```python
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
```

### `cli.py`

```python
"""cli.py - a search prompt for your terminal.

Run:  python cli.py            (loads the saved index, or builds it the first time)
      python cli.py --rebuild  (throw the saved index away and build a new one)
"""

import sys

from engine import load_engine
from snippets import highlight

HELP = """Type words to search. Commands:
  -word           exclude a word          (python -snake)
  :mode and|or    all words / any word    (default: and)
  :method bm25|tfidf   ranking formula    (default: bm25)
  :stats          show index statistics
  :help           show this help
  :quit           leave"""


def show_results(response, query, mode, method):
    """Print one search response nicely."""
    total = response["total"]
    print(f"\n{total} result(s) for '{query}'  [mode={mode}, method={method}]\n")

    for rank, result in enumerate(response["results"], start=1):
        source = result["url"] or result["doc_id"]
        print(f"{rank}. {result['title']}   (score {result['score']:.3f})")
        print(f"   {source}")
        print("   " + highlight(result["snippet"], response["terms"]))
        print()


def main():
    rebuild = "--rebuild" in sys.argv
    engine = load_engine(rebuild=rebuild)

    stats = engine.stats()
    print(f"MiniSearch ready: {stats['documents']} documents, {stats['terms']} unique terms.")
    print("Type :help for help.\n")

    mode = "and"
    method = "bm25"

    while True:
        try:
            query = input("search> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if query == "":
            continue

        if query.startswith(":"):
            parts = query.split()
            command = parts[0]
            if command in (":quit", ":q"):
                break
            elif command == ":help":
                print(HELP)
            elif command == ":stats":
                print(engine.stats())
            elif command == ":mode" and len(parts) == 2 and parts[1] in ("and", "or"):
                mode = parts[1]
                print(f"mode = {mode}")
            elif command == ":method" and len(parts) == 2 and parts[1] in ("bm25", "tfidf"):
                method = parts[1]
                print(f"method = {method}")
            else:
                print("Unknown command. Type :help")
            continue

        response = engine.search(query, mode=mode, method=method, top_k=5)
        show_results(response, query, mode, method)


if __name__ == "__main__":
    main()
```

### `crawler.py`

```python
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
```

### `app.py`

```python
"""app.py - Stage 10: a web interface for the search engine.

Run:  python app.py      then open http://127.0.0.1:5000
"""

from flask import Flask, abort, render_template, request

from engine import load_engine
from snippets import highlight_parts


def create_app(engine=None):
    """Build the web app. Tests pass in a small engine; normally we load the real one."""
    app = Flask(__name__)
    if engine is None:
        engine = load_engine()

    @app.route("/")
    def home():
        return render_template("home.html", stats=engine.stats())

    @app.route("/search")
    def search_page():
        query = request.args.get("q", "").strip()
        mode = request.args.get("mode", "and")
        if mode not in ("and", "or"):
            mode = "and"

        response = None
        if query:
            response = engine.search(query, mode=mode)
            for result in response["results"]:
                result["parts"] = highlight_parts(result["snippet"], response["terms"])
        return render_template("results.html", query=query, mode=mode, response=response)

    @app.route("/doc/<doc_id>")
    def view_document(doc_id):
        document = engine.documents.get(doc_id)
        if document is None:
            abort(404)
        return render_template("document.html", doc_id=doc_id, document=document)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
```

### `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}MiniSearch{% endblock %}</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 720px; margin: 0 auto; padding: 1rem; line-height: 1.5; color: #222; }
    header { display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
    .logo { font-weight: 700; font-size: 1.3rem; text-decoration: none; color: #1a56db; }
    form { display: flex; gap: .5rem; flex: 1; }
    input[type=text] { flex: 1; padding: .5rem; font-size: 1rem; }
    select, button { padding: .5rem; font-size: 1rem; }
    article { margin: 1.5rem 0; }
    article h3 { margin: 0; }
    .source { color: #2f7d32; font-size: .85rem; }
    .meta { color: #666; }
    mark { background: #fff3a3; }
    pre { white-space: pre-wrap; font-family: inherit; }
  </style>
</head>
<body>
  <header>
    <a class="logo" href="{{ url_for('home') }}">MiniSearch</a>
    <form action="{{ url_for('search_page') }}" method="get">
      <input type="text" name="q" value="{{ query | default('') }}" placeholder="Search..." autofocus>
      <select name="mode">
        <option value="and" {% if mode | default('and') == 'and' %}selected{% endif %}>all words</option>
        <option value="or" {% if mode | default('and') == 'or' %}selected{% endif %}>any word</option>
      </select>
      <button type="submit">Search</button>
    </form>
  </header>
  <main>
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

### `templates/home.html`

```html
{% extends "base.html" %}

{% block content %}
  <h1>Search {{ stats.documents }} documents</h1>
  <p class="meta">{{ stats.terms }} unique words are in the index. Try <em>python beginners</em>,
     <em>snakes</em>, or <em>learning -python</em> (a minus sign excludes a word).</p>
{% endblock %}
```

### `templates/results.html`

```html
{% extends "base.html" %}

{% block title %}{{ query }} - MiniSearch{% endblock %}

{% block content %}
  {% if not response %}
    <p class="meta">Type something to search.</p>
  {% elif response.total == 0 %}
    <p>No results for <strong>{{ query }}</strong>. Try fewer words, or switch to "any word".</p>
  {% else %}
    <p class="meta">{{ response.total }} result{{ "" if response.total == 1 else "s" }} for <strong>{{ query }}</strong></p>
    {% for r in response.results %}
      <article>
        <h3>
          {% if r.url %}
            <a href="{{ r.url }}">{{ r.title }}</a>
          {% else %}
            <a href="{{ url_for('view_document', doc_id=r.doc_id) }}">{{ r.title }}</a>
          {% endif %}
        </h3>
        <div class="source">{{ r.url or r.doc_id }} &middot; score {{ "%.3f" | format(r.score) }}</div>
        <p>{% for piece, is_match in r.parts %}{% if is_match %}<mark>{{ piece }}</mark>{% else %}{{ piece }}{% endif %}{% endfor %}</p>
      </article>
    {% endfor %}
  {% endif %}
{% endblock %}
```

### `templates/document.html`

```html
{% extends "base.html" %}

{% block title %}{{ document.title }} - MiniSearch{% endblock %}

{% block content %}
  <h1>{{ document.title }}</h1>
  <p class="meta">{{ doc_id }}</p>
  <pre>{{ document.text }}</pre>
{% endblock %}
```

### `tests/conftest.py`

```python
"""Shared test setup: a tiny corpus with answers we can work out by hand."""

import pytest

from engine import SearchEngine


@pytest.fixture
def tiny_documents():
    return {
        "doc1.txt": {"title": "Python fun", "url": "", "text": "Python is a fun language to learn."},
        "doc2.txt": {"title": "Fast Python", "url": "", "text": "Learning Python is fun and Python is fast."},
        "doc3.txt": {"title": "Cats", "url": "", "text": "Cats are fun animals."},
    }


@pytest.fixture
def tiny_engine(tiny_documents):
    engine = SearchEngine()
    engine.build(tiny_documents)
    return engine
```

### `tests/test_processor.py`

```python
import processor
from processor import process, remove_stop_words, stem, tokenize


def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Hello, World!!") == ["hello", "world"]


def test_tokenize_handles_extra_spaces_and_empty_text():
    assert tokenize("   lots   of   spaces  ") == ["lots", "of", "spaces"]
    assert tokenize("") == []


def test_tokenize_joins_apostrophes_and_keeps_digits():
    assert tokenize("Don't stop, it’s T20!") == ["dont", "stop", "its", "t20"]


def test_tokenize_splits_on_dashes_and_slashes():
    assert tokenize("well-known/popular") == ["well", "known", "popular"]


def test_remove_stop_words():
    assert remove_stop_words(["python", "is", "a", "fun", "language"]) == ["python", "fun", "language"]


def test_stem_common_endings():
    assert stem("learning") == "learn"
    assert stem("learned") == "learn"
    assert stem("learns") == "learn"
    assert stem("running") == "run"
    assert stem("programming") == "program"
    assert stem("snakes") == "snake"


def test_stem_leaves_short_or_special_words_alone():
    assert stem("is") == "is"
    assert stem("bus") == "bus"
    assert stem("class") == "class"
    assert stem("focus") == "focus"
    assert stem("speed") == "speed"


def test_process_full_pipeline():
    assert process("The Quick brown FOX, jumped!") == ["quick", "brown", "fox", "jump"]


def test_process_without_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", False)
    assert process("Learning Python is fun") == ["learning", "python", "fun"]


def test_process_with_stemming(monkeypatch):
    monkeypatch.setattr(processor, "USE_STEMMING", True)
    assert process("Learning Python is fun") == ["learn", "python", "fun"]
```

### `tests/test_loader_indexer.py`

```python
import pytest

from indexer import build_index
from loader import load_crawled_pages, load_text_files


def test_load_text_files_uses_first_line_as_title(tmp_path):
    (tmp_path / "a.txt").write_text("My Title\nSome body text.", encoding="utf-8")
    documents = load_text_files(tmp_path)
    assert documents["a.txt"]["title"] == "My Title"
    assert "Some body text." in documents["a.txt"]["text"]


def test_load_text_files_empty_file_uses_file_name(tmp_path):
    (tmp_path / "blank.txt").write_text("", encoding="utf-8")
    assert load_text_files(tmp_path)["blank.txt"]["title"] == "blank"


def test_load_text_files_ignores_other_extensions(tmp_path):
    (tmp_path / "notes.md").write_text("hello", encoding="utf-8")
    assert load_text_files(tmp_path) == {}


def test_load_text_files_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_files(tmp_path / "nope")


def test_load_crawled_pages_missing_file_gives_empty_dict(tmp_path):
    assert load_crawled_pages(tmp_path / "nope.json") == {}


def test_build_index_counts_and_lengths(tiny_documents):
    index, doc_lengths = build_index(tiny_documents)
    assert index["python"] == {"doc1.txt": 1, "doc2.txt": 2}
    assert index["cat"] == {"doc3.txt": 1}                     # "Cats" was stemmed to "cat"
    assert index["learn"] == {"doc1.txt": 1, "doc2.txt": 1}    # learn + learning
    assert doc_lengths == {"doc1.txt": 4, "doc2.txt": 5, "doc3.txt": 3}


def test_build_index_empty_corpus():
    assert build_index({}) == ({}, {})
```

### `tests/test_search.py`

```python
import math

from search import find_matches, parse_query, score_documents, search


def test_parse_query_splits_included_and_excluded_words():
    assert parse_query("Python -snakes Fun") == (["python", "fun"], ["snake"])


def test_parse_query_all_stop_words_gives_nothing():
    assert parse_query("the is a") == ([], [])


def test_and_search_needs_every_word(tiny_engine):
    assert find_matches(["python", "fun"], [], tiny_engine.index, "and") == {"doc1.txt", "doc2.txt"}
    assert find_matches(["cat", "python"], [], tiny_engine.index, "and") == set()


def test_or_search_needs_any_word(tiny_engine):
    assert find_matches(["cat", "python"], [], tiny_engine.index, "or") == {"doc1.txt", "doc2.txt", "doc3.txt"}


def test_exclude_removes_documents(tiny_engine):
    assert find_matches(["fun"], ["cat"], tiny_engine.index, "and") == {"doc1.txt", "doc2.txt"}


def test_unknown_words_and_empty_queries(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    assert search("zzzz", index, lengths) == []
    assert search("", index, lengths) == []
    assert search("the", index, lengths) == []
    assert search("python zzzz", index, lengths, mode="and") == []
    assert [d for d, _ in search("python zzzz", index, lengths, mode="or")] == ["doc2.txt", "doc1.txt"]


def test_queries_are_case_insensitive_and_stemmed(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    assert search("PYTHON", index, lengths) == search("python", index, lengths)
    assert {d for d, _ in search("learning", index, lengths)} == {"doc1.txt", "doc2.txt"}


def test_tfidf_matches_hand_calculation(tiny_engine):
    # "python" is in 2 of 3 docs, so idf = ln(3/2). doc2 has it 2 times in 5 words.
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    scores = score_documents(["python"], {"doc1.txt", "doc2.txt"}, index, lengths, "tfidf")
    expected_doc2 = (2 / 5) * math.log(3 / 2)                   # = 0.162
    assert math.isclose(scores["doc2.txt"], expected_doc2)


def test_word_in_every_document_has_zero_tfidf(tiny_engine):
    index, lengths = tiny_engine.index, tiny_engine.doc_lengths
    scores = score_documents(["fun"], set(lengths), index, lengths, "tfidf")
    assert all(score == 0 for score in scores.values())


def test_bm25_gives_positive_scores_and_sorted_results(tiny_engine):
    ranked = search("python", tiny_engine.index, tiny_engine.doc_lengths, method="bm25")
    scores = [score for _, score in ranked]
    assert all(score > 0 for score in scores)
    assert scores == sorted(scores, reverse=True)


def test_rare_word_outranks_common_word(tiny_engine):
    # doc3 is the only one with "cat" (rare); every doc has "fun" (common).
    ranked = search("fun cat", tiny_engine.index, tiny_engine.doc_lengths, mode="or")
    assert ranked[0][0] == "doc3.txt"


def test_real_sample_data_finds_expected_documents():
    from engine import DATA_FOLDER
    from engine import SearchEngine
    from loader import load_text_files

    engine = SearchEngine()
    engine.build(load_text_files(DATA_FOLDER))
    both = [d for d, _ in search("python beginners", engine.index, engine.doc_lengths)]
    assert set(both) == {"python_programming.txt", "chess.txt"}
    assert [d for d, _ in search("snakes", engine.index, engine.doc_lengths)] == ["python_snakes.txt"]
    no_snakes = [d for d, _ in search("python -snake", engine.index, engine.doc_lengths)]
    assert "python_snakes.txt" not in no_snakes and "python_programming.txt" in no_snakes
```

### `tests/test_snippets_storage_engine.py`

```python
from engine import SearchEngine, load_engine
from snippets import highlight, highlight_parts, make_snippet


def test_snippet_is_centred_on_the_first_match():
    text = "word " * 50 + "needle " + "word " * 50
    snippet = make_snippet(text, ["needle"], width=60)
    assert "needle" in snippet
    assert snippet.startswith("...") and snippet.endswith("...")
    assert len(snippet) <= 66


def test_snippet_without_match_uses_the_beginning():
    assert make_snippet("Short text here.", ["zzz"]) == "Short text here."


def test_highlight_wraps_whole_words_starting_with_a_term():
    assert highlight("Learning is fun to learn", ["learn"]) == "**Learning** is fun to **learn**"


def test_highlight_without_terms_changes_nothing():
    assert highlight("Nothing to see", []) == "Nothing to see"
    assert highlight_parts("Nothing to see", []) == [("Nothing to see", False)]


def test_highlight_parts_flags_matches():
    assert highlight_parts("a cat sat", ["cat"]) == [("a ", False), ("cat", True), (" sat", False)]


def test_save_and_load_round_trip(tiny_engine, tmp_path):
    path = tmp_path / "index.json"
    tiny_engine.save(path)
    loaded = SearchEngine()
    loaded.load(path)
    assert loaded.index == tiny_engine.index
    assert loaded.doc_lengths == tiny_engine.doc_lengths
    assert loaded.documents == tiny_engine.documents


def test_load_engine_builds_then_reuses_saved_index(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "a.txt").write_text("Apples\nApples are red fruit.", encoding="utf-8")
    index_file = tmp_path / "index.json"
    kwargs = dict(index_file=index_file, data_folder=data, crawled_file=tmp_path / "none.json")

    first = load_engine(**kwargs)
    assert index_file.exists()

    (data / "b.txt").write_text("Bananas\nBananas are yellow.", encoding="utf-8")
    assert load_engine(**kwargs).stats()["documents"] == 1          # loaded the saved index
    assert load_engine(rebuild=True, **kwargs).stats()["documents"] == 2   # rebuilt


def test_engine_search_returns_everything_an_interface_needs(tiny_engine):
    response = tiny_engine.search("python fun")
    assert response["terms"] == ["python", "fun"]
    assert response["total"] == 2
    top = response["results"][0]
    assert set(top) == {"doc_id", "title", "url", "score", "snippet"}


def test_engine_search_top_k_limits_results_but_not_total(tiny_engine):
    response = tiny_engine.search("fun", mode="or", top_k=1)
    assert len(response["results"]) == 1
    assert response["total"] == 3


def test_stats(tiny_engine):
    stats = tiny_engine.stats()
    assert stats["documents"] == 3
    assert stats["terms"] > 0
    assert SearchEngine().stats() == {"documents": 0, "terms": 0, "average_length": 0}
```

### `tests/test_crawler.py`

```python
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
```

### `tests/test_app.py`

```python
import pytest

from app import create_app


@pytest.fixture
def client(tiny_engine):
    return create_app(tiny_engine).test_client()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Search 3 documents" in response.get_data(as_text=True)


def test_search_shows_results_with_highlights(client):
    html = client.get("/search?q=python").get_data(as_text=True)
    assert "2 results for" in html
    assert "<mark>Python</mark>" in html


def test_search_with_no_results(client):
    html = client.get("/search?q=zzzz").get_data(as_text=True)
    assert "No results for" in html


def test_empty_query_asks_for_input(client):
    assert "Type something to search" in client.get("/search").get_data(as_text=True)


def test_or_mode_finds_more(client):
    assert "3 results" in client.get("/search?q=python+cats&mode=or").get_data(as_text=True)


def test_user_input_is_escaped(client):
    html = client.get("/search?q=<script>alert(1)</script>").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html


def test_document_page_and_404(client):
    assert client.get("/doc/doc3.txt").status_code == 200
    assert client.get("/doc/missing.txt").status_code == 404
```

### `pytest.ini`

```ini
[pytest]
testpaths = tests
pythonpath = .
```

### `requirements.txt`

```text
requests
beautifulsoup4
flask
pytest
```

### `.gitignore`

```text
venv/
__pycache__/
*.pyc
.pytest_cache/
index.json
crawled/
```

---

# Appendix B: Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `python` not recognised (Windows) | Python not on PATH | Reinstall and tick "Add python.exe to PATH", or try `py` |
| `ModuleNotFoundError: No module named 'flask'` (or `requests`, `bs4`) | Virtual environment not active, or packages not installed | Activate `venv`, then `pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'processor'` (or `search`, `engine`...) | Running from the wrong folder, or file misnamed | `cd` into the project folder; check the file name |
| `FileNotFoundError: Folder not found: ...data` | `data/` missing | Create it and add the sample files |
| `python cli.py` says `0 documents` | No `.txt` files in `data/` (Windows may hide a double extension like `doc.txt.txt`) | Show file extensions in File Explorer |
| Search results seem stale or don't include new files | Old `index.json` | Delete `index.json`, or run `python cli.py --rebuild` |
| Changed `USE_STEMMING` or stop words but nothing changed | Same reason | Rebuild the index |
| `KeyError` in the indexer | Writing to `index[term][doc_id]` before `index[term]` exists | Create `index[term] = {}` first (Step 4) |
| Every score is 0.000 with `tfidf` | The word is in *every* document, so IDF = 0 | Expected; use `bm25`, or add more documents |
| Crawler saves 0 pages | Server not running, wrong URL, or blocked by `robots.txt` | Read the messages it prints; test the URL in a browser |
| `Address already in use` (port 8000 or 5000) | An earlier server is still running | Stop it with `Ctrl+C` (or use another port) |
| `TemplateNotFound: home.html` | Folder must be called exactly `templates`, next to `app.py` | Rename/move it |
| `pytest` can't import modules | Running from the wrong folder | Run `python -m pytest` from the project root (where `pytest.ini` is) |
| PowerShell blocks `Activate.ps1` | Script policy | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt |

**General debugging routine:** read the error from the **bottom up**; `print()` the variables just before the failing line; shrink the input to the smallest example that still fails; then trace it on paper.

---

# Appendix C: Command cheat sheet

```bash
# every new terminal
cd minisearch
source venv/bin/activate          # Windows: venv\Scripts\activate

# use it
python cli.py                     # search in the terminal
python cli.py --rebuild           # rebuild the index first
python app.py                     # web interface at http://127.0.0.1:5000

# crawl (keep the delay >= 1 second for real websites)
python -m http.server 8000 --directory demo_site     # terminal 1: practice site
python crawler.py http://localhost:8000/ 10 0        # terminal 2
python crawler.py https://quotes.toscrape.com 20     # a real practice site

# test
python -m pytest -q

# save your progress
git add .
git commit -m "describe what you did"
```
