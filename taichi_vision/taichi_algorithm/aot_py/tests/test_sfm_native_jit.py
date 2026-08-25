"""CPU-JIT parity smoke tests for family-local 3D kernels.

The test subprocess loads the SfM modules under lightweight package stubs.
This keeps the check independent from the application's AOT/OpenGL bootstrap
and verifies the explicit ``backend='taichi'`` path on a CPU worker.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


class NativeSfMJitTests(unittest.TestCase):
    def test_cpu_jit_registration_tsdf_and_plane_sweep_parity(self):
        root = Path(__file__).resolve().parents[4]
        script = r'''
import importlib.util
import json
import pathlib
import sys
import types
import numpy as np

base = pathlib.Path("taichi_vision/taichi_algorithm")
for name, path in [
    ("taichi_vision", base.parent.parent),
    ("taichi_vision.taichi_algorithm", base),
    ("taichi_vision.taichi_algorithm.sfm", base / "sfm"),
]:
    module = types.ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module

name = "taichi_vision.taichi_algorithm.pipeline_common"
spec = importlib.util.spec_from_file_location(name, base / "pipeline_common.py")
common = importlib.util.module_from_spec(spec)
sys.modules[name] = common
spec.loader.exec_module(common)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

registration = load(
    "taichi_vision.taichi_algorithm.sfm.registration",
    base / "sfm" / "registration.py",
)
plane_sweep = load(
    "taichi_vision.taichi_algorithm.sfm.plane_sweep",
    base / "sfm" / "plane_sweep.py",
)
mvs_regularization = load(
    "taichi_vision.taichi_algorithm.sfm.mvs_regularization",
    base / "sfm" / "mvs_regularization.py",
)
if not registration.TAICHI_AVAILABLE:
    raise RuntimeError("Taichi is unavailable in the AOT_MODE=0 subprocess")
registration.ti.init(arch=registration.ti.cpu, offline_cache=False)

rng = np.random.default_rng(17)
target = rng.uniform(-1.0, 1.0, (32, 3)).astype(np.float64)
target[:, 2] += 3.0
source = target + np.array([0.015, -0.010, 0.025])
normals = np.tile(np.array([0.0, 0.0, 1.0]), (len(target), 1))
numpy_icp = registration.point_to_plane_icp(
    source, target, normals, max_iterations=12,
    max_correspondence_distance=0.2, backend="numpy",
)
taichi_icp = registration.point_to_plane_icp(
    source, target, normals, max_iterations=12,
    max_correspondence_distance=0.2, backend="taichi",
)
if not taichi_icp.success or abs(float(taichi_icp.transform[2, 3] - numpy_icp.transform[2, 3])) > 2.0e-3:
    raise AssertionError("Taichi ICP did not match the NumPy z-translation")

depth = np.full((8, 8), 2.0, dtype=np.float32)
K = np.array([[50.0, 0.0, 4.0], [0.0, 50.0, 4.0], [0.0, 0.0, 1.0]], dtype=np.float32)
pose = np.eye(4, dtype=np.float64)
numpy_tsdf = registration.integrate_tsdf(
    [depth], [K], [pose], voxel_size=0.1, truncation=0.2,
    origin=(-0.4, -0.4, 1.6), grid_shape=(8, 8, 8), max_voxels=1024,
    backend="numpy",
)
taichi_tsdf = registration.integrate_tsdf(
    [depth], [K], [pose], voxel_size=0.1, truncation=0.2,
    origin=(-0.4, -0.4, 1.6), grid_shape=(8, 8, 8), max_voxels=1024,
    backend="taichi",
)
if int(taichi_tsdf.weights.sum()) <= 0 or not np.isfinite(taichi_tsdf.tsdf).all():
    raise AssertionError("Taichi TSDF did not observe a finite surface")
if abs(float(np.mean(taichi_tsdf.tsdf) - np.mean(numpy_tsdf.tsdf))) > 0.08:
    raise AssertionError("Taichi TSDF diverges from the NumPy reference")

# Project exactly on half-pixel coordinates.  The reference uses ``np.rint``
# (ties-to-even), so (0.5, 0.5) must sample pixel (0, 0), not (1, 1).  This
# catches the historical ``floor(u + 0.5)`` native rounding mismatch.
half_depth = np.array([[1.0, 2.0], [2.0, 2.0]], dtype=np.float32)
K_half = np.array([[1.0, 0.0, 0.5], [0.0, 1.0, 0.5], [0.0, 0.0, 1.0]], dtype=np.float32)
half_kwargs = dict(
    voxel_size=1.0,
    truncation=2.0,
    origin=(-0.5, -0.5, 0.5),
    grid_shape=(1, 1, 1),
    max_voxels=8,
)
numpy_half = registration.integrate_tsdf(
    [half_depth], [K_half], [pose], backend="numpy", **half_kwargs,
)
taichi_half = registration.integrate_tsdf(
    [half_depth], [K_half], [pose], backend="taichi", **half_kwargs,
)
if not np.array_equal(taichi_half.weights, numpy_half.weights) or not np.allclose(
    taichi_half.tsdf, numpy_half.tsdf, atol=1.0e-6, rtol=0.0
):
    raise AssertionError(
        "Taichi TSDF does not match NumPy np.rint ties-to-even at half-pixels"
    )

h = w = 12
y, x = np.indices((h, w))
image = ((x + 2 * y) / 20.0).astype(np.float32)
K_small = np.array([[15.0, 0.0, 5.5], [0.0, 15.0, 5.5], [0.0, 0.0, 1.0]], dtype=np.float32)
R = np.eye(3, dtype=np.float32)
t = np.array([0.1, 0.0, 0.0], dtype=np.float32)
numpy_depth, _ = plane_sweep.plane_sweep_stereo(
    image, image, K_small, K_small, R, t,
    depth_min=0.8, depth_max=1.2, n_depths=3, patch_radius=1, backend="numpy",
)
taichi_depth, _ = plane_sweep.plane_sweep_stereo(
    image, image, K_small, K_small, R, t,
    depth_min=0.8, depth_max=1.2, n_depths=3, patch_radius=1, backend="taichi",
)
plane_diff = float(np.mean(np.abs(taichi_depth - numpy_depth)))
if not np.isfinite(taichi_depth).all() or plane_diff > 0.2:
    raise AssertionError("Taichi plane sweep is not finite/parity-compatible")

# The global SGM/PatchMatch recurrences now have explicit serial Taichi-JIT
# kernels.  Exercise them directly on a bounded volume so this test does not
# conflate the native recurrence with the separate plane-sweep orchestration.
cost = np.ascontiguousarray(rng.random((4, 8, 9)), dtype=np.float32)
sgm = mvs_regularization._regularize_sgm_taichi(cost, directions=4, p1=0.02, p2=0.20)
labels, selected = mvs_regularization._regularize_patchmatch_taichi(
    cost, iterations=2, random_seed=17
)
if not np.isfinite(sgm).all() or not np.isfinite(selected).all():
    raise AssertionError("Taichi SGM/PatchMatch produced non-finite costs")
if labels.shape != cost.shape[1:] or np.any(labels < 0) or np.any(labels >= cost.shape[0]):
    raise AssertionError("Taichi PatchMatch produced invalid labels")

print(json.dumps({
    "icp_backend": taichi_icp.report.backend,
    "tsdf_backend": taichi_tsdf.report.backend,
    "plane_sweep_mean_abs": plane_diff,
    "sgm_finite": bool(np.isfinite(sgm).all()),
    "patchmatch_finite": bool(np.isfinite(selected).all()),
}))
'''
        env = os.environ.copy()
        env["AOT_MODE"] = "0"
        # A few developer shells export ``TI_ARCH=cpu``; Taichi 1.7 names its
        # CPU backend ``x64`` and treats that value as an invalid architecture.
        # The child explicitly calls ``ti.init(arch=ti.cpu)`` below, so remove
        # the ambient selector to make the test deterministic.
        env.pop("TI_ARCH", None)
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + "\n" + completed.stderr)
        lines = [line.strip() for line in completed.stdout.splitlines() if line.strip().startswith("{")]
        self.assertTrue(lines, completed.stdout)
        payload = json.loads(lines[-1])
        self.assertEqual(payload["icp_backend"], "taichi-cpu-jit")
        self.assertEqual(payload["tsdf_backend"], "taichi-cpu-jit")
        self.assertLessEqual(payload["plane_sweep_mean_abs"], 0.2)
        self.assertTrue(payload["sgm_finite"])
        self.assertTrue(payload["patchmatch_finite"])


if __name__ == "__main__":
    unittest.main()
