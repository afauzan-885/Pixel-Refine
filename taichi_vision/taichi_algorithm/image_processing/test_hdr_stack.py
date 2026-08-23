"""Family-local HDR stack/deghost smoke and contract tests."""

from __future__ import annotations

import unittest

import numpy as np

from .hdr_stack import deghost_confidence, hdr_stack


class HDRStackContractTests(unittest.TestCase):
    def setUp(self):
        y, x = np.mgrid[:24, :32]
        base = 0.35 + 0.2 * np.sin(x / 4.0) + 0.15 * np.cos(y / 5.0)
        self.reference = np.clip(base, 0.0, 1.0).astype(np.float32)
        self.target = np.clip(self.reference * 0.72, 0.0, 1.0)
        self.target[8:16, 12:22] = 1.0 - self.target[8:16, 12:22]

    def test_confidence_contract(self):
        confidence, residual = deghost_confidence(
            self.reference,
            self.target,
            return_residual=True,
        )
        self.assertEqual(confidence.shape, self.reference.shape)
        self.assertEqual(residual.shape, self.reference.shape)
        self.assertTrue(np.isfinite(confidence).all())
        self.assertTrue(np.isfinite(residual).all())
        self.assertGreaterEqual(float(confidence.min()), 0.05)
        self.assertLessEqual(float(confidence.max()), 1.0)

    def test_explicit_numpy_stack(self):
        result, masks, report = hdr_stack(
            [self.reference, self.target],
            backend="numpy",
            return_masks=True,
            return_report=True,
        )
        self.assertEqual(result.shape, self.reference.shape)
        self.assertEqual(masks.shape, (2,) + self.reference.shape)
        self.assertTrue(np.isfinite(result).all())
        self.assertTrue(report.success)
        self.assertEqual(report.backend, "numpy")
        self.assertTrue(report.warnings)

    def test_taichi_deghost_residual_matches_numpy_and_aot(self):
        numpy_confidence, numpy_residual = deghost_confidence(
            self.reference,
            self.target,
            return_residual=True,
            backend="numpy",
        )
        taichi_confidence, taichi_residual = deghost_confidence(
            self.reference,
            self.target,
            return_residual=True,
            backend="taichi",
        )
        np.testing.assert_allclose(taichi_residual, numpy_residual, rtol=0.0, atol=2.0e-6)
        np.testing.assert_allclose(taichi_confidence, numpy_confidence, rtol=0.0, atol=2.0e-6)
        try:
            aot_confidence, aot_residual = deghost_confidence(
                self.reference,
                self.target,
                return_residual=True,
                backend="aot",
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        np.testing.assert_allclose(aot_residual, numpy_residual, rtol=0.0, atol=2.0e-6)
        np.testing.assert_allclose(aot_confidence, numpy_confidence, rtol=0.0, atol=2.0e-6)

    def test_taichi_deghost_stack_reports_explicit_policy_backend(self):
        result, masks, report = hdr_stack(
            [self.reference, self.target],
            backend="numpy",
            deghost_backend="taichi",
            return_masks=True,
            return_report=True,
        )
        self.assertEqual(result.shape, self.reference.shape)
        self.assertEqual(masks.shape, (2,) + self.reference.shape)
        self.assertEqual(report.metrics["deghost_backend_taichi"], 1.0)
        self.assertTrue(np.isfinite(result).all())

    def test_taichi_deghost_random_border_parity(self):
        rng = np.random.default_rng(20260810)
        reference = rng.uniform(-0.2, 1.2, size=(7, 9, 3)).astype(np.float32)
        target = rng.uniform(-0.2, 1.2, size=(7, 9, 3)).astype(np.float32)
        numpy_confidence, numpy_residual = deghost_confidence(
            reference,
            target,
            smooth_radius=2,
            edge_weight=1.75,
            return_residual=True,
            backend="numpy",
        )
        taichi_confidence, taichi_residual = deghost_confidence(
            reference,
            target,
            smooth_radius=2,
            edge_weight=1.75,
            return_residual=True,
            backend="taichi",
        )
        np.testing.assert_allclose(taichi_residual, numpy_residual, rtol=0.0, atol=2.0e-5)
        np.testing.assert_allclose(taichi_confidence, numpy_confidence, rtol=0.0, atol=2.0e-5)

    def test_standalone_deghost_working_memory_guard(self):
        with self.assertRaises(MemoryError):
            deghost_confidence(
                self.reference,
                self.target,
                max_working_bytes=16,
                backend="numpy",
            )

    def test_invalid_backend_does_not_fallback(self):
        with self.assertRaises(ValueError):
            hdr_stack([self.reference, self.target], backend="auto")

    def test_working_memory_guard_runs_before_fusion(self):
        with self.assertRaises(MemoryError):
            hdr_stack([self.reference, self.target], backend="numpy", max_working_bytes=1)


if __name__ == "__main__":
    unittest.main()
