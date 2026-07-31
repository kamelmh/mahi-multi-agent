"""
Obsidian MCP Integration for OpenCode
Adds Obsidian vault access as MCP tools.
"""
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


VAULT_PATH = Path(r"C:\Users\Admin\My Drive\LifeWorkspace")


def search_notes(query: str, limit: int = 10) -> List[Dict]:
    """Search for notes in the Obsidian vault."""
    results = []
    query_lower = query.lower()

    for md_file in VAULT_PATH.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            if query_lower in content.lower() or query_lower in md_file.stem.lower():
                rel_path = md_file.relative_to(VAULT_PATH)
                # Get first 200 chars as snippet
                snippet = content[:200].replace("\n", " ").strip()
                results.append({
                    "path": str(rel_path),
                    "name": md_file.stem,
                    "snippet": snippet,
                })
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


def list_notes(directory: str = "") -> List[Dict]:
    """List all notes in a directory."""
    dir_path = VAULT_PATH / directory if directory else VAULT_PATH
    notes = []

    for item in dir_path.iterdir():
        if item.is_file() and item.suffix == ".md":
            notes.append({
                "name": item.stem,
                "path": str(item.relative_to(VAULT_PATH)),
                "size": item.stat().st_size,
            })
        elif item.is_dir() and not item.name.startswith("."):
            notes.append({
                "name": item.name + "/",
                "path": str(item.relative_to(VAULT_PATH)),
                "type": "directory",
            })

    return notes


def get_vault_stats() -> Dict:
    """Get vault statistics."""
    md_files = list(VAULT_PATH.rglob("*.md"))
    pdf_files = list(VAULT_PATH.rglob("*.pdf"))
    img_files = list(VAULT_PATH.rglob("*.png")) + list(VAULT_PATH.rglob("*.jpg"))

    total_size = sum(f.stat().st_size for f in VAULT_PATH.rglob("*") if f.is_file())

    return {
        "total_md": len(md_files),
        "total_pdf": len(pdf_files),
        "total_images": len(img_files),
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "vault_path": str(VAULT_PATH),
    }


# MCP Tool definitions for OpenCode
MCP_TOOLS = [
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
                "path": {"type": "string", "description": "Note path relative to vault root"},
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
                "path": {"type": "string", "description": "Note path relative to vault root"},
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


def handle_tool_call(tool_name: str, arguments: Dict) -> Any:
    """Handle MCP tool calls."""
    if tool_name == "obsidian_search":
        return search_notes(arguments["query"], arguments.get("limit", 10))
    elif tool_name == "obsidian_read":
        return read_note(arguments["path"])
    elif tool_name == "obsidian_create":
        return create_note(arguments["path"], arguments["content"])
    elif tool_name == "obsidian_update":
        return update_note(arguments["path"], arguments["content"])
    elif tool_name == "obsidian_list":
        return list_notes(arguments.get("directory", ""))
    elif tool_name == "obsidian_stats":
        return get_vault_stats()
    else:
        return f"Unknown tool: {tool_name}"


def main():
    """CLI interface for Obsidian MCP."""
    import sys
    if len(sys.argv) < 2:
        print("Usage: python obsidian_mcp.py <command> [args]")
        print("Commands:")
        print("  search <query>     - Search notes")
        print("  read <path>        - Read a note")
        print("  list [directory]   - List notes")
        print("  stats              - Vault statistics")
        print("  tools              - List MCP tools")
        return

    command = sys.argv[1]

    if command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = search_notes(query)
        for r in results:
            print(f"  {r['path']}: {r['snippet'][:80]}...")

    elif command == "read" and len(sys.argv) > 2:
        path = sys.argv[2]
        content = read_note(path)
        print(content[:2000])

    elif command == "list":
        directory = sys.argv[2] if len(sys.argv) > 2 else ""
        notes = list_notes(directory)
        for n in notes:
            print(f"  {n['path']}")

    elif command == "stats":
        stats = get_vault_stats()
        print(json.dumps(stats, indent=2))

    elif command == "tools":
        for tool in MCP_TOOLS:
            print(f"  {tool['name']}: {tool['description']}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
