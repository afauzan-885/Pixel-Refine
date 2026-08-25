"""Semantic CPU parity gates for staged phase-correlation block execution."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    PHASE_CORRELATION_ADAPTER_OPERATIONS,
    _phase_peak_reduce,
    register_phase_correlation_block_adapters,
    run_phase_correlation_partition_tiled,
    verify_phase_correlation_parity,
)


class PhaseCorrelationAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_phase_correlation_block_adapters()

    def test_registration_is_map_reduce_and_fail_closed(self):
        self.assertEqual(set(PHASE_CORRELATION_ADAPTER_OPERATIONS), {"phase_correlation"})
        adapter = registered_block_adapters()["phase_correlation"]
        self.assertTrue(adapter.partition_ready)
        self.assertEqual(adapter.partition_strategy.value, "map_reduce")
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["output_domain"])
        self.assertEqual(
            adapter.metadata["output_domain_kind"],
            "correlation_surface_to_shift_tuple",
        )
        self.assertTrue(can_partition_block("phase_correlation", "cpu"))
        self.assertFalse(can_auto_block("phase_correlation", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("phase_correlation", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("phase_correlation", "vulkan"))

    def test_non_multiple_dimensions_parity_with_and_without_hanning(self):
        rows, cols = np.indices((13, 19), dtype=np.float32)
        reference = (
            np.sin(rows * np.float32(0.17))
            + np.cos(cols * np.float32(0.23))
            + np.float32(0.01) * rows * cols
        ).astype(np.float32)
        comparison = np.roll(reference, shift=(2, -3), axis=(0, 1))
        for use_hanning in (False, True):
            with self.subTest(use_hanning=use_hanning):
                report = verify_phase_correlation_parity(
                    (reference, comparison),
                    block_size=(5, 7),
                    params={"use_hanning": use_hanning},
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertEqual(report["frequency_shape"], [16, 32])
                self.assertEqual(report["correlation_shape"], [13, 19])
                self.assertFalse(report["native_runtime"])
                result = run_phase_correlation_partition_tiled(
                    (reference, comparison),
                    block_size=(4, 6),
                    params={"use_hanning": use_hanning},
                )
                self.assertEqual(len(result), 3)
                self.assertTrue(np.isfinite(np.asarray(result)).all())

    def test_deterministic_first_peak_and_unsupported_inputs_fail_closed(self):
        reference = np.zeros((9, 14), dtype=np.float32)
        reference[2:5, 4:8] = 1.0
        comparison = np.roll(reference, shift=(1, 2), axis=(0, 1))
        first = run_phase_correlation_partition_tiled(
            (reference, comparison), block_size=(3, 5), params={"use_hanning": False}
        )
        second = run_phase_correlation_partition_tiled(
            (reference, comparison), block_size=(4, 6), params={"use_hanning": False}
        )
        np.testing.assert_array_equal(np.asarray(first), np.asarray(second))
        self.assertTrue(np.isfinite(np.asarray(first)).all())

        with self.assertRaises(ValueError):
            run_phase_correlation_partition_tiled(
                (reference, comparison[:8]), block_size=4, params={"use_hanning": False}
            )
        with self.assertRaises(ValueError):
            run_phase_correlation_partition_tiled(
                (reference.reshape(-1), comparison.reshape(-1)), block_size=4,
                params={"use_hanning": False},
            )
        with self.assertRaises(ValueError):
            run_phase_correlation_partition_tiled(
                (np.ones((1, 8), dtype=np.float32), np.ones((1, 8), dtype=np.float32)),
                block_size=4,
                params={"use_hanning": True},
            )
        with self.assertRaises(ValueError):
            run_phase_correlation_partition_tiled(
                (reference, comparison), block_size=5000, params={"use_hanning": False}
            )
        with self.assertRaises(ValueError):
            run_phase_correlation_partition_tiled(
                (reference, comparison), block_size=4,
                params={"use_hanning": False, "max_shift": -1},
            )

    def test_peak_reducer_rejects_nonfinite_surface_and_invalid_source_shape(self):
        surface = np.zeros((8, 8), dtype=np.float32)
        surface[2, 3] = 1.0
        with self.assertRaises(ValueError):
            _phase_peak_reduce(
                surface.copy().astype(np.float32) + np.where(
                    np.indices(surface.shape)[0] == 0, np.nan, 0.0
                ),
                (8, 8),
                block_size=3,
            )
        with self.assertRaises(ValueError):
            _phase_peak_reduce(surface, (9, 8), block_size=3)
        with self.assertRaises(ValueError):
            _phase_peak_reduce(surface, (0, 8), block_size=3)


if __name__ == "__main__":
    unittest.main()
