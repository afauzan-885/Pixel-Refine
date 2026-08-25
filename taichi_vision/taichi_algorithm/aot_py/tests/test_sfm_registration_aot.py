"""Target-qualified CPU AOT parity checks for ICP and TSDF registration."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


class SfMRegistrationAOTTests(unittest.TestCase):
    """Exercise the exact CPU artifact without changing the parent runtime."""

    def test_cpu_aot_registration_matches_numpy_reference(self):
        root = Path(__file__).resolve().parents[4]
        artifact = (
            root
            / "taichi_vision"
            / "taichi_algorithm"
            / "aot_tcm"
            / "cpu_x86_64_windows"
            / "sfm_registration_cpu_x86_64_windows.tcm"
        )
        if not artifact.is_file():
            self.skipTest(f"CPU sfm_registration artifact is unavailable: {artifact}")

        script = r"""
import json
import numpy as np
from taichi_vision.taichi_algorithm.sfm.registration import integrate_tsdf, point_to_plane_icp

rng = np.random.default_rng(22)
target = rng.normal(size=(10, 3)).astype(np.float32)
source = target + np.array([0.02, -0.01, 0.0], dtype=np.float32)
normals = np.zeros_like(target)
normals[:, 2] = 1.0
kwargs = dict(
    max_iterations=2,
    min_correspondences=6,
    max_correspondence_distance=2.0,
    max_kernel_pairs=200,
)
reference_icp = point_to_plane_icp(source, target, normals, backend="numpy", **kwargs)
aot_icp = point_to_plane_icp(source, target, normals, backend="aot", **kwargs)

depth = np.ones((6, 6), dtype=np.float32)
K = np.array([[4.0, 0.0, 2.5], [0.0, 4.0, 2.5], [0.0, 0.0, 1.0]], dtype=np.float32)
pose = np.eye(4, dtype=np.float32)
tsdf_kwargs = dict(
    voxel_size=0.1,
    truncation=0.2,
    origin=(-0.2, -0.2, 0.7),
    grid_shape=(4, 4, 4),
    max_voxels=1000,
)
reference_tsdf = integrate_tsdf([depth], [K], [pose], backend="numpy", **tsdf_kwargs)
aot_tsdf = integrate_tsdf([depth], [K], [pose], backend="aot", **tsdf_kwargs)

payload = {
    "icp_backend": aot_icp.report.backend,
    "tsdf_backend": aot_tsdf.report.backend,
    "transform_max_abs": float(np.max(np.abs(aot_icp.transform - reference_icp.transform))),
    "residual_max_abs": float(np.max(np.abs(aot_icp.residuals - reference_icp.residuals))),
    "correspondences_equal": bool(np.array_equal(aot_icp.correspondences, reference_icp.correspondences)),
    "tsdf_max_abs": float(np.max(np.abs(aot_tsdf.tsdf - reference_tsdf.tsdf))),
    "weights_equal": bool(np.array_equal(aot_tsdf.weights, reference_tsdf.weights)),
}
print("RESULT " + json.dumps(payload, sort_keys=True))
"""
        env = os.environ.copy()
        env["AOT_MODE"] = "1"
        env["AOT_ARCH"] = "cpu"
        # The parent suite may disable the application's auto-destroy
        # watchdog for CPU-JIT runs.  This child intentionally exercises the
        # real CPU AOT bridge, so isolate that setting; otherwise the bridge's
        # watchdog can hard-exit during interpreter teardown and turn a
        # successful parity run into a spurious return code 1.
        env["AUTO_DESTROY"] = "1"
        env["DISABLE_AOT_WATCHDOG"] = "1"
        env.pop("TI_ARCH", None)
        env.pop("TAICHI_ARCH", None)
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(
            completed.returncode, 0, completed.stdout + "\n" + completed.stderr
        )
        lines = [
            line.strip()
            for line in completed.stdout.splitlines()
            if line.startswith("RESULT ")
        ]
        self.assertTrue(lines, completed.stdout + "\n" + completed.stderr)
        payload = json.loads(lines[-1][len("RESULT ") :])
        self.assertEqual(payload["icp_backend"], "aot")
        self.assertEqual(payload["tsdf_backend"], "aot")
        self.assertLessEqual(payload["transform_max_abs"], 1.0e-5)
        self.assertLessEqual(payload["residual_max_abs"], 1.0e-5)
        self.assertTrue(payload["correspondences_equal"])
        self.assertLessEqual(payload["tsdf_max_abs"], 1.0e-5)
        self.assertTrue(payload["weights_equal"])


if __name__ == "__main__":
    unittest.main()
