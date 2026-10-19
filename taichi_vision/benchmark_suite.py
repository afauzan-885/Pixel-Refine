"""Comprehensive Benchmark and Validation Suite for SFM, Alignment, Panorama (6MP), and NeRF.

Generates realistic synthetic scenes with known ground truth, runs 3 iterations,
and reports accuracy, latency (mean & min), and memory consumption (RAM and VRAM).
"""

from __future__ import annotations

import gc
import os
import sys
import time
from typing import Any, Dict

import numpy as np
import psutil

# Ensure Eel-Dance is in path so taichi_vision resolves
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from taichi_vision.taichi_algorithm.sfm.triangulation import triangulate_adaptive
from taichi_vision.taichi_algorithm.sfm.cheirality_check import check_cheirality_full, check_cheirality_minimal
from taichi_vision.taichi_algorithm.sfm.bundle_adjustment import bundle_adjust_lm
from taichi_vision.taichi_algorithm.sfm.plane_sweep import plane_sweep_stereo
from taichi_vision.taichi_algorithm.alignment.phase_correlation import phase_correlation
from taichi_vision.taichi_algorithm.alignment.ncc import zncc
from taichi_vision.taichi_algorithm.alignment.apap import (
    fit_apap,
    APAPWarp,
    fit_aanap,
    AANAPWarp,
)
from taichi_vision.taichi_algorithm.alignment.tps import fit_tps_checked, TPSWarp
from taichi_vision.taichi_algorithm.panorama.seam import dynamic_programming_seam
from taichi_vision.taichi_algorithm.panorama.projection import cylindrical_projection, spherical_projection
from taichi_vision.taichi_algorithm.panorama.exposure import compensate_exposure
from taichi_vision.taichi_algorithm.panorama.stitch import stitch_panorama, sparse_to_dense_warp
from taichi_vision.taichi_algorithm.nerf import (
    NeRFConfig,
    NeRFScene,
    render_nerf_view,
    generate_rays,
    stratified_sampling,
    MultiResHashGrid,
    HarmonicPositionalEncoding,
    render_volume,
)


def get_mem_mb() -> float:
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def get_vram_status() -> dict:
    try:
        from taichi_vision.taichi_aot import engine
        status = engine.get_memory_status()
        return {
            "device_heap_usage_mb": status.get("device_heap_usage", 0) / (1024 * 1024),
            "resident_mb": status.get("resident_bytes", 0) / (1024 * 1024),
        }
    except Exception:
        return {"device_heap_usage_mb": 0.0, "resident_mb": 0.0}


def run_benchmark_3x(fn, *args, **kwargs) -> tuple[Any, list[float], float]:
    """Runs a function for 3 iterations, measures latency and peak RAM."""
    gc.collect()
    latencies = []
    mem_before = get_mem_mb()
    mem_peak = mem_before
    res = None

    for _ in range(3):
        t0 = time.perf_counter()
        res = fn(*args, **kwargs)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)
        curr_mem = get_mem_mb()
        if curr_mem > mem_peak:
            mem_peak = curr_mem

    ram_delta_mb = max(0.0, mem_peak - mem_before)
    return res, latencies, ram_delta_mb


# ==============================================================================
# 1. SFM BENCHMARKS
# ==============================================================================
def generate_synthetic_sfm_scene(n_points: int = 100, seed: int = 42):
    rng = np.random.default_rng(seed)
    pts3d = np.zeros((n_points, 3), dtype=np.float64)
    pts3d[:, 0] = rng.uniform(-1.5, 1.5, n_points)
    pts3d[:, 1] = rng.uniform(-1.0, 1.0, n_points)
    pts3d[:, 2] = rng.uniform(3.0, 7.0, n_points)

    K1 = np.array([[800.0, 0.0, 400.0], [0.0, 800.0, 300.0], [0.0, 0.0, 1.0]], dtype=np.float64)
    K2 = K1.copy()

    yaw = np.radians(6.0)
    pitch = np.radians(-2.0)
    Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)], [0, 1, 0], [-np.sin(yaw), 0, np.cos(yaw)]])
    Rx = np.array([[1, 0, 0], [0, np.cos(pitch), -np.sin(pitch)], [0, np.sin(pitch), np.cos(pitch)]])
    R_gt = Rx @ Ry
    t_gt = np.array([0.4, 0.05, 0.02], dtype=np.float64)

    P1 = K1 @ np.hstack([np.eye(3), np.zeros((3, 1))])
    P2 = K2 @ np.hstack([R_gt, t_gt[:, None]])

    pts1_h = (np.hstack([pts3d, np.ones((n_points, 1))]) @ P1.T)
    pts1_2d = pts1_h[:, :2] / pts1_h[:, 2:3]

    pts2_h = (np.hstack([pts3d, np.ones((n_points, 1))]) @ P2.T)
    pts2_2d = pts2_h[:, :2] / pts2_h[:, 2:3]

    pts1_2d_noisy = pts1_2d + rng.normal(0, 0.2, pts1_2d.shape)
    pts2_2d_noisy = pts2_2d + rng.normal(0, 0.2, pts2_2d.shape)

    return {
        "pts3d_gt": pts3d,
        "P1": P1, "P2": P2,
        "K1": K1, "K2": K2,
        "R_gt": R_gt, "t_gt": t_gt,
        "pts1_2d": pts1_2d_noisy,
        "pts2_2d": pts2_2d_noisy,
    }


