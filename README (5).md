# Build Your Own Search Engine in Python

### The Complete Beginner's Guide: from "what is a variable?" to "I built a search engine"

---

## Who this guide is for

You are **new to programming**. You want to learn Python by building something real, and you do **not** want to just copy a YouTube tutorial. Your bigger goal is to build your own AI someday, and a search engine is the first step, because every modern AI assistant that answers questions from documents has a search engine inside it.

This guide will:

- explain **every concept from zero** (no "as you already know...")
- teach you the **Python you need, exactly when you need it**
- break each part of the search engine into **baby steps**
- give you **tasks to code yourself**, with hints if you get stuck
- **not** give you a finished project to copy

If you finish it, you will not just have a search engine. You will know how to look at a big problem, cut it into small pieces, and build each piece yourself. That is the real skill.

---

## How to read this guide (the symbols)

| Symbol | Meaning |
|---|---|
| 🧠 **Concept** | An idea explained in plain English (not about Python itself) |
| 🐍 **Python** | A Python feature explained with a small example |
| 🛠️ **Task** | *You* write code here |
| 💡 **Hint** | Help if you're stuck (usually hidden until you click it) |
| ⚠️ **Watch out** | A common mistake |
| ✅ **Checkpoint** | How you know the stage is done |

### The 5 rules of learning by building

1. **Type code yourself. Never paste.** Typing forces your brain to read every character.
2. **Print everything.** After every step, `print()` your variables and look at them. Beginners who print a lot learn much faster.
3. **Make it work ugly first.** Ugly working code beats beautiful code that doesn't exist.
4. **Shrink the problem.** Stuck on 10 documents? Do 1. Stuck on 1? Do a 3-word sentence.
5. **Struggle for 30 minutes before looking at a hint.** The struggle is where the learning happens. After you solve it, *re-type the solution from memory the next day.*

### Keep a learning diary

Create a file called `NOTES.md`. After each session write three lines:

```
Today I built: ...
I got stuck on: ...
I now understand: ...
```

This turns confusion into memory.

---

## Table of contents

