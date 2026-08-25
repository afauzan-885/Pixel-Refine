"""Regression checks for the legacy :mod:`taichi_algorithm` facade.

The package has two import contracts (AOT and JIT).  A static ``__all__``
without a matching attribute in either mode makes ``from ... import *`` fail
before a caller can select an explicit backend.  This test intentionally runs
each mode in a subprocess: the package initialiser owns Taichi/AOT runtime
lifecycle and must not be reloaded in the parent test process.

The child only imports the module and classifies exported values as callable or
constant.  It never invokes an exported function, so placeholders or optional
runtime operations cannot be mistaken for execution evidence.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


_ROOT = Path(__file__).resolve().parents[4]


_PROBE = r"""
import json
import importlib
import os
import sys

module = importlib.import_module("taichi_vision.taichi_algorithm")
names = list(getattr(module, "__all__", ()))
missing = [name for name in names if not hasattr(module, name)]
star_namespace = {}
star_error = ""
try:
    # Exercise the public import contract itself.  ``exec`` keeps the probe
    # namespace isolated and, importantly, does not invoke any imported
    # callable; it only binds the names selected by ``__all__``.
    exec("from taichi_vision.taichi_algorithm import *", star_namespace)
except Exception as exc:
    star_error = f"{type(exc).__name__}: {exc}"
star_missing = [name for name in names if name not in star_namespace]
missing = sorted(set(missing).union(star_missing))
callable_names = []
constant_names = []
for name in names:
    if name in missing:
        continue
    value = getattr(module, name)
    if callable(value):
        callable_names.append(name)
    else:
        constant_names.append(name)
payload = {
    "count": len(names),
    "unique": len(set(names)),
    "missing": missing,
    "star_missing": star_missing,
    "star_error": star_error,
    "callable_count": len(callable_names),
    "constant_count": len(constant_names),
    "callable": sorted(callable_names),
    "constants": sorted(constant_names),
}
print("EXPORT_RESULT " + json.dumps(payload, sort_keys=True))
sys.stdout.flush()
os._exit(0 if not missing else 17)
"""


_ADAPTER_PROBE = r"""
import os
import sys
import numpy as np
import taichi_vision.taichi_algorithm as ta

image = np.zeros((16, 16), dtype=np.float32)
image[8, :] = 1.0
image[:, 8] = 1.0
lines, edges = ta.hough_lines_with_canny(image, vote_threshold=2)
levels = ta.build_image_pyramid(image, levels=3)
points = np.asarray([[0, 0, 0], [0.01, 0.01, 0], [1, 1, 1]], dtype=np.float32)
filtered, keep = ta.radius_outlier_removal(points, radius=0.1, min_neighbors=1)
translation = ta.global_translate_zncc(image, image)
tone = ta.contrast_adjust(np.ones((4, 4, 3), dtype=np.float32), 1.1, 0.01)
assert isinstance(lines, list) and edges.shape == image.shape
assert [level.shape for level in levels] == [(16, 16), (8, 8), (4, 4)]
assert filtered.ndim == 2 and keep.ndim == 1 and filtered.shape[0] == keep.shape[0]
assert len(translation) == 3 and np.isfinite(translation).all()
assert tone.shape == (4, 4, 3) and np.isfinite(tone).all()
print("ADAPTER_RESULT ok", flush=True)
sys.stdout.flush()
os._exit(0)
"""


_JIT_ADAPTER_PROBE = r"""
import os
import sys
import numpy as np
import taichi_vision.taichi_algorithm as ta

image = np.zeros((8, 8), dtype=np.float32)
image[2:6, 3:5] = 1.0
flow = np.zeros((8, 8, 2), dtype=np.float32)
gray = np.zeros((8, 8, 3), dtype=np.float32)
outputs = {
    "gaussian": ta.gaussian(image, 3),
    "bilateral": ta.bilateral(image, 3, 1, 1),
    "ransac": ta.ransac(flow),
    "gray": ta.cvtColor(gray, ta.COLOR_BGR2GRAY),
    "rgb": ta.cvtColor(image, ta.COLOR_GRAY2BGR),
}
assert outputs["gaussian"].shape == image.shape
assert outputs["bilateral"].shape == image.shape
assert outputs["ransac"].shape == flow.shape
assert outputs["gray"].shape == image.shape
assert outputs["rgb"].shape == gray.shape
assert all(np.isfinite(np.asarray(value)).all() for value in outputs.values())
print("JIT_ADAPTER_RESULT ok", flush=True)
sys.stdout.flush()
os._exit(0)
"""


class LegacyExportContractTests(unittest.TestCase):
    """Keep the root export surface importable in both supported modes."""

    def _probe(self, mode: str) -> dict[str, object]:
        env = os.environ.copy()
        env["AOT_MODE"] = str(mode)
        env["TAICHI_ARCH"] = "cpu"
        env["TAICHI_ARCH"] = "cpu"
        env["AOT_ARCH"] = "cpu"
        env["DISABLE_AOT_WATCHDOG"] = "1"
        env["AUTO_DESTROY"] = "1"
        completed = subprocess.run(
            [sys.executable, "-c", _PROBE],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        lines = [
            line.strip()
            for line in completed.stdout.splitlines()
            if line.startswith("EXPORT_RESULT ")
        ]
        self.assertTrue(
            lines,
            "export probe did not emit a result for AOT_MODE="
            f"{mode}:\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        payload = json.loads(lines[-1][len("EXPORT_RESULT ") :])
        self.assertEqual(
            completed.returncode,
            0,
            "legacy export probe failed for AOT_MODE="
            f"{mode}: {payload}\nstderr={completed.stderr}",
        )
        self.assertLessEqual(payload["unique"], payload["count"], payload)
        self.assertGreater(payload["callable_count"], 0, payload)
        self.assertGreater(payload["constant_count"], 0, payload)
        self.assertEqual(
            payload["callable_count"] + payload["constant_count"],
            payload["count"] - len(payload["missing"]),
            payload,
        )
        self.assertEqual(payload["missing"], [], payload)
        self.assertEqual(payload["star_missing"], [], payload)
        self.assertEqual(payload["star_error"], "", payload)
        return payload

    def test_aot_mode_exports(self) -> None:
        self._probe("1")

    def test_jit_mode_exports(self) -> None:
        self._probe("0")

    def test_aot_legacy_adapters(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "1",
                "TAICHI_ARCH": "cpu",
                "AOT_ARCH": "cpu",
                "DISABLE_AOT_WATCHDOG": "1",
                "AUTO_DESTROY": "1",
            }
        )
        completed = subprocess.run(
            [sys.executable, "-c", _ADAPTER_PROBE],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"AOT adapter probe failed:\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertIn("ADAPTER_RESULT ok", completed.stdout)

    def test_jit_legacy_adapters(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "AOT_MODE": "0",
                "TAICHI_ARCH": "cpu",
                "TAICHI_ARCH": "cpu",
                "AOT_ARCH": "cpu",
                "DISABLE_AOT_WATCHDOG": "1",
                "AUTO_DESTROY": "1",
            }
        )
        completed = subprocess.run(
            [sys.executable, "-c", _JIT_ADAPTER_PROBE],
            cwd=str(_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=240,
        )
        self.assertEqual(
            completed.returncode,
            0,
            f"JIT adapter probe failed:\nstdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertIn("JIT_ADAPTER_RESULT ok", completed.stdout)


if __name__ == "__main__":
    unittest.main()
