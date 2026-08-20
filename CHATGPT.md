# CHATGPT.md — MAHI Multi-Agent System Context

## Overview
MAHI (Multi-Agent Hub for Intelligent workflows) is a local multi-agent system for MAHI Kamel Abdelghani. It manages 10 specialized AI agents with shared tools, hooks, skills, and a 4-tier model router.

## Quick Start
1. Clone: `git clone https://github.com/kamelmh/mahi-multi-agent.git`
2. Install Python 3.14: `C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe`
3. Install hound: `pip install hound-mcp`
4. Run tests: `python -m pytest test_command_center.py`

## Architecture

### Agents (10)
| Agent | Purpose | Model |
|-------|---------|-------|
| code | Code generation, review, debugging | nemotron-3-nano-30b |
| code-pro | Complex architecture, system design | gpt-5.5-free |
| writing | Emails, proposals, UGC content | nemotron-3-super-120b |
| write-pro | Premium, high-stakes writing | gpt-5.5-free |
| quick | Fast responses, simple tasks | llama-3.3-70b (Groq) |
| career | Job applications, CV, cover letters | nemotron-3-super-120b |
| teaching | Education, exercises, assessments | nemotron-3-super-120b |
| dss | Academic decision support | nemotron-3-super-120b |
| research | Web research, analysis, summarization | nemotron-3-super-120b |
| spiritual | Spirituality, Quran, astrology | nemotron-3-super-120b |

### Model Router (4 tiers)
| Tier | Provider | Model | Speed |
|------|----------|-------|-------|
| Instant | Groq | llama-3.3-70b-versatile | <100ms |
| Normal | OpenRouter | nemotron-nano-12b | ~500ms |
| Quality | OpenRouter | nemotron-3-super-120b | ~2s |
| Context | Google | gemini-2.5-flash | ~3s |

### Tools
| Tool | File | Purpose |
|------|------|---------|
| file_search | tools/registry.py | Search files by name |
| pdf_extract | tools/registry.py | Extract text from PDFs |
| pdf_summarize | tools/registry.py | Summarize PDFs |
| web_search | tools/registry.py | Search web via hound CLI |
| scrape | tools/registry.py | Stealth web scraping (Scrapling) |

### Skills (7 installed)
| Skill | Location | Purpose |
|-------|----------|---------|
| brief-to-prompt | ~/.config/opencode/skills/ | Generate UGC prompts from product briefs |
| ugc-planner | ~/.config/opencode/skills/ | 7-day content campaign planner |
| claude-commands | ~/.config/opencode/skills/ | 50 power prompts for better output |
| brain-setup | ~/.config/opencode/skills/ | Bootstrap project memory |
| brain-page | ~/.config/opencode/skills/ | Create/update memory pages |
| brain-ingest | ~/.config/opencode/skills/ | Bulk knowledge ingestion |
| brain-bootstrap | ~/.config/opencode/skills/ | Seed real knowledge |

## Key Files

### Core
- `agents/base.py` — BaseAgent with tool registry, hooks, storage integration
- `tools/registry.py` — ToolRegistry with all tools
- `harness_router.py` — UHP-compatible server routing tasks to agents

### Agents
- `agents/code_agent.py` — Code agent with critical thinking prompts
- `agents/writing_agent.py` — Writing agent with UGC/UGC prompts
- `agents/research_agent.py` — Research agent with scrape tool
- `agents/career_agent.py` — Career agent for job applications
- `agents/teaching_agent.py` — Teaching agent for education

### Infrastructure
- `floci_integration.py` — S3 + DynamoDB local storage
- `mcp-hound.py` — Hound MCP wrapper (web search)
- `command_center.py` — Command center with hound integration
- `vibe_pipeline_v2.py` — 10-role parallel vibe pipeline

### UI
- `ui/gadget/dashboard_hub.py` — Dashboard Hub server
- `ui/gadget/index.html` — Polished hub UI (2,420+ lines)

### Brain
- `brain/pages/architecture.md` — System architecture
- `brain/pages/tools-registry.md` — Tool documentation
- `brain/pages/reference-repos.md` — Reference repos inventory
- `brain/pages/ai-creative-skills.md` — AI Creative OS skills

## Services
| Service | Port | Status |
|---------|------|--------|
| Dashboard Hub | 8000 | Ready |
| Harness Router (UHP) | 8600 | Ready |
| DeepSeek Harness | 8500 | Needs credits |
| SIS Ta'allim | 5000 | Ready |
| Academix DSS | 5173 | Ready |
| Teaching Platform | 8501 | Ready |

## Harness Router API
```
GET  /v1/uhp          — Protocol discovery
GET  /v1/harnesses    — List available harnesses
POST /v1/tasks        — Run a task {harness, task, session_id?}
GET  /v1/sessions/:id — Get session history
GET  /health          — Health check
```

## Git History
- `3faf413` — Wire AI Creative OS prompts into agent system prompts
- `45b2e22` — Add brain.md, harness router, scrapling, AI Creative OS skills
- `e585de4` — Wire full agent system (hooks, tools, skills, hound)
- `38419a9` — Expand model router with 4 tiers
- `27c3a0f` — Wire vibe pipeline to real MAHI agents

## Reference Repos (8)
| Repo | Stars | Purpose |
|------|-------|---------|
| xberg | 9.2k | Document extraction (101 formats) |
| Scrapling | 75.4k | Stealth web scraping (anti-bot) |
| Open-Sora | 29.3k | Video generation |
| olmocr | 19.4k | PDF-to-Markdown via VLM |
| smart-ralph | 519 | Spec-driven dev loop |
| brain.md | 492 | Persistent agent memory |
| autocache | 159 | Anthropic cache proxy |
| AgentsSwarms | Open | Multi-agent orchestration platform |

## Testing
```bash
# Run all tests
python -m pytest test_command_center.py -v

# Run specific test
python -m pytest test_command_center.py::test_tool_registry -v
```

## Environment
- Python: 3.14.6 (C:\Users\Admin\AppData\Local\Python\pythoncore-3.14-64\python.exe)
- Git Bash: C:\Program Files\Git\bin\bash.exe
- Working dir: C:\Users\Admin\projects\active\agents\mahi-multi-agent
- Data dir: C:\Users\Admin\My Drive\LifeWorkspace\

## Common Tasks

### Add a new tool
1. Add method to `tools/registry.py`
2. Add to `detect_intent()` tool set
3. Add `_tool_name()` method for run_tool
4. Add to agent config in `agents/*.py`

### Add a new agent
1. Create `agents/new_agent.py`
2. Define AgentConfig with model, tools, capabilities
3. Create class extending BaseAgent
4. Add to `agents/__init__.py`

### Add a new skill
1. Create `~/.config/opencode/skills/skill-name/SKILL.md`
2. Add to `opencode.jsonc` skills section
3. Test with trigger phrase

### Debug harness router
```bash
# Check health
curl http://127.0.0.1:8600/health

# List harnesses
curl http://127.0.0.1:8600/v1/harnesses

# Run task
curl -X POST http://127.0.0.1:8600/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"harness": "mahi-writing", "task": "Write a hello world"}'
```
