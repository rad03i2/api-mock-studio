from __future__ import annotations

import argparse
import logging
import sys

from .core import ConfigError, load_routes
from .server import serve

VERSION = "1.0.0"
AUTHOR = "Radwan Abdulhadi Ahmed / @rad03i2"


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="api-mock-studio", description="Run a local HTTP mock API from JSON routes.")
    p.add_argument("config", help="Path to JSON route configuration")
    p.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--cors", action="store_true", help="Enable permissive CORS for local development")
    p.add_argument("--check", action="store_true", help="Validate config and exit")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION} — {AUTHOR}")
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    if not 1 <= args.port <= 65535:
        print("error: port must be 1..65535", file=sys.stderr)
        return 2
    try:
        routes = load_routes(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.check:
        print(f"Valid configuration: {len(routes)} route(s)")
        return 0
    logging.basicConfig(level=logging.WARNING if args.quiet else logging.INFO, format="%(levelname)s %(message)s")
    serve(routes, args.host, args.port, args.cors)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
