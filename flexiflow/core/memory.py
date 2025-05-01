import json
from typing import Dict, Any
from datetime import datetime
from ..models.base import MemoryEntry

class SharedMemory:
    """In Memory Key value store for agent collaboration"""
    def __init__(self):
        self.store: Dict[str, MemoryEntry] = {}
        
    def write(self, key:str, value: Any) -> None:
        """ Write to memory"""
        entry = MemoryEntry(key=key, value=value, timestamp = datetime.now())
        self.store[key]=entry
        self.store[key].value = json.loads(json.dumps(value))
        
    def read(self, key:str) -> Any:
        """Read from memory """
        entry = self.store.get(key)
        return entry.value if entry else None