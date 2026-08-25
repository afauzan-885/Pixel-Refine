"""Unified fail-closed audit for iterative and variable-cardinality stages."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot import (
    ITERATIVE_FEATURE_GAP_OPERATIONS,
    iterative_feature_gap_report,
    register_akaze_block_adapters,
    verify_akaze_keypoint_parity,
)


class IterativeFeatureGapTests(unittest.TestCase):
    def test_akaze_keypoint_stage_has_bounded_cpu_candidate_only_parity(self):
        register_akaze_block_adapters()
        image = np.zeros((37, 43), dtype=np.float32)
        image[5:30:4, 7:36:5] = 1.0
        report = verify_akaze_keypoint_parity(
            (image,), block_size=(11, 13), params={"max_keypoints": 128}
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["backend"], "cpu")
        self.assertTrue(report["deterministic_merge"])
        self.assertFalse(report["native_runtime"])
        self.assertEqual(report["max_abs_error"], 0.0)
    def test_all_iterative_feature_operations_remain_full_frame(self):
        report = iterative_feature_gap_report(backend="cpu")
        self.assertEqual(report["operation_order"], list(ITERATIVE_FEATURE_GAP_OPERATIONS))
        self.assertEqual(report["default_mode"], "full_frame")
        self.assertEqual(report["status"], "fail_closed_until_iterative_parity_evidence")
        self.assertFalse(report["semantic_cpu_parity_proven"])
        self.assertFalse(report["native_partition_parity_proven"])
        for record in report["operations"].values():
            self.assertEqual(record["status"], "gap_fail_closed")
            self.assertFalse(record["native_runtime"])
            self.assertTrue(record["preserves_default_full_frame"])
            self.assertGreaterEqual(len(record["required_evidence"]), 3)

    def test_subset_deduplicates_and_keeps_device_scope(self):
        report = iterative_feature_gap_report(
            ("bm3d", "akaze", "bm3d"),
            backend="cuda",
            device="NVIDIA GeForce MX150",
        )
        self.assertEqual(report["operation_order"], ["bm3d", "akaze"])
        self.assertEqual(report["device"], "NVIDIA GeForce MX150")
        for record in report["operations"].values():
            self.assertFalse(record["native_partition_evidence"])

    def test_unknown_stage_rejected(self):
        with self.assertRaises(ValueError):
            iterative_feature_gap_report("unknown_stage", backend="cpu")


if __name__ == "__main__":
    unittest.main()
