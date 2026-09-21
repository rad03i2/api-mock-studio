from __future__ import annotations

import json
import logging
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from .core import Route, find_route, render

LOG = logging.getLogger("api-mock-studio")
MAX_BODY = 1_048_576


def make_handler(routes: list[Route], cors: bool = False):
    class Handler(BaseHTTPRequestHandler):
        server_version = "ApiMockStudio/1.0"

        def _send(self, status: int, body, headers: dict[str, str] | None = None):
            payload = b"" if self.command == "HEAD" else json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("X-Content-Type-Options", "nosniff")
            if cors:
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
                self.send_header("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,HEAD,OPTIONS")
            for key, value in (headers or {}).items():
                if key.lower() not in {"content-length", "connection"}:
                    self.send_header(key, value)
            self.end_headers()
            if payload:
                self.wfile.write(payload)

        def _handle(self):
            parsed = urlsplit(self.path)
            route, params = find_route(routes, self.command, parsed.path)
            if route is None:
                self._send(404, {"error": "route_not_found", "method": self.command, "path": parsed.path})
                return
            length = int(self.headers.get("Content-Length", "0") or 0)
            if length > MAX_BODY:
                self._send(413, {"error": "request_body_too_large"})
                return
            raw = self.rfile.read(length) if length else b""
            request_body = None
            if raw:
                try:
                    request_body = json.loads(raw)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    request_body = raw.decode("utf-8", errors="replace")
            if route.delay_ms:
                time.sleep(route.delay_ms / 1000)
            body = render(route.body, params)
            if isinstance(body, dict) and body.get("$echo") is True:
                body = {"method": self.command, "path": parsed.path, "params": params,
                        "query": parse_qs(parsed.query), "body": request_body}
            self._send(route.status, body, route.headers)

        do_GET = _handle
        do_POST = _handle
        do_PUT = _handle
        do_PATCH = _handle
        do_DELETE = _handle
        do_HEAD = _handle

        def do_OPTIONS(self):
            self._send(204, None)

        def log_message(self, fmt, *args):
            LOG.info("%s - %s", self.address_string(), fmt % args)

    return Handler


def serve(routes: list[Route], host: str, port: int, cors: bool = False):
    server = ThreadingHTTPServer((host, port), make_handler(routes, cors))
    LOG.info("Listening on http://%s:%s with %d routes", host, port, len(routes))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
