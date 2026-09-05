import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Impor kernel homography solver dari ransac
from taichi_vision.taichi_algorithm.alignment.ransac import (
    ransac_homography_kernel,
    find_best_candidate_kernel,
    refine_homography_iterative_kernel,
    generate_inlier_mask_kernel,
    refine_homography_kernel,
    _compute_mean_flow_kernel,
    _count_inliers_kernel,
    _compute_inlier_mean_kernel,
    _apply_ransac_result_kernel,
    ransac_fundamental_kernel,
    generate_fundamental_inlier_mask_kernel,
    vsac_classify_independent_kernel,
)

def compile_ransac_tcm(arch=ti.vulkan, save_path="ransac_vulkan.tcm"):
    print(f"\n>>> Compiling RANSAC/MAGSAC++ AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # ``ti.cpu`` and ``ti.x64`` are distinct aliases in some Taichi 1.7.4
    # builds.  Treat both as the CPU profile; otherwise the worker can enter
    # the graphics graph path and report a misleading ndim error.
    if arch == ti.cpu or arch == getattr(ti, "x64", None):
        # CPU feature alignment uses the same Taichi RANSAC contract as the
        # graphics backends. The old CPU artifact intentionally omitted these
        # graphs, which forced the adapter to depend on OpenCV.
        _register_homography_graphs(module)

        g_flow = ti.graph.GraphBuilder()
        # The kernels index the final x/y components explicitly
        # (``flow[iy, ix, 0]``), so the graph ABI is a scalar f32 3-D array
        # with shape HxWx2.  Describing it as a vector2 2-D ndarray makes
        # Taichi 1.7.4 validate the access as rank-2 and fail at compile time.
        fflow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        fmask = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_mask", ti.i32, ndim=2)
        fmodel = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "model", ti.f32, ndim=1)
        foutput = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.f32, ndim=3)
        fh = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        fw = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        fthreshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
        fstride_refine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_refine", ti.i32)
        fstride_final = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_final", ti.i32)
        g_flow.dispatch(_compute_mean_flow_kernel, fflow, fmodel, fh, fw, fstride_refine)
        g_flow.dispatch(_count_inliers_kernel, fflow, fmodel, fthreshold, fmask, fh, fw, fstride_refine)
        g_flow.dispatch(_compute_inlier_mean_kernel, fflow, fmask, fmodel, fh, fw, fstride_refine)
        g_flow.dispatch(_count_inliers_kernel, fflow, fmodel, fthreshold, fmask, fh, fw, fstride_final)
        g_flow.dispatch(_apply_ransac_result_kernel, fflow, fmask, fmodel, foutput, fh, fw)
        module.add_graph("ransac_flow_cleanup_f32", g_flow.compile())

        # Fundamental estimation is intentionally opt-in because the
        # 8-point hypothesis kernel is substantially larger than the flow
        # cleanup graph.  When enabled, keep the exact source kernels and
        # graph ABI shared with graphics targets; old CPU artifacts remain
        # valid and simply do not advertise these optional graphs.
        if os.environ.get("PIXEL_REFINE_COMPILE_VSAC", "0") == "1":
            _register_fundamental_graphs(module)
        module.archive(save_path)
        print(f"Successfully compiled CPU RANSAC flow AOT and archived to: {save_path}")
        ti.reset()
        return

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

    # 1.5 Find Best Candidate Graph
    g_best = ti.graph.GraphBuilder()
    bcand_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_candidates", ti.f32, ndim=2)
    bcnt_arg  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_counts", ti.i32, ndim=1)
    bnhyp_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_hypotheses",  ti.i32)
    bbest_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_best_out",    ti.f32, ndim=1)
    g_best.dispatch(find_best_candidate_kernel, bcand_arg, bcnt_arg, bnhyp_arg, bbest_arg)
    module.add_graph("find_best_candidate", g_best.compile())

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

    # 4. Full GPU Pipeline Graph
    g_pipeline = ti.graph.GraphBuilder()
    apts1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1", ti.f32, ndim=2)
    apts2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2", ti.f32, ndim=2)
    anpts = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_pts", ti.i32)
    anhyp = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "n_hypotheses", ti.i32)
    arthresh = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "reproj_threshold", ti.f32)
    aseed = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "seed_offset", ti.i32)
    ahcand = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_candidates", ti.f32, ndim=2)
    aicnt = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_counts", ti.i32, ndim=1)
    ahbest = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_best", ti.f32, ndim=1)
    amask = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mask", ti.i32, ndim=1)
    
    amax_ref_iters = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_ref_iters", ti.i32)
    aearly_stop = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "early_stop_thresh", ti.f32)
    ahrefined = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "H_refined", ti.f32, ndim=1)

    g_pipeline.dispatch(ransac_homography_kernel, apts1, apts2, anpts, anhyp, arthresh, ahcand, aicnt, aseed)
    g_pipeline.dispatch(find_best_candidate_kernel, ahcand, aicnt, anhyp, ahbest)
    g_pipeline.dispatch(refine_homography_iterative_kernel, apts1, apts2, ahbest, anpts, arthresh, amax_ref_iters, aearly_stop, ahrefined)
    g_pipeline.dispatch(generate_inlier_mask_kernel, apts1, apts2, ahrefined, anpts, arthresh, amask)
    module.add_graph("ransac_homography_pipeline", g_pipeline.compile())

    # Flow cleanup graph used by the public AOT API.  Keep the reduction
    # buffers explicit; this avoids relying on a missing monolithic graph and
    # works identically for CPU and Vulkan AOT.
    g_flow = ti.graph.GraphBuilder()
    # The flow kernels index ``flow[y, x, component]`` explicitly.  Describe
    # the target graph as scalar f32 rank-3 (H x W x 2) instead of a vector2
    # rank-2 ndarray; Taichi 1.7.4 otherwise validates the access as rank-2
    # and rejects the graphics worker before any archive is produced.
    fflow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
    fmask = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_mask", ti.i32, ndim=2)
    fmodel = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "model", ti.f32, ndim=1)
    foutput = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.f32, ndim=3)
    fh = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    fw = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    fthreshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    fstride_refine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_refine", ti.i32)
    fstride_final = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_final", ti.i32)
    g_flow.dispatch(_compute_mean_flow_kernel, fflow, fmodel, fh, fw, fstride_refine)
    g_flow.dispatch(_count_inliers_kernel, fflow, fmodel, fthreshold, fmask, fh, fw, fstride_refine)
    g_flow.dispatch(_compute_inlier_mean_kernel, fflow, fmask, fmodel, fh, fw, fstride_refine)
    g_flow.dispatch(_count_inliers_kernel, fflow, fmodel, fthreshold, fmask, fh, fw, fstride_final)
    g_flow.dispatch(_apply_ransac_result_kernel, fflow, fmask, fmodel, foutput, fh, fw)
    module.add_graph("ransac_flow_cleanup_f32", g_flow.compile())

    if os.environ.get("PIXEL_REFINE_COMPILE_VSAC", "0") == "1":
        _register_fundamental_graphs(module)

    module.archive(save_path)
    print(f"Successfully compiled RANSAC/MAGSAC++ AOT and archived to: {save_path}")
    ti.reset()


