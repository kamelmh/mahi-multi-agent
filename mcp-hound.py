"""
Hound MCP Server for MAHI Multi-Agent System
Provides keyless web search, fetch, crawl, screenshot, cache clearing, and version.

Mirrors mcp-obsidian.py pattern: stdio JSON-RPC MCP server + direct CLI mode.
"""
import sys
import os
import json
import subprocess
import asyncio
import shutil
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MAHI_ROOT = Path(__file__).parent
sys.path.insert(0, str(MAHI_ROOT))

# ── Hound binary detection ──────────────────────────────────────────────
HOUND_EXE = None
# Prefer the hound.exe that was installed with hound-mcp (Python 3.14 env)
_preferred = Path(
    r"C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\Scripts\hound.exe"
)
if _preferred.is_file():
    HOUND_EXE = str(_preferred)
else:
    # Fall back to shutil.which (works if System32 is on PATH)
    _found = shutil.which("hound")
    if _found:
        HOUND_EXE = _found

# ── 6 hound tool schemas (matching master_fetch.server tool definitions) ──
HOUND_TOOLS = [
    {
        "name": "mcp_smart_fetch",
        "description": "Fetch any URL or PDF. Auto anti-bot (HTTP -> stealthy). Use after smart_search to get page content - search gives URLs + snippets, smart_fetch gives the full page.\n\nPOWER FEATURES: focus='query' extracts only BM25-relevant paragraphs. pages='9' or pages='1-5,9-7' for specific PDF pages. urls=['url1','url2']: parallel bulk fetch.\n\nRESPONSE SIGNALS: content_ok=True = real content. False = JS shell, login wall, or error. next_action: follow it - optimal next call (paginate, switch source). page_type: 'list' = page links to real content, 'auth_wall'/'paywall' = behind login. network: data over XHR. is_truncated + next_offset: more content. content_age_days + is_stale: seek newer sources. quality_score: PDF extraction quality 0-1.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {"type": "array", "items": {"type": "string"}, "description": "Multiple URLs to fetch in parallel."},
                "url": {"type": "string", "description": "Single URL to fetch."},
                "focus": {"type": "string", "description": "Query-focused BM25 filter."},
                "pages": {"type": "string", "description": "PDF page spec like '1-5' or '1,3,5-7'."},
                "css_selector": {"type": "string", "description": "DOM element to narrow extraction."},
            },
            "required": ["url"],
        },
    },
    {
        "name": "mcp_smart_search",
        "description": "Keyless web search (no API key, no account). 10 general backends in parallel (DDG, Brave, Mojeek, Yahoo, Yandex, Startpage, Google, Wikipedia, Grokipedia) neural-reranked + consensus + six-signal ranking.\n\nRESULT FIELDS: relevance_score (0-1), fetch_relevance (high/med/low), engines_consensus, source_type, related_queries.\n\nFILTERS: site, exclude_sites, freshness, page, location, language, region.\n\nBYOK: configured Serper/Tavily/Exa/Firecrawl/TinyFish keys become primary with rotation; otherwise keyless backends used.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text."},
                "max_results": {"type": "integer", "default": 6, "description": "Max results to return."},
                "site": {"type": "string", "description": "Restrict to domain."},
                "exclude_sites": {"type": "array", "items": {"type": "string"}},
                "freshness": {"type": "string", "enum": ["day", "week", "month", "year"]},
            },
            "required": ["query"],
        },
    },
    {
        "name": "mcp_smart_crawl",
        "description": "Deep-crawl a site: best-first same-domain walk, each page as markdown + content_ok + page_type.\n\nTWO-PHASE CRAWL: sitemap maps all URLs from sitemap.xml in one fetch -> then crawl_urls to fetch only those pages. sitemap='auto' = use if present else BFS. discover_only = URL map only.\n\nfocus='query' prioritizes relevant pages AND focus-filters each page's content. Caps: max_pages (10), max_depth (2), max_total_chars (token budget), deadline_ms.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Start URL to crawl."},
                "focus": {"type": "string", "description": "Query to prioritize & filter content."},
                "max_pages": {"type": "integer", "default": 10},
                "max_depth": {"type": "integer", "default": 2},
            },
            "required": ["url"],
        },
    },
    {
        "name": "mcp_screenshot",
        "description": "Screenshot a URL as an image. Multimodal agents only (content as images/canvas/visual layout). Text agents: use smart_fetch. Stealthy browser auto-managed.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to screenshot."},
                "full_page": {"type": "boolean", "default": True},
            },
            "required": ["url"],
        },
    },
    {
        "name": "cache_clear",
        "description": "Clear fetch cache. all=true wipes all (default: expired only). To re-fetch one URL fresh, pass cache_ttl=0 to smart_fetch/smart_crawl instead.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "all": {"type": "boolean", "description": "Wipe entire cache."},
            },
        },
    },
    {
        "name": "version",
        "description": "Show version + update status of hound.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


# ── MCP JSON-RPC handler ────────────────────────────────────────────────
def handle_request(request: dict) -> dict:
    """Handle MCP JSON-RPC request — mirrors mcp-obsidian.py pattern."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "hound", "version": "13.1.2"},
            },
        }
    elif method == "notifications/initialized":
        return None
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": HOUND_TOOLS},
        }
    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        # Try persistent hound subprocess proxy
        if not hasattr(handle_request, "_hound_proxy"):
            handle_request._hound_proxy = HoundProxy()
        try:
            result = handle_request._hound_proxy.call_tool(tool_name, arguments)
            return {"jsonrpc": "2.0", "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id,
                    "error": {"code": -32603, "message": f"Tool call failed: {e}"}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


class HoundProxy:
    """Persistent JSON-RPC proxy to the hound MCP server (stdio)."""

    def __init__(self):
        self.proc = None
        self._init_done = False

    def _ensure_hound(self):
        if self.proc is None and HOUND_EXE:
            self.proc = subprocess.Popen(
                [HOUND_EXE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace"
            )
            # Wait for initialize response (one-line JSON)
            import time
            deadline = time.time() + 30
            while time.time() < deadline:
                line = self.proc.stdout.readline()
                if not line:
                    break
                try:
                    msg = json.loads(line)
                    if msg.get("id") == 1 and "result" in msg:
                        self._init_done = True
                        break
                except Exception:
                    pass
            if not self._init_done:
                # Best-effort: proceed anyway; hound warms on first fetch
                self._init_done = True

    def call_tool(self, tool_name: str, arguments: dict):
        """Send a tools/call to the persistent hound subprocess and return the text result."""
        self._ensure_hound()
        if self.proc is None:
            # Fallback: spawn one-shot hound call via CLI proxy
            return self._one_shot_call(tool_name, arguments)

        # Send JSON-RPC tools/call request
        msg = {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": tool_name, "arguments": arguments}, "id": 1}
        self.proc.stdin.write(json.dumps(msg) + "\n")
        self.proc.stdin.flush()

        # Read response line (hound returns one line per response)
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("hound proxy: no response from hound")
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            raise RuntimeError(f"hound proxy: malformed response: {line}")

        # hound returns: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"..."}]}}
        if "error" in msg:
            raise RuntimeError(f"hound error: {msg['error']}")
        result = msg.get("result", {})
        content = result.get("content", [])
        if content and content[0].get("type") == "text":
            return content[0]["text"]
        return str(result)

    def _one_shot_call(self, tool_name, arguments):
        """One-shot: spawn hound, send request, read response, exit."""
        exe = HOUND_EXE or shutil.which("hound")
        if not exe:
            raise RuntimeError("Hound binary not found. Install hound-mcp[all].")
        # Build JSON-RPC request: initialize + tools/call in one session
        # Use hound's stdio MCP: write initialize, wait for result, then tools/call, read result, then close.
        import time
        proc = subprocess.Popen(
            [exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="replace"
        )
        try:
            # 1. initialize
            init_msg = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "mahi", "version": "1.0"}}}
            proc.stdin.write(json.dumps(init_msg) + "\n"); proc.stdin.flush()
            # read init response (id=1 result)
            init_resp = proc.stdout.readline()
            # 2. notifications/initialized (no id, no response needed) — but we skip to tools/call
            # 3. tools/call
            call_msg = {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": tool_name, "arguments": arguments}, "id": 2}
            proc.stdin.write(json.dumps(call_msg) + "\n"); proc.stdin.flush()
            # read response
            resp_line = proc.stdout.readline()
            proc.stdin.close()
            proc.wait(timeout=60)
            resp = json.loads(resp_line)
            if "error" in resp:
                raise RuntimeError(f"hound one-shot error: {resp['error']}")
            result = resp.get("result", {})
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                return content[0]["text"]
            return str(result)
        finally:
            try:
                proc.stdin.close()
            except Exception:
                pass


# ── CLI mode ────────────────────────────────────────────────────────────
def main():
    """CLI entry points: python mcp-hound.py search <query> | fetch <url> | ..."""
    if len(sys.argv) < 2:
        print("Usage: python mcp-hound.py <search|fetch|crawl|screenshot|cache_clear|version> [args]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "version":
        # invoke version tool via proxy or just print installed version
        print("Hound v13.1.2 (keyless)")
    elif cmd == "search":
        query = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
        if not query:
            print("Usage: python mcp-hound.py search <query>")
            sys.exit(1)
        # one-shot search via hound
        try:
            result = HoundProxy()._one_shot_call("mcp_smart_search", {"query": query, "max_results": 5})
            print(result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif cmd == "fetch":
        url = sys.argv[2] if len(sys.argv) > 2 else ""
        if not url:
            print("Usage: python mcp-hound.py fetch <url>")
            sys.exit(1)
        try:
            result = HoundProxy()._one_shot_call("mcp_smart_fetch", {"url": url, "focus": "general"})
            # Print key parts
            print(result[:2000] if len(result) > 2000 else result)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif cmd == "cache_clear":
        try:
            HoundProxy()._one_shot_call("cache_clear", {"all": False})
            print("Cache cleared.")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python mcp-hound.py <search|fetch|crawl|screenshot|cache_clear|version> [args]")


if __name__ == "__main__":
    main()