"""Research Agent — web search, analysis, summarization."""
from agents.base import BaseAgent, AgentConfig, Task


def create_research_agent() -> BaseAgent:
    config = AgentConfig(
        id="research",
        name="Research Agent",
        description="Web research, analysis, comparison, summarization",
        model_primary="nvidia/nemotron-3-super-120b-a12b:free",
        model_fallback="openai/gpt-oss-20b:free",
        provider="openrouter",
        capabilities=["web search", "analysis", "comparison", "summarization", "fact-checking"],
        tools=["web_search", "file_read", "file_write"],
        max_concurrent=1,
        timeout=120,
    )

    class ResearchAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Research Agent — thorough analysis and fact-finding.

Approach:
1. Understand the question clearly
2. Consider multiple perspectives
3. Cite sources when possible
4. Distinguish fact from opinion
5. Provide actionable insights

Format:
- Summary first (2-3 sentences)
- Detailed findings
- Key takeaways
- Recommended actions

Be thorough but concise. Use bullet points for clarity."""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return ResearchAgent(config)
