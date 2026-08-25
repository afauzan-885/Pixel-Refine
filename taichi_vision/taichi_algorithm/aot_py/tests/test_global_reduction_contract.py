"""Fail-closed global reduction contract tests."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot import (
    GLOBAL_REDUCTION_CONTRACT_OPERATIONS,
    global_reduction_partition_gap_report,
)
from taichi_vision.taichi_aot.block import registered_block_adapters


class GlobalReductionContractTests(unittest.TestCase):
    def test_reductions_are_audited_without_native_promotion(self):
        report = global_reduction_partition_gap_report(backend="cuda")
        self.assertEqual(report["operation_order"], list(GLOBAL_REDUCTION_CONTRACT_OPERATIONS))
        self.assertEqual(report["default_mode"], "full_frame")
        self.assertFalse(report["native_partition_parity_proven"])
        self.assertFalse(report["runtime_dispatch_changed"])
        for record in report["operations"].values():
            self.assertEqual(record["reduction_order"], "row-major deterministic merge")
            self.assertFalse(record["native_runtime"])
            self.assertTrue(record["preserves_default_full_frame"])
            self.assertGreaterEqual(len(record["required_evidence"]), 3)

    def test_histogram_is_audited_and_remains_fail_closed(self):
        """Histogram has a semantic map/reduce adapter but no native proof."""

        # Other contract tests may have registered the optional semantic
        # adapter in this process.  The diagnostic must be read-only: it may
        # observe that registration, but must not create or remove entries.
        before = dict(registered_block_adapters())
        report = global_reduction_partition_gap_report(
            ("histogram_aot",), backend="cuda", device="NVIDIA GeForce MX150"
        )
        after = dict(registered_block_adapters())
        record = report["operations"]["histogram"]
        self.assertEqual(report["operation_order"], ["histogram"])
        self.assertEqual(set(after), set(before))
        # Adapter registration is semantic-only and backend capability is
        # still not sufficient for native promotion on CUDA.
        self.assertEqual(
            record["adapter_registered"], "histogram" in before
        )
        self.assertEqual(
            record["semantic_cpu_partition"], "histogram" in before
        )
        self.assertFalse(record["native_partition_evidence"])
        self.assertFalse(record["native_runtime"])
        self.assertTrue(record["preserves_default_full_frame"])
        self.assertIn(record["status"], {"gap_fail_closed", "semantic_cpu_qualified"})

    def test_subset_is_exact_device_scoped_and_read_only(self):
        report = global_reduction_partition_gap_report(
            ("otsu_threshold", "otsu_threshold"),
            backend="vulkan",
            device="Intel(R) UHD Graphics 620",
        )
        self.assertEqual(report["operation_order"], ["otsu_threshold"])
        self.assertEqual(report["operations"]["otsu_threshold"]["native_evidence_records"], [])

    def test_unknown_reduction_rejected(self):
        with self.assertRaises(ValueError):
            global_reduction_partition_gap_report("unknown_reduction", backend="cpu")


if __name__ == "__main__":
    unittest.main()
