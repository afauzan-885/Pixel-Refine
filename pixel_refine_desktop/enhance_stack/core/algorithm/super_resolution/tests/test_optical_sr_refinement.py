"""Synthetic optical-SR experiments with known HR ground truth.

The tests deliberately generate LR observations from a known HR image using
the same blur/shift forward model used by ``iterative_optical_refine``.  This
keeps the comparison honest: a larger output image alone is not treated as
evidence of recovered resolution.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import cv2
import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.spatial_splat_sr import (
    iterative_optical_refine,
    iterative_optical_refine_stream,
    robust_subpixel_splat,
    robust_subpixel_splat_stream,
    simulate_lr_from_hr,
)


def _synthetic_scene(kind: str, height: int = 64, width: int = 64) -> np.ndarray:
    y, x = np.mgrid[0:height, 0:width].astype(np.float32)
    xn = x / np.float32(max(width - 1, 1))
    yn = y / np.float32(max(height - 1, 1))

    if kind == "smooth":
        scene = 0.12 + 0.35 * xn + 0.18 * np.sin(y / 4.0)
    elif kind == "edges":
        scene = np.full((height, width), 0.12, dtype=np.float32)
        scene[(x > width * 0.20) & (x < width * 0.48)] = 0.78
        scene[(y > height * 0.52) & (y < height * 0.78)] = 0.48
        circle = (x - width * 0.72) ** 2 + (y - height * 0.30) ** 2 < (height * 0.16) ** 2
        scene[circle] = 0.92
    elif kind == "texture":
        scene = 0.45 + 0.18 * np.sin(x / 2.1) + 0.16 * np.sin(y / 3.3)
        scene += 0.08 * np.sin((x + y) / 1.7)
    elif kind == "natural_texture":
        # Deterministic multi-scale field: low-frequency illumination,
        # mid-frequency structure, and fine texture without unconstrained
        # white-noise frequencies that no 2x LR burst can recover.
        rng = np.random.default_rng(44)
        low = cv2.resize(
            rng.random((10, 10), dtype=np.float32),
            (width, height),
            interpolation=cv2.INTER_CUBIC,
        )
        mid = cv2.resize(
            rng.random((24, 24), dtype=np.float32),
            (width, height),
            interpolation=cv2.INTER_CUBIC,
        )
        scene = 0.15 + 0.45 * low + 0.25 * mid
        scene += 0.10 * np.sin(x / 2.8 + y / 4.2)
    else:
        raise ValueError(f"unknown synthetic scene: {kind}")
    return np.clip(scene, 0.0, 1.0).astype(np.float32)


def _burst(scene: np.ndarray, scale: int = 2) -> tuple[np.ndarray, np.ndarray]:
    lr_h, lr_w = scene.shape[0] // scale, scene.shape[1] // scale
    shifts = ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25), (0.5, 0.5))
    flow = np.zeros((len(shifts), lr_h, lr_w, 2), dtype=np.float32)
    for index, (dx, dy) in enumerate(shifts):
        flow[index, ..., 0] = np.float32(dx)
        flow[index, ..., 1] = np.float32(dy)
    return simulate_lr_from_hr(scene, flow, scale=scale), flow


def _independent_camera_burst(
    scene: np.ndarray,
    scale: int = 2,
    shifts=None,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate observations with OpenCV's camera-like blur/remap path.

    This intentionally does not call ``simulate_lr_from_hr``.  The blur is
    performed by OpenCV and the subpixel observation is sampled through
    ``cv2.remap`` so the inverse test is not circular with the SR oracle.
    """
    height, width = scene.shape
    lr_h, lr_w = height // scale, width // scale
    if shifts is None:
        shifts = (
            (0.0, 0.0),
            (0.25, 0.0),
            (-0.25, 0.0),
            (0.0, 0.25),
            (0.0, -0.25),
            (0.5, 0.5),
        )
    blurred = cv2.GaussianBlur(
        np.ascontiguousarray(scene, dtype=np.float32),
        (0, 0),
        0.85,
        borderType=cv2.BORDER_REFLECT101,
    )
    yy, xx = np.mgrid[0:lr_h, 0:lr_w].astype(np.float32)
    frames = []
    flow = np.zeros((len(shifts), lr_h, lr_w, 2), dtype=np.float32)
    for index, (dx, dy) in enumerate(shifts):
        flow[index, ..., 0] = np.float32(dx)
        flow[index, ..., 1] = np.float32(dy)
        frames.append(
            cv2.remap(
                blurred,
                np.ascontiguousarray((xx + dx) * scale),
                np.ascontiguousarray((yy + dy) * scale),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )
        )
    return np.stack(frames).astype(np.float32), flow


