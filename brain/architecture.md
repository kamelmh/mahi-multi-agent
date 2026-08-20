---
slug: architecture
title: System architecture
role: system architecture
updated: "2026-08-20T10:35:13"
---

# System architecture

## Agents (10)
code, code-pro, writing, write-pro, quick, career, teaching, dss, research, spiritual

## Model Router (4 tiers)
- Instant: Groq (llama-3.3-70b-versatile)
- Normal: OpenRouter (nvidia/nemotron-nano-12b-a12b:free)
- Quality: OpenRouter (nvidia/nemotron-3-super-120b-a12b:free)
- Context: Google (gemini-2.5-flash)

## Tools
- file_search: Name search under directories
- pdf_extract: PyMuPDF text + metadata extraction
- pdf_summarize: First 300 chars summary
- web_search: Via hound CLI (keyless)
- scrape: Scrapling StealthyFetcher (anti-bot)

## Hooks
before_task, after_task, before_tool, after_tool, auto_save

## Skills
frontend-design, accessibility, seo (auto-injected when relevant)
