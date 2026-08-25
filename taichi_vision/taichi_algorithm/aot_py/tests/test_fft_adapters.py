"""Semantic parity gates for staged FFT block adapters.

FFT remains a global operation: these tests only qualify the deterministic
CPU NumPy stage contract and explicitly verify that automatic/native dispatch
stays fail-closed.  They do not exercise a Taichi bridge or claim GPU support.
"""

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
    FFT_ADAPTER_OPERATIONS,
    register_fft_block_adapters,
    run_fft_partition_tiled,
    verify_fft_parity,
)


class FFTAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_fft_block_adapters()

    def test_registration_is_multistage_and_fail_closed(self):
        self.assertEqual(set(FFT_ADAPTER_OPERATIONS), {"fft", "fft2", "ifft2"})
        for operation in FFT_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                adapter = registered_block_adapters()[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertEqual(adapter.partition_strategy.value, "multi_stage")
                self.assertTrue(adapter.metadata["semantic_only"])
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_forward_padding_and_separable_parity_non_power_dimensions(self):
        rows, cols = np.indices((5, 7), dtype=np.float32)
        source = (0.25 * rows + 0.75 * cols + np.sin(rows + cols)).astype(np.float32)
        report = verify_fft_parity("fft2", (source,), block_size=(2, 3))
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertEqual(report["frequency_shape"], [8, 8])
        self.assertEqual(report["output_shape"], [8, 8, 2])
        pair = run_fft_partition_tiled("fft2", (source,), block_size=(3, 2))
        padded = np.zeros((8, 8), dtype=np.float32)
        padded[:5, :7] = source
        expected = np.fft.fft2(padded)
        expected_pair = np.stack((expected.real, expected.imag), axis=-1).astype(np.float32)
        np.testing.assert_allclose(pair, expected_pair, rtol=2.0e-5, atol=2.0e-5)

    def test_hanning_and_inverse_scaling_crop(self):
        rng = np.random.default_rng(20260810)
        source = rng.normal(size=(6, 5)).astype(np.float32)
        forward = verify_fft_parity(
            "fft2",
            (source,),
            block_size=(3, 4),
            params={"use_hanning": True},
        )
        self.assertTrue(forward["passed"], forward)
        spectrum = run_fft_partition_tiled(
            "fft2", (source,), block_size=(2, 3), params={"use_hanning": True}
        )
        inverse = verify_fft_parity(
            "ifft2",
            (spectrum,),
            block_size=(4, 2),
            params={"target_shape": source.shape},
        )
        self.assertTrue(inverse["passed"], inverse)
        recovered = run_fft_partition_tiled(
            "ifft2", (spectrum,), block_size=(3, 3), params={"target_shape": source.shape}
        )
        rows = np.arange(source.shape[0], dtype=np.float32)
        cols = np.arange(source.shape[1], dtype=np.float32)
        window = (
            np.float32(0.5) * (1.0 - np.cos(np.float32(2.0 * np.pi) * rows / 5.0))
        )[:, None] * (
            np.float32(0.5) * (1.0 - np.cos(np.float32(2.0 * np.pi) * cols / 4.0))
        )[None, :]
        np.testing.assert_allclose(
            recovered,
            source * window,
            rtol=3.0e-5,
            atol=3.0e-5,
        )

    def test_fft_family_alias_and_invalid_shapes_fail_closed(self):
        source = np.arange(3 * 5, dtype=np.float32).reshape(3, 5)
        alias_report = verify_fft_parity("fft", (source,), block_size=2)
        self.assertTrue(alias_report["passed"], alias_report)
        with self.assertRaises(ValueError):
            run_fft_partition_tiled("fft2", (source.reshape(-1),), block_size=2)
        spectrum = run_fft_partition_tiled("fft2", (source,), block_size=2)
        with self.assertRaises(ValueError):
            run_fft_partition_tiled(
                "ifft2", (spectrum,), block_size=2, params={"target_shape": (9, 9)}
            )
        with self.assertRaises(ValueError):
            run_fft_partition_tiled("ifft2", (np.zeros((7, 7, 2), dtype=np.float32),), block_size=2)
        with self.assertRaises(ValueError):
            run_fft_partition_tiled(
                "fft2", (np.ones((1, 4), dtype=np.float32),), block_size=2,
                params={"use_hanning": True},
            )
        with self.assertRaises(ValueError):
            run_fft_partition_tiled("fft2", (source,), block_size=5000)


if __name__ == "__main__":
    unittest.main()
