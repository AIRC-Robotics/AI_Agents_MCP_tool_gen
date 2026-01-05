import json
from pathlib import Path
import tempfile
import unittest

from mvp_toolgen.orchestrator import run_pipeline


class PipelineTests(unittest.TestCase):
    def test_pipeline_generates_report(self) -> None:
        spec_path = Path("sample_openapi.json")
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = run_pipeline(spec_path, Path(tmpdir))
            self.assertTrue(report_path.exists())
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertTrue(report["validation"]["passed"])
            self.assertIn("get_current_weather", report["tools"])


if __name__ == "__main__":
    unittest.main()
