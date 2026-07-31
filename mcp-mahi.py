"""
MAHI Multi-Agent MCP Server for OpenCode
Routes tasks to specialized agents.
"""
import sys
import os
import json

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add MAHI to path
sys.path.insert(0, r"C:\Users\Admin\MAHI")

from router.classifier import classify
from orchestrator.engine import Orchestrator
from agents.base import Task


# Import all agent creators
from agents.code_agent import create_code_agent
from agents.writing_agent import create_writing_agent
from agents.research_agent import create_research_agent
from agents.career_agent import create_career_agent
from agents.teaching_agent import create_teaching_agent
from agents.dss_agent import create_dss_agent
from agents.spiritual_agent import create_spiritual_agent
from agents.quick_agent import create_quick_agent


# Initialize orchestrator
orchestrator = Orchestrator()
for creator in [create_code_agent, create_writing_agent, create_research_agent,
                create_career_agent, create_teaching_agent, create_dss_agent,
                create_spiritual_agent, create_quick_agent]:
    orchestrator.register_agent(creator())


def route_task(user_input: str) -> dict:
    """Classify and route a task."""
    classification = classify(user_input)
    return {
        "category": classification.category,
        "agent": classification.agent_id,
        "model": classification.model,
        "confidence": classification.confidence,
        "urgency": classification.urgency,
    }


def get_agent_status() -> list:
    """Get status of all agents."""
    agents = []
    for agent_id, agent in orchestrator.agents.items():
        agents.append({
            "id": agent.id,
            "name": agent.name,
            "model": agent.config.model_primary,
            "state": agent.state.value,
        })
    return agents


def get_orchestrator_status() -> dict:
    """Get orchestrator status."""
    return {
        "agents": len(orchestrator.agents),
        "queue": len(orchestrator.task_queue),
        "active": len(orchestrator.active_tasks),
        "completed": len(orchestrator.completed_tasks),
    }


# MCP Protocol Handler
def handle_request(request: dict) -> dict:
    """Handle MCP JSON-RPC request."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "mahi-multi-agent", "version": "1.0.0"},
            },
        }

    elif method == "notifications/initialized":
        return None

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "mahi_route",
                        "description": "Route a task to the appropriate MAHI agent (code, writing, research, career, teaching, dss, spiritual, quick)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "input": {"type": "string", "description": "Task description"},
                            },
                            "required": ["input"],
                        },
                    },
                    {
                        "name": "mahi_agents",
                        "description": "List all MAHI agents and their status",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "mahi_status",
                        "description": "Get MAHI orchestrator status",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                ]
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "mahi_route":
                result = route_task(arguments["input"])
            elif tool_name == "mahi_agents":
                result = get_agent_status()
            elif tool_name == "mahi_status":
                result = get_orchestrator_status()
            else:
                return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}}

            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32000, "message": str(e)}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Run MCP server via stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            if response is not None:
                print(json.dumps(response, ensure_ascii=False))
                sys.stdout.flush()
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
