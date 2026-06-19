"""
app_state.py
------------
Screen router — maps tool names to page builder functions.
"""

from typing import Dict, Callable, Optional


class AppState:
    """Manages screen navigation by mapping tool names to page builders."""

    def __init__(self, bridge):
        self._bridge = bridge
        self._pages: Dict[str, Callable] = {}
        self._current_tool: Optional[str] = None

    def register_page(self, tool_name: str, builder_func: Callable):
        self._pages[tool_name] = builder_func

    def navigate_to(self, tool_name: str):
        if tool_name in self._pages:
            self._current_tool = tool_name

    def get_current_tool(self) -> Optional[str]:
        return self._current_tool
