"""Regression tests for the shared block executor used by extended wrappers.

The wrappers are defined under ``image_processing`` but the block executor is
owned by ``aot_api``.  Keep the executor mocked here so this test validates the
operation identity/import contract without requiring a native device or TCM.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from taichi_vision.taichi_algorithm import aot_api
from taichi_vision.taichi_algorithm.image_processing import extended_aot


class ExtendedBlockDispatchTests(unittest.TestCase):
    def test_extended_wrappers_reach_aot_api_block_executor(self):
        source = np.arange(64, dtype=np.float32).reshape(8, 8)
        kernel = np.ones((3, 3), dtype=np.float32)
        lut = np.arange(256, dtype=np.float32)
        sentinel = np.full(source.shape, 42.0, dtype=np.float32)

        with patch.object(aot_api, "_run_blockwise", return_value=sentinel) as runner:
            morphology = extended_aot.dilate_aot(source, ksize=3)
            filtered = extended_aot.filter2d_aot(source, kernel)
            threshold_value, thresholded = extended_aot.threshold_aot(
                source, thresh=17.0, maxval=255.0, thresh_type="BINARY"
            )
            normalized = extended_aot.normalize_aot(source, 0.0, 1.0)
            guided = extended_aot.joint_bilateral_guidance_aot(
                source, source, radius=1
            )
            enhanced = extended_aot.enhance_image_aot(source, source, lut)

        self.assertEqual(float(threshold_value), 17.0)
        for result in (morphology, filtered, thresholded, normalized, guided, enhanced):
            np.testing.assert_array_equal(result, sentinel)
        self.assertEqual(
            {call.args[0] for call in runner.call_args_list},
            {
                "morphology",
                "filter2d",
                "threshold",
                "normalize",
                "joint_bilateral_guidance",
                "enhance_image",
            },
        )
        self.assertEqual(runner.call_count, 6)


if __name__ == "__main__":
    unittest.main()
