"""Integration contracts for the explicit NumPy SfM orchestration path.

The point-cloud kernels are imported when ``AOT_MODE=0`` but require an
active Taichi runtime.  A composed pipeline that explicitly requests
``backend='numpy'`` must therefore select the reference helpers directly;
this regression test exercises that boundary in the same process as the
other SfM stages.
"""

from __future__ import annotations

import unittest

import numpy as np

# ``aot_py`` is a script collection rather than a Python package (it has no
# package ``__init__``), so pytest's importlib mode cannot resolve a relative
# import beyond ``tests``.  Use the canonical repository package path instead;
# this keeps the harness independent of invocation style without changing the
# runtime API under test.
from taichi_vision.taichi_algorithm.sfm.reconstruction_pipeline import (
    run_point_cloud_pipeline,
)
from taichi_vision.taichi_algorithm.sfm.registration import (
    integrate_tsdf,
    point_to_plane_icp,
)


class SfMNumPyBackendContractTests(unittest.TestCase):
    def test_point_cloud_pipeline_does_not_enter_uninitialised_taichi(self):
        rng = np.random.default_rng(20260810)
        points = rng.uniform(-1.0, 1.0, size=(48, 3)).astype(np.float32)
        points[:, 2] += 3.0

        result = run_point_cloud_pipeline(
            points,
            voxel_size=0.05,
            sor_k=8,
            backend="numpy",
        )

        self.assertEqual(result.report.backend, "point-cloud-numpy")
        self.assertGreater(len(result.points), 0)
        self.assertEqual(result.points.shape, result.normals.shape)
        self.assertTrue(np.isfinite(result.points).all())
        self.assertTrue(np.isfinite(result.normals).all())

    def test_registration_numpy_stages_remain_composable(self):
        rng = np.random.default_rng(11)
        target = rng.uniform(-0.4, 0.4, size=(12, 3)).astype(np.float64)
        target[:, 2] += 2.0
        source = target + np.asarray([0.01, -0.01, 0.02])
        normals = np.tile(np.asarray([0.0, 0.0, 1.0]), (len(target), 1))

        icp = point_to_plane_icp(
            source,
            target,
            normals,
            max_iterations=3,
            max_correspondence_distance=0.2,
            backend="numpy",
        )
        self.assertEqual(icp.report.backend, "numpy-reference")
        self.assertTrue(np.isfinite(icp.transform).all())

        depth = np.full((5, 6), 2.0, dtype=np.float32)
        K = np.asarray(
            [[30.0, 0.0, 2.5], [0.0, 30.0, 2.0], [0.0, 0.0, 1.0]],
            dtype=np.float64,
        )
        tsdf = integrate_tsdf(
            [depth],
            [K],
            [np.eye(4, dtype=np.float64)],
            voxel_size=0.1,
            truncation=0.2,
            origin=(-0.2, -0.2, 1.6),
            grid_shape=(5, 5, 5),
            max_voxels=125,
            backend="numpy",
        )
        self.assertEqual(tsdf.report.backend, "numpy-reference")
        self.assertGreater(int(np.count_nonzero(tsdf.weights)), 0)
        self.assertTrue(np.isfinite(tsdf.tsdf).all())


if __name__ == "__main__":
    unittest.main()
