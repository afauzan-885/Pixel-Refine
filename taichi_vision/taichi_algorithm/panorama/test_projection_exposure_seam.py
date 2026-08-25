"""Known-value checks for panorama projection/exposure/seam leaves."""

from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from .exposure import (
    apply_exposure_compensation,
    estimate_exposure_compensation,
)
from .projection import (
    cylindrical_projection,
    equirectangular_projection,
    project_image,
    spherical_projection,
)
from .seam import (
    blend_with_seam,
    dynamic_programming_seam,
    graph_cut_maxflow,
    graph_cut_surrogate,
    seam_energy,
)


class PanoramaPrimitiveTests(unittest.TestCase):
    def setUp(self) -> None:
        yy, xx = np.indices((32, 48), dtype=np.float32)
        self.image = np.stack(
            [xx / 47.0, yy / 31.0, 0.5 * (xx + yy) / 47.0],
            axis=2,
        ).astype(np.float32)

    def test_projections_return_finite_output_and_mask(self) -> None:
        for projection in ("cylindrical", "spherical", "equirectangular"):
            result = project_image(self.image, projection=projection, return_result=True)
            self.assertEqual(result.image.dtype, np.float32)
            self.assertEqual(result.valid.dtype, np.bool_)
            self.assertTrue(np.isfinite(result.image).all())
            self.assertEqual(result.image.shape[:2], result.valid.shape)
            self.assertGreater(int(result.valid.sum()), 0)
        self.assertEqual(cylindrical_projection(self.image).shape, self.image.shape)
        self.assertEqual(spherical_projection(self.image).shape, self.image.shape)
        self.assertEqual(equirectangular_projection(self.image).shape[:2], (32, 64))

    def test_projection_backend_and_budget_fail_closed(self) -> None:
        # AOT composes the host projection map with the target-qualified
        # remap leaf.  It must either execute that exact leaf or fail closed
        # with an actionable error when the selected target has no remap TCM.
        try:
            result = project_image(self.image, backend="aot", return_result=True)
        except NotImplementedError as exc:
            self.assertIn("remap", str(exc).lower())
        else:
            self.assertEqual(result.backend, "aot")
            self.assertTrue(np.isfinite(result.image).all())
        with self.assertRaises((ValueError, MemoryError)):
            project_image(self.image, max_pixels=10)
        with self.assertRaises(ValueError):
            project_image(self.image, projection="unknown")

    def test_aot_projection_rejects_non_vec3_3d_layout_before_dispatch(self) -> None:
        # The remap AOT ABI is scalar HxW or fixed vec3 HxWx3.  Guarding the
        # unsupported singleton/RGBA layouts at the family boundary avoids a
        # low-level field-dimension error from the native graph.
        rgba = np.ones((*self.image.shape[:2], 4), dtype=np.float32)
        singleton = np.ones((*self.image.shape[:2], 1), dtype=np.float32)
        for image in (rgba, singleton):
            with self.assertRaises(NotImplementedError):
                project_image(image, backend="aot")

    def test_aot_projection_composition_sends_safe_map_to_remap_leaf(self) -> None:
        """The AOT contract owns sampling in ``remap``, not a host fallback.

        This isolates the composition boundary from artifact availability: the
        projection stage must provide finite, target-safe coordinates and a
        validity mask, while the qualified remap leaf remains responsible for
        interpolation.  The production parity test below still exercises the
        real target artifact when one is installed.
        """

        captured = {}

        def fake_remap(src, map_x, map_y, *, return_gpu=False):
            captured["src"] = src
            captured["map_x"] = map_x
            captured["map_y"] = map_y
            captured["return_gpu"] = return_gpu
            return np.zeros((*map_x.shape, src.shape[2]), dtype=np.float32)

        with patch("taichi_vision.taichi_algorithm.aot_api.remap", fake_remap):
            result = project_image(
                self.image,
                projection="spherical",
                yaw=0.07,
                pitch=-0.03,
                backend="aot",
                return_result=True,
            )

        self.assertEqual(result.backend, "aot")
        self.assertFalse(captured["return_gpu"])
        self.assertEqual(captured["map_x"].shape, result.valid.shape)
        self.assertEqual(captured["map_y"].shape, result.valid.shape)
        self.assertTrue(np.isfinite(captured["map_x"]).all())
        self.assertTrue(np.isfinite(captured["map_y"]).all())
        # Invalid inverse-map entries are replaced with a safe coordinate
        # before dispatch; remap must never receive NaN/Inf or an out-of-range
        # coordinate that could trigger backend-specific border behaviour.
        self.assertTrue((captured["map_x"] >= 0.0).all())
        self.assertTrue((captured["map_x"] <= self.image.shape[1] - 1).all())
        self.assertTrue((captured["map_y"] >= 0.0).all())
        self.assertTrue((captured["map_y"] <= self.image.shape[0] - 1).all())

    def test_taichi_projection_matches_numpy_reference(self) -> None:
        # This is a CPU-JIT parity gate.  The implementation uses no AOT
        # artifact and therefore must be selected explicitly.
        for projection in ("cylindrical", "spherical", "equirectangular"):
            reference = project_image(
                self.image,
                projection=projection,
                backend="numpy",
                return_result=True,
            )
            taichi_result = project_image(
                self.image,
                projection=projection,
                backend="taichi",
                taichi_arch="cpu",
                return_result=True,
            )
            self.assertEqual(taichi_result.image.shape, reference.image.shape)
            np.testing.assert_array_equal(taichi_result.valid, reference.valid)
            np.testing.assert_allclose(taichi_result.image, reference.image, atol=2.0e-5, rtol=2.0e-5)

    def test_aot_projection_matches_numpy_reference(self) -> None:
        # This is a target-qualified CPU-AOT parity gate for the existing
        # ``remap`` graph; projection coordinate construction remains the
        # family-local host helper by design.
        for projection in ("cylindrical", "spherical", "equirectangular"):
            reference = project_image(
                self.image,
                projection=projection,
                backend="numpy",
                return_result=True,
            )
            try:
                aot_result = project_image(
                    self.image,
                    projection=projection,
                    backend="aot",
                    return_result=True,
                )
            except NotImplementedError as exc:
                self.skipTest(str(exc))
            self.assertEqual(aot_result.backend, "aot")
            np.testing.assert_array_equal(aot_result.valid, reference.valid)
            np.testing.assert_allclose(aot_result.image, reference.image, atol=3.0e-5, rtol=3.0e-5)

    def test_exposure_gain_bias_recovers_known_correction(self) -> None:
        reference = self.image
        # target * gain + offset should map back to reference.
        target = (reference - 0.08) / 1.35
        target = np.clip(target, 0.0, 1.0).astype(np.float32)
        masks = [np.ones(reference.shape[:2], dtype=bool), np.ones(reference.shape[:2], dtype=bool)]
        compensation = estimate_exposure_compensation(
            [reference, target], masks=masks, mode="gain_bias", backend="numpy", max_samples=1000
        )
        corrected = apply_exposure_compensation([reference, target], compensation)
        self.assertAlmostEqual(float(compensation.gains[1, 0]), 1.35, delta=0.04)
        self.assertLess(float(np.mean(np.abs(corrected[1] - reference))), 0.02)
        with self.assertRaises(NotImplementedError):
            estimate_exposure_compensation([reference, target], backend="aot")

    def test_taichi_exposure_estimate_and_apply_match_reference(self) -> None:
        reference = (0.2 + 0.6 * self.image).astype(np.float32)
        target = np.clip((reference - 0.08) / 1.35, 0.0, 1.0).astype(np.float32)
        masks = [np.ones(reference.shape[:2], dtype=bool)] * 2
        numpy_compensation = estimate_exposure_compensation(
            [reference, target], masks=masks, mode="gain_bias", backend="numpy", max_samples=1000
        )
        taichi_compensation = estimate_exposure_compensation(
            [reference, target], masks=masks, mode="gain_bias", backend="taichi"
        )
        np.testing.assert_allclose(taichi_compensation.gains, numpy_compensation.gains, atol=2.0e-5)
        np.testing.assert_allclose(taichi_compensation.offsets, numpy_compensation.offsets, atol=2.0e-5)
        numpy_result = apply_exposure_compensation(
            [reference, target], numpy_compensation, backend="numpy", clip=(0.0, 1.0)
        )
        taichi_result = apply_exposure_compensation(
            [reference, target], numpy_compensation, backend="taichi", clip=(0.0, 1.0)
        )
        np.testing.assert_allclose(taichi_result[1], numpy_result[1], atol=2.0e-6, rtol=2.0e-6)

    def test_seams_are_deterministic_and_composite(self) -> None:
        left = np.zeros((20, 30), dtype=np.float32)
        right = np.ones_like(left)
        overlap = np.ones_like(left, dtype=bool)
        labels_a = dynamic_programming_seam(left, right, overlap_mask=overlap)
        labels_b = dynamic_programming_seam(left, right, overlap_mask=overlap)
        np.testing.assert_array_equal(labels_a, labels_b)
        labels_gc = graph_cut_surrogate(left, right, overlap_mask=overlap, iterations=2)
        self.assertEqual(labels_gc.shape, left.shape)
        blended = blend_with_seam(left, right, labels_gc)
        self.assertTrue(np.isfinite(blended).all())
        self.assertTrue(np.all((blended == 0.0) | (blended == 1.0)))
        with self.assertRaises(NotImplementedError):
            dynamic_programming_seam(left, right, backend="aot")

    def test_taichi_seam_energy_and_dp_match_reference(self) -> None:
        left = self.image
        right = np.roll(self.image, 1, axis=1).astype(np.float32)
        overlap = np.ones(left.shape[:2], dtype=bool)
        numpy_energy, numpy_mask = seam_energy(left, right, overlap_mask=overlap, backend="numpy")
        taichi_energy, taichi_mask = seam_energy(left, right, overlap_mask=overlap, backend="taichi")
        np.testing.assert_array_equal(taichi_mask, numpy_mask)
        np.testing.assert_allclose(taichi_energy, numpy_energy, atol=2.0e-6, rtol=2.0e-6)
        numpy_labels = dynamic_programming_seam(left, right, overlap_mask=overlap, backend="numpy")
        taichi_labels = dynamic_programming_seam(left, right, overlap_mask=overlap, backend="taichi")
        # Equal-energy/tie pixels may choose different predecessor labels after
        # float32 JIT reduction.  Verify the actual objective rather than
        # requiring a brittle bit-for-bit tie break.
        numpy_cost = float(np.sum(numpy_energy[numpy_labels]))
        taichi_cost = float(np.sum(numpy_energy[taichi_labels]))
        self.assertLessEqual(taichi_cost, numpy_cost + 1.0e-3)
        graph_labels = graph_cut_surrogate(left, right, overlap_mask=overlap, backend="taichi", iterations=2)
        self.assertEqual(graph_labels.shape, overlap.shape)

    @staticmethod
    def _graph_cut_objective(
        labels: np.ndarray,
        left: np.ndarray,
        right: np.ndarray,
        overlap: np.ndarray,
        *,
        smoothness: float,
        color_weight: float,
        gradient_weight: float,
    ) -> float:
        """Independent small-grid oracle for ``graph_cut_maxflow`` energy."""

        left_gray = left if left.ndim == 2 else (0.299 * left[..., 0] + 0.587 * left[..., 1] + 0.114 * left[..., 2])
        right_gray = right if right.ndim == 2 else (0.299 * right[..., 0] + 0.587 * right[..., 1] + 0.114 * right[..., 2])
        gx_l = np.diff(left_gray, axis=1, prepend=left_gray[:, :1])
        gy_l = np.diff(left_gray, axis=0, prepend=left_gray[:1, :])
        gx_r = np.diff(right_gray, axis=1, prepend=right_gray[:, :1])
        gy_r = np.diff(right_gray, axis=0, prepend=right_gray[:1, :])
        unary_left = gradient_weight * (np.abs(gx_l) + np.abs(gy_l))
        unary_right = gradient_weight * (np.abs(gx_r) + np.abs(gy_r))
        cross = color_weight * np.abs(left_gray - right_gray)
        value = float(np.sum(np.where(labels, unary_right, unary_left)[overlap]))
        h, w = overlap.shape
        for y in range(h):
            for x in range(w):
                if not overlap[y, x]:
                    continue
                if x + 1 < w and overlap[y, x + 1]:
                    pair = smoothness * (1.0 + 0.5 * (cross[y, x] + cross[y, x + 1]))
                    value += float(pair) * bool(labels[y, x] != labels[y, x + 1])
                elif x + 1 == w or not overlap[y, x + 1]:
                    value += float(smoothness * (1.0 + cross[y, x])) * bool(labels[y, x])
                if y + 1 < h and overlap[y + 1, x]:
                    pair = smoothness * (1.0 + 0.5 * (cross[y, x] + cross[y + 1, x]))
                    value += float(pair) * bool(labels[y, x] != labels[y + 1, x])
                elif y + 1 == h or not overlap[y + 1, x]:
                    value += float(smoothness * (1.0 + cross[y, x])) * bool(labels[y, x])
                if x == 0:
                    value += float(smoothness * (1.0 + cross[y, x])) * bool(labels[y, x])
                if y == 0:
                    value += float(smoothness * (1.0 + cross[y, x])) * bool(labels[y, x])
        return value

    def test_exact_graph_cut_matches_bruteforce_oracle(self) -> None:
        rng = np.random.default_rng(20260810)
        left = rng.random((3, 3), dtype=np.float32)
        right = rng.random((3, 3), dtype=np.float32)
        overlap = np.array(
            [[False, True, True], [True, True, False], [False, True, False]],
            dtype=bool,
        )
        kwargs = dict(smoothness=0.31, color_weight=0.8, gradient_weight=0.6)
        labels = graph_cut_maxflow(left, right, overlap_mask=overlap, **kwargs)
        actual = self._graph_cut_objective(labels, left, right, overlap, **kwargs)
        best = float("inf")
        for bits in range(1 << 9):
            candidate = np.array([(bits >> index) & 1 for index in range(9)], dtype=bool).reshape(3, 3)
            best = min(best, self._graph_cut_objective(candidate, left, right, overlap, **kwargs))
        self.assertLessEqual(actual, best + 2.0e-10)
        np.testing.assert_array_equal(labels, graph_cut_maxflow(left, right, overlap_mask=overlap, **kwargs))

    def test_taichi_graph_cut_hybrid_matches_numpy_objective(self) -> None:
        rng = np.random.default_rng(7)
        left = rng.random((8, 9), dtype=np.float32)
        right = rng.random((8, 9), dtype=np.float32)
        overlap = np.ones((8, 9), dtype=bool)
        kwargs = dict(smoothness=0.21, color_weight=0.7, gradient_weight=0.5, overlap_mask=overlap)
        numpy_labels = graph_cut_maxflow(left, right, backend="numpy", **kwargs)
        taichi_labels = graph_cut_maxflow(left, right, backend="taichi", **kwargs)
        numpy_cost = self._graph_cut_objective(numpy_labels, left, right, overlap, **{k: kwargs[k] for k in ("smoothness", "color_weight", "gradient_weight")})
        taichi_cost = self._graph_cut_objective(taichi_labels, left, right, overlap, **{k: kwargs[k] for k in ("smoothness", "color_weight", "gradient_weight")})
        self.assertLessEqual(taichi_cost, numpy_cost + 2.0e-5)
        self.assertTrue(np.isfinite(taichi_cost))

    def test_graph_cut_budget_and_aot_contract(self) -> None:
        left = np.zeros((8, 8), dtype=np.float32)
        right = np.ones_like(left)
        with self.assertRaises(ValueError):
            graph_cut_maxflow(left, right, max_pixels=10)
        with self.assertRaises(MemoryError):
            graph_cut_maxflow(left, right, max_working_bytes=1024)
        try:
            aot_labels = graph_cut_maxflow(left, right, backend="aot")
        except (FileNotFoundError, NotImplementedError) as exc:
            # A target without the panorama TCM must fail closed rather than
            # silently routing to the CPU-JIT or NumPy map builder.
            self.assertIn("panorama", str(exc).lower())
        else:
            np.testing.assert_array_equal(
                aot_labels,
                graph_cut_maxflow(left, right, backend="numpy"),
            )


if __name__ == "__main__":
    unittest.main()
