#!/usr/bin/env node
/**
 * Session Intelligence MCP Server for OpenCode
 */
const fs = require("fs");
const path = require("path");

const STATE_FILE = path.join("C:", "Users", "Admin", "My Drive", "LifeWorkspace", ".session-state.json");
const SESSIONS_DIR = path.join("C:", "Users", "Admin", "My Drive", "LifeWorkspace", "15_Advanced_Tools", "sessions");

function loadState() {
  try { return JSON.parse(fs.readFileSync(STATE_FILE, "utf-8")); } catch { return {}; }
}

function loadSessions() {
  const indexFile = path.join(SESSIONS_DIR, "index.json");
  try { return JSON.parse(fs.readFileSync(indexFile, "utf-8")).sessions || []; } catch { return []; }
}

function analyze() {
  const state = loadState();
  const sessions = loadSessions();
  const projects = {};
  const decisions = state.recent_decisions || [];

  for (const s of sessions) {
    const p = s.active_project || "unknown";
    projects[p] = (projects[p] || 0) + 1;
  }

  return {
    timestamp: new Date().toISOString(),
    session_state_loaded: Object.keys(state).length > 0,
    archived_sessions: sessions.length,
    active_project: state.active_project || "none",
    projects,
    recent_decisions_count: decisions.length,
    pending_tasks: (state.pending_tasks || []).length,
  };
}

function recommendations() {
  const state = loadState();
  const recs = [];
  const tasks = state.pending_tasks || [];
  if (tasks.length > 0) recs.push(`You have ${tasks.length} pending tasks`);
  if (state.active_project) recs.push(`Active project: ${state.active_project}`);
  if (!state.last_session) recs.push("No recent session found");
  if (tasks.length === 0 && !state.active_project) recs.push("All clear — consider starting a new task");
  return recs;
}

const TOOLS = [
  { name: "session_analyze", description: "Analyze session patterns and detect trends", inputSchema: { type: "object", properties: {} } },
  { name: "session_recommendations", description: "Get recommendations based on session history", inputSchema: { type: "object", properties: {} } },
  { name: "session_state", description: "Get current session state", inputSchema: { type: "object", properties: {} } },
];

function handle(req) {
  const { method, params, id } = req;
  if (method === "initialize") return { jsonrpc: "2.0", id, result: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "session-intel", version: "1.0.0" } } };
  if (method === "notifications/initialized") return null;
  if (method === "tools/list") return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  if (method === "tools/call") {
    const { name } = params;
    try {
      let result;
      if (name === "session_analyze") result = analyze();
      else if (name === "session_recommendations") result = recommendations();
      else if (name === "session_state") result = loadState();
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
