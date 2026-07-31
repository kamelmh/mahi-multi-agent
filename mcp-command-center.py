"""
Command Center MCP Server for OpenCode
Provides system status and health monitoring.
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


def check_all_systems() -> dict:
    """Check status of all systems."""
    systems = {}

    # MAHI Multi-Agent
    try:
        sys.path.insert(0, r"C:\Users\Admin\MAHI")
        from agents.base import BaseAgent
        systems["mahi-multi-agent"] = {"status": "available", "path": r"C:\Users\Admin\MAHI"}
    except ImportError as e:
        systems["mahi-multi-agent"] = {"status": "error", "error": str(e)}

    # Session Intelligence
    try:
        sys.path.insert(0, r"C:\Users\Admin\automation\session-intelligence")
        from agent import SessionIntelligence
        systems["session-intelligence"] = {"status": "available"}
    except ImportError as e:
        systems["session-intelligence"] = {"status": "error", "error": str(e)}

    # Freelance Responder
    try:
        sys.path.insert(0, r"C:\Users\Admin\automation\freelance-responder")
        from responder import FreelanceResponder
        systems["freelance-responder"] = {"status": "available"}
    except ImportError as e:
        systems["freelance-responder"] = {"status": "error", "error": str(e)}

    # Astrology Notifier
    try:
        sys.path.insert(0, r"C:\Users\Admin\automation\astrology-notifier")
        from notifier import AstrologyNotifier
        systems["astrology-notifier"] = {"status": "available"}
    except ImportError as e:
        systems["astrology-notifier"] = {"status": "error", "error": str(e)}

    # Obsidian MCP
    try:
        obsidian_path = Path(r"C:\Users\Admin\My Drive\LifeWorkspace")
        md_count = len(list(obsidian_path.rglob("*.md")))
        systems["obsidian-mcp"] = {"status": "available", "vault_files": md_count}
    except Exception as e:
        systems["obsidian-mcp"] = {"status": "error", "error": str(e)}

    # Context Engine
    try:
        kg_path = Path(r"C:\Users\Admin\context-engine\knowledge-graph.json")
        kg_size = kg_path.stat().st_size if kg_path.exists() else 0
        systems["context-engine"] = {"status": "available", "knowledge_graph_kb": kg_size // 1024}
    except Exception as e:
        systems["context-engine"] = {"status": "error", "error": str(e)}

    # OpenCode
    try:
        opencode_path = Path(r"C:\Users\Admin\.config\opencode\opencode.jsonc")
        systems["opencode"] = {"status": "available" if opencode_path.exists() else "missing"}
    except Exception as e:
        systems["opencode"] = {"status": "error", "error": str(e)}

    return systems


def get_health_summary() -> dict:
    """Get health summary."""
    systems = check_all_systems()
    available = sum(1 for s in systems.values() if s["status"] == "available")
    total = len(systems)
    return {
        "timestamp": datetime.now().isoformat(),
        "systems": systems,
        "health": f"{available}/{total} systems available",
        "available": available,
        "total": total,
    }


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
                "serverInfo": {"name": "command-center", "version": "1.0.0"},
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
                        "name": "system_health",
                        "description": "Get health status of all MAHI systems",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "system_status",
                        "description": "Get detailed status of all systems",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

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
        if cmd == "health":
            print(json.dumps(get_health_summary(), indent=2, ensure_ascii=False))
        elif cmd == "status":
            print(json.dumps(check_all_systems(), indent=2, ensure_ascii=False))
        else:
            print(f"Usage: python mcp-command-center.py [health|status]")
    else:
        main()
