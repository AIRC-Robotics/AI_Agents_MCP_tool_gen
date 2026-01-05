from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .spec import AnalysisResult, ToolSpec


class SpecError(ValueError):
    pass


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SpecError(f"Invalid JSON spec: {exc}") from exc


def analyze_openapi(spec_path: Path) -> AnalysisResult:
    raw = _load_json(spec_path)
    title = raw.get("info", {}).get("title", spec_path.stem)
    base_url = ""
    servers = raw.get("servers") or []
    if servers:
        base_url = servers[0].get("url", "").rstrip("/")

    tools = []
    for path, methods in raw.get("paths", {}).items():
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch"}:
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                safe_path = path.strip("/").replace("/", "_").replace("{", "").replace("}", "")
                operation_id = f"{method.lower()}_{safe_path or 'root'}"
            description = operation.get("summary") or operation.get("description") or ""

            parameters: Dict[str, str] = {}
            for param in operation.get("parameters", []):
                name = param.get("name")
                if not name:
                    continue
                schema = param.get("schema", {})
                param_type = schema.get("type", "string")
                parameters[name] = param_type

            response_example = operation.get("x-mock-response")

            tools.append(
                ToolSpec(
                    name=operation_id,
                    description=description,
                    method=method.upper(),
                    url=f"{base_url}{path}",
                    parameters=parameters,
                    response_example=response_example,
                )
            )
    if not tools:
        raise SpecError("No operations found in spec")
    return AnalysisResult(title=title, tools=tools)
