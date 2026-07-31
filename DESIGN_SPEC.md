# MAHI Multi-Agent Launcher — Design Spec

> **Version:** 2.0
> **Date:** 2026-07-18
> **Status:** Design Phase
> **Author:** MAHI Kamel Abdelghani

---

## 1. Vision

Transform the current single-menu batch launcher into a **structured multi-agent orchestration system** where specialized AI agents handle specific tasks, coordinate through a central hub, and present a unified interface.

**Current State:** `MAHI.bat` — 236-line batch file, 4 menus, manual selection
**Target State:** Multi-agent launcher with task routing, parallel execution, and unified dashboard

---

## 2. Architecture

### 2.1 System Layers

```
┌─────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│  Terminal UI │ Web Dashboard │ CLI Commands │ Voice  │
├─────────────────────────────────────────────────────┤
│                   ROUTING LAYER                      │
│  Task Classifier │ Agent Matcher │ Load Balancer     │
├─────────────────────────────────────────────────────┤
│                    AGENT LAYER                       │
│  Code Agent │ Writing Agent │ Research Agent │ ...   │
├─────────────────────────────────────────────────────┤
│                  ORCHESTRATION LAYER                 │
│  Task Queue │ State Manager │ Context Handler        │
├─────────────────────────────────────────────────────┤
│                   PROVIDER LAYER                     │
│  Groq │ AIHubMix │ Cloudflare │ Ollama │ Anthropic   │
├─────────────────────────────────────────────────────┤
│                    DATA LAYER                        │
│  LifeWorkspace │ Projects │ Config │ Session State   │
└─────────────────────────────────────────────────────┘
```

### 2.2 Directory Structure

```
C:\Users\Admin\MAHI\
├── launcher\
│   ├── MAHI.bat              # Legacy launcher (keep for compatibility)
│   ├── MAHI.ps1              # PowerShell launcher (current)
│   └── MAHI.py               # NEW: Python orchestrator (main entry)
├── agents\
│   ├── __init__.py
│   ├── base.py               # BaseAgent class
│   ├── code_agent.py         # Code generation, review, debugging
│   ├── writing_agent.py      # Emails, proposals, documentation
│   ├── research_agent.py     # Web search, analysis, summarization
│   ├── career_agent.py       # CV, cover letters, job applications
│   ├── teaching_agent.py     # Education content, exercises, grading
│   ├── dss_agent.py          # ERP, VBA, data analysis
│   └── spiritual_agent.py    # Astrology, Quranic study
├── router\
│   ├── __init__.py
│   ├── classifier.py         # Task classification engine
│   ├── matcher.py            # Agent-task matching
│   └── models.json           # Model routing rules
├── orchestrator\
│   ├── __init__.py
│   ├── engine.py             # Task queue, execution, state
│   ├── context.py            # Context management
│   └── state.json            # Persistent state
├── ui\
│   ├── terminal.py           # Rich terminal UI
│   ├── dashboard.py          # Web dashboard (optional)
│   └── templates\            # UI templates
├── config\
│   ├── agents.json           # Agent definitions
│   ├── providers.json        # Provider configs
│   └── settings.json         # Global settings
├── logs\
│   └── sessions\             # Session logs
└── README.md
```

---

## 3. Agent Definitions

### 3.1 Agent Registry

| Agent ID | Name | Role | Primary Model | Provider | Tools |
|----------|------|------|---------------|----------|-------|
| `code` | Code Agent | Code generation, review, debug | GPT-OSS 20B | Groq | File I/O, Git, Terminal |
| `code-pro` | Code Pro | Complex architecture, refactoring | GPT-5.5-free | AIHubMix | File I/O, Git, Terminal |
| `write` | Writing Agent | Emails, proposals, docs | Llama 3.3 70B | Groq | File I/O, Templates |
| `write-pro` | Writing Pro | Client-facing, publications | GPT-5.5-free | AIHubMix | File I/O, Templates |
| `research` | Research Agent | Web search, analysis | GLM 5.2 | Cloudflare | Web Search, File I/O |
| `career` | Career Agent | CV, jobs, applications | Llama 3.3 70B | Groq | File I/O, Web |
| `teaching` | Teaching Agent | Education content | GPT-OSS 20B | Groq | File I/O, Templates |
| `dss` | DSS Agent | ERP, VBA, data analysis | GPT-OSS 120B | Groq | File I/O, Excel |
| `spiritual` | Spiritual Agent | Astrology, Quran | Allam 2 7B | Groq | File I/O |
| `quick` | Quick Agent | Simple questions | Llama 3.1 8B | Groq | None |
| `local` | Local Agent | Privacy-sensitive | Phi-4 Mini | Ollama | File I/O |

### 3.2 Agent Capabilities Matrix

