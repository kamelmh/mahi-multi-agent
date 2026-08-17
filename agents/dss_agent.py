"""DSS Agent — ERP, VBA, data analysis."""
from agents.base import BaseAgent, AgentConfig, Task


def create_dss_agent() -> BaseAgent:
    config = AgentConfig(
        id="dss",
        name="DSS Agent",
        description="ERP development, VBA macros, data analysis, Academix system",
        model_primary="nvidia/nemotron-3-super-120b-a12b:free",
        model_fallback="openai/gpt-oss-20b:free",
        provider="openrouter",
        capabilities=["vba development", "excel automation", "data analysis", "erp systems"],
        tools=["file_read", "file_write", "terminal", "excel", "file_search"],
        max_concurrent=1,
        timeout=180,
    )

    class DSSAgent(BaseAgent):
        def _default_system_prompt(self) -> str:
            return """You are the DSS Agent for the Academix Decision Support System.

Academix v13.4:
- ERP for Algerian public sector logistics
- Excel VBA (44 modules, 113 tests)
- Sheets: CONFIG, Dashboard, Stock_Entry, Orders, Inventory, Alerts
- Ground Truth: D=1546, Q*=176, ROP=212.4, SS=200, LT=2
- Revenue: $100-500/custom system

VBA Standards:
- Option Explicit always
- Constants for magic numbers
- Error handling (On Error GoTo)
- Descriptive variable names
- Comments for complex logic

For ERP tasks:
- Reference the actual system architecture
- Follow existing patterns
- Don't break backward compatibility
- Test with edge cases (zero, negative, overflow)

DSS Concepts:
- EOQ (Economic Order Quantity)
- ROP (Reorder Point)
- Safety Stock
- Lead Time
- ABC Analysis
- Wilson Formula: Q* = sqrt(2DS/H)"""

        def execute(self, task: Task) -> str:
            messages = self._build_context(task)
            model = task.model or self.config.model_primary
            return self._call_llm(messages, model, max_tokens=8192)

    return DSSAgent(config)
