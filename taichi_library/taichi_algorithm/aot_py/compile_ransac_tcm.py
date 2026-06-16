import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Impor kernel homography solver dari ransac
from taichi_library.taichi_algorithm.ransac import (
    ransac_homography_kernel,
    generate_inlier_mask_kernel,
    refine_homography_kernel,
)

def compile_ransac_tcm(arch=ti.vulkan, save_path="ransac_vulkan.tcm"):
    print(f"\n>>> Compiling RANSAC/MAGSAC++ AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. RANSAC Homography Graph
    g_ransac = ti.graph.GraphBuilder()
    rpts1_arg    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1",           ti.f32, ndim=2)
    rpts2_arg    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2",           ti.f32, ndim=2)
    rnpts_arg    = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_pts",          ti.i32)
    rnhyp_arg    = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_hypotheses",   ti.i32)
    rrthresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "reproj_threshold",ti.f32)
    rHcand_arg   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_candidates",   ti.f32, ndim=2)
    ricnt_arg    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_counts",  ti.i32, ndim=1)
    rseed_arg    = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "seed_offset",    ti.i32)
    g_ransac.dispatch(ransac_homography_kernel, rpts1_arg, rpts2_arg, rnpts_arg, rnhyp_arg, rrthresh_arg, rHcand_arg, ricnt_arg, rseed_arg)
    module.add_graph("ransac_homography", g_ransac.compile())

    # 2. Generate Inlier Mask Graph
    g_mask = ti.graph.GraphBuilder()
    mpts1_arg   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1",           ti.f32, ndim=2)
    mpts2_arg   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2",           ti.f32, ndim=2)
    mhbest_arg  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_best",         ti.f32, ndim=1)
    mnpts_arg   = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_pts",          ti.i32)
    mrthresh_arg= ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "reproj_threshold",ti.f32)
    mmask_arg   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mask_out",       ti.i32, ndim=1)
    g_mask.dispatch(generate_inlier_mask_kernel, mpts1_arg, mpts2_arg, mhbest_arg, mnpts_arg, mrthresh_arg, mmask_arg)
    module.add_graph("generate_inlier_mask", g_mask.compile())

    # 3. Refine Homography Graph (Least-Squares over all inliers)
    g_refine = ti.graph.GraphBuilder()
    rfpts1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1",   ti.f32, ndim=2)
    rfpts2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2",   ti.f32, ndim=2)
    rfmask_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mask",   ti.i32, ndim=1)
    rfnpts_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_pts",  ti.i32)
    rfthresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "reproj_threshold", ti.f32)
    rfATA_arg  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ATA_out",ti.f32, ndim=2)
    rfATb_arg  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ATb_out",ti.f32, ndim=1)
    g_refine.dispatch(refine_homography_kernel, rfpts1_arg, rfpts2_arg, rfmask_arg, rfnpts_arg, rfthresh_arg, rfATA_arg, rfATb_arg)
    module.add_graph("refine_homography", g_refine.compile())

    module.archive(save_path)
    print(f"Successfully compiled RANSAC/MAGSAC++ AOT and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu"),
    ]
    
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"ransac_{suffix}.tcm"))
        try:
            compile_ransac_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