def benchmark_sfm():
    scene = generate_synthetic_sfm_scene(n_points=50)
    results = {}

    # A) Triangulation
    print("  -> Triangulation...", flush=True)
    def run_triangulation():
        pts_3d_est, _, _ = triangulate_adaptive(
            scene["pts1_2d"], scene["pts2_2d"],
            scene["P1"], scene["P2"],
            scene["K1"], scene["K2"]
        )
        return pts_3d_est

    pts_est, times, ram_mb = run_benchmark_3x(run_triangulation)
    rmse_3d = np.sqrt(np.mean((pts_est - scene["pts3d_gt"]) ** 2))
    results["triangulation"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": float(rmse_3d),
        "error_unit": "units 3D RMSE",
    }

    # B) Cheirality Check
    print("  -> Cheirality...", flush=True)
    def run_cheirality():
        count, mask = check_cheirality_full(
            scene["R_gt"], scene["t_gt"],
            scene["K1"], scene["K2"],
            scene["pts1_2d"], scene["pts2_2d"]
        )
        return count, mask

    (count, mask), times, ram_mb = run_benchmark_3x(run_cheirality)
    inlier_ratio = count / len(scene["pts1_2d"])
    results["cheirality"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "accuracy": float(inlier_ratio * 100.0),
        "accuracy_unit": "% valid cheirality",
    }

    # C) Bundle Adjustment
    print("  -> Bundle Adjustment...", flush=True)
    n_pts = len(scene["pts3d_gt"])
    tr = np.trace(scene["R_gt"])
    angle_gt = np.arccos(np.clip((tr - 1.0) / 2.0, -1.0, 1.0))
    axis_vec = np.array([
        scene["R_gt"][2, 1] - scene["R_gt"][1, 2],
        scene["R_gt"][0, 2] - scene["R_gt"][2, 0],
        scene["R_gt"][1, 0] - scene["R_gt"][0, 1]
    ])
    axis_norm = np.linalg.norm(axis_vec)
    axis_unit = axis_vec / max(axis_norm, 1e-10)

    cam_init = np.zeros((2, 11), dtype=np.float32)
    cam_init[0, :3] = [0.0, 1.0, 0.0]
    cam_init[0, 3] = 0.0
    cam_init[0, 7:] = [800.0, 800.0, 400.0, 300.0]

    cam_init[1, :3] = axis_unit
    cam_init[1, 3] = float(angle_gt) + 0.005
    cam_init[1, 4:7] = scene["t_gt"] + np.array([0.005, -0.002, 0.002])
    cam_init[1, 7:] = [800.0, 800.0, 400.0, 300.0]

    obs = np.vstack([
        np.column_stack([np.zeros(n_pts, dtype=np.int32), np.arange(n_pts, dtype=np.int32)]),
        np.column_stack([np.ones(n_pts, dtype=np.int32), np.arange(n_pts, dtype=np.int32)])
    ])
    obs_2d = np.vstack([scene["pts1_2d"], scene["pts2_2d"]]).astype(np.float32)
    pts3d_perturbed = scene["pts3d_gt"].astype(np.float32) + np.random.normal(0, 0.05, scene["pts3d_gt"].shape).astype(np.float32)

    def run_ba():
        c_opt, p_opt, cost, n_it = bundle_adjust_lm(
            cam_init.copy(), pts3d_perturbed.copy(), obs, obs_2d,
            max_iterations=3, fx=800.0, fy=800.0, cx=400.0, cy=300.0
        )
        return cost, n_it

    (final_cost, n_it), times, ram_mb = run_benchmark_3x(run_ba)
    results["bundle_adjustment"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": float(final_cost),
        "error_unit": "px reprojection RMSE",
    }

    # D) Plane Sweep Stereo
    print("  -> Plane Sweep...", flush=True)
    h, w = 24, 24
    yy, xx = np.indices((h, w), dtype=np.float32)
    ref_img = (np.sin(xx * 0.1) * np.cos(yy * 0.1) * 0.5 + 0.5).astype(np.float32)
    tgt_img = np.roll(ref_img, shift=2, axis=1)

    def run_plane_sweep():
        d_map, conf = plane_sweep_stereo(
            ref_img, tgt_img,
            scene["K1"][:3, :3].astype(np.float32), scene["K2"][:3, :3].astype(np.float32),
            scene["R_gt"].astype(np.float32), scene["t_gt"].astype(np.float32),
            depth_min=1.0, depth_max=10.0, n_depths=3, patch_radius=1, backend="numpy"
        )
        return d_map, conf

    (d_map, conf), times, ram_mb = run_benchmark_3x(run_plane_sweep)
    results["plane_sweep"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "mean_depth": float(np.mean(d_map)),
        "mean_conf": float(np.mean(conf)),
    }

    return results


