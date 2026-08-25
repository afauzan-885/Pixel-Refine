"""Fail-closed contract tests for normal versus bounded BM3D."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot import (
    bm3d_partition_gap_report,
    register_bounded_semantic_adapters,
    run_adapter_tiled,
)


class BM3DPartitionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_bounded_semantic_adapters()

    def test_sigma_zero_baseline_is_not_normal_native_support(self):
        report = bm3d_partition_gap_report(backend="cpu")
        record = report["operations"]["bm3d"]
        self.assertEqual(report["default_mode"], "full_frame")
        self.assertEqual(record["status"], "restricted_semantic_cpu")
        self.assertTrue(record["semantic_cpu_partition"])
        self.assertFalse(record["automatic_safe"])
        self.assertFalse(record["automatic_dispatch_safe"])
        self.assertFalse(record["native_partition_evidence"])
        self.assertEqual(record["semantic_parameter_scope"], "explicit sigma=0 identity only")
        self.assertTrue(record["preserves_default_full_frame"])

    def test_exact_device_scope_does_not_infer_native_evidence(self):
        report = bm3d_partition_gap_report(
            backend="cuda", device="NVIDIA GeForce MX150"
        )
        record = report["operations"]["bm3d"]
        self.assertFalse(record["native_partition_evidence"])
        self.assertEqual(record["native_evidence_records"], [])
        self.assertFalse(report["native_partition_parity_proven"])

    def test_report_is_diagnostic_and_contains_required_gates(self):
        report = bm3d_partition_gap_report()
        record = report["operations"]["bm3d"]
        self.assertFalse(report["runtime_dispatch_changed"])
        self.assertGreaterEqual(len(record["blocked_reasons"]), 3)
        self.assertGreaterEqual(len(record["required_evidence"]), 3)

    def test_bm3d_adapter_rejects_nonzero_sigma_instead_of_tiling_normal_bm3d(self):
        """The bounded adapter must not masquerade as normal BM3D.

        ``register_bounded_semantic_adapters`` only provides the exact
        ``sigma=0`` identity baseline.  A nonzero sigma activates the
        non-local patch-search/aggregation algorithm and therefore remains
        full-frame.  Exercise the actual adapter entry point so a future
        planner cannot accidentally route normal BM3D through this semantic
        identity adapter merely because an adapter is registered.
        """

        image = np.zeros((19, 23), dtype=np.float32)
        with self.assertRaisesRegex(ValueError, "only supports explicit sigma=0"):
            run_adapter_tiled(
                "bm3d",
                (image,),
                block_size=(7, 9),
                params={"sigma": 12.0},
            )


if __name__ == "__main__":
    unittest.main()
