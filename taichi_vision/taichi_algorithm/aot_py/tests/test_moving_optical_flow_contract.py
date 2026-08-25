"""Moving-frame optical-flow must remain fail-closed until parity exists."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot import (
    OPTICAL_FLOW_CONTRACT_OPERATIONS,
    moving_optical_flow_partition_gap_report,
    verify_moving_flow_translation_contract,
    aggregate_native_moving_flow_candidates,
    qualify_native_moving_flow_candidates,
)
from taichi_vision.taichi_aot.native_evidence import native_partition_evidence_snapshot


class MovingOpticalFlowContractTests(unittest.TestCase):
    def test_native_candidate_qualification_is_review_only(self):
        record = {
            "backend": "vulkan", "device": "Intel(R) UHD Graphics 620",
            "native_runtime": True, "block_selected": True,
            "shape": [48, 48, 2], "finite": True,
            "max_abs_error_vs_same_backend_full": 0.0,
            "repeat_max_abs_error": 0.0, "deterministic_merge": True,
            "median_translation": [1.0, 1.0], "evidence_status": "candidate_only",
            "block_plan": {"contract": {"partition_qualified": True, "automatic_safe": True}},
        }
        report = qualify_native_moving_flow_candidates(
            [record], expected_targets=[("vulkan", "Intel(R) UHD Graphics 620")],
            expected_translation=(1.0, 1.0), shape=(48, 48, 2),
        )
        self.assertTrue(report["promotion_eligible"])
        self.assertEqual(report["status"], "candidate_ready_for_review")
        self.assertEqual(report["evidence_status"], "candidate_only")
        self.assertFalse(report["automatic_safe"])
        self.assertFalse(report["parity_qualified"])
        self.assertFalse(report["dispatch_promotion"])
        self.assertFalse(report["registry_mutated"])
        self.assertFalse(report["dispatch_changed"])

    def test_native_candidate_qualification_accepts_opt_in_verified_contract_only(self):
        record = {
            "backend": "vulkan", "device": "Intel(R) UHD Graphics 620",
            "native_runtime": True, "block_selected": True, "shape": [48, 48, 2],
            "finite": True, "max_abs_error_vs_same_backend_full": 0.0,
            "repeat_max_abs_error": 0.0, "deterministic_merge": True,
            "median_translation": [1.0, 1.0], "evidence_status": "candidate_only",
        }
        without = qualify_native_moving_flow_candidates(
            [record], expected_targets=[("vulkan", "Intel(R) UHD Graphics 620")],
            expected_translation=(1.0, 1.0), shape=(48, 48, 2),
            verified_contracts={("vulkan", "Intel(R) UHD Graphics 620"): {"partition_qualified": True, "automatic_safe": True, "operation": "farneback_flow"}},
        )
        self.assertTrue(without["promotion_eligible"])
        self.assertFalse(without["registry_mutated"])
        wrong = qualify_native_moving_flow_candidates(
            [record], expected_targets=[("vulkan", "Intel(R) UHD Graphics 620")],
            verified_contracts={("vulkan", "Intel(R) UHD Graphics 620"): {"partition_qualified": True, "automatic_safe": True, "operation": "resize"}},
        )
        self.assertFalse(wrong["promotion_eligible"])
        self.assertTrue(any("not farneback_flow" in item for item in wrong["reasons"]))

    def test_native_candidate_qualification_reports_exact_metadata_reason(self):
        record = {
            "backend": "vulkan", "device": "Intel(R) UHD Graphics 620",
            "native_runtime": True, "block_selected": True,
            "shape": [48, 48, 2], "finite": True,
            "max_abs_error_vs_same_backend_full": 0.0,
            "repeat_max_abs_error": 0.0, "deterministic_merge": True,
            "median_translation": [1.0, 1.0],
        }
        report = qualify_native_moving_flow_candidates(
            [record], expected_targets=[("vulkan", "Intel(R) UHD Graphics 620")],
            expected_translation=(1.0, 1.0), shape=(48, 48, 2),
        )
        self.assertFalse(report["promotion_eligible"])
        self.assertEqual(report["status"], "fail_closed")
        self.assertTrue(any("not explicitly candidate_only" in item for item in report["reasons"]))
        self.assertFalse(report["registry_mutated"])
    def test_native_candidate_aggregate_requires_exact_targets_and_repeat(self):
        record = {
            "backend": "vulkan",
            "device": "Intel(R) UHD Graphics 620",
            "native_runtime": True,
            "block_selected": True,
            "shape": [48, 48, 2],
            "finite": True,
            "max_abs_error_vs_same_backend_full": 0.0,
            "repeat_max_abs_error": 0.0,
            "deterministic_merge": True,
            "median_translation": [1.0, 1.0],
        }
        report = aggregate_native_moving_flow_candidates(
            [record],
            expected_targets=[("vulkan", "Intel(R) UHD Graphics 620")],
            expected_translation=(1.0, 1.0),
            shape=(48, 48, 2),
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["evidence_status"], "candidate_only")
        self.assertFalse(report["registry_mutated"])

    def test_native_candidate_aggregate_fails_closed_on_missing_target_or_repeat(self):
        record = {
            "backend": "opengl", "device": "NVIDIA GeForce MX150",
            "native_runtime": True, "block_selected": True,
            "shape": [64, 64, 2], "finite": True,
            "max_abs_error_vs_same_backend_full": 0.0,
            "median_translation": [2.0, 1.0],
        }
        report = aggregate_native_moving_flow_candidates(
            [record],
            expected_targets=[("opengl", "NVIDIA GeForce MX150"), ("vulkan", "Intel(R) UHD Graphics 620")],
            expected_translation=(2.0, 1.0),
            shape=(64, 64, 2),
        )
        self.assertFalse(report["passed"])
        self.assertEqual(report["evidence_status"], "fail_closed")
        self.assertEqual(len(report["missing_targets"]), 1)
        self.assertFalse(report["registry_mutated"])
    def test_synthetic_translation_gate_accepts_only_complete_observation(self):
        full = __import__("numpy").zeros((5, 7, 2), dtype="float32")
        full[..., 0] = 2.0
        full[..., 1] = -1.0
        tiled = full.copy()
        report = verify_moving_flow_translation_contract(
            full,
            tiled,
            expected_translation=(2.0, -1.0),
            block_selected=True,
            backend="cpu",
            device="CPU (x86_64 Windows)",
            halo=4,
            pyramid_levels=1,
            deterministic_merge=True,
            same_backend=True,
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["evidence_status"], "candidate_only")
        self.assertFalse(report["native_runtime"])
        self.assertEqual(report["halo"], 4)
        self.assertTrue(report["deterministic_merge"])

    def test_synthetic_translation_gate_rejects_missing_block_or_bad_motion(self):
        np = __import__("numpy")
        full = np.zeros((5, 7, 2), dtype="float32")
        full[..., 0] = 2.0
        bad = full.copy()
        bad[..., 0] = 3.0
        missing_block = verify_moving_flow_translation_contract(
            full,
            full,
            expected_translation=(2.0, -1.0),
            block_selected=False,
            backend="cuda",
            device="NVIDIA GeForce MX150",
            deterministic_merge=True,
            same_backend=True,
        )
        bad_motion = verify_moving_flow_translation_contract(
            full,
            bad,
            expected_translation=(2.0, -1.0),
            block_selected=True,
            backend="cuda",
            device="NVIDIA GeForce MX150",
            deterministic_merge=True,
            same_backend=True,
        )
        self.assertFalse(missing_block["passed"])
        self.assertFalse(bad_motion["passed"])
        self.assertEqual(missing_block["evidence_status"], "fail_closed")
        self.assertEqual(bad_motion["evidence_status"], "fail_closed")

    def test_boundary_exchange_requirements_fail_closed(self):
        np = __import__("numpy")
        flow = np.zeros((3, 3, 2), dtype="float32")
        report = verify_moving_flow_translation_contract(
            flow,
            flow,
            expected_translation=(0.0, 0.0),
            block_selected=True,
            backend="vulkan",
            device="Intel(R) UHD Graphics 620",
            halo=0,
            pyramid_levels=1,
            deterministic_merge=False,
            same_backend=True,
        )
        self.assertFalse(report["passed"])
        self.assertFalse(report["deterministic_merge"])

    def test_all_moving_families_are_explicitly_fail_closed(self):
        report = moving_optical_flow_partition_gap_report(backend="cpu")
        self.assertEqual(report["status"], "fail_closed_until_moving_parity_evidence")
        self.assertEqual(
            report["operation_order"], list(OPTICAL_FLOW_CONTRACT_OPERATIONS)
        )
        self.assertEqual(report["default_mode"], "full_frame")
        self.assertFalse(report["semantic_cpu_parity_proven"])
        self.assertFalse(report["native_partition_parity_proven"])
        for record in report["operations"].values():
            self.assertTrue(record["moving_frame"])
            self.assertFalse(record["identity_frame_specialization"])
            self.assertEqual(record["status"], "moving_gap_fail_closed")
            self.assertFalse(record["semantic_cpu_partition"])
            self.assertFalse(record["native_partition_evidence"])
            self.assertTrue(record["preserves_default_full_frame"])
            self.assertIn("moving-frame coarse-to-fine parity is not proven", record["blocked_reasons"])

    def test_subset_and_exact_device_scope_are_read_only(self):
        before = native_partition_evidence_snapshot()
        report = moving_optical_flow_partition_gap_report(
            ("lucas_kanade", "block_matching", "lucas_kanade"),
            backend="cuda",
            device="NVIDIA GeForce MX150",
        )
        self.assertEqual(report["operation_order"], ["lucas_kanade", "block_matching"])
        self.assertEqual(report["backend"], "cuda")
        self.assertEqual(report["device"], "NVIDIA GeForce MX150")
        self.assertFalse(report["native_partition_parity_proven"])
        for record in report["operations"].values():
            self.assertEqual(record["native_evidence_records"], [])
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_unknown_flow_is_rejected(self):
        with self.assertRaises(ValueError):
            moving_optical_flow_partition_gap_report("unknown_flow", backend="cpu")


if __name__ == "__main__":
    unittest.main()
