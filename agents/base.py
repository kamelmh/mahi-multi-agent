"""Base Agent class for MAHI Multi-Agent System."""
from __future__ import annotations
import json
import time
import uuid
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Optional

MAHI_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIFEWORKSPACE = r"C:\Users\Admin\My Drive\LifeWorkspace"


class AgentState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    WAITING = "waiting"


class TaskState(Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Task:
    id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    user_input: str = ""
    category: str = ""
    agent_id: str = ""
    model: str = ""
    urgency: str = "normal"
    state: TaskState = TaskState.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    @property
    def elapsed(self) -> float:
        if self.started_at is None:
            return 0.0
        end = self.completed_at or time.time()
        return round(end - self.started_at, 2)

    def complete(self, result: str):
        self.result = result
        self.state = TaskState.COMPLETE
        self.completed_at = time.time()

    def fail(self, error: str):
        self.error = error
        self.state = TaskState.FAILED
        self.completed_at = time.time()

    def to_dict(self) -> dict:
        d = asdict(self)
        d["state"] = self.state.value
        return d


@dataclass
class AgentConfig:
    id: str
    name: str
    description: str
    model_primary: str
    model_fallback: str = ""
    model_premium: str = ""
    provider: str = "groq"
    capabilities: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    max_concurrent: int = 1
    timeout: int = 120
    system_prompt: str = ""


class BaseAgent(ABC):
    """Base class for all MAHI agents."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.active_tasks: dict[str, Task] = {}
        self.completed_tasks: list[Task] = []
        self._load_system_prompt()
        self._hooks = self._load_hooks()

    @property
    def id(self) -> str:
        return self.config.id

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_available(self) -> bool:
        return len(self.active_tasks) < self.config.max_concurrent

    def _load_system_prompt(self):
        """Load system prompt from config or use default."""
        if not self.config.system_prompt:
            self.config.system_prompt = self._default_system_prompt()

    def _load_hooks(self):
        """Load and register lifecycle hooks."""
        try:
            from hooks import HookManager, register_defaults
            hooks = HookManager()
            register_defaults(hooks)
            return hooks
        except ImportError:
            return None

    def _default_system_prompt(self) -> str:
        return (
            f"You are {self.config.name}, a specialized AI assistant.\n"
            f"Purpose: {self.config.description}\n"
            f"Be concise, accurate, and helpful."
        )

    def _tool_registry(self):
        """Lazy import of the shared ToolRegistry (avoids circular imports at module load)."""
        from tools.registry import ToolRegistry
        return ToolRegistry()

    def _try_use_tools(self, task_text: str) -> str | None:
        """Detect tool intent from task text, invoke the tool, and return formatted context."""
        try:
            reg = self._tool_registry()
            intents = reg.detect_intent(task_text)
            if not intents:
                return None
            parts = []
            for name, kwargs in intents:
                if self._hooks:
                    self._hooks.fire("before_tool", tool_name=name, kwargs=kwargs)
                result = reg.run_tool(name, **kwargs)
                if self._hooks:
                    self._hooks.fire("after_tool", tool_name=name, kwargs=kwargs, result=result)
                parts.append(f"### {name} result:\n```\n{json.dumps(result, ensure_ascii=False, indent=2)[:3000]}\n```")
            if not parts:
                return None
            return "\n\n".join(parts)
        except Exception:
            return None

    def _build_context(self, task: Task) -> list[dict]:
        """Build message list for API call."""
        messages = [{"role": "system", "content": self.config.system_prompt}]

        # Add session context if available
        session_file = os.path.join(LIFEWORKSPACE, ".session-state.json")
        if os.path.exists(session_file):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    session = json.load(f)
                ctx = f"User: {session.get('user', {}).get('name', 'MAHI')}"
                ctx += f"\nActive project: {session.get('active_project', 'None')}"
                messages.append({"role": "system", "content": ctx})
            except Exception:
                pass

        # Inject relevant skills into context
        try:
            from tools.skill_loader import load_relevant_skills
            skill_context = load_relevant_skills(task.user_input)
            if skill_context:
                messages.append(
                    {"role": "system", "content": f"Relevant skills (apply these patterns):\n{skill_context}"}
                )
        except ImportError:
            pass

        # Inject tool results if the task asks for them
        tool_context = self._try_use_tools(task.user_input)
        if tool_context:
            messages.append(
                {"role": "system", "content": f"Tool results (use them to answer):\n{tool_context}"}
            )

        messages.append({"role": "user", "content": task.user_input})
        return messages

    def _call_llm(self, messages: list[dict], model: str, max_tokens: int = 4096) -> str:
        """Call LLM via provider API with retry and fallback."""
        import urllib.request
        import urllib.error

        fallback_models = [
            "nvidia/nemotron-3-nano-30b-a3b:free",
            "google/gemma-4-26b-a4b-it:free",
        ]
        models_to_try = [model] + [m for m in fallback_models if m != model]

        last_error = None
        for try_model in models_to_try:
            for attempt in range(2):  # 2 attempts per model
                try:
                    provider = self._get_provider(try_model)
                    url = provider["base_url"] + "/chat/completions"
                    data = json.dumps({
                        "model": try_model,
                        "messages": messages,
                        "max_tokens": max_tokens
                    }).encode()

                    req = urllib.request.Request(
                        url,
                        data=data,
                        headers={
                            "Authorization": f"Bearer {provider['api_key']}",
                            "Content-Type": "application/json"
                        }
                    )

                    timeout = min(self.config.timeout, 45)  # Cap at 45s
                    resp = urllib.request.urlopen(req, timeout=timeout)
                    result = json.loads(resp.read())
                    return result["choices"][0]["message"]["content"]

                except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, Exception) as e:
                    last_error = e
                    if attempt == 0:
                        import time
                        time.sleep(2)  # Wait before retry
                    continue

        raise Exception(f"All models failed: {last_error}")

    def _get_provider(self, model: str) -> dict:
        """Get provider config for a model."""
        providers = {
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": os.environ.get("OPENROUTER_API_KEY", "")
            },
            "aihubmix": {
                "base_url": "https://aihubmix.com/v1",
                "api_key": os.environ.get("OPENAI_API_KEY", "")
            },
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "api_key": os.environ.get("GROQ_API_KEY", "")
            },
        }

        # Auto-detect provider from model name
        if "openai/" in model or "google/" in model or "nvidia/" in model or "qwen/" in model or "deepseek/" in model or "meta-llama/" in model:
            return providers["openrouter"]
        elif "gpt-5" in model or "gpt-4" in model:
            return providers["aihubmix"]
        else:
            return providers["openrouter"]  # Default to OpenRouter

    def _storage(self):
        """Lazy import of Floci storage (avoids circular imports)."""
        from floci_integration import get_storage
        return get_storage()

    def _save_output(self, task_id: str, output: str) -> dict:
        """Save agent output to S3 (or local fallback)."""
        try:
            storage = self._storage()
            return storage.save_agent_output(self.id, task_id, output)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _load_output(self, task_id: str) -> Optional[dict]:
        """Load agent output from S3 (or local fallback)."""
        try:
            storage = self._storage()
            return storage.load_agent_output(self.id, task_id)
        except Exception:
            return None

    def _save_session(self, session_id: str, data: dict) -> dict:
        """Save session data to DynamoDB (or local fallback)."""
        try:
            storage = self._storage()
            return storage.sessions.save(session_id, data)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _load_session(self, session_id: str) -> Optional[dict]:
        """Load session data from DynamoDB (or local fallback)."""
        try:
            storage = self._storage()
            return storage.sessions.load(session_id)
        except Exception:
            return None

    @abstractmethod
    def execute(self, task: Task) -> str:
        """Execute a task and return the result. Must be implemented by subclasses."""
        ...

    def run(self, task: Task) -> Task:
        """Run a task through this agent."""
        task.state = TaskState.RUNNING
        task.started_at = time.time()
        self.state = AgentState.RUNNING
        self.active_tasks[task.id] = task

        if self._hooks:
            self._hooks.fire("before_task", task=task, agent=self)

        try:
            result = self.execute(task)
            task.complete(result)
        except Exception as e:
            task.fail(str(e))
        finally:
            self.active_tasks.pop(task.id, None)
            self.completed_tasks.append(task)
            self.state = AgentState.IDLE

        if self._hooks:
            self._hooks.fire("after_task", task=task, agent=self)

        return task

    def get_status(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state.value,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "model": self.config.model_primary,
        }
