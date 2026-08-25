"""Fail-closed feature/geometry partition contract tests."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot import (
    FEATURE_GEOMETRY_CONTRACT_OPERATIONS,
    can_auto_block,
    can_auto_partition_dispatch,
    feature_geometry_partition_gap_report,
    operation_contract,
    register_akaze_block_adapters,
    validate_homography_correspondence_contract,
)


class FeatureGeometryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_akaze_block_adapters()

    def test_report_covers_feature_and_global_geometry(self):
        report = feature_geometry_partition_gap_report(backend="cpu")
        self.assertEqual(
            FEATURE_GEOMETRY_CONTRACT_OPERATIONS,
            ("akaze", "find_homography"),
        )
        self.assertEqual(report["operation_order"], ["akaze", "find_homography"])
        self.assertEqual(set(report["operations"]), {"akaze", "find_homography"})
        self.assertEqual(report["default_mode"], "full_frame")
        self.assertFalse(report["native_partition_parity_proven"])
        self.assertFalse(report["runtime_dispatch_changed"])

    def test_akaze_is_restricted_semantic_cpu_only(self):
        record = feature_geometry_partition_gap_report(backend="cpu")[
            "operations"
        ]["akaze"]
        self.assertEqual(record["status"], "restricted_semantic_cpu")
        self.assertTrue(record["adapter_registered"])
        self.assertTrue(record["semantic_cpu_partition"])
        self.assertFalse(record["automatic_safe"])
        self.assertFalse(record["automatic_dispatch_safe"])
        self.assertFalse(record["native_partition_evidence"])
        self.assertTrue(record["preserves_default_full_frame"])
        self.assertGreaterEqual(len(record["required_evidence"]), 3)

    def test_homography_remains_global_and_fail_closed(self):
        record = feature_geometry_partition_gap_report(backend="cuda")[
            "operations"
        ]["find_homography"]
        self.assertEqual(record["status"], "gap_fail_closed")
        self.assertEqual(record["path"], "global")
        self.assertFalse(record["semantic_cpu_partition"])
        self.assertFalse(record["partition_safe"])
        self.assertFalse(record["native_runtime"])
        self.assertTrue(record["preserves_default_full_frame"])
        self.assertGreaterEqual(len(record["blocked_reasons"]), 3)

    def test_alias_subset_is_read_only_and_unknown_rejected(self):
        before = {
            name: operation_contract(name).as_dict()
            for name in ("akaze", "find_homography")
        }
        report = feature_geometry_partition_gap_report(
            ("akaze", "akaze"), backend="vulkan", device="synthetic"
        )
        self.assertEqual(report["operation_order"], ["akaze"])
        self.assertEqual(report["backend"], "vulkan")
        self.assertEqual(report["device"], "synthetic")
        self.assertFalse(report["operations"]["akaze"]["native_partition_evidence"])
        after = {
            name: operation_contract(name).as_dict()
            for name in ("akaze", "find_homography")
        }
        self.assertEqual(before, after)
        with self.assertRaises(ValueError):
            feature_geometry_partition_gap_report("unknown_geometry", backend="cpu")

    def test_homography_correspondence_preflight_preserves_row_pairing(self):
        # The global solver remains full-frame; this only validates the
        # deterministic input boundary needed before any future partitioned
        # reducer can be considered.
        pts1 = np.asarray(
            [[0, 0], [10, 0], [0, 10], [10, 10], [4, 7]], dtype=np.int16
        )
        pts2 = (pts1.astype(np.float32) + np.asarray([2.5, -1.25], dtype=np.float32))
        report = validate_homography_correspondence_contract(
            pts1, pts2, max_points=8
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["point_count"], 5)
        self.assertEqual(report["shape"], [5, 2])
        self.assertEqual(report["dtype"], "float32")
        self.assertTrue(report["contiguous"])
        self.assertTrue(report["paired_rows"])
        self.assertEqual(report["ordering"], "input_row_order_preserved")
        self.assertFalse(report["partition_qualified"])
        self.assertFalse(report["native_runtime"])

    def test_homography_correspondence_preflight_rejects_unsafe_inputs(self):
        valid = np.asarray(
            [[0, 0], [1, 0], [0, 1], [1, 1]], dtype=np.float32
        )
        with self.assertRaises(ValueError):
            validate_homography_correspondence_contract(valid[:3], valid)
        with self.assertRaises(ValueError):
            validate_homography_correspondence_contract(valid, valid, max_points=3)
        invalid = valid.copy()
        invalid[0, 0] = np.nan
        with self.assertRaises(ValueError):
            validate_homography_correspondence_contract(invalid, valid)
        with self.assertRaises(ValueError):
            validate_homography_correspondence_contract(valid.reshape(2, 4), valid)


if __name__ == "__main__":
    unittest.main()
