"""Spiritual Agent — astrology, Quran, spiritual practice."""
from agents.base import BaseAgent, AgentConfig, Task


def create_spiritual_agent() -> BaseAgent:
    config = AgentConfig(
        id="spiritual",
        name="Spiritual Agent",
        description="Vedic astrology, Quranic study, spiritual practice",
        model_primary="google/gemma-4-26b-a4b-it:free",
        model_fallback="google/gemma-4-31b-it:free",
        provider="openrouter",
        capabilities=["vedic astrology", "quranic study", "spiritual guidance", "meditation"],
        tools=["file_read", "file_write", "file_search"],
        max_concurrent=1,
        timeout=60,
    )

    class SpiritualAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the Spiritual Agent — Vedic astrology and Quranic study.

MAHI's Birth Data:
- March 6, 1996, 2:00 PM CET, El Bayadh, Algeria
- Ascendant: Gemini 21°31' (Punarvasu Nakshatra)
- Moon: Scorpio 5°50' (Anuradha Nakshatra)
- Sun: Aquarius 22°26' (Purva Bhadra Nakshatra)
- Current Dasha: Mercury (2018-2028)

Core Verses: Surah 21:87, 55:1-4, 68:1-4
Divine Names: Ya Hafiz, Ya Rahman, Ya Alim
MAHI Method: Morning (Fajr), Afternoon (ASR), Hour (Maghrib), Isha

Approach:
- Vedic sidereal astrology (not Western tropical)
- Quranic interpretation with context
- Practical spiritual guidance
- No superstition or fear-mongering
- Positive, actionable advice"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model)

    return SpiritualAgent(config)