def _spatial_camera_burst(
    scene: np.ndarray, scale: int = 2
) -> tuple[np.ndarray, np.ndarray]:
    """Generate an independent burst with a small spatially varying flow."""
    height, width = scene.shape
    lr_h, lr_w = height // scale, width // scale
    yy, xx = np.mgrid[0:lr_h, 0:lr_w].astype(np.float32)
    center_x = np.float32((lr_w - 1) / 2.0)
    center_y = np.float32((lr_h - 1) / 2.0)
    params = (
        (0.0, 0.0, 0.0, 0.0),
        (0.12, -0.08, 0.0010, -0.0007),
        (-0.10, 0.10, -0.0008, 0.0009),
        (0.20, 0.15, 0.0005, -0.0005),
        (-0.18, 0.04, -0.0004, 0.0006),
    )
    blurred = cv2.GaussianBlur(
        np.ascontiguousarray(scene, dtype=np.float32),
        (0, 0),
        0.85,
        borderType=cv2.BORDER_REFLECT101,
    )
    flow = np.zeros((len(params), lr_h, lr_w, 2), dtype=np.float32)
    frames = []
    for index, (tx, ty, ax, ay) in enumerate(params):
        dx = tx + ax * (yy - center_y) + 0.0003 * (xx - center_x)
        dy = ty + ay * (xx - center_x) - 0.0002 * (yy - center_y)
        flow[index, ..., 0] = dx
        flow[index, ..., 1] = dy
        frames.append(
            cv2.remap(
                blurred,
                np.ascontiguousarray(xx * scale + dx * scale),
                np.ascontiguousarray(yy * scale + dy * scale),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )
        )
    return np.stack(frames).astype(np.float32), flow


