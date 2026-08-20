---
id: architecture
title: MAHI Architecture
category: decision
status: active
tags: [architecture, multi-agent]
created: "2026-08-20T10:32:34"
updated: "2026-08-20T10:34:51"
---

<!-- compiled_truth -->
MAHI (Multi-Agent Hub for Intelligent workflows) is a local multi-agent system. 10 agents: code, code-pro, writing, write-pro, quick, career, teaching, dss, research, spiritual. 4-tier model router: Instant (Groq), Normal (OpenRouter), Quality (OpenRouter), Context (Gemini). Tools: file_search, pdf_extract, web_search, scrape (Scrapling). Hooks: before_task, after_task, before_tool, after_tool, auto_save. Skills: frontend-design, accessibility, seo. Storage: Floci (S3+DynamoDB local) with JSON fallback.


## Timeline

- time: 2026-08-20T10:32:34
  kind: decision
  summary: "Created this page: MAHI Architecture"
  source: created via brain create-page
  affects: [architecture]

- time: 2026-08-20T10:34:51
  kind: decision
  summary: Initial MAHI architecture documentation
  source: brain update-truth
  affects: [architecture]
