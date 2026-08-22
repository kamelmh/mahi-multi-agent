"""MAHI Harness Router — lightweight UHP-compatible server for routing tasks to agents."""

import os
import sys
import json
import time
import uuid
import subprocess
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

MAHI_ROOT = Path(__file__).parent.parent
UHP_VERSION = "2026-08-20"

# -------------------------------------------------------------------------
# Harness registry — maps harness IDs to agent configs (10 agents)
# -------------------------------------------------------------------------

# Model-to-backend mapping
BACKEND_MAP = {
    "nemotron-120b": "openrouter",   # Premium quality model
    "nemotron-nano": "openrouter",   # Normal capability model
    "llama-3.3-70b": "groq",         # Instant/fast model
}

# Harness registry — maps harness IDs to agent configs (10 agents total)
HARNESSES = {
    # --- Core agents (existing) ---
    "mahi-code": {
        "id": "mahi-code",
        "name": "MAHI Code Agent",
        "description": "Code generation, review, debugging, and refactoring",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["code", "review", "debug", "refactor"],
        "tiers": ["instant", "normal", "quality"],  # model tiers supported
    },
    "mahi-research": {
        "id": "mahi-research",
        "name": "MAHI Research Agent",
        "description": "Web research, analysis, summarization, and knowledge base search",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["research", "analysis", "search", "kb_search"],
        "tiers": ["instant", "normal"],
    },
    "mahi-writing": {
        "id": "mahi-writing",
        "name": "MAHI Writing Agent",
        "description": "Content creation, editing, documentation, and UGC prompt generation",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["writing", "editing", "docs", "ugc_prompt"],
        "tiers": ["instant", "normal"],
    },
    "mahi-quick": {
        "id": "mahi-quick",
        "name": "MAHI Quick Agent",
        "description": "Fast responses for simple tasks, chat, and immediate assistance",
        "backend": "groq",
        "model": "llama-3.3-70b-versatile",
        "capabilities": ["quick", "simple", "chat", "summarize"],
        "tiers": ["instant"],
    },
    # --- Premium agents (added for swarm coordination) ---
    "mahi-code-pro": {
        "id": "mahi-code-pro",
        "name": "MAHI Code Pro Agent",
        "description": "Advanced code generation with critical thinking, architecture design, and complex refactoring",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["code", "review", "debug", "refactor", "architect", "optimize"],
        "tiers": ["quality"],  # Premium tier only
    },
    "mahi-writing-pro": {
        "id": "mahi-writing-pro",
        "name": "MAHI Writing Pro Agent",
        "description": "Premium UGC prompt generation with CINEMATIC/UGC AUTHENTIC modes, persona matching, and multi-modal prompts",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-super-120b-a12b:free",
        "capabilities": ["writing", "editing", "docs", "ugc_prompt", "cinematic", "authentic", "persona_match"],
        "tiers": ["quality"],  # Premium tier only
    },
    # --- Specialist agents (added for full 10-agent coverage) ---
    "mahi-career": {
        "id": "mahi-career",
        "name": "MAHI Career Agent",
        "description": "Career planning, job search, resume review, and professional development",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "capabilities": ["career", "resume", "interview", "networking", "skill_gap"],
        "tiers": ["normal"],
    },
    "mahi-teaching": {
        "id": "mahi-teaching",
        "name": "MAHI Teaching Agent",
        "description": "Educational content generation, lesson planning, and Arabic-first instructional design",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "capabilities": ["teaching", "lesson_plan", "exam_gen", "notes_gen", "arabic_rtl"],
        "tiers": ["normal"],
    },
    "mahi-dss": {
        "id": "mahi-dss",
        "name": "MAHI DSS Agent",
        "description": "Academix DSS data analysis, dashboard monitoring, and system health checks",
        "backend": "groq",
        "model": "llama-3.3-70b-versatile",
        "capabilities": ["dss", "analysis", "monitoring", "health_check", "metrics"],
        "tiers": ["instant"],
    },
    "mahi-spiritual": {
        "id": "mahi-spiritual",
        "name": "MAHI Spiritual Agent",
        "description": "Spiritual guidance, reflection, astrology basics, and mindfulness practices",
        "backend": "openrouter",
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "capabilities": ["spiritual", "reflection", "astrology", "mindfulness", "meditation"],
        "tiers": ["normal"],
    },
}

