"""Unit tests for alignment family: Phase Correlation, ZNCC, APAP, AANAP, Multi-Row APAP, and TPS."""

import unittest
import numpy as np

from taichi_vision.taichi_algorithm.alignment.phase_correlation import phase_correlation
from taichi_vision.taichi_algorithm.alignment.ncc import zncc
from taichi_vision.taichi_algorithm.alignment.apap import (
    fit_apap,
    fit_apap_reference,
    filter_apap_correspondences,
    APAPWarp,
    fit_aanap,
    AANAPWarp,
    warp_image,
    align_burst_stack,
    align_multi_image_panorama,
)
from taichi_vision.taichi_algorithm.alignment.tps import fit_tps_checked, TPSWarp
from taichi_vision.taichi_algorithm.alignment.quality import (
    TransformEstimationError,
    estimate_homography,
    project_points,
)


class TestAlignment(unittest.TestCase):
    def test_warp_apap_reuses_caller_global_homography(self):
        from unittest.mock import patch

        from taichi_vision.taichi_algorithm.alignment import apap as apap_module
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        points = np.array(
            [[0.0, 0.0], [20.0, 0.0], [0.0, 20.0], [20.0, 20.0]],
            dtype=np.float64,
        )
        global_h = np.array(
            [[1.0, 0.0, 2.0], [0.0, 1.0, -3.0], [0.0, 0.0, 1.0]],
            dtype=np.float64,
        )
        warp_model = object()
        expected = object()

        with (
            patch.object(apap_module, "fit_apap", return_value=warp_model) as fit,
            patch.object(
                mesh_warp, "warp_image_sparse_mesh", return_value=expected
            ) as image_warp,
        ):
            result = mesh_warp.warp_apap(
                np.zeros((24, 24, 3), dtype=np.float32),
                points,
                points + np.array([2.0, -3.0]),
                global_homography=global_h,
            )

        self.assertIs(result, expected)
        self.assertIs(fit.call_args.kwargs["global_homography"], global_h)
        self.assertIs(image_warp.call_args.kwargs["warp_func"], warp_model)

    def test_phase_correlation_shift(self):
        h, w = 64, 64
        yy, xx = np.indices((h, w), dtype=np.float32)
        ref = (np.sin(xx * 0.2) * np.cos(yy * 0.2)).astype(np.float32)
        shift_x, shift_y = 3.0, -2.0
        comp = np.roll(np.roll(ref, int(shift_y), axis=0), int(shift_x), axis=1)

        dx, dy, resp = phase_correlation(ref, comp)
        self.assertAlmostEqual(dx, shift_x, delta=0.5)
        self.assertAlmostEqual(dy, shift_y, delta=0.5)
        self.assertGreater(resp, 0.5)

    def test_zncc(self):
        a = np.random.uniform(0.0, 1.0, (32, 32)).astype(np.float32)
        b = a * 1.5 + 0.2 # linear transform
        score = zncc(a, b)
        self.assertAlmostEqual(score, 1.0, delta=1e-3)

    def test_apap(self):
        src_pts = np.array([
            [x, y] for y in np.linspace(10, 90, 4) for x in np.linspace(10, 90, 4)
        ], dtype=np.float64)
        # Translation + mild scale
        dst_pts = src_pts * 1.05 + np.array([5.0, -3.0])

        warp = fit_apap(src_pts, dst_pts, grid_shape=(4, 4))
        self.assertIsInstance(warp, APAPWarp)

        self.assertFalse(np.any(warp.support_counts))
        with self.assertRaisesRegex(
            TransformEstimationError, "no fitted local correspondence support"
        ):
            warp.map_points(src_pts)

    def test_native_apap_relative_residual_across_sparse_and_uneven_layouts(self):
        rng = np.random.default_rng(20261017)
        regular_x, regular_y = np.meshgrid(
            np.linspace(8.0, 248.0, 11), np.linspace(8.0, 248.0, 11)
        )
        regular = np.column_stack((regular_x.ravel(), regular_y.ravel()))
        clustered = np.vstack(
            [
                rng.normal((48.0, 48.0), (12.0, 12.0), (24, 2)),
                rng.normal((208.0, 208.0), (12.0, 12.0), (24, 2)),
                [[8.0, 8.0], [248.0, 8.0], [8.0, 248.0], [248.0, 248.0]],
            ]
        )
        edge = np.vstack(
            [
                np.column_stack(
                    (np.linspace(4.0, 252.0, 30), rng.uniform(4.0, 14.0, 30))
                ),
                np.column_stack(
                    (rng.uniform(4.0, 14.0, 30), np.linspace(4.0, 252.0, 30))
                ),
                [[4.0, 4.0], [252.0, 4.0], [4.0, 252.0], [252.0, 252.0]],
            ]
        )
        fixtures = {
            "high_uniform": rng.uniform(4.0, 252.0, (122, 2)),
            "medium_regular": regular,
            "low_clustered": clustered,
            "extreme_edge_corner": edge,
        }
        query_y, query_x = np.mgrid[4.0:252.0:33j, 4.0:252.0:33j]
        query = np.column_stack((query_x.ravel(), query_y.ravel()))

        for name, source in fixtures.items():
            with self.subTest(layout=name):
                source = np.ascontiguousarray(source, dtype=np.float64)
                radius_sq = np.sum((source - [128.0, 128.0]) ** 2, axis=1)
                amplitude = 1.5 * np.exp(-radius_sq / (2.0 * 42.0**2))
                target = source + np.column_stack((amplitude, -0.6 * amplitude))
                warp = fit_apap(source, target, grid_shape=(4, 4))

                sigma_x, sigma_y = (
                    warp.sigma
                    if isinstance(warp.sigma, tuple)
                    else (warp.sigma, warp.sigma)
                )
                delta = query[:, None, :] - warp.centers[None, :, :]
                query_weights = np.exp(
                    -(
                        delta[:, :, 0] ** 2 / (2.0 * sigma_x**2)
                        + delta[:, :, 1] ** 2 / (2.0 * sigma_y**2)
                    )
                )
                query_weights *= warp.support_counts[None, :] > 0
                supported = (
                    (np.max(query_weights, axis=1) >= 0.15)
                    & (np.sum(query_weights, axis=1) > 1.0e-12)
                )
                supported_query = query[supported]
                self.assertGreater(len(supported_query), 0)

                expected_amplitude = 1.5 * np.exp(
                    -np.sum((supported_query - [128.0, 128.0]) ** 2, axis=1)
                    / (2.0 * 42.0**2)
                )
                expected = supported_query + np.column_stack(
                    (expected_amplitude, -0.6 * expected_amplitude)
                )
                apap_mapping = warp.map_points(supported_query)
                homography_mapping = project_points(
                    supported_query, estimate_homography(source, target)
                )
                apap_error = np.linalg.norm(apap_mapping - expected, axis=1)
                homography_error = np.linalg.norm(
                    homography_mapping - expected, axis=1
                )

                self.assertEqual(len(warp.source_points), len(source))
                self.assertTrue(np.isfinite(apap_mapping).all())
                self.assertLess(
                    float(np.percentile(apap_error, 50)),
                    float(np.percentile(homography_error, 50)),
                )
                self.assertLess(
                    float(np.percentile(apap_error, 95)),
                    float(np.percentile(homography_error, 95)),
                )
                self.assertGreater(float(np.mean(apap_error < homography_error)), 0.5)

    def test_native_apap_rejects_non_pure_tps_residual_request(self):
        points = np.array(
            [[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [10.0, 10.0]],
            dtype=np.float64,
        )
        with self.assertRaisesRegex(ValueError, "pure Moving DLT"):
            fit_apap(
                points,
                points + np.array([1.0, -1.0]),
                enable_residual_spline=True,
            )

    def test_native_apap_does_not_fall_back_when_target_module_is_missing(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module
        from taichi_vision.taichi_algorithm import aot_api

        points = np.array(
            [[0.0, 0.0], [10.0, 0.0], [0.0, 10.0], [10.0, 10.0]],
            dtype=np.float64,
        )
        with patch.object(
            aot_api,
            "load_tcm",
            side_effect=RuntimeError("target module unavailable"),
        ), patch.object(apap_module, "_fit_apap_numpy_reference") as reference_fit:
            with self.assertRaisesRegex(RuntimeError, "no CPU/NumPy fallback"):
                fit_apap(points, points + np.array([1.0, -1.0]))
            reference_fit.assert_not_called()

    def test_apap_reference_keeps_all_correspondences_across_adversarial_layouts(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module

        rng = np.random.default_rng(20261016)
        regular_x, regular_y = np.meshgrid(
            np.linspace(8.0, 248.0, 11), np.linspace(8.0, 248.0, 11)
        )
        regular = np.column_stack((regular_x.ravel(), regular_y.ravel()))
        clustered = np.vstack(
            [
                rng.normal((48.0, 48.0), (12.0, 12.0), (24, 2)),
                rng.normal((208.0, 208.0), (12.0, 12.0), (24, 2)),
                np.array([[8.0, 8.0], [248.0, 8.0], [8.0, 248.0], [248.0, 248.0]]),
            ]
        )
        # Points concentrated near long edges and corners create an anisotropic,
        # low-coverage layout while retaining two-dimensional support.
        edge_points = np.vstack(
            [
                np.column_stack((np.linspace(4.0, 252.0, 30), rng.uniform(4.0, 14.0, 30))),
                np.column_stack((rng.uniform(4.0, 14.0, 30), np.linspace(4.0, 252.0, 30))),
                np.array([[4.0, 4.0], [252.0, 4.0], [4.0, 252.0], [252.0, 252.0]]),
            ]
        )
        layouts = {
            "high_uniform": rng.uniform(4.0, 252.0, (122, 2)),
            "medium_regular": regular,
            "low_clustered": clustered,
            "extreme_edge_corner": edge_points,
        }
        original_solver = apap_module._weighted_homography

        for name, source in layouts.items():
            with self.subTest(layout=name):
                source = np.ascontiguousarray(source, dtype=np.float64)
                radial = np.sum((source - np.array([128.0, 128.0])) ** 2, axis=1)
                amplitude = 1.5 * np.exp(-radial / (2.0 * 42.0**2))
                target = source + np.column_stack((amplitude, -0.6 * amplitude))
                seen_counts = []

                def record_and_solve(src, dst, weights):
                    seen_counts.append(len(src))
                    return original_solver(src, dst, weights)

                with patch.object(apap_module, "_weighted_homography", record_and_solve):
                    limited = fit_apap_reference(
                        source,
                        target,
                        grid_shape=(2, 2),
                        max_controls_per_node=3,
                        enable_residual_spline=False,
                    )
                unlimited = fit_apap_reference(
                    source,
                    target,
                    grid_shape=(2, 2),
                    max_controls_per_node=len(source),
                    enable_residual_spline=False,
                )

                self.assertTrue(seen_counts)
                self.assertTrue(all(count == len(source) for count in seen_counts))
                np.testing.assert_array_equal(limited.source_points, source)
                np.testing.assert_array_equal(limited.target_points, target)
                np.testing.assert_allclose(
                    limited.map_points(source), unlimited.map_points(source), atol=1e-10
                )
                self.assertTrue(np.isfinite(limited.map_points(source)).all())
                global_only = project_points(
                    source, estimate_homography(source, target)
                )
                local_effect = np.linalg.norm(
                    limited.map_points(source) - global_only, axis=1
                )
                self.assertGreater(float(np.max(local_effect)), 1.0e-3)

    def test_apap_rejects_nonfinite_rows_instead_of_silently_dropping_them(self):
        from taichi_vision.taichi_algorithm.alignment.apap import _validate_apap_correspondences

        source = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [np.nan, 2.0]])
        target = source.copy()
        with self.assertRaisesRegex(ValueError, "no correspondence rows were dropped"):
            _validate_apap_correspondences(source, target, min_points=4)

    def test_apap_fixed_grid_residual_uses_all_122_rows_across_layouts(self):
        from taichi_vision.taichi_algorithm.alignment.apap import fit_apap_tps_grid_reference

        rng = np.random.default_rng(20261016)
        uniform = rng.uniform(4.0, 252.0, (122, 2))
        medium_x, medium_y = np.meshgrid(
            np.linspace(8.0, 248.0, 10), np.linspace(8.0, 248.0, 12)
        )
        medium = np.vstack(
            [
                np.column_stack((medium_x.ravel(), medium_y.ravel())),
                [[42.0, 219.0], [218.0, 39.0]],
            ]
        )
        clustered = np.vstack(
            [
                rng.normal((48.0, 48.0), (15.0, 15.0), (56, 2)),
                rng.normal((208.0, 208.0), (15.0, 15.0), (56, 2)),
                [
                    [8.0, 8.0], [248.0, 8.0], [8.0, 248.0], [248.0, 248.0],
                    [128.0, 8.0], [8.0, 128.0], [248.0, 128.0], [128.0, 248.0],
                    [128.0, 96.0], [96.0, 128.0],
                ],
            ]
        )
        edge = np.vstack(
            [
                np.column_stack((np.linspace(4.0, 252.0, 59), rng.uniform(4.0, 12.0, 59))),
                np.column_stack((rng.uniform(4.0, 12.0, 59), np.linspace(4.0, 252.0, 59))),
                [[4.0, 4.0], [252.0, 4.0], [4.0, 252.0], [252.0, 252.0]],
            ]
        )
        qx, qy = np.meshgrid(np.linspace(4.0, 252.0, 33), np.linspace(4.0, 252.0, 33))
        query = np.column_stack((qx.ravel(), qy.ravel()))

        def localized_motion(points):
            radius_sq = np.sum((points - [128.0, 128.0]) ** 2, axis=1)
            amplitude = 1.5 * np.exp(-radius_sq / (2.0 * 42.0**2))
            return points + np.column_stack((amplitude, -0.6 * amplitude))

        fixtures = {
            "high_uniform": (uniform, localized_motion),
            "medium_regular": (medium, localized_motion),
            "low_clustered": (clustered, localized_motion),
            # This edge-only scene has a known affine motion; it has no observed
            # foreground controls in the interior from which a local bump could be inferred.
            "extreme_edges": (edge, lambda points: points * 1.002 + [0.5, -0.25]),
        }

        for name, (source, transform) in fixtures.items():
            with self.subTest(layout=name):
                target = transform(source)
                fitted = fit_apap_tps_grid_reference(
                    source, target, grid_size=8, regularization=1.0e-4
                )
                expected = transform(query)
                error = np.linalg.norm(fitted.map_points(query) - expected, axis=1)
                self.assertEqual(fitted.input_count, len(source))
                self.assertEqual(len(fitted.control_points), 64)
                self.assertLessEqual(float(error.max()), 1.0)
                self.assertLessEqual(float(error.mean()), 0.15)
                self.assertTrue(np.isfinite(fitted.map_points(query)).all())

                if name == "high_uniform":
                    changed_target = target.copy()
                    changed_target[-1, 0] += 0.25
                    perturbed = fit_apap_tps_grid_reference(
                        source, changed_target, grid_size=8, regularization=1.0e-4
                    )
                    effect = np.linalg.norm(
                        perturbed.map_points(query) - fitted.map_points(query), axis=1
                    )
                    self.assertGreater(float(effect.max()), 1.0e-8)
                    local = np.linalg.norm(fitted.map_points(query) - query, axis=1)
                    self.assertGreater(float(local.max()), 1.0)

    def test_aanap(self):
        src_pts = np.array([
            [x, y] for y in np.linspace(20, 180, 5) for x in np.linspace(20, 180, 5)
        ], dtype=np.float64)
        dst_pts = src_pts * 1.02 + np.array([4.0, -2.0])

        aanap_warp = fit_aanap(src_pts, dst_pts, grid_shape=(5, 5))
        self.assertIsInstance(aanap_warp, AANAPWarp)

        mapped = aanap_warp.map_points(src_pts)
        err = np.mean(np.abs(mapped - dst_pts))
        self.assertLess(err, 1.0)

    def test_apap_parallax_precision(self):
        # Multi-plane parallax scene: Plane 1 (grid) shifts by (+15, +8), Plane 2 (circles) shifts by (+32, +18)
        grid_pts = np.array([[x, y] for y in np.linspace(50, 550, 5) for x in np.linspace(50, 550, 5)], dtype=np.float64)
        c_pts = np.array([[200.0, 300.0], [280.0, 300.0], [240.0, 260.0], [240.0, 340.0]], dtype=np.float64)
        all_ref = np.vstack([grid_pts, c_pts])

        mov_grid = grid_pts + np.array([15.0, 8.0])
        mov_c = c_pts + np.array([32.0, 18.0])
        all_mov = np.vstack([mov_grid, mov_c])

        # APAP with parallax support
        warp = fit_apap(all_mov, all_ref, grid_shape=(4, 4))
        self.assertIsInstance(warp, APAPWarp)

        mapped = warp.map_points(all_mov)
        apap_error = np.linalg.norm(mapped - all_ref, axis=1)
        global_h = estimate_homography(all_mov, all_ref)
        homography_error = np.linalg.norm(
            project_points(all_mov, global_h) - all_ref, axis=1
        )
        self.assertLess(float(np.median(apap_error)), float(np.median(homography_error)))
        self.assertLess(float(np.percentile(apap_error, 95)), float(np.percentile(homography_error, 95)))
        self.assertGreater(float(np.mean(apap_error < homography_error)), 0.5)

        # AANAP with parallax support
        aanap_warp = fit_aanap(all_mov, all_ref, grid_shape=(4, 4))
        self.assertIsInstance(aanap_warp, AANAPWarp)
        mapped_aanap = aanap_warp.map_points(all_mov)
        err_aanap = np.mean(np.abs(mapped_aanap - all_ref))
        self.assertLess(err_aanap, 0.05)

    def test_apap_retains_local_motion_outside_global_ransac_inliers(self):
        rng = np.random.default_rng(3)
        reference_points = rng.uniform([20.0, 20.0], [492.0, 492.0], (300, 2))
        local_displacement = np.column_stack(
            (
                22.0 * np.sin(reference_points[:, 0] / 100.0),
                10.0 * np.sin(reference_points[:, 1] / 90.0),
            )
        )
        support_points = reference_points + local_displacement

        support_to_reference = estimate_homography(
            support_points, reference_points
        )
        ref_matches, support_matches = filter_apap_correspondences(
            reference_points,
            support_points,
            support_to_reference,
            residual_threshold=60.0,
        )
        self.assertGreater(len(ref_matches), 250)

        apap = fit_apap(
            ref_matches,
            support_matches,
            global_homography=np.linalg.inv(support_to_reference),
            grid_shape=(4, 4),
        )
        query_y, query_x = np.mgrid[40.0:473.0:17j, 40.0:473.0:17j]
        query = np.column_stack((query_x.ravel(), query_y.ravel()))
        expected_support = query + np.column_stack(
            (
                22.0 * np.sin(query[:, 0] / 100.0),
                10.0 * np.sin(query[:, 1] / 90.0),
            )
        )
        global_support = project_points(
            query, np.linalg.inv(support_to_reference)
        )

        apap_error = np.linalg.norm(apap.map_points(query) - expected_support, axis=1)
        homography_error = np.linalg.norm(global_support - expected_support, axis=1)
        self.assertLess(float(np.median(apap_error)), float(np.median(homography_error)))
        self.assertLess(float(np.percentile(apap_error, 95)), float(np.percentile(homography_error, 95)))
        self.assertGreater(float(np.mean(apap_error < homography_error)), 0.5)

    def test_pure_apap_reference_improves_local_motion_relative_to_homography(self):
        rng = np.random.default_rng(3)
        reference_points = rng.uniform([20.0, 20.0], [492.0, 492.0], (300, 2))
        local_displacement = np.column_stack(
            (
                22.0 * np.sin(reference_points[:, 0] / 100.0),
                10.0 * np.sin(reference_points[:, 1] / 90.0),
            )
        )
        support_points = reference_points + local_displacement
        support_to_reference = estimate_homography(
            support_points, reference_points
        )

        apap = fit_apap_reference(
            reference_points,
            support_points,
            global_homography=np.linalg.inv(support_to_reference),
            grid_shape=(4, 4),
        )
        query = np.array([[100.0, 100.0], [400.0, 400.0], [250.0, 250.0]])
        expected = query + np.column_stack(
            (
                22.0 * np.sin(query[:, 0] / 100.0),
                10.0 * np.sin(query[:, 1] / 90.0),
            )
        )
        apap_residual = np.linalg.norm(apap.map_points(query) - expected, axis=1)
        homography_residual = np.linalg.norm(
            project_points(query, np.linalg.inv(support_to_reference)) - expected,
            axis=1,
        )

        self.assertIsNone(apap.residual_field)
        self.assertTrue(np.isfinite(apap_residual).all())
        self.assertGreater(int(np.count_nonzero(apap.support_counts)), 0)
        self.assertLess(float(np.median(apap_residual)), float(np.median(homography_residual)))
        self.assertLess(float(np.percentile(apap_residual, 95)), float(np.percentile(homography_residual, 95)))
        self.assertGreater(float(np.mean(apap_residual < homography_residual)), 0.5)

    def test_apap_reference_rejects_nodes_when_local_fit_has_no_gain(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module

        yy, xx = np.mgrid[20.0:492.0:11j, 20.0:492.0:11j]
        source = np.column_stack((xx.ravel(), yy.ravel()))
        target = source + np.array([8.0, -5.0])
        with patch.object(apap_module, "_locally_improves_global", return_value=False):
            apap = fit_apap_reference(source, target, grid_shape=(4, 4))

        self.assertFalse(np.any(apap.support_counts))
        query = np.column_stack((xx.ravel(), yy.ravel()))
        with self.assertRaisesRegex(
            TransformEstimationError, "no fitted local correspondence support"
        ):
            apap.map_points(query)

    def test_apap_reference_rejects_queries_without_local_support(self):
        clustered = np.array(
            [
                [100.0, 100.0], [110.0, 100.0], [100.0, 110.0], [110.0, 110.0],
                [300.0, 300.0], [310.0, 300.0], [300.0, 310.0], [310.0, 310.0],
            ], dtype=np.float64,
        )
        target = clustered.copy()
        target[:4] += np.array([7.0, -3.0])
        target[4:] += np.array([-6.0, 5.0])
        global_h = estimate_homography(clustered, target)
        apap = fit_apap_reference(
            clustered,
            target,
            global_homography=global_h,
            grid_shape=(3, 3),
            sigma=(20.0, 20.0),
            min_support=4,
        )
        outside_support = np.array([[205.0, 205.0], [205.0, 205.0]])

        self.assertTrue(np.any(apap.support_counts == 0))
        with self.assertRaisesRegex(
            TransformEstimationError, "no fitted local correspondence support"
        ):
            apap.map_points(outside_support)
        np.testing.assert_array_equal(
            apap.map_points(outside_support, unsupported="identity"),
            outside_support,
        )

    def test_apap_reference_does_not_replace_singular_local_field_with_global(self):
        yy, xx = np.mgrid[20.0:492.0:9j, 20.0:492.0:9j]
        source = np.column_stack((xx.ravel(), yy.ravel()))
        target = source + np.array([8.0, -5.0])
        apap = fit_apap_reference(source, target, grid_shape=(3, 3))
        query = np.array([[256.0, 256.0]], dtype=np.float64)
        self.assertTrue(np.any(apap.support_counts > 0))

        apap.homographies[:] = 0.0
        with self.assertRaisesRegex(
            TransformEstimationError, "singular.*no global homography fallback"
        ):
            apap.map_points(query)

    def test_native_apap_rejects_queries_without_local_support(self):
        clustered = np.array(
            [
                [100.0, 100.0], [110.0, 100.0], [100.0, 110.0], [110.0, 110.0],
                [300.0, 300.0], [310.0, 300.0], [300.0, 310.0], [310.0, 310.0],
            ],
            dtype=np.float64,
        )
        target = clustered.copy()
        target[:4] += np.array([7.0, -3.0])
        target[4:] += np.array([-6.0, 5.0])
        apap = fit_apap(
            clustered,
            target,
            global_homography=estimate_homography(clustered, target),
            grid_shape=(3, 3),
            sigma=(20.0, 20.0),
            min_support=4,
        )

        self.assertTrue(np.any(apap.support_counts == 0))
        with self.assertRaisesRegex(
            TransformEstimationError, "no fitted local correspondence support"
        ):
            unsupported_query = np.array([[205.0, 205.0]], dtype=np.float64)
            apap.map_points(unsupported_query)
        np.testing.assert_array_equal(
            apap.map_points(unsupported_query, unsupported="identity"),
            unsupported_query,
        )

    def test_native_apap_reports_unqualified_opengl_before_loading_module(self):
        import os
        from unittest.mock import patch

        points = np.array(
            [[0.0, 0.0], [32.0, 0.0], [0.0, 32.0], [32.0, 32.0]],
            dtype=np.float64,
        )
        from taichi_vision.taichi_algorithm import aot_api

        with patch.dict(os.environ, {"PIXEL_REFINE_AOT_ARCH": "opengl"}), patch.object(
            aot_api, "load_tcm"
        ) as load_tcm:
            with self.assertRaisesRegex(
                RuntimeError, "not runtime-qualified on OpenGL"
            ):
                fit_apap(points, points + np.array([2.0, -1.0]))
        load_tcm.assert_not_called()

    def test_apap_flow_preserves_local_inverse_mapping_and_pixel_units(self):
        yy, xx = np.meshgrid(np.linspace(8.0, 88.0, 6), np.linspace(8.0, 120.0, 8), indexing="ij")
        reference = np.column_stack((xx.ravel(), yy.ravel()))
        support = reference + np.column_stack((
            6.0 * np.sin(reference[:, 0] / 30.0),
            3.0 * np.cos(reference[:, 1] / 25.0),
        ))
        warp = fit_apap(reference, support, grid_shape=(4, 4))
        flow = warp.to_flow((17, 19), full_shape=(96, 128))
        qx, qy = np.meshgrid(np.linspace(0, 127, 19), np.linspace(0, 95, 17))
        query = np.column_stack((qx.ravel(), qy.ravel()))
        reconstructed = query + flow.reshape(-1, 2) * np.array((128 / 19, 96 / 17))
        np.testing.assert_allclose(reconstructed, warp.map_points(query), atol=1e-5)
        self.assertEqual(flow.dtype, np.float32)
        self.assertGreater(float(np.ptp(flow[..., 0])), 0.5)
        with self.assertRaises(ValueError):
            warp.to_flow((1, 19), full_shape=(96, 128))

    def test_native_apap_mesh_stays_on_device_and_matches_point_mapping(self):
        from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
            compute_sparse_mesh,
            warp_image_sparse_mesh,
        )

        yy, xx = np.meshgrid(
            np.linspace(8.0, 88.0, 6),
            np.linspace(8.0, 120.0, 8),
            indexing="ij",
        )
        source = np.column_stack((xx.ravel(), yy.ravel()))
        target = source + np.column_stack(
            (
                6.0 * np.sin(source[:, 0] / 30.0),
                3.0 * np.cos(source[:, 1] / 25.0),
            )
        )
        warp = fit_apap(source, target, grid_shape=(4, 4))

        mesh_buffer = warp._map_mesh_buffer((128, 96), (17, 19))
        native_mesh = mesh_buffer.to_numpy()
        point_mesh = compute_sparse_mesh(warp, (128, 96), (17, 19))
        self.assertEqual(mesh_buffer.shape, (17, 19, 2))
        self.assertTrue(mesh_buffer.is_vector)
        np.testing.assert_allclose(native_mesh, point_mesh, atol=2.0e-5, rtol=1.0e-7)

        image_y, image_x = np.mgrid[:96, :128]
        image = (
            0.45 + 0.25 * np.sin(image_x * 0.12) * np.cos(image_y * 0.09)
        ).astype(np.float32)
        reference = np.roll(image, 2, axis=1)
        candidates = np.array(
            [[2.0, 0.0], [-2.0, 0.0], [0.0, 2.0], [0.0, -2.0]],
            dtype=np.float32,
        )
        device_warp, device_mask = warp_image_sparse_mesh(
            image,
            warp,
            mesh_shape=(17, 19),
            ref_image=reference,
            cand_motions=candidates,
            enable_adaptive_refine=True,
            max_refine_iters=2,
        )
        legacy_warp, legacy_mask = warp_image_sparse_mesh(
            image,
            warp.map_points,
            mesh_shape=(17, 19),
            ref_image=reference,
            cand_motions=candidates,
            enable_adaptive_refine=True,
            max_refine_iters=2,
        )
        np.testing.assert_allclose(device_warp, legacy_warp, atol=5.0e-7, rtol=1.0e-6)
        np.testing.assert_array_equal(device_mask, legacy_mask)

        resident_result = warp_image_sparse_mesh(
            image,
            warp,
            mesh_shape=(17, 19),
            ref_image=reference,
            cand_motions=candidates,
            enable_adaptive_refine=True,
            max_refine_iters=2,
            return_gpu=True,
        )
        self.assertTrue(hasattr(resident_result, "to_numpy"))
        np.testing.assert_allclose(
            resident_result.to_numpy(), legacy_warp, atol=5.0e-7, rtol=1.0e-6
        )

    def test_rgb_apap_bounded_search_corrects_all_channels_from_luma(self):
        from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
            warp_image_sparse_mesh,
        )

        height, width = 48, 64
        yy, xx = np.mgrid[:height, :width]
        pattern = ((xx * 17 + yy * 29 + xx * yy * 3) % 251).astype(np.float32) / 250.0
        image = np.stack(
            (pattern, np.roll(pattern, 3, axis=0), np.roll(pattern, 5, axis=1)),
            axis=-1,
        ).astype(np.float32)
        reference = np.roll(image, 2, axis=1)
        grid_y, grid_x = np.mgrid[0.0 : height - 1.0 : 7j, 0.0 : width - 1.0 : 7j]
        points = np.column_stack((grid_x.ravel(), grid_y.ravel()))
        warp = fit_apap(points, points, grid_shape=(4, 4))

        refined, _ = warp_image_sparse_mesh(
            image,
            warp,
            mesh_shape=(17, 19),
            ref_image=reference,
            cand_motions=np.asarray([[-2.0, 0.0]], dtype=np.float32),
            enable_adaptive_refine=True,
            max_refine_iters=2,
        )

        baseline_error = float(np.mean(np.abs(image[4:-4, 4:-4] - reference[4:-4, 4:-4])))
        refined_error = float(np.mean(np.abs(refined[4:-4, 4:-4] - reference[4:-4, 4:-4])))
        self.assertEqual(refined.shape, image.shape)
        self.assertTrue(np.isfinite(refined).all())
        self.assertLess(refined_error, baseline_error * 0.1)

    def test_rgb_fused_warp_refine_matches_two_pass_output(self):
        from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
            _get_aot_mesh_module,
            warp_image_sparse_mesh,
        )
        from taichi_vision.taichi_aot.engine import engine

        height, width = 48, 64
        yy, xx = np.mgrid[:height, :width]
        pattern = ((xx * 11 + yy * 23 + xx * yy * 5) % 241).astype(np.float32) / 240.0
        image = np.stack(
            (pattern, np.roll(pattern, 2, axis=0), np.roll(pattern, 4, axis=1)),
            axis=-1,
        ).astype(np.float32)
        reference = np.roll(image, 2, axis=1)
        points_y, points_x = np.mgrid[0.0 : height - 1.0 : 7j, 0.0 : width - 1.0 : 7j]
        points = np.column_stack((points_x.ravel(), points_y.ravel())).astype(np.float32)
        warp = fit_apap(points, points, grid_shape=(4, 4))
        native_engine, module = _get_aot_mesh_module()
        source_gpu = native_engine.upload(image, is_vector=True, vector_dim=3)
        reference_gpu = native_engine.upload(reference, is_vector=True, vector_dim=3)
        mesh_gpu = warp._map_mesh_buffer(
            (width, height), (17, 19), allow_unsupported=True
        )
        u_gpu = native_engine.upload(np.linspace(0.0, 18.0, width, dtype=np.float32))
        v_gpu = native_engine.upload(np.linspace(0.0, 16.0, height, dtype=np.float32))
        candidates = np.asarray([[-2.0, 0.0]], dtype=np.float32)
        candidates_gpu = native_engine.upload(candidates, is_vector=True, vector_dim=2)
        two_pass_gpu = native_engine.allocate(
            (height, width, 3), dtype=np.float32, is_vector=True, vector_dim=3
        )
        try:
            graph_args = dict(
                mesh=mesh_gpu,
                u_grid=u_gpu,
                v_grid=v_gpu,
                dst=two_pass_gpu,
                w_src_f=float(width - 1),
                h_src_f=float(height - 1),
                w_mesh_max=18,
                h_mesh_max=16,
                w_src_max=width - 1,
                h_src_max=height - 1,
            )
            module.run("sparse_mesh_warp_3d_f32", src=source_gpu, **graph_args)
            module.run(
                "adaptive_refine_3d_f32",
                ref=reference_gpu,
                warped=two_pass_gpu,
                mov=source_gpu,
                cand_motions=candidates_gpu,
                num_cands=1,
                err_threshold=0.04,
                max_iters=2,
                **{key: value for key, value in graph_args.items() if key != "dst"},
                dst=two_pass_gpu,
            )
            native_engine.sync()
            two_pass = two_pass_gpu.to_numpy()

            fused_gpu = warp_image_sparse_mesh(
                source_gpu,
                warp,
                mesh_shape=(17, 19),
                ref_image=reference_gpu,
                cand_motions=candidates,
                enable_adaptive_refine=True,
                max_refine_iters=2,
                return_gpu=True,
            )
            try:
                np.testing.assert_allclose(
                    fused_gpu.to_numpy(), two_pass, atol=5.0e-7, rtol=1.0e-6
                )
            finally:
                fused_gpu.release()
        finally:
            for buffer in (
                two_pass_gpu,
                candidates_gpu,
                v_gpu,
                u_gpu,
                mesh_gpu,
                reference_gpu,
                source_gpu,
            ):
                buffer.release()

    def test_apap_model_grid_is_independent_of_warp_mesh_density(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        recorded = {}

        class IdentityWarp:
            def map_points(self, points):
                return np.asarray(points)

        def capture_fit(
            source,
            target,
            *,
            grid_shape,
            enable_residual_spline,
            global_homography=None,
            sigma=None,
        ):
            recorded["fit_grid"] = grid_shape
            recorded["residual_enabled"] = enable_residual_spline
            recorded["global_homography"] = global_homography
            recorded["sigma"] = sigma
            return IdentityWarp()

        def capture_warp(**kwargs):
            recorded["warp_grid"] = kwargs["mesh_shape"]
            recorded["adaptive_refine"] = kwargs["enable_adaptive_refine"]
            recorded["ref_image"] = kwargs["ref_image"]
            return kwargs["image"], np.ones(kwargs["image"].shape[:2], dtype=bool)

        with patch.object(apap_module, "fit_apap", capture_fit), patch.object(
            mesh_warp, "warp_image_sparse_mesh", capture_warp
        ):
            mesh_warp.warp_apap(
                np.zeros((20, 30, 3), dtype=np.float32),
                np.zeros((4, 2), dtype=np.float32),
                np.ones((4, 2), dtype=np.float32),
                mesh_shape=(33, 33),
                fit_grid_shape=(17, 17),
            )

        self.assertEqual(recorded["fit_grid"], (17, 17))
        self.assertEqual(recorded["warp_grid"], (33, 33))
        self.assertFalse(recorded["residual_enabled"])

    def test_warp_apap_default_fit_grid_is_independent_from_mesh_density(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        recorded = {}

        class IdentityWarp:
            def map_points(self, points):
                return np.asarray(points)

        def capture_fit(
            source,
            target,
            *,
            grid_shape,
            enable_residual_spline,
            global_homography=None,
            sigma=None,
        ):
            recorded["fit_grid"] = grid_shape
            recorded["residual_enabled"] = enable_residual_spline
            recorded["global_homography"] = global_homography
            recorded["sigma"] = sigma
            return IdentityWarp()

        def capture_warp(**kwargs):
            recorded["warp_grid"] = kwargs["mesh_shape"]
            recorded["adaptive_refine"] = kwargs["enable_adaptive_refine"]
            recorded["ref_image"] = kwargs["ref_image"]
            return kwargs["image"], np.ones(kwargs["image"].shape[:2], dtype=bool)

        with patch.object(apap_module, "fit_apap", capture_fit), patch.object(
            mesh_warp, "warp_image_sparse_mesh", capture_warp
        ):
            mesh_warp.warp_apap(
                np.zeros((20, 30), dtype=np.float32),
                np.zeros((4, 2), dtype=np.float32),
                np.ones((4, 2), dtype=np.float32),
                ref_image=np.ones((20, 30), dtype=np.float32),
                mesh_shape=(33, 33),
            )

        self.assertEqual(recorded["fit_grid"], (4, 4))
        self.assertEqual(recorded["warp_grid"], (33, 33))
        self.assertFalse(recorded["residual_enabled"])
        self.assertTrue(recorded["adaptive_refine"])
        self.assertIsNotNone(recorded["ref_image"])

    def test_adaptive_mesh_warp_uploads_motion_candidates_as_vec2(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        uploaded = []
        allocated = []
        graph_runs = []
        readbacks = []

        class FakeBuffer:
            def __init__(self, value):
                self.value = np.asarray(value)

            def to_numpy(self):
                readbacks.append(self.value)
                return self.value

        class FakeEngine:
            arch = "cpu"
            gpu_name = "test device"

            def upload(self, value, **kwargs):
                uploaded.append((np.asarray(value).shape, kwargs, np.asarray(value).copy()))
                return FakeBuffer(value)

            def allocate(self, shape, **kwargs):
                allocated.append((tuple(shape), kwargs))
                return FakeBuffer(np.zeros(shape, dtype=kwargs.get("dtype", np.float32)))

        class FakeModule:
            def run(self, graph_name, **kwargs):
                graph_runs.append((graph_name, kwargs))
                return None

        image = np.ones((8, 8), dtype=np.float32)
        result = None
        with patch.object(
            mesh_warp, "_get_aot_mesh_module", return_value=(FakeEngine(), FakeModule())
        ):
            result = mesh_warp.warp_image_sparse_mesh(
                image,
                lambda points: np.asarray(points),
                mesh_shape=(3, 3),
                ref_image=image,
                enable_adaptive_refine=True,
            )

        candidate_upload = next(
            item for item in uploaded if item[0] == (1, 2)
        )
        self.assertEqual(candidate_upload[1], {"is_vector": True, "vector_dim": 2})
        refine_args = next(
            kwargs for graph_name, kwargs in graph_runs
            if graph_name == "adaptive_refine_2d_f32"
        )
        self.assertIs(refine_args["warped"], refine_args["dst"])
        full_frame_zero_uploads = [
            item for item in uploaded
            if item[0] == image.shape and np.count_nonzero(item[2]) == 0
        ]
        self.assertEqual(len(full_frame_zero_uploads), 0)
        self.assertIn(((8, 8), {"dtype": np.float32}), allocated)
        self.assertIs(result[0], readbacks[-1])

    def test_sparse_mesh_warp_can_return_native_output_without_readback(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        readbacks = []
        graph_runs = []

        class FakeBuffer:
            def __init__(self, value):
                self.value = np.asarray(value)
                self.shape = self.value.shape
                self.dtype = self.value.dtype
                self.is_vector = self.value.ndim == 3

            def to_numpy(self):
                readbacks.append(self.value)
                return self.value

        class FakeEngine:
            arch = "cpu"
            gpu_name = "test device"

            def upload(self, value, **_kwargs):
                return FakeBuffer(value)

            def allocate(self, shape, **kwargs):
                return FakeBuffer(np.zeros(shape, dtype=kwargs.get("dtype", np.float32)))

            def sync(self):
                return None

        class FakeModule:
            def run(self, graph_name, **kwargs):
                graph_runs.append((graph_name, kwargs))

        image = np.ones((8, 8), dtype=np.float32)
        with patch.object(
            mesh_warp, "_get_aot_mesh_module", return_value=(FakeEngine(), FakeModule())
        ):
            output = mesh_warp.warp_image_sparse_mesh(
                image,
                lambda points: np.asarray(points),
                mesh_shape=(3, 3),
                return_gpu=True,
            )

        self.assertIsInstance(output, FakeBuffer)
        self.assertEqual(readbacks, [])
        self.assertEqual(len(graph_runs), 1)
        self.assertEqual(graph_runs[0][0], "sparse_mesh_warp_2d_f32")

    def test_tps(self):
        src_pts = np.array([[10.0, 10.0], [90.0, 10.0], [10.0, 90.0], [90.0, 90.0], [50.0, 50.0]], dtype=np.float64)
        dst_pts = src_pts + np.array([2.0, -1.0])

        warp, _ = fit_tps_checked(src_pts, dst_pts)
        self.assertIsInstance(warp, TPSWarp)

        mapped = warp.map_points(src_pts)
        err = np.mean(np.abs(mapped - dst_pts))
        self.assertLess(err, 1e-3)

    def test_warp_image(self):
        # Create a simple synthetic image
        img = np.zeros((100, 100), dtype=np.float32)
        img[30:70, 30:70] = 1.0

        src_pts = np.array([[20.0, 20.0], [80.0, 20.0], [20.0, 80.0], [80.0, 80.0]], dtype=np.float64)
        dst_pts = src_pts + np.array([5.0, 5.0]) # 5-px shift

        # Inverse mapping: dst -> src
        inv_warp = fit_aanap(dst_pts, src_pts, grid_shape=(2, 2))
        warped, mask = warp_image(img, inv_warp)

        self.assertEqual(warped.shape, (100, 100))
        self.assertEqual(mask.shape, (100, 100))
        # Center should have shifted by +5 px
        self.assertGreater(warped[40, 40], 0.5)

    def test_align_burst_stack(self):
        # Generate 3 frames of synthetic burst images
        h, w = 120, 120
        base = np.zeros((h, w), dtype=np.float32)
        # Add rich feature points
        np.random.seed(42)
        for _ in range(30):
            rx, ry = np.random.randint(15, 105, 2)
            base[ry-3:ry+4, rx-3:rx+4] = np.random.uniform(0.5, 1.0)

        # Shift frames slightly to simulate handheld jitter
        f0 = base.copy()
        f1 = np.roll(np.roll(base, 2, axis=0), 3, axis=1)
        f2 = np.roll(np.roll(base, -1, axis=0), -2, axis=1)

        aligned, reports = align_burst_stack([f0, f1, f2], reference_index=0, method="aanap")
        self.assertEqual(len(aligned), 3)
        self.assertEqual(len(reports), 3)
        for frame in aligned:
            self.assertEqual(frame.shape, (h, w))

    def test_align_burst_apap_uses_native_mesh_warp_and_reference_search(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        reference = np.zeros((48, 64), dtype=np.float32)
        moving = np.ones_like(reference)
        points = np.array(
            [[4.0, 4.0], [59.0, 4.0], [59.0, 43.0], [4.0, 43.0], [31.0, 22.0]],
            dtype=np.float64,
        )
        expected_mask = np.ones(reference.shape, dtype=bool)
        with patch.object(
            mesh_warp,
            "warp_apap",
            return_value=(moving.copy(), expected_mask),
        ) as native_warp:
            aligned, reports = align_burst_stack(
                [reference, moving],
                method="apap",
                grid_shape=(5, 5),
                sigma=12.0,
                guided_matches=[None, (points, points)],
            )

        self.assertEqual(aligned[1].shape, reference.shape)
        self.assertEqual(reports[1]["method"], "apap")
        self.assertIs(native_warp.call_args.kwargs["ref_image"], reference)
        self.assertTrue(native_warp.call_args.kwargs["enable_adaptive_refine"])
        self.assertEqual(native_warp.call_args.kwargs["fit_grid_shape"], (5, 5))
        self.assertEqual(native_warp.call_args.kwargs["sigma"], 12.0)

    def test_align_burst_apap_runs_native_identity_seed_and_search(self):
        rng = np.random.default_rng(20261018)
        reference = rng.random((40, 56), dtype=np.float32)
        moving = np.roll(np.roll(reference, 1, axis=0), 2, axis=1)
        x, y = np.meshgrid(
            np.linspace(8.0, 46.0, 5),
            np.linspace(7.0, 31.0, 4),
        )
        reference_points = np.column_stack((x.ravel(), y.ravel()))
        moving_points = reference_points + np.array([2.0, 1.0])

        aligned, reports = align_burst_stack(
            [reference, moving],
            method="apap",
            grid_shape=(3, 3),
            guided_matches=[None, (reference_points, moving_points)],
        )

        self.assertEqual(reports[1]["method"], "apap")
        self.assertEqual(aligned[1].shape, reference.shape)
        self.assertTrue(np.isfinite(aligned[1]).all())
        before = float(np.mean(np.square(moving - reference)))
        after = float(np.mean(np.square(aligned[1] - reference)))
        self.assertLess(after, before)

    def test_align_multi_image_panorama(self):
        # Generate 3 horizontal overlapping image frames
        h, w = 80, 100
        canvas_wide = np.zeros((h, 240), dtype=np.float32)
        # Texture
        np.random.seed(99)
        for _ in range(60):
            rx, ry = np.random.randint(10, 230), np.random.randint(10, 70)
            canvas_wide[ry-2:ry+3, rx-2:rx+3] = np.random.uniform(0.5, 1.0)

        img0 = canvas_wide[:, 0:100].copy()
        img1 = canvas_wide[:, 70:170].copy()
        img2 = canvas_wide[:, 140:240].copy()

        # Single-row panorama of 3 images
        pano, report = align_multi_image_panorama([img0, img1, img2], method="aanap", blend="feather")
        self.assertGreater(pano.shape[1], 150)
        self.assertEqual(report["image_count"], 3)

    def test_align_multi_image_panorama_routes_apap_rows_through_aot(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.panorama import stitch as panorama_stitch

        image = np.zeros((24, 32), dtype=np.float32)
        calls = []

        def fake_stitch(images, **kwargs):
            calls.append((len(images), kwargs))
            return np.asarray(images[0]).copy()

        with patch.object(
            panorama_stitch, "stitch_panorama", side_effect=fake_stitch
        ):
            panorama, report = align_multi_image_panorama(
                [image, image.copy(), image.copy(), image.copy()],
                grid_layout=(2, 2),
                method="apap",
            )
            multi_row_calls = list(calls)
            calls.clear()
            align_multi_image_panorama(
                [image, image.copy()],
                method="apap",
            )

        self.assertEqual(report["layout"], "multi_row_2x2")
        self.assertEqual(panorama.shape, image.shape)
        self.assertEqual(len(multi_row_calls), 3)
        self.assertTrue(all(kwargs["refine"] == "apap" for _, kwargs in multi_row_calls))
        self.assertTrue(all(kwargs["backend"] == "aot" for _, kwargs in multi_row_calls))

        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1]["backend"], "aot")

    def test_align_multi_image_panorama_apap_executes_single_and_multi_row(self):
        image = np.zeros((32, 40), dtype=np.float32)
        rng = np.random.default_rng(20261018)
        image[4:28, 4:36] = rng.random((24, 32), dtype=np.float32)
        points = np.array(
            [[5.0, 5.0], [34.0, 5.0], [34.0, 26.0], [5.0, 26.0], [20.0, 15.0]],
            dtype=np.float64,
        )

        def matcher(_reference: np.ndarray, _moving: np.ndarray):
            return points.copy(), points.copy()

        single_row, single_report = align_multi_image_panorama(
            [image, image.copy()],
            method="apap",
            blend="average",
            matcher=matcher,
        )
        multi_row, multi_report = align_multi_image_panorama(
            [image, image.copy(), image.copy(), image.copy()],
            grid_layout=(2, 2),
            method="apap",
            blend="average",
            matcher=matcher,
        )

        self.assertEqual(single_report["layout"], "single_row")
        self.assertEqual(multi_report["layout"], "multi_row_2x2")
        self.assertTrue(np.isfinite(single_row).all())
        self.assertTrue(np.isfinite(multi_row).all())


if __name__ == "__main__":
    unittest.main()
