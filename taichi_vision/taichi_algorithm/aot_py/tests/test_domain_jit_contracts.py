"""CPU-JIT contract probes for exposure, tone mapping, and minimal SfM."""

from __future__ import annotations

import unittest

try:
    from .test_domain_catalog import _run_probe
except ImportError:  # pragma: no cover - unittest discover compatibility
    from test_domain_catalog import _run_probe


class DomainJitContractTests(unittest.TestCase):
    def test_exposure_reinhard_five_point_and_cheirality(self):
        payload = _run_probe(
            r'''
import json
import numpy as np
from taichi_vision.taichi_algorithm.image_processing.tone_mapping import reinhard_tone_map
from taichi_vision.taichi_algorithm.panorama.exposure import (
    apply_exposure_compensation,
    estimate_exposure_compensation,
)
from taichi_vision.taichi_algorithm.sfm.cheirality_check import (
    check_cheirality_full,
    check_cheirality_minimal,
)
from taichi_vision.taichi_algorithm.sfm.five_point_solver import solve_five_point

# Constant-field Reinhard oracle.  With lum_white=1 the burn-out factor
# cancels algebraically for this bounded case.
image = np.full((8, 9, 3), 0.5, dtype=np.float32)
toned = reinhard_tone_map(image, key=0.18, lum_white=1.0, epsilon=1.0e-6)
expected_tone = (0.18 / 0.5 * 0.5) / (1.0 + 0.18 / 0.5 * 0.5)
tone_error = float(np.max(np.abs(toned - expected_tone)))
assert np.isfinite(toned).all() and toned.shape == image.shape

# Affine exposure compensation: target = reference*1.25 - 0.08.
rng = np.random.default_rng(7)
reference = np.clip(rng.random((16, 20), dtype=np.float32), 0.05, 0.95)
target = reference * np.float32(1.25) - np.float32(0.08)
numpy_model = estimate_exposure_compensation([reference, target], backend="numpy")
taichi_model = estimate_exposure_compensation([reference, target], backend="taichi")
numpy_result = apply_exposure_compensation([reference, target], numpy_model, backend="numpy")[1]
taichi_result = apply_exposure_compensation([reference, target], taichi_model, backend="taichi")[1]
exposure_error = float(np.max(np.abs(numpy_result - taichi_result)))
assert np.isfinite(taichi_result).all()
assert np.allclose(taichi_model.gains[1, 0], 0.8, atol=2.0e-5)
assert np.allclose(taichi_model.offsets[1, 0], 0.064, atol=2.0e-5)

# Exact calibrated two-view geometry in normalized camera coordinates.
rng = np.random.default_rng(42)
points3d = np.column_stack((
    rng.uniform(-0.8, 0.8, 5),
    rng.uniform(-0.6, 0.6, 5),
    rng.uniform(3.0, 7.0, 5),
))
angle = 0.08
rotation = np.array([
    [np.cos(angle), 0.0, np.sin(angle)],
    [0.0, 1.0, 0.0],
    [-np.sin(angle), 0.0, np.cos(angle)],
], dtype=np.float64)
translation = np.array([-0.3, 0.02, 0.05], dtype=np.float64)
points1 = points3d[:, :2] / points3d[:, 2, None]
camera2 = (rotation @ points3d.T).T + translation
points2 = camera2[:, :2] / camera2[:, 2, None]
cross = np.array([
    [0.0, -translation[2], translation[1]],
    [translation[2], 0.0, -translation[0]],
    [-translation[1], translation[0], 0.0],
])
essential = cross @ rotation
candidates = solve_five_point(points1, points2)
assert candidates
residual = min(
    float(np.max(np.abs(np.einsum(
        "ni,ij,nj->n",
        np.c_[points2, np.ones(5)], candidate,
        np.c_[points1, np.ones(5)],
    ))))
    for candidate in candidates
)
assert residual < 1.0e-4, residual
minimal_valid, _, _ = check_cheirality_minimal(
    essential, np.eye(3), np.eye(3), points1, points2
)
positive_count, mask = check_cheirality_full(
    rotation, translation, np.eye(3), np.eye(3), points1, points2
)
assert minimal_valid
assert positive_count == 5 and bool(mask.all())
print(json.dumps({
    "tone_error": tone_error,
    "exposure_error": exposure_error,
    "five_point_residual": residual,
    "cheirality_positive": int(positive_count),
    "tone_backend": "taichi-cpu-jit",
    "exposure_backend": taichi_model.backend,
}))
''',
            mode="0",
        )
        self.assertLess(payload["tone_error"], 2.0e-5)
        self.assertLess(payload["exposure_error"], 2.0e-5)
        self.assertLess(payload["five_point_residual"], 1.0e-4)
        self.assertEqual(payload["cheirality_positive"], 5)
        self.assertEqual(payload["tone_backend"], "taichi-cpu-jit")
        self.assertEqual(payload["exposure_backend"], "taichi")


if __name__ == "__main__":
    unittest.main()
