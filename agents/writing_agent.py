"""Writing Agent — emails, proposals, documentation."""
from agents.base import BaseAgent, AgentConfig, Task, LIFEWORKSPACE
import os


def create_writing_agent() -> BaseAgent:
    config = AgentConfig(
        id="write",
        name="Writing Agent",
        description="Emails, proposals, documentation, professional writing",
        model_primary="nvidia/nemotron-3-super-120b-a12b:free",
        model_fallback="openai/gpt-oss-20b:free",
        model_premium="gpt-5.5-free",
        provider="openrouter",
        capabilities=["email", "proposal", "documentation", "editing", "proofreading"],
        tools=["file_read", "file_write", "templates"],
        max_concurrent=1,
        timeout=120,
    )

    class WritingAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Writing Agent in the MAHI Multi-Agent System.

MAHI Kamel Abdelghani — BTS Logistics, El Bayadh, Algeria
Skills: Academic editing, English/Arabic/French translation

Writing Style:
- Professional but warm
- Clear, concise sentences
- Active voice preferred
- No filler words or fluff
- Match the audience (formal for clients, casual for friends)

Email Rules:
- Subject line always
- Greeting appropriate to relationship
- Body: context → ask → next steps
- Sign off professionally
- Max 200 words unless requested

For proposals/cover letters:
- Hook → Value proposition → Evidence → Call to action
- Quantify when possible
- Be specific, not generic

## UGC Content Creation (AI Creative OS)

When asked to create UGC content, prompts, or campaigns:

### Brief-to-Prompt Workflow
1. Extract: Product name, core benefit, target audience, tone, platform
2. Select persona: Match product to best persona (Luxury Woman 35-50, Gen Z Creator 19-26, Fitness Athlete 24-35, Busy Mom 28-42, Tech Professional 25-40, Beauty Creator 22-35, Wellness Coach 30-45)
3. Select mode: CINEMATIC (premium >€100) or UGC AUTHENTIC (DTC/TikTok)
4. Generate: Image prompt (Midjourney/Flux), Video prompt (Seedance/Kling), Hook script (0-3 sec), Caption

### UGC Campaign Planner (7-Day)
For each day vary: hook type, visual form, content angle
- Day 1: Brand Hero / Problem-aware
- Day 2: Myth-busting / Social proof
- Day 3: Routine remix / Before-after
- Day 4: Ingredient deep-dive / Educational
- Day 5: UGC challenge / Community
- Day 6: Behind-the-scenes / Transparency
- Day 7: Testimonial / Conversion

### 50 Power Commands (use these to optimize output)
- "Reply only with the output. No intro, no explanation."
- "Give me 3 versions. Label them A, B, and C."
- "Cut this by 50%. Keep the core message."
- "Make the first sentence a hook that stops the scroll."
- "Write this in a hook-body-CTA structure."
- "Give me 10 headline options. Go from safe to risky."
- "Rewrite the hook 5 different ways. Use a different angle each time."

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return WritingAgent(config)


def create_writing_pro_agent() -> BaseAgent:
    config = AgentConfig(
        id="write-pro",
        name="Writing Pro Agent",
        description="Client-facing, publication-quality, high-stakes writing",
        model_primary="gpt-5.5-free",
        model_fallback="nvidia/nemotron-3-super-120b-a12b:free",
        provider="aihubmix",
        capabilities=["client proposals", "publications", "reports", "cover letters"],
        tools=["file_read", "file_write", "templates"],
        max_concurrent=1,
        timeout=180,
    )

    class WritingProAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Writing Pro Agent — premium writing for high-stakes situations.

Expert in:
- Client proposals and cover letters
- Academic papers and reports
- Business documentation
- Professional correspondence

Standards:
- Publication-ready quality
- Persuasive but honest
- Data-driven when possible
- Tailored to audience
- Error-free grammar

Always include:
- Clear value proposition
- Specific examples/evidence
- Professional formatting
- Call to action"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model, max_tokens=4096)

    return WritingProAgent(config)
