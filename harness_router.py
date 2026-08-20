"""MAHI Harness Router — lightweight UHP-compatible server for routing tasks to agents."""

import os
import sys
import json
import time
import uuid
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

MAHI_ROOT = Path(__file__).parent.parent
UHP_VERSION = "2026-08-11"

# Harness registry — maps harness IDs to agent configs
HARNESSES = {
    "mahi-code": {
        "id": "mahi-code",
        "name": "MAHI Code Agent",
        "description": "Code generation, review, debugging",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["code", "review", "debug", "refactor"],
    },
    "mahi-research": {
        "id": "mahi-research",
        "name": "MAHI Research Agent",
        "description": "Web research, analysis, summarization",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["research", "analysis", "search"],
    },
    "mahi-writing": {
        "id": "mahi-writing",
        "name": "MAHI Writing Agent",
        "description": "Content creation, editing, documentation",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["writing", "editing", "docs"],
    },
    "mahi-quick": {
        "id": "mahi-quick",
        "name": "MAHI Quick Agent",
        "description": "Fast responses for simple tasks",
        "backend": "groq",
        "model": "llama-3.3-70b-versatile",
        "capabilities": ["quick", "simple", "chat"],
    },
}

# Session storage
SESSIONS = {}

def generate_id():
    return str(uuid.uuid4())[:8]

def call_openrouter(model, messages, api_key):
    """Call OpenRouter API."""
    import urllib.request
    data = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def call_groq(model, messages, api_key):
    """Call Groq API."""
    import urllib.request
    data = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def run_harness(harness_id, task, session_id=None):
    """Run a task on a harness and return the result."""
    harness = HARNESSES.get(harness_id)
    if not harness:
        return {"error": f"Unknown harness: {harness_id}"}

    # Get or create session
    if not session_id:
        session_id = generate_id()
        SESSIONS[session_id] = {
            "harness": harness_id,
            "created": time.time(),
            "messages": [],
        }

    session = SESSIONS[session_id]
    session["messages"].append({"role": "user", "content": task})

    # Build context
    system_prompt = f"You are {harness['name']}. {harness['description']}. Respond concisely and helpfully."
    messages = [{"role": "system", "content": system_prompt}] + session["messages"]

    # Route to backend
    api_key = os.environ.get(f"{harness['backend'].upper()}_API_KEY", "")
    if not api_key:
        return {"error": f"No API key for {harness['backend']}"}

    if harness["backend"] == "openrouter":
        response = call_openrouter(harness["model"], messages, api_key)
    elif harness["backend"] == "groq":
        response = call_groq(harness["model"], messages, api_key)
    else:
        return {"error": f"Unknown backend: {harness['backend']}"}

    session["messages"].append({"role": "assistant", "content": response})

    return {
        "session_id": session_id,
        "harness": harness_id,
        "response": response,
        "model": harness["model"],
    }


class UHPHandler(BaseHTTPRequestHandler):
    """HTTP handler implementing UHP protocol."""

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("UHP-Version", UHP_VERSION)
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Protocol discovery
        if path == "/v1/uhp":
            self._send_json({
                "version": UHP_VERSION,
                "conformance": "core",
                "harnesses": f"{self.headers.get('Host', 'localhost')}/v1/harnesses",
            })

        # List harnesses
        elif path == "/v1/harnesses":
            self._send_json({"harnesses": list(HARNESSES.values())})

        # Get session
        elif path.startswith("/v1/sessions/"):
            sid = path.split("/")[-1]
            session = SESSIONS.get(sid)
            if session:
                self._send_json(session)
            else:
                self._send_json({"error": "Session not found"}, 404)

        # Health check
        elif path == "/health":
            self._send_json({"status": "ok", "harnesses": len(HARNESSES)})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        # Run task
        if path == "/v1/tasks":
            harness_id = body.get("harness", "mahi-quick")
            task = body.get("task", "")
            session_id = body.get("session_id")

            if not task:
                self._send_json({"error": "No task provided"}, 400)
                return

            result = run_harness(harness_id, task, session_id)
            self._send_json(result)

        # Create session
        elif path == "/v1/sessions":
            harness_id = body.get("harness", "mahi-quick")
            session_id = generate_id()
            SESSIONS[session_id] = {
                "harness": harness_id,
                "created": time.time(),
                "messages": [],
            }
            self._send_json({"session_id": session_id, "harness": harness_id})

        else:
            self._send_json({"error": "Not found"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8600
    server = HTTPServer(("127.0.0.1", port), UHPHandler)
    print(f"MAHI Harness Router running on http://127.0.0.1:{port}")
    print(f"UHP discovery: http://127.0.0.1:{port}/v1/uhp")
    print(f"Harnesses: http://127.0.0.1:{port}/v1/harnesses")
    print(f"Tasks: POST http://127.0.0.1:{port}/v1/tasks")
    print()
    print("Harnesses available:")
    for h in HARNESSES.values():
        print(f"  {h['id']}: {h['name']} ({h['backend']}/{h['model']})")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
