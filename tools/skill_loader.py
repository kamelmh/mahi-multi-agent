"""MAHI Skill Loader — injects relevant skills into agent system prompts."""
from __future__ import annotations
import os
from pathlib import Path

MAHI_ROOT = Path(__file__).parent.parent
SKILLS_DIRS = [
    MAHI_ROOT / ".claude" / "skills",
    MAHI_ROOT / ".agents" / "skills",
]

# Skill trigger keywords → skill folder name
SKILL_TRIGGERS = {
    "frontend-design": ["ui", "html", "css", "component", "layout", "responsive", "design", "frontend", "page", "website"],
    "accessibility": ["a11y", "accessibility", "aria", "screen reader", "wcag"],
    "seo": ["seo", "meta", "sitemap", "search engine", "structured data"],
}


def load_relevant_skills(task_text: str, max_skills: int = 2) -> str:
    """Return skill content snippets relevant to the task text."""
    low = task_text.lower()
    matched = []

    for skill_name, keywords in SKILL_TRIGGERS.items():
        if any(kw in low for kw in keywords):
            matched.append(skill_name)

    if not matched:
        return ""

    parts = []
    for skill_name in matched[:max_skills]:
        for skills_dir in SKILLS_DIRS:
            skill_file = skills_dir / skill_name / "SKILL.md"
            if skill_file.exists():
                try:
                    content = skill_file.read_text(encoding="utf-8")[:2000]
                    parts.append(f"## Skill: {skill_name}\n{content}")
                except Exception:
                    pass
                break

    return "\n\n---\n\n".join(parts) if parts else ""
