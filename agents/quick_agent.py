"""Quick Agent — simple questions, fast answers."""
from agents.base import BaseAgent, AgentConfig, Task


def create_quick_agent() -> BaseAgent:
    config = AgentConfig(
        id="quick",
        name="Quick Agent",
        description="Simple questions, quick answers, fast lookups",
        model_primary="google/gemma-4-26b-a4b-it:free",
        model_fallback="nvidia/nemotron-3-super-120b-a12b:free",
        provider="openrouter",
        capabilities=["quick answers", "definitions", "calculations", "conversions"],
        tools=[],
        max_concurrent=3,
        timeout=30,
    )

    class QuickAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Quick Agent — fast, concise answers.

Rules:
- Reply in 1-3 sentences max
- No preamble, no conclusion
- Direct answer only
- If complex, say "use /code for complex tasks"
- For math, just give the answer
- For definitions, one sentence"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model, max_tokens=256)

    return QuickAgent(config)