def _radial_camera_burst(
    scene: np.ndarray, scale: int = 2
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a burst with a small nonlinear radial lens displacement."""
    height, width = scene.shape
    lr_h, lr_w = height // scale, width // scale
    yy, xx = np.mgrid[0:lr_h, 0:lr_w].astype(np.float32)
    center_x = np.float32((lr_w - 1) / 2.0)
    center_y = np.float32((lr_h - 1) / 2.0)
    xn = (xx - center_x) / np.float32(max(lr_w / 2.0, 1.0))
    yn = (yy - center_y) / np.float32(max(lr_h / 2.0, 1.0))
    radius2 = xn * xn + yn * yn
    params = (
        (0.0, 0.0),
        (0.18, -0.12),
        (-0.16, 0.14),
        (0.10, 0.08),
        (-0.12, -0.06),
    )
    blurred = cv2.GaussianBlur(
        np.ascontiguousarray(scene, dtype=np.float32),
        (0, 0),
        0.85,
        borderType=cv2.BORDER_REFLECT101,
    )
    flow = np.zeros((len(params), lr_h, lr_w, 2), dtype=np.float32)
    frames = []
    for index, (tx, ty) in enumerate(params):
        dx = tx + 0.20 * xn * radius2
        dy = ty - 0.18 * yn * radius2
        flow[index, ..., 0] = dx
        flow[index, ..., 1] = dy
        frames.append(
            cv2.remap(
                blurred,
                np.ascontiguousarray(xx * scale + dx * scale),
                np.ascontiguousarray(yy * scale + dy * scale),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )
        )
    return np.stack(frames).astype(np.float32), flow


class OpticalSRRefinementExperimentTest(unittest.TestCase):
    def test_refinement_beats_interpolation_on_multiple_scene_types(self):
        scale = 2
        metrics = {}
        for kind in ("smooth", "edges", "texture", "natural_texture"):
            scene = _synthetic_scene(kind)
            frames, flow = _burst(scene, scale)
            confidence = np.ones(frames.shape, dtype=np.float32)

            bicubic = cv2.resize(
                frames[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
            )
            bilinear = cv2.resize(
                frames[0], scene.shape[::-1], interpolation=cv2.INTER_LINEAR
            )
            nearest = cv2.resize(
                frames[0], scene.shape[::-1], interpolation=cv2.INTER_NEAREST
            )
            splat, _ = robust_subpixel_splat(
                frames[..., None],
                flow,
                confidence,
                scale=scale,
                fallback=frames[0:1, ..., None],
            )
            refined = iterative_optical_refine(
                frames,
                flow,
                confidence,
                scale=scale,
                iterations=20,
                step=0.5,
            )

            scene_metrics = {
                "nearest": float(np.mean((nearest - scene) ** 2)),
                "bilinear": float(np.mean((bilinear - scene) ** 2)),
                "bicubic": float(np.mean((bicubic - scene) ** 2)),
                "splat": float(np.mean((splat[..., 0] - scene) ** 2)),
                "refined": float(np.mean((refined - scene) ** 2)),
            }
            metrics[kind] = scene_metrics
            self.assertLess(scene_metrics["splat"], scene_metrics["bicubic"])
            self.assertLess(scene_metrics["refined"], scene_metrics["splat"])

        print(f"[OPTICAL-SR] metrics={metrics}")

    def test_independent_camera_forward_model_beats_interpolation(self):
        """Validate against a forward model separate from the SR implementation."""
        metrics = {}
        for kind in ("edges", "natural_texture"):
            scene = _synthetic_scene(kind, height=128, width=128)
            frames, flow = _independent_camera_burst(scene)
            confidence = np.ones_like(frames)
            bicubic = cv2.resize(
                frames[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
            )
            splat, _ = robust_subpixel_splat(
                frames[..., None],
                flow,
                confidence,
                scale=2,
                fallback=frames[0:1, ..., None],
            )
            refined = iterative_optical_refine(
                frames,
                flow,
                confidence,
                scale=2,
                iterations=20,
                step=0.1,
                regularization=0.1,
            )
            scene_metrics = {
                "bicubic": float(np.mean((bicubic - scene) ** 2)),
                "splat": float(np.mean((splat[..., 0] - scene) ** 2)),
                "refined": float(np.mean((refined - scene) ** 2)),
            }
            metrics[kind] = scene_metrics
            self.assertLess(scene_metrics["splat"], scene_metrics["bicubic"])
            self.assertLess(scene_metrics["refined"], scene_metrics["splat"])
        print(f"[OPTICAL-SR] independent_camera_mse={metrics}")

    def test_spatially_varying_motion_preserves_optical_gain(self):
        scene = _synthetic_scene("natural_texture", height=128, width=128)
        frames, flow = _spatial_camera_burst(scene)
        confidence = np.ones_like(frames)
        bicubic = cv2.resize(
            frames[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
        )
        splat, _ = robust_subpixel_splat(
            frames[..., None],
            flow,
            confidence,
            scale=2,
            fallback=frames[0:1, ..., None],
        )
        refined = iterative_optical_refine(
            frames,
            flow,
            confidence,
            scale=2,
            iterations=20,
            step=0.1,
            regularization=0.1,
        )
        metrics = {
            "bicubic": float(np.mean((bicubic - scene) ** 2)),
            "splat": float(np.mean((splat[..., 0] - scene) ** 2)),
            "refined": float(np.mean((refined - scene) ** 2)),
        }
        self.assertLess(metrics["splat"], metrics["bicubic"])
        self.assertLess(metrics["refined"], metrics["splat"])
        print(f"[OPTICAL-SR] spatial_flow_mse={metrics}")

    def test_nonlinear_radial_motion_preserves_optical_gain(self):
        scene = _synthetic_scene("natural_texture", height=128, width=128)
        frames, flow = _radial_camera_burst(scene)
        confidence = np.ones_like(frames)
        bicubic = cv2.resize(
            frames[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
        )
        splat, _ = robust_subpixel_splat(
            frames[..., None],
            flow,
            confidence,
            scale=2,
            fallback=frames[0:1, ..., None],
        )
        refined = iterative_optical_refine(
            frames,
            flow,
            confidence,
            scale=2,
            iterations=20,
            step=0.1,
            regularization=0.1,
        )
        metrics = {
            "bicubic": float(np.mean((bicubic - scene) ** 2)),
            "splat": float(np.mean((splat[..., 0] - scene) ** 2)),
            "refined": float(np.mean((refined - scene) ** 2)),
        }
        self.assertLess(metrics["splat"], metrics["bicubic"])
        self.assertLess(metrics["refined"], metrics["splat"])
        print(f"[OPTICAL-SR] radial_flow_mse={metrics}")

    def test_independent_phase_diversity_beats_integer_shift_burst(self):
        height = width = 128
        y, x = np.mgrid[0:height, 0:width].astype(np.float32)
        scene = 0.5 + 0.38 * np.sin(2.0 * np.pi * 0.25 * x)
        scene += 0.16 * np.sin(2.0 * np.pi * 0.19 * y + 0.3)
        scene = np.clip(scene, 0.0, 1.0).astype(np.float32)
        shifts = {
            "subpixel": (
                (0.0, 0.0),
                (0.25, 0.0),
                (-0.25, 0.0),
                (0.0, 0.25),
                (0.0, -0.25),
                (0.5, 0.5),
            ),
            "integer": (
                (0.0, 0.0),
                (1.0, 0.0),
                (-1.0, 0.0),
                (0.0, 1.0),
                (0.0, -1.0),
            ),
        }
        metrics = {}
        for name, phase in shifts.items():
            frames, flow = _independent_camera_burst(
                scene, shifts=phase
            )
            refined = iterative_optical_refine(
                frames,
                flow,
                np.ones_like(frames),
                scale=2,
                iterations=20,
                step=0.1,
                regularization=0.1,
            )
            metrics[name] = float(np.mean((refined - scene) ** 2))
        self.assertLess(metrics["subpixel"], metrics["integer"])
        print(f"[OPTICAL-SR] independent_phase_mse={metrics}")

    def test_confidence_rejects_synthetic_ghost_region(self):
        scale = 2
        scene = _synthetic_scene("edges")
        frames, flow = _burst(scene, scale)
        ghost = frames[3].copy()
        ghost[8:16, 10:22] = 1.0
        frames[3] = ghost

        no_rejection = np.ones(frames.shape, dtype=np.float32)
        rejection = no_rejection.copy()
        rejection[3, 8:16, 10:22] = 0.0

        no_rejection_result = iterative_optical_refine(
            frames, flow, no_rejection, scale=scale, iterations=15, step=0.5
        )
        rejection_result = iterative_optical_refine(
            frames, flow, rejection, scale=scale, iterations=15, step=0.5
        )
        no_rejection_mse = float(np.mean((no_rejection_result - scene) ** 2))
        rejection_mse = float(np.mean((rejection_result - scene) ** 2))

        self.assertLess(rejection_mse, no_rejection_mse)
        print(
            "[OPTICAL-SR] ghost_mse "
            f"without_weight={no_rejection_mse:.9g} "
            f"with_weight={rejection_mse:.9g}"
        )

    def test_exposure_gain_is_a_multiplicative_support_correction(self):
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
            SplatSRAlgorithm,
        )

        rng = np.random.default_rng(17)
        reference = rng.uniform(0.12, 0.82, (64, 64)).astype(np.float32)
        support = np.ascontiguousarray(reference * np.float32(0.68))
        gain = float(
            SplatSRAlgorithm._estimate_exposure_gain(reference, support)
        )
        corrected = support * np.float32(gain)
        raw_mse = float(np.mean((support - reference) ** 2))
        corrected_mse = float(np.mean((corrected - reference) ** 2))

        self.assertAlmostEqual(gain, 1.0 / 0.68, places=5)
        self.assertLess(corrected_mse, raw_mse * 1.0e-5)
        print(
            "[OPTICAL-SR] exposure_gain "
            f"estimated={gain:.9g} raw_mse={raw_mse:.9g} "
            f"corrected_mse={corrected_mse:.9g}"
        )

    def test_weightnet_confidence_adapter_accepts_grayscale_analysis(self):
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.SplatSR import (
            SplatSRAlgorithm,
        )

        image = np.linspace(0.1, 0.9, 32 * 32, dtype=np.float32).reshape(32, 32)
        flow = np.zeros((32, 32, 2), dtype=np.float32)
        rgb = SplatSRAlgorithm._warp_rgb_for_confidence(image, flow)

        self.assertEqual(rgb.shape, (32, 32, 3))
        self.assertTrue(np.isfinite(rgb).all())
        self.assertLess(float(np.max(np.abs(rgb[..., 0] - rgb[..., 1]))), 1.0e-7)
        self.assertLess(float(np.max(np.abs(rgb[..., 1] - rgb[..., 2]))), 1.0e-7)

    def test_streaming_splat_fills_uncovered_hr_locations(self):
        scene = _synthetic_scene("smooth")
        frames, flow = _burst(scene)
        confidence = np.zeros(frames.shape, dtype=np.float32)
        result, coverage = robust_subpixel_splat_stream(
            frames[..., None],
            lambda index: flow[index],
            lambda index: confidence[index],
            scale=2,
            block_size=32,
        )
        self.assertTrue(np.isfinite(result).all())
        self.assertGreater(float(np.mean(coverage <= 1.0e-6)), 0.0)
        self.assertGreater(float(np.mean(result)), 0.0)
        print(
            "[OPTICAL-SR] streaming uncovered_fraction="
            f"{float(np.mean(coverage <= 1.0e-6)):.6f} fallback_filled=True"
        )

    def test_weightnet_confidence_improves_ghosted_splat(self):
        """Use the real CPU WeightNet pair as a learned confidence provider."""
        encoder = Path(
            "database/Learning_Model/weightNet/CPU/decoupled/encoder_256_cpu.onnx"
        )
        attention = Path(
            "database/Learning_Model/weightNet/CPU/decoupled/attention_256_cpu.onnx"
        )
        if not (encoder.is_file() and attention.is_file()):
            self.skipTest("CPU WeightNet 256 decoupled model pair is unavailable")

        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.weightnet_confidence import (
            WeightNetConfidenceProvider,
        )

        scale = 2
        scene = _synthetic_scene("texture", height=512, width=512)
        frames, flow = _burst(scene, scale)
        frames[2, 80:135, 105:170] = 1.0
        confidence = np.ones(frames.shape, dtype=np.float32)
        yy, xx = np.mgrid[0 : frames.shape[1], 0 : frames.shape[2]].astype(np.float32)
        ref_rgb = np.repeat(frames[0][..., None], 3, axis=2)
        provider = WeightNetConfidenceProvider(
            model_path=Path("database/Learning_Model/weightNet/CPU/weightnet_256_cpu_fp32.onnx"),
            runtime="cpu",
            tile_size=256,
            work_scale=1.0,
        )
        for index in (1, 2):
            aligned = cv2.remap(
                frames[index],
                np.ascontiguousarray(xx - flow[index, ..., 0]),
                np.ascontiguousarray(yy - flow[index, ..., 1]),
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REPLICATE,
            )
            support_rgb = np.repeat(aligned[..., None], 3, axis=2)
            confidence[index] = provider(ref_rgb, support_rgb)

        uniform, _ = robust_subpixel_splat(
            frames[..., None],
            flow,
            np.ones_like(confidence),
            scale=scale,
            fallback=frames[0:1, ..., None],
        )
        weighted, _ = robust_subpixel_splat(
            frames[..., None],
            flow,
            confidence,
            scale=scale,
            fallback=frames[0:1, ..., None],
        )
        uniform_mse = float(np.mean((uniform[..., 0] - scene) ** 2))
        weighted_mse = float(np.mean((weighted[..., 0] - scene) ** 2))
        self.assertLess(weighted_mse, uniform_mse)
        print(
            "[OPTICAL-SR] WeightNet providers="
            f"{provider.providers} uniform_mse={uniform_mse:.9g} "
            f"weightnet_mse={weighted_mse:.9g}"
        )

    def test_noisy_burst_uses_conservative_refinement(self):
        """Noise must not be mistaken for recoverable high-frequency detail."""
        rng = np.random.default_rng(11)
        scene = _synthetic_scene("natural_texture")
        frames, flow = _burst(scene)
        noisy = np.clip(
            frames + rng.normal(0.0, 0.012, frames.shape).astype(np.float32),
            0.0,
            1.0,
        )
        bicubic = cv2.resize(
            noisy[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
        )
        refined = iterative_optical_refine(
            noisy,
            flow,
            np.ones_like(noisy),
            scale=2,
            iterations=20,
            step=0.1,
            regularization=0.1,
        )
        refined_mse = float(np.mean((refined - scene) ** 2))
        bicubic_mse = float(np.mean((bicubic - scene) ** 2))
        self.assertLess(refined_mse, bicubic_mse)
        print(
            "[OPTICAL-SR] noisy natural_texture "
            f"bicubic_mse={bicubic_mse:.9g} refined_mse={refined_mse:.9g}"
        )

    def test_flow_error_is_measurable(self):
        """A sub-pixel SR claim must expose sensitivity to alignment error."""
        scene = _synthetic_scene("natural_texture")
        frames, flow = _burst(scene)
        bad_flow = flow.copy()
        bad_flow[1:, ..., 0] += np.float32(0.08)
        bad_flow[1:, ..., 1] -= np.float32(0.05)
        good = iterative_optical_refine(
            frames,
            flow,
            np.ones_like(frames),
            scale=2,
            iterations=20,
            step=0.5,
        )
        bad = iterative_optical_refine(
            frames,
            bad_flow,
            np.ones_like(frames),
            scale=2,
            iterations=20,
            step=0.5,
        )
        good_mse = float(np.mean((good - scene) ** 2))
        bad_mse = float(np.mean((bad - scene) ** 2))
        self.assertLess(good_mse, bad_mse)
        print(
            "[OPTICAL-SR] flow_error "
            f"good_mse={good_mse:.9g} bad_mse={bad_mse:.9g}"
        )

    def test_stream_refinement_matches_full_frame_oracle(self):
        scene = _synthetic_scene("natural_texture")
        frames, flow = _burst(scene)
        confidence = np.ones_like(frames)
        full = iterative_optical_refine(
            frames,
            flow,
            confidence,
            scale=2,
            iterations=4,
            step=0.1,
            regularization=0.1,
        )
        streamed = iterative_optical_refine_stream(
            frames[..., None],
            lambda index: flow[index],
            lambda index: confidence[index],
            scale=2,
            block_size=32,
            iterations=4,
            step=0.1,
            regularization=0.1,
        )
        max_error = float(np.max(np.abs(full - streamed)))
        self.assertLess(max_error, 2.0e-6)
        print(f"[OPTICAL-SR] stream_refinement_max_abs={max_error:.9g}")

    def test_subpixel_phase_diversity_recovers_high_frequency_detail(self):
        """Only phase-diverse observations should improve near-Nyquist detail."""
        height = width = 64
        y, x = np.mgrid[0:height, 0:width].astype(np.float32)
        scene = 0.5 + 0.4 * np.sin(2.0 * np.pi * 0.25 * x)
        scene += 0.2 * np.sin(2.0 * np.pi * 0.25 * 0.73 * y)
        scene = np.clip(scene, 0.0, 1.0).astype(np.float32)
        patterns = {
            "subpixel": ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25), (0.5, 0.5)),
            "integer": ((0.0, 0.0), (1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0)),
        }
        metrics = {}
        for name, shifts in patterns.items():
            flow = np.zeros((len(shifts), height // 2, width // 2, 2), dtype=np.float32)
            for index, (dx, dy) in enumerate(shifts):
                flow[index, ..., 0] = np.float32(dx)
                flow[index, ..., 1] = np.float32(dy)
            frames = simulate_lr_from_hr(scene, flow, scale=2)
            refined = iterative_optical_refine(
                frames,
                flow,
                np.ones_like(frames),
                scale=2,
                iterations=20,
                step=0.1,
                regularization=0.1,
            )
            metrics[name] = float(np.mean((refined - scene) ** 2))
        self.assertLess(metrics["subpixel"], metrics["integer"])
        print(f"[OPTICAL-SR] high_frequency_phase_mse={metrics}")

    def test_sample_photos_as_known_hr_ground_truth(self):
        """Use repository photographs as controlled, realistic HR scenes."""
        sample_paths = sorted(Path("sample").glob("*.jpg"))
        if not sample_paths:
            self.skipTest("repository sample photographs are unavailable")

        shifts = ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25), (0.5, 0.5))
        rng = np.random.default_rng(2026)
        metrics = {}
        for path in sample_paths:
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            if image is None:
                continue
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (256, 256), interpolation=cv2.INTER_AREA)
            scene = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0
            flow = np.zeros((len(shifts), 128, 128, 2), dtype=np.float32)
            for index, (dx, dy) in enumerate(shifts):
                flow[index, ..., 0] = np.float32(dx)
                flow[index, ..., 1] = np.float32(dy)
            frames = simulate_lr_from_hr(scene, flow)
            frames = np.clip(
                frames + rng.normal(0.0, 0.006, frames.shape).astype(np.float32),
                0.0,
                1.0,
            )
            confidence = np.ones_like(frames)
            bicubic = cv2.resize(
                frames[0], scene.shape[::-1], interpolation=cv2.INTER_CUBIC
            )
            splat, _ = robust_subpixel_splat(
                frames[..., None],
                flow,
                confidence,
                scale=2,
                fallback=frames[0:1, ..., None],
            )
            refined = iterative_optical_refine(
                frames,
                flow,
                confidence,
                scale=2,
                iterations=20,
                step=0.1,
                regularization=0.1,
            )
            photo_metrics = {
                "bicubic": float(np.mean((bicubic - scene) ** 2)),
                "splat": float(np.mean((splat[..., 0] - scene) ** 2)),
                "refined": float(np.mean((refined - scene) ** 2)),
            }
            metrics[path.name] = photo_metrics
            self.assertLess(photo_metrics["splat"], photo_metrics["bicubic"])
            self.assertLess(photo_metrics["refined"], photo_metrics["splat"])
        self.assertTrue(metrics)
        print(f"[OPTICAL-SR] sample_photo_mse={metrics}")

    def test_rgb_splat_reconstructs_all_channels(self):
        """RGB SR must not leave chroma on a single-frame interpolation path."""
        height = width = 64
        y, x = np.mgrid[0:height, 0:width].astype(np.float32)
        scene = np.stack(
            [
                np.clip(0.2 + 0.3 * np.sin(x / 5.0), 0.0, 1.0),
                np.clip(0.4 + 0.2 * np.sin(y / 4.0), 0.0, 1.0),
                np.clip(0.6 + 0.15 * np.sin((x + y) / 3.5), 0.0, 1.0),
            ],
            axis=-1,
        ).astype(np.float32)
        shifts = ((0.0, 0.0), (0.25, 0.0), (-0.25, 0.0), (0.0, 0.25), (0.0, -0.25))
        flow = np.zeros((len(shifts), height // 2, width // 2, 2), dtype=np.float32)
        for index, (dx, dy) in enumerate(shifts):
            flow[index, ..., 0] = np.float32(dx)
            flow[index, ..., 1] = np.float32(dy)
        frames = np.stack(
            [simulate_lr_from_hr(scene[..., channel], flow, scale=2) for channel in range(3)],
            axis=-1,
        )
        splat, _ = robust_subpixel_splat(
            frames,
            flow,
            np.ones((len(shifts), height // 2, width // 2), dtype=np.float32),
            scale=2,
            fallback=frames[0:1],
        )
        per_channel_mse = np.mean((splat - scene) ** 2, axis=(0, 1))
        self.assertTrue(np.all(per_channel_mse < 0.01))
        self.assertGreater(float(np.std(splat[..., 0] - splat[..., 1])), 1.0e-3)
        print(f"[OPTICAL-SR] rgb_channel_mse={per_channel_mse.tolist()}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
