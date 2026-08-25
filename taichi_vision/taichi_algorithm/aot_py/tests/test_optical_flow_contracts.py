"""Fail-closed audit gates for dense optical-flow block execution.

The maintained flow wrappers have historical tile executors, but their
multi-stage/iterative semantics are not yet covered by a deterministic CPU
full-vs-tiled proof.  These tests make that gap explicit and protect the
default full-frame dispatch while a future parity tranche is developed.
"""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot import (
    OPTICAL_FLOW_CONTRACT_OPERATIONS,
    OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS,
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    optical_flow_partition_gap_report,
    operation_contract,
    register_optical_flow_identity_adapters,
)


class OpticalFlowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_optical_flow_identity_adapters()

    def test_gap_report_covers_all_flow_families(self):
        report = optical_flow_partition_gap_report(backend="cpu")
        expected = (
            "farneback_flow",
            "lucas_kanade",
            "block_matching",
            "ofb",
        )
        self.assertEqual(OPTICAL_FLOW_CONTRACT_OPERATIONS, expected)
        self.assertEqual(report["operation_order"], list(expected))
        self.assertEqual(set(report["operations"]), set(expected))
        self.assertEqual(report["default_mode"], "full_frame")
        # The identity-frame semantic adapters may already be lazily
        # registered by another test module.  Their restricted status is
        # deterministic and must not be treated as moving-flow evidence.
        self.assertEqual(
            report["semantic_cpu_parity_proven"],
            bool(OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS),
        )
        self.assertFalse(report["native_partition_parity_proven"])
        self.assertFalse(report["runtime_dispatch_changed"])

    def test_every_flow_operation_fails_closed_for_partition_dispatch(self):
        report = optical_flow_partition_gap_report(backend="cpu")
        for operation in OPTICAL_FLOW_CONTRACT_OPERATIONS:
            with self.subTest(operation=operation):
                record = report["operations"][operation]
                if operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
                    self.assertEqual(record["status"], "restricted_semantic_cpu")
                    self.assertTrue(record["semantic_cpu_partition"])
                else:
                    self.assertEqual(record["status"], "gap_fail_closed")
                    self.assertFalse(record["semantic_cpu_partition"])
                self.assertTrue(record["preserves_default_full_frame"])
                self.assertFalse(record["native_partition_evidence"])
                self.assertFalse(record["native_runtime"])
                self.assertFalse(record["automatic_safe"])
                self.assertEqual(
                    record["partition_safe"],
                    operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS,
                )
                self.assertFalse(record["automatic_dispatch_safe"])
                self.assertGreaterEqual(len(record["blocked_reasons"]), 2)
                self.assertGreaterEqual(len(record["required_evidence"]), 2)
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertEqual(
                    can_partition_block(operation, "cpu"),
                    operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS,
                )
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))

    def test_report_exposes_executor_evidence_without_promoting_parity(self):
        report = optical_flow_partition_gap_report(backend="vulkan")
        for operation in ("farneback_flow", "lucas_kanade", "block_matching"):
            with self.subTest(operation=operation):
                record = report["operations"][operation]
                self.assertIsNotNone(record["legacy_executor"])
                self.assertEqual(record["legacy_evidence_status"], "executor_only")
                self.assertFalse(record["automatic_dispatch_safe"])
        ofb = report["operations"]["ofb"]
        self.assertIsNone(ofb["legacy_executor"])
        self.assertEqual(ofb["path"], "global")

    def test_alias_and_subset_reports_are_read_only(self):
        before = {
            name: operation_contract(name).as_dict()
            for name in ("farneback_flow", "lucas_kanade", "block_matching", "ofb")
        }
        report = optical_flow_partition_gap_report(
            ("lucasKanade", "block_matching", "lucas_kanade"),
            backend="cpu",
            device="synthetic",
        )
        self.assertEqual(
            report["operation_order"], ["lucas_kanade", "block_matching"]
        )
        self.assertEqual(report["backend"], "cpu")
        self.assertEqual(report["device"], "synthetic")
        after = {
            name: operation_contract(name).as_dict()
            for name in ("farneback_flow", "lucas_kanade", "block_matching", "ofb")
        }
        self.assertEqual(before, after)

    def test_unknown_operation_is_rejected_without_mutating_registry(self):
        with self.assertRaises(ValueError):
            optical_flow_partition_gap_report("unknown_flow", backend="cpu")


if __name__ == "__main__":
    unittest.main()
