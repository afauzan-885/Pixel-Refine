"""Semantic parity gates for Canny/CLAHE multi-stage block adapters."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    ANALYSIS_ADAPTER_OPERATIONS,
    register_analysis_block_adapters,
    verify_analysis_parity,
)


class AnalysisAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_analysis_block_adapters()

    def test_registration_is_multistage_and_fail_closed(self):
        self.assertEqual(set(ANALYSIS_ADAPTER_OPERATIONS), {"canny_aot", "clahe_aot"})
        for operation in ANALYSIS_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[operation]
            self.assertTrue(adapter.partition_ready)
            self.assertEqual(adapter.partition_strategy.value, "multi_stage")
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertTrue(can_partition_block(operation, "cpu"))
            self.assertFalse(can_auto_block(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_canny_prefix_halo_and_global_hysteresis_non_multiple(self):
        # Deliberately non-multiple dimensions force clipped halos at all four
        # edges and exercise weak-edge connectivity across a block boundary.
        rows, cols = np.indices((19, 27), dtype=np.float32)
        image = np.clip(
            0.06 * rows + 0.03 * cols + (rows >= 9).astype(np.float32) * 0.55,
            0.0,
            1.0,
        ).astype(np.float32)
        report = verify_analysis_parity(
            "canny_aot",
            (image,),
            block_size=(5, 7),
            params={"low_threshold": 0.08, "high_threshold": 0.20, "aperture_size": 3},
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertEqual(report["halo"], 2)
        self.assertEqual(report["stage_contract"]["global_stage"], "hysteresis")
        self.assertFalse(report["native_runtime"])

    def test_clahe_global_lut_and_local_interpolation_non_multiple(self):
        rows, cols = np.indices((23, 31), dtype=np.float32)
        image = np.mod(rows * np.float32(13.0) + cols * np.float32(7.0), 256.0)
        report = verify_analysis_parity(
            "clahe_aot",
            (image,),
            block_size=(6, 8),
            params={"clip_limit": 2.0, "tile_grid_size": (5, 3), "num_bins": 256},
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertEqual(report["halo"], 0)
        self.assertEqual(report["stage_contract"]["global_stage"], "histogram+clip_cdf")
        self.assertFalse(report["native_runtime"])

    def test_unsupported_parameters_fail_closed(self):
        source = np.ones((9, 11), dtype=np.float32)
        cases = (
            ("canny_aot", {"low_threshold": 1.0, "high_threshold": 0.5}),
            ("canny_aot", {"aperture_size": 5}),
            ("clahe_aot", {"num_bins": 1024}),
            ("clahe_aot", {"tile_grid_size": (65, 1)}),
        )
        for operation, params in cases:
            with self.subTest(operation=operation, params=params):
                with self.assertRaises(ValueError):
                    verify_analysis_parity(operation, (source,), block_size=4, params=params)


if __name__ == "__main__":
    unittest.main()
