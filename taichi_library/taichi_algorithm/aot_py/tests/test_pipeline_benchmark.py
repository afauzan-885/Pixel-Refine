"""Contract tests for the bounded throughput/pressure harness."""

from __future__ import annotations

import unittest

import numpy as np

from ..tools.pipeline_benchmark import BenchmarkCase, run_benchmark


class PipelineBenchmarkTests(unittest.TestCase):
    def test_budget_skip_happens_before_allocation(self):
        cases = [BenchmarkCase(16, 16), BenchmarkCase(7072, 7072)]
        results = run_benchmark(lambda image: np.asarray(image), cases=cases, max_input_bytes=1024)
        self.assertEqual(results[0].status, "ok")
        self.assertEqual(results[1].status, "skipped_budget")


if __name__ == "__main__":
    unittest.main()
