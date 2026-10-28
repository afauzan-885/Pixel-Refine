"""Regresi numerik geometri; GPU opt-in dengan PIXEL_REFINE_TEST_GPU_GEOMETRY=1."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import numpy as np

from .benchmark_geometry_accuracy import make_case
from .quality import (
    TransformEstimationError, _consensus_errors, _msac_cost,
    _refine_consensus, estimate_affine, estimate_homography, project_points,
    ransac_transform,
)


class GeometryAccuracyTests(unittest.TestCase):
    def test_affine_large_coordinate_origin(self):
        rng = np.random.default_rng(42)
        source = rng.normal(0, 12, (96, 2)) + [1.e9, -2.e9]
        truth = np.array([[1.02, -.07, 21], [.04, .98, -13], [0, 0, 1.]])
        target = project_points(source, truth)
        result = estimate_affine(source, target)
        query = source + [11, -3]
        np.testing.assert_allclose(project_points(query, result), project_points(query, truth), rtol=0, atol=2.e-6)

    def test_minimal_homography_keeps_null_vector(self):
        source = np.array([[0, 0], [180, 0], [175, 110], [0, 120.]])
        truth = np.array([[1.04, -.12, 8], [.03, .98, -4], [.0003, -.0002, 1.]])
        target = project_points(source, truth)
        np.testing.assert_allclose(estimate_homography(source, target), truth, rtol=0, atol=1.e-10)

    def test_weighted_fit_and_zero_weight_outlier(self):
        rng = np.random.default_rng(51)
        source = rng.uniform(-100, 100, (40, 2))
        truth = np.array([[1.04, -.12, 8], [.03, .98, -4], [.0003, -.0002, 1.]])
        for fit in (estimate_affine, estimate_homography):
            matrix = truth.copy()
            if fit is estimate_affine:
                matrix[2] = [0, 0, 1]
            target = project_points(source, matrix)
            target[-1] = [1.e4, -2.e4]
            weights = np.ones(40)
            weights[-1] = 0
            result = fit(source, target, weights=weights)
            np.testing.assert_allclose(project_points(source, result), project_points(source, matrix), atol=1.e-8)
            for invalid in (np.zeros(40), np.full(40, np.nan), np.full(40, -1.)):
                with self.assertRaises(ValueError):
                    fit(source, target, weights=invalid)

    def test_rank_deficient_models_are_not_substituted(self):
        source = np.column_stack((np.arange(12), np.arange(12) * .5))
        for fit in (estimate_affine, estimate_homography):
            with self.assertRaises(TransformEstimationError):
                fit(source, source + [2, 3])

    def test_refinement_never_worsens_msac_and_mask_is_current(self):
        for model in ("affine", "homography"):
            source, target, truth, _, _ = make_case("center_cluster", .75, 947, model)
            result, mask, cost = _refine_consensus(source, target, truth, model=model, threshold=3.)
            self.assertLessEqual(cost, _msac_cost(_consensus_errors(source, target, truth), 3.) + 1.e-9)
            np.testing.assert_array_equal(mask, _consensus_errors(source, target, result) <= 9.)

    def test_affine_multiple_seeds_distributions(self):
        for distribution in ("uniform", "center_cluster", "upper_left_cluster", "two_clusters"):
            for seed in (13, 271, 991):
                with self.subTest(distribution=distribution, seed=seed):
                    source, target, truth, clean, query = make_case(distribution, .75, seed, "affine")
                    result, mask, _ = ransac_transform(source, target, model="affine", seed=seed, iterations=256)
                    error = np.linalg.norm(project_points(query, result) - project_points(query, truth), axis=1)
                    self.assertLess(np.percentile(error, 95), 8.)
                    self.assertGreater(clean[mask].mean(), .95)

    def test_cpu_homography_ransac_recovers_projective_model(self):
        source, target, truth, _, query = make_case("uniform", .5, 171, "homography")
        result, mask, _ = ransac_transform(source, target, seed=171, iterations=128)
        error = np.linalg.norm(project_points(query, result) - project_points(query, truth), axis=1)
        self.assertLess(np.percentile(error, 95), 1.5)
        np.testing.assert_array_equal(mask, _consensus_errors(source, target, result) <= 9.)

    def test_device_error_propagates_and_owned_buffers_are_released(self):
        from .. import aot_api as api
        source, target, _, _, _ = make_case("uniform", .25, 51, "homography")
        allocated = []

        class Buffer:
            def __init__(self):
                self.released = False
                allocated.append(self)

            def release(self):
                self.released = True

        from types import SimpleNamespace
        fake_engine = SimpleNamespace(allocate=lambda *a, **k: Buffer())
        with patch.object(api, "upload", side_effect=lambda *a, **k: Buffer()), \
             patch.object(api, "engine", fake_engine), \
             patch.object(api, "_mod", side_effect=RuntimeError("device failure")):
            with self.assertRaisesRegex(RuntimeError, "device failure"):
                api.find_homography(source, target)
        self.assertEqual(len(allocated), 4)
        self.assertTrue(all(b.released for b in allocated))

    def test_aot_invalid_inputs_fail_before_device_dispatch(self):
        from .. import aot_api as api
        source = np.column_stack((np.arange(12), np.arange(12) * .5))
        with patch.object(api, "_mod", side_effect=AssertionError("must not dispatch")):
            self.assertEqual(api.find_homography(source, source + [2, 3]), (None, None))
            self.assertEqual(api.find_homography(np.full((4, 2), np.nan), np.zeros((4, 2))), (None, None))
            with self.assertRaises(ValueError):
                api.find_homography(source, source[:4])


@unittest.skipUnless(os.environ.get("PIXEL_REFINE_TEST_GPU_GEOMETRY") == "1", "GPU runtime opt-in")
class GeometryGPUAccuracyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from taichi_vision import taichi_aot
        cls.api = taichi_aot
        print("Geometry GPU runtime:", taichi_aot.backend_info(), flush=True)

    def test_minimal_four_points(self):
        source = np.array([[0, 0], [180, 0], [175, 110], [0, 120.]], dtype=np.float32)
        truth = np.array([[1.04, -.12, 8], [.03, .98, -4], [.0003, -.0002, 1.]])
        target = project_points(source, truth).astype(np.float32)
        h, mask = self.api.find_homography(source, target, seed=61)
        self.assertIsNotNone(h)
        self.assertEqual(mask.sum(), 4)
        np.testing.assert_allclose(project_points(source, h), target, atol=1.e-4)

    def test_multiseed_homography_distributions(self):
        for distribution in ("uniform", "center_cluster", "upper_left_cluster", "two_clusters"):
            for seed in (13, 271, 991):
                with self.subTest(distribution=distribution, seed=seed):
                    source, target, truth, clean, query = make_case(distribution, .25, seed, "homography")
                    result, mask = self.api.find_homography(source, target, seed=seed)
                    self.assertIsNotNone(result)
                    error = np.linalg.norm(project_points(query, result) - project_points(query, truth), axis=1)
                    self.assertLess(np.percentile(error, 95), 12.)
                    self.assertGreater(clean[mask.ravel().astype(bool)].mean(), .95)
                    np.testing.assert_array_equal(mask.ravel().astype(bool), _consensus_errors(source, target, result) <= 9.)

    def test_same_matrix_warps_with_matched_border(self):
        from .benchmark_geometry_accuracy import warp_parity_diagnostic
        for row in warp_parity_diagnostic()["cases"]:
            with self.subTest(model=row["model"], shape=row["shape"]):
                self.assertLess(row["reflect101_mae"], 1.e-4)
                self.assertLess(row["reflect101_max"], 1.e-3)
                self.assertGreater(row["constant_mae"], .01)

    def test_coordinate_scale_and_origin_do_not_change_geometry(self):
        source, target, truth, _, _ = make_case("uniform", 0., 313, "homography", outliers=0.)
        for scale, offset in ((.001, np.array([0., 0.])), (10., np.array([100000., -200000.]))):
            with self.subTest(scale=scale):
                shifted_source = source * scale + offset
                shifted_target = target * scale + offset
                result, mask = self.api.find_homography(
                    shifted_source, shifted_target, seed=61, ransacReprojThreshold=3. * scale,
                )
                self.assertIsNotNone(result)
                self.assertEqual(mask.sum(), len(source))
                np.testing.assert_allclose(project_points(shifted_source, result), shifted_target, rtol=0, atol=scale * 1.e-5)

    def test_residue_class_inliers(self):
        # The legacy modulo-LCG could not draw four clean points from these
        # residue classes; 50% clean correspondences still support the model.
        source, target, truth, _, _ = make_case("uniform", 0., 611, "homography", outliers=0.)
        clean = np.arange(len(source)) % 4 < 2
        target[~clean] = np.random.default_rng(99).uniform(-1000, 1000, ((~clean).sum(), 2))
        result, mask = self.api.find_homography(source, target, seed=77)
        self.assertIsNotNone(result)
        np.testing.assert_allclose(result, truth, atol=1.e-7)
        self.assertEqual(mask.sum(), clean.sum())

    def test_device_warps_do_not_implicitly_read_back(self):
        from taichi_vision.taichi_algorithm.image_processing.extended_aot import warp_affine_aot
        rng = np.random.default_rng(29)
        matrix_affine = np.asarray([[1., 0., 1.25], [0., 1., -0.75]], dtype=np.float32)
        matrix_projective = np.asarray([[1., .01, 1.], [0., 1., -1.], [.0001, 0., 1.]], dtype=np.float32)
        for image in (rng.random((17, 23), dtype=np.float32), rng.random((17, 23, 3), dtype=np.float32)):
            with self.subTest(shape=image.shape):
                source = self.api.upload(image)
                affine_result = perspective_result = None
                try:
                    with patch.object(type(source), "to_numpy", side_effect=AssertionError("unexpected readback")):
                        affine_result = warp_affine_aot(source, matrix_affine, (23, 17))
                        perspective_result = self.api.warp_perspective(source, matrix_projective, (23, 17))
                    self.assertIsInstance(affine_result, type(source))
                    self.assertIsInstance(perspective_result, type(source))
                    affine_host = affine_result.to_numpy()
                    perspective_host = perspective_result.to_numpy()
                    explicit_affine = warp_affine_aot(source, matrix_affine, (23, 17), return_gpu=False)
                    explicit_perspective = self.api.warp_perspective(
                        source, matrix_projective, (23, 17), return_gpu=False,
                    )
                    np.testing.assert_allclose(explicit_affine, affine_host, rtol=0, atol=1.e-6)
                    np.testing.assert_allclose(explicit_perspective, perspective_host, rtol=0, atol=1.e-6)
                    np.testing.assert_array_equal(source.to_numpy(), image)
                finally:
                    if affine_result is not None:
                        affine_result.release()
                    if perspective_result is not None:
                        perspective_result.release()
                    source.release()

    def test_device_input_ownership_determinism_and_mask(self):
        source, target, _, _, _ = make_case("uniform", .25, 2027, "homography")
        source = source.astype(np.float32)
        target = target.astype(np.float32)
        buffers = [self.api.upload(source), self.api.upload(target)]
        mask_gpu = None
        try:
            first, mask = self.api.find_homography(source, target, seed=41)
            second, mask_gpu = self.api.find_homography(*buffers, seed=41, return_gpu=True)
            np.testing.assert_allclose(first, second, rtol=0, atol=1.e-7)
            np.testing.assert_array_equal(mask.ravel(), mask_gpu.to_numpy())
            np.testing.assert_array_equal(buffers[0].to_numpy(), source)
            np.testing.assert_array_equal(buffers[1].to_numpy(), target)
        finally:
            if mask_gpu is not None:
                mask_gpu.release()
            for b in buffers:
                b.release()


if __name__ == "__main__":
    unittest.main()
