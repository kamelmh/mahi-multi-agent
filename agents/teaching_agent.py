"""Teaching Agent — education content, exercises, grading."""
from agents.base import BaseAgent, AgentConfig, Task


def create_teaching_agent() -> BaseAgent:
    config = AgentConfig(
        id="teaching",
        name="Teaching Agent",
        description="English teaching content, exercises, lesson plans, grading",
        model_primary="nvidia/nemotron-3-nano-30b-a3b:free",
        model_fallback="nvidia/nemotron-3-super-120b-a12b:free",
        provider="openrouter",
        capabilities=["exercise generation", "lesson plans", "grading", "curriculum design"],
        tools=["file_read", "file_write", "templates", "file_search"],
        max_concurrent=1,
        timeout=120,
    )

    class TeachingAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Teaching Agent for the English Education Project.

Context: AI-powered English teaching system for Algerian schools
Levels: A1 (1AM) to B2 (4AM) — Algerian Bac curriculum
Skills: Grammar, vocabulary, phonetics, reading, writing

Exercise Types:
- Fill-in-the-blank
- Multiple choice (MCQ)
- Sentence building
- Error correction
- Matching
- Reading comprehension
- Writing prompts

Rules:
- Align with Algerian curriculum
- Include answer keys
- Progressive difficulty
- Clear instructions in English
- Cultural relevance for Algerian students

CBA (Competency-Based Approach) methodology:
- Real-world contexts
- Student-centered
- Integrated skills
- Assessment for learning"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return TeachingAgent(config)
