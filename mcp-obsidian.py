"""
Obsidian MCP Server for OpenCode
Provides vault access as MCP tools.
"""
import sys
import os
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

VAULT_PATH = Path(r"C:\Users\Admin\My Drive\LifeWorkspace")


def search_notes(query: str, limit: int = 10) -> list:
    """Search for notes in the Obsidian vault."""
    results = []
    query_lower = query.lower()

    for md_file in VAULT_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if query_lower in content.lower() or query_lower in md_file.stem.lower():
                rel_path = str(md_file.relative_to(VAULT_PATH))
                snippet = content[:200].replace("\n", " ").strip()
                results.append({"path": rel_path, "name": md_file.stem, "snippet": snippet})
                if len(results) >= limit:
                    break
        except Exception:
            continue
    return results


def read_note(path: str) -> str:
    """Read a specific note by path."""
    full_path = VAULT_PATH / path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    return f"Note not found: {path}"


def create_note(path: str, content: str) -> str:
    """Create a new note in the vault."""
    full_path = VAULT_PATH / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    return f"Created: {path}"


def update_note(path: str, content: str) -> str:
    """Update an existing note."""
    full_path = VAULT_PATH / path
    if full_path.exists():
        full_path.write_text(content, encoding="utf-8")
        return f"Updated: {path}"
    return f"Note not found: {path}"


def list_notes(directory: str = "") -> list:
    """List all notes in a directory."""
    dir_path = VAULT_PATH / directory if directory else VAULT_PATH
    notes = []
    try:
        for item in dir_path.iterdir():
            if item.is_file() and item.suffix == ".md":
                notes.append({"name": item.stem, "path": str(item.relative_to(VAULT_PATH)), "type": "file"})
            elif item.is_dir() and not item.name.startswith("."):
                notes.append({"name": item.name, "path": str(item.relative_to(VAULT_PATH)), "type": "directory"})
    except Exception:
        pass
    return notes


def get_stats() -> dict:
    """Get vault statistics."""
    md_files = list(VAULT_PATH.rglob("*.md"))
    pdf_files = list(VAULT_PATH.rglob("*.pdf"))
    total_size = sum(f.stat().st_size for f in VAULT_PATH.rglob("*") if f.is_file())
    return {
        "total_md": len(md_files),
        "total_pdf": len(pdf_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "vault_path": str(VAULT_PATH),
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
                "serverInfo": {"name": "obsidian-vault", "version": "1.0.0"},
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
                        "name": "obsidian_search",
                        "description": "Search notes in Obsidian vault by keyword",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"},
                                "limit": {"type": "integer", "description": "Max results", "default": 10},
                            },
                            "required": ["query"],
                        },
                    },
                    {
                        "name": "obsidian_read",
                        "description": "Read a specific note from Obsidian vault",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Note path relative to vault root"},
                            },
                            "required": ["path"],
                        },
                    },
                    {
                        "name": "obsidian_create",
                        "description": "Create a new note in Obsidian vault",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Note path"},
                                "content": {"type": "string", "description": "Note content"},
                            },
                            "required": ["path", "content"],
                        },
                    },
                    {
                        "name": "obsidian_update",
                        "description": "Update an existing note in Obsidian vault",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "description": "Note path"},
                                "content": {"type": "string", "description": "New content"},
                            },
                            "required": ["path", "content"],
                        },
                    },
                    {
                        "name": "obsidian_list",
                        "description": "List notes in Obsidian vault directory",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "directory": {"type": "string", "description": "Directory path (empty for root)"},
                            },
                        },
                    },
                    {
                        "name": "obsidian_stats",
                        "description": "Get Obsidian vault statistics",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "obsidian_search":
                result = search_notes(arguments["query"], arguments.get("limit", 10))
            elif tool_name == "obsidian_read":
                result = read_note(arguments["path"])
            elif tool_name == "obsidian_create":
                result = create_note(arguments["path"], arguments["content"])
            elif tool_name == "obsidian_update":
                result = update_note(arguments["path"], arguments["content"])
            elif tool_name == "obsidian_list":
                result = list_notes(arguments.get("directory", ""))
            elif tool_name == "obsidian_stats":
                result = get_stats()
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
        args = _sys.argv[2:]
        if cmd == "search":
            print(json.dumps(search_notes(args[0], int(args[1]) if len(args) > 1 else 10), indent=2, ensure_ascii=False))
        elif cmd == "read":
            print(read_note(args[0]))
        elif cmd == "create":
            print(create_note(args[0], args[1]))
        elif cmd == "list":
            print(json.dumps(list_notes(args[0] if args else ""), indent=2, ensure_ascii=False))
        elif cmd == "stats":
            print(json.dumps(get_stats(), indent=2, ensure_ascii=False))
        elif cmd == "recent":
            notes = list_notes("")
            for n in notes[:int(args[0]) if args else 5]:
                print(f"  {n['path']}")
        else:
            print(f"Usage: python mcp-obsidian.py [search|read|create|list|stats|recent] [args]")
    else:
        main()
