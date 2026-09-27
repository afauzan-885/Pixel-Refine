"""Verification for the compute_spatial -> splat SR responsibility split.

Covers the two halves of the contract and their interface:

* the reliability graph (weight map only, no Hann tiling, no overlap-dependent
  scale) and its ghost rejection behaviour;
* the Hann-blended reconstruction (taichi_vision window, exact blend identity,
  tiling invariance, and a measured resolution gain over bicubic);
* the provider that carries one into the other.
"""

from __future__ import annotations

import os
import unittest

# Pin the backend before taichi_vision is imported.  These cases assert graph
# contracts, so they must run on a target whose spatial TCM has been rebuilt;
# an ambient GPU selection would silently test a stale artifact.  Set
# PIXEL_REFINE_AOT_ARCH explicitly to exercise another backend.
os.environ.setdefault("PIXEL_REFINE_AOT_ARCH", "cpu")

import cv2
import numpy as np

from taichi_vision import taichi_aot
from taichi_vision.taichi_algorithm.spatial_fusion import compute_spatial as spatial
from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
    _compute_tile_starts,
)
from taichi_vision.taichi_algorithm.spatial_fusion import (
    accumulate_tile_hann_taichi,
    clear_f32_2d_taichi,
    clear_f32_3d_taichi,
    mean_division_vec3_weight_taichi,
)

from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.reliability_confidence import (
    ReliabilityConfidenceProvider,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.spatial_splat_runtime import (
    SpatialSplatAOT,
    get_runtime,
    run_fused_burst,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.spatial_splat_sr import (
    simulate_lr_from_hr,
)


def _scene(height: int, width: int) -> np.ndarray:
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    return np.clip(
        0.20 + 0.45 * x / (width - 1) + 0.20 * np.sin(y / 5.0) + 0.08 * np.sin(x / 2.3),
        0.0,
        1.0,
    ).astype(np.float32)


def _burst(scene: np.ndarray, scale: int = 2):
    shifts = ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25), (0.5, 0.5))
    lr_h, lr_w = scene.shape[0] // scale, scene.shape[1] // scale
    flow = np.zeros((len(shifts), lr_h, lr_w, 2), dtype=np.float32)
    for index, (dx, dy) in enumerate(shifts):
        flow[index, ..., 0] = np.float32(dx)
        flow[index, ..., 1] = np.float32(dy)
    return simulate_lr_from_hr(scene, flow, scale=scale), flow


class ReliabilityMapTest(unittest.TestCase):
    """The weight map is an evaluator: normalized, gated, overlap-independent."""

    def _reliability(self, motion: float, tile: int = 32):
        eng = taichi_aot.engine
        h = w = 128
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        reference = np.clip(
            0.30 + 0.35 * x / (w - 1) + 0.10 * np.sin(y / 3.0), 0.0, 1.0
        ).astype(np.float32)
        current = reference.copy()
        current[40:72, 40:72] = 1.0  # ghost patch
        rows = np.asarray(_compute_tile_starts(h, tile, overlap=0.25), dtype=np.int32)
        cols = np.asarray(_compute_tile_starts(w, tile, overlap=0.25), dtype=np.int32)
        ref_gpu = taichi_aot.upload(reference)
        cur_gpu = taichi_aot.upload(current)
        out = eng.allocate((h, w), dtype=np.float32, host_accessible=True)
        try:
            spatial.generate_spatial_weights_taichi(
                current_image=cur_gpu,
                reference_image=ref_gpu,
                weight_map_sum=out,
                base_window=0,
                stability_map=None,
                row_starts=rows,
                col_starts=cols,
                tile_h=tile,
                tile_w=tile,
                noise_sigma=0.02,
                motion_sensitivity=motion,
                noise_offset_factor=0.0,
                equalize_brightness=False,
                buffer_provider=None,
                early_exit_threshold=0.0,
                reliability_mode=True,
            )
            eng.sync()
            return np.asarray(out.to_numpy(), dtype=np.float32)
        finally:
            out.destroy()
            ref_gpu.destroy()
            cur_gpu.destroy()

    def test_reliability_is_bounded_and_finite(self):
        result = self._reliability(8.0)
        self.assertTrue(np.isfinite(result).all())
        self.assertGreaterEqual(float(result.min()), 0.0)
        self.assertLessEqual(float(result.max()), 1.0)

    def test_ghost_region_has_lower_reliability_than_clean_region(self):
        result = self._reliability(8.0)
        ghost = float(result[56, 56])
        clean = float(result[10, 10])
        self.assertLess(ghost, clean)
        print(f"[RELIABILITY] ghost={ghost:.6f} clean={clean:.6f}")

    def test_reliability_scale_is_bounded_for_aggressive_and_lenient_settings(self):
        """A hard rejection must show up as zero, never as full confidence.

        The four-pass tiling covers the whole frame, so a zero accumulated
        weight can only mean "every window rejected this sample".  Mapping that
        to full confidence would invert the rejection exactly where ghosting is.
        """
        strict = self._reliability(150.0)
        lenient = self._reliability(2.0)
        for name, result in (("strict", strict), ("lenient", lenient)):
            self.assertTrue(np.isfinite(result).all(), name)
            self.assertGreaterEqual(float(result.min()), 0.0, name)
            self.assertLessEqual(float(result.max()), 1.0, name)
        # A stricter sensitivity rejects at least as much as a lenient one.
        strict_zero = float((strict <= 1e-8).mean())
        lenient_zero = float((lenient <= 1e-8).mean())
        self.assertGreaterEqual(strict_zero, lenient_zero)
        print(
            f"[RELIABILITY] rejected_fraction strict={strict_zero:.4f} "
            f"lenient={lenient_zero:.4f}"
        )


