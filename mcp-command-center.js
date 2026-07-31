#!/usr/bin/env node
/**
 * Command Center MCP Server for OpenCode
 */
const fs = require("fs");
const path = require("path");

function checkSystems() {
  const systems = {};
  const checks = [
    ["mahi-multi-agent", "C:\\Users\\Admin\\MAHI\\agents\\base.py"],
    ["obsidian-vault", "C:\\Users\\Admin\\My Drive\\LifeWorkspace\\00-Brain-Map.md"],
    ["context-engine", "C:\\Users\\Admin\\context-engine\\knowledge-graph.json"],
    ["session-intelligence", "C:\\Users\\Admin\\automation\\session-intelligence\\agent.py"],
    ["freelance-responder", "C:\\Users\\Admin\\automation\\freelance-responder\\responder.py"],
    ["astrology-notifier", "C:\\Users\\Admin\\automation\\astrology-notifier\\notifier.py"],
    ["opencode-config", "C:\\Users\\Admin\\.config\\opencode\\opencode.jsonc"],
  ];

  for (const [name, p] of checks) {
    systems[name] = fs.existsSync(p) ? "available" : "missing";
  }
  return systems;
}

function health() {
  const systems = checkSystems();
  const available = Object.values(systems).filter(v => v === "available").length;
  const total = Object.keys(systems).length;
  return { timestamp: new Date().toISOString(), systems, health: `${available}/${total} systems available`, available, total };
}

const TOOLS = [
  { name: "system_health", description: "Get health status of all MAHI systems", inputSchema: { type: "object", properties: {} } },
  { name: "system_status", description: "Get detailed status of all systems", inputSchema: { type: "object", properties: {} } },
];

function handle(req) {
  const { method, params, id } = req;
  if (method === "initialize") return { jsonrpc: "2.0", id, result: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "command-center", version: "1.0.0" } } };
  if (method === "notifications/initialized") return null;
  if (method === "tools/list") return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  if (method === "tools/call") {
    const { name } = params;
    try {
      let result;
      if (name === "system_health") result = health();
      else if (name === "system_status") result = checkSystems();
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
