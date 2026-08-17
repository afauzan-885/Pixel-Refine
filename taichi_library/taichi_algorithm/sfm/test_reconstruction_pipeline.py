"""Known-value and allocation-gate tests for the SfM family orchestration."""

from __future__ import annotations

import unittest

import numpy as np

from .reconstruction_pipeline import (
    PairwiseSfMConfig,
    reconstruct_pair,
    run_patchmatch_mvs,
    run_plane_sweep_mvs,
    run_sgm_mvs,
)
from .registration import integrate_tsdf, point_to_plane_icp


def _synthetic_pair(seed: int = 3):
    rng = np.random.default_rng(seed)
    points = rng.uniform([-1.0, -1.0, 3.0], [1.0, 1.0, 8.0], size=(48, 3))
    intrinsics = np.asarray([[500.0, 0.0, 32.0], [0.0, 500.0, 24.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    translation = np.asarray([0.25, 0.0, 0.0], dtype=np.float64)

    def project(rotation, offset):
        camera = (rotation @ points.T).T + offset
        return (camera[:, :2] / camera[:, 2:3]) @ intrinsics[:2, :2].T + intrinsics[:2, 2]

    return (
        project(np.eye(3), np.zeros(3)),
        project(np.eye(3), translation),
        intrinsics,
    )


class ReconstructionPipelineTests(unittest.TestCase):
    def test_known_calibrated_pair_passes_pose_and_reprojection_gates(self):
        points1, points2, intrinsics = _synthetic_pair()
        result = reconstruct_pair(
            points1,
            points2,
            intrinsics,
            intrinsics,
            config=PairwiseSfMConfig(
                max_hypotheses=4,
                min_inlier_count=12,
                min_inlier_ratio=0.5,
                min_cheirality_ratio=0.5,
            ),
        )
        self.assertTrue(result.success, result.report.warnings)
        self.assertEqual(len(result.points_3d), len(points1))
        self.assertTrue(np.isfinite(result.points_3d).all())
        self.assertLess(float(np.median(result.reprojection_error_px)), 1.0e-2)
        self.assertGreaterEqual(result.report.metrics["cheirality_ratio"], 0.5)

    def test_plane_sweep_budget_is_checked_before_dispatch(self):
        image = np.zeros((32, 32), dtype=np.float32)
        K = np.eye(3, dtype=np.float32)
        with self.assertRaises(MemoryError):
            run_plane_sweep_mvs(
                image,
                [image],
                K,
                [K],
                [np.eye(3, dtype=np.float32)],
                [np.zeros(3, dtype=np.float32)],
                n_depths=64,
                max_volume_bytes=1,
            )

    def test_sgm_mvs_is_finite_and_deterministic(self):
        height, width = 10, 12
        yy, xx = np.indices((height, width), dtype=np.float32)
        image = (0.2 * xx + 0.7 * yy + 0.01 * xx * yy).astype(np.float32)
        K = np.asarray(
            [[24.0, 0.0, width * 0.5], [0.0, 24.0, height * 0.5], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        args = (
            image,
            [image.copy()],
            K,
            [K],
            [np.eye(3, dtype=np.float32)],
            [np.zeros(3, dtype=np.float32)],
        )
        kwargs = dict(
            depth_min=0.8,
            depth_max=1.2,
            n_depths=5,
            patch_radius=1,
            backend="numpy",
            max_volume_bytes=2_000_000,
            directions=4,
            refine=False,
        )
        first = run_sgm_mvs(*args, **kwargs)
        second = run_sgm_mvs(*args, **kwargs)
        self.assertEqual(first.report.backend, "sgm-numpy")
        self.assertEqual(first.depth.shape, image.shape)
        self.assertTrue(np.isfinite(first.depth).all())
        self.assertTrue(np.isfinite(first.confidence).all())
        np.testing.assert_array_equal(first.depth, second.depth)
        np.testing.assert_array_equal(first.confidence, second.confidence)
        self.assertGreaterEqual(first.report.metrics["depth_valid_fraction"], 1.0)

    def test_patchmatch_mvs_is_bounded_and_repeatable(self):
        image = np.arange(8 * 9, dtype=np.float32).reshape(8, 9)
        K = np.asarray(
            [[20.0, 0.0, 4.0], [0.0, 20.0, 3.5], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        args = (
            image,
            [image],
            K,
            [K],
            [np.eye(3, dtype=np.float32)],
            [np.zeros(3, dtype=np.float32)],
        )
        kwargs = dict(
            depth_min=1.0,
            depth_max=2.0,
            n_depths=4,
            patch_radius=0,
            backend="numpy",
            iterations=2,
            random_seed=7,
            max_volume_bytes=1_000_000,
            refine=False,
        )
        first = run_patchmatch_mvs(*args, **kwargs)
        second = run_patchmatch_mvs(*args, **kwargs)
        self.assertEqual(first.report.backend, "patchmatch-numpy")
        self.assertEqual(first.depth.shape, image.shape)
        self.assertTrue(np.isfinite(first.depth).all())
        self.assertTrue(np.isfinite(first.confidence).all())
        np.testing.assert_array_equal(first.depth, second.depth)
        np.testing.assert_array_equal(first.confidence, second.confidence)

    def test_sgm_and_patchmatch_budget_precedes_cost_volume(self):
        image = np.zeros((32, 32), dtype=np.float32)
        K = np.eye(3, dtype=np.float32)
        args = (
            image,
            [image],
            K,
            [K],
            [np.eye(3, dtype=np.float32)],
            [np.zeros(3, dtype=np.float32)],
        )
        for method in (run_sgm_mvs, run_patchmatch_mvs):
            with self.assertRaises(MemoryError):
                method(
                    *args,
                    n_depths=16,
                    depth_min=1.0,
                    depth_max=2.0,
                    max_volume_bytes=1024,
                )

    def test_registration_aot_is_explicit_or_fail_closed(self):
        """AOT must execute the qualified graph or report its absence."""

        rng = np.random.default_rng(23)
        target = rng.uniform(-1.0, 1.0, size=(12, 3)).astype(np.float64)
        target[:, 2] += 3.0
        source = target + np.asarray([0.01, -0.01, 0.02], dtype=np.float64)
        normals = np.tile(np.asarray([0.0, 0.0, 1.0]), (len(target), 1))
        try:
            icp = point_to_plane_icp(
                source,
                target,
                normals,
                max_iterations=4,
                max_correspondence_distance=0.2,
                backend="aot",
            )
        except NotImplementedError as exc:
            self.assertIn("sfm_registration", str(exc))
        else:
            self.assertEqual(icp.report.backend, "aot")
            self.assertTrue(icp.success)
            self.assertTrue(np.isfinite(icp.transform).all())
            reference_icp = point_to_plane_icp(
                source,
                target,
                normals,
                max_iterations=4,
                max_correspondence_distance=0.2,
                backend="numpy",
            )
            np.testing.assert_allclose(icp.transform, reference_icp.transform, atol=2.0e-5, rtol=2.0e-5)

        depth = np.full((6, 6), 2.0, dtype=np.float32)
        K = np.asarray(
            [[40.0, 0.0, 3.0], [0.0, 40.0, 3.0], [0.0, 0.0, 1.0]],
            dtype=np.float32,
        )
        try:
            tsdf = integrate_tsdf(
                [depth],
                [K],
                [np.eye(4, dtype=np.float64)],
                voxel_size=0.1,
                truncation=0.2,
                origin=(-0.3, -0.3, 1.6),
                grid_shape=(6, 6, 6),
                max_voxels=216,
                backend="aot",
            )
        except NotImplementedError as exc:
            self.assertIn("sfm_registration", str(exc))
        else:
            self.assertEqual(tsdf.report.backend, "aot")
            self.assertGreater(int(np.count_nonzero(tsdf.weights)), 0)
            self.assertTrue(np.isfinite(tsdf.tsdf).all())
            reference_tsdf = integrate_tsdf(
                [depth],
                [K],
                [np.eye(4, dtype=np.float64)],
                voxel_size=0.1,
                truncation=0.2,
                origin=(-0.3, -0.3, 1.6),
                grid_shape=(6, 6, 6),
                max_voxels=216,
                backend="numpy",
            )
            np.testing.assert_allclose(tsdf.tsdf, reference_tsdf.tsdf, atol=2.0e-5, rtol=2.0e-5)
            np.testing.assert_array_equal(tsdf.weights, reference_tsdf.weights)


if __name__ == "__main__":
    unittest.main()
