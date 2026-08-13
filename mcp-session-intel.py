"""
Session Intelligence MCP Server for OpenCode
Provides session analytics and pattern detection.
"""
import sys
import os
import json
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MAHI_ROOT = Path(__file__).parent
sys.path.insert(0, str(MAHI_ROOT))

from command_center import SessionIntelligence

si = SessionIntelligence()


def analyze_patterns() -> dict:
    return {"timestamp": datetime.now().isoformat(), "analysis": si.analyze_patterns()}


def get_recommendations() -> list:
    analysis = si.analyze_patterns()
    return [a["action"] for a in analysis.get("next_actions", [])]


def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "session-intelligence", "version": "2.0.0"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": [
                {"name": "session_analyze", "description": "Analyze session patterns", "inputSchema": {"type": "object", "properties": {}}},
                {"name": "session_recommendations", "description": "Get next action recommendations", "inputSchema": {"type": "object", "properties": {}}},
            ]},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        try:
            if tool_name == "session_analyze":
                result = analyze_patterns()
            elif tool_name == "session_recommendations":
                result = get_recommendations()
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False, default=str)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
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
    if len(sys.argv) > 1 and sys.argv[1] != '{"jsonrpc"':
        cmd = sys.argv[1]
        if cmd == "analyze":
            print(json.dumps(analyze_patterns(), indent=2, ensure_ascii=False))
        elif cmd == "recommendations":
            for r in get_recommendations():
                print(f"  - {r}")
        else:
            print(f"Usage: python mcp-session-intel.py [analyze|recommendations]")
    else:
        main()
