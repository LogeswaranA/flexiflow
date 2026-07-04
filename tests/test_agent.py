import pytest

from flexiflow.ai.providers import AIProvider
from flexiflow.core.agent import Agent
from flexiflow.core.memory import SharedMemory
from flexiflow.core.tools import ToolsRegistry, mock_weather_api
from flexiflow.models.base import AgentConfig, Task


class CannedProvider(AIProvider):
    """Test double that returns a deterministic summary."""

    def generate_summary(self, data):
        return f"AI summary for {data['city']}"


@pytest.fixture
def memory():
    return SharedMemory()


@pytest.fixture
def tools():
    registry = ToolsRegistry()
    registry.register("weather_api", mock_weather_api)
    return registry


def make_agent(role, memory, tools, ai_provider=None):
    config = AgentConfig(name=f"{role}_agent", role=role, tools=["weather_api"])
    return Agent(config, memory, tools, ai_provider)


class TestDataFetcherRole:
    def test_executes_tool_and_returns_result(self, memory, tools):
        agent = make_agent("data_fetcher", memory, tools)
        task = Task(id="fetch", agent_name="data_fetcher_agent", description="fetch weather")

        result = agent.execute_task(task, "Paris")

        assert result == {"city": "Paris", "temp": "20", "condition": "sunny"}

    def test_writes_result_to_shared_memory(self, memory, tools):
        agent = make_agent("data_fetcher", memory, tools)
        task = Task(id="fetch", agent_name="data_fetcher_agent", description="fetch weather")

        agent.execute_task(task, "Paris")

        assert memory.read("fetch_result") == {
            "city": "Paris",
            "temp": "20",
            "condition": "sunny",
        }


class TestSummarizerRole:
    def _summarize_task(self):
        return Task(
            id="summarize",
            agent_name="summarizer_agent",
            description="summarize weather",
            dependencies=["fetch"],
        )

    def test_fallback_summary_without_ai_provider(self, memory, tools):
        memory.write("fetch_result", {"city": "Paris", "temp": "20", "condition": "sunny"})
        agent = make_agent("summarizer", memory, tools)

        result = agent.execute_task(self._summarize_task(), None)

        assert result == "Weather in Paris: 20°C, sunny."
        assert memory.read("summarize_result") == result

    def test_uses_ai_provider_when_available(self, memory, tools):
        memory.write("fetch_result", {"city": "Paris", "temp": "20", "condition": "sunny"})
        agent = make_agent("summarizer", memory, tools, ai_provider=CannedProvider())

        result = agent.execute_task(self._summarize_task(), None)

        assert result == "AI summary for Paris"
        assert memory.read("summarize_result") == result

    def test_returns_none_when_dependency_data_missing(self, memory, tools):
        agent = make_agent("summarizer", memory, tools)

        result = agent.execute_task(self._summarize_task(), None)

        assert result is None


class TestUnknownRole:
    def test_returns_none(self, memory, tools):
        agent = make_agent("mystery", memory, tools)
        task = Task(id="noop", agent_name="mystery_agent", description="does nothing")

        assert agent.execute_task(task, "anything") is None


def test_execute_task_produces_no_debug_output(memory, tools, capsys):
    """Library code must not print debug noise to stdout."""
    memory.write("fetch_result", {"city": "Paris", "temp": "20", "condition": "sunny"})

    fetcher = make_agent("data_fetcher", memory, tools)
    fetcher.execute_task(
        Task(id="fetch2", agent_name="data_fetcher_agent", description="fetch"), "Paris"
    )

    summarizer = make_agent("summarizer", memory, tools)
    summarizer.execute_task(
        Task(
            id="summarize",
            agent_name="summarizer_agent",
            description="summarize",
            dependencies=["fetch"],
        ),
        None,
    )

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""
