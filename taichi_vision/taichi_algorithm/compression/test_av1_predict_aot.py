"""Tests for the AV1 DC prediction reference contract."""
from __future__ import annotations

import random
import unittest

from .av1_predict_aot import (
    AV1PredictionError,
    av1_dc_predict_capability_report,
    av1_dc_predict_residual_4x4,
)


class AV1PredictionTests(unittest.TestCase):
    def test_reconstruction_is_exact_for_odd_dimensions(self) -> None:
        randomizer = random.Random(0xA71DC)
        for height, width in ((1, 1), (3, 7), (8, 10), (11, 13)):
            samples = [randomizer.randrange(256) for _ in range(height * width)]
            result = av1_dc_predict_residual_4x4(samples, height, width)
            self.assertEqual(result.reconstructed, tuple(samples))
            self.assertEqual(len(result.residual), height * width)

    def test_first_block_uses_8bit_midpoint(self) -> None:
        result = av1_dc_predict_residual_4x4([128] * 16, 4, 4)
        self.assertEqual(result.residual, (0,) * 16)
        result = av1_dc_predict_residual_4x4([0] * 16, 4, 4)
        self.assertEqual(result.residual, (-128,) * 16)

    def test_validation_is_fail_closed(self) -> None:
        with self.assertRaises(AV1PredictionError):
            av1_dc_predict_residual_4x4([0] * 15, 4, 4)
        with self.assertRaises(AV1PredictionError):
            av1_dc_predict_residual_4x4([256] * 16, 4, 4)
        report = av1_dc_predict_capability_report()
        self.assertTrue(report["lossless_reconstruction"])
        self.assertFalse(report["complete_frame_encoder"])


if __name__ == "__main__":
    unittest.main()
