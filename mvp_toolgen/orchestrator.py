from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .analyzer import analyze_openapi
from .generator import generate_module
from .tester import run_tool_tests
from .validator import validate_module


def run_pipeline(spec_path: Path, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    analysis = analyze_openapi(spec_path)
    module_path = output_dir / "generated_tools.py"
    generate_module(analysis, module_path)
    tests = run_tool_tests(analysis, module_path)
    validation = validate_module(analysis, module_path, tests)

    report = {
        "title": analysis.title,
        "tools": [tool.name for tool in analysis.tools],
        "tests": {name: asdict(result) for name, result in tests.results.items()},
        "validation": {
            "passed": validation.passed,
            "issues": [issue.message for issue in validation.issues],
        },
    }
    report_path = output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run MVP MCP tool generation pipeline")
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    report = run_pipeline(args.spec, args.output)
    print(f"Report written to {report}")
