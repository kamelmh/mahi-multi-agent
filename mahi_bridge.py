"""
MAHI → OpenCode Bridge
Routes OpenCode tasks through MAHI's classifier and agents.
"""
import sys
import os

# Add MAHI to path
sys.path.insert(0, str(Path(__file__).parent))

from router.classifier import classify
from agents.code_agent import create_code_agent
from agents.writing_agent import create_writing_agent
from agents.research_agent import create_research_agent
from agents.career_agent import create_career_agent
from agents.teaching_agent import create_teaching_agent
from agents.dss_agent import create_dss_agent
from agents.spiritual_agent import create_spiritual_agent
from agents.quick_agent import create_quick_agent
from orchestrator.engine import Orchestrator
from agents.base import Task


class MAHIBridge:
    """Bridge between OpenCode and MAHI Multi-Agent System."""

    def __init__(self):
        self.orchestrator = Orchestrator()
        self._register_agents()

    def _register_agents(self):
        """Register all MAHI agents."""
        agents = [
            create_code_agent(),
            create_writing_agent(),
            create_research_agent(),
            create_career_agent(),
            create_teaching_agent(),
            create_dss_agent(),
            create_spiritual_agent(),
            create_quick_agent(),
        ]
        for agent in agents:
            self.orchestrator.register_agent(agent)

    def route(self, user_input: str) -> dict:
        """Classify input and route to appropriate agent."""
        classification = classify(user_input)

        task = Task(
            user_input=user_input,
            category=classification.category,
            agent_id=classification.agent_id,
            model=classification.model,
            urgency=classification.urgency,
        )

        # Submit to orchestrator
        self.orchestrator.submit(task)

        return {
            "category": classification.category,
            "agent": classification.agent_id,
            "model": classification.model,
            "confidence": classification.confidence,
            "urgency": classification.urgency,
        }

    def get_status(self) -> dict:
        """Get orchestrator status."""
        return {
            "agents": len(self.orchestrator.agents),
            "queue": len(self.orchestrator.task_queue),
            "active": len(self.orchestrator.active_tasks),
            "completed": len(self.orchestrator.completed_tasks),
        }


def main():
    """CLI interface for MAHI bridge."""
    if len(sys.argv) < 2:
        print("Usage: python mahi_bridge.py <command> [args]")
        print("Commands:")
        print("  route <input>  - Classify and route a task")
        print("  status         - Show orchestrator status")
        print("  agents         - List registered agents")
        return

    bridge = MAHIBridge()
    command = sys.argv[1]

    if command == "route" and len(sys.argv) > 2:
        user_input = " ".join(sys.argv[2:])
        result = bridge.route(user_input)
        print(f"Category: {result['category']}")
        print(f"Agent: {result['agent']}")
        print(f"Model: {result['model']}")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Urgency: {result['urgency']}")

    elif command == "status":
        status = bridge.get_status()
        print(f"Agents: {status['agents']}")
        print(f"Queue: {status['queue']}")
        print(f"Active: {status['active']}")
        print(f"Completed: {status['completed']}")

    elif command == "agents":
        for agent_id, agent in bridge.orchestrator.agents.items():
            print(f"  {agent_id}: {agent.name} ({agent.config.model_primary})")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
