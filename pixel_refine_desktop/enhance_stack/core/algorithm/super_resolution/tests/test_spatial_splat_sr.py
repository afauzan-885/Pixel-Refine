"""Known-value tests for the spatially robust sub-pixel SR oracle."""

from __future__ import annotations

import unittest

import cv2
import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.spatial_splat_sr import (
    robust_subpixel_splat,
    spatial_rejection_map,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
    SplatSRAlgorithm,
)


class SpatialSplatKnownValueTest(unittest.TestCase):
    def test_lucas_kanade_warp_flow_is_inverted_for_splat(self):
        lk_flow = np.asarray([[[0.25, -0.5]]], dtype=np.float32)
        splat_flow = SplatSRAlgorithm._splat_flow_from_lk_flow(lk_flow)
        np.testing.assert_array_equal(
            splat_flow,
            np.asarray([[[-0.25, 0.5]]], dtype=np.float32),
        )

    @staticmethod
    def _scene(height: int, width: int, scale: int) -> np.ndarray:
        y, x = np.mgrid[0 : height * scale, 0 : width * scale].astype(np.float32)
        return np.clip(
            0.15 + 0.42 * x / (width * scale - 1.0) + 0.12 * np.sin(y / 3.0),
            0.0,
            1.0,
        )

    @staticmethod
    def _sample(scene: np.ndarray, height: int, width: int, scale: int, dx: float, dy: float) -> np.ndarray:
        y = np.arange(height, dtype=np.float32)[:, None] * scale + dy * scale
        x = np.arange(width, dtype=np.float32)[None, :] * scale + dx * scale
        y = np.clip(y, 0.0, scene.shape[0] - 1.0)
        x = np.clip(x, 0.0, scene.shape[1] - 1.0)
        y0 = np.floor(y).astype(np.int32)
        x0 = np.floor(x).astype(np.int32)
        y1 = np.minimum(y0 + 1, scene.shape[0] - 1)
        x1 = np.minimum(x0 + 1, scene.shape[1] - 1)
        wy = y - y0
        wx = x - x0
        return (
            (1.0 - wy) * (1.0 - wx) * scene[y0, x0]
            + (1.0 - wy) * wx * scene[y0, x1]
            + wy * (1.0 - wx) * scene[y1, x0]
            + wy * wx * scene[y1, x1]
        ).astype(np.float32)

    def test_subpixel_reconstruction_beats_single_frame_bicubic(self):
        h, w, scale = 24, 24, 2
        ground_truth = self._scene(h, w, scale)
        shifts = ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25))
        frames = np.stack([self._sample(ground_truth, h, w, scale, dx, dy) for dx, dy in shifts])
        flow = np.asarray([(-dx, -dy) for dx, dy in shifts], dtype=np.float32)
        confidence = spatial_rejection_map(frames, flow, noise_sigma=0.03)

        result, coverage = robust_subpixel_splat(
            frames,
            flow,
            confidence,
            scale=scale,
            block_size=16,
            fallback=frames[:1],
        )
        baseline = cv2.resize(frames[0], (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
        splat_mse = float(np.mean((result - ground_truth) ** 2))
        baseline_mse = float(np.mean((baseline - ground_truth) ** 2))

        self.assertEqual(result.shape, ground_truth.shape)
        self.assertTrue(np.all(np.isfinite(result)))
        self.assertGreater(float(np.mean(coverage > 1e-6)), 0.99)
        self.assertLess(splat_mse, baseline_mse)
        print(f"[PASS] subpixel MSE={splat_mse:.9g} bicubic_MSE={baseline_mse:.9g}")

    def test_block_and_full_frame_are_identical(self):
        rng = np.random.default_rng(2026)
        frames = rng.random((3, 11, 13, 2), dtype=np.float32)
        flow = rng.normal(0.0, 0.2, (3, 11, 13, 2)).astype(np.float32)
        confidence = spatial_rejection_map(frames, flow, noise_sigma=0.1)
        full, full_coverage = robust_subpixel_splat(frames, flow, confidence, scale=2)
        blocked, blocked_coverage = robust_subpixel_splat(
            frames, flow, confidence, scale=2, block_size=9
        )
        self.assertEqual(float(np.max(np.abs(full - blocked))), 0.0)
        self.assertEqual(float(np.max(np.abs(full_coverage - blocked_coverage))), 0.0)
        print("[PASS] block/full max_abs=0.0")

    def test_motion_rejection_lowers_changed_region_confidence(self):
        h, w = 20, 20
        base = np.full((h, w), 0.4, dtype=np.float32)
        changed = base.copy()
        changed[7:13, 7:13] = 1.0
        frames = np.stack([base, changed])
        confidence = spatial_rejection_map(frames, np.zeros((2, 2), dtype=np.float32), noise_sigma=0.03)
        self.assertLess(float(confidence[1, 9, 9]), float(confidence[1, 2, 2]))
        print("[PASS] changed-region rejection is active")


if __name__ == "__main__":
    unittest.main(verbosity=2)