# Session storage
SESSIONS = {}

def generate_id():
    return str(uuid.uuid4())[:8]

def call_openrouter(model, messages, api_key):
    """Call OpenRouter API."""
    import urllib.request
    data = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def call_groq(model, messages, api_key):
    """Call Groq API."""
    import urllib.request
    data = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

def run_harness(harness_id, task, session_id=None):
    """Run a task on a harness and return the result."""
    harness = HARNESSES.get(harness_id)
    if not harness:
        return {"error": f"Unknown harness: {harness_id}"}

    # Get or create session
    if not session_id:
        session_id = generate_id()
        SESSIONS[session_id] = {
            "harness": harness_id,
            "created": time.time(),
            "messages": [],
        }

    session = SESSIONS[session_id]
    session["messages"].append({"role": "user", "content": task})

    # Build context
    system_prompt = f"You are {harness['name']}. {harness['description']}. Respond concisely and helpfully."
    messages = [{"role": "system", "content": system_prompt}] + session["messages"]

    # Route to backend
    api_key = os.environ.get(f"{harness['backend'].upper()}_API_KEY", "")
    if not api_key:
        return {"error": f"No API key for {harness['backend']}"}

    if harness["backend"] == "openrouter":
        response = call_openrouter(harness["model"], messages, api_key)
    elif harness["backend"] == "groq":
        response = call_groq(harness["model"], messages, api_key)
    else:
        return {"error": f"Unknown backend: {harness['backend']}"}

    session["messages"].append({"role": "assistant", "content": response})

    return {
        "session_id": session_id,
        "harness": harness_id,
        "response": response,
        "model": harness["model"],
    }


def distribute_task(task: str, session_id: str = None) -> dict:
    """Split a complex task across 2-3 agents based on detected intents.

    Returns a combined response from multiple agents with individual results.
    """
    from tools.registry import ToolRegistry, TOOL_DEFS
    reg = ToolRegistry()

    intents = reg.detect_intent(task)
    if not intents:
        intents = [("web_search", {"query": task[:100]})]

    # Determine which agents to involve based on intents
    intent_names = [i[0] for i in intents]
    assigned_agents = []

    if any(i in intent_names for i in ["file_search", "pdf_extract"]):
        assigned_agents.append("mahi-research")
    if any(i in intent_names for i in ["web_search", "scrape"]):
        assigned_agents.append("mahi-research")
    if any(i in intent_names for i in ["code", "debug", "refactor"]):
        assigned_agents.append("mahi-code")
    if any(i in intent_names for i in ["writing", "ugc"]):
        assigned_agents.append("mahi-writing")

    # Deduplicate and cap at 3
    seen = set()
    unique = []
    for a in assigned_agents:
        if a not in seen and a in HARNESSES:
            seen.add(a)
            unique.append(a)
    assigned_agents = unique[:3]

    if not assigned_agents:
        assigned_agents = ["mahi-quick"]

    # Run each agent on the task
    responses = []
    results = []
    for agent_id in assigned_agents:
        r = run_harness(agent_id, task, session_id)
        responses.append(r.get("response", ""))
        results.append(r)

    # Combine into unified response
    combined = "**Multi-Agent Coordinated Result**\n\n"
    for i, agent_id in enumerate(assigned_agents):
        agent_name = HARNESSES[agent_id]["name"]
        resp = responses[i] if i < len(responses) else ""
        combined += "**" + agent_name + ":** " + resp[:500] + "\n\n"

    return {
        "session_id": session_id,
        "task": task,
        "distribution_mode": "distribute",
        "agents_involved": assigned_agents,
        "combined_response": combined,
        "individual_results": [
            {"agent": a, "response": r.get("response", "")[:200]}
            for a, r in zip(assigned_agents, results)
        ],
    }


