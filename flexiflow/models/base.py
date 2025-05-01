from pydantic import BaseModel
from typing import List, Any
from datetime import datetime

class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    role: str
    tools: List[str]
    
class Task(BaseModel):
    """Represent a task in the workflow"""
    id: str
    agent_name: str
    description: str  # Fixed spelling from 'discription' to 'description'
    dependencies: List[str] = []
    
class MemoryEntry(BaseModel):
    """Memory Entry"""
    key: str
    value: Any
    timestamp: datetime
    