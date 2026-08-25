"""Contract tests for the newly exposed SfM AOT/hybrid adapters.

VSAC is intentionally optional because existing target artifacts may predate
its heavier fundamental-estimation graph. The test accepts either a validated
result or an explicit NotImplementedError, never a silent fallback.
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

desc1 = np.zeros((7, 16), dtype=np.uint8)
desc2 = desc1.copy()
desc2[3, 0] = 255
matches, distances = ta.bfmatcher_hamming(desc1, desc2, k=1)
assert matches.shape == (7, 2), matches.shape
assert distances.shape == (7,), distances.shape
assert np.array_equal(matches[:, 0], np.arange(7, dtype=np.int32))
assert int(distances[3]) in (0, 8)

pts1 = np.array([[0., 0.], [1., 0.], [0., 1.], [1., 1.], [0.2, 0.4]], dtype=np.float32)
pts2 = pts1 + np.array([0.03, -0.02], dtype=np.float32)
candidates = ta.solve_five_point(pts1, pts2)
assert isinstance(candidates, list) and candidates
assert all(np.asarray(candidate).shape == (3, 3) for candidate in candidates)
assert all(np.isfinite(candidate).all() for candidate in candidates)

rng = np.random.default_rng(17)
try:
    result = ta.vsac_fundamental(
        rng.random((12, 2), dtype=np.float32),
        rng.random((12, 2), dtype=np.float32),
    )
except NotImplementedError as exc:
    assert "AOT" in str(exc) or "artifact" in str(exc)
else:
    F, mask, stats = result
    assert np.asarray(F).shape == (3, 3)
    assert np.asarray(mask).shape == (12,)
    assert isinstance(stats, dict)
print("AOT_GAP_RESULT ok", flush=True)
"""


class AOTGapAdapterTests(unittest.TestCase):
    def test_hamming_five_point_and_vsac_contracts(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "1",
                "AOT_ARCH": "cpu",
                "DISABLE_AOT_WATCHDOG": "1",
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
            f"AOT gap probe failed:\nstdout={result.stdout}\nstderr={result.stderr}",
        )
        self.assertIn("AOT_GAP_RESULT ok", result.stdout)


if __name__ == "__main__":
    unittest.main()
