"""MAHI Tool Registry — gives agents access to absorbed tools (pdf-tools, file-search, hound web)."""

import os
import re
import sys
import json
import importlib.util
import subprocess
from pathlib import Path

MAHI_ROOT = Path(__file__).parent.parent
PDF_TOOLS = MAHI_ROOT / "tools" / "pdf-tools"
FILE_SEARCH = MAHI_ROOT / "tools" / "file-search"

TMP_DIR = MAHI_ROOT / "tmp"



# -------------------------------------------------------------------------
# Tool definitions � can be used by routing guidance and skill composition
# -------------------------------------------------------------------------

TOOL_DEFS = {
    "file_search": {
        "type": "function",
        "function": {
            "name": "file_search",
            "description": "Search files by name under a root directory (default: MAHI brain). Use when the user's question may be answered by finding relevant files in the codebase, docs, or any directory on the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for file names"},
                    "root": {"type": "string", "description": "Root directory to search under"},
                    "content": {"type": "boolean", "description": "If True, search file contents instead of names"},
                    "limit": {"type": "integer", "description": "Maximum number of results to return"},
                },
                "required": ["query"],
            },
        },
    },
    "pdf_extract": {
        "type": "function",
        "function": {
            "name": "pdf_extract",
            "description": "Extract text and metadata from a PDF file. Use when the user needs content from a specific PDF document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Path to the PDF file to extract"},
                },
                "required": ["pdf_path"],
            },
        },
    },
    "pdf_summarize": {
        "type": "function",
        "function": {
            "name": "pdf_summarize",
            "description": "Summarize a PDF document. Use when the user wants a quick overview of a PDF's content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pdf_path": {"type": "string", "description": "Path to the PDF file to summarize"},
                },
                "required": ["pdf_path"],
            },
        },
    },
    "web_search": {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web via hound CLI. Use when the user needs current information, latest news, or external references.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for web results"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return"},
                },
                "required": ["query"],
            },
        },
    },
    "scrape": {
        "type": "function",
        "function": {
            "name": "scrape",
            "description": "Scrape a URL using Scrapling with stealth mode. Use when the user needs to extract structured data from a web page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to scrape"},
                    "selector": {"type": "string", "description": "Optional CSS selector to filter elements"},
                    "stealth": {"type": "boolean", "description": "If True, use stealth mode"},
                },
                "required": ["url"],
            },
        },
    },
}

