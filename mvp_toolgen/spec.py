from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ToolSpec:
    name: str
    description: str
    method: str
    url: str
    parameters: Dict[str, str]
    response_example: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    title: str
    tools: List[ToolSpec] = field(default_factory=list)