```
Agent          │ Code │ Write │ Research │ Career │ Teach │ DSS │ Spiritual │ Speed │ Cost
───────────────┼──────┼───────┼──────────┼────────┼───────┼─────┼───────────┼───────┼──────
code           │ ★★★  │ ☆     │ ☆        │ ☆      │ ☆     │ ★★  │ ☆         │ Fast  │ Free
code-pro       │ ★★★★ │ ☆     │ ☆        │ ☆      │ ☆     │ ★★★ │ ☆         │ Slow  │ Free*
write          │ ☆    │ ★★★   │ ☆        │ ★★     │ ★★    │ ☆   │ ☆         │ Med   │ Free
write-pro      │ ☆    │ ★★★★  │ ☆        │ ★★★    │ ★★    │ ☆   │ ☆         │ Slow  │ Free*
research       │ ★    │ ★★    │ ★★★      │ ★      │ ★★    │ ☆   │ ★         │ Med   │ Free
career         │ ☆    │ ★★★   │ ★★       │ ★★★    │ ★     │ ☆   │ ☆         │ Med   │ Free
teaching       │ ★★   │ ★★    │ ★        │ ☆      │ ★★★   │ ☆   │ ☆         │ Med   │ Free
dss            │ ★★★  │ ☆     │ ☆        │ ☆      │ ☆     │ ★★★★│ ☆         │ Med   │ Free
spiritual      │ ☆    │ ☆     │ ★        │ ☆      │ ☆     │ ☆   │ ★★★       │ Fast  │ Free
quick          │ ☆    │ ☆     │ ☆        │ ☆      │ ☆     │ ☆   │ ☆         │ ★★★★★ │ Free
local          │ ★    │ ★     │ ☆        │ ☆      │ ☆     │ ★   │ ☆         │ Slow  │ Free

★ = capability level (☆=none, ★=basic, ★★=good, ★★★=great, ★★★★=excellent, ★★★★★=fastest)
Free* = AIHubMix (10-try limit without credit)
```

### 3.3 Agent Definition Format

```json
{
  "id": "code",
  "name": "Code Agent",
  "description": "Code generation, review, and debugging",
  "model": {
    "primary": "groq/gpt-oss-20b",
    "fallback": "cloudflare/glm-5.2",
    "premium": "aihubmix/gpt-5.5-free"
  },
  "capabilities": ["code generation", "code review", "debugging", "refactoring"],
  "tools": ["file_read", "file_write", "terminal", "git"],
  "context": {
    "max_tokens": 8192,
    "system_prompt": "You are an expert software engineer...",
    "knowledge_files": ["AGENTS.md", "coding-standards.md"]
  },
  "limits": {
    "max_concurrent": 2,
    "timeout_seconds": 120,
    "daily_requests": "unlimited"
  }
}
```

---

## 4. Task Classification Engine

### 4.1 Task Categories

| Category | Keywords | Default Agent | Fallback |
|----------|----------|---------------|----------|
| `code.generate` | write, create, build, function, class | `code` | `code-pro` |
| `code.review` | review, check, audit, fix, bug | `code` | `dss` |
| `code.debug` | error, crash, debug, trace, why | `code` | `code-pro` |
| `write.email` | email, message, reply, draft | `write` | `write-pro` |
| `write.proposal` | proposal, bid, cover letter | `write-pro` | `career` |
| `write.docs` | document, readme, guide, doc | `write` | `write-pro` |
| `research.find` | search, find, look up, research | `research` | `quick` |
| `research.analyze` | analyze, compare, evaluate | `research` | `code` |
| `career.apply` | apply, application, job | `career` | `write-pro` |
| `career.cv` | cv, resume, portfolio | `career` | `write-pro` |
| `teaching.create` | exercise, lesson, quiz, teach | `teaching` | `write` |
| `dss.work` | erp, vba, excel, academix | `dss` | `code` |
| `spiritual.read` | astrology, quran, spiritual | `spiritual` | `quick` |
| `quick.ask` | what, how, why, simple | `quick` | `local` |

### 4.2 Classification Algorithm

```python
def classify_task(user_input: str) -> TaskClassification:
    """
    1. Tokenize and extract keywords
    2. Match against category patterns
    3. Check urgency (simple → quick agent)
    4. Check complexity (simple → code agent, complex → code-pro)
    5. Check privacy (sensitive → local agent)
    6. Return classification with confidence score
    """
    tokens = tokenize(user_input)
    
    # Pattern matching
    for category, patterns in CATEGORY_PATTERNS.items():
        score = match_patterns(tokens, patterns)
        if score > THRESHOLD:
            agent = select_agent(category, complexity, privacy)
            return TaskClassification(
                category=category,
                agent=agent,
                confidence=score,
                model=select_model(agent, urgency)
            )
    
    # Default: quick agent for simple, code agent for complex
    return default_classification(user_input)
```

### 4.3 Model Selection Logic

