#!/usr/bin/env python3
"""
MAHI PDF Tools — HTTP micro-service for PDF extraction and summarization.

Usage:
    python pdf_tools_api.py serve [--port 8300]
    python pdf_tools_api.py extract <file.pdf>
    python pdf_tools_api.py summarize <file.pdf>
    python pdf_tools_api.py status

Endpoints:
    GET  /                          API help
    GET  /extract?path=<file.pdf>   Extract text + metadata from PDF
    GET  /summarize?path=<file.pdf> Summarize PDF (first 300 chars)
    GET  /status                    Service status
    POST /extract                   Body: {"path": "/path/to/file.pdf"}
    POST /summarize                 Body: {"path": "/path/to/file.pdf"}

Works with PyPDF2, PyMuPDF (fitz), or the bundled pdf-tools extractor.
"""
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

MAHI_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MAHI_ROOT)

from tools.registry import ToolRegistry

_stats = {"extracts": 0, "summarizes": 0, "errors": 0, "start_time": time.time()}
_registry = ToolRegistry()


def extract_pdf(pdf_path: str) -> dict:
    """Extract text and metadata from a PDF."""
    _stats["extracts"] += 1
    try:
        result = _registry.pdf_extract(pdf_path)
        return result
    except Exception as e:
        _stats["errors"] += 1
        return {"success": False, "error": str(e)}


def summarize_pdf(pdf_path: str) -> dict:
    """Summarize a PDF."""
    _stats["summarizes"] += 1
    try:
        result = _registry.pdf_summarize(pdf_path)
        return result
    except Exception as e:
        _stats["errors"] += 1
        return {"success": False, "error": str(e)}


def get_status() -> dict:
    """Get service status."""
    # Check which PDF libraries are available
    libs = {}
    try:
        import PyPDF2
        libs["PyPDF2"] = PyPDF2.__version__
    except ImportError:
        libs["PyPDF2"] = None

    try:
        import fitz
        libs["PyMuPDF"] = fitz.version
    except ImportError:
        libs["PyMuPDF"] = None

    try:
        from tools.pdf_tools.src.extract.pdf_extractor import extract_text
        libs["pdf_tools_extractor"] = True
    except ImportError:
        libs["pdf_tools_extractor"] = False

    return {
        "service": "MAHI PDF Tools",
        "version": "1.0.0",
        "available_libraries": libs,
        "stats": {
            "extracts": _stats["extracts"],
            "summarizes": _stats["summarizes"],
            "errors": _stats["errors"],
            "uptime_seconds": int(time.time() - _stats["start_time"]),
        },
    }


class PDFToolsHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

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
                "service": "MAHI PDF Tools API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /extract?path=<file.pdf>": "Extract text + metadata from PDF",
                    "GET /summarize?path=<file.pdf>": "Summarize PDF (first 300 chars)",
                    "GET /status": "Service status + available libraries",
                }
            })
        elif path == "/extract":
            pdf_path = params.get("path", [""])[0]
            if not pdf_path:
                self._send(400, {"error": "Missing path parameter ?path=/file.pdf"})
                return
            if not os.path.isfile(pdf_path):
                self._send(400, {"error": f"File not found: {pdf_path}"})
                return
            result = extract_pdf(pdf_path)
            self._send(200, result)
        elif path == "/summarize":
            pdf_path = params.get("path", [""])[0]
            if not pdf_path:
                self._send(400, {"error": "Missing path parameter ?path=/file.pdf"})
                return
            if not os.path.isfile(pdf_path):
                self._send(400, {"error": f"File not found: {pdf_path}"})
                return
            result = summarize_pdf(pdf_path)
            self._send(200, result)
        elif path == "/status":
            self._send(200, get_status())
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/extract", "/summarize"):
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                pdf_path = data.get("path", "")
                if not pdf_path:
                    self._send(400, {"error": "Missing 'path' in request body"})
                    return
                if not os.path.isfile(pdf_path):
                    self._send(400, {"error": f"File not found: {pdf_path}"})
                    return
                if path == "/extract":
                    result = extract_pdf(pdf_path)
                else:
                    result = summarize_pdf(pdf_path)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "Not found"})


def serve(port: int = 8300):
    """Start the PDF tools API server."""
    server = ThreadingHTTPServer(("127.0.0.1", port), PDFToolsHandler)
    print(f"\n  MAHI PDF Tools API")
    print(f"  Listening:  http://127.0.0.1:{port}")
    print(f"  Endpoints:  GET /extract?path=..., GET /summarize?path=..., GET /status")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  PDF Tools API stopped.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "extract":
        if len(sys.argv) < 3:
            print("Usage: python pdf_tools_api.py extract <file.pdf>")
            return
        pdf_path = sys.argv[2]
        result = extract_pdf(pdf_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "summarize":
        if len(sys.argv) < 3:
            print("Usage: python pdf_tools_api.py summarize <file.pdf>")
            return
        pdf_path = sys.argv[2]
        result = summarize_pdf(pdf_path)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "status":
        result = get_status()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif cmd == "serve":
        port = 8300
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            port = int(sys.argv[idx + 1])
        serve(port)

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: extract, summarize, status, serve")


if __name__ == "__main__":
    main()
