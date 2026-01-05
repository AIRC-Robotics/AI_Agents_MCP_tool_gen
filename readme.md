# AI agents for MCP tool generation

## MVP pipeline

This repository includes a minimal MVP implementation that:

1. Analyzes an OpenAPI (JSON) spec.
2. Generates a Python MCP-style module.
3. Tests the generated tool using a mocked HTTP response.
4. Produces a validation report.

### Run the MVP

```bash
python -m mvp_toolgen.orchestrator sample_openapi.json out
```

The report is written to `out/report.json`.

### Run tests

```bash
python -m unittest
```
