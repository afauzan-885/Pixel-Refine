"""Semantic parity gates for the bounded local/stencil adapter tranche."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    LOCAL_STENCIL_ADAPTER_OPERATIONS,
    register_local_stencil_block_adapters,
    verify_adapter_parity,
    local_stencil_contract_report,
)


class LocalStencilAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_local_stencil_block_adapters()

    def test_registration_is_bounded_and_native_gate_is_fail_closed(self):
        expected = {
            "morphology",
            "filter2d",
            "threshold",
            "normalize",
            "joint_bilateral_guidance",
            "enhance_image",
            "joint_bilateral_filter",
            "guided_filter",
            "non_local_means",
        }
        self.assertEqual(set(LOCAL_STENCIL_ADAPTER_OPERATIONS), expected)
        self.assertTrue(expected.issubset(self.adapters))
        for operation in expected:
            adapter = registered_block_adapters()[operation]
            self.assertTrue(adapter.partition_ready)
            self.assertTrue(adapter.metadata["semantic_only"])
            self.assertTrue(can_auto_block(operation, "cpu"))
            # CPU semantic dispatch is qualified by this adapter; native
            # evidence is a separate, stricter gate below the runtime probe.
            self.assertTrue(can_auto_partition_dispatch(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))
            self.assertFalse(
                can_auto_partition_dispatch(
                    operation,
                    "cpu",
                    require_native_evidence=True,
                    device="CPU (x86_64 Windows)",
                )
            )

    def test_full_frame_vs_halo_tiled_semantic_parity(self):
        rng = np.random.default_rng(20260810)
        source = rng.random((17, 21), dtype=np.float32)
        guide = rng.random((17, 21), dtype=np.float32)
        blurred = rng.random((17, 21), dtype=np.float32)
        lut = np.linspace(0.0, 1.0, 256, dtype=np.float32)
        kernel = np.asarray(
            [[0.0, 1.0, 0.0], [1.0, 4.0, 1.0], [0.0, 1.0, 0.0]],
            dtype=np.float32,
        ) / np.float32(8.0)
        cases = (
            ("morphology", (source,), {"operation": "dilate"}),
            ("filter2d", (source,), {"kernel": kernel}),
            (
                "threshold",
                (source,),
                {"threshold": 0.5, "max_value": 1.0, "mode": 0},
            ),
            (
                "normalize",
                (source,),
                {
                    "mode": "MINMAX",
                    "alpha": 0.0,
                    "beta": 1.0,
                    "src_min": float(source.min()),
                    "src_max": float(source.max()),
                },
            ),
            (
                "joint_bilateral_guidance",
                (source, guide),
                {"radius": 1, "preset": "medium"},
            ),
            (
                "enhance_image",
                (source, blurred),
                {
                    "lut": lut,
                    "micro_contrast": 1.2,
                    "clarity": 0.2,
                    "noise_coring": 0.05,
                },
            ),
            (
                "joint_bilateral_filter",
                (source, guide),
                {"radius": 1, "preset": "medium"},
            ),
            (
                "guided_filter",
                (guide, source),
                {"radius": 1, "epsilon": 1.0e-4},
            ),
            (
                "non_local_means",
                (source,),
                {
                    "h_param": 10.0,
                    "search_radius": 1,
                    "patch_radius": 1,
                    "refinement_strength": 1.0,
                    "shrinkage_strength": 1.0,
                },
            ),
        )
        for operation, inputs, params in cases:
            with self.subTest(operation=operation):
                report = verify_adapter_parity(
                    operation, inputs, block_size=(5, 7), params=params
                )
                self.assertTrue(report["passed"], report)
                self.assertLessEqual(report["max_abs_error"], 1.0e-6)
                self.assertEqual(report["backend"], "cpu")
                self.assertFalse(report["native_runtime"])

    def test_contract_report_is_read_only_and_separates_cpu_from_native(self):
        report = local_stencil_contract_report(
            "filter2d", backend="vulkan", device="Intel(R) UHD Graphics 620"
        )
        self.assertEqual(report["operation"], "filter2d")
        self.assertTrue(report["semantic_cpu_partition"])
        self.assertFalse(report["partition_safe"])
        self.assertFalse(report["automatic_dispatch_safe"])
        self.assertEqual(report["native_evidence_records"], [])
        self.assertFalse(report["registry_mutated"])
        self.assertFalse(report["runtime_dispatch_changed"])


if __name__ == "__main__":
    unittest.main()
