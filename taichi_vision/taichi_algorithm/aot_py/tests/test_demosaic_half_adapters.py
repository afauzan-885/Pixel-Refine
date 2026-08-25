"""CPU parity gates for fused Hamilton/ARM 2x2 auxiliary demosaic paths."""

from __future__ import annotations

import unittest

import numpy as np

import taichi_vision.taichi_aot as taichi_aot


class DemosaicHalfAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = taichi_aot.register_demosaic_half_adapters()
        cls.wb = (1.17, 0.93, 1.29, 1.04)
        cls.levels = (0.03, 1.1)
        cls.cmatrix = np.asarray(
            [[1.1, -0.1, 0.05], [0.02, 0.98, 0.03], [-0.04, 0.11, 1.02]],
            dtype=np.float32,
        )
        cls.patterns = (
            (0, 1, 1, 2),  # RGGB
            (2, 1, 1, 0),  # BGGR
            (1, 0, 2, 1),  # GRBG
            (1, 2, 0, 1),  # GBRG
        )

    @classmethod
    def tearDownClass(cls):
        # Do not leak an explicit block policy into another test module.
        taichi_aot.set_block_mode(False, threshold_bytes=512 * 1024 * 1024)

    def _params(self, cfa):
        return {
            "wb": self.wb,
            "levels": self.levels,
            "cfa": cfa,
            "cmatrix": self.cmatrix,
        }

    def _source(self, shape, cfa):
        return np.random.default_rng(sum(shape) + sum(cfa)).random(
            shape, dtype=np.float32
        )

    def test_semantic_adapter_exact_on_odd_non_multiple_cfa_shapes(self):
        operations = (
            "hamilton_demosaic_half_res",
            "hamilton_demosaic_rgb_half_res",
            "arm_demosaic_half_res",
            "arm_demosaic_rgb_half_res",
        )
        for operation in operations:
            for cfa in self.patterns:
                with self.subTest(operation=operation, cfa=cfa):
                    report = taichi_aot.verify_demosaic_half_parity(
                        operation,
                        (self._source((17, 23), cfa),),
                        block_size=(4, 6),
                        params=self._params(cfa),
                    )
                    self.assertTrue(report["passed"], report)
                    self.assertEqual(report["max_abs_error"], 0.0)
                    self.assertFalse(report["native_runtime"])

    def test_public_full_frame_and_existing_half_blockwise_are_exact(self):
        # This invokes the maintained wrappers twice: with block mode disabled
        # and with the existing ``_demosaic_half_blockwise`` path enabled.
        operations = (
            "hamilton_demosaic_half_res",
            "hamilton_demosaic_rgb_half_res",
            "arm_demosaic_half_res",
            "arm_demosaic_rgb_half_res",
        )
        for operation in operations:
            for cfa in self.patterns:
                with self.subTest(operation=operation, cfa=cfa):
                    source = self._source((17, 23), cfa)
                    args = [source, *self.wb]
                    if "rgb_half_res" in operation:
                        args.append(self.cmatrix)
                    args.extend((*self.levels, *cfa))
                    taichi_aot.set_block_mode(
                        False, size=(4, 6), threshold_bytes=0
                    )
                    full = getattr(taichi_aot, operation)(*args)
                    taichi_aot.set_block_mode(
                        True, size=(4, 6), threshold_bytes=0
                    )
                    tiled = getattr(taichi_aot, operation)(*args)
                    np.testing.assert_array_equal(full, tiled)

    def test_dcb_and_mlri_half_res_use_bounded_semantic_contract(self):
        report = taichi_aot.demosaic_half_partition_gap_report(backend="cpu")
        for operation in (
            "dcb_demosaic_half_res",
            "dcb_demosaic_rgb_half_res",
        ):
            with self.subTest(operation=operation):
                record = report["operations"][operation]
                self.assertEqual(record["status"], "semantic_cpu_qualified")
                self.assertTrue(record["adapter_registered"])
                self.assertTrue(record["partition_safe"])
                self.assertTrue(record["preserves_default_full_frame"])

    def test_native_and_automatic_gates_remain_disabled(self):
        report = taichi_aot.demosaic_half_partition_gap_report(backend="cpu")
        for operation in self.adapters:
            with self.subTest(operation=operation):
                record = report["operations"][operation]
                self.assertTrue(record["semantic_cpu_partition"])
                self.assertTrue(record["partition_safe"])
                self.assertFalse(record["automatic_safe"])
                self.assertFalse(record["automatic_dispatch_safe"])
                self.assertFalse(record["native_partition_evidence"])
                self.assertFalse(record["native_runtime"])


if __name__ == "__main__":
    unittest.main()
