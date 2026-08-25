"""JIT regression for the native integral-image ZNCC orchestration."""

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[4]


class NCCJITTests(unittest.TestCase):
    def test_jit_zncc_returns_score_map_and_peak(self):
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "0",
                "TAICHI_ARCH": "cpu",
                "TAICHI_ARCH": "cpu",
                "AOT_ARCH": "cpu",
                # Keep the long-lived worker alive for the duration of the
                # child; the parent test process owns normal teardown.
                "AUTO_DESTROY": "0",
            }
        )
        code = r"""
import numpy as np
from taichi_vision.taichi_algorithm.alignment.ncc import zncc
rng = np.random.default_rng(4)
image = rng.random((20, 24), dtype=np.float32)
template = image[5:10, 7:13].copy()
score = zncc(image, template)
assert score.shape == (16, 19), score.shape
assert np.isfinite(score).all()
peak = np.unravel_index(np.argmax(score), score.shape)
assert tuple(int(v) for v in peak) == (5, 7), peak
print("NCC_JIT_RESULT ok", flush=True)
"""
        completed = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"JIT ZNCC probe failed:\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertIn("NCC_JIT_RESULT ok", completed.stdout)


if __name__ == "__main__":
    unittest.main()
