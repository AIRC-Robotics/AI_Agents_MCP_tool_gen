from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .spec import AnalysisResult, ToolSpec


def _render_tool(tool: ToolSpec) -> str:
    params = ", ".join(f"{name}: str" for name in tool.parameters) or ""
    docstring = tool.description.replace("\\", "\\\\").replace("\"", "\\\"")
    return f"""


@mcp.tool()
async def {tool.name}({params}) -> dict:
    "{docstring}"
    params = {{
{_render_params_dict(tool)}
    }}
    return await _request("{tool.method}", "{tool.url}", params)
"""


def _render_params_dict(tool: ToolSpec) -> str:
    if not tool.parameters:
        return ""
    return "\n".join(f"        \"{name}\": {name}," for name in tool.parameters)


def generate_module(analysis: AnalysisResult, output_path: Path) -> None:
    tool_blocks = "\n".join(_render_tool(tool) for tool in analysis.tools)
    output_path.write_text(
        _module_template(analysis.title, tool_blocks),
        encoding="utf-8",
    )


def _module_template(title: str, tool_blocks: str) -> str:
    return f"""from __future__ import annotations

import asyncio
import json
import urllib.parse
import urllib.request

from mvp_mcp import FastMCP

mcp = FastMCP({title!r})


async def _request(method: str, url: str, params: dict) -> dict:
    data = None
    headers = {{"Content-Type": "application/json"}}
    full_url = url

    if method.upper() == "GET" and params:
        query = urllib.parse.urlencode(params)
        full_url = f"{{url}}?{{query}}"
    elif params:
        data = json.dumps(params).encode("utf-8")

    request = urllib.request.Request(full_url, data=data, headers=headers, method=method.upper())
    response = await asyncio.to_thread(urllib.request.urlopen, request)
    raw = response.read().decode("utf-8")
    if not raw:
        return {{}}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {{"raw": raw}}
{tool_blocks}
"""
