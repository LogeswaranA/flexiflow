from typing import Any
from .memory import SharedMemory
from .tools import ToolsRegistry
from ..models.base import AgentConfig, Task
from ..ai.providers import AIProvider
from typing import Optional

class Agent:
    """Lightweight Agent with roles & tools """
    def __init__(self, config: AgentConfig, memory: SharedMemory, tools: ToolsRegistry, ai_provider: Optional[AIProvider] = None):
        self.config = config
        self.memory = memory
        self.tools = tools  
        self.ai_provider = ai_provider
    
    def execute_task(self,task:Task, input_data:Any) -> Any:
        """Execute task based on agent's role"""
        if self.config.role == "data_fetcher":
            result = self.tools.execute("weather_api",input_data)
            self.memory.write(f"{task.id}_result", result)
            return result
        elif self.config.role == "summarizer":
            data = self.memory.read(f"{task.dependencies[0]}_result")
            if data:
                if self.ai_provider:
                    print("i am in if")
                    # Use AI provider for summarization
                    summary = self.ai_provider.generate_summary(data)
                else:
                    print("i am in else")
                    # Fallback to basic summarization
                    summary = f"Weather in {data['city']}: {data['temp']}°C, {data['condition']}."
                self.memory.write(f"{task.id}_result", summary)
                return summary
        return None