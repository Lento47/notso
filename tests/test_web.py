"""Tests for the Notso web UI."""
from __future__ import annotations

import http.client
import threading
from http.server import HTTPServer

from notso.engine import build_index
from notso.sample_docs import SAMPLE_DOCUMENTS
from notso.web.app import SearchWebApp, create_handler


def _start_server(app: SearchWebApp) -> tuple[HTTPServer, threading.Thread]:
    server = HTTPServer(("127.0.0.1", 0), create_handler(app))
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server, thread


def _request(path: str, port: int) -> tuple[int, str]:
    connection = http.client.HTTPConnection("127.0.0.1", port)
    connection.request("GET", path)
    response = connection.getresponse()
    body = response.read().decode("utf-8")
    connection.close()
    return response.status, body


def test_home_page_renders_form() -> None:
    index = build_index(SAMPLE_DOCUMENTS)
    app = SearchWebApp(index)
    server, thread = _start_server(app)
    try:
        status, body = _request("/", server.server_port)
    finally:
        server.shutdown()
        thread.join()
    assert status == 200
    assert "<form" in body
    assert "Notso Search" in body


def test_search_page_renders_results() -> None:
    index = build_index(SAMPLE_DOCUMENTS)
    app = SearchWebApp(index)
    server, thread = _start_server(app)
    try:
        status, body = _request("/search?q=python", server.server_port)
    finally:
        server.shutdown()
        thread.join()
    assert status == 200
    assert "Results" in body
    assert "python" in body.lower()
