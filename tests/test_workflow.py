import pytest

from flexiflow.core.memory import SharedMemory
from flexiflow.core.tools import ToolsRegistry, mock_weather_api
from flexiflow.core.workflow import WorkflowManager
from flexiflow.models.base import AgentConfig, Task


@pytest.fixture
def manager():
    memory = SharedMemory()
    tools = ToolsRegistry()
    tools.register("weather_api", mock_weather_api)
    return WorkflowManager(memory, tools)


def fetch_task(task_id="fetch", agent="fetcher"):
    return Task(id=task_id, agent_name=agent, description="fetch weather")


def summarize_task(depends_on="fetch"):
    return Task(
        id="summarize",
        agent_name="summarizer",
        description="summarize weather",
        dependencies=[depends_on],
    )


def register_fetcher(manager, name="fetcher"):
    manager.add_agent(AgentConfig(name=name, role="data_fetcher", tools=["weather_api"]))


def register_summarizer(manager):
    manager.add_agent(AgentConfig(name="summarizer", role="summarizer", tools=[]))


class TestRegistration:
    def test_add_agent_registers_agent_by_name(self, manager):
        register_fetcher(manager)

        assert "fetcher" in manager.agents
        assert manager.agents["fetcher"].config.role == "data_fetcher"

    def test_add_task_adds_graph_node(self, manager):
        manager.add_task(fetch_task())

        assert "fetch" in manager.graph.nodes
        assert manager.graph.nodes["fetch"]["task"].agent_name == "fetcher"

    def test_add_task_with_dependency_adds_edge(self, manager):
        manager.add_task(fetch_task())
        manager.add_task(summarize_task())

        assert manager.graph.has_edge("fetch", "summarize")


class TestEventDrivenMode:
    def test_independent_tasks_return_one_result_each(self, manager):
        register_fetcher(manager)
        manager.add_task(fetch_task("fetch_paris"))
        manager.add_task(fetch_task("fetch_london"))

        results = manager.execute("Paris")

        assert len(results) == 2
        assert all(r["city"] == "Paris" for r in results)

    def test_missing_agent_surfaces_as_error_result(self, manager):
        manager.add_task(fetch_task(agent="ghost"))

        results = manager.execute("Paris")

        assert len(results) == 1
        assert isinstance(results[0], ValueError)

    def test_empty_workflow_returns_empty_list(self, manager):
        assert manager.execute("anything") == []

    def test_force_event_driven_overrides_graph_mode(self, manager):
        register_fetcher(manager)
        register_summarizer(manager)
        manager.add_task(fetch_task())
        manager.add_task(summarize_task())

        results = manager.execute("Paris", force_event_driven=True)

        assert isinstance(results, list)
        assert len(results) == 2


class TestGraphMode:
    def test_dependent_tasks_run_in_topological_order(self, manager):
        register_fetcher(manager)
        register_summarizer(manager)
        manager.add_task(fetch_task())
        manager.add_task(summarize_task())

        result = manager.execute("Paris")

        assert result == "Weather in Paris: 20°C, sunny."

    def test_missing_agent_raises_value_error(self, manager):
        register_fetcher(manager)
        manager.add_task(fetch_task())
        manager.add_task(summarize_task())  # summarizer never registered

        with pytest.raises(ValueError, match="summarizer"):
            manager.execute("Paris")

    def test_dependency_declared_before_task_definition(self, manager):
        """Adding the dependent task first must not corrupt the graph."""
        register_fetcher(manager)
        register_summarizer(manager)
        manager.add_task(summarize_task())  # references "fetch" before it exists
        manager.add_task(fetch_task())

        result = manager.execute("Paris")

        assert result == "Weather in Paris: 20°C, sunny."
