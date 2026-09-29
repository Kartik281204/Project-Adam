# Build Your Own Search Engine in Python — A Learning Guide

This guide is for someone **very new to programming** who wants to learn Python by building real things, without copying a video tutorial line by line.

It does **not** hand you the finished code. It explains *what each part is, why it exists, what Python you need to build it,* and gives you **tasks** so you write the code yourself. Small hints and examples are included so you never get stuck for days.

> **Golden rule:** If you copy-paste code you don't understand, you learn nothing. If you write 10 ugly lines that *you* understand, you learn a lot.

---

## Table of Contents

1. [What is a search engine, really?](#1-what-is-a-search-engine-really)
2. [The big picture (5 parts)](#2-the-big-picture-5-parts)
3. [How to learn without tutorials](#3-how-to-learn-without-tutorials)
4. [Setup](#4-setup)
5. [Project structure](#5-project-structure)
6. [Stage 1 — Documents (your data)](#stage-1--documents-your-data)
7. [Stage 2 — Text processing](#stage-2--text-processing)
8. [Stage 3 — The inverted index (the heart)](#stage-3--the-inverted-index-the-heart)
9. [Stage 4 — Searching the index](#stage-4--searching-the-index)
10. [Stage 5 — Ranking results](#stage-5--ranking-results)
11. [Stage 6 — The crawler](#stage-6--the-crawler)
12. [Stage 7 — Saving your index](#stage-7--saving-your-index)
13. [Stage 8 — User interface](#stage-8--user-interface)
14. [Stage 9 — Testing and evaluating](#stage-9--testing-and-evaluating)
15. [Stage 10 — Upgrades (and where AI comes in)](#stage-10--upgrades-and-where-ai-comes-in)
16. [Python concepts checklist](#python-concepts-checklist)
17. [Common mistakes](#common-mistakes)
18. [Milestone checklist](#milestone-checklist)
19. [Glossary](#glossary)

---

## 1. What is a search engine, really?

A search engine answers one question:

> "Out of a huge pile of documents, which ones are most relevant to what the user typed?"

That's it. Google, Bing, the search bar in your notes app — all do this. The difference is scale (billions of pages vs. ten files).

The trick that makes it fast: **you do not scan every document every time someone searches.** Instead you do the hard work *once, in advance* (reading and organising everything), so that each search is almost instant.

Think of a **book**. To find where "photosynthesis" is mentioned, you don't read all 500 pages. You flip to the **index at the back**, look up "photosynthesis", and it says "pages 42, 87, 133". A search engine builds exactly that kind of index, automatically.

---

## 2. The big picture (5 parts)

```
   ┌──────────┐     ┌────────────┐     ┌───────────┐
   │ 1.CRAWLER│ ──▶ │ 2.PROCESSOR│ ──▶ │ 3. INDEXER│
   │ get pages│     │ clean text │     │ build     │
   └──────────┘     └────────────┘     │ lookup    │
                                       └─────┬─────┘
                                             │ saved to disk
                                             ▼
   ┌──────────┐     ┌────────────┐     ┌───────────┐
   │ 5. UI    │ ◀── │ 4. RANKER  │ ◀── │ QUERY     │
   │ show     │     │ sort by    │     │ user types│
   │ results  │     │ relevance  │     │ a search  │
   └──────────┘     └────────────┘     └───────────┘
```

| Part | Job | Analogy |
|---|---|---|
| **Crawler** | Collects documents (web pages, files) | A librarian gathering books |
| **Processor** | Cleans text into standard "words" | Removing typos/formatting from every book |
| **Indexer** | Builds word → documents lookup table | The index at the back of a book |
| **Ranker** | Orders results by how relevant they are | Putting the best matches on top |
| **Interface** | Lets a human type a query and see results | The search bar |

**Important:** Build in a *different* order than the diagram. Start with a folder of text files (no crawler), get search working, and add the crawler later. Each stage below builds on the last and always leaves you with something that *runs*.

---

## 3. How to learn without tutorials

This is the most important section. Read it twice.

### The loop for every stage

1. **Understand the goal in plain English.** Write it in a comment or notebook before any code. ("I want a function that takes a sentence and returns a list of lowercase words.")
2. **Try to solve it with the dumbest possible code.** Ugly is fine.
3. **Run it. Print things.** Use `print()` after every step to *see* what your data looks like. Beginners who print a lot learn 3x faster.
4. **When stuck, shrink the problem.** Can't build the whole index? Build it for *one* document. Then two.
5. **Read the error message from the bottom up.** The last line says what went wrong; the lines above say where.
6. **Search the *concept*, not the project.** Google "python split string into words", "python dictionary add key if missing" — not "how to build a search engine in Python".
7. **Read the official docs** at [docs.python.org](https://docs.python.org/3/). It feels hard at first and becomes your superpower.
8. **Only after 30+ minutes of real trying**, look at a hint or ask for help. Then re-type the solution *from memory* the next day.

### Tools that keep you honest

- **Keep a `NOTES.md`** — every day write "what I built, what confused me, what I learned".
- **Use Git** from day one (`git init`, commit after each stage). Committing a working stage is a tiny victory and a safety net.
- **Explain it out loud** (rubber-duck debugging). If you can't explain a line, you don't understand it yet.
- **Change things on purpose.** Once code works, break it deliberately and predict what happens.

---

## 4. Setup

### 4.1 Install Python
Download Python 3.11+ from [python.org](https://www.python.org/downloads/). Check it works:

```bash
python --version
```
(On some systems it's `python3 --version`.)

### 4.2 An editor
Use **VS Code** with the Python extension, or **PyCharm Community**.

### 4.3 Virtual environment (important habit)
A virtual environment is a private box of packages for one project, so projects don't break each other.

```bash
mkdir my_search_engine
cd my_search_engine
python -m venv venv

# Activate it:
# Windows:      venv\Scripts\activate
# Mac/Linux:    source venv/bin/activate
```
When active, your terminal shows `(venv)`.

### 4.4 Libraries you'll eventually use
Install only when you need them:

```bash
pip install requests beautifulsoup4 flask
```
- `requests` → download web pages (Stage 6)
- `beautifulsoup4` → read HTML (Stage 6)
- `flask` → make a small website (Stage 8)

Everything before Stage 6 uses **only built-in Python**. That's deliberate: you learn the fundamentals, not libraries.

---

## 5. Project structure

Start simple, grow as needed:

```
my_search_engine/
├── README.md
├── NOTES.md              # your learning diary
├── data/                 # your text files / crawled pages
│   ├── doc1.txt
│   └── doc2.txt
├── processor.py          # Stage 2: clean text
├── indexer.py            # Stage 3: build the index
├── search.py             # Stage 4-5: query + ranking
├── crawler.py            # Stage 6: fetch web pages
├── storage.py            # Stage 7: save/load index
├── app.py                # Stage 8: interface
└── tests/
    └── test_search.py    # Stage 9
```

Why separate files? Each file does **one job**. When something breaks you know where to look. (This idea is called *separation of concerns*.)

---

## Stage 1 — Documents (your data)

### What and why
A search engine needs things to search. A **document** is any unit of text: a web page, a note, a PDF, a tweet. For now: text files.

### What you need to know in Python
- Variables, strings
- Lists and dictionaries
- Reading files: `open()`, `with`, `.read()`
- Loops (`for`)
- The `os` or `pathlib` module to list files in a folder

### Your tasks
1. Create a `data/` folder with **5–10 small `.txt` files**. Make them about different topics (e.g. sentences about cricket, cooking, python, space). Overlap some words on purpose.
2. Write a function `load_documents(folder)` that returns a **dictionary**:
   ```
   {
     "doc1.txt": "the full text of doc1...",
     "doc2.txt": "the full text of doc2..."
   }
   ```
3. Print the number of documents and the first 50 characters of each.

### Concepts to google
`python read all files in a folder`, `python with open`, `pathlib glob`

### Checkpoint
You can load a folder into a dictionary of `{filename: text}`.

---

## Stage 2 — Text processing

### What and why
Computers see `"Python"`, `"python"`, and `"Python,"` as three *different* strings. A user searching "python" expects all of them to match. **Processing** (also called *normalisation*) makes text consistent.

### The steps (called a "pipeline")

| Step | Example | Why |
|---|---|---|
| **Lowercase** | `"Python"` → `"python"` | So case doesn't matter |
| **Remove punctuation** | `"hello,"` → `"hello"` | So commas don't stick to words |
| **Tokenise** | `"I love python"` → `["i","love","python"]` | Split text into individual words (*tokens*) |
| **Remove stop words** | remove `the, is, a, of, and` | Very common words carry little meaning |
| **Stemming** *(optional, later)* | `"running","runs"` → `"run"` | Match different forms of one word |

### What you need to know in Python
- String methods: `.lower()`, `.split()`, `.strip()`, `.replace()`
- Loops and list comprehensions
- Sets (fast "is this word in this collection?" checks)
- `import string` and `string.punctuation`
- Regular expressions with `re` *(nice-to-have; try without first)*

### Your tasks
1. Write `tokenize(text)` that returns a list of clean lowercase words.
2. Test it with tricky input: `"Hello, World!!"`, `"It's 5 o'clock"`, an empty string `""`.
3. Create a `STOP_WORDS` set (start with ~20 words) and write `remove_stop_words(tokens)`.
4. Chain them: `process(text)` → clean list of tokens.
5. **Later:** implement a *very* simple stemmer yourself (strip `ing`, `ed`, `s` from the end). It'll be wrong sometimes — that's the lesson. Then compare with the real `nltk.stem.PorterStemmer`.

### Design decision to think about
> Should "don't" become `["don't"]`, `["don", "t"]`, or `["dont"]`? There's no single right answer. Pick one, write it in `NOTES.md`, move on.

### Checkpoint
`process("The Quick brown FOX, jumped!")` → `["quick", "brown", "fox", "jumped"]`

---

## Stage 3 — The inverted index (the heart)

### What and why
This is the single most important idea in search.

**Forward index** (what you have now):
```
doc1 → ["python", "is", "fun"]
doc2 → ["python", "is", "fast"]
```

**Inverted index** (what you want) — flip it:
```
"python" → [doc1, doc2]
"fun"    → [doc1]
"fast"   → [doc2]
```

Now to find "python", you look up **one key** and instantly get every document. No scanning. That's why Google can search billions of pages in milliseconds.

### A richer version
Store *how many times* a word appears and *where*:

```python
{
  "python": {
      "doc1.txt": {"count": 3, "positions": [0, 14, 22]},
      "doc2.txt": {"count": 1, "positions": [5]},
  },
  "fun": {
      "doc1.txt": {"count": 1, "positions": [2]},
  },
}
```
Start with just `count`. Add `positions` later when you want phrase search.

### What you need to know in Python
- **Dictionaries** (deeply — this stage is 90% dictionaries)
- Nested dictionaries: a dict whose values are dicts
- Checking `if key in dict`
- `dict.get(key, default)` and `collections.defaultdict`
- `enumerate()` to get word positions
- `collections.Counter` to count words

### Your tasks
1. Build the index for **one** document by hand-written loop. Print it.
2. Extend to all documents.
3. Write `build_index(documents)` that returns the inverted index.
4. Print the index for a small dataset and *check it by eye*: is every word listed under the correct documents?
5. Also record `doc_lengths = {"doc1.txt": 42, ...}` (number of tokens per doc). You'll need it for ranking.

### Common mistakes
- Modifying a dictionary while looping over it.
- Forgetting to create the inner dictionary before writing into it (`KeyError`). This is what `defaultdict` fixes — try to understand the bug first, then the fix.

### Checkpoint
`index["python"]` shows exactly which documents contain "python" and how often.

---

## Stage 4 — Searching the index

### What and why
Take what the user typed, process it **the same way** you processed the documents, and look each word up in the index.

> **Critical rule:** the query must go through the *same* `process()` function as the documents. Otherwise "Python" (query) will never match "python" (index).

### Search styles to build (in order)

| Style | Meaning | Example |
|---|---|---|
| **OR search** | Any word matches | `python fast` → docs with python OR fast |
| **AND search** | All words must match | `python fast` → docs with python AND fast |
| **Phrase search** *(later)* | Words appear together, in order | `"machine learning"` |
| **NOT search** *(later)* | Exclude a word | `python -snake` |

### What you need to know in Python
- **Sets** and set operations: `|` (union = OR), `&` (intersection = AND), `-` (difference = NOT). These make AND/OR search a one-liner once you see it.
- Functions that return lists/sets
- `input()` for a quick command-line loop
- `while True:` loops and `break`

### Your tasks
1. `search_or(query, index)` → set of matching doc names.
2. `search_and(query, index)` → set of matching doc names.
3. Handle: empty query, word not in index, all stop words (e.g. query = `"the"`).
4. Make a loop:
   ```
   Search> python fast
   Found 2 results: doc1.txt, doc2.txt
   Search> quit
   ```

### Checkpoint
A working (unranked) search engine in the terminal. **Commit this. You just built a search engine.**

---

## Stage 5 — Ranking results

### What and why
Search returns 500 documents. Which comes first? **Ranking** assigns each result a **score**, then sorts high → low.

### Level 1 — Term Frequency (TF)
Score = how many times the query word appears in the doc. Simple, but flawed: a very long document wins just because it has more words.

### Level 2 — Normalised TF
Divide by document length:
```
TF = (times word appears in doc) / (total words in doc)
```

### Level 3 — TF-IDF (the classic)
Problem: the word "system" appears in every document, so it tells you nothing. A rare word like "photosynthesis" is a much stronger signal.

**IDF (Inverse Document Frequency)** measures how rare a word is:
```
IDF(word) = log( total_docs / docs_containing_word )
```
- Word in all docs → IDF ≈ 0 (useless)
- Word in 1 of 1000 docs → high IDF (very informative)

```
TF-IDF(word, doc) = TF(word, doc) × IDF(word)
```
For a multi-word query, **add up** the TF-IDF of each query word for each document.

### Level 4 — BM25 (what real engines use)
BM25 is an improved TF-IDF that stops repeated words from scoring endlessly and handles doc length better. Look up the formula only after TF-IDF works; implementing it yourself is a great milestone. Parameters `k1` (≈1.5) and `b` (≈0.75) are standard.

### What you need to know in Python
- `math.log()`
- Sorting with `sorted(..., key=..., reverse=True)`
- Lambda functions (`lambda x: x[1]`)
- Dictionaries of scores: `{"doc1.txt": 0.42, ...}`
- Tuples, and sorting lists of tuples

### Your tasks
1. Rank by raw term count. Look at results — do they feel right?
2. Upgrade to TF-IDF. Compare rankings on the same queries. Write in `NOTES.md` *why* they differ.
3. Show scores next to each result.
4. Return only the top 5 (`results[:5]`).
5. **Challenge:** implement BM25 and compare.

### Experiment ideas
- Search a word that's in every doc. What are the scores?
- Search a rare word. Does the right doc win?
- Make one document 10x longer. Does raw count still behave sensibly?

### Checkpoint
Results appear **sorted by relevance** with scores.

---

## Stage 6 — The crawler

### What and why
So far your documents were files you made. A **crawler** (spider/bot) collects documents automatically from the web by:

1. Starting at a **seed URL**
2. Downloading the page
3. Extracting the text (to index) and the **links** (to visit next)
4. Repeating for each new link

```
seed → page A → links to B, C → visit B → links to D, E ...
```

### Key concepts

- **HTTP request:** asking a server for a page. Done with `requests.get(url)`.
- **HTML parsing:** web pages are messy HTML. `BeautifulSoup` lets you pull out the text (`soup.get_text()`) and links (`soup.find_all("a")`).
- **Queue (frontier):** a list of URLs still to visit. Use a `collections.deque`.
- **Visited set:** URLs already done, so you never loop forever (`set`).
- **Depth / page limit:** stop after N pages or depth D. **Always set a limit.**
- **Relative → absolute URLs:** `/about` must become `https://site.com/about` (`urllib.parse.urljoin`).

### Be a polite crawler (very important)
- Read the site's `robots.txt` (e.g. `https://example.com/robots.txt`) and respect it. Python has `urllib.robotparser`.
- **Wait between requests** (`time.sleep(1)`) so you don't overload servers.
- Set a proper `User-Agent` header identifying your bot.
- Practice on sites made for it: **[books.toscrape.com](https://books.toscrape.com)** and **[quotes.toscrape.com](https://quotes.toscrape.com)**, or Wikipedia (with delays).
- Don't crawl private, login-protected, or personal data.

### What you need to know in Python
- `try / except` (network calls *will* fail)
- `while` loops with a queue
- Sets, `deque`
- String / URL handling
- Functions returning multiple values (tuples)

### Your tasks
1. Download **one** page and print its title and first 200 characters of text.
2. Extract all links from it and print them.
3. Turn relative links into absolute ones.
4. Build the crawl loop with `queue`, `visited`, `max_pages=20`, and `time.sleep(1)`.
5. Save each page's text into `data/` (or a dictionary) so Stages 2–5 index it.
6. Handle errors: 404 pages, timeouts, non-HTML links (PDFs, images).
7. Only follow links **within the same domain**.

### Common mistakes
- No page limit → your crawler runs forever.
- Not tracking visited URLs → infinite loops.
- Treating `page.html#section` and `page.html` as different pages.

### Checkpoint
You point it at a small site and it builds a searchable collection by itself.

---

## Stage 7 — Saving your index

### What and why
Rebuilding the index every time you run the program is wasteful. **Persistence** = saving to disk so you can reload instantly.

### Options (easiest → most powerful)

| Option | Good for | Notes |
|---|---|---|
| **JSON** (`json` module) | Learning, small data | Human-readable. `json.dump()` / `json.load()` |
| **Pickle** (`pickle`) | Quick Python-only saves | Not human-readable; never load pickles from untrusted sources |
| **SQLite** (`sqlite3`) | Bigger data, real projects | Built-in database, no server. Learn basic SQL |

### Your tasks
1. Save the index and doc lengths to `index.json`; load them back and confirm search still works.
2. Store each doc's **title, URL, and a text snippet** too (you'll need them for the UI).
3. Add "incremental" behaviour: if a page is already indexed, skip it.
4. **Later:** move to SQLite with tables `documents` and `postings`.

### Checkpoint
Run the program twice; the second time it starts instantly without re-crawling.

---

## Stage 8 — User interface

### Level 1 — Command line (you already have it)
Improve it: show rank number, title, score, and a snippet.

### Level 2 — Snippets with highlighting
Show the part of the document around the matched word:
```
1. Intro to Python (score 0.83)
   ...python is a **fast** and easy language to learn...
```
Find the word's position (you stored `positions`!) and slice the text around it.

### Level 3 — Web interface with Flask
Flask turns a Python function into a web page.

Concepts:
- **Route:** a URL mapped to a function (`@app.route("/")`)
- **Request:** data the user sends (`request.args.get("q")`)
- **Template:** an HTML file with blanks filled by Python (Jinja2)

Your pages:
- `/` — a search box
- `/search?q=python` — results list

### What you need to know in Python
- Functions, decorators (just *use* them at first)
- f-strings for formatting
- Basic HTML forms (`<form>`, `<input>`)

### Checkpoint
You open `http://localhost:5000`, type a query, and see ranked results in your browser.

---

## Stage 9 — Testing and evaluating

### Why
"It seems to work" is not enough. Tests catch bugs when you change things later.

### Unit tests
Use Python's built-in `unittest`, or `pytest` (`pip install pytest`).

```python
def test_tokenize_lowercases():
    assert tokenize("Hello World") == ["hello", "world"]
```
Write tests for: `tokenize`, `remove_stop_words`, `build_index`, `search_and`, ranking order.

### Evaluating quality
How do you know your search is *good*?

1. Make a small **test set**: 10 queries, and for each, which documents *should* be top results (you decide).
2. Measure:
   - **Precision@k:** of the top k results, how many were correct?
   - **Recall:** of all correct docs, how many did you find?
3. Change something (add stemming, switch to BM25) and re-measure. Numbers tell you if you actually improved.

### Also measure speed
Use `time.time()` (or `timeit`) to time indexing and searching as you add more docs. Watch what gets slow — that's how you learn about performance.

---

## Stage 10 — Upgrades (and where AI comes in)

You now have a real, classical search engine. Everything here is optional and independent — pick what excites you.

### Search-quality upgrades
- **Phrase search** using stored positions
- **Stemming / lemmatisation** (`nltk`, `spaCy`)
- **Typo tolerance** — edit distance (Levenshtein), or "Did you mean...?"
- **Autocomplete** — a *trie* data structure
- **Synonyms** — "car" also finds "automobile"
- **Field boosting** — title matches count more than body matches
- **PageRank** — rank pages by how many other pages link to them (great graph-theory project)

### Engineering upgrades
- Multithreaded / async crawling (`asyncio`, `aiohttp`)
- SQLite → PostgreSQL / Elasticsearch
- Compress the index
- Caching frequent queries

### The AI step (your longer-term goal)
Your keyword engine matches **words**. AI-based search matches **meaning**.

| Classical (what you built) | AI-powered (next) |
|---|---|
| "car" won't match "automobile" | Understands they're similar |
| Needs exact words | Understands the *idea* of the query |
| TF-IDF / BM25 scoring | Cosine similarity between **embeddings** |

Path forward, one small step at a time:
1. Learn what an **embedding** is: a list of numbers representing the meaning of a text.
2. Use `sentence-transformers` to turn each document into an embedding.
3. Embed the query, then rank documents by **cosine similarity**.
4. Combine both: **hybrid search** = BM25 score + embedding score. Because you built BM25 yourself, you'll understand exactly what each half does.
5. Feed the top results into a language model to *answer* the question, not just list pages. This pattern is called **RAG (Retrieval-Augmented Generation)**, and the search engine you just built is its retrieval half.

Build the classical version first. Everyone who skips it ends up treating AI search as a black box.

---

## Python concepts checklist

Tick these off as the stages force you to use them.

**Basics**
- [ ] Variables, numbers, strings, f-strings
- [ ] `if / elif / else`
- [ ] `for` and `while` loops
- [ ] Functions, parameters, `return`

**Data structures**
- [ ] Lists (indexing, slicing, `append`)
- [ ] Dictionaries (nested, `.get`, `.items()`)
- [ ] Sets (union, intersection)
- [ ] Tuples
- [ ] `defaultdict`, `Counter`, `deque`

**Intermediate**
- [ ] List / dict comprehensions
- [ ] Sorting with `key=` and `lambda`
- [ ] File I/O with `with open`
- [ ] `try / except`
- [ ] Modules and `import`
- [ ] `if __name__ == "__main__":`
- [ ] Virtual environments and `pip`

**Later**
- [ ] Classes and objects (refactor into `class SearchEngine`)
- [ ] `json`, `sqlite3`
- [ ] Type hints
- [ ] Unit testing

> Tip: Once everything works in functions, refactor it into a `SearchEngine` **class** with methods `add_document()`, `build_index()`, `search()`, `save()`, `load()`. That's a perfect first object-oriented project.

---

## Common mistakes

1. **Trying to build everything at once.** Do stage by stage.
2. **Not printing intermediate data.** Always look at what your variables contain.
3. **Processing queries differently from documents.** Same pipeline both ways.
4. **Ignoring edge cases:** empty query, unknown word, empty file.
5. **Crawling without limits or delays.** Can get your IP blocked.
6. **Copying code you don't understand.** Type it yourself and change it.
7. **Not using Git.** Commit at every checkpoint.
8. **Skipping tests** and then being afraid to change working code.

---

## Milestone checklist

- [ ] **M1** Load a folder of `.txt` files into a dictionary
- [ ] **M2** `process(text)` returns clean tokens
- [ ] **M3** Inverted index built and printed correctly
- [ ] **M4** Terminal search works (AND / OR)
- [ ] **M5** Results ranked with TF-IDF
- [ ] **M6** Crawler collects pages from a small site
- [ ] **M7** Index saved and loaded from disk
- [ ] **M8** Flask web interface with snippets
- [ ] **M9** Tests written, precision measured
- [ ] **M10** BM25 implemented and compared with TF-IDF
- [ ] **M11** First embedding-based (semantic) search
- [ ] **M12** Hybrid search + a small RAG demo

Suggested pace for a beginner: **1–2 weeks per stage** at 1 hour a day. Don't rush; understanding beats speed.

---

## Glossary

| Term | Meaning |
|---|---|
| **Document** | One unit of searchable text (a page, a file) |
| **Corpus** | The full collection of documents |
| **Token** | One "word" after splitting text |
| **Tokenisation** | Splitting text into tokens |
| **Stop words** | Very common words (the, is, a) usually ignored |
| **Stemming** | Chopping words to a root (running → run) |
| **Lemmatisation** | Smarter reduction using grammar (better → good) |
| **Index** | Data structure that makes lookups fast |
| **Inverted index** | Maps each word → the documents containing it |
| **Posting** | One entry in the index: (document, count, positions) |
| **Query** | What the user types |
| **TF** | Term Frequency: how often a word is in a doc |
| **IDF** | Inverse Document Frequency: how rare a word is overall |
| **TF-IDF** | TF × IDF, a classic relevance score |
| **BM25** | Improved TF-IDF used by real engines |
| **Crawler / Spider** | Program that fetches pages by following links |
| **Seed URL** | Where the crawl starts |
| **Frontier** | Queue of URLs waiting to be crawled |
| **robots.txt** | File telling bots what they may crawl |
| **Precision / Recall** | Metrics for how good results are |
| **Embedding** | List of numbers representing the meaning of text |
| **Cosine similarity** | Measure of how close two embeddings are |
| **Hybrid search** | Keyword scoring + semantic scoring combined |
| **RAG** | Retrieval-Augmented Generation: search first, then have an LLM answer using the results |

---

## Final advice

You're building something real, not a toy. A basic search engine touches almost every fundamental skill: strings, dictionaries, sets, files, networking, sorting, math, web apps, testing. If you can build it and *explain every line*, you'll be far ahead of someone who has watched 50 tutorials.

When you get stuck, come back with: **(1) what you were trying to do, (2) the code you wrote, (3) the exact error or wrong output, (4) what you already tried.** That's how programmers ask good questions.

Start with Stage 1 today. Just load a folder of text files. Go.
