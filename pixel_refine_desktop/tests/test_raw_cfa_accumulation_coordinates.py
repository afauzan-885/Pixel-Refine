"""Source-kernel oracle for CFA flow/confidence resize coordinates."""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap


def test_cfa_accumulator_uses_resize_pixel_centers_for_flow_and_weights():
    code = textwrap.dedent(
        r'''
        import numpy as np
        import taichi as ti

        ti.init(arch=ti.cpu)
        from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
            remap_accumulate_cfa_weighted_plane_kernel as kernel,
            remap_accumulate_cfa_scalar_weighted_plane_kernel as scalar_kernel,
        )

        h_dst, w_dst = 12, 16
        h_flow, w_flow = 5, 7
        h_work, w_work = 6, 8
        flow = np.empty((h_flow, w_flow, 2), dtype=np.float32)
        for y in range(h_flow):
            for x in range(w_flow):
                flow[y, x, 0] = np.float32(0.035 * x - 0.02 * y)
                flow[y, x, 1] = np.float32(0.025 * y - 0.015 * x)

        weights = np.empty((h_work, w_work, 3), dtype=np.float32)
        for y in range(h_work):
            for x in range(w_work):
                weights[y, x, :] = np.float32((x + 2 * y) / 18.0)

        def bilinear_clamp(array, x, y, channel=None):
            x = min(max(float(x), 0.0), float(array.shape[1] - 1))
            y = min(max(float(y), 0.0), float(array.shape[0] - 1))
            x0, y0 = int(np.floor(x)), int(np.floor(y))
            x1, y1 = min(x0 + 1, array.shape[1] - 1), min(y0 + 1, array.shape[0] - 1)
            tx, ty = x - x0, y - y0
            if channel is None:
                q00, q01 = array[y0, x0], array[y0, x1]
                q10, q11 = array[y1, x0], array[y1, x1]
            else:
                q00, q01 = array[y0, x0, channel], array[y0, x1, channel]
                q10, q11 = array[y1, x0, channel], array[y1, x1, channel]
            return float((1 - ty) * ((1 - tx) * q00 + tx * q01) + ty * ((1 - tx) * q10 + tx * q11))

        for phase_y in range(2):
            for phase_x in range(2):
                origin_y, origin_x = phase_y, phase_x
                plane_h = len(range(origin_y, h_dst, 2))
                plane_w = len(range(origin_x, w_dst, 2))
                source = np.empty((plane_h, plane_w), dtype=np.float32)
                for y in range(plane_h):
                    for x in range(plane_w):
                        source[y, x] = np.float32((x + 2 * y) / 16.0)
                out_sum = np.zeros((h_dst, w_dst), dtype=np.float32)
                out_weight = np.zeros_like(out_sum)
                channel = phase_y * 2 + phase_x
                kernel(
                    source, flow, weights, out_sum, out_weight,
                    h_dst, w_dst, h_flow, w_flow, h_work, w_work,
                    plane_h, plane_w, origin_y, origin_x, channel % 3,
                    float(w_dst) / w_flow, float(h_dst) / h_flow,
                )

                expected_sum = np.zeros_like(out_sum)
                expected_weight = np.zeros_like(out_weight)
                for py in range(origin_y, h_dst, 2):
                    for px in range(origin_x, w_dst, 2):
                        fx = min(max((px + 0.5) * w_flow / w_dst - 0.5, 0.0), w_flow - 1.0)
                        fy = min(max((py + 0.5) * h_flow / h_dst - 0.5, 0.0), h_flow - 1.0)
                        dx = bilinear_clamp(flow, fx, fy, 0)
                        dy = bilinear_clamp(flow, fx, fy, 1)
                        sx = (px - origin_x) / 2 + dx * (w_dst / w_flow) * 0.5
                        sy = (py - origin_y) / 2 + dy * (h_dst / h_flow) * 0.5
                        if 0.0 <= sx <= plane_w - 1 and 0.0 <= sy <= plane_h - 1:
                            value = bilinear_clamp(source, sx, sy)
                            wx = min(max((px + 0.5) * w_work / w_dst - 0.5, 0.0), w_work - 1.0)
                            wy = min(max((py + 0.5) * h_work / h_dst - 0.5, 0.0), h_work - 1.0)
                            weight = min(max(bilinear_clamp(weights, wx, wy, channel % 3), 0.0), 1.0)
                            expected_sum[py, px] = value * weight
                            expected_weight[py, px] = weight

                np.testing.assert_allclose(out_weight, expected_weight, rtol=0, atol=2e-7)
                np.testing.assert_allclose(out_sum, expected_sum, rtol=0, atol=2e-7)

                scalar_sum = np.zeros((h_dst, w_dst), dtype=np.float32)
                scalar_weight = np.zeros_like(scalar_sum)
                scalar_kernel(
                    source, flow, np.ascontiguousarray(weights[..., 0]), scalar_sum, scalar_weight,
                    h_dst, w_dst, h_flow, w_flow, h_work, w_work,
                    plane_h, plane_w, origin_y, origin_x,
                    float(w_dst) / w_flow, float(h_dst) / h_flow,
                )
                np.testing.assert_allclose(scalar_weight, expected_weight, rtol=0, atol=2e-7)
                np.testing.assert_allclose(scalar_sum, expected_sum, rtol=0, atol=2e-7)
        print("source-kernel CFA coordinate oracle passed")
        '''
    )
    env = os.environ.copy()
    env["AOT_MODE"] = "0"
    env.pop("TI_ARCH", None)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "source-kernel CFA coordinate oracle passed" in result.stdout
