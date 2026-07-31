"""Career Agent — CV, jobs, applications."""
from agents.base import BaseAgent, AgentConfig, Task, LIFEWORKSPACE
import os


def create_career_agent() -> BaseAgent:
    config = AgentConfig(
        id="career",
        name="Career Agent",
        description="CV writing, job applications, LinkedIn optimization",
        model_primary="nvidia/nemotron-3-super-120b-a12b:free",
        model_fallback="openai/gpt-oss-20b:free",
        provider="openrouter",
        capabilities=["cv writing", "cover letters", "job search", "linkedin", "interview prep"],
        tools=["file_read", "file_write", "web_search"],
        max_concurrent=1,
        timeout=120,
    )

    class CareerAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Career Agent for MAHI Kamel Abdelghani.

Profile:
- BA English Language (Saida, 2015-2020)
- BTS Stock Management & Logistics (CNEPD, in progress)
- Skills: Python, VBA, Claude API, Academic Editing, English C1
- Location: El Bayadh, Algeria
- Target: AI/DSS roles, freelancing (editing, formatting)

Career Advice Rules:
- Be honest about qualifications
- Highlight transferable skills
- Focus on what CAN be done, not what can't
- Tailor to each opportunity
- Quantify achievements when possible

For CVs:
- Skills-based format (not chronological)
- Include real projects (Academix DSS, Teaching System)
- Certifications: CCA-F (in progress)
- Languages: Arabic (native), English (C1), French (B1)"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return CareerAgent(config)
