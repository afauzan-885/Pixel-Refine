"""Evaluasi sintetis multi-seed; jalankan dengan Python venv dari root proyek."""
from __future__ import annotations

import argparse
import json
import platform
import time
from pathlib import Path

import cv2
import numpy as np

from taichi_vision.taichi_algorithm.alignment.quality import project_points, ransac_transform

DISTRIBUTIONS = ("uniform", "center_cluster", "upper_left_cluster", "two_clusters", "thin_strip")


def make_case(distribution, noise, seed, model, *, outliers=0.2):
    rng = np.random.default_rng(seed)
    n = 96
    if distribution == "uniform":
        source = rng.uniform([0, 0], [512, 384], (n, 2))
    elif distribution == "center_cluster":
        source = rng.normal([256, 192], [34, 26], (n, 2))
    elif distribution == "upper_left_cluster":
        source = rng.normal([65, 55], [24, 20], (n, 2))
    elif distribution == "two_clusters":
        source = rng.normal(np.tile([[95, 80], [410, 300]], (n // 2, 1)), [24, 20])
    else:
        source = np.column_stack((rng.uniform(15, 497, n), rng.normal(190, 1.25, n)))
    truth = np.array([[1.015, -0.065, 13.5], [0.045, 0.985, -9.25], [0, 0, 1.]], dtype=np.float64)
    if model == "homography":
        truth[2, :2] = [1.2e-4, -8.0e-5]
    target = project_points(source, truth) + rng.normal(0, noise, (n, 2))
    clean = np.ones(n, dtype=bool)
    bad = rng.choice(n, int(n * outliers), replace=False)
    clean[bad] = False
    target[bad] = rng.uniform([-50, -50], [562, 434], (len(bad), 2))
    validation = rng.uniform([0, 0], [512, 384], (2048, 2))
    return source, target, truth, clean, validation


def warp_parity_diagnostic():
    """Same-matrix comparison with both matched and mismatched borders."""
    from taichi_vision import taichi_aot as aot
    from taichi_vision.taichi_algorithm import warp_affine

    image = np.random.default_rng(43).random((127, 159, 3), dtype=np.float32)
    report = []
    for model in ("affine", "homography"):
        matrix = np.array([[1.015, -.065, 13.5], [.045, .985, -9.25], [0, 0, 1.]])
        if model == "homography":
            matrix[2, :2] = [1.2e-4, -8.e-5]
        for channels in (1, 3):
            source = image[:, :, 0].copy() if channels == 1 else image
            if model == "affine":
                actual = warp_affine(source, matrix[:2], (159, 127))
                reference = lambda border: cv2.warpAffine(source, matrix[:2], (159, 127), flags=cv2.INTER_LINEAR, borderMode=border)
            else:
                uploaded = aot.upload(source)
                try:
                    actual = aot.warp_perspective(uploaded, matrix, (159, 127), return_gpu=False)
                finally:
                    uploaded.release()
                reference = lambda border: cv2.warpPerspective(source, matrix, (159, 127), flags=cv2.INTER_LINEAR, borderMode=border)
            matched = reference(cv2.BORDER_REFLECT_101)
            constant = reference(cv2.BORDER_CONSTANT)
            report.append({"model": model, "shape": list(source.shape), "dtype": str(source.dtype),
                           "reflect101_mae": float(np.abs(actual - matched).mean()),
                           "reflect101_max": float(np.abs(actual - matched).max()),
                           "constant_mae": float(np.abs(actual - constant).mean())})
    return {"backend": aot.backend_info(), "cases": report}


def run(output, seeds):
    from taichi_vision import taichi_aot as aot

    report = {"environment": {"python": platform.python_version(), "numpy": np.__version__,
                               "opencv": cv2.__version__, "backend": aot.backend_info()},
              "configuration": {"seeds": seeds, "noise_px": [.25, .75, 2.], "n": 96,
                                "outlier_fraction": .2, "threshold_px": 3., "validation_n": 2048},
              "cases": []}
    for model in ("affine", "homography"):
        for distribution in DISTRIBUTIONS:
            for noise in (.25, .75, 2.):
                for seed in seeds:
                    source, target, truth, clean, validation = make_case(distribution, noise, seed, model)
                    row = dict(model=model, distribution=distribution, noise=noise, seed=seed)
                    for name in ("taichi", "opencv"):
                        start = time.perf_counter()
                        cv2.setRNGSeed(seed)
                        if name == "opencv":
                            if model == "affine":
                                h, mask = cv2.estimateAffine2D(source, target, method=cv2.RANSAC,
                                    ransacReprojThreshold=3., maxIters=512, confidence=.99, refineIters=10)
                                if h is not None:
                                    h = np.vstack((h, [0, 0, 1]))
                            else:
                                h, mask = cv2.findHomography(source, target, cv2.RANSAC, 3., maxIters=1024)
                        elif model == "affine":
                            h, mask, _ = ransac_transform(source, target, model=model, iterations=512, seed=seed)
                        else:
                            h, mask = aot.find_homography(source, target, method="RANSAC", n_hypotheses=1024, seed=seed)
                        elapsed = (time.perf_counter() - start) * 1000
                        if h is None:
                            row[name] = {"failed": True, "ms": elapsed}
                            continue
                        errors = np.linalg.norm(project_points(validation, h) - project_points(validation, truth), axis=1)
                        selected = np.asarray(mask).reshape(-1).astype(bool)
                        row[name] = {"failed": False, "p95_px": float(np.percentile(errors, 95)),
                                     "median_px": float(np.median(errors)), "ms": elapsed,
                                     "precision": float(clean[selected].mean()) if selected.any() else 0.,
                                     "recall": float(selected[clean].mean())}
                    report["cases"].append(row)
            print(model, distribution, flush=True)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    for model in ("affine", "homography"):
        for name in ("taichi", "opencv"):
            values = [r[name]["p95_px"] for r in report["cases"] if r["model"] == model and not r[name]["failed"]]
            print(model, name, "median-p95", np.median(values), "worst", max(values), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[173, 947, 2027, 8191, 23003])
    parser.add_argument("--warp-only", action="store_true", help="Diagnosis border dengan matriks identik")
    args = parser.parse_args()
    if args.warp_only:
        result = warp_parity_diagnostic()
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
    else:
        run(args.output, args.seeds)
