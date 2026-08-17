#!/usr/bin/env python3
"""
MAHI Agents — CLI and HTTP API interface.

Usage:
    python agents_cli.py list                     # List all agents with tools
    python agents_cli.py run <agent> "<task>"     # Run a task with an agent
    python agents_cli.py serve [--port 8100]      # Start HTTP API server
    python agents_cli.py status                   # Show agent system status

Examples:
    python agents_cli.py run research "search the web for AI trends 2026"
    python agents_cli.py run code "find file main.py in the project"
    python agents_cli.py run teaching "summarize this pdf document.pdf"
    python agents_cli.py serve --port 8100
"""
import json
import os
import sys
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

MAHI_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MAHI_ROOT)

from agents.base import Task, TaskState
from tools.registry import ToolRegistry

# Agent registry — maps agent IDs to their factory functions
AGENT_FACTORIES = {}

def _register_agents():
    """Lazy-load agent factories to avoid circular imports."""
    global AGENT_FACTORIES
    if AGENT_FACTORIES:
        return
    try:
        from agents.research_agent import create_research_agent
        from agents.code_agent import create_code_agent, create_code_pro_agent
        from agents.writing_agent import create_writing_agent
        from agents.teaching_agent import create_teaching_agent
        from agents.career_agent import create_career_agent
        from agents.spiritual_agent import create_spiritual_agent
        from agents.dss_agent import create_dss_agent
        from agents.quick_agent import create_quick_agent

        AGENT_FACTORIES = {
            "research": create_research_agent,
            "code": create_code_agent,
            "code-pro": create_code_pro_agent,
            "writing": create_writing_agent,
            "teaching": create_teaching_agent,
            "career": create_career_agent,
            "spiritual": create_spiritual_agent,
            "dss": create_dss_agent,
            "quick": create_quick_agent,
        }
    except ImportError as e:
        print(f"Warning: Some agents could not be loaded: {e}", file=sys.stderr)


def list_agents():
    """List all available agents with their tools."""
    _register_agents()
    reg = ToolRegistry()
    agents = []
    for aid, factory in AGENT_FACTORIES.items():
        try:
            agent = factory()
            agents.append({
                "id": agent.id,
                "name": agent.name,
                "model": agent.config.model_primary,
                "tools": agent.config.tools,
                "capabilities": agent.config.capabilities,
                "description": agent.config.description,
            })
        except Exception as e:
            agents.append({"id": aid, "error": str(e)})
    return agents


def run_task(agent_id: str, task_text: str) -> dict:
    """Run a task with the specified agent."""
    _register_agents()
    factory = AGENT_FACTORIES.get(agent_id)
    if not factory:
        return {"error": f"Unknown agent: {agent_id}. Available: {', '.join(AGENT_FACTORIES.keys())}"}

    agent = factory()
    task = Task(user_input=task_text)
    result = agent.run(task)

    return {
        "agent": agent_id,
        "task_id": result.id,
        "state": result.state.value,
        "result": result.result,
        "error": result.error,
        "elapsed": result.elapsed,
        "tools_used": agent.config.tools,
    }


def get_status() -> dict:
    """Get overall agent system status."""
    _register_agents()
    reg = ToolRegistry()
    agents = []
    for aid, factory in AGENT_FACTORIES.items():
        try:
            agent = factory()
            agents.append(agent.get_status())
        except Exception as e:
            agents.append({"id": aid, "error": str(e)})

    return {
        "agents": agents,
        "tools": {
            "file_search": True,
            "pdf_extract": True,
            "pdf_summarize": True,
            "web_search": True,
        },
        "total_agents": len(agents),
    }


# === HTTP API Server ===

class AgentAPIHandler(BaseHTTPRequestHandler):
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
        path = urlparse(self.path).path
        if path == "/":
            self._send(200, {
                "service": "MAHI Agents API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /": "This help",
                    "GET /agents": "List all agents",
                    "GET /status": "System status",
                    "POST /run": "Run a task (body: {agent, task})",
                }
            })
        elif path == "/agents":
            self._send(200, list_agents())
        elif path == "/status":
            self._send(200, get_status())
        else:
            self._send(404, {"error": "Not found"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/run":
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length)) if length else {}
                agent_id = data.get("agent", "")
                task_text = data.get("task", "")
                if not agent_id or not task_text:
                    self._send(400, {"error": "Missing 'agent' or 'task' in request body"})
                    return
                result = run_task(agent_id, task_text)
                self._send(200, result)
            except Exception as e:
                self._send(500, {"error": str(e)})
        else:
            self._send(404, {"error": "Not found"})


def serve(port: int = 8100):
    """Start the agents HTTP API server."""
    _register_agents()
    server = ThreadingHTTPServer(("127.0.0.1", port), AgentAPIHandler)
    print(f"\n  MAHI Agents API")
    print(f"  Listening:  http://127.0.0.1:{port}")
    print(f"  Agents:     {', '.join(AGENT_FACTORIES.keys())}")
    print(f"  Endpoints:  GET /agents, GET /status, POST /run")
    print(f"  Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Agents API stopped.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "list":
        agents = list_agents()
        print(json.dumps(agents, indent=2, ensure_ascii=False))

    elif cmd == "run":
        if len(sys.argv) < 4:
            print("Usage: python agents_cli.py run <agent> \"<task>\"")
            print("Agents: research, code, code-pro, writing, teaching, career, spiritual, dss, quick")
            return
        agent_id = sys.argv[2]
        task_text = sys.argv[3]
        result = run_task(agent_id, task_text)
        if result.get("error"):
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"\n{'='*60}")
        print(f"Agent:   {result['agent']}")
        print(f"Task:    {result['task_id']}")
        print(f"State:   {result['state']}")
        print(f"Elapsed: {result['elapsed']}s")
        print(f"Tools:   {', '.join(result['tools_used'])}")
        print(f"{'='*60}\n")
        print(result.get("result", "(no result)"))

    elif cmd == "status":
        status = get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif cmd == "serve":
        port = 8100
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            port = int(sys.argv[idx + 1])
        serve(port)

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: list, run, status, serve")


if __name__ == "__main__":
    main()
