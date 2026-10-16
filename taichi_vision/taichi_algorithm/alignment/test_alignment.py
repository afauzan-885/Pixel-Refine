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
    estimate_homography,
    project_points,
)


class TestAlignment(unittest.TestCase):
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

        mapped = warp.map_points(src_pts)
        err = np.mean(np.abs(mapped - dst_pts))
        self.assertLess(err, 0.5)

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
        err = np.mean(np.abs(mapped - all_ref))
        self.assertLess(err, 0.05)

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
        query = np.array([[100.0, 100.0], [400.0, 400.0], [250.0, 250.0]])
        expected_support = query + np.column_stack(
            (
                22.0 * np.sin(query[:, 0] / 100.0),
                10.0 * np.sin(query[:, 1] / 90.0),
            )
        )
        global_support = project_points(
            query, np.linalg.inv(support_to_reference)
        )

        apap_error = np.mean(
            np.linalg.norm(apap.map_points(query) - expected_support, axis=1)
        )
        homography_error = np.mean(
            np.linalg.norm(global_support - expected_support, axis=1)
        )
        self.assertLess(apap_error, homography_error * 0.1)

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

    def test_apap_model_grid_is_independent_of_warp_mesh_density(self):
        from unittest.mock import patch
        from taichi_vision.taichi_algorithm.alignment import apap as apap_module
        from taichi_vision.taichi_algorithm.alignment import mesh_warp

        recorded = {}

        class IdentityWarp:
            def map_points(self, points):
                return np.asarray(points)

        def capture_fit(source, target, *, grid_shape):
            recorded["fit_grid"] = grid_shape
            return IdentityWarp()

        def capture_warp(**kwargs):
            recorded["warp_grid"] = kwargs["mesh_shape"]
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


if __name__ == "__main__":
    unittest.main()
