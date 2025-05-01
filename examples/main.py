from typing_extensions import override
from flexiflow import FlexiFlow
from flexiflow.models.base import AgentConfig, Task
from flexiflow.ai.providers import OpenAIProvider, GroqProvider
from flexiflow.core.workflow import WorkflowManager
import os
from dotenv import load_dotenv
load_dotenv(override=True)

def demo_graph_based_mode(flexiflow: FlexiFlow, city: str) -> None:
    """Demonstrate graph-based mode with dependent tasks."""
    print("\n=== Graph-Based Mode ===")
    
    # Define agents
    fetcher_config = AgentConfig(name="fetcher", role="data_fetcher", tools=["weather_api"])
    summarizer_config = AgentConfig(name="summarizer", role="summarizer", tools=[])
    flexiflow.add_agent(fetcher_config)
    flexiflow.add_agent(summarizer_config)

    # Define tasks with dependencies
    fetch_task = Task(
        id="fetch_weather",
        agent_name="fetcher",
        description="Fetch weather data for a city"
    )
    summarize_task = Task(
        id="summarize_weather",
        agent_name="summarizer",
        description="Summarize weather data",
        dependencies=["fetch_weather"]
    )
    flexiflow.add_task(fetch_task)
    flexiflow.add_task(summarize_task)

    # Run in graph-based mode
    result = flexiflow.run(city, force_event_driven=False)
    print(f"Result for {city}: {result}")

def demo_event_driven_mode(flexiflow: FlexiFlow, cities: list) -> None:
    """Demonstrate event-driven mode with independent tasks."""
    print("\n=== Event-Driven Mode ===")
    
    # Define a single agent for fetching weather data
    fetcher_config = AgentConfig(name="fetcher", role="data_fetcher", tools=["weather_api"])
    flexiflow.add_agent(fetcher_config)

    # Define independent tasks for each city
    for i, city in enumerate(cities):
        task = Task(
            id=f"fetch_weather_{i}",
            agent_name="fetcher",
            description=f"Fetch weather data for {city}",
            dependencies=[]
        )
        flexiflow.add_task(task)

    # Run in event-driven mode
    results = flexiflow.run(cities[0], force_event_driven=True)
    for city, result in zip(cities, results):
        print(f"Result for {city}: {result}")

def main():
    # Initialize AI provider (choose one)
    ai_provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    # or
    # ai_provider = GroqProvider(api_key="your-groq-key")

    # Initialize FlexiFlow with AI provider
    flexiflow = FlexiFlow(ai_provider=ai_provider)

    # Demo graph-based mode (single city with dependencies)
    demo_graph_based_mode(flexiflow, city="New York")

    # Reset workflow for event-driven demo
    flexiflow.workflow = WorkflowManager(flexiflow.memory, flexiflow.tools)

    # Demo event-driven mode (multiple cities concurrently)
    demo_event_driven_mode(flexiflow, cities=["New York", "London", "Tokyo"])

if __name__ == "__main__":
    main()