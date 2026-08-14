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
├── mcp-*.py         # MCP servers (obsidian, session-intel, command-center, mahi)
├── ui/gadget/       # Web dashboard (18 tabs) — absorbed from lifeworkspace-gadget
├── brain/           # Knowledge: system-design-notes, session analysis
├── tools/pdf-tools/ # PDF utilities — absorbed from lifeworkspace-pdf-tools
└── orchestration/   # Automation (journal, session autosave, weekly review)
```

## Absorbed Projects (2026-08-14)

| Absorbed | Origin | New home |
|----------|--------|----------|
| Gadget dashboard | `docs/lifeworkspace-gadget` (local repo) | `ui/gadget/` |
| System design notes | `research/system-design-notes` (local repo) | `brain/system-design-notes/` |
| PDF tools | `libs/lifeworkspace-pdf-tools` (GitHub, archived) | `tools/pdf-tools/` |
| Automation scripts | `libs/dev-toolkit/automation` | `orchestration/` |

## License

Private — MAHI Kamel Abdelghani