```python
def select_model(agent_id: str, urgency: str) -> str:
    """
    Urgency levels:
    - instant: Need answer now (quick agent, Llama 3.1 8B)
    - normal: Standard work (agent primary model)
    - quality: Best result (premium model, 10-try limit)
    - privacy: Sensitive data (local model, Ollama)
    """
    agent = get_agent(agent_id)
    
    if urgency == "instant":
        return "groq/llama-3.1-8b-instant"
    elif urgency == "privacy":
        return "ollama/phi4-mini"
    elif urgency == "quality":
        return agent.model.premium
    else:
        return agent.model.primary
```

---

## 5. Orchestrator Engine

### 5.1 Task Queue

```python
class TaskQueue:
    """
    Manages task execution with priorities and dependencies.
    
    States: PENDING → QUEUED → RUNNING → COMPLETE/FAILED
    """
    def __init__(self):
        self.tasks: List[Task] = []
        self.running: Dict[str, Task] = {}
        self.max_concurrent = 3
    
    def submit(self, task: Task) -> str:
        """Submit task, returns task_id"""
        task.state = "QUEUED"
        self.tasks.append(task)
        self.process_queue()
        return task.id
    
    def process_queue(self):
        """Start tasks if under concurrent limit"""
        while len(self.running) < self.max_concurrent:
            task = self.get_next()
            if not task:
                break
            self.execute(task)
    
    def execute(self, task: Task):
        """Run task with appropriate agent"""
        agent = get_agent(task.agent_id)
        self.running[task.id] = task
        task.state = "RUNNING"
        
        # Run in thread (non-blocking)
        Thread(target=agent.run, args=(task,)).start()
```

### 5.2 Context Management

```python
class ContextManager:
    """
    Manages context across agent sessions.
    
    - Loads relevant LifeWorkspace files
    - Passes session state
    - Handles inter-agent communication
    """
    def build_context(self, task: Task) -> dict:
        context = {
            "user": load_user_profile(),
            "session": load_session_state(),
            "workspace": load_workspace_context(),
            "task_history": get_recent_tasks(),
            "files": load_relevant_files(task.category)
        }
        return context
```

### 5.3 State Management

```json
{
  "version": "2.0",
  "started_at": "2026-07-18T10:00:00Z",
  "active_tasks": [
    {
      "id": "task_001",
      "category": "code.generate",
      "agent": "code",
      "model": "groq/gpt-oss-20b",
      "state": "RUNNING",
      "started_at": "2026-07-18T10:01:00Z",
      "progress": 0.45
    }
  ],
  "completed_today": 12,
  "agents_used": {
    "code": 5,
    "write": 3,
    "quick": 4
  },
  "model_usage": {
    "groq/llama-3.1-8b-instant": 15,
    "groq/gpt-oss-20b": 8,
    "aihubmix/gpt-5.5-free": 2
  }
}
```

---

## 6. UI/UX Design

### 6.1 Terminal UI (Primary)

```
╔══════════════════════════════════════════════════════════╗
║               M A H I   S Y S T E M   v2.0              ║
║               Multi-Agent Orchestrator                   ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  ┌─ TASK INPUT ─────────────────────────────────────┐   ║
║  │ > Write a Python function to parse CSV files     │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  ┌─ CLASSIFICATION ─────────────────────────────────┐   ║
║  │ Category:  code.generate                          │   ║
║  │ Agent:     Code Agent (GPT-OSS 20B)               │   ║
║  │ Model:     groq/gpt-oss-20b                       │   ║
║  │ Urgency:   normal                                 │   ║
║  │ Confidence: 95%                                   │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  ┌─ ACTIVE AGENTS ──────────────────────────────────┐   ║
║  │ 🟢 Code Agent    │ task_001 │ 45% │ 12s elapsed  │   ║
║  │ 🟡 Writing Agent │ task_002 │ 80% │ 25s elapsed  │   ║
║  │ ⚪ Research Agent│  idle    │     │              │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  ┌─ QUICK ACTIONS ──────────────────────────────────┐   ║
║  │ [1] Code Task    [4] Research    [7] DSS/ERP     │   ║
║  │ [2] Write Task   [5] Career      [8] Teaching     │   ║
║  │ [3] Quick Ask    [6] Spiritual   [9] Dashboard    │   ║
║  │                                                    │   ║
║  │ [S] Status  [L] Logs  [H] History  [0] Exit       │   ║
║  └──────────────────────────────────────────────────┘   ║
║                                                          ║
║  Models: Groq(unlimited) │ AIHubMix(8/10) │ Ollama(free)║
╚══════════════════════════════════════════════════════════╝
```

### 6.2 Workflow Modes

#### Mode 1: Interactive (Default)
- User types task → System classifies → Agent executes → Result shown
- Best for: Ad-hoc work, exploration

