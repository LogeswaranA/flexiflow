from typing import Dict, Callable, Any

class ToolsRegistry:
    """Manage pluggable tools for Agent"""
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        
    def register(self,name:str, func:Callable) -> None:
        """Register the tool"""
        self.tools[name] = func
        
    def execute(self,tool_name:str, *args, **kwargs) -> Any: 
        """Execute the tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"No such {tool_name} tool exists")
        return tool(*args,**kwargs)
    
# Mock Weather Tool for test
def mock_weather_api(city:str) -> Dict:
    """ Mock tool to fetch weather data """
    return {"city":city,"temp":"20","condition":"sunny"}