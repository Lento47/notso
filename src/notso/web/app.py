"""Lightweight web UI for the Notso search engine."""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from string import Template
from typing import Iterable, List
from urllib.parse import parse_qs, urlparse

from ..engine import SearchIndex, SearchResult, build_index, load_index, search
from ..sample_docs import SAMPLE_DOCUMENTS


DEFAULT_INDEX_PATH = Path("data/index.json")


@dataclass
class SearchWebApp:
    """Holds state for serving the Notso web UI."""

    index: SearchIndex
    template_dir: Path = field(
        default_factory=lambda: Path(__file__).resolve().parent / "templates"
    )

    def render_template(self, name: str, **context: str) -> str:
        template_path = self.template_dir / name
        template = Template(template_path.read_text(encoding="utf-8"))
        return template.safe_substitute(context)

    def render_home(self, query: str = "") -> str:
        return self.render_template(
            "home.html",
            query=escape(query),
        )

    def render_results(self, query: str, results: Iterable[SearchResult]) -> str:
        items: List[str] = []
        for result in results:
            items.append(
                "<li>"
                f"<div class=\"result-title\">{escape(result.doc_id)}</div>"
                f"<div class=\"result-score\">Score: {result.score:.4f}</div>"
                f"<div class=\"result-text\">{escape(result.text)}</div>"
                "</li>"
            )
        results_html = "\n".join(items) if items else "<li>No results found.</li>"
        return self.render_template(
            "results.html",
            query=escape(query),
            results_html=results_html,
        )

    def handle_get(self, handler: BaseHTTPRequestHandler) -> None:
        parsed = urlparse(handler.path)
        if parsed.path == "/":
            content = self.render_home()
            self._send_html(handler, content)
            return
        if parsed.path == "/search":
            params = parse_qs(parsed.query)
            query = params.get("q", [""])[0]
            results = search(self.index, query, top_k=10) if query else []
            content = self.render_results(query, results)
            self._send_html(handler, content)
            return
        handler.send_response(404)
        handler.send_header("Content-Type", "text/plain; charset=utf-8")
        handler.end_headers()
        handler.wfile.write(b"Not Found")

    @staticmethod
    def _send_html(handler: BaseHTTPRequestHandler, content: str) -> None:
        body = content.encode("utf-8")
        handler.send_response(200)
        handler.send_header("Content-Type", "text/html; charset=utf-8")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        handler.wfile.write(body)


def load_or_build_index(index_path: Path) -> SearchIndex:
    """Load an index from disk or build one from sample docs."""

    if index_path.exists():
        return load_index(index_path)
    return build_index(SAMPLE_DOCUMENTS)


def create_handler(app: SearchWebApp) -> type[BaseHTTPRequestHandler]:
    """Create a request handler bound to a SearchWebApp."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
            app.handle_get(self)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A003
            return

    return Handler


def run(host: str = "127.0.0.1", port: int = 8080, index_path: Path | None = None) -> None:
    """Run the Notso web server."""

    resolved_index = index_path or DEFAULT_INDEX_PATH
    template_dir = Path(__file__).resolve().parent / "templates"
    app = SearchWebApp(load_or_build_index(resolved_index), template_dir)
    server = HTTPServer((host, port), create_handler(app))
    print(f"Notso web UI running at http://{host}:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
