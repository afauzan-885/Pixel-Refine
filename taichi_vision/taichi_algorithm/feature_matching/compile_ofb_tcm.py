import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_vision.taichi_algorithm.feature_matching.ofb import (
    compute_score_map,
    extract_grid_keypoints,
    _compute_descriptors_kernel,
    _hamming_matcher_kernel,
    pack_matches_kernel,
)

def compile_ofb_tcm(arch=ti.vulkan, save_path="ofb_vulkan.tcm"):
    print(f"\n>>> Compiling O-FAST-BRIEF AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    g_detect = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    score_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "score_map", ti.f32, ndim=2)
    keypoints_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints", ti.f32, ndim=2)
    counter_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    grid_size_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    margin_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "margin", ti.i32)
    threshold_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    
    # Pipeline Deteksi: Score Map -> Grid ANMS
    g_detect.dispatch(compute_score_map, src_arg, score_arg, h_arg, w_arg, margin_arg)
    g_detect.dispatch(extract_grid_keypoints, score_arg, keypoints_arg, counter_arg, h_arg, w_arg, grid_size_arg, threshold_arg)
    
    module.add_graph("detect_keypoints", g_detect.compile())

    g_desc = ti.graph.GraphBuilder()
    src_arg2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    kps_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps", ti.f32, ndim=2)
    pattern_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pattern", ti.f32, ndim=2)
    desc_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc", ti.i32, ndim=2)
    counter_arg2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    h_arg2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    
    g_desc.dispatch(_compute_descriptors_kernel, src_arg2, kps_arg, pattern_arg, desc_arg, counter_arg2, h_arg2, w_arg2)
    module.add_graph("compute_descriptors", g_desc.compile())

    g_match = ti.graph.GraphBuilder()
    d1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc1", ti.i32, ndim=2)
    d2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc2", ti.i32, ndim=2)
    m_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    c1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    c2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    ratio_thresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ratio_threshold", ti.f32)
    
    g_match.dispatch(_hamming_matcher_kernel, d1_arg, d2_arg, m_arg, c1_arg, c2_arg, ratio_thresh_arg)
    module.add_graph("match_descriptors", g_match.compile())

    g_pack = ti.graph.GraphBuilder()
    kps1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps1", ti.f32, ndim=2)
    kps2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "kps2", ti.f32, ndim=2)
    matches_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "matches", ti.i32, ndim=2)
    counter1_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter1", ti.i32, ndim=1)
    counter2_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter2", ti.i32, ndim=1)
    results_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.f32, ndim=2)

    g_pack.dispatch(pack_matches_kernel, kps1_arg, kps2_arg, matches_arg, counter1_arg, counter2_arg, results_arg)
    module.add_graph("pack_matches", g_pack.compile())

    module.archive(save_path)
    print(f"Successfully compiled O-FAST-BRIEF and archived to: {save_path}")
    ti.reset()

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"ofb_{suffix}.tcm"))
        try:
            compile_ofb_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
