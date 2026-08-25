"""Focused smoke tests for the family-local SfM/MVS orchestration."""

from __future__ import annotations

import os
import unittest
import importlib.util

import numpy as np

os.environ.setdefault("AOT_MODE", "1")

from taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline import (  # noqa: E402
    PairwiseSfMConfig,
    reconstruct_pair,
    reconstruct_sequence,
    run_plane_sweep_mvs,
    run_point_cloud_pipeline,
)
from taichi_vision.taichi_algorithm.sfm.registration import (  # noqa: E402
    integrate_tsdf,
    point_to_plane_icp,
    project_points,
    solve_pnp_checked,
)
from taichi_vision.taichi_algorithm.sfm.poisson_recon import poisson_reconstruct  # noqa: E402


def _project(points, K, R, t):
    camera = (R @ points.T).T + t.reshape(1, 3)
    image = (K @ camera.T).T
    return image[:, :2] / image[:, 2:3]


class ReconstructionPipelineTests(unittest.TestCase):
    def setUp(self):
        self.K = np.array(
            [[500.0, 0.0, 128.0], [0.0, 500.0, 128.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        rng = np.random.default_rng(44)
        self.points = np.column_stack(
            [rng.uniform(-1.0, 1.0, 48), rng.uniform(-0.8, 0.8, 48), rng.uniform(2.0, 8.0, 48)]
        )

    def test_known_calibrated_pair_passes_quality_gate(self):
        R = np.eye(3, dtype=np.float64)
        t = np.array([-0.25, 0.0, 0.0], dtype=np.float64)
        p1 = _project(self.points, self.K, np.eye(3), np.zeros(3))
        p2 = _project(self.points, self.K, R, t)

        result = reconstruct_pair(
            p1,
            p2,
            self.K,
            self.K,
            config=PairwiseSfMConfig(
                min_inlier_count=16,
                min_inlier_ratio=0.5,
                reprojection_threshold_px=1.0,
                max_hypotheses=2,
            ),
        )

        self.assertTrue(result.success, result.report.warnings)
        self.assertGreaterEqual(result.report.metrics["inlier_ratio"], 0.5)
        self.assertLess(float(np.median(result.reprojection_error_px)), 1.0)
        self.assertEqual(result.points_3d.shape[1], 3)
        self.assertTrue(np.isfinite(result.confidence).all())

    def test_all_point_fundamental_fallback_rejects_outliers(self):
        angle = 0.08
        R = np.array(
            [[np.cos(angle), 0.0, np.sin(angle)], [0.0, 1.0, 0.0], [-np.sin(angle), 0.0, np.cos(angle)]],
            dtype=np.float64,
        )
        t = np.array([-0.25, 0.01, 0.02], dtype=np.float64)
        p1 = _project(self.points, self.K, np.eye(3), np.zeros(3))
        p2 = _project(self.points, self.K, R, t)
        p2[::4] = np.random.default_rng(2).uniform(0.0, 256.0, (len(p2[::4]), 2))

        result = reconstruct_pair(
            p1,
            p2,
            self.K,
            self.K,
            config=PairwiseSfMConfig(
                min_inlier_count=20,
                min_inlier_ratio=0.4,
                reprojection_threshold_px=1.5,
                max_hypotheses=2,
            ),
        )

        self.assertTrue(result.success, result.report.warnings)
        self.assertGreaterEqual(result.report.metrics["n_inliers"], 20)
        self.assertLess(result.report.metrics["n_inliers"], len(p1))
        self.assertTrue(
            any(
                any(f"pose_method={method}" in item for method in ("vsac_fundamental", "eight_point_all", "five_point"))
                for item in result.report.warnings
            )
        )

    def test_mvs_budget_is_checked_before_allocation(self):
        image = np.zeros((100, 120), dtype=np.float32)
        with self.assertRaises(MemoryError):
            run_plane_sweep_mvs(
                image,
                [image],
                self.K,
                [self.K],
                [np.eye(3, dtype=np.float32)],
                [np.array([-0.2, 0.0, 0.0], dtype=np.float32)],
                n_depths=64,
                max_volume_bytes=1024,
            )

    def test_mvs_aot_research_leaves_are_reused(self):
        height, width = 16, 18
        yy, xx = np.indices((height, width), dtype=np.float32)
        image = ((xx + yy) / max(height + width - 2, 1)).astype(np.float32)
        K = np.array(
            [[32.0, 0.0, width * 0.5], [0.0, 32.0, height * 0.5], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        try:
            result = run_plane_sweep_mvs(
                image,
                [image.copy()],
                K,
                [K],
                [np.eye(3, dtype=np.float32)],
                [np.array([-0.2, 0.0, 0.0], dtype=np.float32)],
                depth_min=0.8,
                depth_max=1.2,
                n_depths=3,
                patch_radius=1,
                backend="aot",
                max_volume_bytes=1_000_000,
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(result.report.backend, "plane-sweep-aot")
        self.assertEqual(result.depth.shape, image.shape)
        self.assertEqual(result.confidence.shape, image.shape)
        self.assertTrue(np.isfinite(result.depth).all())
        self.assertTrue(np.isfinite(result.confidence).all())
        self.assertTrue(np.all(result.depth >= 0.8 - 1.0e-5))
        self.assertTrue(np.all(result.depth <= 1.2 + 1.0e-5))

    def test_point_cloud_preprocess_reports_finite_output(self):
        result = run_point_cloud_pipeline(
            self.points.astype(np.float32),
            voxel_size=0.05,
            sor_k=4,
            build_surface=False,
        )
        self.assertEqual(result.points.shape[1], 3)
        self.assertEqual(result.normals.shape, result.points.shape)
        self.assertTrue(np.isfinite(result.points).all())
        self.assertTrue(np.isfinite(result.normals).all())
        with self.assertRaises(MemoryError):
            run_point_cloud_pipeline(self.points.astype(np.float32), max_points=8)

    def test_point_cloud_pipeline_reuses_aot_research_leaves(self):
        try:
            result = run_point_cloud_pipeline(
                self.points.astype(np.float32),
                voxel_size=0.05,
                sor_k=4,
                sor_std=2.0,
                build_surface=True,
                grid_resolution=8,
                solver_iterations=2,
                dilate_radius=0,
                max_grid_voxels=1024,
                backend="aot",
            )
        except NotImplementedError as exc:
            self.skipTest(str(exc))
        self.assertEqual(result.report.backend, "point-cloud-aot")
        self.assertEqual(result.points.shape[1], 3)
        self.assertEqual(result.normals.shape, result.points.shape)
        self.assertEqual(result.vertices.shape[1], 3)
        self.assertEqual(result.faces.shape[1], 3)
        self.assertTrue(np.isfinite(result.points).all())
        self.assertTrue(np.isfinite(result.normals).all())

    def test_point_to_plane_icp_recovers_translation(self):
        rng = np.random.default_rng(4)
        target = rng.uniform(-1.0, 1.0, (80, 3)).astype(np.float64)
        target[:, 2] += 3.0
        normals = target / np.linalg.norm(target, axis=1, keepdims=True)
        source = target + np.array([0.02, -0.01, 0.03])

        result = point_to_plane_icp(
            source,
            target,
            normals,
            max_iterations=30,
            max_correspondence_distance=0.2,
        )

        self.assertTrue(result.success, result.report.warnings)
        self.assertTrue(result.converged)
        self.assertLess(result.report.metrics["rmse"], 1.0e-5)
        np.testing.assert_allclose(result.transform[:3, 3], [-0.02, 0.01, -0.03], atol=2.0e-3)

    def test_sequence_pose_chain_keeps_trusted_prefix(self):
        p1 = _project(self.points, self.K, np.eye(3), np.zeros(3))
        p2 = _project(self.points, self.K, np.eye(3), np.array([-0.25, 0.0, 0.0]))
        result = reconstruct_sequence(
            [(p1, p2), (p1, p2)],
            [self.K, self.K, self.K],
            config=PairwiseSfMConfig(
                min_inlier_count=16,
                min_inlier_ratio=0.5,
                reprojection_threshold_px=1.0,
                max_hypotheses=2,
            ),
        )
        self.assertTrue(result.success, result.report.warnings)
        self.assertEqual(len(result.poses_world_to_camera), 3)
        self.assertTrue(np.isfinite(np.stack(result.poses_world_to_camera)).all())

    def test_tsdf_integration_is_bounded_and_observes_surface(self):
        depth = np.full((8, 8), 2.0, dtype=np.float32)
        K = np.array([[50.0, 0.0, 4.0], [0.0, 50.0, 4.0], [0.0, 0.0, 1.0]], dtype=np.float32)
        result = integrate_tsdf(
            [depth],
            [K],
            [np.eye(4, dtype=np.float64)],
            voxel_size=0.1,
            truncation=0.2,
            origin=(-0.4, -0.4, 1.6),
            grid_shape=(8, 8, 8),
            max_voxels=1024,
        )
        self.assertEqual(result.tsdf.shape, (8, 8, 8))
        self.assertGreater(int(result.weights.sum()), 0)
        self.assertTrue(np.isfinite(result.tsdf).all())
        self.assertLessEqual(result.report.metrics["grid_voxels"], 1024.0)
        with self.assertRaises(MemoryError):
            integrate_tsdf(
                [depth],
                [K],
                [np.eye(4, dtype=np.float64)],
                grid_shape=(16, 16, 16),
                max_voxels=128,
            )

    def test_projection_and_pnp_quality_gate(self):
        if importlib.util.find_spec("cv2") is None:
            self.skipTest("OpenCV reference backend is unavailable")
        object_points = np.array(
            [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]],
            dtype=np.float64,
        )
        translation = np.array([0.0, 0.0, 4.0], dtype=np.float64)
        image_points, valid = project_points(object_points, self.K, np.eye(3), translation)
        self.assertTrue(valid.all())
        result = solve_pnp_checked(object_points, image_points, self.K)
        self.assertTrue(result.success, result.report.warnings)
        self.assertEqual(int(np.count_nonzero(result.inlier_mask)), len(object_points))
        self.assertLess(float(np.median(result.reprojection_error_px)), 1.0e-4)

    def test_poisson_small_cloud_reference_path(self):
        points = np.array(
            [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0.5, 0.5, 0.01], [0.5, 0, 0.01]],
            dtype=np.float32,
        )
        normals = np.tile(np.array([0.0, 0.0, 1.0], dtype=np.float32), (len(points), 1))
        vertices, faces = poisson_reconstruct(
            points,
            normals,
            grid_resolution=8,
            solver_iterations=2,
            dilate_radius=0,
        )
        self.assertEqual(vertices.shape[1], 3)
        self.assertEqual(faces.shape[1], 3)
        self.assertTrue(np.isfinite(vertices).all())


if __name__ == "__main__":
    unittest.main()