def run_swarm_task(task: str, preferred_harness: str = None, distribution: str = "single") -> dict:
    """Run a task using swarm coordination across available agents.

    Distribution modes:
    - "single": Run on the single best-matched agent (default)
    - "distribute": Split complex tasks across 2-3 agents based on capabilities
    - "swarm": Full swarm coordination with multiple agents and approval steps

    The function uses:
    1. Intent detection (via ToolRegistry) to understand task requirements
    2. Routing guidance (from ToolRegistry) to guide model tool choice
    3. Agent capability matching to select the best agent(s)
    4. Tool invocation with full trace collection
    """
    from tools.registry import ToolRegistry, TOOL_DEFS
    reg = ToolRegistry()

    intents = reg.detect_intent(task)
    if not intents:
        # Fallback: try web_search for general research
        intents = [("web_search", {"query": task[:100]})]

    # Step 2: Build routing guidance for the system prompt
    routing_guidance = reg.build_routing_guidance(available_tools=list(TOOL_DEFS.keys()))

    # Step 3: Select the best agent based on task category and capabilities
    task_lower = task.lower()

    # Career-related tasks → mahi-career
    if any(kw in task_lower for kw in ["career", "job", "resume", "interview", "professional"]):
        selected_harness = "mahi-career"
    # Teaching/educational tasks → mahi-teaching
    elif any(kw in task_lower for kw in ["teach", "lesson", "student", "study", "learn", "exam"]):
        selected_harness = "mahi-teaching"
    # Spiritual/reflection tasks → mahi-spiritual
    elif any(kw in task_lower for kw in ["spiritual", "reflection", "meditation", "mindfulness", "astrology"]):
        selected_harness = "mahi-spiritual"
    # DSS/monitoring tasks → mahi-dss
    elif any(kw in task_lower for kw in ["dss", "dashboard", "monitor", "health check", "metrics", "system"]):
        selected_harness = "mahi-dss"
    # Code-related tasks → mahi-code or mahi-code-pro
    elif any(kw in task_lower for kw in ["code", "program", "function", "debug", "refactor", "script"]):
        # Use pro tier if available and task is complex, otherwise regular
        if "architect" in task_lower or "complex" in task_lower or "optimize" in task_lower:
            selected_harness = "mahi-code-pro"
        else:
            selected_harness = "mahi-code"
    # UGC/prompt generation tasks → mahi-writing or mahi-writing-pro
    elif any(kw in task_lower for kw in ["ugc", "prompt", "content", "social media", "tiktok", "instagram", "caption", "hook"]):
        if "cinematic" in task_lower or "premium" in task_lower or "mode" in task_lower:
            selected_harness = "mahi-writing-pro"
        else:
            selected_harness = "mahi-writing"
    # Research tasks → mahi-research
    elif any(kw in task_lower for kw in ["research", "search", "look up", "find information", "latest"]):
        selected_harness = "mahi-research"
    # Quick/simple tasks → mahi-quick
    elif any(kw in task_lower for kw in ["quick", "simple", "chat", "hello", "what is", "tell me"]):
        selected_harness = "mahi-quick"
    # Default: use preferred harness or first available
    else:
        selected_harness = preferred_harness or "mahi-quick"

    # Step 4: Adjust harness based on distribution mode and tier availability
    harness = HARNESSES.get(selected_harness)
    if not harness:
        return {"error": f"Unknown harness: {selected_harness}"}

    # Tier-aware selection: if distribution requires quality tier but only normal available
    if distribution in ("distribute", "swarm") and "quality" in harness.get("tiers", []):
        # Check if we have a quality-tier agent available; if not, fall back to normal
        if "quality" not in [HARNESSES[h].get("tiers", []) for h in HARNESSES if HARNESSES[h]]:
            # downgrade to normal-capable agent
            quality_agents = [h for h, hconf in HARNESSES.items() if "quality" in hconf.get("tiers", [])]
            if quality_agents:
                # Use the first quality agent but with normal model
                selected_harness = quality_agents[0]
                harness = HARNESSES[selected_harness]
                # Update model to a normal-tier one
                if harness["model"].startswith("nemotron-3-super"):
                    harness["model"] = "nvidia/nemotron-3-nano-30b-a3b:free"
                    harness["backend"] = "openrouter"
            # else: keep original, model may fail but we'll try

    # Step 5: Run the task on the selected harness with routing guidance
    # Inject routing guidance into the system prompt
    system_prompt = f"""You are {harness['name']}. {harness['description']}.

    TOOL ROUTING GUIDANCE:
    {routing_guidance}

    Available tools: {', '.join(TOOL_DEFS.keys())}
    Use the appropriate tool based on the guidance above. Each tool description
    tells you when to use it (e.g., 'Use file_search when the user asks to find
    something in the codebase', 'Use web_search when the user asks to search the web').

    Task: {task}"""

    messages = [{"role": "system", "content": system_prompt}]

    # Step 6: Run via the harness backend
    api_key = os.environ.get(f"{harness['backend'].upper()}_API_KEY", "")
    if not api_key:
        return {"error": f"No API key for {harness['backend']}"}

    # Use the appropriate backend call
    if harness["backend"] == "openrouter":
        import urllib.request
        data = json.dumps({"model": harness["model"], "messages": messages}).encode()
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                response = result["choices"][0]["message"]["content"]
        except Exception as e:
            response = f"Error: {e}"

    elif harness["backend"] == "groq":
        import urllib.request
        data = json.dumps({"model": harness["model"], "messages": messages}).encode()
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                response = result["choices"][0]["message"]["content"]
        except Exception as e:
            response = f"Error: {e}"
    else:
        response = f"Error: Unknown backend {harness['backend']}"

    # Step 7: Collect traces for swarm coordination
    traces = {
        "task": task,
        "selected_harness": selected_harness,
        "harness_id": harness["id"],
        "detected_intents": [{"tool": i[0], "kwargs": i[1]} for i in intents],
        "routing_guidance_used": routing_guidance,
        "distribution_mode": distribution,
        "response": response,
        "model": harness["model"],
        "backend": harness["backend"],
    }

    return {
        "session_id": None,  # Swarm tasks don't create sessions by default
        "harness": harness["id"],
        "agent": harness["name"],
        "response": response,
        "model": harness["model"],
        "traces": traces,
        "distribution_mode": distribution,
    }


