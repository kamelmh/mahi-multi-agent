#!/usr/bin/env python3
"""
MAHI Web Search — HTTP API for keyless web search via Hound.

Usage:
    python web_search_api.py serve [--port 8200]
    python web_search_api.py search "query"
    python web_search_api.py fetch "https://example.com"
    python web_search_api.py status

Endpoints:
    GET  /                     API help
    GET  /search?q=<query>     Web search (returns JSON)
    GET  /fetch?url=<url>      Fetch URL content (returns JSON)
    GET  /status               Hound availability + stats
    POST /search               Body: {"query": "...", "max_results": 6}

Zero API keys required — uses Hound's multi-backend search.
"""
import json
import os
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

MAHI_ROOT = os.path.dirname(os.path.abspath(__file__))
HOUND_PY = os.path.join(MAHI_ROOT, "mcp-hound.py")
PYTHON = sys.executable

# Stats tracking
_stats = {"searches": 0, "fetches": 0, "errors": 0, "start_time": time.time()}


def hound_search(query: str, max_results: int = 6) -> dict:
    """Run a hound search via mcp-hound.py CLI."""
    _stats["searches"] += 1
    try:
        result = subprocess.run(
            [PYTHON, HOUND_PY, "search", query],
            capture_output=True, text=True, timeout=30,
            cwd=MAHI_ROOT, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            _stats["errors"] += 1
            return {"error": f"Hound search failed: {result.stderr[:500]}", "query": query}
        # Parse JSON output
        output = result.stdout.strip()
        if not output:
            return {"error": "No output from hound", "query": query}
        data = json.loads(output)
        # Limit results
        if "results" in data:
            data["results"] = data["results"][:max_results]
        return data
    except subprocess.TimeoutExpired:
        _stats["errors"] += 1
        return {"error": "Search timed out (30s)", "query": query}
    except json.JSONDecodeError as e:
        _stats["errors"] += 1
        return {"error": f"Failed to parse hound output: {e}", "query": query}
    except Exception as e:
        _stats["errors"] += 1
        return {"error": str(e), "query": query}


def hound_fetch(url: str) -> dict:
    """Fetch a URL via hound."""
    _stats["fetches"] += 1
    try:
        result = subprocess.run(
            [PYTHON, HOUND_PY, "fetch", url],
            capture_output=True, text=True, timeout=30,
            cwd=MAHI_ROOT, encoding="utf-8", errors="replace"
        )
        if result.returncode != 0:
            _stats["errors"] += 1
            return {"error": f"Hound fetch failed: {result.stderr[:500]}", "url": url}
        output = result.stdout.strip()
        if not output:
            return {"error": "No output from hound", "url": url}
        return json.loads(output)
    except subprocess.TimeoutExpired:
        _stats["errors"] += 1
        return {"error": "Fetch timed out (30s)", "url": url}
    except json.JSONDecodeError:
        # Return raw text if not JSON
        return {"content": output, "url": url, "format": "text"}
    except Exception as e:
        _stats["errors"] += 1
        return {"error": str(e), "url": url}


def hound_status() -> dict:
    """Check hound availability."""
    try:
        result = subprocess.run(
            [PYTHON, HOUND_PY, "version"],
            capture_output=True, text=True, timeout=10,
            cwd=MAHI_ROOT, encoding="utf-8", errors="replace"
        )
        version = result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        version = "unknown"

    return {
        "available": True,
        "version": version,
        "stats": {
            "searches": _stats["searches"],
            "fetches": _stats["fetches"],
            "errors": _stats["errors"],
            "uptime_seconds": int(time.time() - _stats["start_time"]),
        },
        "backends": ["duckduckgo", "brave", "mojeek", "yahoo", "yandex", "startpage", "google", "qwant"],
    }


class WebSearchHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # Suppress default logging

    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body, ensure_ascii=False, indent=2).encode("utf-8")
        elif isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        if path == "/":
            self._send(200, {
                "service": "MAHI Web Search API",
                "version": "1.0.0",
                "backends": 8,
                "api_key_required": False,
                "endpoints": {
                    "GET /search?q=<query>": "Web search (JSON results)",
                    "GET /fetch?url=<url>": "Fetch URL content",
                    "GET /status": "Hound availability + stats",
                }
            })
        elif path == "/search":
            query = params.get("q", params.get("query", [""]))[0]
            max_results = int(params.get("max_results", ["6"])[0])
            if not query:
                self._send(400, {"error": "Missing query parameter ?q=..."})
                return
            result = hound_search(query, max_results)
            self._send(200, result)
        elif path == "/fetch":
            url = params.get("url", [""])[0]
            if not url:
                self._send(400, {"error": "Missing url parameter ?url=..."})
                return
            result = hound_fetch(url)
            self._send(200, result)
        elif path == "/status":
            self._send(200, hound_status())
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/search":
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                query = data.get("query", "")
                max_results = data.get("max_results", 6)
                if not query:
                    self._send(400, {"error": "Missing 'query' in request body"})
                    return
                result = hound_search(query, max_results)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "Not found"})


def serve(port: int = 8200):
    """Start the web search API server."""
    server = ThreadingHTTPServer(("127.0.0.1", port), WebSearchHandler)
    print(f"\n  MAHI Web Search API")
    print(f"  Listening:  http://127.0.0.1:{port}")
    print(f"  Backends:   8 search engines (zero API keys)")
    print(f"  Endpoints:  GET /search?q=..., GET /fetch?url=..., GET /status")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Web Search API stopped.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: python web_search_api.py search \"query\"")
            return
        query = " ".join(sys.argv[2:])
        result = hound_search(query)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "fetch":
        if len(sys.argv) < 3:
            print("Usage: python web_search_api.py fetch \"https://example.com\"")
            return
        url = sys.argv[2]
        result = hound_fetch(url)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "status":
        result = hound_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "serve":
        port = 8200
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            port = int(sys.argv[idx + 1])
        serve(port)

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: search, fetch, status, serve")


if __name__ == "__main__":
    main()
