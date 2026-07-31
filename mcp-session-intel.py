"""
Session Intelligence MCP Server for OpenCode
Provides session analytics and pattern detection.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, r"C:\Users\Admin\automation\session-intelligence")

from agent import SessionIntelligence

si = SessionIntelligence()


def analyze_patterns() -> dict:
    """Analyze session patterns."""
    state = si.load_session_state()
    sessions = si.load_session_archive()
    analysis = si.analyze_patterns()
    return {
        "timestamp": datetime.now().isoformat(),
        "session_state_loaded": bool(state),
        "archived_sessions": len(sessions),
        "analysis": analysis,
    }


def get_recommendations() -> list:
    """Get recommendations based on patterns."""
    return si.generate_recommendations()


def get_session_state() -> dict:
    """Get current session state."""
    return si.load_session_state()


# MCP Protocol Handler
def handle_request(request: dict) -> dict:
    """Handle MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "session-intelligence", "version": "1.0.0"},
            },
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "session_analyze",
                        "description": "Analyze session patterns and detect trends",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "session_recommendations",
                        "description": "Get recommendations based on session history",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "session_state",
                        "description": "Get current session state",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "session_analyze":
                result = analyze_patterns()
            elif tool_name == "session_recommendations":
                result = get_recommendations()
            elif tool_name == "session_state":
                result = get_session_state()
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False, default=str)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Run MCP server via stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    import sys as _sys
    if len(_sys.argv) > 1 and _sys.argv[1] != '{"jsonrpc"':
        cmd = _sys.argv[1]
        if cmd == "analyze":
            print(json.dumps(analyze_patterns(), indent=2, ensure_ascii=False))
        elif cmd == "recommendations":
            recs = get_recommendations()
            for r in recs:
                print(f"  - {r}")
        elif cmd == "state":
            print(json.dumps(get_session_state(), indent=2, ensure_ascii=False))
        else:
            print(f"Usage: python mcp-session-intel.py [analyze|recommendations|state]")
    else:
        main()