1. [What is a search engine? (from scratch)](#chapter-1--what-is-a-search-engine-from-scratch)
2. [Before you code: computers, programs, and the terminal](#chapter-2--before-you-code-computers-programs-and-the-terminal)
3. [Python crash course (everything you need)](#chapter-3--python-crash-course)
4. [Setting up your workspace](#chapter-4--setting-up-your-workspace)
5. [Stage 1: Documents](#stage-1--documents-your-data)
6. [Stage 2: Text processing](#stage-2--text-processing)
7. [Stage 3: The inverted index](#stage-3--the-inverted-index-the-heart-of-search)
8. [Stage 4: Searching the index](#stage-4--searching-the-index)
9. [Stage 5: Ranking results](#stage-5--ranking-results)
10. [Stage 6: The crawler](#stage-6--the-crawler)
11. [Stage 7: Saving your index](#stage-7--saving-your-index)
12. [Stage 8: The user interface](#stage-8--the-user-interface)
13. [Stage 9: Testing and measuring quality](#stage-9--testing-and-measuring-quality)
14. [Stage 10: Upgrades and the road to AI](#stage-10--upgrades-and-the-road-to-ai)
15. [Debugging playbook](#appendix-a--debugging-playbook)
16. [Cheat sheet](#appendix-b--python-cheat-sheet)
17. [Glossary](#appendix-c--glossary)
18. [Milestones and schedule](#appendix-d--milestones-and-schedule)
19. [Free resources](#appendix-e--free-resources)

---

# Chapter 1 — What is a search engine? (from scratch)

## 1.1 The problem

Imagine you have **1,000 text files** of notes on your laptop. You want to find every note that mentions the word `budget`.

The most obvious approach:

```
for each of the 1,000 files:
    open the file
    read all the text
    check if "budget" is in it
```

This works, but it is **slow**. Every search re-reads everything. With 1,000 small files it's fine. With 1,000,000 files it takes minutes. With the entire internet (billions of pages) it would take years. Yet Google answers in a fraction of a second.

How?

## 1.2 The big idea: prepare in advance

🧠 **Concept: the index at the back of a book**

Open any textbook and look at the **index** at the very back. It looks like this:

```
photosynthesis ......... 42, 87, 133
python ................. 12, 15, 201
```

When you want to know where "photosynthesis" is discussed, you do **not** read all 500 pages. You look up one word in the index, and it tells you exactly which pages to open.

A search engine does the same thing. Before anyone searches, the engine reads every document **once** and builds an index: a lookup table from **words → documents that contain them**. When someone searches, the engine just looks up the words in that table.

So a search engine works in **two phases**:

| Phase | When | Speed | What happens |
|---|---|---|---|
| **Indexing** | Once, in advance | Can be slow | Read all documents, clean them, build the lookup table |
| **Querying** | Every time a user searches | Must be very fast | Look up the words in the table, rank the results |

Doing the heavy work up front so that each search is cheap is the central idea of this whole project.

## 1.3 The five parts of a search engine

```
   PHASE 1: INDEXING (done ahead of time)
   ┌───────────┐    ┌────────────┐    ┌───────────┐
   │ 1.CRAWLER │ ─▶ │ 2.PROCESSOR│ ─▶ │ 3. INDEXER│ ─▶ (saved index)
   │ collect   │    │ clean the  │    │ build the │
   │ documents │    │ text       │    │ word→docs │
   └───────────┘    └────────────┘    │ table     │
                                      └───────────┘

   PHASE 2: QUERYING (done at every search)
   ┌───────────┐    ┌────────────┐    ┌───────────┐
   │ USER TYPES│ ─▶ │ 4. SEARCHER│ ─▶ │ 5. RANKER │ ─▶ results shown
   │ a query   │    │ look words │    │ sort best │    to the user
   │           │    │ up in index│    │ first     │
   └───────────┘    └────────────┘    └───────────┘
```

| Part | Its job in one sentence | Real-life analogy |
|---|---|---|
| **Crawler** | Collects documents (web pages, files) | A librarian gathering books |
| **Processor** | Turns messy text into clean, standard words | Editing every book into the same format |
| **Indexer** | Builds the "word → documents" table | Creating the index at the back of the book |
| **Searcher** | Takes a query and finds matching documents | Flipping to the index and looking up a word |
| **Ranker** | Puts the *most relevant* results first | Putting the best books on the top shelf |

You will also build a **user interface** (a way for a human to type a query) and **storage** (saving the index so you don't rebuild it every time).

## 1.4 The order you'll build it in

You will **not** build the crawler first. That's the most confusing part and beginners quit there. Instead:

| Stage | You build | Why in this order |
|---|---|---|
| 1 | Load text files | Get *some* data to work with |
| 2 | Clean text | Search needs consistent words |
| 3 | The index | The core idea |
| 4 | Search | Now you have a real search engine! |
| 5 | Ranking | Make the results good |
| 6 | Crawler | Now collect data automatically |
| 7 | Saving | Don't rebuild every time |
| 8 | Interface | Make it usable |
| 9 | Testing | Make it trustworthy |
| 10 | AI upgrades | Where your bigger goal begins |

After **Stage 4** you already have a working search engine. Everything after that makes it better.

## 1.5 The running example (we'll use this all guide long)

To keep everything concrete, we'll follow **three tiny documents** through every stage:

```
doc1: "Python is a fun language to learn."
doc2: "Learning Python is fun and Python is fast."
doc3: "Cats are fun animals."
```

Here's a preview of what happens to them. Don't worry if it isn't clear yet. Each step is explained later. Come back to this table after each stage and watch it make more sense.

**After cleaning (Stage 2)**, we lowercase, remove punctuation, split into words, and drop very common words like `is`, `a`, `to`, `and`, `are`:

```
doc1: ["python", "fun", "language", "learn"]              (4 words)
doc2: ["learning", "python", "fun", "python", "fast"]     (5 words)
doc3: ["cats", "fun", "animals"]                          (3 words)
```

**After building the index (Stage 3)**, we flip it around into word → documents (with counts):

```
python   → doc1: 1 time,  doc2: 2 times
fun      → doc1: 1,       doc2: 1,       doc3: 1
language → doc1: 1
learn    → doc1: 1
learning → doc2: 1
fast     → doc2: 1
cats     → doc3: 1
animals  → doc3: 1
```

**Searching (Stage 4)** for `python fun`:

```
OR  search (any word matches):  doc1, doc2, doc3
AND search (all words match):   doc1, doc2
```

**Ranking (Stage 5)** scores each result and sorts it:

```
doc2  score 0.162   ← "python" appears twice, so it ranks first
doc1  score 0.101
doc3  score 0.000
```

By the end, you will have written all of that yourself.

---

# Chapter 2 — Before you code: computers, programs, and the terminal

Skip anything you already know. Nothing here is optional if it's new to you.

## 2.1 What is a program?

A **program** is a list of instructions written for a computer. Computers are extremely fast but completely literal. They do exactly what you write, not what you *mean*. If you make a tiny spelling mistake, they refuse. Getting used to this is 50% of learning to program.

## 2.2 What is Python?

**Python** is a programming language, a set of rules for writing instructions that a computer can understand. It is popular because it reads almost like English, and it is the main language used for AI and data science.

You write instructions in a plain text file ending in `.py` (like `hello.py`). A program called the **Python interpreter** reads that file and carries out the instructions one line at a time, from top to bottom.

## 2.3 Files, folders, and paths

- A **file** holds data (a document, a photo, a program).
- A **folder** (directory) holds files and other folders.
- A **path** is the address of a file: `C:\Users\Asha\my_search_engine\data\doc1.txt` (Windows) or `/home/asha/my_search_engine/data/doc1.txt` (Mac/Linux).

Two kinds of paths:

- **Absolute path**: the full address from the top of the drive.
- **Relative path**: the address starting from where you currently are. `data/doc1.txt` means "inside the folder called `data` (next to me), the file `doc1.txt`."

Your project will mostly use relative paths, which is why it matters *where you run your program from*.

## 2.4 The terminal (command line)

The **terminal** is a text window where you type commands instead of clicking. Programmers use it constantly. Open it:

- **Windows:** search "Command Prompt" or "PowerShell" (or use the terminal built into VS Code)
- **Mac:** search "Terminal"
- **Linux:** Ctrl+Alt+T

Commands you need (Windows / Mac-Linux):

| What you want | Windows | Mac / Linux |
|---|---|---|
| Show where you are | `cd` | `pwd` |
| List files here | `dir` | `ls` |
| Make a folder | `mkdir data` | `mkdir data` |
| Go into a folder | `cd data` | `cd data` |
| Go up one folder | `cd ..` | `cd ..` |
| Clear the screen | `cls` | `clear` |

Try it: open the terminal, make a folder called `my_search_engine`, and go into it.

```bash
mkdir my_search_engine
cd my_search_engine
```

## 2.5 Running Python

Two ways:

1. **Interactive mode (REPL).** Type `python` in the terminal (or `python3` on Mac/Linux). You get a `>>>` prompt where you type one line and see the result immediately. Great for experimenting. Type `exit()` to leave.
2. **Script mode.** Put code in a file, e.g. `hello.py`, then run `python hello.py`. This is how real programs run.

**Use the REPL as your playground for the whole guide.** Any time you're unsure what a line does, try it there.

---

# Chapter 3 — Python crash course

This chapter teaches **only** the Python you need for this project. Try every example in the REPL. Don't try to memorize. Come back here whenever you forget something. (Appendix B is a one-page cheat sheet.)

## 3.1 Printing and comments

🐍 `print()` shows something on the screen.

```python
print("Hello, world!")
```
Output:
```
Hello, world!
```

Anything after a `#` is a **comment**: a note for humans that Python ignores.

```python
# This line is ignored by Python
print("This runs")  # comments can also go at the end of a line
```

## 3.2 Variables and basic data types

🐍 A **variable** is a name attached to a value, like a labelled box.

```python
name = "Asha"      # the name "name" now points to the text "Asha"
age = 20
print(name)        # Asha
print(age)         # 20
```

The `=` sign does **not** mean "equals" as in maths. It means "store the value on the right into the name on the left." You can change a variable any time:

```python
age = 20
age = age + 1      # take the current age (20), add 1, store it back
print(age)         # 21
```

The main **data types** (kinds of values):

| Type | Name in Python | Example | Used for |
|---|---|---|---|
| Whole number | `int` | `42`, `-7` | Counts |
| Decimal number | `float` | `3.14`, `0.25` | Scores |
| Text | `str` (string) | `"hello"`, `'hi'` | Words, documents |
| True/False | `bool` | `True`, `False` | Yes/no decisions |
| "Nothing" | `NoneType` | `None` | "no value yet" |

Check a value's type with `type()`:

```python
print(type(42))        # <class 'int'>
print(type("hello"))   # <class 'str'>
print(type(0.5))       # <class 'float'>
```

**Naming rules:** letters, digits, underscores; can't start with a digit; no spaces. Python convention is `snake_case` (`doc_lengths`, not `DocLengths`). Choose *meaningful* names: `word_count` beats `x`.

**Maths:**

```python
print(7 + 2)    # 9
print(7 - 2)    # 5
print(7 * 2)    # 14
print(7 / 2)    # 3.5   (normal division, always gives a float)
print(7 // 2)   # 3     (floor division: drops the decimal part)
print(7 % 2)    # 1     (remainder)
print(2 ** 3)   # 8     (power)
```

**f-strings** let you put variables inside text. Put `f` before the quotes and variables in `{}`:

```python
name = "Asha"
score = 0.8312
print(f"{name} scored {score:.2f}")   # Asha scored 0.83   (.2f = 2 decimal places)
```

## 3.3 Strings (text)

🧠 Your search engine is basically a text-handling machine, so strings are your most important tool.

A **string** is a sequence of characters. Characters have positions numbered from **0**:

```python
text = "Hello, World!"
#       H e l l o ,   W o r l d !
#       0 1 2 3 4 5 6 7 8 9 ...
print(len(text))       # 13   (number of characters)
print(text[0])         # H    (first character)
print(text[-1])        # !    (last character; negative counts from the end)
print(text[0:5])       # Hello  (slice: from position 0 up to, NOT including, 5)
```

**Very important string methods** (a *method* is a built-in action you call with a dot):

```python
text = "  Hello, World!  "

print(text.lower())               # "  hello, world!  "
print(text.upper())               # "  HELLO, WORLD!  "
print(text.strip())               # "Hello, World!"   (removes spaces at both ends)
print(text.replace("World", "Python"))   # "  Hello, Python!  "
print("World" in text)            # True   (is this piece inside the text?)
print("hello world hi".split())   # ['hello', 'world', 'hi']   (split into a list of words)
print("a,b,c".split(","))         # ['a', 'b', 'c']            (split on a chosen character)
print(" ".join(["a", "b", "c"]))  # "a b c"                    (glue a list back together)
print("Hello".startswith("He"))   # True
```

⚠️ **Strings never change in place.** Methods return a **new** string. This is one of the most common beginner bugs:

```python
text = "HELLO"
text.lower()             # this creates "hello" but throws it away!
print(text)              # still "HELLO"

text = text.lower()      # correct: store the result
print(text)              # "hello"
```

## 3.4 Lists

🐍 A **list** is an ordered collection of items, written in square brackets.

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])         # apple
print(fruits[-1])        # cherry
print(len(fruits))       # 3
print(fruits[1:3])       # ['banana', 'cherry']

fruits.append("date")    # add to the end
print(fruits)            # ['apple', 'banana', 'cherry', 'date']

print("banana" in fruits)   # True
```

Lists can hold anything, including numbers, strings, or even other lists. They can be empty: `results = []`. Lists *can* be changed in place (unlike strings).

## 3.5 Tuples

🐍 A **tuple** is like a list but written with round brackets and **cannot be changed** after creation. Great for a small fixed group of related values.

```python
result = ("doc1.txt", 0.83)        # (document name, score)
print(result[0])                   # doc1.txt

name, score = result               # "unpacking": split into two variables
print(name, score)                 # doc1.txt 0.83
```

## 3.6 Dictionaries (you'll use these constantly)

🐍 A **dictionary** (`dict`) stores **key → value** pairs, exactly like a real dictionary: look up a word (key), get its meaning (value).

```python
ages = {"Asha": 20, "Ravi": 22}

print(ages["Asha"])          # 20        (look up by key)
ages["Meera"] = 19           # add a new pair
ages["Asha"] = 21            # change an existing value
print(len(ages))             # 3
print("Ravi" in ages)        # True      (checks KEYS)
```

Looking up a key that doesn't exist crashes with a **KeyError**:

```python
print(ages["Zed"])           # KeyError: 'Zed'
```

Safe ways to look up:

```python
print(ages.get("Zed"))       # None       (no crash)
print(ages.get("Zed", 0))    # 0          (custom default)
```

**Looping through a dictionary:**

```python
for name, age in ages.items():
    print(name, "is", age)
```

**Counting words with a dictionary** (you'll do exactly this in Stage 3):

```python
words = ["python", "fun", "python"]
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
print(counts)                # {'python': 2, 'fun': 1}
```

Read that loop slowly: for each word, "get its current count (or 0 if we've never seen it), add 1, store it back."

**Nested dictionaries** (dictionaries inside dictionaries), which is exactly the shape of a search index:

```python
index = {
    "python": {"doc1.txt": 1, "doc2.txt": 2},
    "fun":    {"doc1.txt": 1, "doc2.txt": 1, "doc3.txt": 1},
}
print(index["python"])                 # {'doc1.txt': 1, 'doc2.txt': 2}
print(index["python"]["doc2.txt"])     # 2
```

🧠 **Why dictionaries are so fast:** a dictionary doesn't check its keys one by one. It uses a clever trick (a *hash table*) to jump almost directly to the right spot. Looking up a key takes roughly the same time whether the dictionary has 10 keys or 10 million. This speed is why search engines can exist.

## 3.7 Sets

🐍 A **set** is a collection of **unique** items with **no order**. Written with curly braces (but no colons).

```python
a = {1, 2, 3}
b = {2, 3, 4}

print(a | b)      # {1, 2, 3, 4}   union: everything in a OR b
print(a & b)      # {2, 3}         intersection: in a AND b
print(a - b)      # {1}            difference: in a but NOT in b

print(set([1, 1, 2, 2, 3]))   # {1, 2, 3}   duplicates removed
print(3 in a)                 # True   (very fast check)

empty = set()     # careful: {} makes an empty DICTIONARY, not a set
```

🧠 These three operations are **exactly** what you need for AND / OR / NOT search. "Documents containing python AND fun" is just `docs_with_python & docs_with_fun`.

## 3.8 Decisions: if / elif / else

🐍 Programs make choices using conditions.

```python
score = 75

if score >= 90:
    print("Excellent")
elif score >= 50:
    print("Pass")
else:
    print("Fail")
```

**Indentation matters!** In Python, the spaces at the start of a line show which code belongs inside the `if`. Use **4 spaces** (or one Tab, be consistent). The colon `:` at the end of the `if` line is required.

Comparison operators: `==` (equal), `!=` (not equal), `<`, `>`, `<=`, `>=`. **Note:** `==` compares; `=` stores. Mixing them up is a classic bug.

Combine conditions with `and`, `or`, `not`:

```python
if age >= 18 and has_id:
    print("Allowed")
```

**Truthiness:** empty things count as False, non-empty as True. This is handy:

```python
query = ""
if not query:           # true when query is empty
    print("Please type something")
```
(Empty string, empty list, empty dict, empty set, `0`, and `None` are all "falsy".)

## 3.9 Loops

🐍 A **loop** repeats code.

**`for` loop:** do something for each item in a collection.

```python
for fruit in ["apple", "banana"]:
    print("I like", fruit)
```

**`range()`** makes a sequence of numbers:

```python
for i in range(3):
    print(i)             # 0, 1, 2   (starts at 0, stops BEFORE 3)
```

**`enumerate()`** gives you the position *and* the item. You will use this to record word positions:

```python
for position, word in enumerate(["python", "is", "fun"]):
    print(position, word)
# 0 python
# 1 is
# 2 fun
```

**`while` loop:** repeat as long as a condition is true.

```python
count = 0
while count < 3:
    print(count)
    count += 1           # short for count = count + 1
```

⚠️ If the condition never becomes false, the loop runs **forever**. (Press `Ctrl+C` to stop a runaway program.)

**`break`** exits a loop early; **`continue`** skips to the next round:

```python
while True:
    answer = input("Type quit to stop: ")
    if answer == "quit":
        break
```

`input("...")` pauses and returns whatever the user types (as a string).

## 3.10 Functions

🐍 A **function** is a named, reusable block of code. You **define** it once with `def`, then **call** it as many times as you like.

```python
def add(a, b):
    return a + b

result = add(2, 3)
print(result)            # 5
```

- `a` and `b` are **parameters** (the inputs).
- `return` sends a value back to whoever called the function.
- The indented lines are the function's body.

**Default values:**

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Asha"))              # Hello, Asha!
print(greet("Asha", "Namaste"))   # Namaste, Asha!
```

⚠️ **`print` vs `return`, the most confused pair for beginners.**

- `print` **shows** something to a human on the screen. The program can't use it afterwards.
- `return` **hands a value back** so the rest of the program can use it.

```python
def bad_add(a, b):
    print(a + b)         # shows 5, but returns None!

x = bad_add(2, 3)
print(x)                 # None
```

Write a **docstring** (a note in triple quotes) at the top of each function to say what it does:

```python
def tokenize(text):
    """Split text into a list of lowercase words."""
    ...
```

**Why functions matter for this project:** every stage will be one or two functions. Small functions are easy to test, easy to fix, and easy to reuse.

## 3.11 Reading and writing files

🐍 Use `open()` inside a `with` block. The `with` block closes the file automatically, even if there's an error.

```python
with open("data/doc1.txt", "r", encoding="utf-8") as file:
    content = file.read()      # the whole file as one string

print(content)
```

- `"r"` = read mode (default). `"w"` = write (erases the file first!). `"a"` = append.
- `encoding="utf-8"` tells Python how to interpret special characters. Always include it. It prevents strange errors with characters like `é` or `₹`.

Writing:

```python
with open("output.txt", "w", encoding="utf-8") as file:
    file.write("Hello file!\n")     # \n means "new line"
```

**`pathlib`** is a modern, friendlier way to handle paths:

```python
from pathlib import Path

folder = Path("data")

for path in folder.glob("*.txt"):     # every file ending in .txt
    print(path.name)                  # doc1.txt
    print(path.stem)                  # doc1   (name without extension)
    text = path.read_text(encoding="utf-8")   # shortcut: read the whole file
```

(`glob` = "find files matching this pattern"; `*` means "anything".)

## 3.12 Modules and imports

🐍 A **module** is a Python file full of ready-made tools. **Importing** brings them into your program. Python comes with a large **standard library** (built-in modules). No installation needed.

```python
import math
print(math.log(10))              # 2.302585...
print(math.sqrt(16))             # 4.0

from collections import Counter, defaultdict, deque
```

Three handy tools from `collections`:

```python
# Counter: counts things automatically
print(Counter(["a", "b", "a"]))          # Counter({'a': 2, 'b': 1})

# defaultdict: a dict that creates missing entries for you
counts = defaultdict(int)                # missing keys start at 0
counts["python"] += 1                    # no KeyError!
print(counts["python"])                  # 1

# deque: a fast queue (add to one end, remove from the other)
queue = deque(["a", "b"])
queue.append("c")
print(queue.popleft())                   # a   (first in, first out)
```

**Your own files are modules too.** If you have `processor.py` containing a function `tokenize`, then in another file in the same folder:

```python
from processor import tokenize
```

**Third-party packages** (made by other people) are installed with `pip`, e.g. `pip install requests`. You'll do this in Stage 6.

## 3.13 Errors: your best teachers

Errors are not failures. They are Python telling you exactly what's wrong. **Read them from the bottom up.**

```
Traceback (most recent call last):
  File "main.py", line 3, in <module>
    print(ages["Zed"])
KeyError: 'Zed'
```

- **Last line:** *what* went wrong (`KeyError: 'Zed'`, the key `'Zed'` doesn't exist).
- **Lines above:** *where* (file `main.py`, line 3).

Common errors and what they mean:

| Error | Typical cause |
|---|---|
| `SyntaxError` | Typo: missing colon, bracket, or quote |
| `IndentationError` | Wrong spacing at the start of a line |
| `NameError` | Used a variable that doesn't exist (misspelt, or not defined yet) |
| `TypeError` | Wrong kind of value, e.g. adding a number to a string |
| `KeyError` | Dictionary key doesn't exist |
| `IndexError` | List position doesn't exist (`fruits[10]` in a 3-item list) |
| `ValueError` | Right type but a bad value, e.g. `int("abc")` |
| `FileNotFoundError` | File path is wrong, or you're running from the wrong folder |
| `ModuleNotFoundError` | Package not installed / virtual environment not active |
| `ZeroDivisionError` | Divided by zero |

**Handling errors on purpose with `try / except`:**

```python
try:
    number = int("abc")
except ValueError:
    print("That wasn't a number")
```

Python *tries* the risky code; if that specific error happens, it runs the `except` block instead of crashing. You'll need this in the crawler (web requests fail all the time).

## 3.14 List comprehensions (a shortcut you can learn later)

🐍 A compact way to build a new list from an old one.

The long way:
```python
numbers = [1, 2, 3, 4]
doubled = []
for n in numbers:
    doubled.append(n * 2)
```

The comprehension way (same result):
```python
doubled = [n * 2 for n in numbers]           # [2, 4, 6, 8]
```

With a filter:
```python
words = ["the", "python", "is", "fun"]
stop = {"the", "is"}
kept = [w for w in words if w not in stop]   # ['python', 'fun']
```

Read it aloud: "make a list of `w`, for each `w` in `words`, if `w` is not in `stop`."

**Beginner advice:** always write the long `for` loop first. Once it works, convert it to a comprehension if you like. Both are correct.

## 3.15 Sorting and `lambda`

🐍 `sorted()` returns a new sorted list.

```python
print(sorted([3, 1, 2]))                   # [1, 2, 3]
print(sorted([3, 1, 2], reverse=True))     # [3, 2, 1]
```

To sort a dictionary's pairs by their **value** (exactly what ranking needs):

```python
scores = {"doc1": 0.10, "doc2": 0.16, "doc3": 0.0}

ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
print(ranked)      # [('doc2', 0.16), ('doc1', 0.1), ('doc3', 0.0)]
```

Unpacking that:
- `scores.items()` gives pairs like `("doc1", 0.10)`.
- `key=` tells `sorted` *what to sort by*.
- `lambda item: item[1]` is a tiny nameless function meaning "given a pair called `item`, give me its second part (position 1), the score."
- `reverse=True` puts the biggest first.

## 3.16 Classes (a preview; needed only at the end)

🐍 A **class** bundles data and the functions that work on it into one "object." You don't need this until you tidy up your finished project.

```python
class Dog:
    def __init__(self, name):      # runs when you create a Dog
        self.name = name           # store data inside the object

    def bark(self):                # a "method": a function belonging to the object
        return f"{self.name} says woof"

rex = Dog("Rex")
print(rex.bark())                  # Rex says woof
```

Later you'll turn your project into a `SearchEngine` class.

## 3.17 The `main` guard

🐍 You'll often see this at the bottom of a script:

```python
def main():
    print("Program starts here")

if __name__ == "__main__":
    main()
```

It means: "run `main()` only if this file was run directly, not if it was imported by another file." That lets you reuse your functions in other files without accidentally running the whole program.

## 3.18 Self-check before moving on

You should be able to explain (in your own words):

- [ ] the difference between a list, a dictionary, and a set
- [ ] why `text.lower()` alone doesn't change `text`
- [ ] the difference between `print` and `return`
- [ ] how to read an error message
- [ ] what `for word in words:` does

If any are shaky, re-run the examples in the REPL. It's much cheaper to fix now than mid-project.

**Mini-exercises** (do these! about 30 minutes):

1. Write a function `count_words(sentence)` that returns a dictionary of word counts. `count_words("a b a")` → `{"a": 2, "b": 1}`.
2. Write a function that takes a list of numbers and returns only the even ones.
3. Write a program that asks the user for a word (with `input`) until they type `quit`, and prints the word in uppercase.
4. Given two sets of numbers, print the ones they have in common.

---

# Chapter 4 — Setting up your workspace

## 4.1 Install Python

1. Go to [python.org/downloads](https://www.python.org/downloads/) and download Python 3.11 or newer.
2. **Windows:** on the first installer screen, tick **"Add python.exe to PATH"** before clicking Install. (Forgetting this is the #1 setup problem.)
3. Check it worked. Open a **new** terminal:

```bash
python --version
```
You should see something like `Python 3.12.4`. (On Mac/Linux you may need `python3 --version`. If so, use `python3` everywhere this guide says `python`.)

## 4.2 Install a code editor

**VS Code** (free, [code.visualstudio.com](https://code.visualstudio.com/)) with its **Python extension** is a great choice. It colours your code, shows errors, and has a built-in terminal (`Ctrl+` ` `).

## 4.3 Create the project folder

```bash
mkdir my_search_engine
cd my_search_engine
mkdir data
```

Open this folder in VS Code (`File → Open Folder`).

## 4.4 Virtual environments

🧠 **Concept.** Different projects need different add-on packages (and different versions of them). A **virtual environment** ("venv") is a private, isolated set of packages for *one* project so projects never interfere with each other. Professional programmers do this for every project.

Create and activate one:

```bash
python -m venv venv
```
- Windows (Command Prompt): `venv\Scripts\activate`
- Windows (PowerShell): `venv\Scripts\Activate.ps1`
- Mac/Linux: `source venv/bin/activate`

When active, your terminal line starts with `(venv)`. **Activate it every time you open a new terminal for this project.**

> PowerShell error about "scripts disabled"? Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt.

Installing packages (later, only when needed):

```bash
pip install requests beautifulsoup4 flask
```

## 4.5 Git: a save-game system for code

🧠 **Git** records snapshots of your project ("commits") so you can undo mistakes and see your history. Install from [git-scm.com](https://git-scm.com/).

```bash
git init                        # once, at the start
```

Create a file called `.gitignore` containing:
```
venv/
__pycache__/
*.pyc
```
(This tells Git not to track the virtual environment.)

After each working stage:

```bash
git add .
git commit -m "Stage 1: load documents"
```

Commit after every checkpoint. Then, no matter how badly you break things later, you can get back to something that worked.

## 4.6 Your first script

Create `hello.py`:

```python
print("My search engine project begins!")
```
Run it: `python hello.py`. Seeing output means your setup works. You can delete `hello.py` afterwards.

## 4.7 Final project layout

You'll grow into this structure. **Don't create everything now**; add each file when its stage arrives.

```
my_search_engine/
├── README.md
├── NOTES.md              # your learning diary
├── .gitignore
├── venv/                 # virtual environment (not tracked by Git)
├── data/                 # your documents (.txt files or crawled pages)
├── loader.py             # Stage 1: load documents
├── processor.py          # Stage 2: clean text
├── indexer.py            # Stage 3: build the index
├── search.py             # Stages 4-5: search and rank
├── crawler.py            # Stage 6: fetch web pages
├── storage.py            # Stage 7: save / load the index
├── app.py                # Stage 8: web interface
├── templates/            # Stage 8: HTML pages
└── tests/                # Stage 9
```

🧠 **Why many small files?** This is a design principle called **separation of concerns**: each file does *one job*. When something breaks you immediately know which file to open.

---

# Stage 1 — Documents (your data)

## Goal (in plain English)

> "Read a folder of text files into my program so I can work with them."

## 🧠 Concepts

**Document.** In search, a *document* is any chunk of text you want to be searchable: a web page, a note, an email, a PDF. It doesn't have to be a "Word document."

**Corpus.** The whole collection of documents is called the **corpus** (plural: *corpora*). Your search engine searches a corpus.

**Why text files first?** Because they're the simplest possible input, and they let you finish stages 1 to 5 without dealing with the internet.

**Data structure choice.** We'll store the corpus as a **dictionary**:

```python
{
    "doc1.txt": "Python is a fun language to learn.",
    "doc2.txt": "Learning Python is fun and Python is fast.",
    "doc3.txt": "Cats are fun animals.",
}
```
Keys are document names (IDs). Values are the full text. A dictionary is perfect because it gives you "name → text" lookups.

## Python you need

Review: strings (3.3), dictionaries (3.6), loops (3.9), functions (3.10), files and `pathlib` (3.11).

## 🛠️ Baby steps

### Step 1. Create the data

In your `data/` folder create text files. Start with the three from the running example (`doc1.txt`, `doc2.txt`, `doc3.txt`, each containing the sentence shown). Then add **5 to 7 more** of your own, 2 to 5 sentences each, on different topics (cricket, cooking, space, cities, music...). Make some share words on purpose, so your search has something interesting to find.

### Step 2. Read *one* file and print it

Open a new file `loader.py`. Write code that opens `data/doc1.txt` and prints its contents. Run it.

<details>
<summary>💡 Hint</summary>

```python
with open("data/doc1.txt", "r", encoding="utf-8") as file:
    text = file.read()
print(text)
```
</details>

### Step 3. List the files in the folder

Use `pathlib` to print the **names** of all `.txt` files in `data/`. Try `sorted(...)` on the result so the order is predictable.

### Step 4. Read every file into a dictionary

Combine Steps 2 and 3: loop over the files and fill a dictionary `{filename: text}`. Print how many documents you loaded.

### Step 5. Wrap it in a function

Turn your code into a function:

```python
def load_documents(folder):
    """Read every .txt file in `folder` and return {filename: text}."""
    ...
```

Then test it from the bottom of the file:

```python
if __name__ == "__main__":
    docs = load_documents("data")
    print(f"Loaded {len(docs)} documents")
    for name, text in docs.items():
        print(name, "->", text[:50])
```

<details>
<summary>💡 Hint: skeleton</summary>

```python
from pathlib import Path

def load_documents(folder):
    documents = {}
    for path in sorted(Path(folder).glob("*.txt")):
        # TODO: read the file's text
        # TODO: store it: documents[path.name] = ...
        pass
    return documents
```
</details>

## ⚠️ Common errors

| You see | Why | Fix |
|---|---|---|
| `FileNotFoundError` | Wrong path or wrong "current folder" | Run from the project folder; `print(Path.cwd())` to see where you are |
| Loaded 0 documents | Folder name misspelt, or files aren't `.txt` (e.g. `doc1.txt.txt`; Windows hides extensions!) | Turn on "File name extensions" in File Explorer |
| `UnicodeDecodeError` | File saved in a strange encoding | Save as UTF-8, and always pass `encoding="utf-8"` |

## ✅ Checkpoint

`load_documents("data")` returns a dictionary of `{filename: text}`. Commit: `git commit -m "Stage 1"`.

---

# Stage 2 — Text processing

## Goal (in plain English)

> "Turn messy text into a clean list of standard words, so that 'Python', 'python' and 'Python,' all count as the same word."

## 🧠 Concepts

### Why this stage exists

Computers are **literal**. To Python, these are four completely different strings:

```
"Python"     "python"     "Python,"     "PYTHON!"
```

But to a human they're all "python." If the index stores `"Python,"` and the user searches `"python"`, there'd be no match, and your engine would seem broken. **Text processing** (also called **normalisation** or **preprocessing**) fixes this by converting text into a consistent form.

The same processing must be applied **both** to the documents (when indexing) and to the user's query (when searching). If you forget the second one, nothing matches. Remember this. It causes more search bugs than anything else.

### The processing pipeline

A **pipeline** is a series of steps where each one's output feeds the next:

```
raw text ─▶ lowercase ─▶ remove punctuation ─▶ split into words ─▶ remove stop words ─▶ (stem) ─▶ tokens
```

| Step | Before | After | Why |
|---|---|---|---|
| **1. Lowercase** | `"Python is FUN"` | `"python is fun"` | Case shouldn't matter |
| **2. Remove punctuation** | `"fun, right?"` | `"fun  right "` | Commas and dots shouldn't stick to words |
| **3. Tokenise** (split) | `"python is fun"` | `["python", "is", "fun"]` | A list of individual words is easier to count |
| **4. Remove stop words** | `["python", "is", "fun"]` | `["python", "fun"]` | Very common words carry almost no meaning |
| **5. Stemming** *(optional)* | `["learning", "learns"]` | `["learn", "learn"]` | Match different forms of one word |

**Token:** one unit after splitting, usually a word. **Tokenisation** is the act of splitting text into tokens.

**Stop words:** extremely common words (`the`, `is`, `a`, `and`, `of`, `to`...) that appear in nearly every document. Searching for them is useless because everything matches. Removing them also makes the index smaller. Real search engines sometimes keep them (so "to be or not to be" works), so this is a **design decision**.

**Stemming:** cutting words down to a root so that *learn*, *learning*, *learned*, *learns* all match. A stemmer is a set of chopping rules; it's crude and produces non-words (`"studies"` → `"studi"`), but consistently, and consistency is all search needs.

## Python you need

String methods `.lower()`, `.split()`, `.replace()` (3.3), loops (3.9), functions (3.10), sets (3.7), the `string` module, list comprehensions (3.14, optional).

## 🛠️ Baby steps

Create `processor.py`. Build the pipeline **one step at a time**, testing each in the REPL first.

### Step 1: Lowercase

Write `to_lower(text)`, or just use `.lower()` inside a bigger function. Remember: strings don't change in place, so use the result.

### Step 2: Remove punctuation

Python provides a ready-made list of punctuation characters:

```python
import string
print(string.punctuation)     # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
```

**Approach A: a loop with `.replace()`**

```python
text = "Hello, World!"
for character in string.punctuation:
    text = text.replace(character, " ")
print(text)                    # "Hello  World "
```
We replace punctuation with a **space**, not with nothing. Why? Think of `"hello,world"`: removing the comma gives `"helloworld"` (one wrong word), but replacing with a space gives two correct words. Extra spaces are harmless because `.split()` ignores them.

**Approach B: `str.translate` (faster, more advanced)**

```python
table = str.maketrans(string.punctuation, " " * len(string.punctuation))
clean = "Hello, World!".translate(table)
```
`maketrans` builds a "swap this character for that one" table; `translate` applies it in one go. Try A first; return to B later.

**Approach C: regular expressions.** `re.findall(r"[a-z0-9]+", text.lower())` grabs runs of letters and digits directly, skipping everything else. Powerful, but regexes are their own learning journey. Save for later.

⚠️ **Design decision: apostrophes.** What should `"don't"` become? `"don t"` (both parts), `"dont"`, or `"don't"`? There's no single right answer. Pick one, write your choice in `NOTES.md`, and move on. Perfect is the enemy of finished.

### Step 3: Tokenise

`"python  is fun ".split()` gives `['python', 'is', 'fun']`. Notice `.split()` with **no argument** handles multiple spaces for you.

Now combine steps 1 to 3 into:

```python
def tokenize(text):
    """Lowercase the text, remove punctuation, and return a list of words."""
    ...
```

Test with tricky inputs:

| Input | Expected output |
|---|---|
| `"Hello, World!!"` | `["hello", "world"]` |
| `"Python is fun."` | `["python", "is", "fun"]` |
| `"   lots   of   spaces   "` | `["lots", "of", "spaces"]` |
| `""` (empty) | `[]` |
| `"C++ & Python3"` | your call! (write down what you chose) |

### Step 4: Remove stop words

Create a **set** of stop words. A set is right here because "is this word in the stop list?" is very fast:

```python
STOP_WORDS = {"a", "an", "the", "is", "are", "was", "were", "and", "or",
              "of", "to", "in", "on", "it", "this", "that"}
```

Write:

```python
def remove_stop_words(tokens):
    """Return the tokens with all stop words removed."""
    ...
```

Loop through tokens; keep each one that is **not in** `STOP_WORDS`.

### Step 5: Chain them together

```python
def process(text):
    """Full pipeline: raw text -> list of clean tokens."""
    tokens = tokenize(text)
    tokens = remove_stop_words(tokens)
    return tokens
```

Verify against the running example:

```python
process("Learning Python is fun and Python is fast.")
# expected: ['learning', 'python', 'fun', 'python', 'fast']
```

(The stop-word set above already contains every stop word this example needs: `is`, `a`, `to`, `and`, `are`.)

### Step 6 (optional but educational): Write a tiny stemmer

Goal: `learning`, `learned`, `learns` → `learn`. Rough idea in plain English:

> If the word ends with "ing", "ed", "es", or "s", chop that ending off, but only if enough letters remain (so "is" doesn't become "i").

<details>
<summary>💡 Hint</summary>

```python
def simple_stem(word):
    for suffix in ["ing", "ed", "es", "s"]:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            return word[:-len(suffix)]
    return word
```
`word[:-3]` means "everything except the last 3 characters."
</details>

Then test it on lots of words. You'll find it fails ("news" → "new", "was" is safe due to length rule, "bus" → "bu"...). **That is the lesson**: stemming is hard, and that's why smart people wrote real stemmers. When you're ready:

```bash
pip install nltk
```
```python
from nltk.stem import PorterStemmer
stemmer = PorterStemmer()
print(stemmer.stem("running"))    # run
print(stemmer.stem("studies"))    # studi
```
Compare it against yours.

**Should you use a stemmer in the engine?** Try both and see. Notice that with stemming, the query `learn` will also find documents that only contain `learning`. That's better recall (finds more), but sometimes worse precision (finds some wrong things).

## ⚠️ Common errors

- Forgetting `text = text.lower()` and using `text.lower()` alone.
- Returning `None` because you forgot `return`.
- Applying `.split()` **before** removing punctuation, leaving `"world!"` as a token.
- Processing documents one way and queries another.

## ✅ Checkpoint

```python
process("The Quick brown FOX, jumped!")
# ['quick', 'brown', 'fox', 'jumped']
```

Write **at least 5 test cases** in a scratch file, using `print` to compare actual vs expected. (In Stage 9 you'll turn these into real tests.) Commit.

---

# Stage 3 — The inverted index (the heart of search)

## Goal (in plain English)

> "Build a lookup table where I can type a word and instantly get every document that contains it, and how many times."

## 🧠 Concepts

### Forward index vs inverted index

After Stage 2, each document is a list of words. That's a **forward index**: *document → its words*.

```
doc1 → ["python", "fun", "language", "learn"]
doc2 → ["learning", "python", "fun", "python", "fast"]
doc3 → ["cats", "fun", "animals"]
```

To find "python" in this structure you must **check every document**. That's the slow way we wanted to avoid.

An **inverted index** flips it around: *word → the documents containing it*.

```
python   → doc1, doc2
fun      → doc1, doc2, doc3
language → doc1
learn    → doc1
learning → doc2
fast     → doc2
cats     → doc3
animals  → doc3
```

Now "find python" is **one dictionary lookup**. No scanning. It's called "inverted" because it's the reverse of the natural "document contains words" direction. (It is exactly the index at the back of a book.)

### Storing counts (postings)

For ranking we also need to know **how many times** each word appears in each document. So each entry becomes a small dictionary:

```python
index = {
    "python":   {"doc1.txt": 1, "doc2.txt": 2},
    "fun":      {"doc1.txt": 1, "doc2.txt": 1, "doc3.txt": 1},
    "language": {"doc1.txt": 1},
    ...
}
```

Read it: `index["python"]["doc2.txt"]` → `2` means "the word *python* appears 2 times in *doc2*." Each `{doc: count}` entry is called a **posting**, and the whole list of postings for a word is a **posting list**.

### Document lengths

We also record how many words each document has after processing:

```python
doc_lengths = {"doc1.txt": 4, "doc2.txt": 5, "doc3.txt": 3}
```
Why? A word appearing 5 times in a 10-word note is far more significant than 5 times in a 10,000-word book. Ranking (Stage 5) needs these lengths.

### Later upgrade: positions

Instead of just a count you can store *where* in the document the word occurs (position 0, 14, 22...). That enables **phrase search** ("machine learning" as a phrase). Ignore this for now; build counts first.

## Python you need

Dictionaries in depth, nested dictionaries, `.get()`, `in` (3.6); loops and `enumerate` (3.9); `Counter` and `defaultdict` (3.12).

## 🛠️ Baby steps

Create `indexer.py`. It will **import** your `process` function:

```python
from processor import process
```

### Step 1: Count words in ONE document, manually

Take the token list `["learning", "python", "fun", "python", "fast"]`. Using an empty dictionary and a loop (like the "counting words" example in 3.6), produce:

```python
{"learning": 1, "python": 2, "fun": 1, "fast": 1}
```
Print it and check it by eye. (Later you can replace your loop with `Counter(tokens)`, but write the loop by hand first so you understand what `Counter` does.)

### Step 2: Put those counts into the big index

For each `(word, count)` from that document, you need to do:

```
index[word][doc_name] = count
```

But the first time you see a word, `index[word]` doesn't exist yet → **KeyError**. You must create the inner dictionary first. In plain English:

> "If this word isn't in the index yet, give it an empty dictionary. Then record this document's count under it."

Handle this with an `if word not in index:` check (or `setdefault`, or a `defaultdict`, whichever you can explain in your own words).

### Step 3: Do it for ALL documents

Loop through `documents.items()`, process each text, count, and insert. Also fill `doc_lengths[doc_name] = len(tokens)` in the same loop.

### Step 4: Wrap it in a function

```python
def build_index(documents):
    """Return (index, doc_lengths) built from {doc_name: text}."""
    ...
```

<details>
<summary>💡 Hint: skeleton</summary>

```python
def build_index(documents):
    index = {}
    doc_lengths = {}

    for doc_name, text in documents.items():
        tokens = process(text)
        doc_lengths[doc_name] = len(tokens)

        # TODO: count how many times each token appears in this document
        # TODO: for each (token, count): add it to index[token][doc_name]

    return index, doc_lengths
```
</details>

### Step 5: Inspect the result

Print the index prettily:

```python
for word in sorted(index):
    print(word, "->", index[word])
```

## Trace it by hand (do this on paper!)

Take the running example. After processing each document you get the lists shown in Chapter 1. Now, **on paper**, build the index step by step. Compare with your program's output. If they differ, one of them (probably your program) has a bug. This paper-tracing habit is how professional programmers debug.

## ⚠️ Common errors

- `KeyError` when writing into `index[word][doc]` because `index[word]` doesn't exist yet.
- Creating **one** counts dictionary outside the loop and reusing it across documents (counts from doc1 leak into doc2). Make a fresh count for each document.
- Forgetting to `return` both values (or unpacking the wrong number: `index, lengths = build_index(docs)`).
- Modifying a dictionary *while looping over it*.

## ✅ Checkpoint

- `index["python"]` → `{"doc1.txt": 1, "doc2.txt": 2}` (for the running example)
- `doc_lengths` → `{"doc1.txt": 4, "doc2.txt": 5, "doc3.txt": 3}`
- Looking up `index["python"]` is one step, not a scan of all documents.

Commit: `git commit -m "Stage 3: inverted index"`.

---

# Stage 4 — Searching the index

## Goal (in plain English)

> "Take what the user typed, and return the documents that match."

## 🧠 Concepts

### A query is just another piece of text

The user types `Python FUN!`. Your index contains `python` and `fun`, lowercase, no punctuation. So the query has to go through the **same** `process()` function first:

```
"Python FUN!"  ─▶  process()  ─▶  ["python", "fun"]
```

This is the golden rule from Stage 2. **Same pipeline for documents and queries.**

### Looking up a word

After processing, each query word is looked up in the index:

```python
index["python"]   # {"doc1.txt": 1, "doc2.txt": 2}
index["fun"]      # {"doc1.txt": 1, "doc2.txt": 1, "doc3.txt": 1}
```

We only care *which documents* here (not counts yet), so we want just the **keys**. Fun fact: looping over a dictionary (or turning it into a set) gives you its keys:

```python
set(index["python"])    # {"doc1.txt", "doc2.txt"}
```

### OR search vs AND search

With several query words, "matches" can mean two things:

| Style | Meaning | Set operation | `python fun` on the running example |
|---|---|---|---|
| **OR** | The document contains **at least one** word | union `\|` | doc1, doc2, doc3 |
| **AND** | The document contains **all** the words | intersection `&` | doc1, doc2 |

This is precisely why we studied sets in Chapter 3. Picture two overlapping circles: OR is everything in either circle; AND is only the overlap.

Google-style engines default to AND (all your words must appear) and then rank. OR-style is more forgiving. Build both, then choose a default.

### What if a word isn't in the index?

- **OR:** just ignore it; other words might still match.
- **AND:** the answer is *no documents*, since no document can contain a word that isn't anywhere. That is correct behaviour, not a bug.

## Python you need

Sets and set operations (3.7), `.get()` with a default (3.6), loops, functions, `input()` and `while True` (3.9).

## 🛠️ Baby steps

Create `search.py`. Import what you need:

```python
from processor import process
```

### Step 1: Get the documents for one word

```python
def docs_for_term(term, index):
    """Return the set of document names that contain `term` (empty set if none)."""
    ...
```
Use `index.get(term, {})` so that an unknown word gives an empty dictionary instead of a KeyError. Then convert the keys to a set.

### Step 2: OR search

Plain English plan:

1. Process the query into tokens.
2. Start with an empty set of results.
3. For each token, find its documents and **add** them to the results (union).
4. Return the results.

```python
def search_or(query, index):
    ...
```

### Step 3: AND search

Plain English plan:

1. Process the query into tokens.
2. If there are no tokens, return an empty set.
3. Start `results` with the documents of the **first** token.
4. For each remaining token, keep only documents that are also in that token's set (intersection).
5. Return `results`.

<details>
<summary>💡 Hint: skeleton</summary>

```python
def search_and(query, index):
    tokens = process(query)
    if not tokens:
        return set()

    results = docs_for_term(tokens[0], index)
    for token in tokens[1:]:
        # TODO: keep only documents that are ALSO in this token's set
        pass
    return results
```
`tokens[1:]` means "all tokens except the first."
</details>

### Step 4: Edge cases

Test that these behave sensibly (no crashes!):

| Query | What should happen |
|---|---|
| `""` | Empty result, and a friendly message in the UI |
| `"the"` (only a stop word) | Empty (everything got removed by processing) |
| `"zzzzz"` (not in any doc) | Empty |
| `"python zzzzz"` with AND | Empty |
| `"python zzzzz"` with OR | Same as just `"python"` |
| `"PYTHON"` | Same as `"python"` |

### Step 5: A command-line search loop

```
Search> python fun
Found 2 results: doc1.txt, doc2.txt
Search> quit
```

Plan: load documents → build the index → `while True:` ask for input → if the user types `quit`, `break` → otherwise search and print.

### Step 6 (bonus): NOT search

Let the user write `python -cats` to mean "python but not cats." Split the query on spaces; words that start with `-` go into an "exclude" list. Use the set **difference** operator `-`.

## ⚠️ Common errors

- Forgetting to call `process(query)`. Then `"Python"` never matches.
- Mutating your index results (e.g. calling `results.update(...)` on the *same set object* that lives inside your index). Convert to a fresh `set(...)` to be safe.
- Empty query crashing on `tokens[0]` (`IndexError`).

## ✅ Checkpoint

You can search the running example:

```
OR  "python fun"  → {doc1, doc2, doc3}
AND "python fun"  → {doc1, doc2}
AND "cats python" → set()
```

🎉 **You have just built a working search engine.** Results aren't sorted yet, but everything after this is improvement. Commit and celebrate.

---

# Stage 5 — Ranking results

## Goal (in plain English)

> "When 200 documents match, show the most relevant ones first."

## 🧠 Concepts

### Why ranking matters

Real searches match hundreds of documents. Users only look at the first few, so **the order is the product**. Ranking gives each matching document a **score** (a number: bigger = more relevant) and sorts by it.

```
python fun  →  doc2 (0.162),  doc1 (0.101),  doc3 (0.000)
```

How do we compute a score? The history of search is a series of smarter and smarter answers to that question. We'll climb the ladder one rung at a time.

### Rung 1: Term Frequency (TF) by raw count

Simplest idea: *the more times a word appears in a document, the more relevant it is.*

`python` appears twice in doc2 and once in doc1, so doc2 wins. Sensible!

**Flaw:** a 10,000-word document will contain almost any word many times purely because it's long. Long documents unfairly win.

### Rung 2: Normalised TF

Divide the count by the document's length, giving the **fraction** of the document made of that word:

```
TF(word, doc) = (times word appears in doc) / (number of words in doc)
```

Running example, the word `python`:

- doc1: 1 / 4 = **0.25**
- doc2: 2 / 5 = **0.40**

This is why we saved `doc_lengths` in Stage 3.

### Rung 3: Inverse Document Frequency (IDF), *rarity matters*

Not all query words are equally informative. Suppose a user searches `the guide to photosynthesis`. Almost every document contains `guide`, but very few contain `photosynthesis`. A match on the rare word is a **much stronger** signal.

**IDF** measures rarity:

```
IDF(word) = ln( N / df )

   N  = total number of documents
   df = number of documents that contain the word ("document frequency")
```

🧠 **What is `ln`?** It's the *natural logarithm*, a function that turns big ratios into small, gentle numbers. You don't need the theory. Just know: `ln(1) = 0`, and it grows slowly as the input grows. In Python: `math.log(x)`.

Running example (N = 3):

| Word | df | N / df | IDF = ln(N/df) | Meaning |
|---|---|---|---|---|
| `fun` | 3 | 1 | **0.000** | In *every* doc → useless for telling docs apart |
| `python` | 2 | 1.5 | **0.405** | Fairly common |
| `cats` | 1 | 3 | **1.099** | Rare → very informative |

The rarer the word, the higher the IDF.

### Rung 4: TF-IDF

Multiply the two ideas:

```
TF-IDF(word, doc) = TF(word, doc) × IDF(word)
```

"A word scores high in a document if it appears **often there** but **rarely elsewhere**."

For a query with several words, the document's score is the **sum** of the TF-IDF of each query word.

### Full worked example: query `python fun`

```
doc1:  python → TF 0.25 × IDF 0.405 = 0.101
       fun    → TF 0.25 × IDF 0.000 = 0.000
       score = 0.101

doc2:  python → TF 0.40 × IDF 0.405 = 0.162
       fun    → TF 0.20 × IDF 0.000 = 0.000
       score = 0.162

doc3:  python → not present = 0
       fun    → TF 0.33 × IDF 0.000 = 0.000
       score = 0.000
```

Ranking: **doc2 (0.162) > doc1 (0.101) > doc3 (0.000)**. 

Notice how `fun` contributed nothing because every document has it. That's IDF working exactly as intended.

> **Small-corpus note:** with only 3 documents, IDF values are extreme. Use 10 or more documents when you test ranking, and results will feel much more natural. Some implementations also use `ln(1 + N/df)` so a word in all documents gets a small positive weight instead of exactly 0. Both are acceptable variants.

### Rung 5: BM25 (what real engines use)

BM25 is TF-IDF with two upgrades:

1. **Saturation.** In TF-IDF, a word appearing 100 times scores 10× more than one appearing 10 times. But after a few mentions, extra repetition adds little real relevance. BM25 makes the benefit **level off**. A parameter `k1` controls how quickly.
2. **Smarter length handling.** Instead of naively dividing by length, BM25 compares each document's length to the **average** length, controlled by a parameter `b` (0 = ignore length; 1 = fully normalise).

The formula, for one query word `q` in document `D`:

```
                          f(q,D) × (k1 + 1)
score(q,D) = IDF(q) × ─────────────────────────────────────────
                       f(q,D) + k1 × (1 − b + b × |D| / avgdl)

  f(q,D) = how many times q appears in D  (the raw count)
  |D|    = length of D (number of tokens)
  avgdl  = average document length across the corpus
  k1     = 1.5   (common default)
  b      = 0.75  (common default)
  IDF(q) = ln( 1 + (N − df + 0.5) / (df + 0.5) )
```

A document's total score is again the sum over all query words.

**Check your BM25 against this example.** For the running example and the single word `python`: `avgdl = (4+5+3)/3 = 4`, IDF = `ln(1 + 1.5/2.5) ≈ 0.470`.

- doc1 → about **0.470**
- doc2 → about **0.621**

If your numbers match, your BM25 works. Don't panic if the formula looks scary: it's just arithmetic. Type it one piece at a time into variables (`numerator`, `denominator`, `idf`...) instead of one giant line.

## Python you need

`math.log` (3.12), dictionaries of scores and `.get()` (3.6), `sorted(..., key=lambda...)` (3.15), tuples and unpacking (3.5), slicing (`results[:5]`) (3.4).

## 🛠️ Baby steps

Work in `search.py`. Ranking needs three ingredients: the **index**, **doc_lengths**, and the **number of documents** (`len(doc_lengths)`).

### Step 1: Rank by raw count (Rung 1)

Plain English:

1. Process the query into tokens.
2. Make an empty dictionary `scores = {}`.
3. For each token, look up its postings `{doc: count}`. For each `(doc, count)`, **add** `count` to `scores[doc]`.
4. Sort `scores.items()` by score, highest first.
5. Return the sorted list of `(doc, score)`.

Adding to a score that may not exist yet? That's the same "counting" pattern as before: `scores[doc] = scores.get(doc, 0) + count`.

### Step 2: Sort and show top results

```python
ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
top_five = ranked[:5]
```
Print them as `1. doc2.txt (score 0.162)`.

### Step 3: Upgrade to TF (normalised)

Divide each count by `doc_lengths[doc]`. Compare the ranking against Step 1 for the same queries.

### Step 4: Upgrade to TF-IDF

For each query token:

1. `df = len(index[token])` (skip the token if it's not in the index, to avoid `KeyError` and `log(0)` errors).
2. `idf = math.log(N / df)`.
3. For each `(doc, count)`: `tf = count / doc_lengths[doc]`, then `scores[doc] += tf * idf`.

<details>
<summary>💡 Hint: skeleton</summary>

```python
import math
from processor import process

def rank_tfidf(query, index, doc_lengths, top_k=5):
    tokens = process(query)
    total_docs = len(doc_lengths)
    scores = {}

    for token in tokens:
        if token not in index:
            continue                       # skip unknown words
        postings = index[token]            # {doc_name: count}
        df = len(postings)
        idf = math.log(total_docs / df)

        for doc_name, count in postings.items():
            tf = count / doc_lengths[doc_name]
            # TODO: add tf * idf to this document's score
            pass

    # TODO: sort scores highest-first and return the top_k
```
</details>

### Step 5: Check against the worked example

Run `python fun` on the three running-example documents. You should get `doc2 ≈ 0.162`, `doc1 ≈ 0.101`, `doc3 = 0`. If yes, your ranking is correct. If not, print `tf` and `idf` for each word and compare with the numbers above.

### Step 6 (challenge): Implement BM25

Copy your TF-IDF function, then change the scoring line to the BM25 formula. Compute `avgdl` once (`sum(doc_lengths.values()) / len(doc_lengths)`). Verify with the check values above.

### Step 7: Experiments (this is where you actually learn)

Write your observations in `NOTES.md`:

1. Search a word that is in **every** document. What are the scores? Why?
2. Search a rare word. Does the right document come first?
3. Make one document **10× longer** by pasting text repeatedly. Compare raw count vs TF vs BM25. Which ranking behaves best?
4. Search two words, one rare and one common. Which drives the ranking?
5. Compare TF-IDF and BM25 on 5 queries. Where do they disagree? Which looks better *to you*?

## ⚠️ Common errors

- `ZeroDivisionError` or `ValueError: math domain error`: usually `df` is 0 or `N` is 0. Skip words that aren't in the index.
- Sorting ascending (lowest first). Add `reverse=True`.
- Overwriting instead of accumulating: `scores[doc] = value` versus `scores[doc] += value` (which needs the key to exist; use `.get`).
- Doing integer maths by mistake in old code. In Python 3, `/` is fine, but `//` throws away decimals.
- Forgetting to use the *processed* tokens.

## ✅ Checkpoint

`search("python fun")` returns a sorted list of `(document, score)` with the best first, and it matches the worked example. Commit: `git commit -m "Stage 5: ranking"`.

---

# Stage 6 — The crawler

## Goal (in plain English)

> "Automatically collect pages from a website by following links, and save their text so my search engine can index them."

## 🧠 Concepts

### How the web works (the 2-minute version)

- A **URL** is the address of a web page: `https://books.toscrape.com/catalogue/page-2.html`
  - `https` = the protocol (how to talk)
  - `books.toscrape.com` = the **domain** (which server)
  - `/catalogue/page-2.html` = the **path** (which page on that server)
- When you open a page, your browser sends an **HTTP request** ("please give me this page") and the server sends back a **response**.
- The response has a **status code**: `200` = OK, `404` = not found, `403` = forbidden, `500` = server error, `429` = you're asking too fast.
- The body of the response is usually **HTML**, the page's source code.

### What HTML looks like

HTML wraps content in **tags**:

```html
<html>
  <head><title>My Page</title></head>
  <body>
    <h1>Welcome</h1>
    <p>Some text with a <a href="/about.html">link</a>.</p>
  </body>
</html>
```

- `<title>` = the page title, `<p>` = paragraph, `<h1>` = heading.
- `<a href="...">` = a **link**. The `href` attribute is where the link points.

A crawler needs two things from every page: **the visible text** (to index) and **the links** (to know where to go next).

### What is a crawler?

A crawler (also called a **spider** or **bot**) is a loop:

```
1. Start with a "seed" URL in a to-visit queue.
2. Take the next URL from the queue.
3. Download the page.
4. Save its text (for the index).
5. Find all links on it; add any NEW ones to the queue.
6. Repeat until the queue is empty or a limit is reached.
```

Two data structures make this work:

| Structure | Python tool | Purpose |
|---|---|---|
| **Frontier / queue** | `collections.deque` | URLs waiting to be visited, in order (first in, first out) |
| **Visited set** | `set` | URLs already done, so you never visit twice (and never loop forever) |

This visiting pattern is called **breadth-first search**: you finish all links on the current level before going deeper.

### Being a polite, legal crawler (not optional!)

Bots that misbehave get blocked and can cause harm. Always:

1. **Check `robots.txt`.** Sites publish rules at `https://site.com/robots.txt` saying what bots may crawl. Respect them.
2. **Wait between requests.** `time.sleep(1)` means at most about one request per second, so you don't overload the server.
3. **Identify yourself** with a `User-Agent` header like `MyLearningBot/0.1`.
4. **Limit your crawl** (e.g. 20 pages). Never leave it unbounded.
5. **Practise on sites built for it:** [books.toscrape.com](https://books.toscrape.com) and [quotes.toscrape.com](https://quotes.toscrape.com). Wikipedia is fine at small scale with delays.
6. **Never** crawl login-protected pages or personal data, and don't republish other people's content.

## Python you need

Modules and `import` (3.12), `pip install` (4.4), `try/except` (3.13), `while` loops (3.9), `deque` and sets (3.12), strings (3.3).

Install two packages (venv active!):

```bash
pip install requests beautifulsoup4
```

- `requests`: downloads web pages.
- `beautifulsoup4` (imported as `bs4`): reads HTML and lets you search inside it.

## 🛠️ Baby steps

Create `crawler.py`. Build it **one tiny piece at a time.**

### Step 1: Download ONE page

```python
import requests

response = requests.get("https://books.toscrape.com", timeout=10)
print(response.status_code)      # 200 means success
print(response.text[:300])       # the first 300 characters of HTML
```
`timeout=10` means "give up after 10 seconds" (always include it, or your program can hang forever).

### Step 2: Parse the HTML

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(response.text, "html.parser")
print(soup.title.string)                 # the page title
```

### Step 3: Extract the visible text

Pages contain invisible junk (`<script>` code, `<style>` rules). Remove those first, then grab the text:

```python
for tag in soup(["script", "style"]):
    tag.decompose()                      # delete the tag from the page
text = soup.get_text(separator=" ")
```
Print the first 300 characters. Does it look like real text? Great. (You'll probably see extra blank space. Processing from Stage 2 handles that.)

### Step 4: Extract the links

```python
for link in soup.find_all("a", href=True):
    print(link["href"])
```
You'll notice many links are **relative** (`catalogue/page-2.html`), not full URLs. Fix that in the next step.

### Step 5: Make URLs absolute and clean

```python
from urllib.parse import urljoin, urldefrag, urlparse

base = "https://site.com/a/b.html"
print(urljoin(base, "../c.html"))        # https://site.com/c.html
print(urljoin(base, "https://x.com"))    # https://x.com   (already absolute, unchanged)

url, fragment = urldefrag("https://site.com/page.html#top")
print(url)                               # https://site.com/page.html   (removes the #top part)

print(urlparse("https://site.com/a/b.html").netloc)    # site.com  (the domain)
```
- `urljoin` turns any relative link into a full URL.
- `urldefrag` removes `#section` parts, so the same page isn't visited twice.
- `netloc` lets you check whether a link stays on the same site. Only follow links to the **same domain**.

Write a helper `extract_links(soup, page_url)` that returns a set of clean, absolute, same-domain URLs.

### Step 6: Respect robots.txt

```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://books.toscrape.com/robots.txt")
rp.read()
print(rp.can_fetch("MyLearningBot", "https://books.toscrape.com/catalogue/page-2.html"))
```
Skip any URL where `can_fetch` returns `False`. (Some practice sites have no `robots.txt`, and that's fine: Python treats missing rules as "allowed.")

### Step 7: The crawl loop

Plain-English plan:

```
queue   = deque([seed_url])
visited = set()
pages   = {}                       # url -> text

while queue is not empty and len(pages) < max_pages:
    url = queue.popleft()
    if url in visited: skip it
    add url to visited
    try:
        download the page
        skip if status isn't 200 or content isn't HTML
        extract text  -> store in pages[url]
        extract links -> add unvisited ones to the queue
    except a network error:
        print a warning and carry on
    wait 1 second
```

<details>
<summary>💡 Hint: skeleton</summary>

```python
import time
from collections import deque

def crawl(seed_url, max_pages=20):
    queue = deque([seed_url])
    visited = set()
    pages = {}          # {url: text}

    while queue and len(pages) < max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            response = requests.get(
                url, timeout=10,
                headers={"User-Agent": "MyLearningBot/0.1"},
            )
            # TODO: skip the page unless status_code == 200
            # TODO: build soup, get text -> pages[url] = text
            # TODO: get links -> append unvisited ones to queue
        except requests.RequestException as error:
            print("Failed:", url, error)

        time.sleep(1)

    return pages
```
</details>

### Step 8: Feed the crawler into your engine

The crawler returns `{url: text}`, which is the **same shape** as your Stage 1 `{filename: text}` dictionary. So you can pass it straight into `build_index()`. That's the payoff of choosing good data structures early. Bonus: also store each page's `<title>` so you can show it in results later.

## ⚠️ Common errors and traps

| Problem | Cause / fix |
|---|---|
| Crawler never stops | No page limit, or `visited` isn't being used |
| Visits the same page repeatedly | URLs differ by `#fragment` or trailing `/`. Clean them |
| `requests.exceptions.ConnectionError` | No internet or blocked site → wrap in `try/except` |
| Crawls into PDFs / images | Check `response.headers.get("Content-Type", "")` contains `text/html` |
| Blocked / status 403 or 429 | You're too fast or bot-blocked. Increase delay; respect the site |
| Wandered off to other websites | You forgot the same-domain check |

## ✅ Checkpoint

Point it at `https://quotes.toscrape.com`, crawl 20 pages, index them, and search for a word from one of the quotes. Commit.

---

# Stage 7 — Saving your index

## Goal (in plain English)

> "Save the index to disk so I don't have to crawl and rebuild every time I start the program."

## 🧠 Concepts

### Memory vs disk

Everything in your variables lives in **RAM** (memory), which is fast but **wiped** when the program ends. To keep data, you must write it to **disk** (a file). Writing data out in a form that can be reloaded later is called **serialisation** (or *persistence*). Reading it back is *deserialisation*.

### Your options

| Option | What it is | Good for | Downsides |
|---|---|---|---|
| **JSON** (`json` module) | Human-readable text format that maps nicely onto dicts and lists | Learning, small/medium data | Slow/large for huge data; some types don't convert |
| **Pickle** (`pickle` module) | Python's own binary format; saves nearly any object | Quick saves | Only Python can read it; **never load pickles from untrusted sources** (can run malicious code) |
| **SQLite** (`sqlite3` module) | A real database in a single file, built into Python | Larger data, real projects | You need to learn some SQL |

Start with **JSON**. Move to SQLite when you want to grow.

### JSON gotchas

- JSON keys must be **strings**.
- JSON has no **sets**; convert them to lists before saving.
- Tuples come back as lists.

## Python you need

Files and `with open` (3.11), dictionaries (3.6), modules (3.12).

## 🛠️ Baby steps

Create `storage.py`.

### Step 1: JSON save and load, in the REPL first

```python
import json

data = {"python": {"doc1.txt": 1, "doc2.txt": 2}}

with open("index.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)          # indent=2 makes the file readable

with open("index.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded == data)                     # True
```
Open `index.json` in your editor and look at it. It's your dictionary as text.

### Step 2: Functions

```python
def save_index(index, doc_lengths, path="index.json"):
    ...

def load_index(path="index.json"):
    ...   # returns (index, doc_lengths)
```
Save both dictionaries together as **one** JSON object: `{"index": ..., "doc_lengths": ...}`.

### Step 3: Smarter startup

Plain English: *"If `index.json` exists, load it. Otherwise, load the documents, build the index, and save it."*  Use `Path("index.json").exists()`.

### Step 4: Store more than counts

For a nice interface you'll want each document's **title**, **URL**, and a **text snippet**. Add a third dictionary `doc_info = {doc_id: {"title": ..., "url": ..., "text": ...}}` and save that too.

### Step 5 (later): SQLite

SQLite stores data in **tables** (like spreadsheets: rows and columns). A taste:

```python
import sqlite3

conn = sqlite3.connect("search.db")           # creates the file if missing
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    url TEXT UNIQUE,
    title TEXT,
    body TEXT)""")

cur.execute("INSERT OR IGNORE INTO documents (url, title, body) VALUES (?, ?, ?)",
            ("https://example.com", "Example", "Some text"))
conn.commit()                                  # actually save the change

cur.execute("SELECT title FROM documents WHERE url = ?", ("https://example.com",))
print(cur.fetchall())                          # [('Example',)]
conn.close()
```

The `?` placeholders (rather than pasting values into the SQL text) protect against a famous attack called **SQL injection**. Always use them. A good next design: tables `documents` and `postings(term, doc_id, count)`. A one-hour SQL tutorial is enough to start.

## ⚠️ Common errors

- `TypeError: Object of type set is not JSON serializable` → convert sets to lists.
- Loading a file that doesn't exist → check `.exists()` first.
- Using `"w"` mode on a file you meant to keep: `"w"` **erases** it first.
- Index out of date after adding documents → decide how you'll rebuild (or add "incremental" updates: skip URLs already stored).

## ✅ Checkpoint

Run your program twice. The **second** start loads instantly without rebuilding. Commit.

---

# Stage 8 — The user interface

## Goal (in plain English)

> "Let a normal person type a search and see nice results, first in the terminal, then in a web browser."

## 🧠 Level 1: Better command-line output

Improve your terminal results to show, for each hit: **rank, title, score, and a snippet** of text.

### Snippets

A **snippet** is a short excerpt around the matching word, so users can see *why* a page matched:

```
1. Intro to Python (score 0.83)
   ...python is a fun and easy language to learn...
```

Plain-English recipe:

1. Take the document's original text and one query word.
2. Find where the word appears: `text.lower().find(word)` returns its position, or `-1` if it's not found.
3. Slice a window around it: `text[max(0, pos - 40) : pos + 80]`.
4. Add `...` at the ends.

(`max(0, ...)` stops the start from going negative.) Later, highlight matches by wrapping them in `**` (terminal) or `<mark>` tags (web).

## 🧠 Level 2: A web interface with Flask

### Concepts

- A **web server** is a program that waits for browser requests and sends back pages. **Flask** is a small Python tool for writing one.
- A **route** connects a URL path to a Python function: visit `/search` → run the `search_page()` function.
- **Request parameters:** when a form is submitted with method `get`, the browser goes to `/search?q=python`. In Flask, `request.args.get("q")` reads `python`.
- A **template** is an HTML file with blanks that Python fills in (using a mini-language called Jinja2).

### Baby step 1: "Hello, Flask"

```bash
pip install flask
```
`app.py`:

```python
from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, search engine!"

if __name__ == "__main__":
    app.run(debug=True)
```
Run `python app.py` and open `http://127.0.0.1:5000` in your browser. You should see the text. (`@app.route` is a **decorator**, a line that attaches behaviour to the function below it. Just use it like a recipe for now.)

### Baby step 2: A search form

Make a folder `templates/` and a file `templates/home.html`:

```html
<!DOCTYPE html>
<html>
  <head><title>My Search Engine</title></head>
  <body>
    <h1>My Search Engine</h1>
    <form action="/search" method="get">
      <input type="text" name="q" placeholder="Search...">
      <button type="submit">Search</button>
    </form>
  </body>
</html>
```
Change `home()` to `return render_template("home.html")`.

### Baby step 3: A results page

Add a `/search` route:

```python
@app.route("/search")
def search_page():
    query = request.args.get("q", "")
    results = ...   # TODO: call your ranking function, build a list of results
    return render_template("results.html", query=query, results=results)
```

And `templates/results.html`:

```html
<h2>Results for "{{ query }}"</h2>

{% if results %}
  {% for r in results %}
    <div>
      <a href="{{ r.url }}">{{ r.title }}</a>
      <small>score {{ "%.3f"|format(r.score) }}</small>
      <p>{{ r.snippet }}</p>
    </div>
  {% endfor %}
{% else %}
  <p>No results found.</p>
{% endif %}
```
`{{ ... }}` prints a value; `{% ... %}` is logic (loops and conditions). Jinja automatically **escapes** text so user input can't inject harmful HTML. Keep that safety on. Build each result as a dictionary, e.g. `{"url": ..., "title": ..., "score": ..., "snippet": ...}`.

⚠️ Load / build your index **once** when the app starts (at the top of `app.py`), not inside the route. Otherwise every search rebuilds everything.

## Python you need

Functions (3.10), dictionaries (3.6), f-strings (3.2), `pip` (4.4), decorators (just use them), basic HTML forms.

## ⚠️ Common errors

- `TemplateNotFound`: the folder must be named exactly `templates`, next to `app.py`.
- Blank results: print `query` and `results` inside the route to see what's happening.
- Changes not showing: keep `debug=True` for auto-reload; refresh the browser.
- Port already in use: close the earlier server (Ctrl+C in its terminal).

## ✅ Checkpoint

You open `http://127.0.0.1:5000`, type a query, and see ranked results with titles and snippets. Commit.

---

# Stage 9 — Testing and measuring quality

## Goal (in plain English)

> "Prove my search engine works, and be able to tell whether a change made it better or worse."

## 🧠 Concepts

### Why test?

Right now you check your code by running it and looking. That works for 200 lines. At 2,000 lines, changing one function silently breaks another, and you won't notice. **Automated tests** are small programs that check your code for you, in a second, every time.

A test says: *"When I give this function this input, it must return this output."*

### `assert`

🐍 `assert` crashes if a condition is False, and does nothing if it's True:

```python
assert 2 + 2 == 4        # fine, silently passes
assert 2 + 2 == 5        # AssertionError: crashes → the test fails
```

### pytest

**pytest** is a tool that finds and runs your tests automatically.

```bash
pip install pytest
```

Create `tests/test_processor.py`:

```python
from processor import tokenize, process

def test_tokenize_lowercases_and_strips_punctuation():
    assert tokenize("Hello, World!!") == ["hello", "world"]

def test_tokenize_empty_string():
    assert tokenize("") == []

def test_process_removes_stop_words():
    assert process("Learning Python is fun and Python is fast.") == [
        "learning", "python", "fun", "python", "fast"
    ]
```

Run from the project folder:

```bash
pytest
```
Green dots = pass. Red F = a failure, with an explanation of exactly what differed.

**Rules of thumb:**

- Function names must start with `test_`.
- One test checks **one behaviour**, with a name saying which.
- Use a **tiny fixed corpus**, your running example, so the expected answers are known.
- Test **edge cases**: empty input, unknown words, very long text.
- If pytest can't find your modules (`ModuleNotFoundError`), run it from the project root, or add an empty file named `conftest.py` there.

## 🛠️ Tasks

1. **Processor tests:** `tokenize`, `remove_stop_words`, `process` (at least 6 cases).
2. **Indexer test:** build an index from the three running-example documents and assert:
   - `index["python"] == {"doc1.txt": 1, "doc2.txt": 2}`
   - `doc_lengths == {"doc1.txt": 4, "doc2.txt": 5, "doc3.txt": 3}`
3. **Search tests:** `search_and("python fun")` returns doc1 and doc2 only; a nonsense word returns an empty set.
4. **Ranking test:** for query `python fun`, the top result is `doc2.txt` and its score is about `0.162`.
   Floating-point numbers can't be compared with `==` reliably, so use `abs(score - 0.162) < 0.001` or `pytest.approx(0.162, abs=0.001)`.
5. **Break something on purpose:** change your code to be wrong (e.g. skip lowercasing), run `pytest`, and watch tests catch it. Undo the change.

## 🧠 Measuring search *quality*

Passing tests means the code does what you told it. It doesn't mean the *results are good*. To measure that, you need **relevance judgements**: your own opinion about which documents *should* come back.

### Build a small test set

Write 10 queries, and for each, list the documents you believe are relevant:

```python
test_queries = {
    "python fast":    {"doc2.txt"},
    "cats":           {"doc3.txt"},
    "learn language": {"doc1.txt", "doc2.txt"},
}
```

### Two key measurements

- **Precision@k**: *Of the top k results I returned, what fraction are actually relevant?* ("Am I showing junk?")
- **Recall**: *Of all the relevant documents that exist, what fraction did I find?* ("Am I missing things?")

**Worked example.** Suppose 4 documents are relevant: `{A, C, D, E}`. Your engine returns, in order, `[A, B, C, F, G]`.

- Top 3 = `[A, B, C]`. Relevant among them: A and C → **Precision@3 = 2/3 ≈ 0.67**
- Relevant found in top 5: A and C → **Recall@5 = 2/4 = 0.50**

Write a function that computes both, run your test queries, and record the average in `NOTES.md`. Now every change has a **number**: did adding stemming raise recall? Did BM25 improve precision? This turns "I think it's better" into evidence.

### Measure speed too

```python
import time
start = time.perf_counter()
results = search("python fun")
print(f"Search took {(time.perf_counter() - start) * 1000:.2f} ms")
```

Time **indexing** and **searching** as you add documents (10 → 100 → 1000). Notice which one grows. That's your first taste of performance engineering.

## ✅ Checkpoint

`pytest` runs green with at least 10 tests, and you have a table of precision/recall numbers for TF-IDF vs BM25.

---

# Stage 10 — Upgrades, and the road to AI

You now have a real search engine. Everything below is **optional and independent**. Pick whatever excites you.

## 10.1 Tidy up: turn it into a class

🐍 Refactor (reorganise without changing behaviour) your functions into one `SearchEngine` class so the data and behaviour live together:

```python
class SearchEngine:
    def __init__(self):
        self.documents = {}
        self.index = {}
        self.doc_lengths = {}

    def add_document(self, name, text): ...
    def build_index(self): ...
    def search(self, query, top_k=5): ...
    def save(self, path): ...
    def load(self, path): ...
```
Run your tests before and after. If they still pass, your refactor is safe. That's the entire point of tests.

## 10.2 Better classical search

| Upgrade | Idea | Skills you'll learn |
|---|---|---|
| **Phrase search** (`"machine learning"`) | Store word *positions*; require positions to be consecutive | Lists, nested data |
| **Typo tolerance / "Did you mean...?"** | **Edit distance** (Levenshtein): how many single-letter changes turn one word into another | Dynamic programming |
| **Autocomplete** | A **trie**, a tree where each path spells a word prefix | Trees, recursion, classes |
| **Synonyms** | A dictionary such as `{"car": ["automobile"]}` expanded at query time | Dictionaries |
| **Title boosting** | Count matches in the title double or triple | Weighted scoring |
| **PageRank** | Rank pages by how many important pages link to them (crawler must record links) | Graphs, iteration, linear algebra intro |
| **Pagination** | Show results 1 to 10, then 11 to 20 | Slicing, web UI |
| **Caching** | Remember answers to popular queries | Dictionaries, memory trade-offs |
| **Faster crawling** | Fetch several pages at once with `asyncio` or threads | Concurrency |

## 10.3 The AI step

This is where your bigger goal begins.

### Keyword search vs meaning search

Your engine matches **words**. Search for `automobile` and it will *not* find a document about `cars`, because the strings differ. **Semantic search** matches **meaning**, so "automobile" finds "car."

| Keyword search (what you built) | Semantic / AI search |
|---|---|
| Matches exact (or stemmed) words | Matches ideas |
| Scoring: TF-IDF or BM25 | Scoring: similarity between **embeddings** |
| Fast, transparent, no model needed | Needs a model; sometimes fuzzy |
| Great for names, codes, exact terms | Great for natural-language questions |

### Concept: vectors and embeddings

A **vector** is just a list of numbers, like coordinates. `(3, 4)` is a point on a 2D map.

An **embedding** is a vector that an AI model produces to represent the **meaning** of a piece of text. The model is trained so that texts with similar meaning get vectors that point in similar directions. (Real embeddings have hundreds of numbers, e.g. 384, not 2. But the idea is the same.)

A toy picture in 2D:

```
cat    = (0.90, 0.10)
kitten = (0.85, 0.20)
car    = (0.10, 0.90)
```
`cat` and `kitten` are near each other; `car` is far away.

### Concept: cosine similarity

To measure "how similar are two vectors," compare the **angle** between them. This is **cosine similarity**:

```
cos(a, b) = (a · b) / (|a| × |b|)

  a · b  = "dot product": multiply matching numbers and add them up
  |a|    = length of the vector = square root of the sum of squares
```

Worked example:

```
cat · kitten = 0.90×0.85 + 0.10×0.20 = 0.785
|cat| ≈ 0.906,  |kitten| ≈ 0.873
cos(cat, kitten) ≈ 0.785 / (0.906 × 0.873) ≈ 0.99   ← almost identical direction

cat · car = 0.90×0.10 + 0.10×0.90 = 0.18
cos(cat, car) ≈ 0.18 / (0.906 × 0.906) ≈ 0.22        ← quite different
```
Result: 1.0 means identical direction, near 0 means unrelated.

🛠️ **Exercise:** implement `dot(a, b)`, `length(a)`, and `cosine(a, b)` yourself in plain Python (about 8 lines). Check against the numbers above. This is the core maths of modern semantic search, and you'll understand it fully instead of treating it as magic.

### Using a real embedding model

```bash
pip install sentence-transformers
```

```python
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")    # downloads once (~90 MB), then works offline

docs = [
    "Cars need fuel and regular maintenance.",
    "Cats are fun animals.",
    "Python is a fun language to learn.",
]
doc_vectors = model.encode(docs)                    # one vector per document

query_vector = model.encode("automobile repair")
scores = util.cos_sim(query_vector, doc_vectors)    # similarity to each document
print(scores)                                       # the "cars" doc should score highest
```
Notice: the query shares **no words** with the first document, yet it wins. That's meaning-based search.

### Hybrid search: the best of both

Keyword scores catch exact matches; semantic scores catch meaning. Combine them:

1. Compute BM25 scores (yours!) and semantic scores.
2. **Normalise** each to the range 0 to 1 (divide by the maximum).
3. `final = alpha × bm25 + (1 − alpha) × semantic`, with `alpha` around 0.5. Tune it using your Stage 9 test set.

Another popular method is **Reciprocal Rank Fusion (RRF)**: combine the *rankings* rather than the scores. Look it up once hybrid works.

Because *you* built BM25 from scratch, you'll understand what each half contributes, which is rare and valuable.

### RAG: turning search into an AI assistant

**RAG (Retrieval-Augmented Generation)** is how AI assistants answer questions using *your* documents:

```
1. User asks a question.
2. RETRIEVE: your search engine finds the top few relevant passages.
3. AUGMENT: put those passages into a prompt: "Using only the text below, answer the question..."
4. GENERATE: a language model writes the answer.
```
**The search engine you built is step 2**, the "retrieval" half. The quality of the final AI answer depends heavily on retrieval quality, which is why building search well matters.

### Your AI roadmap from here

1. Split long documents into **chunks** (paragraphs) so results are precise.
2. Add embeddings and semantic scoring.
3. Combine into hybrid search and evaluate with your test set.
4. Add a language model to write answers from retrieved chunks (RAG).
5. Add sources/citations, so users can verify every answer.

---

# Appendix A — Debugging playbook

When your code doesn't work (it will, constantly, for everyone, forever), follow this routine:

1. **Read the error message from the bottom up.** What type of error? Which line?
2. **Print the variables** just before the failing line: `print(type(x), x)`.
3. **Shrink the input.** Test the function with the smallest example that still fails.
4. **Check your assumptions.** "Surely this list isn't empty." Print `len(...)`.
5. **Trace by hand on paper** with the three-document example. Compare to what the program printed.
6. **Comment out** recent code to find which change broke things (Git helps: `git diff`, `git stash`).
7. **Explain the code out loud** to a rubber duck (or a friend). You'll often spot it mid-sentence.
8. **Search the exact error message** in quotes, plus "python". Read Stack Overflow answers for *why*, not just the fix.
9. **Take a break.** A 10-minute walk solves an astonishing number of bugs.

**How to ask for help well** (in a forum or to an AI):

```
1. What I'm trying to do:
2. The code (a minimal version that still fails):
3. What I expected:
4. What actually happened (paste the full error):
5. What I've already tried:
```

---

# Appendix B — Python cheat sheet

```python
# --- basics ---
x = 5;  name = "Asha";  ok = True
print(f"{name} has {x}")
input("prompt: ")                       # returns a string
len(obj);  type(obj);  int("5");  str(5);  float("2.5")

# --- strings ---
s.lower()  s.upper()  s.strip()  s.split()  s.split(",")
" ".join(list_of_str)  s.replace(a, b)  s.startswith(a)  s.find(a)  a in s

# --- list ---
lst = [1, 2, 3];  lst.append(4);  lst[0];  lst[-1];  lst[1:3];  lst.sort()

# --- tuple ---
t = ("a", 1);  x, y = t

# --- dict ---
d = {"k": 1};  d["k"];  d["new"] = 2;  d.get("k", 0)
"k" in d;  d.keys();  d.values();  d.items()
for key, value in d.items(): ...

# --- set ---
s = {1, 2};  s.add(3);  a | b   a & b   a - b;  set()   # empty set

# --- control flow ---
if a: ...  elif b: ...  else: ...
for item in collection: ...
for i, item in enumerate(collection): ...
for i in range(5): ...
while condition: ...   break   continue

# --- functions ---
def name(param, other=default):
    """docstring"""
    return value

# --- files ---
with open("f.txt", "r", encoding="utf-8") as f:  text = f.read()
from pathlib import Path;  Path("data").glob("*.txt");  path.read_text(encoding="utf-8")

# --- errors ---
try: ...
except ValueError as e: ...

# --- sorting ---
sorted(items, key=lambda x: x[1], reverse=True)

# --- collections ---
from collections import Counter, defaultdict, deque
Counter(list_of_words);  defaultdict(int);  deque().popleft()

# --- json ---
import json;  json.dump(obj, f);  json.load(f)

# --- math ---
import math;  math.log(x);  math.sqrt(x)
```

**Terminal / Git**

```bash
python file.py          # run a script
pip install package     # install a package
pytest                  # run tests
git add . ; git commit -m "message"
```

---

# Appendix C — Glossary

| Term | Meaning |
|---|---|
| **Algorithm** | A step-by-step method for solving a problem |
| **AND / OR search** | All words must match / any word may match |
| **BM25** | A better version of TF-IDF used by real search engines |
| **Breadth-first search** | Visiting all neighbours before going deeper (used by crawler) |
| **Corpus** | Your whole collection of documents |
| **Cosine similarity** | Measure of how close in direction two vectors are |
| **Crawler / spider** | A program that fetches pages by following links |
| **Dictionary (dict)** | Python's key → value structure |
| **Document** | One searchable unit of text |
| **Embedding** | A list of numbers representing text meaning |
| **Frontier** | The queue of URLs waiting to be crawled |
| **Function** | Named, reusable block of code |
| **HTML** | The markup language web pages are written in |
| **HTTP** | The protocol browsers and servers use to communicate |
| **Hybrid search** | Combining keyword and semantic scores |
| **IDF** | Inverse Document Frequency: how rare a word is across documents |
| **Index (search)** | Data structure enabling fast lookup of documents by word |
| **Inverted index** | Maps each word → documents containing it |
| **JSON** | A text format for saving structured data |
| **Lemmatisation** | Reducing words to dictionary form using grammar (better → good) |
| **Module** | A Python file of reusable code you can import |
| **Normalisation** | Making text consistent (lowercase, no punctuation...) |
| **Pipeline** | A chain of steps, each feeding the next |
| **Posting / posting list** | A (document, count) entry / all entries for one word |
| **Precision** | Of the results returned, what fraction are relevant |
| **Query** | What the user types |
| **RAG** | Retrieval-Augmented Generation: search, then let an AI answer from the results |
| **Recall** | Of all relevant documents, what fraction were returned |
| **REPL** | Interactive Python prompt (`>>>`) |
| **robots.txt** | A site's rules for what bots may crawl |
| **Route** | A URL path connected to a function in a web app |
| **Seed URL** | The starting page of a crawl |
| **Semantic search** | Search by meaning rather than exact words |
| **Set** | Collection of unique, unordered items |
| **Snippet** | Short excerpt of text shown with a search result |
| **Stemming** | Chopping words to a root (running → run) |
| **Stop words** | Very common words (the, is, a...) usually ignored |
| **Template** | HTML with blanks that Python fills in |
| **TF** | Term Frequency: how often a word appears in a document |
| **TF-IDF** | TF × IDF: a classic relevance score |
| **Token / tokenisation** | One unit of text / splitting text into units |
| **Tuple** | Immutable (unchangeable) ordered group of values |
| **Unit test** | Small automated check of one behaviour |
| **URL** | A web address |
| **Vector** | A list of numbers |
| **Virtual environment** | Isolated set of packages for one project |

---

# Appendix D — Milestones and schedule

## Milestone checklist

- [ ] **M0** Python installed, venv works, Git initialised
- [ ] **M1** Crash-course mini-exercises done
- [ ] **M2** Stage 1: documents loaded into a dictionary
- [ ] **M3** Stage 2: `process()` works on 5+ test inputs
- [ ] **M4** Stage 3: inverted index matches your hand-traced version
- [ ] **M5** Stage 4: AND / OR search in the terminal 🎉
- [ ] **M6** Stage 5: TF-IDF ranking matches the worked example
- [ ] **M7** Stage 5 challenge: BM25 implemented
- [ ] **M8** Stage 6: crawler collects 20 pages politely
- [ ] **M9** Stage 7: index saved and reloaded
- [ ] **M10** Stage 8: web interface with snippets
- [ ] **M11** Stage 9: 10+ passing tests and precision/recall numbers
- [ ] **M12** Stage 10: cosine similarity written by hand, first semantic search
- [ ] **M13** Hybrid search + a tiny RAG demo

## Suggested pace

At about 1 hour a day. Don't rush. Understanding beats speed.

| Weeks | Focus |
|---|---|
| 1 to 2 | Setup + Python crash course (Chapters 2 to 4) |
| 3 | Stage 1 and Stage 2 |
| 4 | Stage 3 |
| 5 | Stage 4 |
| 6 to 7 | Stage 5 (TF-IDF, then BM25) |
| 8 to 9 | Stage 6 (crawler) |
| 10 | Stages 7 and 8 |
| 11 | Stage 9 |
| 12+ | Stage 10 and your AI project |

---

# Appendix E — Free resources

- **Official Python tutorial:** docs.python.org/3/tutorial (dense but authoritative)
- **Automate the Boring Stuff with Python** (free online): gentle, project-based
- **CS50P: Introduction to Programming with Python** (Harvard, free on YouTube/edX): use it to *learn a concept*, then build your own thing
- **Real Python** (realpython.com): clear articles on `dictionaries`, `pathlib`, `requests`, `Flask`
- **Introduction to Information Retrieval** (Manning, Raghavan & Schütze, free online): the classic textbook behind everything in Stages 3 to 5
- **Python Tutor** (pythontutor.com): visualises your code running line by line, great for understanding loops and dictionaries

---

## Final advice

You are not "just following a tutorial." You are building a real system and understanding every line. A basic search engine touches almost every fundamental skill: strings, dictionaries, sets, files, networking, sorting, maths, web apps, and testing. If you can build it and **explain every line out loud**, you'll be far ahead of someone who has watched fifty tutorials.

**Start with Chapter 3's mini-exercises, then Stage 1 today.** Load a folder of text files into a dictionary. That's the whole first goal. Then take the next step, and the next.

You've got this. 🚀
