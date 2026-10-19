"""Ground-truth quality gate for the resident compute_flow AOT graphs.

Run in a fresh project-venv process for each backend and artifact root.
The mask excludes newly exposed pixels; optical flow uses support sampling
offsets (x + dx, y + dy), matching remap_with_flow.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def quality_cases():
    rng = np.random.default_rng(14026)
    texture = cv2.GaussianBlur(rng.random((384, 512), dtype=np.float32), (0, 0), 1.2)
    texture = np.ascontiguousarray((texture - .5) * 2.5 + .5, dtype=np.float32)
    for name, dx, dy, contrast, exposure, noise in (
        ("horizontal", 8., 0., 1., 0., 0.),
        ("vertical", 0., -12., 1., 0., 0.),
        ("diagonal", -12., 8., 1., 0., 0.),
        ("far_motion", 72., -20., 1., 0., 0.),
        ("far_reverse", -72., 20., 1., 0., 0.),
        ("far_low_contrast", 72., -20., .12, 0., 0.),
        ("far_very_low_contrast", 72., -20., .035, 0., 0.),
        ("low_contrast", 8., -4., .12, 0., .0005),
        ("very_low_contrast", 8., -4., .035, 0., .0003),
        ("exposure", -8., 4., 1., .06, .001),
        ("subpixel", 2.5, -1.5, 1., 0., .001),
        ("noisy_motion", -6., 4., 1., 0., .015),
    ):
        ref = (texture - .5) * contrast + .5
        comp = cv2.warpAffine(ref, np.float32([[1, 0, dx], [0, 1, dy]]),
                              (512, 384), flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT_101)
        comp = comp + exposure + rng.normal(0., noise, ref.shape)
        mask = np.zeros(ref.shape, bool)
        margin = max(64, int(max(abs(dx), abs(dy))) + 32)
        mask[64:-64, margin:-margin] = True
        limit = .30 if name == "subpixel" else .10 if name in {"noisy_motion", "very_low_contrast"} else .05
        yield name, np.float32(ref), np.float32(comp), (dx, dy), mask, limit
    mask = np.zeros(ref.shape, bool)
    mask[64:-64, 64:-64] = True
    ref = rng.random((384, 512), dtype=np.float32) * .6 + .2
    comp = cv2.warpAffine(ref, np.float32([[1, 0, 4], [0, 1, -4]]),
                          (512, 384), borderMode=cv2.BORDER_REFLECT_101)
    yield "sharp_texture", ref, comp, (4., -4.), mask, .05
    # Static sky has no newly exposed pixels: require stability at edges too.
    mask = np.ones((384, 512), dtype=bool)
    ref = np.full((384, 512), .55, np.float32) + np.float32(rng.normal(0., .002, (384, 512)))
    comp = np.full_like(ref, .55) + np.float32(rng.normal(0., .002, ref.shape))
    yield "flat_sky_noise", ref, comp, (0., 0.), mask, .1
    ref = np.full((384, 512), .55, np.float32) + np.float32(rng.normal(0., .015, (384, 512)))
    comp = np.full_like(ref, .59) + np.float32(rng.normal(0., .015, ref.shape))
    yield "flat_sky_heavy_noise", ref, comp, (0., 0.), mask, .1
    yy, xx = np.mgrid[:384, :512]
    ref = np.float32(.4 + xx * .0008 + yy * .0002)
    comp = ref + np.float32(.06)
    yield "sky_gradient_exposure", ref, comp, (0., 0.), mask, .1
    for noise in (.002, .015):
        base = np.float32(.4 + xx * .0008 + yy * .0002)
        ref = base + np.float32(rng.normal(0., noise, base.shape))
        comp = base + np.float32(.06) + np.float32(rng.normal(0., noise, base.shape))
        yield f"sky_gradient_noise_{noise}", ref, comp, (0., 0.), mask, .1
    ref = np.float32(.5 + .2 * np.sin(xx * np.pi / 8))
    comp = ref + np.float32(.03)
    yield "ambiguous_stripes", ref, comp, (0., 0.), mask, .1
    ref = texture.copy()
    comp = ref.copy()
    comp[128:192, 192:256] = cv2.warpAffine(
        ref, np.float32([[1, 0, 4], [0, 1, -3]]), (512, 384),
        borderMode=cv2.BORDER_REFLECT_101)[128:192, 192:256]
    mask = np.zeros(ref.shape, bool)
    mask[144:176, 208:240] = True
    yield "local_motion", ref, comp, (4., -3.), mask, .05


def run_flow(ref, comp, *, smooth, radius=32, distance=6):
    from taichi_vision import taichi_aot as aot
    engine = aot.get_engine()
    module = aot.load_tcm("compute_flow")
    buffers = []
    args = {}
    try:
        for prefix, image in (("ref", ref), ("comp", comp)):
            for level in range(3):
                shape = (image.shape[1] // (2 ** level), image.shape[0] // (2 ** level))
                array = cv2.resize(image, shape, interpolation=cv2.INTER_AREA)
                buf = engine.upload(np.ascontiguousarray(array, dtype=np.float32))
                buffers.append(buf)
                args[f"{prefix}_l{level}"] = buf
        for name, level in (("flow_l2", 2), ("flow_l1", 1), ("flow_l1_seed", 1),
                            ("flow_l0_seed", 0), ("flow_l0_raw", 0)):
            shape = (ref.shape[0] // (2 ** level), ref.shape[1] // (2 ** level), 2)
            buf = engine.allocate(shape, dtype=np.float32, is_vector=False)
            buffers.append(buf)
            args[name] = buf
        graph = "align_end_to_end_3layer_adaptive_" + ("smooth" if smooth else "blocky")
        if smooth and aot.aot_graph_available("compute_flow", "align_end_to_end_3layer_adaptive_smooth_wola"):
            graph = "align_end_to_end_3layer_adaptive_smooth_wola"
            buf = engine.allocate((((ref.shape[0] + 15) // 16) * 8,
                                   ((ref.shape[1] + 15) // 16) * 8, 2),
                                  dtype=np.float32, is_vector=False)
            buffers.append(buf)
            args["grid_flow_l0"] = buf
        module.run(graph,
                   **args, tile_h=32, tile_w=32, scale=2., downscale=2,
                   search_dist=distance, max_search_radius=radius)
        engine.sync()
        return args["flow_l0_raw"].to_numpy()
    finally:
        engine.sync()
        for buf in reversed(buffers):
            buf.release()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--radius", type=int, default=32)
    parser.add_argument("--distance", type=int, default=6)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--repeat", type=int, default=1)
    options = parser.parse_args()
    from taichi_vision import taichi_aot as aot
    results = []
    for smooth in (False, True):
        for name, ref, comp, truth, mask, limit in quality_cases():
            previous = None
            repeat_error = 0.
            for _ in range(options.repeat):
                flow = run_flow(ref, comp, smooth=smooth, radius=options.radius,
                                distance=options.distance)
                if previous is not None:
                    repeat_error = max(repeat_error, float(np.max(np.abs(flow - previous))))
                previous = flow
            error = np.linalg.norm(flow[mask] - np.float32(truth), axis=1)
            row = dict(case=name, smooth=smooth, shape=list(ref.shape), dtype=str(ref.dtype),
                       mean_epe=float(error.mean()), p95_epe=float(np.quantile(error, .95)),
                       median_flow=np.median(flow[mask], axis=0).tolist(),
                       max_epe=float(error.max()),
                       finite=bool(np.isfinite(flow).all()), repeat_max_abs=repeat_error,
                       passed=bool(np.isfinite(flow).all() and error.mean() <= limit
                                   and repeat_error <= 1e-5
                                   and ("sky" not in name or error.max() <= .1)))
            results.append(row)
            print(json.dumps(row), flush=True)
    report = dict(backend=aot.backend_info(), radius=options.radius,
                  distance=options.distance, results=results)
    options.report.parent.mkdir(parents=True, exist_ok=True)
    options.report.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    if options.check and not all(row["passed"] for row in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
