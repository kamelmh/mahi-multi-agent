"""Task Classification Engine for MAHI Multi-Agent System."""
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class Classification:
    category: str
    agent_id: str
    model: str
    urgency: str
    confidence: float


# Category patterns: keyword → (category, agent_id, urgency)
# ORDER MATTERS: more specific patterns first
PATTERNS = [
    # CAREER tasks (check before writing to catch cover letters, CVs)
    (r"\b(cv|resume|portfolio|cover letter|linkedin)\b",
     "career.cv", "career", "normal"),
    (r"\b(apply|application|submit|job|position|role|hire)\b",
     "career.apply", "career", "normal"),

    # CODE tasks
    (r"\b(write|create|build|generate|make|code|function|class|script|implement)\b.*\b(code|python|javascript|typescript|function|class|script|program|api|endpoint)\b",
     "code.generate", "code", "normal"),
    (r"\b(review|check|audit|fix|debug|bug|error|issue|problem|fail|crash|broken)\b.*\b(code|script|function|program|error|output)\b",
     "code.review", "code", "normal"),
    (r"\b(refactor|optimize|improve|clean|restructure|simplify)\b.*\b(code|function|class|script)\b",
     "code.refactor", "code", "normal"),
    (r"\b(explain|how does|what does|walk through|trace)\b.*\b(code|function|class|script|this)\b",
     "code.explain", "code", "normal"),

    # WRITING tasks
    (r"\b(write|draft|compose|create)\b.*\b(email|message|reply|letter|note|memo)\b",
     "write.email", "write", "normal"),
    (r"\b(write|draft|compose|create)\b.*\b(proposal|bid|application)\b",
     "write.proposal", "write-pro", "normal"),
    (r"\b(write|draft|compose|create|make)\b.*\b(document|readme|guide|doc|documentation|report|article)\b",
     "write.docs", "write", "normal"),
    (r"\b(edit|proofread|rewrite|polish|improve)\b.*\b(text|paragraph|essay|document|email)\b",
     "write.edit", "write", "normal"),
    (r"\b(write|draft|compose|create)\b.*\b(paragraph|essay|summary|intro|conclusion|blog|story|content)\b",
     "write.docs", "write", "normal"),
    (r"\b(write|draft|compose)\b.*\b(short|brief|long|detailed|full)\b",
     "write.docs", "write", "normal"),

    # RESEARCH tasks
    (r"\b(search|find|look up|research|investigate|explore)\b",
     "research.find", "research", "normal"),
    (r"\b(analyze|compare|evaluate|assess|review)\b.*\b(option|choice|alternative|pros|cons|vs)\b",
     "research.analyze", "research", "normal"),

    # TEACHING tasks
    (r"\b(exercise|lesson|quiz|test|assessment|teach|grammar|vocabulary)\b",
     "teaching.create", "teaching", "normal"),
    (r"\b(grade|evaluate|score|feedback|correct)\b.*\b(answer|student|exercise)\b",
     "teaching.grade", "teaching", "normal"),

    # DSS tasks
    (r"\b(erp|vba|excel|academix|macro|spreadsheet|inventory|stock)\b",
     "dss.work", "dss", "normal"),

    # SPIRITUAL tasks
    (r"\b(astrology|chart|horoscope|natal|transit|nakshatra|quran|surah|ayah|spiritual|dhikr|ruqya)\b",
     "spiritual.read", "spiritual", "normal"),

    # QUICK tasks (simple questions)
    (r"^(what|how|why|when|where|who|is|are|can|do|does|will|should)\b.{0,30}\?$",
     "quick.ask", "quick", "instant"),
    (r"\b(convert|calculate|translate|define|meaning)\b",
     "quick.ask", "quick", "instant"),
]


def classify(user_input: str) -> Classification:
    """Classify user input and determine agent + model."""
    text = user_input.lower().strip()

    # Check each pattern
    for pattern, category, agent_id, urgency in PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            model = _select_model(agent_id, urgency)
            confidence = _calc_confidence(text, pattern)
            return Classification(
                category=category,
                agent_id=agent_id,
                model=model,
                urgency=urgency,
                confidence=confidence
            )

    # Default: quick agent for short, code agent for long
    if len(text.split()) < 10:
        return Classification(
            category="quick.ask",
            agent_id="quick",
            model="google/gemma-4-26b-a4b-it:free",
            urgency="instant",
            confidence=0.5
        )
    else:
        return Classification(
            category="code.generate",
            agent_id="code",
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            urgency="normal",
            confidence=0.4
        )


def _select_model(agent_id: str, urgency: str) -> str:
    """Select best model for agent + urgency.

    Model tiers (from awesome-free-llm-apis):
    - instant: fastest inference (Groq, Cerebras)
    - normal: balanced speed/quality (OpenRouter free tier)
    - quality: best output (larger models, direct APIs)
    - context: large context window (Google Gemini 1M)
    """
    MODELS = {
        # Tier 1: Instant — Groq/Cerebras for sub-second responses
        "instant": "groq/llama-3.3-70b-versatile",

        # Tier 2: Normal — OpenRouter free tier, balanced
        "normal": {
            "code": "nvidia/nemotron-3-nano-30b-a3b:free",
            "code-pro": "nvidia/nemotron-3-super-120b-a12b:free",
            "write": "nvidia/nemotron-3-nano-30b-a3b:free",
            "write-pro": "nvidia/nemotron-3-super-120b-a12b:free",
            "research": "nvidia/nemotron-3-nano-30b-a3b:free",
            "career": "nvidia/nemotron-3-nano-30b-a3b:free",
            "teaching": "nvidia/nemotron-3-nano-30b-a3b:free",
            "dss": "nvidia/nemotron-3-nano-30b-a3b:free",
            "spiritual": "google/gemma-4-26b-a4b-it:free",
            "quick": "google/gemma-4-26b-a4b-it:free",
        },

        # Tier 3: Quality — larger models for complex tasks
        "quality": "nvidia/nemotron-3-super-120b-a12b:free",

        # Tier 4: Context — 1M window for large documents
        "context": "google/gemini-2.5-flash",
    }

    if urgency == "instant":
        return MODELS["instant"]
    elif urgency == "quality":
        return MODELS["quality"]
    elif urgency == "context":
        return MODELS["context"]
    else:
        return MODELS["normal"].get(agent_id, "llama-3.3-70b-versatile")


def _calc_confidence(text: str, pattern: str) -> float:
    """Calculate confidence score based on match quality."""
    matches = re.findall(pattern, text, re.IGNORECASE)
    word_count = len(text.split())

    # More specific matches = higher confidence
    if len(matches) >= 2:
        return 0.95
    elif len(matches) == 1:
        # Short text with match = high confidence
        if word_count < 15:
            return 0.85
        return 0.75
    return 0.5
