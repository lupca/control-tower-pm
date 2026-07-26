from typing import Any, Dict


class MCPClient:
    def __init__(self, service_name: str):
        self.service_name = service_name

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "tool": tool_name,
            "result": [{"file": "app/main.py", "score": 0.95}]
        }
