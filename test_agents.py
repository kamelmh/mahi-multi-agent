#!/usr/bin/env python3
"""Test all MAHI agents with real LLM calls."""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

from orchestrator.engine import Orchestrator
from agents.base import Task

from agents.code_agent import create_code_agent
from agents.writing_agent import create_writing_agent
from agents.quick_agent import create_quick_agent
from agents.career_agent import create_career_agent
from agents.spiritual_agent import create_spiritual_agent
from agents.teaching_agent import create_teaching_agent
from agents.dss_agent import create_dss_agent
from agents.research_agent import create_research_agent

def main():
    orch = Orchestrator()
    
    factories = [
        create_code_agent,
        create_writing_agent,
        create_quick_agent,
        create_career_agent,
        create_spiritual_agent,
        create_teaching_agent,
        create_dss_agent,
        create_research_agent,
    ]
    
    for factory in factories:
        try:
            agent = factory()
            orch.register_agent(agent)
            print(f"Registered: {agent.id}")
        except Exception as e:
            print(f"Failed to register {factory.__name__}: {e}")
    
    print(f"\n=== Testing {len(orch.agents)} agents ===\n")
    
    test_tasks = [
        ("code", "Write a Python function that returns the Fibonacci sequence up to n terms"),
        ("write", "Write a 2-sentence overview of climate change"),
        ("quick", "What is the capital of France?"),
        ("career", "What are 3 tips for a software engineering interview?"),
        ("spiritual", "Write a short meditation breathing exercise"),
        ("teaching", "Explain the present simple tense in English"),
        ("dss", "What metrics should a small business track monthly?"),
        ("research", "Summarize the latest trends in AI for 2026"),
    ]
    
    results = []
    for agent_id, user_input in test_tasks:
        print(f"\n--- Testing {agent_id} ---")
        task = Task(agent_id=agent_id, user_input=user_input)
        orch.submit(task)
        
        timeout = 30
        start = time.time()
        while task.state.value in ("queued", "running") and time.time() - start < timeout:
            time.sleep(0.5)
        
        if task.state.value == "complete":
            output = task.result[:200] if task.result else "(empty)"
            print(f"  OK: {output}")
            results.append((agent_id, "PASS", output))
        elif task.state.value == "failed":
            print(f"  FAIL: {task.error}")
            results.append((agent_id, "FAIL", task.error))
        else:
            print(f"  TIMEOUT after {timeout}s")
            results.append((agent_id, "TIMEOUT", "no response"))
    
    print("\n\n=== SUMMARY ===")
    passed = sum(1 for _, s, _ in results if s == "PASS")
    print(f"Passed: {passed}/{len(results)}")
    for agent_id, status, detail in results:
        icon = "+" if status == "PASS" else "x"
        print(f"  {icon} {agent_id}: {status}")
    
    return 0 if passed == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
