from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}

class ConfigError(ValueError):
    pass

@dataclass(frozen=True)
class Route:
    method: str
    path: str
    status: int
    headers: dict[str, str]
    body: Any
    delay_ms: int = 0

    def match(self, method: str, path: str) -> dict[str, str] | None:
        if self.method != method.upper():
            return None
        names: list[str] = []
        parts = []
        for part in self.path.strip("/").split("/") if self.path != "/" else []:
            if part.startswith(":") and len(part) > 1:
                names.append(part[1:])
                parts.append(r"([^/]+)")
            else:
                parts.append(re.escape(part))
        pattern = r"^/" + "/".join(parts) + r"/?$" if parts else r"^/?$"
        found = re.match(pattern, path)
        return dict(zip(names, found.groups())) if found else None


def _route(raw: Any, index: int) -> Route:
    if not isinstance(raw, dict):
        raise ConfigError(f"routes[{index}] must be an object")
    method = str(raw.get("method", "GET")).upper()
    path = raw.get("path")
    status = raw.get("status", 200)
    delay = raw.get("delay_ms", 0)
    headers = raw.get("headers", {})
    if method not in METHODS:
        raise ConfigError(f"routes[{index}].method is unsupported")
    if not isinstance(path, str) or not path.startswith("/") or "?" in path:
        raise ConfigError(f"routes[{index}].path must start with / and exclude query strings")
    if not isinstance(status, int) or not 100 <= status <= 599:
        raise ConfigError(f"routes[{index}].status must be 100..599")
    if not isinstance(delay, int) or not 0 <= delay <= 30_000:
        raise ConfigError(f"routes[{index}].delay_ms must be 0..30000")
    if not isinstance(headers, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in headers.items()):
        raise ConfigError(f"routes[{index}].headers must contain string keys and values")
    return Route(method, path, status, headers, raw.get("body"), delay)


def load_routes(path: str | Path) -> list[Route]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Cannot load config: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("routes"), list):
        raise ConfigError("config must be an object containing a routes array")
    routes = [_route(item, i) for i, item in enumerate(data["routes"])]
    seen = set()
    for route in routes:
        key = (route.method, route.path)
        if key in seen:
            raise ConfigError(f"duplicate route: {route.method} {route.path}")
        seen.add(key)
    return routes


def find_route(routes: list[Route], method: str, path: str) -> tuple[Route | None, dict[str, str]]:
    for route in routes:
        params = route.match(method, path)
        if params is not None:
            return route, params
    return None, {}


def render(value: Any, params: dict[str, str]) -> Any:
    if isinstance(value, str):
        for key, val in params.items():
            value = value.replace("{{params." + key + "}}", val)
        return value
    if isinstance(value, list):
        return [render(v, params) for v in value]
    if isinstance(value, dict):
        return {k: render(v, params) for k, v in value.items()}
    return value
