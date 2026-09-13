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
    pack_matches_offset_kernel,
)
from taichi_vision.taichi_algorithm.pyramid import pyramid as pyramid_kernels
from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

def compile_ofb_tcm(arch=ti.vulkan, save_path="ofb_vulkan.tcm"):
    print(f"\n>>> Compiling O-FAST-BRIEF AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # Keep the canonical pyramid kernels in the OFB archive as well.  This is
    # source-level bundling: an AOT module cannot invoke an already archived
    # pyramid TCM, but it can contain the same kernel implementations and
    # expose them as additional graphs.  The runtime can therefore record a
    # same-module pyramid sequence without changing the public pyramid API.
    g_pyramid = ti.graph.GraphBuilder()
    pyr_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    pyr_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_pyramid.dispatch(
        pyramid_kernels._downsample_2x_kernel,
        pyr_src,
        pyr_dst,
    )
    module.add_graph("downsample_2x_f32", g_pyramid.compile())

    g_pyramid_3ch = ti.graph.GraphBuilder()
    pyr_src_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    pyr_dst_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_pyramid_3ch.dispatch(
        pyramid_kernels._downsample_2x_kernel_3ch,
        pyr_src_3ch,
        pyr_dst_3ch,
    )
    module.add_graph("downsample_2x_3ch_f32", g_pyramid_3ch.compile())

    pyr_offset_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_y", ti.i32)
    pyr_offset_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_x", ti.i32)
    g_pyramid_offset = ti.graph.GraphBuilder()
    g_pyramid_offset.dispatch(
        pyramid_kernels._downsample_2x_offset_kernel,
        pyr_src,
        pyr_dst,
        pyr_offset_y,
        pyr_offset_x,
    )
    module.add_graph("downsample_2x_offset_f32", g_pyramid_offset.compile())

    g_pyramid_offset_3ch = ti.graph.GraphBuilder()
    g_pyramid_offset_3ch.dispatch(
        pyramid_kernels._downsample_2x_offset_kernel_3ch,
        pyr_src_3ch,
        pyr_dst_3ch,
        pyr_offset_y,
        pyr_offset_x,
    )
    module.add_graph(
        "downsample_2x_offset_3ch_f32",
        g_pyramid_offset_3ch.compile(),
    )

    # Static chain graphs provide the low-overhead bundle path.  The graph
    # still contains one native downsample dispatch per level (there is no
    # arithmetic fusion claim), but the host submits the complete ordered
    # chain once and does not create a one-shot recorder for every call.
    for chain_length in (2, 3):
        chain = ti.graph.GraphBuilder()
        chain_args = [
            ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
        ]
        # Keep input/output handles distinct even though the runtime binds
        # each intermediate pair to the same buffer.  Reusing one graph Arg
        # in two dispatches makes Taichi infer incompatible shape constraints
        # (the producer's output shape versus the consumer's input shape).
        chain_inputs = [chain_args[0]]
        chain_outputs = []
        for level_index in range(1, chain_length):
            out_arg = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY,
                f"level_{level_index}_out",
                ti.f32,
                ndim=2,
            )
            in_arg = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY,
                f"level_{level_index}_in",
                ti.f32,
                ndim=2,
            )
            chain_outputs.append(out_arg)
            chain_inputs.append(in_arg)
        dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
        chain_outputs.append(dst_arg)
        for level_index in range(chain_length):
            chain.dispatch(
                pyramid_kernels._downsample_2x_kernel,
                chain_inputs[level_index],
                chain_outputs[level_index],
            )
        module.add_graph(
            f"pyramid_chain_{chain_length}_f32",
            chain.compile(),
        )

        chain_3ch = ti.graph.GraphBuilder()
        chain_args_3ch = [
            ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
        ]
        chain_inputs_3ch = [chain_args_3ch[0]]
        chain_outputs_3ch = []
        for level_index in range(1, chain_length):
            out_arg = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY,
                f"level_{level_index}_out",
                ti.f32,
                ndim=3,
            )
            in_arg = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY,
                f"level_{level_index}_in",
                ti.f32,
                ndim=3,
            )
            chain_outputs_3ch.append(out_arg)
            chain_inputs_3ch.append(in_arg)
        dst_arg_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
        chain_outputs_3ch.append(dst_arg_3ch)
        for level_index in range(chain_length):
            chain_3ch.dispatch(
                pyramid_kernels._downsample_2x_kernel_3ch,
                chain_inputs_3ch[level_index],
                chain_outputs_3ch[level_index],
            )
        module.add_graph(
            f"pyramid_chain_{chain_length}_3ch_f32",
            chain_3ch.compile(),
        )

    g_pyramid_up = ti.graph.GraphBuilder()
    pyr_flow_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    pyr_flow_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    pyr_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    g_pyramid_up.dispatch(
        pyramid_kernels._upsample_flow_kernel,
        pyr_flow_src,
        pyr_flow_dst,
        pyr_scale,
    )
    module.add_graph("upsample_flow_f32", g_pyramid_up.compile())

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

    # Fused dispatch variants preserve the exact kernel order and buffers of
    # the legacy graphs while reducing Python -> C API -> graph launch traffic.
    g_detect_desc = ti.graph.GraphBuilder()
    dd_detect_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "detect_src", ti.f32, ndim=2)
    dd_desc_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "descriptor_src", ti.f32, ndim=2)
    dd_score = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "score_map", ti.f32, ndim=2)
    dd_kps = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "keypoints", ti.f32, ndim=2)
    dd_counter = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "counter", ti.i32, ndim=1)
    dd_pattern = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "pattern", ti.f32, ndim=2)
    dd_desc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "desc", ti.i32, ndim=2)
    dd_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    dd_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    dd_grid = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_size", ti.i32)
    dd_margin = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "margin", ti.i32)
    dd_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    g_detect_desc.dispatch(compute_score_map, dd_detect_src, dd_score, dd_h, dd_w, dd_margin)
    g_detect_desc.dispatch(extract_grid_keypoints, dd_score, dd_kps, dd_counter, dd_h, dd_w, dd_grid, dd_threshold)
    g_detect_desc.dispatch(_compute_descriptors_kernel, dd_desc_src, dd_kps, dd_pattern, dd_desc, dd_counter, dd_h, dd_w)
    module.add_graph("detect_and_describe", g_detect_desc.compile())

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
    g_match_pack.dispatch(_hamming_matcher_kernel, mp_d1, mp_d2, mp_matches, mp_c1, mp_c2, mp_ratio)
    g_match_pack.dispatch(pack_matches_kernel, mp_kps1, mp_kps2, mp_matches, mp_c1, mp_c2, mp_results)
    module.add_graph("match_and_pack", g_match_pack.compile())

    # Offset variant writes each pyramid level into one shared result buffer.
    # It preserves the legacy row layout while moving the host readback out of
    # the level loop (one readback per feature-matching call).
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
        _hamming_matcher_kernel,
        op_d1, op_d2, op_matches, op_c1, op_c2, op_ratio,
    )
    g_match_pack_offset.dispatch(
        pack_matches_offset_kernel,
        op_kps1, op_kps2, op_matches, op_c1, op_c2, op_results, op_offset,
    )
    module.add_graph("match_and_pack_offset", g_match_pack_offset.compile())

    archive_module(module, save_path)
    print(f"Successfully compiled O-FAST-BRIEF and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
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
            os.path.join(target_dir, f"ofb_{target_id}.tcm")
        )
        try:
            compile_ofb_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
