"""Isolated CPU-JIT parity check for the UV atlas rasteriser."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


class TextureMappingJitTests(unittest.TestCase):
    def test_cpu_jit_uv_atlas_matches_numpy(self):
        root = Path(__file__).resolve().parents[4]
        script = r'''
import importlib.util
import pathlib
import numpy as np
import taichi as ti

path = pathlib.Path("taichi_vision/taichi_algorithm/sfm/texture_mapping.py")
spec = importlib.util.spec_from_file_location("texture_mapping_standalone", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ti.init(arch=ti.cpu, offline_cache=False)
uv = np.asarray([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
faces = np.asarray([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
y, x = np.indices((7, 9), dtype=np.float32)
texture = np.stack([x / 8.0, y / 6.0, 0.25 * np.ones_like(x)], axis=-1).astype(np.float32)
oracle = module.rasterize_texture_atlas(uv, faces, texture, (9, 11), backend="numpy", return_result=True)
native = module.rasterize_texture_atlas(uv, faces, texture, (9, 11), backend="taichi", return_result=True)
if not np.array_equal(oracle.valid, native.valid):
    raise AssertionError("UV coverage mismatch")
if not np.allclose(oracle.atlas, native.atlas, atol=2.0e-5, rtol=2.0e-5):
    raise AssertionError("UV atlas value mismatch")
print("texture_uv_jit_ok")
'''
        env = os.environ.copy()
        env["AOT_MODE"] = "0"
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
        self.assertIn("texture_uv_jit_ok", completed.stdout)


if __name__ == "__main__":
    unittest.main()