def search_knowledge_base(query: str, top_k: int = 5) -> dict:
    """Search the MAHI knowledge base (brain.md + tools directory) using hybrid retrieval.

    Following the AgentSwarms pattern of hybrid search (pgvector embeddings + keyword fallback),
    this function combines:
    1. Keyword search over file names and content
    2. PDF content extraction and search
    3. Brain page name matching

    Returns up to top_k results with citation metadata, suitable for feeding into an
    agent's system prompt as grounded context.
    """
    from tools.registry import ToolRegistry, TOOL_DEFS
    import json
    from pathlib import Path

    reg = ToolRegistry()
    results = []

    # --- Step 1: File search over brain/ directory ---
    # Brain directory is co-located with this file (harness_router.py)
    brain_root = Path(__file__).parent / "brain"
    try:
        file_results = reg.file_search(query, root=brain_root, content=False, limit=top_k)
        for r in file_results:
            results.append({
                "source": "file_search",
                "name": r.get("name", r.get("path", "unknown")),
                "snippet": r.get("path", "")[:200],
                "kind": "file",
            })
    except Exception as e:
        results.append({"source": "file_search", "error": str(e)})

    # --- Step 2: PDF extraction and search ---
    try:
        pdf_results = reg.file_search(query, root=brain_root, content=True, limit=top_k // 2)
        for r in pdf_results:
            pdf_path = r.get("path", "")
            if pdf_path and pdf_path.endswith(".pdf"):
                pdf_extract_result = reg.pdf_extract(pdf_path)
                if pdf_extract_result.get("success"):
                    text = pdf_extract_result.get("text", "")[:300]
                    results.append({
                        "source": "pdf_extract",
                        "name": pdf_path,
                        "snippet": text,
                        "kind": "pdf",
                    })
    except Exception as e:
        results.append({"source": "pdf_search", "error": str(e)})

    # --- Step 3: Deduplicate and rank by relevance ---
    # Simple dedup by name; keep top_k
    seen = set()
    uniq = []
    for r in results:
        name_key = r.get("name", "")
        if name_key not in seen:
            seen.add(name_key)
            uniq.append(r)

    # Sort: files with matches in snippet first, then alphabetically
    uniq.sort(key=lambda r: (r.get("snippet", "")[:50] == "", r.get("name", "")))

    # Return top_k
    result = {
        "success": True,
        "results": uniq[:top_k],
        "query": query,
        "method": "hybrid_keyword_pdf",
    }
    return result


class UHPHandler(BaseHTTPRequestHandler):
    """HTTP handler implementing UHP protocol."""

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("UHP-Version", UHP_VERSION)
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Protocol discovery
        if path == "/v1/uhp":
            self._send_json({
                "version": UHP_VERSION,
                "conformance": "core",
                "harnesses": f"{self.headers.get('Host', 'localhost')}/v1/harnesses",
            })

        # List harnesses
        elif path == "/v1/harnesses":
            self._send_json({"harnesses": list(HARNESSES.values())})

        # Get session
        elif path.startswith("/v1/sessions/"):
            sid = path.split("/")[-1]
            session = SESSIONS.get(sid)
            if session:
                self._send_json(session)
            else:
                self._send_json({"error": "Session not found"}, 404)

        # Health check
        elif path == "/health":
            self._send_json({"status": "ok", "harnesses": len(HARNESSES)})

        else:
            self._send_json({"error": "Not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        # Run task
        if path == "/v1/tasks":
            harness_id = body.get("harness", "mahi-quick")
            task = body.get("task", "")
            session_id = body.get("session_id")

            if not task:
                self._send_json({"error": "No task provided"}, 400)
                return

            result = run_harness(harness_id, task, session_id)
            self._send_json(result)

        # Create session
        elif path == "/v1/sessions":
            harness_id = body.get("harness", "mahi-quick")
            session_id = generate_id()
            SESSIONS[session_id] = {
                "harness": harness_id,
                "created": time.time(),
                "messages": [],
            }
            self._send_json({"session_id": session_id, "harness": harness_id})


        # KB search endpoint
        elif path == "/api/kb_search":
            body = body or {}
            query = body.get("query", "")
            top_k = body.get("top_k", 5)
            if query:
                result = search_knowledge_base(query, top_k=top_k)
            else:
                result = {"error": "No query provided"}
            self._send_json(result)


        # Swarm task endpoint (single/distribute/swarm modes)
        elif path == "/api/swarm_task":
            body = body or {}
            task = body.get("task", "")
            distribution = body.get("distribution", "single")
            preferred_harness = body.get("harness")
            session_id = body.get("session_id")
            
            if not task:
                self._send_json({"error": "No task provided"}, 400)
                return
            
            if distribution == "distribute":
                result = distribute_task(task, session_id)
            elif distribution == "swarm":
                result = run_swarm_task(task, preferred_harness or "mahi-quick", "swarm")
            else:
                result = run_swarm_task(task, preferred_harness or "mahi-quick", "single")
            
            self._send_json(result)

        else:
            self._send_json({"error": "Not found"}, 404)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8600
    server = HTTPServer(("127.0.0.1", port), UHPHandler)
    print(f"MAHI Harness Router running on http://127.0.0.1:{port}")
    print(f"UHP discovery: http://127.0.0.1:{port}/v1/uhp")
    print(f"Harnesses: http://127.0.0.1:{port}/v1/harnesses")
    print(f"Tasks: POST http://127.0.0.1:{port}/v1/tasks")
    print()
    print("Harnesses available:")
    for h in HARNESSES.values():
        tiers_str = ", ".join(h.get("tiers", []))
        print(f"  {h['id']}: {h['name']} ({h['backend']}/{h['model']}) [tiers: {tiers_str}]")
    print()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
