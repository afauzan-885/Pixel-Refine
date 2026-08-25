"""Restricted semantic CPU identity-frame optical-flow parity gates."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot import (
    OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS,
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    optical_flow_partition_gap_report,
    register_optical_flow_identity_adapters,
    run_optical_flow_identity_partition_tiled,
    verify_optical_flow_identity_parity,
)


class OpticalFlowIdentityAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        register_optical_flow_identity_adapters()

    @staticmethod
    def _params(operation: str) -> dict:
        if operation == "farneback_flow":
            return {
                "pyr_scale": 0.5,
                "num_levels": 1,
                "num_iters": 1,
                "poly_n": 5,
                "flags": 0,
                "flow_init": None,
            }
        return {
            "maxLevel": 0,
            "prevPts": None,
            "nextPts": None,
            "adaptive": False,
            "motion_mode": "fast",
            "dense_mode": "smooth",
        }

    @staticmethod
    def _image() -> np.ndarray:
        rows, cols = np.indices((17, 23), dtype=np.float32)
        return np.ascontiguousarray(
            np.sin(rows * np.float32(0.13))
            + np.cos(cols * np.float32(0.21))
            + rows * np.float32(0.01),
            dtype=np.float32,
        )

    def test_restricted_identity_parity_and_cpu_only_gate(self):
        image = self._image()
        for operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                operation_image = (
                    np.full_like(image, np.float32(3.0))
                    if operation == "block_matching"
                    else image
                )
                params = self._params(operation)
                for block_size in ((5, 7), 9):
                    report = verify_optical_flow_identity_parity(
                        operation,
                        (operation_image, operation_image.copy()),
                        block_size=block_size,
                        params=params,
                    )
                    self.assertTrue(report["passed"], report)
                    self.assertEqual(report["max_abs_error"], 0.0)
                    self.assertTrue(report["identity_input"])
                    self.assertFalse(report["native_runtime"])
                result = run_optical_flow_identity_partition_tiled(
                    operation,
                    (operation_image, operation_image),
                    block_size=(5, 7),
                    params=params,
                )
                self.assertEqual(result.shape, (17, 23, 2))
                self.assertEqual(result.dtype, np.dtype(np.float32))
                self.assertTrue(np.array_equal(result, np.zeros_like(result)))
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_partition_block(operation, "vulkan"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))

    def test_moving_or_unsupported_inputs_fail_closed(self):
        image = self._image()
        changed = image.copy()
        changed[3, 4] += np.float32(0.25)
        for operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                operation_image = (
                    np.full_like(image, np.float32(3.0))
                    if operation == "block_matching"
                    else image
                )
                with self.assertRaises(ValueError):
                    run_optical_flow_identity_partition_tiled(
                        operation,
                        (image, changed),
                        block_size=7,
                        params=self._params(operation),
                    )
                invalid = self._params(operation)
                invalid["maxLevel" if operation != "farneback_flow" else "num_levels"] = 2
                with self.assertRaises(ValueError):
                    run_optical_flow_identity_partition_tiled(
                        operation,
                        (operation_image, operation_image),
                        block_size=7,
                        params=invalid,
                    )

    def test_gap_report_labels_restricted_scope_without_native_promotion(self):
        report = optical_flow_partition_gap_report(backend="cpu")
        for operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
            record = report["operations"][operation]
            self.assertEqual(record["status"], "restricted_semantic_cpu")
            self.assertTrue(record["semantic_cpu_partition"])
            self.assertTrue(record["partition_safe"])
            self.assertFalse(record["automatic_safe"])
            self.assertFalse(record["automatic_dispatch_safe"])
            self.assertFalse(record["native_partition_evidence"])
            self.assertTrue(record["preserves_default_full_frame"])
        self.assertFalse(report["operations"]["ofb"]["semantic_cpu_partition"])
        self.assertTrue(report["semantic_cpu_parity_proven"])
        self.assertFalse(report["native_partition_parity_proven"])


if __name__ == "__main__":
    unittest.main()
