"""Summarizer - Uses Groq API to analyze and summarize extracted content.

Groq provides free API access with fast inference.
Uses Llama 3.1 8B for summarization tasks.
"""

import os
import json
import httpx


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"


def get_api_key():
    """Get Groq API key from environment."""
    return os.environ.get("GROQ_API_KEY", "")


def summarize_text(text, context="general document", max_tokens=500):
    """Summarize text using Groq API."""
    api_key = get_api_key()
    if not api_key:
        return {"success": False, "error": "No GROQ_API_KEY set"}

    prompt = f"""Analyze this document and provide:
1. TITLE: A descriptive title
2. CATEGORY: One of [academic, spiritual, teaching, logistics, business, personal, technical, other]
3. SUMMARY: 2-3 sentence summary
4. KEY_TOPICS: List of 3-5 key topics
5. ACTIONABLE_INFO: Any useful information, URLs, setups, configurations, or references found

Context: {context}

Document text (first 3000 chars):
{text[:3000]}

Respond in JSON format:
{{
    "title": "...",
    "category": "...",
    "summary": "...",
    "key_topics": ["...", "..."],
    "actionable_info": ["...", "..."]
}}"""

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
                },
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Extract JSON from response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return {"success": True, **json.loads(content[start:end])}
            return {"success": True, "raw": content}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_image_context(filename, dimensions, category):
    """Provide context about what an image might contain based on metadata."""
    name_lower = filename.lower()

    hints = []
    if "screenshot" in name_lower or "capture" in name_lower:
        hints.append("screenshot")
    if any(x in name_lower for x in ["github", "repo", "code", "terminal"]):
        hints.append("code/repository")
    if any(x in name_lower for x in ["setup", "config", "setting"]):
        hints.append("configuration")
    if any(x in name_lower for x in ["ui", "design", "mockup", "frame"]):
        hints.append("UI/design")
    if any(x in name_lower for x in ["logo", "icon", "brand"]):
        hints.append("branding")
    if any(x in name_lower for x in ["photo", "img", "pic"]):
        hints.append("photo")

    return {
        "hints": hints,
        "likely_content": ", ".join(hints) if hints else "unknown",
    }