# ==============================================================================
# 2. ALIGNMENT BENCHMARKS (APAP, AANAP, Multi-Row, Phase Correlation, TPS)
# ==============================================================================
def benchmark_alignment():
    results = {}

    # A) Phase Correlation (Known Shift)
    print("  -> Phase Correlation...", flush=True)
    h, w = 256, 256
    yy, xx = np.indices((h, w), dtype=np.float32)
    ref = (np.sin(xx * 0.08) * np.cos(yy * 0.08) + 0.5 * np.sin(xx * 0.2)).astype(np.float32)
    shift_x, shift_y = 7.0, -4.0
    comp = np.roll(np.roll(ref, int(shift_y), axis=0), int(shift_x), axis=1)

    def run_phase_corr():
        dx, dy, resp = phase_correlation(ref, comp)
        return dx, dy, resp

    (dx, dy, resp), times, ram_mb = run_benchmark_3x(run_phase_corr)
    shift_err = abs(dx - shift_x) + abs(dy - shift_y)
    results["phase_correlation"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": float(shift_err),
        "error_unit": "px shift error",
    }

    # B) APAP Local Homography Evaluation
    print("  -> APAP Local Homography...", flush=True)
    src_pts = np.array([
        [x, y] for y in np.linspace(20, 200, 4) for x in np.linspace(20, 200, 4)
    ], dtype=np.float64)
    H_true = np.array([[1.02, 0.01, 5.0], [-0.01, 0.98, -3.0], [0.0001, 0.0, 1.0]], dtype=np.float64)
    dst_h = np.hstack([src_pts, np.ones((len(src_pts), 1))]) @ H_true.T
    dst_pts = dst_h[:, :2] / dst_h[:, 2:3]

    apap_warp = fit_apap(src_pts, dst_pts, grid_shape=(4, 4))
    query_pts = np.array([
        [x, y] for y in np.linspace(0, 220, 100) for x in np.linspace(0, 220, 100)
    ], dtype=np.float64) # 10,000 query points

    def run_apap():
        return apap_warp.map_points(query_pts)

    mapped_pts, times, ram_mb = run_benchmark_3x(run_apap)
    expected_h = np.hstack([query_pts, np.ones((len(query_pts), 1))]) @ H_true.T
    expected_pts = expected_h[:, :2] / expected_h[:, 2:3]
    apap_mae = float(np.mean(np.abs(mapped_pts - expected_pts)))
    results["apap_eval"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": apap_mae,
        "error_unit": "px MAE on 10k query pts",
    }

    # C) AANAP (Adaptive As-Natural-As-Possible Warp)
    print("  -> AANAP Local-Global Warp...", flush=True)
    aanap_warp = fit_aanap(src_pts, dst_pts, grid_shape=(4, 4))

    def run_aanap():
        return aanap_warp.map_points(query_pts)

    mapped_aanap, times, ram_mb = run_benchmark_3x(run_aanap)
    aanap_mae = float(np.mean(np.abs(mapped_aanap - expected_pts)))
    results["aanap_eval"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": aanap_mae,
        "error_unit": "px MAE on 10k query pts",
    }

    # D) APAP Parallax Precision Evaluation
    print("  -> APAP Parallax Precision...", flush=True)
    grid_p = np.array([[x, y] for y in np.linspace(20, 200, 4) for x in np.linspace(20, 200, 4)], dtype=np.float64)
    c_p = np.array([[80.0, 100.0], [120.0, 100.0], [100.0, 80.0], [100.0, 120.0]], dtype=np.float64)
    all_s = np.vstack([grid_p, c_p])
    all_d = np.vstack([grid_p + np.array([5.0, 2.0]), c_p + np.array([12.0, 8.0])])

    apap_para_warp = fit_apap(all_s, all_d, grid_shape=(4, 4))

    def run_apap_parallax():
        return apap_para_warp.map_points(all_s)

    mapped_para, times, ram_mb = run_benchmark_3x(run_apap_parallax)
    para_mae = float(np.mean(np.abs(mapped_para - all_d)))
    results["apap_parallax_eval"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": para_mae,
        "error_unit": "px MAE on parallax control points",
    }

    # E) TPS Evaluation
    print("  -> Thin Plate Spline (TPS)...", flush=True)
    tps_warp, _ = fit_tps_checked(src_pts, dst_pts)
    def run_tps():
        return tps_warp.map_points(query_pts)

    mapped_tps, times, ram_mb = run_benchmark_3x(run_tps)
    tps_mae = float(np.mean(np.abs(mapped_tps - expected_pts)))
    results["tps_eval"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": tps_mae,
        "error_unit": "px MAE on 10k query pts",
    }

    return results


