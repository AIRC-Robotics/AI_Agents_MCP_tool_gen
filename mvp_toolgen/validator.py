from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from .spec import AnalysisResult
from .tester import TestReport


@dataclass
class ValidationIssue:
    message: str


@dataclass
class ValidationReport:
    issues: List[ValidationIssue]

    @property
    def passed(self) -> bool:
        return not self.issues


def validate_module(analysis: AnalysisResult, module_path: Path, tests: TestReport) -> ValidationReport:
    issues: List[ValidationIssue] = []
    try:
        compile(module_path.read_text(encoding="utf-8"), str(module_path), "exec")
    except SyntaxError as exc:
        issues.append(ValidationIssue(message=f"Syntax error: {exc}"))

    for name, result in tests.results.items():
        if not result.passed:
            issues.append(ValidationIssue(message=f"Tool {name} failed tests: {result.details}"))

    expected = {tool.name for tool in analysis.tools}
    for missing in expected - tests.results.keys():
        issues.append(ValidationIssue(message=f"Missing test result for {missing}"))

    return ValidationReport(issues=issues)
