import networkx as nx
import asyncio
from typing import Dict, Any, List
from ..models.base import AgentConfig, Task
from .memory import SharedMemory
from .tools import ToolsRegistry
from .agent import Agent

class WorkflowManager:
    """Orchestrates tasks using a hybrid graph-based or event-driven workflow."""
    def __init__(self, memory: SharedMemory, tools: ToolsRegistry):
        self.graph = nx.DiGraph()
        self.memory = memory
        self.tools = tools
        self.agents: Dict[str, Agent] = {}

    def add_agent(self, config: AgentConfig, ai_provider=None) -> None:
        """Register an agent."""
        self.agents[config.name] = Agent(config, self.memory, self.tools, ai_provider)

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow graph."""
        self.graph.add_node(task.id, task=task)
        for dep in task.dependencies:
            self.graph.add_edge(dep, task.id)

    def _is_graph_mode_required(self, tasks: List[Task]) -> bool:
        """Determine if graph-based mode is needed based on task dependencies."""
        return any(task.dependencies for task in tasks)

    async def _execute_event_driven(self, tasks: List[Task], input_data: Any) -> List[Any]:
        """Execute tasks in event-driven mode using asyncio."""
        async def run_task(task: Task) -> Any:
            agent = self.agents.get(task.agent_name)
            if not agent:
                raise ValueError(f"Agent {task.agent_name} not found")
            return agent.execute_task(task, input_data)

        # Iterate over graph node IDs to get Task objects
        task_coroutines = [run_task(self.graph.nodes[task_id]["task"]) for task_id in self.graph.nodes]
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)
        return results

    def execute(self, input_data: Any, force_event_driven: bool = False) -> Any:
        """Execute the workflow, choosing between graph-based and event-driven modes."""
        tasks = [self.graph.nodes[task_id]["task"] for task_id in self.graph.nodes]
        
        if force_event_driven or not self._is_graph_mode_required(tasks):
            # Event-driven mode for independent or high-concurrency tasks
            loop = asyncio.get_event_loop()
            results = loop.run_until_complete(self._execute_event_driven(tasks, input_data))
            return results  # Return all results for event-driven mode
        else:
            # Graph-based mode for dependent tasks
            for task_id in nx.topological_sort(self.graph):
                task = self.graph.nodes[task_id]["task"]
                agent = self.agents.get(task.agent_name)
                if not agent:
                    raise ValueError(f"Agent {task.agent_name} not found")
                result = agent.execute_task(task, input_data)
            return result