# ==============================================================================
# 3. PANORAMA 6MP BENCHMARKS (3000 x 2000 = 6,000,000 Pixels)
# ==============================================================================
def benchmark_panorama():
    results = {}
    h, w = 2000, 3000 # 6 Megapixels (6MP)
    yy, xx = np.indices((h, w), dtype=np.float32)

    # A) Dynamic Programming Seam (6MP)
    print("  -> Dynamic Programming Seam (6MP)...", flush=True)
    left = (0.5 + 0.3 * np.sin(xx * 0.005) * np.cos(yy * 0.005)).astype(np.float32)
    right = np.roll(left, -100, axis=1)
    overlap = np.zeros((h, w), dtype=bool)
    overlap[:, 1400:1600] = True # 200 px wide seam region on 6MP image

    def run_seam():
        return dynamic_programming_seam(left, right, overlap_mask=overlap, direction="vertical", backend="numpy")

    seam_mask, times, ram_mb = run_benchmark_3x(run_seam)
    results["dp_seam_6mp"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "seam_cut_ratio": float(np.mean(seam_mask)),
    }

    # B) Exposure Compensation (6MP)
    print("  -> Exposure Compensation (6MP)...", flush=True)
    img1 = left.copy()
    gt_ratio = 1.35
    img2 = np.clip(img1 * gt_ratio, 0.0, 1.0).astype(np.float32)

    def run_exposure():
        return compensate_exposure([img1, img2], masks=[overlap, overlap], mode="gain", backend="numpy")

    (corrected_images, comp_obj), times, ram_mb = run_benchmark_3x(run_exposure)
    est_gain = float(comp_obj.gains[1, 0])
    ratio_err = abs(est_gain - (1.0 / gt_ratio))
    results["exposure_compensation_6mp"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "error": float(ratio_err),
        "error_unit": "gain ratio error",
    }

    # C) Sparse to Dense Warp (6MP Evaluation)
    print("  -> Sparse to Dense Warp (6MP Remap)...", flush=True)
    yy_grid, xx_grid = np.indices((h, w), dtype=np.float64)
    map_xy = np.stack([xx_grid + 20.0, yy_grid - 10.0], axis=-1)

    def run_sparse_warp():
        return sparse_to_dense_warp(left, map_xy, backend="numpy")

    (warped_img, valid_mask), times, ram_mb = run_benchmark_3x(run_sparse_warp)
    results["sparse_to_dense_warp_6mp"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "valid_pixels": int(np.sum(valid_mask)),
    }

    # D) End-to-End Stitching (6MP 3-Channel Images)
    print("  -> End-to-End Panorama Stitching (6MP 3-Channel)...", flush=True)
    img_l = np.dstack([left, left * 0.9, left * 0.8])
    img_r = np.dstack([right, right * 0.9, right * 0.8])
    T_rel = np.array([[1.0, 0.0, 150.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float64)

    def run_stitch():
        return stitch_panorama([img_l, img_r], transforms=[np.eye(3), T_rel], blend="feather", backend="numpy")

    stitched, times, ram_mb = run_benchmark_3x(run_stitch)
    results["stitch_panorama_e2e_6mp"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "output_shape": list(stitched.shape),
    }

    return results


# ==============================================================================
# 4. NeRF BENCHMARKS (Ray Marching, Instant-NGP Hash Grid, Volume Rendering)
# ==============================================================================
def benchmark_nerf():
    results = {}

    # A) Ray Marching (Ray Generation + Stratified Sampling)
    print("  -> NeRF Ray Marching (200x200 rays, 32 samples/ray)...", flush=True)
    H, W = 200, 200
    K = np.array([[300.0, 0.0, 100.0], [0.0, 300.0, 100.0], [0.0, 0.0, 1.0]], dtype=np.float32)
    c2w = np.eye(4, dtype=np.float32)
    c2w[:3, 3] = np.array([0.0, 0.0, -3.0], dtype=np.float32)

    def run_ray_marching():
        rays_o, rays_d = generate_rays(H, W, K, c2w)
        pts, z_vals, deltas = stratified_sampling(rays_o, rays_d, n_samples=32, near=1.0, far=6.0)
        return pts

    pts, times, ram_mb = run_benchmark_3x(run_ray_marching)
    results["nerf_ray_marching"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "sample_points_count": int(np.prod(pts.shape[:-1])),
    }

    # B) Multi-Resolution Hash Grid Encoding (Instant-NGP)
    print("  -> Instant-NGP Multi-Res Hash Grid Encoding...", flush=True)
    hash_grid = MultiResHashGrid(n_levels=8, n_features_per_level=2, log2_hashmap_size=14)
    query_samples = pts.reshape(-1, 3)[:5000].copy() # 5,000 3D spatial query coordinates

    def run_hash_grid():
        return hash_grid.encode(query_samples)

    features, times, ram_mb = run_benchmark_3x(run_hash_grid)
    results["nerf_hash_grid_encoding"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "feature_dim": int(features.shape[-1]),
    }

    # C) Parallel Volume Rendering
    print("  -> NeRF Volume Rendering Kernel...", flush=True)
    n_rays = 10000
    n_samples = 32
    density = np.abs(np.sin(np.linspace(0, 10, n_rays * n_samples, dtype=np.float32))).reshape(n_rays, n_samples)
    color = np.ones((n_rays, n_samples, 3), dtype=np.float32) * 0.8
    z_vals = np.repeat(np.linspace(1.0, 5.0, n_samples, dtype=np.float32)[None, :], n_rays, axis=0)
    deltas = np.repeat(np.full((1, n_samples), 4.0 / n_samples, dtype=np.float32), n_rays, axis=0)

    def run_vol_render():
        return render_volume(density, color, deltas, z_vals, backend="taichi")

    (rgb_map, depth_map, acc_map), times, ram_mb = run_benchmark_3x(run_vol_render)
    results["nerf_volume_rendering"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "mean_color": float(np.mean(rgb_map)),
    }

    # D) End-to-End Novel View Synthesis
    print("  -> NeRF End-to-End Novel View Synthesis...", flush=True)
    cfg = NeRFConfig(n_samples=24)
    scene = NeRFScene(cfg)
    novel_pose = np.eye(4, dtype=np.float32)
    novel_pose[:3, 3] = np.array([0.2, -0.1, -2.8], dtype=np.float32)

    def run_novel_view():
        rgb, depth, stats = render_nerf_view(scene, 80, 80, K[:3, :3].copy(), novel_pose)
        return rgb

    view_img, times, ram_mb = run_benchmark_3x(run_novel_view)
    results["nerf_novel_view_synthesis"] = {
        "time_ms": float(np.mean(times)),
        "time_min_ms": float(np.min(times)),
        "ram_mb": ram_mb,
        "output_shape": list(view_img.shape),
    }

    return results


def run_full_suite() -> dict:
    print("=== STARTING FULL BENCHMARK SUITE (3x ITERATIONS) ===", flush=True)
    vram_before = get_vram_status()
    t_start = time.time()

    print("\n[1/4] Benchmarking SFM family...", flush=True)
    sfm_res = benchmark_sfm()

    print("\n[2/4] Benchmarking Alignment family...", flush=True)
    align_res = benchmark_alignment()

    print("\n[3/4] Benchmarking Panorama 6MP family...", flush=True)
    pano_res = benchmark_panorama()

    print("\n[4/4] Benchmarking NeRF family...", flush=True)
    nerf_res = benchmark_nerf()

    t_end = time.time()
    vram_after = get_vram_status()

    all_results = {
        "sfm": sfm_res,
        "alignment": align_res,
        "panorama_6mp": pano_res,
        "nerf": nerf_res,
        "total_suite_time_s": t_end - t_start,
        "vram_delta_mb": vram_after["device_heap_usage_mb"] - vram_before["device_heap_usage_mb"],
    }
    return all_results


if __name__ == "__main__":
    import json
    data = run_full_suite()
    print("\n=== BENCHMARK SUITE COMPLETED SUCCESSFULLY ===")
    print(json.dumps(data, indent=2))
