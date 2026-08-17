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


class ToolRegistry:
    """Registry of available tools that agents can invoke."""

    def __init__(self):
        self._loaded = {}

    # --- file-search ---
    def file_search(self, query: str, root: Path = None, content: bool = False,
                    limit: int = 20) -> list[dict]:
        """Search files by name under root (default LifeWorkspace)."""
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

    # --- utility: detect tool intent from task text ---
    def detect_intent(self, text: str) -> list[tuple[str, dict]]:
        """Detect which tool(s) the task is asking for, returning (tool_name, kwargs)."""
        low = text.lower()
        results = []
        tools = {"file_search", "pdf_extract", "pdf_summarize", "web_search"}
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