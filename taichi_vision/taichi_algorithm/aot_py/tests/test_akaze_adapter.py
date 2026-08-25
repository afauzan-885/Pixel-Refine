"""Semantic CPU parity gates for the bounded AKAZE keypoint stage.

The adapter covers only the single-scale Hessian map and deterministic grid
NMS.  FED diffusion, descriptors, matching, and all native graphics backends
remain on the maintained full-frame path until independent evidence exists.
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
    AKAZE_ADAPTER_OPERATIONS,
    register_akaze_block_adapters,
    run_akaze_keypoints_partition_tiled,
    verify_akaze_keypoint_parity,
)


class AkazeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_akaze_block_adapters()

    @staticmethod
    def _image() -> np.ndarray:
        rows, cols = np.indices((37, 53), dtype=np.float32)
        image = (
            np.float32(0.05) * rows
            + np.float32(0.03) * cols
            + np.sin(rows * np.float32(0.41))
            + np.cos(cols * np.float32(0.27))
        )
        # Smooth isolated extrema keep the Hessian response well above a tiny
        # threshold without relying on dimensions divisible by the grid size.
        for row, col, amplitude, radius in (
            (8, 9, 3.0, 2.5),
            (17, 27, -2.0, 3.0),
            (29, 43, 2.5, 2.0),
        ):
            distance = ((rows - row) ** 2 + (cols - col) ** 2) / np.float32(
                radius * radius
            )
            image += np.float32(amplitude) * np.exp(-distance)
        return np.ascontiguousarray(image, dtype=np.float32)

    def test_registration_is_multistage_and_native_fail_closed(self):
        self.assertEqual(set(AKAZE_ADAPTER_OPERATIONS), {"akaze"})
        adapter = registered_block_adapters()["akaze"]
        self.assertTrue(adapter.partition_ready)
        self.assertEqual(adapter.partition_strategy.value, "multi_stage")
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["keypoint_stage"])
        self.assertFalse(adapter.metadata["descriptor_stage"])
        self.assertTrue(adapter.metadata["output_domain"])
        self.assertEqual(adapter.metadata["guard_halo"], 1)
        self.assertTrue(can_partition_block("akaze", "cpu"))
        self.assertFalse(can_auto_block("akaze", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("akaze", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("akaze", "vulkan"))

    def test_guard_band_nms_parity_non_multiple_dimensions(self):
        image = self._image()
        params = {
            "grid_size": 8,
            "threshold": 1.0e-5,
            "margin": 15,
            "max_keypoints": 1500,
        }
        for block_size in ((7, 11), (5, 13), 9):
            with self.subTest(block_size=block_size):
                report = verify_akaze_keypoint_parity(
                    (image,), block_size=block_size, params=params
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertEqual(report["input_shape"], [37, 53])
                self.assertEqual(report["coordinate_order"], "row_col")
                self.assertEqual(report["guard_halo"], 1)
                self.assertFalse(report["native_runtime"])
                self.assertGreaterEqual(report["output_shape"][1], 2)

        first = run_akaze_keypoints_partition_tiled(
            (image,), block_size=(7, 11), params=params
        )
        second = run_akaze_keypoints_partition_tiled(
            (image,), block_size=(5, 13), params=params
        )
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first.dtype, np.float32)
        self.assertTrue(np.isfinite(first).all())

    def test_invalid_inputs_and_full_akaze_pair_fail_closed(self):
        image = self._image()
        with self.assertRaises(ValueError):
            run_akaze_keypoints_partition_tiled(
                (image, image), block_size=7
            )
        with self.assertRaises(TypeError):
            run_akaze_keypoints_partition_tiled(
                (image.reshape(-1),), block_size=7
            )
        invalid = image.copy()
        invalid[0, 0] = np.nan
        with self.assertRaises(ValueError):
            run_akaze_keypoints_partition_tiled((invalid,), block_size=7)
        with self.assertRaises(ValueError):
            run_akaze_keypoints_partition_tiled((image,), block_size=5000)
        for key, value in (
            ("grid_size", 0),
            ("threshold", float("nan")),
            ("margin", -1),
            ("max_keypoints", 0),
        ):
            with self.subTest(parameter=key), self.assertRaises(ValueError):
                run_akaze_keypoints_partition_tiled(
                    (image,), block_size=7, params={key: value}
                )


if __name__ == "__main__":
    unittest.main()
