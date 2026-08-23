"""Backend-free known-value checks for panorama alignment contracts."""

from __future__ import annotations

import unittest

import numpy as np

from ..alignment.apap import fit_apap
from ..alignment.quality import estimate_affine, project_points, ransac_transform
from ..alignment.tps import fit_tps_checked
from .stitch import align_pair, sparse_to_dense_warp, stitch_panorama


class PanoramaAlignmentTests(unittest.TestCase):
    def test_affine_ransac_rejects_outlier(self) -> None:
        source = np.array(
            [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0], [25.0, 75.0], [80.0, 20.0]],
            dtype=np.float64,
        )
        transform = np.array([[1.0, 0.05, 7.0], [-0.03, 0.98, -4.0], [0.0, 0.0, 1.0]])
        target = project_points(source, transform)
        target[-1] = [300.0, -200.0]
        estimated, mask, quality = ransac_transform(
            source,
            target,
            model="affine",
            reprojection_threshold=1.0,
            iterations=256,
            seed=11,
        )
        np.testing.assert_allclose(estimated[:2], transform[:2], atol=1.0e-8)
        self.assertEqual(int(mask.sum()), 5)
        self.assertTrue(quality.valid)

    def test_tps_and_apap_preserve_control_points(self) -> None:
        source = np.array([[0.0, 0.0], [100.0, 0.0], [100.0, 100.0], [0.0, 100.0], [50.0, 50.0], [20.0, 70.0]])
        target = source + np.array([5.0, -3.0])
        target[4] += np.array([2.0, 4.0])
        tps, quality = fit_tps_checked(source, target, source_bounds=(0.0, 0.0, 100.0, 100.0), max_displacement=30.0)
        self.assertTrue(quality.valid)
        # The default regularisation intentionally trades a tiny interpolation
        # residual for a better-conditioned solve on large images.
        np.testing.assert_allclose(tps(source), target, atol=5.0e-3)
        apap = fit_apap(source, target, global_homography=estimate_affine(source, target), grid_shape=(2, 2), sigma=80.0)
        # Matrix-space blending is intentionally smooth rather than exact at
        # every control point; the global quality gate remains the source of
        # truth for residual acceptance.
        np.testing.assert_allclose(apap(source), target, atol=3.0)

    def test_explicit_planar_panorama_canvas_and_blend(self) -> None:
        image = np.zeros((16, 24), dtype=np.float32)
        image[4:12, 6:14] = 1.0
        shift = np.eye(3, dtype=np.float64)
        shift[0, 2] = 12.0
        panorama, report = stitch_panorama(
            [image, image],
            transforms=[np.eye(3), shift],
            blend="average",
            return_report=True,
        )
        self.assertEqual(panorama.shape, (16, 36))
        self.assertAlmostEqual(float(panorama.max()), 1.0, places=6)
        self.assertEqual(int(report.metrics["image_count"]), 2)

    def test_graph_cut_blend_composes_small_canvas(self) -> None:
        image = np.zeros((12, 18), dtype=np.float32)
        image[3:9, 4:12] = 1.0
        shift = np.eye(3, dtype=np.float64)
        shift[0, 2] = 6.0
        panorama, report = stitch_panorama(
            [image, np.clip(image * 0.9 + 0.1, 0.0, 1.0)],
            transforms=[np.eye(3), shift],
            blend="graph_cut",
            seam_backend="numpy",
            return_report=True,
        )
        self.assertEqual(panorama.shape, (12, 24))
        self.assertTrue(np.isfinite(panorama).all())
        self.assertGreater(float(report.metrics["coverage_fraction"]), 0.0)

    def test_phase_fallback_rejects_low_response_aot_wrap(self) -> None:
        rng = np.random.default_rng(20260810)
        reference = rng.random((64, 80), dtype=np.float32)
        moving = np.roll(reference, (2, -3), axis=(0, 1))
        result = align_pair(reference, moving, feature="none")
        np.testing.assert_allclose(result.transform[:2, 2], [3.0, -2.0], atol=1.0e-6)
        self.assertTrue(result.quality.valid)
        # A backend with a reliable wrapped-phase response may accept the
        # native candidate directly; weaker phase leaves are rejected in
        # favour of the NumPy overlap-score oracle.  Both outcomes must keep
        # the same transform and quality gate.
        self.assertTrue(
            any("phase candidate rejected" in warning for warning in result.warnings)
            or any("phase response=" in warning for warning in result.warnings)
        )

    def test_explicit_aot_planar_warp_matches_numpy_reference(self) -> None:
        image = np.zeros((16, 24), dtype=np.float32)
        image[4:12, 6:14] = 1.0
        shift = np.eye(3, dtype=np.float64)
        shift[0, 2] = 5.25
        shift[1, 2] = -0.5
        reference = stitch_panorama(
            [image, image],
            transforms=[np.eye(3), shift],
            blend="average",
            backend="numpy",
        )
        try:
            actual, report = stitch_panorama(
                [image, image],
                transforms=[np.eye(3), shift],
                blend="average",
                backend="aot",
                return_report=True,
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(report.backend, "panorama-aot")
        self.assertEqual(actual.shape, reference.shape)
        np.testing.assert_allclose(actual, reference, atol=3.0e-5, rtol=3.0e-5)

    def test_pairwise_tps_refinement_is_used_by_orchestrator(self) -> None:
        image = np.zeros((16, 24), dtype=np.float32)
        image[4:12, 6:14] = 1.0
        reference_points = np.array([[1.0, 1.0], [22.0, 1.0], [22.0, 14.0], [1.0, 14.0], [12.0, 8.0]])
        moving_points = reference_points + np.array([2.0, 1.0])

        def matcher(_reference: np.ndarray, _moving: np.ndarray):
            return reference_points, moving_points

        panorama = stitch_panorama([image, image], matcher=matcher, refine="tps", blend="average")
        self.assertEqual(panorama.ndim, 2)
        self.assertGreaterEqual(panorama.shape[1], image.shape[1])

    def test_explicit_aot_tps_dense_warp_matches_numpy_reference(self) -> None:
        image = np.zeros((16, 24), dtype=np.float32)
        image[4:12, 6:14] = 1.0
        reference_points = np.array(
            [[1.0, 1.0], [22.0, 1.0], [22.0, 14.0], [1.0, 14.0], [12.0, 8.0]]
        )
        moving_points = reference_points + np.array([2.0, 1.0])

        def matcher(_reference: np.ndarray, _moving: np.ndarray):
            return reference_points, moving_points

        reference = stitch_panorama(
            [image, image],
            matcher=matcher,
            refine="tps",
            blend="average",
            backend="numpy",
        )
        try:
            actual, report = stitch_panorama(
                [image, image],
                matcher=matcher,
                refine="tps",
                blend="average",
                backend="aot",
                return_report=True,
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(report.backend, "panorama-aot")
        self.assertEqual(actual.shape, reference.shape)
        np.testing.assert_allclose(actual, reference, atol=3.0e-5, rtol=3.0e-5)

    def test_panorama_working_memory_guard(self) -> None:
        image = np.zeros((24, 32, 3), dtype=np.float32)
        with self.assertRaises(MemoryError):
            stitch_panorama(
                [image, image],
                transforms=[np.eye(3), np.eye(3)],
                max_working_bytes=1,
            )

    def test_sparse_to_dense_aot_remap_and_flow_parity(self) -> None:
        # A TPS/APAP caller evaluates its sparse warp on this grid; the
        # family-local boundary can then reuse either existing AOT remap leaf.
        height, width = 18, 26
        yy, xx = np.indices((height, width), dtype=np.float32)
        image = np.stack(
            [xx / max(width - 1, 1), yy / max(height - 1, 1), (xx + yy) / (height + width - 2)],
            axis=2,
        ).astype(np.float32)
        source_map = np.stack((xx - 1.25, yy + 0.65), axis=2)
        numpy_result, numpy_valid = sparse_to_dense_warp(image, source_map, backend="numpy")
        for use_flow in (False, True):
            try:
                aot_result, aot_valid = sparse_to_dense_warp(
                    image,
                    source_map,
                    backend="aot",
                    use_flow=use_flow,
                )
            except NotImplementedError as exc:
                self.skipTest(str(exc))
            np.testing.assert_array_equal(aot_valid, numpy_valid)
            np.testing.assert_allclose(aot_result, numpy_result, atol=3.0e-5, rtol=3.0e-5)

    def test_aot_warp_and_stitch_reject_non_vec3_3d_layout(self) -> None:
        rgba = np.ones((8, 9, 4), dtype=np.float32)
        source_map = np.zeros((8, 9, 2), dtype=np.float32)
        with self.assertRaises(NotImplementedError):
            sparse_to_dense_warp(rgba, source_map, backend="aot")
        with self.assertRaises(NotImplementedError):
            stitch_panorama(
                [rgba, rgba],
                transforms=[np.eye(3), np.eye(3)],
                backend="aot",
            )


if __name__ == "__main__":
    unittest.main()
