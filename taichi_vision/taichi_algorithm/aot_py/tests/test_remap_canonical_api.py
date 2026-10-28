"""Contract tests for the canonical packed-coordinate remap API."""

from __future__ import annotations

import unittest
from unittest import mock

import numpy as np

from taichi_vision.taichi_algorithm import aot_api


class CanonicalRemapApiTests(unittest.TestCase):
    def test_displacement_mode_forwards_coordinates_and_infers_output_size(self):
        src = np.zeros((7, 9, 3), dtype=np.float32)
        flow = np.ones((3, 5, 2), dtype=np.float32)
        with mock.patch.object(aot_api, "_remap_with_flow_impl", return_value="result") as core:
            result = aot_api.remap(
                src, flow, coordinate_mode="displacement_xy", output_size=(7, 9)
            )
        self.assertEqual(result, "result")
        self.assertIs(core.call_args.args[0], src)
        self.assertIs(core.call_args.args[1], flow)
        self.assertEqual(core.call_args.args[2:4], (7, 9))

    def test_absolute_coordinates_share_displacement_core(self):
        src = np.zeros((3, 4), dtype=np.float32)
        yy, xx = np.mgrid[:3, :4].astype(np.float32)
        xy = np.stack((xx + 0.25, yy - 0.5), axis=-1)
        with mock.patch.object(aot_api, "_remap_with_flow_impl", return_value="result") as core:
            result = aot_api.remap(src, xy, coordinate_mode="absolute_xy")
        self.assertEqual(result, "result")
        np.testing.assert_allclose(
            core.call_args.args[1],
            np.broadcast_to(np.asarray((0.25, -0.5), dtype=np.float32), xy.shape),
        )
        self.assertEqual(core.call_args.args[2:4], (3, 4))

    def test_legacy_split_maps_delegate_to_the_same_core(self):
        src = np.zeros((3, 4), dtype=np.float32)
        yy, xx = np.mgrid[:3, :4].astype(np.float32)
        with mock.patch.object(aot_api, "_remap_with_flow_impl", return_value="result") as core:
            result = aot_api.remap(src, xx + 0.25, yy - 0.5)
        self.assertEqual(result, "result")
        np.testing.assert_allclose(
            core.call_args.args[1],
            np.broadcast_to(np.asarray((0.25, -0.5), dtype=np.float32), (3, 4, 2)),
        )
        self.assertEqual(core.call_args.args[2:4], (3, 4))

    def test_legacy_split_map_keywords_remain_compatible(self):
        src = np.zeros((3, 4), dtype=np.float32)
        yy, xx = np.mgrid[:3, :4].astype(np.float32)
        with mock.patch.object(aot_api, "_remap_with_flow_impl", return_value="result") as core:
            result = aot_api.remap(src, map_x=xx + 0.25, map_y=yy - 0.5)
        self.assertEqual(result, "result")
        np.testing.assert_allclose(
            core.call_args.args[1],
            np.broadcast_to(np.asarray((0.25, -0.5), dtype=np.float32), (3, 4, 2)),
        )
        self.assertEqual(core.call_args.args[2:4], (3, 4))

    def test_invalid_coordinate_contract_is_rejected_before_dispatch(self):
        src = np.zeros((2, 3), dtype=np.float32)
        with mock.patch.object(aot_api, "_remap_with_flow_impl") as core:
            with self.assertRaisesRegex(ValueError, "coordinate_mode"):
                aot_api.remap(src, np.zeros((2, 3, 2), np.float32), coordinate_mode="guess")
            with self.assertRaisesRegex(TypeError, "float32"):
                aot_api.remap(
                    src,
                    np.zeros((2, 3, 2), np.float64),
                    coordinate_mode="displacement_xy",
                )
        core.assert_not_called()


if __name__ == "__main__":
    unittest.main()