#### Mode 2: Batch
- User provides list of tasks → System queues → Agents process → Results collected
- Best for: Bulk operations, repetitive work

#### Mode 3: Autonomous
- User defines goals → System plans → Agents execute → User reviews
- Best for: Complex projects, multi-step workflows

#### Mode 4: Dashboard
- Web-based UI showing all agents, tasks, and status
- Best for: Monitoring, management

---

## 7. Integration Points

### 7.1 LifeWorkspace Integration

```python
LIFEWORKSPACE_PATH = r"C:\Users\Admin\My Drive\LifeWorkspace"

INTEGRATIONS = {
    "brain_map": f"{LIFEWORKSPACE_PATH}/00-Brain-Map.md",
    "session_state": f"{LIFEWORKSPACE_PATH}/.session-state.json",
    "skills": f"{LIFEWORKSPACE_PATH}/02_Skills_&_Development/",
    "career": f"{LIFEWORKSPACE_PATH}/03_Career_&_Planning/",
    "projects": f"{LIFEWORKSPACE_PATH}/04_Ideas_&_Projects/",
    "education": f"{LIFEWORKSPACE_PATH}/10_Education_Project/",
    "tools": f"{LIFEWORKSPACE_PATH}/15_Advanced_Tools/"
}
```

### 7.2 Provider Integration

| Provider | API Key Location | Models | Cost |
|----------|-----------------|--------|------|
| Groq | User env var | Llama 3.1/3.3, GPT-OSS | Free unlimited |
| AIHubMix | User env var | GPT-5.5, GPT-4.1, GLM | Free 10-try, paid |
| Cloudflare | opencode.jsonc | GLM 5.2, GLM 4.7 | Free unlimited |
| Ollama | Local | Phi-4, Gemma, Qwen | Free unlimited |
| OpenRouter | User env var | DeepSeek V4 | Free tier |

### 7.3 Tool Integration

| Tool | Access | Used By |
|------|--------|---------|
| Git | CLI | Code Agent |
| Python | CLI | All agents |
| VS Code | CLI | Code, DSS agents |
| Obsidian | URI | All agents |
| Browser | URI | Research, Career |
| Excel | COM | DSS Agent |

---

## 8. Implementation Plan

### Phase 1: Core Engine (Day 1)
- [ ] Create `MAHI/agents/base.py` — BaseAgent class
- [ ] Create `MAHI/agents/code_agent.py` — Code agent implementation
- [ ] Create `MAHI/agents/quick_agent.py` — Quick agent implementation
- [ ] Create `MAHI/router/classifier.py` — Task classification
- [ ] Create `MAHI/orchestrator/engine.py` — Task queue
- [ ] Create `MAHI/MAHI.py` — Main entry point

### Phase 2: All Agents (Day 2)
- [ ] Create all 11 agent implementations
- [ ] Configure model routing for each
- [ ] Add tool integrations
- [ ] Test each agent individually

### Phase 3: UI & UX (Day 3)
- [ ] Build terminal UI with Rich library
- [ ] Add progress bars and status display
- [ ] Implement task history and logging
- [ ] Add keyboard shortcuts and aliases

### Phase 4: Integration (Day 4)
- [ ] Connect to LifeWorkspace
- [ ] Add session persistence
- [ ] Update MAHI System desktop shortcut
- [ ] Create README and usage guide

### Phase 5: Polish (Day 5)
- [ ] Add error handling and recovery
- [ ] Performance optimization
- [ ] Add configuration UI
- [ ] Documentation

---

## 9. Dependencies

```txt
# requirements.txt
rich>=13.0          # Terminal UI
prompt_toolkit>=3.0 # Input handling
aiohttp>=3.9        # Async HTTP
psutil>=5.9         # System monitoring
watchdog>=3.0       # File watching
```

---

## 10. Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Time to task | 30s (manual menu) | 5s (auto-classify) |
| Agent utilization | 1 agent at a time | 3 parallel agents |
| Model efficiency | Always same model | Right model per task |
| Error recovery | Manual restart | Auto-retry + fallback |
| Context persistence | None | Session-aware |

---

## 11. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| API rate limits | Task fails | Fallback to other provider |
| Agent crashes | Task lost | Auto-retry, state saved |
| Model quality | Bad output | Confidence threshold, review |
| Resource usage | Slow system | Concurrent limit, timeouts |
| Security | Data leak | Local model for sensitive |

---

## 12. Future Enhancements

- **Voice Interface:** "Hey MAHI, write a cover letter for..."
- **Mobile Dashboard:** Monitor agents from phone
- **Auto-learning:** Track which models work best for which tasks
- **Agent marketplace:** Add new agents from community
- **Multi-user:** Support for team collaboration
- **Cloud sync:** Run agents on cloud VMs

---

**Next Steps:** Approve design → Start Phase 1 implementation
