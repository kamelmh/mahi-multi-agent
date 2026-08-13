# Multica + MAHI Agent System

## Overview

This configuration integrates Multica (managed agents platform) with the MAHI multi-agent system.

## Agents (10)

| Agent | Squad | Purpose |
|-------|-------|---------|
| CodeAgent | CodeTeam | Python/VBA code generation |
| DSSAgent | CodeTeam | VBA/Excel DSS development |
| WriteAgent | ContentTeam | Long-form writing, documentation |
| ArabicAgent | ContentTeam | Arabic text, translation |
| ResearchAgent | ResearchTeam | Web research, analysis |
| SpiritualAgent | ResearchTeam | Astrology, spiritual practice |
| TeachingAgent | EducationTeam | Education content, curriculum |
| CareerAgent | CareerTeam | Freelancing, job applications |
| QuickAgent | — | Fast responses |
| OSSAgent | — | Complex reasoning |

## Squads (5)

| Squad | Leader | Members | Focus |
|-------|--------|---------|-------|
| CodeTeam | CodeAgent | CodeAgent, DSSAgent | All coding |
| ContentTeam | WriteAgent | WriteAgent, ArabicAgent | Writing, translation |
| ResearchTeam | ResearchAgent | ResearchAgent, SpiritualAgent | Research, astrology |
| EducationTeam | TeachingAgent | TeachingAgent | Education |
| CareerTeam | CareerAgent | CareerAgent | Career |

## Autopilots (3)

| Name | Schedule | Task |
|------|----------|------|
| DailyMemorySync | Daily 10 PM | Sync memory files |
| WeeklyReview | Sunday 10 AM | System review |
| TrainingStatusCheck | Monday 9 AM | Training status |

## Setup

```powershell
# 1. Install Multica
irm https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.ps1 | iex

# 2. Configure (interactive - opens browser)
multica setup

# 3. Create agents
multica agent create --name CodeAgent --runtime opencode
multica agent create --name WriteAgent --runtime opencode
# ... (see agents.json for full list)

# 4. Create squads
multica squad create --name CodeTeam --leader CodeAgent
# ... (see agents.json for full list)

# 5. Create autopilots
multica autopilot create --name DailyMemorySync --schedule "0 22 * * *"
# ... (see agents.json for full list)
```

## Files

| File | Purpose |
|------|---------|
| `agents.json` | Agent, squad, autopilot definitions |
| `README.md` | This file |

---

#multica #agents #squads #autopilots #MAHI
