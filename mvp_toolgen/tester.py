from __future__ import annotations

import asyncio
import json
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict
from unittest import mock

from .spec import AnalysisResult, ToolSpec


@dataclass
class ToolTestResult:
    name: str
    passed: bool
    details: str


@dataclass
class TestReport:
    results: Dict[str, ToolTestResult]


class _MockHTTPResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def _load_module(module_path: Path) -> types.ModuleType:
    import importlib.util

    spec = importlib.util.spec_from_file_location("generated_mcp_tools", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load generated module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mock_urlopen_factory(tool: ToolSpec) -> mock.MagicMock:
    if not tool.response_example:
        raise ValueError("Missing response_example for mock test")
    return mock.MagicMock(return_value=_MockHTTPResponse(tool.response_example))


def run_tool_tests(analysis: AnalysisResult, module_path: Path) -> TestReport:
    module = _load_module(module_path)
    results: Dict[str, ToolTestResult] = {}
    for tool in analysis.tools:
        try:
            urlopen_mock = _mock_urlopen_factory(tool)
            with mock.patch("urllib.request.urlopen", urlopen_mock):
                params = {name: f"sample_{name}" for name in tool.parameters}
                output = asyncio.run(module.mcp.call_tool(tool.name, params))
            if tool.response_example and output != tool.response_example:
                raise AssertionError("Output did not match expected mock response")
            results[tool.name] = ToolTestResult(
                name=tool.name,
                passed=True,
                details="ok",
            )
        except Exception as exc:  # noqa: BLE001
            results[tool.name] = ToolTestResult(
                name=tool.name,
                passed=False,
                details=str(exc),
            )
    return TestReport(results=results)