def _register_homography_graphs(module):
    """Register the homography leaves required by the OpenCV-free adapters."""
    g_ransac = ti.graph.GraphBuilder()
    rpts1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1", ti.f32, ndim=2)
    rpts2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2", ti.f32, ndim=2)
    rnpts_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pts", ti.i32)
    rnhyp_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_hypotheses", ti.i32)
    rrthresh_arg = ti.graph.Arg(
        ti.graph.ArgKind.SCALAR, "reproj_threshold", ti.f32
    )
    rHcand_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "H_candidates", ti.f32, ndim=2
    )
    ricnt_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "inlier_counts", ti.i32, ndim=1
    )
    rseed_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "seed_offset", ti.i32)
    g_ransac.dispatch(
        ransac_homography_kernel,
        rpts1_arg,
        rpts2_arg,
        rnpts_arg,
        rnhyp_arg,
        rrthresh_arg,
        rHcand_arg,
        ricnt_arg,
        rseed_arg,
    )
    module.add_graph("ransac_homography", g_ransac.compile())

    g_mask = ti.graph.GraphBuilder()
    mhbest_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "H_best", ti.f32, ndim=1
    )
    mnpts_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pts", ti.i32)
    mrthresh_arg = ti.graph.Arg(
        ti.graph.ArgKind.SCALAR, "reproj_threshold", ti.f32
    )
    mmask_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "mask_out", ti.i32, ndim=1
    )
    g_mask.dispatch(
        generate_inlier_mask_kernel,
        rpts1_arg,
        rpts2_arg,
        mhbest_arg,
        mnpts_arg,
        mrthresh_arg,
        mmask_arg,
    )
    module.add_graph("generate_inlier_mask", g_mask.compile())

    g_refine = ti.graph.GraphBuilder()
    rfmask_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mask", ti.i32, ndim=1)
    rfATA_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ATA_out", ti.f32, ndim=2)
    rfATb_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ATb_out", ti.f32, ndim=1)
    g_refine.dispatch(
        refine_homography_kernel,
        rpts1_arg,
        rpts2_arg,
        rfmask_arg,
        mnpts_arg,
        mrthresh_arg,
        rfATA_arg,
        rfATb_arg,
    )
    module.add_graph("refine_homography", g_refine.compile())


def _register_fundamental_graphs(module):
    """Register the VSAC fundamental leaves in a target-qualified module.

    The public adapter composes these leaves with a bounded host selection
    step.  Keeping candidate generation, Sampson masking, and independent
    classification as separate graphs avoids a second implementation and
    preserves the existing JIT kernel semantics.
    """
    f32, i32 = ti.f32, ti.i32

    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        ransac_fundamental_kernel,
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pts", i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_hypotheses", i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", f32),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "F_candidates", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "scores", i32, ndim=1),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "seed_offset", i32),
    )
    module.add_graph("ransac_fundamental", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        generate_fundamental_inlier_mask_kernel,
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "F_best", f32, ndim=1),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pts", i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", f32),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mask_out", i32, ndim=1),
    )
    module.add_graph("generate_fundamental_inlier_mask", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        vsac_classify_independent_kernel,
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts1", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pts2", f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "F_arr", f32, ndim=1),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pts", i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", f32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "epipole_thresh", f32),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "indep_count_out", i32, ndim=1),
    )
    module.add_graph("vsac_classify_independent", builder.compile())

if __name__ == "__main__":
    script_dir = file_dir
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
