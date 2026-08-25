"""Focused checks for previously fail-closed legacy facade entries.

The tests intentionally execute in a fresh AOT CPU process.  They exercise
the existing bicubic/remap/pyramid/BM3D graphs and pure host helpers through
the public ``taichi_algorithm`` facade; no OpenCV oracle or JIT fallback is
needed for the contract checks.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


_ROOT = Path(__file__).resolve().parents[4]


_PROBE = r"""
import numpy as np
import taichi_vision.taichi_algorithm as ta

img = np.arange(25, dtype=np.float32).reshape(5, 5)
rgb = np.stack([img, img + 100.0, img + 200.0], axis=-1)

bilinear = ta.sample_at_bilinear(img, 1.5, 2.25)
bicubic = ta.sample_at_bicubic(img, 1.5, 2.25)
rgb_sample = ta.sample_at_bicubic(rgb, 1.5, 2.25)
rgb_channel = ta.sample_at_bilinear(rgb, 1.5, 2.25, channel=1)
grid = ta.sample_at_bilinear(img, [0.0, 1.5], [1.0, 2.25])
assert np.isclose(bilinear, 12.75, atol=1e-5), bilinear
assert np.isclose(bicubic, 12.75, atol=1e-5), bicubic
assert rgb_sample.shape == (3,) and np.allclose(rgb_sample, [12.75, 112.75, 212.75], atol=1e-5)
assert np.isclose(rgb_channel, 112.75, atol=1e-5)
assert grid.shape == (2,) and np.allclose(grid, [5.0, 12.75], atol=1e-5)

flow = np.ones((3, 4, 2), dtype=np.float32)
flow_up = ta.upsample_flow(flow, 6, 8)
assert flow_up.shape == (6, 8, 2) and np.allclose(flow_up, 2.0, atol=1e-5)

dct = ta.build_dct_matrix(4)
assert dct.shape == (4, 4) and np.allclose(dct @ dct.T, np.eye(4), atol=1e-5)

denoised = ta.hfcd_denoise(
    np.linspace(0.0, 1.0, 32 * 32, dtype=np.float32).reshape(32, 32),
    0.05,
    block_size=4,
    search_radius=2,
    max_matches=2,
)
assert denoised.shape == (32, 32) and np.isfinite(denoised).all()

for name in (
    "sample_at_bilinear", "sample_at_bicubic", "sample_at", "upsample_flow",
    "hfcd_denoise", "build_dct_matrix",
):
    value = getattr(ta, name)
    assert "Fail-closed" not in (getattr(value, "__doc__", "") or ""), name
print("LEGACY_REMAINING_RESULT ok", flush=True)
"""


class LegacyRemainingTests(unittest.TestCase):
    def test_aot_adapters_and_returns(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "1",
                "TAICHI_ARCH": "cpu",
                "TAICHI_ARCH": "cpu",
                "AOT_ARCH": "cpu",
                "DISABLE_AOT_WATCHDOG": "1",
                "AUTO_DESTROY": "1",
            }
        )
        completed = subprocess.run(
            # Source-only family modules are frequently edited while the
            # AOT child is launched.  ``-B`` prevents a timestamp-equal stale
            # pyc from hiding the current contract under test.
            [sys.executable, "-B", "-c", _PROBE],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=240,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"legacy remaining AOT probe failed:\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertIn("LEGACY_REMAINING_RESULT ok", completed.stdout)


if __name__ == "__main__":
    unittest.main()