class HannBlendTest(unittest.TestCase):
    """The Hann window and the blend come from taichi_vision and are exact."""

    def test_taichi_vision_hann_window_shape_and_reference(self):
        """The window is produced by taichi_vision and behaves as a Hann window.

        Its tabulation is not bit-identical to ``np.hanning(M + 2)[1:-1]`` for
        small tiles (the two denominators differ), so this asserts the
        properties the blend depends on plus closeness to the nearest NumPy
        reference form, instead of an exact equality that does not hold.
        """
        tile = 48
        window = taichi_aot.generate_hanning_window_2d(
            (tile, tile), exclude_boundary=True
        )
        taichi_aot.engine.sync()
        got = np.asarray(window.to_numpy(), dtype=np.float32)
        window.destroy()

        self.assertEqual(got.shape, (tile, tile))
        self.assertTrue(np.isfinite(got).all())
        self.assertGreaterEqual(float(got.min()), 0.0)
        self.assertLessEqual(float(got.max()), 1.0)
        # Symmetric in both axes.
        self.assertLess(float(np.max(np.abs(got - got[::-1, :]))), 1.0e-6)
        self.assertLess(float(np.max(np.abs(got - got[:, ::-1]))), 1.0e-6)
        centre = float(got[tile // 2, tile // 2])
        corner = float(got[0, 0])
        self.assertGreater(centre, corner)
        # A small border value is what suppresses the tile seam.
        self.assertLess(corner, 1.0e-2)

        references = {
            "np.hanning(M)": np.hanning(tile),
            "np.hanning(M+2)[1:-1]": np.hanning(tile + 2)[1:-1],
        }
        best_name, best = min(
            (
                (name, float(np.max(np.abs(got - np.outer(vec, vec)))))
                for name, vec in references.items()
            ),
            key=lambda item: item[1],
        )
        self.assertLess(best, 1.0e-4)
        print(
            f"[HANN] closest_reference={best_name} max_abs={best:.3e} "
            f"centre={centre:.6f} corner={corner:.3e}"
        )

    def test_hann_blend_and_normalization_reproduce_the_input(self):
        """A weighted average over overlapping windows is exact."""
        eng = taichi_aot.engine
        size, tile, stride = 96, 48, 24
        y, x = np.mgrid[0:size, 0:size].astype(np.float32)
        truth = np.stack(
            [
                np.clip(0.15 + 0.7 * x / (size - 1), 0, 1),
                np.clip(0.15 + 0.7 * y / (size - 1), 0, 1),
                np.clip(0.5 + 0.3 * np.sin((x + y) / 11.0), 0, 1),
            ],
            axis=-1,
        ).astype(np.float32)

        window = taichi_aot.generate_hanning_window_2d(
            (tile, tile), exclude_boundary=True
        )
        acc_num = eng.allocate((size, size, 3), dtype=np.float32)
        acc_den = eng.allocate((size, size), dtype=np.float32)
        clear_f32_3d_taichi(acc_num)
        clear_f32_2d_taichi(acc_den)
        coverage_src = taichi_aot.upload(np.ones((tile, tile), dtype=np.float32))
        reference = taichi_aot.upload(truth)
        try:
            tiles = 0
            for y0 in range(0, size, stride):
                for x0 in range(0, size, stride):
                    if y0 + tile > size or x0 + tile > size:
                        continue
                    for channel in range(3):
                        plane = taichi_aot.upload(
                            np.ascontiguousarray(
                                truth[y0 : y0 + tile, x0 : x0 + tile, channel]
                            )
                        )
                        try:
                            accumulate_tile_hann_taichi(
                                plane,
                                coverage_src,
                                window,
                                acc_num,
                                acc_den,
                                channel=channel,
                                offset=(y0, x0),
                            )
                        finally:
                            plane.destroy()
                    tiles += 1
            self.assertGreater(tiles, 4)
            eng.sync()
            final = mean_division_vec3_weight_taichi(
                sum_img=acc_num, sum_weight=acc_den, ref_img=reference
            )
            eng.sync()
            got = np.asarray(final.to_numpy(), dtype=np.float32)
            final.destroy()
            max_abs = float(np.max(np.abs(got - truth)))
            self.assertLess(max_abs, 1.0e-5)
            print(f"[HANN] blend identity tiles={tiles} max|out-truth|={max_abs:.3e}")
        finally:
            for buffer in (acc_num, acc_den, coverage_src, reference, window):
                buffer.destroy()


class BlockedReconstructionTest(unittest.TestCase):
    """The reconstruction half: seam-free blocking and a measured SR gain."""

    @classmethod
    def setUpClass(cls):
        cls.scale = 2
        cls.lr = 48
        cls.truth = _scene(cls.lr * cls.scale, cls.lr * cls.scale)
        cls.frames, cls.flow = _burst(cls.truth, cls.scale)
        cls.confidence = np.ones(cls.frames.shape, dtype=np.float32)

    def _run(self, overlap: float):
        return SpatialSplatAOT().run_hann_blocks(
            self.frames_rgb,
            self.confidence,
            self.flow,
            scale=self.scale,
            block_size=48,
            overlap=overlap,
        )

    @property
    def frames_rgb(self):
        if not hasattr(self, "_frames_rgb"):
            self._frames_rgb = np.ascontiguousarray(
                np.repeat(self.frames[..., None], 3, axis=-1), dtype=np.float32
            )
        return self._frames_rgb

    def test_reconstruction_beats_bicubic(self):
        result, coverage = self._run(0.5)
        self.assertEqual(result.shape, self.truth.shape + (3,))
        self.assertTrue(np.isfinite(result).all())
        baseline = cv2.resize(
            self.frames[0],
            (self.truth.shape[1], self.truth.shape[0]),
            interpolation=cv2.INTER_CUBIC,
        )
        mse_splat = float(np.mean((result[..., 0] - self.truth) ** 2))
        mse_bicubic = float(np.mean((baseline - self.truth) ** 2))
        self.assertLess(mse_splat, mse_bicubic)
        print(
            f"[BLOCKS] splat_mse={mse_splat:.6e} bicubic_mse={mse_bicubic:.6e} "
            f"gain={mse_bicubic / mse_splat:.2f}x coverage_mean={coverage.mean():.3f}"
        )

    def test_overlap_and_non_overlap_agree(self):
        """Hann normalization must make the result independent of the tiling."""
        overlapped, _ = self._run(0.5)
        disjoint, _ = self._run(0.0)
        max_abs = float(np.max(np.abs(overlapped - disjoint)))
        self.assertLess(max_abs, 1.0e-5)
        print(f"[BLOCKS] max|overlap0.5-overlap0.0|={max_abs:.3e}")

    def test_streaming_matches_whole_burst(self):
        streamed, _ = SpatialSplatAOT().run_hann_blocks_streaming(
            self.frames_rgb,
            lambda k: self.flow[k],
            lambda k: self.confidence[k],
            scale=self.scale,
            block_size=48,
            overlap=0.5,
        )
        whole, _ = self._run(0.5)
        max_abs = float(np.max(np.abs(streamed - whole)))
        self.assertLess(max_abs, 1.0e-5)
        print(f"[BLOCKS] max|streaming-whole|={max_abs:.3e}")


class ReliabilityProviderTest(unittest.TestCase):
    """The provider is the interface between the two halves."""

    def test_provider_returns_bounded_luma_confidence(self):
        lr = 64
        y, x = np.mgrid[0:lr, 0:lr].astype(np.float32)
        reference = np.clip(
            0.20 + 0.55 * x / (lr - 1) + 0.06 * np.sin(y / 7.0), 0.0, 1.0
        ).astype(np.float32)
        support = reference.copy()
        support[28:40, 28:40] = 1.0
        reference_rgb = np.repeat(reference[..., None], 3, axis=2)
        support_rgb = np.repeat(support[..., None], 3, axis=2)

        provider = ReliabilityConfidenceProvider(motion_sensitivity=8.0)
        try:
            result = provider(reference_rgb, support_rgb)
            self.assertEqual(result.shape, (lr, lr))
            self.assertEqual(result.dtype, np.float32)
            self.assertTrue(np.isfinite(result).all())
            self.assertGreaterEqual(float(result.min()), 0.0)
            self.assertLessEqual(float(result.max()), 1.0)
            changed = float(result[34, 34])
            uniform = float(result[4, 4])
            self.assertGreater(uniform, 0.0)
            self.assertLess(changed, uniform)
            print(
                f"[PROVIDER] changed={changed:.6f} uniform={uniform:.6f} "
                f"mean={provider.last_mean_reliability:.4f}"
            )
        finally:
            provider.close()


class FusedReconstructionTest(unittest.TestCase):
    """Fused splat+Hann+accumulate must match the two-stage path and reuse cache."""

    scale = 2
    lr = 48

    @classmethod
    def setUpClass(cls):
        cls.truth = _scene(cls.lr * cls.scale, cls.lr * cls.scale)
        cls.frames, cls.flow = _burst(cls.truth, cls.scale)
        cls.confidence = np.ones(cls.frames.shape, dtype=np.float32)
        cls.frames_rgb = np.ascontiguousarray(
            np.repeat(cls.frames[..., None], 3, axis=-1), dtype=np.float32
        )

    def _run(self, runtime=None):
        return run_fused_burst(
            self.frames_rgb,
            self.confidence,
            self.flow,
            scale=self.scale,
            block_size=48,
            overlap=0.5,
            runtime=runtime,
        )

    def test_fused_matches_the_two_stage_path(self):
        """The algebraic simplification must not change the result."""
        two_stage, _ = SpatialSplatAOT().run_hann_blocks(
            self.frames_rgb,
            self.confidence,
            self.flow,
            scale=self.scale,
            block_size=48,
            overlap=0.5,
        )
        runtime = get_runtime()
        runtime.close()
        fused, coverage = self._run(runtime)
        self.assertEqual(fused.shape, two_stage.shape)
        self.assertTrue(np.isfinite(fused).all())
        max_abs = float(np.max(np.abs(fused - two_stage)))
        self.assertLess(max_abs, 1.0e-5)
        print(f"[FUSED] max|fused-two_stage|={max_abs:.3e}")

    def test_cache_reuse_allocates_nothing_and_does_not_bleed(self):
        """A repeated job must not re-allocate, and must not inherit old contents."""
        runtime = get_runtime()
        runtime.close()
        runtime.counters.update(dispatch=0, allocate=0, destroy=0, upload=0)
        first, _ = self._run(runtime)
        cold = dict(runtime.counters)
        second, _ = self._run(runtime)
        warm = {key: runtime.counters[key] - cold[key] for key in runtime.counters}

        self.assertEqual(warm["allocate"], 0)
        self.assertGreater(cold["upload"], 0)
        # Identical results prove the cleared accumulators carry no old state.
        self.assertEqual(float(np.max(np.abs(second - first))), 0.0)
        print(
            f"[FUSED] cold allocate={cold['allocate']} upload={cold['upload']} "
            f"dispatch={cold['dispatch']} | warm allocate={warm['allocate']} "
            f"upload={warm['upload']} dispatch={warm['dispatch']}"
        )

    def test_close_releases_cached_buffers(self):
        """close() must drop the cache so a backend/shape change cannot reuse it."""
        runtime = get_runtime()
        runtime.close()
        self._run(runtime)
        self.assertTrue(runtime._accumulators)
        runtime.close()
        self.assertFalse(runtime._accumulators)
        self.assertFalse(runtime._hann)
        # A fresh job after close rebuilds the cache and still matches.
        after, _ = self._run(runtime)
        self.assertTrue(np.isfinite(after).all())


if __name__ == "__main__":
    unittest.main(verbosity=2)
