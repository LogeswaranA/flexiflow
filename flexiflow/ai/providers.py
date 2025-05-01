from abc import ABC, abstractmethod
from typing import Any, Dict
from openai import OpenAI
from groq import Groq

class AIProvider(ABC):
    """Base class for AI providers"""
    @abstractmethod
    def generate_summary(self, data: Dict) -> str:
        pass

class OpenAIProvider(AIProvider):
    """OpenAI implementation"""
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def generate_summary(self, data: Dict) -> str:
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a weather summarization assistant."
            }, {
                "role": "user",
                "content": f"Summarize this weather data: {data}"
            }]
        )
        return response.choices[0].message.content

class GroqProvider(AIProvider):
    """Groq implementation"""
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def generate_summary(self, data: Dict) -> str:
        response = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{
                "role": "system",
                "content": "You are a weather summarization assistant."
            }, {
                "role": "user",
                "content": f"Summarize this weather data: {data}"
            }]
        )
        return response.choices[0].message.content