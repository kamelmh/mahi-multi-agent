# MAHI Multi-Agent System

10 specialized AI agents with intelligent routing for MAHI Kamel Abdelghani's projects.

## Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `/code` | nemotron-3-nano | Code generation |
| `/write` | nemotron-3-nano | Writing tasks |
| `/quick` | gemma-4-26b | Simple questions |
| `/career` | nemotron-3-nano | CV, cover letters |
| `/teaching` | nemotron-3-nano | Exercises, curriculum |
| `/dss` | nemotron-3-nano | Academix ERP, VBA |
| `/research` | nemotron-3-nano | Analysis, comparison |
| `/spiritual` | gemma-4-26b | Astrology, Quran |
| `/arabic` | nemotron-3-nano | Arabic text |

## Quick Start

```bash
# Single task
python MAHI.py --task "write a python function to calculate factorial"

# Interactive mode
python MAHI.py

# Status
python MAHI.py --status
```

## Project Routing

Tasks are automatically classified and routed to the best agent:
- "write a cover letter" → Career Agent
- "create a B1 exercise" → Teaching Agent
- "explain CMUP formula" → DSS Agent
- "what is 2+2?" → Quick Agent

## Architecture

```
MAHI.py              # Entry point
├── router/          # Task classification
│   └── classifier.py
├── orchestrator/    # Task execution
│   └── engine.py
├── agents/          # 10 specialized agents
│   ├── base.py
│   ├── code_agent.py
│   ├── writing_agent.py
│   ├── quick_agent.py
│   ├── career_agent.py
│   ├── teaching_agent.py
│   ├── dss_agent.py
│   ├── research_agent.py
│   ├── spiritual_agent.py
│   └── ...
├── mcp-*.py         # CLI tools (obsidian, session-intel, command-center)
└── context-engine/  # Session analysis + knowledge graph
```

## License

Private — MAHI Kamel Abdelghani
