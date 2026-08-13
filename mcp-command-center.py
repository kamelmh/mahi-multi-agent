"""
Command Center MCP Server for OpenCode
Provides system status and health monitoring.
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

from command_center import CommandCenter, WORKSPACE

cc = CommandCenter()


def check_all_systems() -> dict:
    systems = {}
    for name, path in cc.systems.items():
        if path.exists():
            files = list(path.rglob("*.md"))
            systems[name] = {"status": "available", "files": len(files)}
        else:
            systems[name] = {"status": "missing"}
    systems["obsidian-mcp"] = {"status": "available", "vault_files": len(list(WORKSPACE.rglob("*.md")))}
    return systems


def get_health_summary() -> dict:
    systems = check_all_systems()
    available = sum(1 for s in systems.values() if s["status"] == "available")
    total = len(systems)
    return {
        "timestamp": datetime.now().isoformat(),
        "systems": systems,
        "health": f"{available}/{total} systems available",
    }


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
                "serverInfo": {"name": "command-center", "version": "2.0.0"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": [
                {"name": "system_health", "description": "Get health status of all MAHI systems", "inputSchema": {"type": "object", "properties": {}}},
                {"name": "system_status", "description": "Get detailed status of all systems", "inputSchema": {"type": "object", "properties": {}}},
            ]},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        try:
            if tool_name == "system_health":
                result = get_health_summary()
            elif tool_name == "system_status":
                result = check_all_systems()
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}}
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
        if cmd == "health":
            print(json.dumps(get_health_summary(), indent=2, ensure_ascii=False))
        elif cmd == "status":
            print(json.dumps(check_all_systems(), indent=2, ensure_ascii=False))
        else:
            print(f"Usage: python mcp-command-center.py [health|status]")
    else:
        main()
