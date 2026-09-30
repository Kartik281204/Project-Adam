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
