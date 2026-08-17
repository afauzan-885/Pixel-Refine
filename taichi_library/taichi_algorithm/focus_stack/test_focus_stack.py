"""Family-local focus-stack smoke and contract tests."""

from __future__ import annotations

import unittest

import numpy as np

from . import focus_measure, focus_stack


class FocusStackContractTests(unittest.TestCase):
    def setUp(self):
        y, x = np.mgrid[:24, :32]
        base = (0.35 + 0.2 * np.sin(x / 4.0) + 0.15 * np.cos(y / 5.0)).astype(np.float32)
        self.frames = [
            np.repeat(base[..., None], 3, axis=2),
            np.repeat(np.roll(base, 1, axis=1)[..., None], 3, axis=2),
        ]

    def test_all_focus_measures_host_oracle(self):
        for method in ("variance_laplacian", "modified_laplacian", "tenengrad", "brenner", "local_variance"):
            result = focus_measure(self.frames[0], method=method, backend="numpy")
            self.assertEqual(result.shape, self.frames[0].shape[:2])
            self.assertTrue(np.isfinite(result).all(), method)
            self.assertGreaterEqual(float(result.min()), 0.0, method)

    def test_explicit_numpy_stack_result(self):
        result = focus_stack(self.frames, backend="numpy", return_result=True)
        self.assertEqual(result.image.shape, self.frames[0].shape)
        self.assertEqual(result.focus_index.shape, self.frames[0].shape[:2])
        self.assertEqual(result.confidence.shape, self.frames[0].shape[:2])
        self.assertTrue(np.isfinite(result.image).all())
        self.assertTrue(np.isfinite(result.scores).all())
        self.assertTrue(result.report.success)

    def test_brenner_requires_explicit_host_backend(self):
        with self.assertRaises(NotImplementedError):
            focus_measure(self.frames[0], method="brenner", backend="aot")

    def test_brenner_taichi_matches_numpy_oracle(self):
        numpy_result = focus_measure(self.frames[0], method="brenner", backend="numpy", radius=1)
        taichi_result = focus_measure(self.frames[0], method="brenner", backend="taichi", radius=1)
        np.testing.assert_allclose(taichi_result, numpy_result, atol=2.0e-6, rtol=2.0e-6)

    def test_taichi_focus_stack_matches_numpy_oracle(self):
        numpy_result = focus_stack(self.frames, backend="numpy", method="tenengrad", return_result=True)
        taichi_result = focus_stack(self.frames, backend="taichi", method="tenengrad", return_result=True)
        np.testing.assert_array_equal(taichi_result.focus_index, numpy_result.focus_index)
        np.testing.assert_allclose(taichi_result.image, numpy_result.image, atol=2.0e-5, rtol=2.0e-5)

    def test_working_memory_guard_runs_before_measure(self):
        with self.assertRaises(MemoryError):
            focus_stack(self.frames, backend="numpy", max_working_bytes=1)


if __name__ == "__main__":
    unittest.main()
