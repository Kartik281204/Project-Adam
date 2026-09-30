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
