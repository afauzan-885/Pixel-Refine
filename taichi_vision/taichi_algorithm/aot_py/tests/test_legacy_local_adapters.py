"""Parity gates for the legacy local/stencil adapter tranche.

These tests exercise only the deterministic CPU semantic contracts.  A green
result does not qualify Vulkan/OpenGL/CUDA dispatch; native promotion still
requires a target/device-scoped probe.
"""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_partition_dispatch,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    LEGACY_LOCAL_ADAPTER_OPERATIONS,
    register_legacy_local_block_adapters,
    verify_adapter_parity,
)


class LegacyLocalAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_legacy_local_block_adapters()

    def test_registration_is_explicit_and_native_gate_is_closed(self):
        expected = set(LEGACY_LOCAL_ADAPTER_OPERATIONS)
        self.assertEqual(
            expected,
            {
                "copy_field",
                "gaussian_blur",
                "box_filter",
                "median_filter",
                "sobel",
                "laplacian",
                "smooth_flow",
                "highlight_recovery",
                "cvtColor_extended",
            },
        )
        self.assertTrue(expected.issubset(self.adapters))
        for operation in expected:
            adapter = registered_block_adapters()[operation]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertFalse(
                can_auto_partition_dispatch(
                    operation,
                    "cpu",
                    require_native_evidence=True,
                    device="CPU (x86_64 Windows)",
                )
            )

    def test_full_frame_vs_tiled_parity_for_scalar_and_flow_paths(self):
        rng = np.random.default_rng(20260810)
        scalar = rng.random((9, 11), dtype=np.float32)
        rgb = rng.random((9, 11, 3), dtype=np.float32) * np.float32(1.2)
        flow = rng.random((9, 11, 2), dtype=np.float32)
        cases = (
            ("copy_field", (scalar,), {}),
            ("gaussian_blur", (scalar,), {"sigma": 1.2, "kernel_size": 5}),
            ("box_filter", (scalar,), {"kernel_size": 5}),
            ("median_filter", (scalar,), {"kernel_size": 3}),
            ("sobel", (scalar,), {}),
            ("laplacian", (scalar,), {}),
            ("smooth_flow", (flow,), {"sigma": 1.0, "kernel_size": 5}),
            (
                "highlight_recovery",
                (rgb,),
                {"wb_r": 1.8, "wb_g": 1.0, "wb_b": 1.4, "strength": 0.7},
            ),
        )
        for operation, inputs, params in cases:
            with self.subTest(operation=operation):
                report = verify_adapter_parity(
                    operation, inputs, block_size=(4, 5), params=params
                )
                self.assertTrue(report["passed"], report)
                self.assertLessEqual(report["max_abs_error"], 1.0e-6)
                self.assertFalse(report["native_runtime"])

    def test_extended_color_codes_are_partition_invariant(self):
        rng = np.random.default_rng(20260811)
        source = rng.random((9, 11, 3), dtype=np.float32) * np.float32(255.0)
        for code in (40, 54, 36, 38, 44, 55, 56):
            with self.subTest(code=code):
                report = verify_adapter_parity(
                    "cvtColor_extended",
                    (source,),
                    block_size=(4, 5),
                    params={"code": code},
                )
                self.assertTrue(report["passed"], report)
                self.assertLessEqual(report["max_abs_error"], 1.0e-6)

    def test_unsupported_variants_fail_closed(self):
        source = np.ones((7, 8), dtype=np.float32)
        flow = np.ones((7, 8, 2), dtype=np.float32)
        with self.assertRaises(ValueError):
            verify_adapter_parity(
                "gaussian_blur", (source,), params={"sigma": 1.0, "kernel_size": 35}
            )
        with self.assertRaises(ValueError):
            verify_adapter_parity(
                "median_filter", (source,), params={"kernel_size": 5}
            )
        with self.assertRaises(ValueError):
            verify_adapter_parity(
                "smooth_flow", (flow,), params={"sigma": 1.0, "kernel_size": 35}
            )
        with self.assertRaises(ValueError):
            verify_adapter_parity(
                "cvtColor_extended",
                (np.ones((7, 8, 3), dtype=np.float32),),
                params={"code": 999},
            )


if __name__ == "__main__":
    unittest.main()
