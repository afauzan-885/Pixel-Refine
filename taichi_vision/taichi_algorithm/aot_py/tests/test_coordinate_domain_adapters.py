"""Semantic CPU parity gates for shape/coordinate-domain block adapters.

These tests intentionally do not initialize a native backend.  They prove the
coordinate mapping and deterministic output merge only; native qualification
still requires the target-specific resize/graph probe and is kept fail-closed.
"""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    COORDINATE_DOMAIN_ADAPTER_OPERATIONS,
    register_coordinate_domain_adapters,
    verify_coordinate_parity,
)


class CoordinateDomainAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_coordinate_domain_adapters()

    def test_registration_and_gates_remain_fail_closed(self):
        self.assertEqual(
            set(COORDINATE_DOMAIN_ADAPTER_OPERATIONS),
            {"resize", "image_pyramid", "warp_affine_aot", "copy_make_border_aot"},
        )
        for operation in COORDINATE_DOMAIN_ADAPTER_OPERATIONS:
            with self.subTest(operation=operation):
                adapter = registered_block_adapters()[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertTrue(adapter.metadata["coordinate_domain"])
                self.assertTrue(adapter.metadata["semantic_only"])
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_resize_linear_cubic_area_non_multiple_rgb(self):
        rng = np.random.default_rng(20260810)
        source = rng.random((23, 31, 3), dtype=np.float32)
        for interpolation in ("linear", "cubic", "area"):
            with self.subTest(interpolation=interpolation):
                report = verify_coordinate_parity(
                    "resize",
                    (source,),
                    params={"dsize": (19, 17), "interpolation": interpolation},
                    block_size=(7, 9),
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertTrue(report["dtype_match"], report)
                self.assertEqual(report["full_dtype"], ["float32"])
                self.assertEqual(report["tiled_dtype"], ["float32"])
                self.assertFalse(report["native_runtime"])

    def test_image_pyramid_multistage_and_shape_edges(self):
        source = np.arange(31 * 37, dtype=np.float32).reshape(31, 37)
        report = verify_coordinate_parity(
            "image_pyramid",
            (source,),
            params={"levels": 3},
            block_size=(7, 11),
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["full_shape"], [[3, 4]])
        self.assertEqual(report["max_abs_error"], 0.0)

    def test_affine_reflect101_and_border_modes(self):
        source = np.arange(17 * 19, dtype=np.float32).reshape(17, 19)
        matrix = np.asarray([[0.98, 0.08, 1.3], [-0.04, 1.02, -2.1]], dtype=np.float32)
        affine = verify_coordinate_parity(
            "warp_affine_aot",
            (source,),
            params={"dsize": (23, 13), "matrix": matrix},
            block_size=(5, 8),
        )
        self.assertTrue(affine["passed"], affine)
        self.assertEqual(affine["max_abs_error"], 0.0)
        self.assertTrue(affine["dtype_match"], affine)
        self.assertEqual(affine["full_dtype"], ["float32"])
        self.assertEqual(affine["tiled_dtype"], ["float32"])

        for mode in ("CONSTANT", "REPLICATE", "REFLECT", "WRAP", "REFLECT_101"):
            with self.subTest(mode=mode):
                report = verify_coordinate_parity(
                    "copy_make_border_aot",
                    (source,),
                    params={
                        "top": 4,
                        "bottom": 3,
                        "left": 5,
                        "right": 2,
                        "border_type": mode,
                        "value": 7.0,
                    },
                    block_size=(6, 7),
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertTrue(report["dtype_match"], report)
                self.assertEqual(report["full_dtype"], ["float32"])
                self.assertEqual(report["tiled_dtype"], ["float32"])


if __name__ == "__main__":
    unittest.main()