class ToolRegistry:
    """Registry of available tools that agents can invoke."""

    def __init__(self):
        self._loaded = {}

    # --- file-search ---
    def file_search(self, query: str, root: Path = None, content: bool = False,
                    limit: int = 20) -> list[dict]:
        """Search files by name under root (default LifeWorkspace)."""
        root = Path(root) if isinstance(root, str) else root
        root = root or MAHI_ROOT / "brain"  # lightweight default
        if not root.is_dir():
            return []
        try:
            searcher_module = FILE_SEARCH / "filesearch.py"
            spec = importlib.util.spec_from_file_location(
                "filesearch", searcher_module
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            searcher = mod.FileSearcher(root=str(root), max_depth=None)
            # scan (may be slow for large repos; acceptable for a tool call)
            searcher.scan()
            q = query if content else query.lower()
            results = searcher.search_name(q, case_sensitive=False, regex=False)
            # trim to limit
            return results[:limit]
        except Exception as e:
            return [{"error": str(e)}]

    # --- pdf-tools ---
    def pdf_extract(self, pdf_path: str) -> dict:
        """Extract text + metadata from a PDF using pdf-tools PyPDF2."""
        try:
            from tools.pdf_tools.src.extract.pdf_extractor import extract_text, extract_metadata
            p = Path(pdf_path)
            if not p.is_file():
                return {"success": False, "error": f"PDF not found: {pdf_path}"}
            text_res = extract_text(str(p), max_pages=10)
            meta_res = extract_metadata(str(p))
            return {**text_res, **meta_res}
        except ImportError:
            # Fallback: try PyMuPDF fitz
            try:
                import fitz as fitz_module
                p = Path(pdf_path)
                if not p.is_file():
                    return {"success": False, "error": f"PDF not found: {pdf_path}"}
                doc = fitz_module.open(str(p))
                text = ""
                for i, page in enumerate(doc):
                    if i >= 10:
                        break
                    t = page.get_text()
                    if t:
                        text += t
                meta = doc.metadata
                doc.close()
                return {
                    "success": True,
                    "text": text.strip(),
                    "total_pages": len(doc),
                    "pages_read": min(10, len(doc)),
                    "metadata": {
                        "title": str(meta.get("title", "")),
                        "author": str(meta.get("author", "")),
                        "subject": str(meta.get("subject", "")),
                    },
                }
            except Exception as e2:
                return {"success": False, "error": str(e2)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def pdf_summarize(self, pdf_path: str) -> dict:
        """Summarize a PDF — delegates to pdf-tools summarizer if available, else basic extract."""
        try:
            res = self.pdf_extract(pdf_path)
            if not res.get("success"):
                return res
            text = res.get("text", "")
            if not text:
                return {"success": False, "error": "No extractable text in PDF"}
            # Return first 300 chars as a minimal summary
            return {
                "success": True,
                "summary": text[:300].replace("\n", " ") + ("..." if len(text) > 300 else ""),
                "total_pages": res.get("total_pages", 0),
                "pages_read": res.get("pages_read", 0),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- web search (via hound CLI / MCP) ---
    def web_search(self, query: str, max_results: int = 6) -> dict:
        """Search the web via hound (mcp-hound.py CLI)."""
        script = MAHI_ROOT / "mcp-hound.py"
        if not script.is_file():
            return {"error": "mcp-hound.py not found"}
        try:
            r = subprocess.run(
                [sys.executable, str(script), "search", query],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=90
            )
            if r.returncode == 0 and r.stdout.strip():
                # Return parsed snippet-ish result
                return {"results": r.stdout.strip()[:1500]}
            return {"error": r.stderr.strip() or "no results"}
        except Exception as e:
            return {"error": str(e)}

    # --- stealth web scraping (via Scrapling) ---
    def scrape(self, url: str, selector: str = None, stealth: bool = True) -> dict:
        """Scrape a URL using Scrapling with optional stealth mode and CSS selector."""
        try:
            if stealth:
                from scrapling.fetchers import StealthyFetcher
                fetcher = StealthyFetcher()
            else:
                from scrapling import Fetcher
                fetcher = Fetcher()
            page = fetcher.fetch(url)
            result = {"success": True, "status": page.status, "url": url}
            if selector:
                elements = page.css(selector)
                result["elements"] = [
                    {"text": el.text, "html": str(el), "attrib": dict(el.attrib)}
                    for el in elements[:20]
                ]
                result["count"] = len(elements)
            else:
                result["title"] = page.css("title")[0].text if page.css("title") else ""
                result["text"] = page.get_all_text()[:3000] if hasattr(page, "get_all_text") else ""
                result["links"] = [
                    {"href": a.attrib.get("href", ""), "text": a.text}
                    for a in page.css("a")[:15]
                ]
            return result
        except ImportError:
            return {"success": False, "error": "scrapling not installed — pip install scrapling[all]"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # --- utility: detect tool intent from task text ---
    def detect_intent(self, text: str) -> list[tuple[str, dict]]:
        """Detect which tool(s) the task is asking for, returning (tool_name, kwargs)."""
        low = text.lower()
        results = []
        tools = {"file_search", "pdf_extract", "pdf_summarize", "web_search", "scrape"}
        # PDF detection: if a .pdf path is mentioned
        if "pdf_extract" in tools or "pdf_summarize" in tools:
            for m in re.finditer(r"([A-Za-z]:\\[\w\\ .\-]+\.pdf|[\w\-/]+\.pdf)", text):
                pdf_path = m.group(1)
                if "pdf_summarize" in tools and re.search(r"\b(summarize|extract|read)\b", low):
                    results.append(("pdf_summarize", {"pdf_path": pdf_path}))
                    break  # only one PDF intent per call
                if "pdf_extract" in tools:
                    results.append(("pdf_extract", {"pdf_path": pdf_path}))
                    break
        # File search: explicit markers
        if "file_search" in tools:
            m = re.search(r"(?:find|locate|search for)\s+(?:a\s+)?(.+?)(?:\s+in\s+|$)", low)
            if m:
                results.append(("file_search", {"query": m.group(1).strip()}))
        # Web search: explicit markers
        if "web_search" in tools:
            m = re.search(r"(?:web search|search the web|look up online|latest news on|research)\s+['\"]?([^'\"]{2,120})", low)
            if m:
                results.append(("web_search", {"query": m.group(1).strip()}))
        # Scrape: explicit URL or scrape/fetch/crawl command
        if "scrape" in tools:
            m = re.search(r"(?:scrape|fetch|crawl|extract from)\s+(https?://[^\s'\"]+)", low)
            if m:
                results.append(("scrape", {"url": m.group(1).strip()}))
        # Deduplicate by tool name, keep first
        seen = set()
        uniq = []
        for name, kwargs in results:
            if name not in seen:
                seen.add(name)
                uniq.append((name, kwargs))
        return uniq

    # --- invoke detected tools ---
    def run_tool(self, tool_name: str, **kwargs) -> dict:
        """Run a named tool with given kwargs; return result dict."""
        method = getattr(self, f"_{tool_name}", None)
        if method is None:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return method(**kwargs)
        except Exception as e:
            return {"error": str(e)}

    # --- per-tool methods (delegate to the other methods above) ---
    def _file_search(self, query: str, root: Path = None, content: bool = False,
                     limit: int = 20) -> dict:
        results = self.file_search(query, root=root, content=content, limit=limit)
        return {"results": results}

    def _pdf_extract(self, pdf_path: str) -> dict:
        return self.pdf_extract(pdf_path)

    def _pdf_summarize(self, pdf_path: str) -> dict:
        return self.pdf_summarize(pdf_path)

    def _web_search(self, query: str, max_results: int = 6) -> dict:
        return self.web_search(query, max_results=max_results)

    def _scrape(self, url: str, selector: str = None, stealth: bool = True) -> dict:
        return self.scrape(url, selector=selector, stealth=stealth)

    # -------------------------------------------------------------------------
    # Routing guidance builder — tells the model which tool to pick
    # -------------------------------------------------------------------------

    def build_routing_guidance(self, available_tools: list[str] = None) -> str:
        """Build routing guidance string for the model's system prompt.

        This is analogous to AgentSwarms' buildRoutingGuidance() — it tells the
        model WHEN to use which tool based on the task description.
        """
        guidance_parts = [
            "Tool Routing Guidance:",
            "- Use **file_search** when the user asks to find, locate, or search for something in the codebase or file system.",
            "- Use **pdf_extract** when the user asks to extract or read a specific PDF file.",
            "- Use **pdf_summarize** when the user asks to summarize a PDF.",
            "- Use **web_search** when the user asks to search the web, look up online, or research current information.",
            "- Use **scrape** when the user asks to scrape, fetch, or crawl a specific URL.",
            "- If uncertain which tool to use, start with file_search or web_search to gather context.",
            "- If multiple tools could apply, prefer the most specific one for the task.",
            "- If uncertain which tool to use, start with `file_search` or `web_search` to gather context, then use more specialized tools as needed.",
        ]

        return "\n".join(guidance_parts)