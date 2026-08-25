"""Backend-free tests for the shared family-pipeline boundary helpers."""

from __future__ import annotations

import unittest

import numpy as np

try:
    # Works when pytest imports the test through the repository package.
    from ...pipeline_common import (
        PipelineReport,
        as_gray_float32,
        finite_fraction,
        image_quality_metrics,
        pressure_sizes,
        timed_stage,
        update_stage_output,
        validate_same_shape,
    )
except ImportError:  # pragma: no cover - direct pytest collection fallback
    from taichi_vision.taichi_algorithm.pipeline_common import (
        PipelineReport,
        as_gray_float32,
        finite_fraction,
        image_quality_metrics,
        pressure_sizes,
        timed_stage,
        update_stage_output,
        validate_same_shape,
    )


class PipelineContractTests(unittest.TestCase):
    def test_image_validation_and_gray_conversion(self):
        images = validate_same_shape(
            [np.ones((4, 5, 3), dtype=np.float64), np.zeros((4, 5, 3), dtype=np.float32)]
        )
        self.assertEqual(images[0].dtype, np.float32)
        self.assertEqual(as_gray_float32(images[0]).shape, (4, 5))
        self.assertAlmostEqual(float(as_gray_float32(np.ones((2, 2, 3), dtype=np.float32))[0, 0]), 1.0)

    def test_quality_and_report(self):
        reference = np.zeros((2, 2), dtype=np.float32)
        candidate = np.ones((2, 2), dtype=np.float32)
        metrics = image_quality_metrics(reference, candidate)
        self.assertEqual(metrics["finite_fraction"], 1.0)
        self.assertEqual(metrics["mean_abs_error"], 1.0)

        report = PipelineReport("contract", backend="test")
        with timed_stage(report, "copy"):
            output = candidate.copy()
        update_stage_output(report, 0, output)
        self.assertTrue(report.success)
        self.assertEqual(report.stages[0].output_shape, (2, 2))
        self.assertEqual(report.stages[0].finite_fraction, 1.0)
        self.assertEqual(finite_fraction(output), 1.0)

    def test_pressure_case_is_descriptive_and_does_not_allocate(self):
        cases = pressure_sizes(resolutions=((7072, 7072),), channels=3)
        self.assertEqual(cases[0]["megapixels"], 50)
        self.assertGreater(cases[0]["bytes"], 500_000_000)

    def test_invalid_stack_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_same_shape([np.zeros((2, 2)), np.zeros((2, 3))])


if __name__ == "__main__":
    unittest.main()
