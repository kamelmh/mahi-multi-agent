# MAHI Vibe Coding — Build Anything in One Session

> Inspired by: Google Cloud engineer building a complete app with Claude in 26 minutes (no team, no prior setup)

## The Vision

One person + MAHI = complete software team. Describe what you want → MAHI routes to the right agents → assemble the result.

## The 5-Role Pipeline

```
User Input (text/voice/screenshot)
    │
    ▼
┌─────────────────┐
│  1. PM AGENT     │  /write agent
│  Multimodal      │  Reads specs, screenshots, voice
│  Output: PRD     │  Generates requirements doc
└────────┬────────┘
         │ handoff (PRD.md)
         ▼
┌─────────────────┐
│  2. UI/UX AGENT  │  gadget + frontend-design skill
│  Plan Mode       │  Figma MCP (future)
│  Output: HTML    │  Generates working UI
└────────┬────────┘
         │ handoff (index.html)
         ▼
┌─────────────────┐
│  3. CODE AGENT   │  /code agent + subagents
│  Skills + MCP    │  DevDoc, Google Cloud MCP
│  Output: Python  │  Builds backend/logic
└────────┬────────┘
         │ handoff (app.py)
         ▼
┌─────────────────┐
│  4. SECURITY     │  security-review skill
│  Plugins + Hooks │  Validates before deploy
│  Output: PASS    │  Checks secrets, input, auth
└────────┬────────┘
         │ handoff (security-pass.md)
         ▼
┌─────────────────┐
│  5. GROWTH       │  /career + /research agents
│  BigQuery MCP    │  Generates pitch, docs, SEO
│  Output: LAUNCH  │  Ready to ship
└─────────────────┘
```

## Current MAHI vs Target

| Role | Current MAHI | What's Missing | Priority |
|------|-------------|----------------|----------|
| PM | `/write` agent exists | PRD template, voice input | High |
| UI/UX | gadget exists, frontend-design skill installed | Plan mode, Figma MCP | Medium |
| Code | `/code` agent exists | Subagent orchestration, DevDoc MCP | High |
| Security | security-review skill exists | Plugins, hooks, automated checks | Medium |
| Growth | `/career` + `/research` exist | BigQuery MCP, launch checklist | Low |

## MVP: Wire the Existing Pieces

### Phase 1: PRD Pipeline (PM → Code)
1. Create PRD template in `brain/templates/`
2. Wire `/write` agent to generate PRD from user description
3. Wire `/code` agent to read PRD and build

### Phase 2: Security Gate
1. Add security-review skill to code agent pipeline
2. Create hooks that auto-run security checks before "deploy"

### Phase 3: Growth Output
1. Wire `/career` agent to generate launch pitch
2. Wire `/research` agent to generate market analysis

## How to Use (Future State)

```bash
# Describe what you want
python MAHI.py --vibe "Build a task management app with auth, 
                       real-time updates, and a dashboard"

# MAHI runs the full pipeline:
# 1. PM generates PRD
# 2. UI/UX generates dashboard HTML
# 3. Code builds backend
# 4. Security validates
# 5. Growth generates pitch deck

# Output: complete app + docs + pitch
```

## Key Insight from the Video

The Google Cloud engineer didn't write code manually. He:
1. **Described** what he wanted (multimodal input)
2. **Let Claude route** to the right tools (Skills, MCP, Subagents)
3. **Assembled** the result from agent outputs

MAHI already has 10 agents. The missing piece is the **pipeline** that connects them in sequence with handoffs.

---

**Created:** 2026-08-15
**Status:** Design Phase
**Next:** Implement Phase 1 (PRD Pipeline)
