"""Independent CPU parity gates for the deliberately bounded hard-gap adapters."""

from __future__ import annotations

import unittest

import numpy as np

import taichi_vision.taichi_aot as taichi_aot


class BoundedSemanticAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        taichi_aot.register_demosaic_half_adapters()
        taichi_aot.register_demosaic_full_adapters()
        taichi_aot.register_bounded_semantic_adapters()
        cls.cfa = (0, 1, 1, 2)
        cls.params = {
            "wb": (1.1, 0.95, 1.25, 1.03),
            "levels": (0.02, 1.2),
            "cfa": cls.cfa,
            "cmatrix": np.asarray(
                [[1.0, 0.02, -0.01], [0.0, 1.0, 0.0], [0.01, -0.02, 1.0]],
                dtype=np.float32,
            ),
        }
        rows, cols = np.indices((11, 15), dtype=np.float32)
        cls.bayer = np.ascontiguousarray(
            0.1 + rows * np.float32(0.031) + cols * np.float32(0.017),
            dtype=np.float32,
        )

    def test_dcb_half_res_is_exact_on_odd_output_tiles(self):
        for operation in ("dcb_demosaic_half_res", "dcb_demosaic_rgb_half_res"):
            with self.subTest(operation=operation):
                report = taichi_aot.verify_demosaic_half_parity(
                    operation,
                    (self.bayer,),
                    block_size=(3, 4),
                    params=self.params,
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertFalse(report["native_runtime"])
                self.assertTrue(taichi_aot.can_partition_block(operation, "cpu"))
                self.assertFalse(taichi_aot.can_auto_block(operation, "cpu"))

    def test_mlri_zero_iteration_subset_is_exact_and_nonzero_fails_closed(self):
        operations = (
            "mlri_admm_demosaic",
            "mlri_admm_demosaic_1channel",
            "mlri_admm_demosaic_3channel",
            "mlri_admm_demosaic_half_res",
            "mlri_admm_demosaic_rgb_half_res",
        )
        for operation in operations:
            with self.subTest(operation=operation):
                params = dict(self.params, iterations=0)
                if operation.endswith("_1channel") or operation.endswith("_3channel"):
                    params.pop("cmatrix", None)
                    if operation.endswith("_3channel"):
                        params["cmatrix"] = self.params["cmatrix"]
                report = (
                    taichi_aot.verify_demosaic_half_parity
                    if "half_res" in operation
                    else taichi_aot.verify_demosaic_full_parity
                )(
                    operation,
                    (self.bayer,),
                    block_size=(3, 4),
                    params=params,
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                invalid = dict(params, iterations=1)
                runner = (
                    taichi_aot.run_demosaic_half_tiled
                    if "half_res" in operation
                    else taichi_aot.run_demosaic_full_tiled
                )
                with self.assertRaises(ValueError):
                    runner(operation, (self.bayer,), block_size=(3, 4), params=invalid)

    def test_bm3d_zero_noise_identity_is_exact_and_nonzero_fails_closed(self):
        image = np.ascontiguousarray(
            np.sin(np.indices((13, 17), dtype=np.float32)[0] * np.float32(0.17)),
            dtype=np.float32,
        )
        report = taichi_aot.verify_adapter_parity(
            "bm3d", (image,), block_size=(5, 7), params={"sigma": 0.0}
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertTrue(taichi_aot.can_partition_block("bm3d", "cpu"))
        self.assertFalse(taichi_aot.can_auto_block("bm3d", "cpu"))
        with self.assertRaises(ValueError):
            taichi_aot.run_adapter_tiled(
                "bm3d", (image,), block_size=5, params={"sigma": 0.1}
            )


if __name__ == "__main__":
    unittest.main()
