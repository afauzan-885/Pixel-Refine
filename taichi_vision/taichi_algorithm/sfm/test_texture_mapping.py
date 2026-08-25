"""UV atlas oracle and explicit Taichi-JIT parity tests."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

import numpy as np

from .texture_mapping import rasterize_texture_atlas


class TextureMappingTests(unittest.TestCase):
    def setUp(self):
        self.uv = np.asarray([[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]], dtype=np.float32)
        self.faces = np.asarray([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        y, x = np.indices((7, 9), dtype=np.float32)
        self.texture = np.stack([x / 8.0, y / 6.0, 0.25 * np.ones_like(x)], axis=-1).astype(np.float32)

    def test_numpy_reference_has_coverage_and_bounds(self):
        result = rasterize_texture_atlas(self.uv, self.faces, self.texture, (9, 11), return_result=True)
        self.assertEqual(result.atlas.shape, (9, 11, 3))
        self.assertGreater(int(np.count_nonzero(result.valid)), 0)
        self.assertTrue(np.isfinite(result.atlas).all())
        self.assertTrue(((result.atlas >= 0.0) & (result.atlas <= 1.0)).all())

    def test_aot_backend_composes_remap_or_fails_closed(self):
        try:
            native = rasterize_texture_atlas(
                self.uv,
                self.faces,
                self.texture,
                (9, 11),
                backend="aot",
                return_result=True,
            )
        except NotImplementedError as exc:
            self.assertIn("remap", str(exc))
        else:
            oracle = rasterize_texture_atlas(
                self.uv,
                self.faces,
                self.texture,
                (9, 11),
                backend="numpy",
                return_result=True,
            )
            self.assertEqual(native.backend, "aot")
            np.testing.assert_array_equal(native.valid, oracle.valid)
            np.testing.assert_allclose(native.atlas, oracle.atlas, atol=2.0e-5, rtol=2.0e-5)

    def test_aot_rejects_singleton_channel_before_vec3_remap(self):
        singleton = np.ones((8, 9, 1), dtype=np.float32)
        with self.assertRaises(NotImplementedError):
            rasterize_texture_atlas(
                self.uv,
                self.faces,
                singleton,
                (9, 11),
                backend="aot",
            )

    def test_aot_composition_sends_barycentric_map_to_remap_leaf(self):
        """UV geometry is host-side; interpolation remains the AOT leaf."""

        captured = {}

        def fake_remap(src, map_x, map_y, **kwargs):
            captured["src"] = src
            captured["map_x"] = map_x
            captured["map_y"] = map_y
            captured["kwargs"] = kwargs
            return np.zeros((*map_x.shape, src.shape[2]), dtype=np.float32)

        with patch("taichi_vision.taichi_algorithm.aot_api.remap", fake_remap):
            result = rasterize_texture_atlas(
                self.uv,
                self.faces,
                self.texture,
                (9, 11),
                backend="aot",
                return_result=True,
            )

        self.assertEqual(result.backend, "aot")
        self.assertEqual(captured["map_x"].shape, result.valid.shape)
        self.assertEqual(captured["map_y"].shape, result.valid.shape)
        self.assertTrue(np.isfinite(captured["map_x"]).all())
        self.assertTrue(np.isfinite(captured["map_y"]).all())
        self.assertTrue((captured["map_x"] >= 0.0).all())
        self.assertTrue((captured["map_x"] <= self.texture.shape[1] - 1).all())
        self.assertTrue((captured["map_y"] >= 0.0).all())
        self.assertTrue((captured["map_y"] <= self.texture.shape[0] - 1).all())
        self.assertEqual(captured["kwargs"], {})

    @unittest.skipUnless(os.environ.get("TEXTURE_MAPPING_JIT") == "1", "run with TEXTURE_MAPPING_JIT=1")
    def test_taichi_jit_matches_numpy(self):
        import taichi as ti

        runtime = ti.lang.impl.get_runtime()
        if getattr(runtime, "prog", None) is None:
            ti.init(arch=ti.cpu, offline_cache=False)
        oracle = rasterize_texture_atlas(self.uv, self.faces, self.texture, (9, 11), backend="numpy", return_result=True)
        native = rasterize_texture_atlas(self.uv, self.faces, self.texture, (9, 11), backend="taichi", return_result=True)
        np.testing.assert_array_equal(native.valid, oracle.valid)
        np.testing.assert_allclose(native.atlas, oracle.atlas, atol=2.0e-5, rtol=2.0e-5)


if __name__ == "__main__":
    unittest.main()
