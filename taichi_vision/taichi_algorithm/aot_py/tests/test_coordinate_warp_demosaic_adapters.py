"""Semantic CPU parity gates for coordinate warps and full Bayer demosaic.

These tests intentionally use odd, non-multiple shapes.  They prove global
coordinate/CFA phase handling only; the adapters are explicit CPU semantic
oracles and must not enable automatic dispatch or native GPU evidence.
"""

from __future__ import annotations

import unittest

import numpy as np

import taichi_vision.taichi_aot as taichi_aot


class CoordinateWarpDemosaicAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.warp = taichi_aot.register_coordinate_warp_adapters()
        cls.demosaic = taichi_aot.register_demosaic_full_adapters()
        cls.cfa_patterns = (
            (0, 1, 1, 2),  # RGGB
            (2, 1, 1, 0),  # BGGR
            (1, 0, 2, 1),  # GRBG
            (1, 2, 0, 1),  # GBRG
        )

    @classmethod
    def tearDownClass(cls):
        taichi_aot.set_block_mode(False, threshold_bytes=512 * 1024 * 1024)

    def test_coordinate_warp_registration_is_semantic_and_fail_closed(self):
        for operation in taichi_aot.COORDINATE_WARP_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                adapter = taichi_aot.registered_block_adapters()[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertTrue(adapter.metadata["coordinate_domain"])
                self.assertTrue(adapter.metadata["semantic_only"])
                self.assertTrue(taichi_aot.can_partition_block(operation, "cpu"))
                # The historical capability table still reports these names
                # as block-capable; registration must not make the stricter
                # automatic-dispatch gate pass.
                self.assertTrue(taichi_aot.can_auto_block(operation, "cpu"))
                self.assertFalse(
                    taichi_aot.can_auto_partition_dispatch(operation, "cpu")
                )
                self.assertFalse(
                    taichi_aot.can_auto_partition_dispatch(operation, "vulkan")
                )

    def test_remap_non_multiple_rgb_maps(self):
        rng = np.random.default_rng(20260810)
        source = rng.random((11, 13, 3), dtype=np.float32)
        map_x = np.linspace(-2.0, 14.0, 9 * 15, dtype=np.float32).reshape(9, 15)
        map_y = np.linspace(-3.0, 12.0, 9 * 15, dtype=np.float32).reshape(9, 15)
        report = taichi_aot.verify_coordinate_warp_parity(
            "remap", (source, map_x, map_y), block_size=(4, 6)
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertFalse(report["native_runtime"])

    def test_remap_with_flow_odd_low_resolution_flow(self):
        rng = np.random.default_rng(20260811)
        source = rng.random((11, 13), dtype=np.float32)
        flow = rng.normal(0.0, 0.25, size=(3, 5, 2)).astype(np.float32)
        report = taichi_aot.verify_coordinate_warp_parity(
            "remap_with_flow",
            (source, flow),
            params={"full_h": 9, "full_w": 15},
            block_size=(4, 6),
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)

    def test_warp_perspective_odd_projective_output(self):
        source = np.arange(11 * 13, dtype=np.float32).reshape(11, 13)
        matrix = np.asarray(
            [[1.0, 0.02, 1.3], [0.01, 1.0, -0.7], [0.0002, 0.0004, 1.0]],
            dtype=np.float32,
        )
        report = taichi_aot.verify_coordinate_warp_parity(
            "warp_perspective",
            (source,),
            params={"dsize": (15, 9), "matrix": matrix},
            block_size=(4, 6),
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)

    def _demosaic_params(self, cfa):
        return {
            "wb": (1.17, 0.93, 1.29, 1.04),
            "levels": (0.03, 1.1),
            "cfa": cfa,
            "cmatrix": np.asarray(
                [[1.1, -0.1, 0.05], [0.02, 0.98, 0.03], [-0.04, 0.11, 1.02]],
                dtype=np.float32,
            ),
        }

    def test_full_demosaic_phase_parity_on_odd_shapes(self):
        rng = np.random.default_rng(20260812)
        source = rng.random((17, 23), dtype=np.float32)
        for operation in taichi_aot.DEMOSAIC_FULL_ADAPTER_OPERATIONS:
            for cfa in self.cfa_patterns:
                with self.subTest(operation=operation, cfa=cfa):
                    params = self._demosaic_params(cfa)
                    if operation == "pure_arm_demosaic":
                        params = {"levels": params["levels"], "cfa": cfa}
                    elif operation.startswith("mlri_admm_"):
                        # The semantic adapter is deliberately restricted to
                        # the zero-iteration phase-safe baseline.  Iterative
                        # MLRI/ADMM remains full-frame.
                        params["iterations"] = 0
                    report = taichi_aot.verify_demosaic_full_parity(
                        operation,
                        (source,),
                        params=params,
                        block_size=(4, 6),
                    )
                    self.assertTrue(report["passed"], report)
                    self.assertEqual(report["max_abs_error"], 0.0)
                    self.assertFalse(report["native_runtime"])

    def test_demosaic_report_preserves_full_frame_and_native_gap(self):
        report = taichi_aot.demosaic_full_partition_gap_report(backend="cpu")
        self.assertEqual(report["status"], "semantic_cpu_only_native_evidence_pending")
        for operation in taichi_aot.DEMOSAIC_FULL_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                record = report["operations"][operation]
                self.assertTrue(record["semantic_cpu_partition"])
                self.assertTrue(record["partition_safe"])
                if operation.startswith("mlri_admm_"):
                    self.assertFalse(record["automatic_safe"])
                else:
                    self.assertTrue(record["automatic_safe"])
                self.assertFalse(record["automatic_dispatch_safe"])
                self.assertFalse(record["native_partition_evidence"])
                self.assertTrue(record["preserves_default_full_frame"])


if __name__ == "__main__":
    unittest.main()
