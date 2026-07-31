#!/usr/bin/env node
/**
 * MAHI Multi-Agent MCP Server for OpenCode
 */
const { execSync } = require("child_process");

function route(input) {
  const text = input.toLowerCase();
  const patterns = [
    [/\b(write|create|build|generate|code|function|class|script|implement)\b.*\b(code|python|javascript|function|class|script)\b/i, "code.generate", "code", 0.85],
    [/\b(review|check|audit|fix|debug|bug|error)\b.*\b(code|script|function)\b/i, "code.review", "code", 0.85],
    [/\b(write|draft|compose|create)\b.*\b(email|message|letter|note)\b/i, "write.email", "write", 0.85],
    [/\b(write|draft|compose|create)\b.*\b(proposal|cover letter|application)\b/i, "write.proposal", "write", 0.85],
    [/\b(search|find|look up|research|investigate)\b/i, "research.find", "research", 0.85],
    [/\b(apply|application|submit|job|position|cv|resume|portfolio|linkedin)\b/i, "career.apply", "career", 0.85],
    [/\b(exercise|lesson|quiz|test|assessment|teach|grammar|vocabulary)\b/i, "teaching.create", "teaching", 0.85],
    [/\b(erp|vba|excel|academix|macro|inventory|stock)\b/i, "dss.work", "dss", 0.85],
    [/\b(astrology|chart|horoscope|natal|transit|nakshatra|quran|surah|spiritual|dhikr)\b/i, "spiritual.read", "spiritual", 0.85],
  ];

  for (const [re, cat, agent, conf] of patterns) {
    if (re.test(text)) {
      const models = { code: "nvidia/nemotron-3-nano-30b-a3b:free", write: "nvidia/nemotron-3-super-120b-a12b:free", research: "nvidia/nemotron-3-super-120b-a12b:free", career: "nvidia/nemotron-3-super-120b-a12b:free", teaching: "nvidia/nemotron-3-nano-30b-a3b:free", dss: "nvidia/nemotron-3-super-120b-a12b:free", spiritual: "google/gemma-4-26b-a4b-it:free" };
      return { category: cat, agent, model: models[agent] || "google/gemma-4-26b-a4b-it:free", confidence: conf, urgency: "normal" };
    }
  }
  return text.split(/\s+/).length < 10
    ? { category: "quick.ask", agent: "quick", model: "google/gemma-4-26b-a4b-it:free", confidence: 0.5, urgency: "instant" }
    : { category: "code.generate", agent: "code", model: "nvidia/nemotron-3-nano-30b-a3b:free", confidence: 0.4, urgency: "normal" };
}

const AGENTS = [
  { id: "code", name: "Code Agent", model: "nvidia/nemotron-3-nano-30b-a3b:free" },
  { id: "write", name: "Writing Agent", model: "nvidia/nemotron-3-super-120b-a12b:free" },
  { id: "research", name: "Research Agent", model: "nvidia/nemotron-3-super-120b-a12b:free" },
  { id: "career", name: "Career Agent", model: "nvidia/nemotron-3-super-120b-a12b:free" },
  { id: "teaching", name: "Teaching Agent", model: "nvidia/nemotron-3-nano-30b-a3b:free" },
  { id: "dss", name: "DSS Agent", model: "nvidia/nemotron-3-super-120b-a12b:free" },
  { id: "spiritual", name: "Spiritual Agent", model: "google/gemma-4-26b-a4b-it:free" },
  { id: "quick", name: "Quick Agent", model: "google/gemma-4-26b-a4b-it:free" },
];

const TOOLS = [
  { name: "mahi_route", description: "Route a task to the appropriate MAHI agent", inputSchema: { type: "object", properties: { input: { type: "string" } }, required: ["input"] } },
  { name: "mahi_agents", description: "List all MAHI agents and their status", inputSchema: { type: "object", properties: {} } },
  { name: "mahi_status", description: "Get MAHI orchestrator status", inputSchema: { type: "object", properties: {} } },
];

function handle(req) {
  const { method, params, id } = req;
  if (method === "initialize") return { jsonrpc: "2.0", id, result: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "mahi", version: "1.0.0" } } };
  if (method === "notifications/initialized") return null;
  if (method === "tools/list") return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  if (method === "tools/call") {
    const { name, arguments: args } = params;
    try {
      let result;
      if (name === "mahi_route") result = route(args.input);
      else if (name === "mahi_agents") result = AGENTS;
      else if (name === "mahi_status") result = { agents: AGENTS.length, queue: 0, active: 0, completed: 0 };
      else return { jsonrpc: "2.0", id, error: { code: -32601, message: `Unknown tool: ${name}` } };
      return { jsonrpc: "2.0", id, result: { content: [{ type: "text", text: JSON.stringify(result, null, 2) }] } };
    } catch (e) { return { jsonrpc: "2.0", id, error: { code: -32000, message: e.message } }; }
  }
  return { jsonrpc: "2.0", id, error: { code: -32601, message: `Unknown method: ${method}` } };
}

process.stdin.setEncoding("utf-8");
let buf = "";
process.stdin.on("data", (chunk) => {
  buf += chunk;
  const lines = buf.split("\n");
  buf = lines.pop();
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try { const req = JSON.parse(trimmed); const resp = handle(req); if (resp) process.stdout.write(JSON.stringify(resp) + "\n"); } catch {}
  }
});
