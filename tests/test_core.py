import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from http.server import ThreadingHTTPServer

from api_mock_studio.core import ConfigError, Route, find_route, load_routes, render
from api_mock_studio.server import make_handler

class CoreTests(unittest.TestCase):
    def test_dynamic_route_and_render(self):
        r = Route("GET", "/users/:id", 200, {}, {"id": "{{params.id}}"})
        route, params = find_route([r], "GET", "/users/42")
        self.assertIs(route, r)
        self.assertEqual(render(route.body, params), {"id": "42"})

    def test_method_matters(self):
        r = Route("POST", "/items", 201, {}, None)
        self.assertIsNone(find_route([r], "GET", "/items")[0])

    def test_reject_duplicate_routes(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "api.json"
            p.write_text(json.dumps({"routes": [{"path":"/x"},{"path":"/x"}]}), encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_routes(p)

    def test_reject_bad_status(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "api.json"
            p.write_text(json.dumps({"routes": [{"path":"/x", "status":999}]}), encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_routes(p)

class HttpTests(unittest.TestCase):
    def test_echo_endpoint(self):
        routes = [Route("POST", "/echo/:id", 201, {}, {"$echo": True})]
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(routes))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            conn.request("POST", "/echo/7?q=yes", body='{"hello":"world"}', headers={"Content-Type":"application/json"})
            response = conn.getresponse()
            body = json.loads(response.read())
            self.assertEqual(response.status, 201)
            self.assertEqual(body["params"], {"id":"7"})
            self.assertEqual(body["query"], {"q":["yes"]})
            self.assertEqual(body["body"], {"hello":"world"})
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

    def test_not_found(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler([]))
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            conn.request("GET", "/missing")
            self.assertEqual(conn.getresponse().status, 404)
        finally:
            server.shutdown(); server.server_close(); thread.join(timeout=2)

if __name__ == "__main__":
    unittest.main()
