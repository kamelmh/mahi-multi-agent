"""PDF Text Extractor - Extracts text and metadata from PDFs.

Uses PyPDF2 for text extraction.
Outputs structured data for summarization.
"""

import os
import json
import PyPDF2


def extract_text(pdf_path, max_pages=10):
    """Extract text from a PDF file."""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            metadata = reader.metadata or {}
            total_pages = len(reader.pages)
            text_parts = []
            pages_read = min(total_pages, max_pages)

            for i in range(pages_read):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    text_parts.append(text.strip())

            return {
                "success": True,
                "text": "\n\n".join(text_parts),
                "total_pages": total_pages,
                "pages_read": pages_read,
                "metadata": {
                    "title": str(metadata.get("title", "")),
                    "author": str(metadata.get("author", "")),
                    "subject": str(metadata.get("subject", "")),
                },
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_metadata(pdf_path):
    """Extract metadata from a PDF without reading all pages."""
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            metadata = reader.metadata or {}
            return {
                "success": True,
                "pages": len(reader.pages),
                "title": str(metadata.get("title", "")),
                "author": str(metadata.get("author", "")),
                "subject": str(metadata.get("subject", "")),
            }
    except Exception as e:
        return {"success": False, "error": str(e)}
