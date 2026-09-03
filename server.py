#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from fathom.analyze import analyze_feedback
from fathom.demo import demo_corpus, request_sample, priority_sample
from fathom.backlog import import_backlog
from fathom.primitive import find_primitives
from fathom.prioritize import prioritize

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/sample":
            sample = demo_corpus()
            return self._json({"items": sample, "count": len(sample)})
        if path == "/api/sample-requests":
            sample = request_sample()
            return self._json({"items": sample, "count": len(sample)})
        if path == "/api/sample-priority":
            sample = priority_sample()
            return self._json(sample)
        if path in {"/", "/index.html"}:
            return super().do_GET()
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path not in {"/api/analyze", "/api/primitive", "/api/backlog", "/api/prioritize"}:
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return self._json({"error": "Invalid JSON"}, 400)
        if path == "/api/backlog":
            try:
                return self._json(import_backlog(body))
            except RuntimeError as err:
                return self._json({"error": str(err)}, 400)
        if path == "/api/prioritize":
            try:
                if body.get("useSample"):
                    return self._json(prioritize(priority_sample()))
                return self._json(prioritize(body))
            except RuntimeError as err:
                return self._json({"error": str(err)}, 400)
        if path == "/api/primitive":
            if body.get("useSample"):
                result = find_primitives(request_sample())
            elif body.get("items"):
                result = find_primitives(body["items"])
            else:
                result = find_primitives(body.get("text") or "")
            return self._json(result)
        if body.get("useSample"):
            result = analyze_feedback(demo_corpus())
        elif body.get("items"):
            result = analyze_feedback(body["items"])
        else:
            result = analyze_feedback(body.get("text") or "")
        return self._json(result)

    def _json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Server(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> None:
    # Local default: localhost:3335. Hosted platforms set PORT and need 0.0.0.0.
    host = os.environ.get("HOST", "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1")
    port = int(os.environ.get("PORT", "3335"))
    server = Server((host, port), Handler)
    print(f"POP running at http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
