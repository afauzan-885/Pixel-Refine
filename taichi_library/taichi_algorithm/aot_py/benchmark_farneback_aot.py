"""Benchmark AOT Farneback against OpenCV.

Usage:
    python taichi_library/taichi_algorithm/aot_py/benchmark_farneback_aot.py
"""

import argparse
import os
import sys
import time

import cv2
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def make_textured_image(h, w, seed=42):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = (
        np.sin(xx * 0.05) * np.cos(yy * 0.04) * 80.0
        + np.sin(xx * 0.12 + yy * 0.08) * 40.0
        + np.cos(xx * 0.03 + yy * 0.06) * 60.0
        + rng.normal(0.0, 12.0, size=(h, w)).astype(np.float32)
        + 128.0
    )
    return np.clip(img, 0.0, 255.0).astype(np.float32)


def median_ms(fn, repeats):
    times = []
    result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        result = fn()
        times.append((time.perf_counter() - t0) * 1000.0)
    return float(np.median(times)), result


def epe(a, b):
    diff = a - b
    return float(np.mean(np.sqrt(diff[..., 0] ** 2 + diff[..., 1] ** 2)))


def affine_flow_ground_truth(h, w, matrix):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x2 = matrix[0, 0] * xx + matrix[0, 1] * yy + matrix[0, 2]
    y2 = matrix[1, 0] * xx + matrix[1, 1] * yy + matrix[1, 2]
    return np.stack([x2 - xx, y2 - yy], axis=-1).astype(np.float32)


def central_mask(h, w, border_ratio=0.18):
    by = int(h * border_ratio)
    bx = int(w * border_ratio)
    mask = np.zeros((h, w), dtype=bool)
    mask[by:h - by, bx:w - bx] = True
    return mask


def masked_epe(flow, truth, mask):
    diff = flow - truth
    mag = np.sqrt(diff[..., 0] ** 2 + diff[..., 1] ** 2)
    return float(np.mean(mag[mask]))


def masked_direction_error_deg(flow, truth, mask):
    f = flow[mask]
    t = truth[mask]
    f_norm = np.linalg.norm(f, axis=1)
    t_norm = np.linalg.norm(t, axis=1)
    valid = (f_norm > 1e-4) & (t_norm > 1e-4)
    if not np.any(valid):
        return 0.0
    dots = np.sum(f[valid] * t[valid], axis=1) / (f_norm[valid] * t_norm[valid])
    dots = np.clip(dots, -1.0, 1.0)
    return float(np.degrees(np.mean(np.arccos(dots))))


def affine_matrix(w, h, angle_deg, scale, tx, ty):
    center = (w * 0.5, h * 0.5)
    return cv2.getRotationMatrix2D(center, angle_deg, scale).astype(np.float32) + np.array(
        [[0.0, 0.0, tx], [0.0, 0.0, ty]], dtype=np.float32
    )


def run_affine_scenarios(h, w, repeats):
    from taichi_library import taichi_aot

    scenarios = [
        ("EASY (Mild Handshake)", 0.5, 1.001, 0.5, -0.3),
        ("MEDIUM (Car Bumps / Med Speed)", 2.0, 1.010, 2.5, -1.8),
        ("HARD (Fast Vehicle / High Vibration)", 6.0, 1.035, 8.0, -5.0),
        ("VERY_HARD (Extreme Speed / Low FPS / Camera Shakes)", 15.0, 1.080, 25.0, -18.0),
    ]
    prev = make_textured_image(h, w)
    mask = central_mask(h, w)

    print(f"\n=========================================================================================")
    print(f"HIGH-SPEED FARNEBACK OPTICAL FLOW BENCHMARK ({w}x{h}, repeats={repeats})")
    print(f"=========================================================================================")

    # Warm up once outside the measured scenario loops.
    warm_matrix = affine_matrix(w, h, 1.0, 1.005, 1.0, -1.0)
    warm_next = cv2.warpAffine(prev, warm_matrix, (w, h), borderMode=cv2.BORDER_REFLECT_101)
    taichi_aot.farneback_flow(prev, warm_next, preset="balanced")
    cv2.calcOpticalFlowFarneback(prev, warm_next, None, 0.5, 3, 15, 3, 5, 1.2, 0)

    for name, angle, scale, tx, ty in scenarios:
        matrix = affine_matrix(w, h, angle, scale, tx, ty)
        next_img = cv2.warpAffine(prev, matrix, (w, h), borderMode=cv2.BORDER_REFLECT_101)
        truth = affine_flow_ground_truth(h, w, matrix)

        cv_ms, cv_flow = median_ms(
            lambda: cv2.calcOpticalFlowFarneback(
                prev, next_img, None, 0.5, 3, 15, 3, 5, 1.2, 0
            ),
            repeats,
        )

        print(
            f"\n>>> Scenario: {name}"
            f"\n    rot={angle:+.1f}deg scale={scale:.3f} tx={tx:+.1f} ty={ty:+.1f}"
        )
        print(
            f"    OpenCV {cv_ms:8.2f} ms  "
            f"epe_gt={masked_epe(cv_flow, truth, mask):.4f}  "
            f"dir_err={masked_direction_error_deg(cv_flow, truth, mask):.2f}deg"
        )

        for preset in ("opencv", "balanced", "fast", "robust"):
            aot_ms, flow = median_ms(
                lambda p=preset: taichi_aot.farneback_flow(
                    prev,
                    next_img,
                    pyr_scale=0.5,
                    num_levels=3,
                    win_size=15,
                    num_iters=3,
                    poly_n=5,
                    poly_sigma=1.2,
                    preset=p,
                ),
                repeats,
            )
            if preset == "robust":
                _, diagnostics = taichi_aot.farneback_flow(
                    prev,
                    next_img,
                    pyr_scale=0.5,
                    num_levels=3,
                    win_size=15,
                    num_iters=3,
                    poly_n=5,
                    poly_sigma=1.2,
                    preset=preset,
                    return_diagnostics=True,
                )
                low_conf = diagnostics.get("low_confidence_ratio", 0.0)
            else:
                low_conf = 0.0
            print(
                f"    AOT {preset:<8} {aot_ms:8.2f} ms  "
                f"speedup={cv_ms / max(aot_ms, 1e-9):5.2f}x  "
                f"epe_gt={masked_epe(flow, truth, mask):.4f}  "
                f"dir_err={masked_direction_error_deg(flow, truth, mask):.2f}deg  "
                f"epe_cv={masked_epe(flow, cv_flow, mask):.4f}"
                + (f"  low_conf={low_conf:.3f}" if preset == "robust" else "")
            )


def run_case(h, w, repeats):
    pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", default="512x512,1024x1024")
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    for item in args.sizes.split(","):
        w_text, h_text = item.lower().split("x")
        h = int(h_text)
        w = int(w_text)
        run_affine_scenarios(h, w, args.repeats)


if __name__ == "__main__":
    main()
