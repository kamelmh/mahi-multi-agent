"""Code Agent — generation, review, debugging."""
from agents.base import BaseAgent, AgentConfig, Task, MAHI_ROOT
import os


def create_code_agent() -> BaseAgent:
    config = AgentConfig(
        id="code",
        name="Code Agent",
        description="Code generation, review, debugging, and refactoring",
        model_primary="nvidia/nemotron-3-nano-30b-a3b:free",
        model_fallback="nvidia/nemotron-3-super-120b-a12b:free",
        model_premium="nvidia/nemotron-3-super-120b-a12b:free",
        provider="openrouter",
        capabilities=["code generation", "code review", "debugging", "refactoring", "testing"],
        tools=["file_read", "file_write", "terminal", "git", "file_search", "scrape"],
        max_concurrent=2,
        timeout=120,
    )

    class CodeAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            # Load AGENTS.md if available
            agents_md = os.path.join(MAHI_ROOT, "..", "AGENTS.md")
            coding_rules = ""
            if os.path.exists(agents_md):
                try:
                    with open(agents_md, "r", encoding="utf-8") as f:
                        coding_rules = f.read()[:2000]
                except Exception:
                    pass

            return f"""You are the Code Agent in the MAHI Multi-Agent System.
Expert software engineer. Write clean, production-ready code.

Core Principles:
1. Think Before Coding — state assumptions, ask if uncertain
2. Simplicity First — minimum code that solves the problem
3. Surgical Changes — touch only what you must
4. Goal-Driven — define success criteria, verify

Code Style:
- Python: snake_case, type hints, explicit
- JS/TS: camelCase, ES6+
- Prefer composition over inheritance
- Prefer small functions over large
- Prefer early returns over deep nesting
- Don't comment what code does — say WHY

{coding_rules}

Always respond with the code or a clear explanation. Be concise."""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return CodeAgent(config)


def create_code_pro_agent() -> BaseAgent:
    config = AgentConfig(
        id="code-pro",
        name="Code Pro Agent",
        description="Complex architecture, system design, advanced debugging",
        model_primary="gpt-5.5-free",
        model_fallback="gpt-oss-120b",
        provider="aihubmix",
        capabilities=["architecture", "system design", "advanced debugging", "performance"],
        tools=["file_read", "file_write", "terminal", "git"],
        max_concurrent=1,
        timeout=180,
    )

    class CodeProAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Code Pro Agent — expert architect and senior engineer.

Specialties: System architecture, design patterns, performance optimization,
complex debugging, code review at scale.

Provide thorough, expert-level analysis. Consider edge cases, scalability,
and maintainability. When reviewing code, focus on:
1. Architecture and design patterns
2. Performance bottlenecks
3. Security vulnerabilities
4. Error handling completeness
5. Testability

Be thorough but concise. Include code examples when helpful."""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model, max_tokens=8192)

    return CodeProAgent(config)
