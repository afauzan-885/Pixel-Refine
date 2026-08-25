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
    extract_grid_keypoints,
    compute_descriptors_kernel,
    hamming_matcher_kernel,
    pack_matches_kernel,
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
        "cpu": "cpu_x86_64_windows",
    }

    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
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
