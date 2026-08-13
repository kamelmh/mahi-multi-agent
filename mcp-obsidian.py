"""
Obsidian MCP Server for OpenCode
Provides vault access as MCP tools.
"""
import sys
import os
import json
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MAHI_ROOT = Path(__file__).parent
sys.path.insert(0, str(MAHI_ROOT))

from command_center import ObsidianVault, WORKSPACE

vault = ObsidianVault()


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
                "serverInfo": {"name": "obsidian-vault", "version": "2.0.0"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": [
                {"name": "obsidian_search", "description": "Search notes in Obsidian vault", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}}, "required": ["query"]}},
                {"name": "obsidian_read", "description": "Read a note from Obsidian vault", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
                {"name": "obsidian_list", "description": "List notes in vault directory", "inputSchema": {"type": "object", "properties": {"directory": {"type": "string"}}}},
                {"name": "obsidian_stats", "description": "Get vault statistics", "inputSchema": {"type": "object", "properties": {}}},
            ]},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            if tool_name == "obsidian_search":
                result = vault.search_notes(arguments["query"], arguments.get("limit", 10))
            elif tool_name == "obsidian_read":
                result = vault.read_note(arguments["path"])
            elif tool_name == "obsidian_list":
                result = vault.list_directory(arguments.get("directory", ""))
            elif tool_name == "obsidian_stats":
                result = vault.get_vault_info()
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
        args = sys.argv[2:]
        if cmd == "search":
            print(json.dumps(vault.search_notes(args[0], int(args[1]) if len(args) > 1 else 10), indent=2, ensure_ascii=False))
        elif cmd == "read":
            print(vault.read_note(args[0]).get("content", "Not found"))
        elif cmd == "list":
            print(json.dumps(vault.list_directory(args[0] if args else ""), indent=2, ensure_ascii=False))
        elif cmd == "stats":
            print(json.dumps(vault.get_vault_info(), indent=2, ensure_ascii=False))
        else:
            print(f"Usage: python mcp-obsidian.py [search|read|list|stats] [args]")
    else:
        main()
