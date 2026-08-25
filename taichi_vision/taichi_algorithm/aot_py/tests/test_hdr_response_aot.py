"""CPU target-qualified HDR residual/response/merge parity contracts."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


_ROOT = Path(__file__).resolve().parents[4]

_PROBE = r"""
import os
import numpy as np
from taichi_vision.taichi_algorithm.image_processing.hdr_stack import deghost_confidence
from taichi_vision.taichi_algorithm.image_processing.hdr_response import (
    estimate_response_curve,
    merge_radiance,
)

rng = np.random.default_rng(20260812)
reference = rng.random((9, 11), dtype=np.float32)
target = np.clip(reference * 0.8 + 0.04, 0.0, 1.0).astype(np.float32)
a = deghost_confidence(reference, target, backend="aot", smooth_radius=0, threshold=0.1)
b = deghost_confidence(reference, target, backend="taichi", smooth_radius=0, threshold=0.1)
assert np.isfinite(a).all() and np.max(np.abs(a - b)) <= 2e-6

times = np.array([0.25, 0.5, 1.0], dtype=np.float32)
frames = [np.clip(reference * t, 0.0, 1.0).astype(np.float32) for t in times]
linear_aot = merge_radiance(frames, times, backend="aot")
linear_np = merge_radiance(frames, times, backend="numpy")
assert np.max(np.abs(linear_aot - linear_np)) <= 2e-5
cal = estimate_response_curve(frames, times, levels=32, sample_count=32, backend="aot")
assert cal.solver_backend == "aot-quantize+numpy-lstsq"
log_aot = merge_radiance(frames, times, calibration=cal, method="log", levels=32, backend="aot")
log_np = merge_radiance(frames, times, calibration=cal, method="log", levels=32, backend="numpy")
assert np.max(np.abs(log_aot - log_np)) <= 2e-5
print("HDR_AOT_RESULT ok", flush=True)
os._exit(0)
"""


class HDRResponseAOTTests(unittest.TestCase):
    def test_cpu_target_hdr_leaf_parity(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "1",
                "PIXEL_REFINE_AOT_ARCH": "cpu",
                "PIXEL_REFINE_DISABLE_AOT_WATCHDOG": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            }
        )
        result = subprocess.run(
            [sys.executable, "-B", "-c", _PROBE],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"HDR AOT probe failed:\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        self.assertIn("HDR_AOT_RESULT ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
