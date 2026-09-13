import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_vision.taichi_algorithm.feature_matching.akaze import (
    compute_conductivity_map,
    fed_diffusion_step,
    compute_hessian_determinant,
    compute_scale_normalized_hessian,
    extract_grid_keypoints,
    extract_scale_space_keypoints,
    compute_descriptors_kernel,
    hamming_matcher_kernel,
    pack_matches_kernel,
    pack_matches_offset_kernel,
)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module


def compile_akaze_tcm(arch=ti.vulkan, save_path="akaze_vulkan.tcm"):
    print(f"\n>>> Compiling A-KAZE AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Conductivity Map Graph
    g_cond = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    cond_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity", ti.f32, ndim=2)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    k_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "k", ti.f32)
    g_cond.dispatch(compute_conductivity_map, src_arg, cond_arg, h_arg, w_arg, k_arg)
    module.add_graph("compute_conductivity_map", g_cond.compile())

    # 2. FED Diffusion Step Graph
    g_fed = ti.graph.GraphBuilder()
    src_fed = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_fed = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    cond_fed = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity", ti.f32, ndim=2)
    h_fed = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_fed = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    tau_fed = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tau", ti.f32)
    g_fed.dispatch(fed_diffusion_step, src_fed, dst_fed, cond_fed, h_fed, w_fed, tau_fed)
    module.add_graph("fed_diffusion_step", g_fed.compile())

    # 3. Hessian Determinant Graph
    g_hess = ti.graph.GraphBuilder()
    src_hess = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    hess_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map", ti.f32, ndim=2)
    h_hess = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_hess = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_hess.dispatch(compute_hessian_determinant, src_hess, hess_arg, h_hess, w_hess)
    module.add_graph("compute_hessian_determinant", g_hess.compile())

    # Paper-faithful scale-normalized Hessian response.
    g_hess_scale = ti.graph.GraphBuilder()
    sh_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    sh_hessian = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map", ti.f32, ndim=2)
    sh_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    sh_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    sh_sigma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma_norm", ti.f32)
    g_hess_scale.dispatch(
        compute_scale_normalized_hessian,
        sh_src, sh_hessian, sh_h, sh_w, sh_sigma,
    )
    module.add_graph("compute_scale_normalized_hessian", g_hess_scale.compile())

    # 4. Keypoint Extraction Graph (ANMS)
    g_detect = ti.graph.GraphBuilder()
    hess_det = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map", ti.f32, ndim=2)
    kps_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints", ti.f32, ndim=2)
    counter_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    h_detect = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_detect = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    grid_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    thresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    g_detect.dispatch(extract_grid_keypoints, hess_det, kps_arg, counter_arg, h_detect, w_detect, grid_arg, thresh_arg)
    module.add_graph("detect_keypoints", g_detect.compile())

    # 3x3x3 scale-space extrema detector.  The public API still returns the
    # same (x, y) match coordinates; scale remains internal to the detector.
    g_detect_scale = ti.graph.GraphBuilder()
    ss_prev = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_prev", ti.f32, ndim=2)
    ss_curr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_curr", ti.f32, ndim=2)
    ss_next = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_next", ti.f32, ndim=2)
    ss_kps = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints", ti.f32, ndim=2)
    ss_counter = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    ss_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    ss_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    ss_grid = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    ss_margin = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "margin", ti.i32)
    ss_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    g_detect_scale.dispatch(
        extract_scale_space_keypoints,
        ss_prev, ss_curr, ss_next, ss_kps, ss_counter,
        ss_h, ss_w, ss_grid, ss_margin, ss_threshold,
    )
    module.add_graph("detect_scale_space_keypoints", g_detect_scale.compile())

    # 5. Compute Descriptors Graph
    g_desc = ti.graph.GraphBuilder()
    src_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    kps_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps", ti.f32, ndim=2)
    pattern_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pattern", ti.f32, ndim=2)
    desc_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc", ti.i32, ndim=2)
    counter_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    h_desc = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_desc = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_desc.dispatch(compute_descriptors_kernel, src_desc, kps_desc, pattern_desc, desc_arg, counter_desc, h_desc, w_desc)
    module.add_graph("compute_descriptors", g_desc.compile())

    # Single-image fused detection/description used by the resident CUDA
    # reference cache.  Dispatch order is identical to the three legacy
    # graphs, but crosses the Python/C-API boundary only once.
    g_detect_desc = ti.graph.GraphBuilder()
    fd_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    fd_hessian = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map", ti.f32, ndim=2)
    fd_kps = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints", ti.f32, ndim=2)
    fd_counter = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    fd_pattern = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pattern", ti.f32, ndim=2)
    fd_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc", ti.i32, ndim=2)
    fd_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    fd_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    fd_grid = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    fd_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    g_detect_desc.dispatch(compute_hessian_determinant, fd_src, fd_hessian, fd_h, fd_w)
    g_detect_desc.dispatch(extract_grid_keypoints, fd_hessian, fd_kps, fd_counter, fd_h, fd_w, fd_grid, fd_threshold)
    g_detect_desc.dispatch(compute_descriptors_kernel, fd_src, fd_kps, fd_pattern, fd_desc, fd_counter, fd_h, fd_w)
    module.add_graph("detect_and_describe", g_detect_desc.compile())

    # 6. Match Descriptors Graph
    g_match = ti.graph.GraphBuilder()
    d1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc1", ti.i32, ndim=2)
    d2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc2", ti.i32, ndim=2)
    m_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    c1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    c2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    ratio_thresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ratio_threshold", ti.f32)
    g_match.dispatch(hamming_matcher_kernel, d1_arg, d2_arg, m_arg, c1_arg, c2_arg, ratio_thresh_arg)
    module.add_graph("match_descriptors", g_match.compile())

    # 7. Pack Matches Graph
    g_pack = ti.graph.GraphBuilder()
    pkps1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps1", ti.f32, ndim=2)
    pkps2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps2", ti.f32, ndim=2)
    pmatches_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    pcounter1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    pcounter2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    presults_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.f32, ndim=2)
    g_pack.dispatch(pack_matches_kernel, pkps1_arg, pkps2_arg, pmatches_arg, pcounter1_arg, pcounter2_arg, presults_arg)
    module.add_graph("pack_matches", g_pack.compile())

    # Pair graphs execute the same two independent image kernels in one AOT
    # launch.  No arithmetic or ordering within either image changes.
    g_cond_pair = ti.graph.GraphBuilder()
    cp_src1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src1", ti.f32, ndim=2)
    cp_src2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src2", ti.f32, ndim=2)
    cp_cond1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity1", ti.f32, ndim=2)
    cp_cond2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity2", ti.f32, ndim=2)
    cp_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    cp_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    cp_k = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "k", ti.f32)
    g_cond_pair.dispatch(compute_conductivity_map, cp_src1, cp_cond1, cp_h, cp_w, cp_k)
    g_cond_pair.dispatch(compute_conductivity_map, cp_src2, cp_cond2, cp_h, cp_w, cp_k)
    module.add_graph("compute_conductivity_pair", g_cond_pair.compile())

    g_fed_pair = ti.graph.GraphBuilder()
    fp_src1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src1", ti.f32, ndim=2)
    fp_src2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src2", ti.f32, ndim=2)
    fp_dst1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst1", ti.f32, ndim=2)
    fp_dst2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst2", ti.f32, ndim=2)
    fp_cond1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity1", ti.f32, ndim=2)
    fp_cond2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conductivity2", ti.f32, ndim=2)
    fp_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    fp_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    fp_tau = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tau", ti.f32)
    g_fed_pair.dispatch(fed_diffusion_step, fp_src1, fp_dst1, fp_cond1, fp_h, fp_w, fp_tau)
    g_fed_pair.dispatch(fed_diffusion_step, fp_src2, fp_dst2, fp_cond2, fp_h, fp_w, fp_tau)
    module.add_graph("fed_diffusion_pair", g_fed_pair.compile())

    g_detect_pair = ti.graph.GraphBuilder()
    dp_src1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src1", ti.f32, ndim=2)
    dp_src2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src2", ti.f32, ndim=2)
    dp_hess1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map1", ti.f32, ndim=2)
    dp_hess2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hessian_map2", ti.f32, ndim=2)
    dp_kps1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints1", ti.f32, ndim=2)
    dp_kps2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints2", ti.f32, ndim=2)
    dp_counter1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    dp_counter2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    dp_pattern = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pattern", ti.f32, ndim=2)
    dp_desc1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc1", ti.i32, ndim=2)
    dp_desc2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc2", ti.i32, ndim=2)
    dp_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    dp_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    dp_grid = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    dp_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    g_detect_pair.dispatch(compute_hessian_determinant, dp_src1, dp_hess1, dp_h, dp_w)
    g_detect_pair.dispatch(extract_grid_keypoints, dp_hess1, dp_kps1, dp_counter1, dp_h, dp_w, dp_grid, dp_threshold)
    g_detect_pair.dispatch(compute_descriptors_kernel, dp_src1, dp_kps1, dp_pattern, dp_desc1, dp_counter1, dp_h, dp_w)
    g_detect_pair.dispatch(compute_hessian_determinant, dp_src2, dp_hess2, dp_h, dp_w)
    g_detect_pair.dispatch(extract_grid_keypoints, dp_hess2, dp_kps2, dp_counter2, dp_h, dp_w, dp_grid, dp_threshold)
    g_detect_pair.dispatch(compute_descriptors_kernel, dp_src2, dp_kps2, dp_pattern, dp_desc2, dp_counter2, dp_h, dp_w)
    module.add_graph("detect_and_describe_pair", g_detect_pair.compile())

    g_match_pack = ti.graph.GraphBuilder()
    mp_d1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc1", ti.i32, ndim=2)
    mp_d2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc2", ti.i32, ndim=2)
    mp_matches = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    mp_c1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    mp_c2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    mp_ratio = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ratio_threshold", ti.f32)
    mp_kps1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps1", ti.f32, ndim=2)
    mp_kps2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps2", ti.f32, ndim=2)
    mp_results = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.f32, ndim=2)
    g_match_pack.dispatch(hamming_matcher_kernel, mp_d1, mp_d2, mp_matches, mp_c1, mp_c2, mp_ratio)
    g_match_pack.dispatch(pack_matches_kernel, mp_kps1, mp_kps2, mp_matches, mp_c1, mp_c2, mp_results)
    module.add_graph("match_and_pack", g_match_pack.compile())

    # Write all pyramid levels into one shared result buffer.  The offset is
    # scalar and does not alter the existing public graph contract.
    g_match_pack_offset = ti.graph.GraphBuilder()
    op_d1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc1", ti.i32, ndim=2)
    op_d2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc2", ti.i32, ndim=2)
    op_matches = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    op_c1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    op_c2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    op_ratio = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ratio_threshold", ti.f32)
    op_kps1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps1", ti.f32, ndim=2)
    op_kps2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps2", ti.f32, ndim=2)
    op_results = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.f32, ndim=2)
    op_offset = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "result_offset", ti.i32)
    g_match_pack_offset.dispatch(
        hamming_matcher_kernel,
        op_d1, op_d2, op_matches, op_c1, op_c2, op_ratio,
    )
    g_match_pack_offset.dispatch(
        pack_matches_offset_kernel,
        op_kps1, op_kps2, op_matches, op_c1, op_c2, op_results, op_offset,
    )
    module.add_graph("match_and_pack_offset", g_match_pack_offset.compile())
    archive_module(module, save_path)
    print(f"Successfully compiled A-KAZE AOT and archived to: {save_path}")
    ti.reset()


if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)

    # Standalone compilation must publish only target-qualified artifacts.
    # The historical ``aot_tcm/akaze_<backend>.tcm`` files are ambiguous on
    # hybrid systems and are intentionally no longer regenerated.  The suite
    # uses the same target IDs; keeping this script aligned prevents a manual
    # compile from reintroducing stale legacy artifacts.
    target_override = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
    target_ids = {
        "vulkan": "vulkan_x86_64_windows",
        "cuda": "cuda_x86_64_windows_nvidia",
        "opengl": "opengl_x86_64_windows",
        "cpu": "cpu_x86_64_windows",
    }

    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.opengl, "opengl"),
        (ti.cpu, "cpu"),
    ]

    for arch, suffix in archs:
        target_id = target_override or target_ids[suffix]
        target_dir = os.path.join(assets_dir, target_id)
        os.makedirs(target_dir, exist_ok=True)
        save_path = os.path.abspath(
            os.path.join(target_dir, f"akaze_{target_id}.tcm")
        )
        try:
            compile_akaze_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
