#!/usr/bin/env node
/**
 * Obsidian MCP Server for OpenCode
 */
const fs = require("fs");
const path = require("path");

const VAULT = path.join("C:", "Users", "Admin", "My Drive", "LifeWorkspace");

function searchNotes(query, limit = 10) {
  const results = [];
  const q = query.toLowerCase();

  function walk(dir) {
    try {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory() && !entry.name.startsWith(".")) {
          walk(full);
        } else if (entry.isFile() && entry.name.endsWith(".md")) {
          try {
            const content = fs.readFileSync(full, "utf-8");
            if (content.toLowerCase().includes(q) || entry.name.toLowerCase().includes(q)) {
              const rel = path.relative(VAULT, full).replace(/\\/g, "/");
              results.push({ path: rel, name: entry.name.replace(".md", ""), snippet: content.slice(0, 200).replace(/\n/g, " ").trim() });
              if (results.length >= limit) return;
            }
          } catch {}
        }
      }
    } catch {}
  }
  walk(VAULT);
  return results;
}

function readNote(p) {
  const full = path.join(VAULT, p);
  if (fs.existsSync(full)) return fs.readFileSync(full, "utf-8");
  return `Note not found: ${p}`;
}

function createNote(p, content) {
  const full = path.join(VAULT, p);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, content, "utf-8");
  return `Created: ${p}`;
}

function updateNote(p, content) {
  const full = path.join(VAULT, p);
  if (fs.existsSync(full)) {
    fs.writeFileSync(full, content, "utf-8");
    return `Updated: ${p}`;
  }
  return `Note not found: ${p}`;
}

function listNotes(dir = "") {
  const dirPath = path.join(VAULT, dir);
  const notes = [];
  try {
    for (const entry of fs.readdirSync(dirPath, { withFileTypes: true })) {
      const rel = path.relative(VAULT, path.join(dirPath, entry.name)).replace(/\\/g, "/");
      notes.push({ name: entry.name, path: rel, type: entry.isDirectory() ? "directory" : "file" });
    }
  } catch {}
  return notes;
}

function getStats() {
  let md = 0, pdf = 0, size = 0;
  function walk(dir) {
    try {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory() && !entry.name.startsWith(".")) walk(full);
        else if (entry.isFile()) {
          const s = fs.statSync(full).size;
          size += s;
          if (entry.name.endsWith(".md")) md++;
          else if (entry.name.endsWith(".pdf")) pdf++;
        }
      }
    } catch {}
  }
  walk(VAULT);
  return { total_md: md, total_pdf: pdf, total_size_mb: Math.round(size / 1048576), vault_path: VAULT };
}

const TOOLS = [
  { name: "obsidian_search", description: "Search notes in Obsidian vault by keyword", inputSchema: { type: "object", properties: { query: { type: "string" }, limit: { type: "integer", default: 10 } }, required: ["query"] } },
  { name: "obsidian_read", description: "Read a specific note from Obsidian vault", inputSchema: { type: "object", properties: { path: { type: "string" } }, required: ["path"] } },
  { name: "obsidian_create", description: "Create a new note in Obsidian vault", inputSchema: { type: "object", properties: { path: { type: "string" }, content: { type: "string" } }, required: ["path", "content"] } },
  { name: "obsidian_update", description: "Update an existing note in Obsidian vault", inputSchema: { type: "object", properties: { path: { type: "string" }, content: { type: "string" } }, required: ["path", "content"] } },
  { name: "obsidian_list", description: "List notes in Obsidian vault directory", inputSchema: { type: "object", properties: { directory: { type: "string" } } } },
  { name: "obsidian_stats", description: "Get Obsidian vault statistics", inputSchema: { type: "object", properties: {} } },
];

function handle(req) {
  const { method, params, id } = req;
  if (method === "initialize") return { jsonrpc: "2.0", id, result: { protocolVersion: "2024-11-05", capabilities: { tools: {} }, serverInfo: { name: "obsidian", version: "1.0.0" } } };
  if (method === "notifications/initialized") return null;
  if (method === "tools/list") return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  if (method === "tools/call") {
    const { name, arguments: args } = params;
    try {
      let result;
      if (name === "obsidian_search") result = searchNotes(args.query, args.limit);
      else if (name === "obsidian_read") result = readNote(args.path);
      else if (name === "obsidian_create") result = createNote(args.path, args.content);
      else if (name === "obsidian_update") result = updateNote(args.path, args.content);
      else if (name === "obsidian_list") result = listNotes(args.directory);
      else if (name === "obsidian_stats") result = getStats();
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
    try {
      const req = JSON.parse(trimmed);
      const resp = handle(req);
      if (resp) { process.stdout.write(JSON.stringify(resp) + "\n"); }
    } catch {}
  }
});
