from .core.memory import SharedMemory
from .core.tools import ToolsRegistry, mock_weather_api
from .core.workflow import WorkflowManager
from .ethics.ethics import EthicsModule
from .models.base import AgentConfig, Task
from typing import Any, Optional
from .ai.providers import AIProvider

class FlexiFlow:
    """Main framework class."""
    def __init__(self, ai_provider: Optional[AIProvider] = None):
        self.memory = SharedMemory()
        self.tools = ToolsRegistry()
        self.workflow = WorkflowManager(self.memory, self.tools)
        self.ethics = EthicsModule()
        self.ai_provider = ai_provider
        # Register default tools
        self.tools.register("weather_api", mock_weather_api)

    def add_agent(self, config: AgentConfig) -> None:
        """Add an agent to the framework."""
        self.workflow.add_agent(config, self.ai_provider)

    def add_task(self, task: Task) -> None:
        """Add a task to the framework."""
        self.workflow.add_task(task)

    def run(self, query: str, force_event_driven: bool = False) -> Any:
        """Run the framework with a user query."""
        result = self.workflow.execute(query, force_event_driven=force_event_driven)
        if self.ethics.validate(result):
            return result
        return None