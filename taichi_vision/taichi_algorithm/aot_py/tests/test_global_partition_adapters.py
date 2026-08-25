"""Deterministic semantic gates for RANSAC flow cleanup and Hough voting."""

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
    GLOBAL_PARTITION_ADAPTER_OPERATIONS,
    register_global_partition_adapters,
    run_global_partition_tiled,
    verify_global_partition_parity,
)


class GlobalPartitionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_global_partition_adapters()

    def test_registration_is_explicit_and_fail_closed(self):
        self.assertEqual(
            set(GLOBAL_PARTITION_ADAPTER_OPERATIONS),
            {"ransac_flow_cleanup", "ransac_flow_cleanup_aot", "hough_lines_aot"},
        )
        for operation in GLOBAL_PARTITION_ADAPTER_OPERATIONS:
            adapter = registered_block_adapters()[operation]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertTrue(adapter.metadata["deterministic_merge"])
            self.assertTrue(can_partition_block(operation, "cpu"))
            self.assertFalse(can_auto_block(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_ransac_non_multiple_parity_and_boundary_tie(self):
        rows, cols = np.indices((17, 23), dtype=np.float32)
        flow = np.empty((17, 23, 2), dtype=np.float32)
        flow[..., 0] = np.float32(0.5) + rows * np.float32(0.001)
        flow[..., 1] = np.float32(-0.25) + cols * np.float32(0.001)
        # Exact-threshold deviations are outliers because the graph uses `<`.
        flow[2, 3] = (1.5, -0.25)  # distance exactly 1.0 in x
        flow[14, 19] = (-4.0, 7.0)
        params = {"threshold": 1.0, "stride_refine": 1, "stride_final": 1}
        for operation in ("ransac_flow_cleanup", "ransac_flow_cleanup_aot"):
            with self.subTest(operation=operation):
                first = verify_global_partition_parity(
                    operation, (flow,), block_size=(5, 7), params=params
                )
                second = verify_global_partition_parity(
                    operation, (flow,), block_size=(8, 9), params=params
                )
                self.assertTrue(first["passed"], first)
                self.assertTrue(second["passed"], second)
                self.assertEqual(first["max_abs_error"], 0.0)
                self.assertEqual(second["max_abs_error"], 0.0)
                left = run_global_partition_tiled(
                    operation, (flow,), block_size=(5, 7), params=params
                )
                right = run_global_partition_tiled(
                    operation, (flow,), block_size=(8, 9), params=params
                )
                np.testing.assert_array_equal(left, right)
                # The exact-boundary sample is replaced, not retained.
                self.assertFalse(np.array_equal(left[2, 3], flow[2, 3]))

    def test_hough_non_multiple_vote_merge_and_tie_order(self):
        edges = np.zeros((19, 27), dtype=np.float32)
        edges[3, :] = 255.0
        edges[:, 9] = 255.0
        edges[12, 17] = 255.0
        params = {
            "rho_resolution": 1.0,
            "theta_resolution": 3.0,
            "threshold": 5,
            "nms_radius": 1,
            "max_peaks": 20,
            "edge_threshold": 128.0,
        }
        first = verify_global_partition_parity(
            "hough_lines_aot", (edges,), block_size=(5, 7), params=params
        )
        second = verify_global_partition_parity(
            "hough_lines_aot", (edges,), block_size=(8, 11), params=params
        )
        self.assertTrue(first["passed"], first)
        self.assertTrue(second["passed"], second)
        self.assertEqual(first["max_abs_error"], 0.0)
        self.assertEqual(second["max_abs_error"], 0.0)
        left = run_global_partition_tiled(
            "hough_lines_aot", (edges,), block_size=(5, 7), params=params
        )
        right = run_global_partition_tiled(
            "hough_lines_aot", (edges,), block_size=(8, 11), params=params
        )
        self.assertEqual(left, right)

        # A constant accumulator creates equal-vote candidates; repeat calls
        # must preserve the row-major first-peak order.
        constant = np.ones((19, 27), dtype=np.float32) * 255.0
        tie_params = {**params, "threshold": 1, "nms_radius": 0, "max_peaks": 7}
        tie_left = run_global_partition_tiled(
            "hough_lines_aot", (constant,), block_size=(4, 6), params=tie_params
        )
        tie_right = run_global_partition_tiled(
            "hough_lines_aot", (constant,), block_size=(7, 5), params=tie_params
        )
        self.assertEqual(tie_left, tie_right)
        self.assertEqual(len(tie_left), 7)

    def test_unsupported_global_variants_fail_closed(self):
        flow = np.zeros((9, 13, 2), dtype=np.float32)
        edges = np.zeros((9, 13), dtype=np.float32)
        cases = (
            ("ransac_flow_cleanup", (flow,), {"stride_refine": 2}),
            ("ransac_flow_cleanup_aot", (flow,), {"threshold": -1.0}),
            ("hough_lines_aot", (edges,), {"rho_resolution": 2.0}),
            ("hough_lines_aot", (edges,), {"max_peaks": 501}),
        )
        for operation, inputs, params in cases:
            with self.subTest(operation=operation, params=params):
                with self.assertRaises(ValueError):
                    verify_global_partition_parity(
                        operation, inputs, block_size=(4, 5), params=params
                    )


if __name__ == "__main__":
    unittest.main()
