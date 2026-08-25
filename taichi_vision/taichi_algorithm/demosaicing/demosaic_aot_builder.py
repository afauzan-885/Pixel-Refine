"""Modular Taichi AOT builder for the demosaic family.

This module centralizes graph *argument* definitions and graph *registration*
for demosaic kernels so that every compiled graph matches exactly what the
runtime wrappers in ``taichi_algorithm/aot_api`` call.  Keeping the argument
names in one place is the defense-in-depth against the mismatch class that
caused ``Missing runtime value for wb_bayer`` and ``name not found
hamilton_demosaic_rgb_half_res`` in the CUDA runtime logs.

Each family exposes a ``register_<family>_graphs(module, kernels)`` function
that only adds graphs (it never owns Taichi init/teardown or arch policy).
The thin per-family compile entry points (e.g. ``compile_bilinear_demosaice_tcm``)
own ``ti.init``, module creation and archiving, and simply call the builder.

``kernels`` is a plain dict of logical-name -> compiled ``@ti.kernel`` callable.
Only the keys a family actually dispatches are required.
"""

import taichi as ti


# ---------------------------------------------------------------------------
# Shared graph-argument helpers
# ---------------------------------------------------------------------------
def scalar_arg(name, dtype):
    return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)


def ndarray_arg(name, dtype, ndim):
    return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, dtype, ndim=ndim)


def demosaic_scalars():
    """The 12 canonical scalar args shared by nearly every demosaic graph.

    Returned as a dict keyed by argument name so graph builders can reference
    them by name and never drift from the wrapper ABI.
    """
    return {
        "wb_r": scalar_arg("wb_r", ti.f32),
        "wb_g1": scalar_arg("wb_g1", ti.f32),
        "wb_b": scalar_arg("wb_b", ti.f32),
        "wb_g2": scalar_arg("wb_g2", ti.f32),
        "black": scalar_arg("black", ti.f32),
        "white": scalar_arg("white", ti.f32),
        "h": scalar_arg("h", ti.i32),
        "w": scalar_arg("w", ti.i32),
        "c00": scalar_arg("c00", ti.i32),
        "c01": scalar_arg("c01", ti.i32),
        "c10": scalar_arg("c10", ti.i32),
        "c11": scalar_arg("c11", ti.i32),
    }


def bilinear_io_args():
    """NDArray args for the bilinear family (bayer, optional cmatrix, dst)."""
    return {
        "bayer": ndarray_arg("bayer", ti.f32, 2),
        "cmatrix": ndarray_arg("cmatrix", ti.f32, 2),
        "dst": ndarray_arg("dst", ti.f32, 3),
        "dst_2d": ndarray_arg("dst", ti.f32, 2),
    }


def rgb_to_bgr_i32_args():
    """Args for the shared f32->i32 BGR converter graph."""
    return {
        "src": ndarray_arg("src", ti.f32, 3),
        "dst": ndarray_arg("dst", ti.i32, 3),
        "h": scalar_arg("h", ti.i32),
        "w": scalar_arg("w", ti.i32),
    }


# ---------------------------------------------------------------------------
# Bilinear family
# ---------------------------------------------------------------------------
def register_bilinear_graphs(module, kernels):
    """Register all bilinear demosaic graphs with wrapper-exact ABI names.

    Registered graphs (must match ``aot_api.bilinear`` and ``demosaic``):
      - ``bilinear_demosaice``            (fused fast RGB)
      - ``pure_bilinear_demosaice``       (8 scalars, no cmatrix/WB)
      - ``bilinear_demosaice_1channel``   (green grayscale, dst 2D)
      - ``bilinear_demosaice_half_res``   (green half-res, dst 2D)
      - ``bilinear_demosaice_rgb_half_res`` (RGB half-res)
      - ``rgb_to_bgr_i32``                (shared converter)
    """
    s = demosaic_scalars()
    io = bilinear_io_args()
    bayer, cmatrix, dst, dst_2d = io["bayer"], io["cmatrix"], io["dst"], io["dst_2d"]
    linear = scalar_arg("linear", ti.i32)

    fast = [
        bayer, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"],
        s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
        linear,
    ]

    # 1. bilinear_demosaice (fused fast RGB, linear or gamma output)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["fast"], *fast)
    module.add_graph("bilinear_demosaice", g.compile())

    # 2. pure_bilinear_demosaice (8 scalars, no cmatrix/WB)
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["pure"],
        bayer, dst,
        s["black"], s["white"],
        s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("pure_bilinear_demosaice", g.compile())

    # 3. bilinear_demosaice_1channel (green grayscale, dst 2D)
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["gray1ch"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"],
        s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("bilinear_demosaice_1channel", g.compile())

    # 4. bilinear_demosaice_half_res (green half-res, dst 2D)
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["half_res"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"],
        s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("bilinear_demosaice_half_res", g.compile())

    # 5. bilinear_demosaice_rgb_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["rgb_half_res"],
        bayer, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"],
        s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
        linear,
    )
    module.add_graph("bilinear_demosaice_rgb_half_res", g.compile())

    # 6. rgb_to_bgr_i32 shared converter
    conv = rgb_to_bgr_i32_args()
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_to_bgr_i32"], conv["src"], conv["dst"], conv["h"], conv["w"])
    module.add_graph("rgb_to_bgr_i32", g.compile())

    return module


# ---------------------------------------------------------------------------
# Multi-pass family I/O args (hamilton / arm / mlri)
# ---------------------------------------------------------------------------
def demosaic_io_args():
    """NDArray args for the multi-pass hamilton / arm / mlri families."""
    return {
        "bayer": ndarray_arg("bayer", ti.f32, 2),
        "green": ndarray_arg("green", ti.f32, 2),
        "cmatrix": ndarray_arg("cmatrix", ti.f32, 2),
        "dst": ndarray_arg("dst", ti.f32, 3),
        "dst_2d": ndarray_arg("dst", ti.f32, 2),
        "wb_bayer": ndarray_arg("wb_bayer", ti.f32, 2),
        "r_diff": ndarray_arg("r_diff", ti.f32, 2),
        "b_diff": ndarray_arg("b_diff", ti.f32, 2),
        "r_diff_filtered": ndarray_arg("r_diff_filtered", ti.f32, 2),
        "b_diff_filtered": ndarray_arg("b_diff_filtered", ti.f32, 2),
        "temp_a": ndarray_arg("temp_a", ti.f32, 2),
        "temp_b": ndarray_arg("temp_b", ti.f32, 2),
    }


# ---------------------------------------------------------------------------
# Hamilton family
# ---------------------------------------------------------------------------
def register_hamilton_graphs(module, kernels):
    """Register Hamilton-Adams graphs with wrapper-exact ABI names.

    Graphs: ``hamilton_demosaic``, ``hamilton_demosaic_tonemapped``,
    ``rgb_to_bgr_i32``.
    """
    s = demosaic_scalars()
    io = demosaic_io_args()
    bayer, green, cmatrix, dst = io["bayer"], io["green"], io["cmatrix"], io["dst"]

    common = [
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    ]

    # 1. hamilton_demosaic (linear fast path)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["green_direct"], bayer, green, *common)
    g.dispatch(kernels["red_blue_direct"], bayer, green, dst, *common)
    module.add_graph("hamilton_demosaic", g.compile())

    # 2. hamilton_demosaic_tonemapped
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["green_direct"], bayer, green, *common)
    g.dispatch(kernels["red_blue_direct"], bayer, green, dst, *common)
    g.dispatch(kernels["srgb_tonemap"], dst, cmatrix, dst, s["h"], s["w"])
    module.add_graph("hamilton_demosaic_tonemapped", g.compile())

    # 3. hamilton_demosaic_1channel (green grayscale, dst 2D)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["green_1ch"], bayer, io["dst_2d"], *common)
    module.add_graph("hamilton_demosaic_1channel", g.compile())

    # 4. hamilton_demosaic_half_res (green half-res grayscale, dst 2D)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["green_half_res"], bayer, io["dst_2d"], *common)
    module.add_graph("hamilton_demosaic_half_res", g.compile())

    # 5. hamilton_demosaic_rgb_half_res (RGB half-res)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_half_res"], bayer, cmatrix, dst, *common)
    module.add_graph("hamilton_demosaic_rgb_half_res", g.compile())

    # 6. hamilton_demosaic_3channel (full demosaic -> grayscale luma)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["preprocess_wb"], bayer, io["wb_bayer"], *common)
    g.dispatch(kernels["green_direct"], bayer, green, *common)
    g.dispatch(kernels["grayscale"], green, io["dst_2d"], s["h"], s["w"])
    module.add_graph("hamilton_demosaic_3channel", g.compile())

    # 7. rgb_to_bgr_i32
    conv = rgb_to_bgr_i32_args()
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_to_bgr_i32"], conv["src"], conv["dst"], conv["h"], conv["w"])
    module.add_graph("rgb_to_bgr_i32", g.compile())

    return module


# ---------------------------------------------------------------------------
# ARM family
# ---------------------------------------------------------------------------
def register_arm_graphs(module, kernels):
    """Register ARM demosaic graphs with wrapper-exact ABI names."""
    s = demosaic_scalars()
    io = demosaic_io_args()
    bayer, cmatrix, dst, dst_2d = io["bayer"], io["cmatrix"], io["dst"], io["dst_2d"]
    wb_bayer, green = io["wb_bayer"], io["green"]
    r_diff, b_diff = io["r_diff"], io["b_diff"]
    r_diff_f, b_diff_f = io["r_diff_filtered"], io["b_diff_filtered"]

    # 1. arm_demosaic (5-pass fused)
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["preprocess_green"],
        bayer, wb_bayer, green,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    g.dispatch(
        kernels["red_blue_residual"],
        wb_bayer, green, r_diff, b_diff,
        s["h"], s["w"], s["c00"], s["c01"], s["c10"], s["c11"],
    )
    g.dispatch(kernels["median3x3"], r_diff, r_diff_f, s["h"], s["w"])
    g.dispatch(kernels["median3x3"], b_diff, b_diff_f, s["h"], s["w"])
    g.dispatch(
        kernels["reconstruct_postprocess"],
        green, r_diff_f, b_diff_f, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"], s["h"], s["w"],
    )
    module.add_graph("arm_demosaic", g.compile())

    # 2. arm_demosaic_tonemapped
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["preprocess_green"],
        bayer, wb_bayer, green,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    g.dispatch(
        kernels["red_blue_residual"],
        wb_bayer, green, r_diff, b_diff,
        s["h"], s["w"], s["c00"], s["c01"], s["c10"], s["c11"],
    )
    g.dispatch(kernels["median3x3"], r_diff, r_diff_f, s["h"], s["w"])
    g.dispatch(kernels["median3x3"], b_diff, b_diff_f, s["h"], s["w"])
    g.dispatch(
        kernels["reconstruct_postprocess"],
        green, r_diff_f, b_diff_f, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"], s["h"], s["w"],
    )
    g.dispatch(kernels["srgb_tonemap"], dst, cmatrix, dst, s["h"], s["w"])
    module.add_graph("arm_demosaic_tonemapped", g.compile())

    # 3. pure_arm_demosaic
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["pure"],
        bayer, dst,
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("pure_arm_demosaic", g.compile())

    # 4. arm_demosaic_1channel
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["green_1ch"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("arm_demosaic_1channel", g.compile())

    # 5. arm_demosaic_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["green_half_res"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("arm_demosaic_half_res", g.compile())

    # 6. arm_demosaic_rgb_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["rgb_half_res"],
        bayer, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    )
    module.add_graph("arm_demosaic_rgb_half_res", g.compile())

    # 7. rgb_to_bgr_i32
    conv = rgb_to_bgr_i32_args()
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_to_bgr_i32"], conv["src"], conv["dst"], conv["h"], conv["w"])
    module.add_graph("rgb_to_bgr_i32", g.compile())

    return module


# ---------------------------------------------------------------------------
# DCB family
# ---------------------------------------------------------------------------
def dcb_io_args():
    """NDArray args for the DCB family."""
    return {
        "bayer": ndarray_arg("bayer", ti.f32, 2),
        "mosaic": ndarray_arg("mosaic", ti.f32, 2),
        "green": ndarray_arg("green", ti.f32, 2),
        "rgb_a": ndarray_arg("rgb_a", ti.f32, 3),
        "rgb_b": ndarray_arg("rgb_b", ti.f32, 3),
        "dst": ndarray_arg("dst", ti.f32, 3),
        "gray": ndarray_arg("gray", ti.f32, 2),
        "cmatrix": ndarray_arg("cmatrix", ti.f32, 2),
        "ratio_src": ndarray_arg("ratio_src", ti.f32, 3),
        "ratio_dst": ndarray_arg("ratio_dst", ti.f32, 3),
        "recovered": ndarray_arg("recovered", ti.f32, 3),
    }


def register_dcb_graphs(module, kernels):
    """Register DCB demosaic graphs with wrapper-exact ABI names."""
    s = demosaic_scalars()
    io = dcb_io_args()
    bayer, mosaic, green = io["bayer"], io["mosaic"], io["green"]
    rgb_a, rgb_b, dst, gray = io["rgb_a"], io["rgb_b"], io["dst"], io["gray"]
    cmatrix = io["cmatrix"]

    common = [
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    ]
    cfa = [s["c00"], s["c01"], s["c10"], s["c11"]]
    wb = [s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"]]

    def _core(graph, preprocess_kernel):
        graph.dispatch(preprocess_kernel, bayer, mosaic, *common)
        graph.dispatch(kernels["green"], mosaic, green, s["h"], s["w"], *cfa)
        graph.dispatch(kernels["initial_rgb"], mosaic, green, rgb_a, s["h"], s["w"], *cfa)
        graph.dispatch(kernels["refine_chroma"], rgb_a, mosaic, rgb_b, s["h"], s["w"], *cfa)

    # 1. dcb_demosaic
    g = ti.graph.GraphBuilder()
    _core(g, kernels["preprocess"])
    g.dispatch(kernels["copy_rgb"], rgb_b, dst, *wb, s["h"], s["w"])
    module.add_graph("dcb_demosaic", g.compile())

    # 2. dcb_demosaic_headroom
    g = ti.graph.GraphBuilder()
    _core(g, kernels["preprocess_headroom"])
    g.dispatch(kernels["copy_rgb_headroom"], rgb_b, dst, *wb, s["h"], s["w"])
    module.add_graph("dcb_demosaic_headroom", g.compile())

    # 3. dcb_demosaic_tonemapped
    g = ti.graph.GraphBuilder()
    _core(g, kernels["preprocess"])
    g.dispatch(kernels["copy_rgb"], rgb_b, dst, *wb, s["h"], s["w"])
    g.dispatch(kernels["srgb_tonemap"], dst, cmatrix, dst, s["h"], s["w"])
    module.add_graph("dcb_demosaic_tonemapped", g.compile())

    # Highlight recovery graphs
    wb_g = scalar_arg("wb_g", ti.f32)
    map_h = scalar_arg("map_h", ti.i32)
    map_w = scalar_arg("map_w", ti.i32)
    ratio_src, ratio_dst, recovered = io["ratio_src"], io["ratio_dst"], io["recovered"]

    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["highlight_ratio_seed"],
        dst, ratio_dst, s["wb_r"], wb_g, s["wb_b"], s["h"], s["w"], map_h, map_w,
    )
    module.add_graph("dcb_highlight_ratio_seed", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["highlight_ratio_propagate"], ratio_src, ratio_dst, map_h, map_w)
    module.add_graph("dcb_highlight_ratio_propagate", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["highlight_apply"],
        dst, ratio_src, recovered, s["wb_r"], wb_g, s["wb_b"], s["h"], s["w"], map_h, map_w,
    )
    module.add_graph("dcb_highlight_apply", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["copy_rgb"], recovered, dst, *wb, s["h"], s["w"])
    module.add_graph("dcb_copy_rgb", g.compile())

    # 4. dcb_demosaic_1channel
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["green_1ch"], bayer, gray, *common)
    module.add_graph("dcb_demosaic_1channel", g.compile())

    # 5. dcb_demosaic_rgb_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_half"], bayer, dst, *common)
    module.add_graph("dcb_demosaic_rgb_half_res", g.compile())

    # 6. dcb_demosaic_half_res (rgb half + luma)
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_half"], bayer, dst, *common)
    g.dispatch(kernels["rgb_luma_half"], dst, gray, s["h"], s["w"])
    module.add_graph("dcb_demosaic_half_res", g.compile())

    # 7. dcb_rgb_to_luma
    g = ti.graph.GraphBuilder()
    g.dispatch(kernels["rgb_luma"], rgb_a, gray, s["h"], s["w"])
    module.add_graph("dcb_rgb_to_luma", g.compile())

    return module


# ---------------------------------------------------------------------------
# MLRI-ADMM family (arch-dependent dispatch)
# ---------------------------------------------------------------------------
def register_mlri_graphs(module, kernels, arch):
    """Register MLRI-ADMM graphs with wrapper-exact ABI names.

    ``arch`` selects the portable (Vulkan, 9 matrix scalars) vs the cmatrix
    ndarray reconstruction path, mirroring the original compiler.
    """
    s = demosaic_scalars()
    io = demosaic_io_args()
    bayer, wb_bayer, green = io["bayer"], io["wb_bayer"], io["green"]
    r_diff, b_diff = io["r_diff"], io["b_diff"]
    temp_a, temp_b = io["temp_a"], io["temp_b"]
    cmatrix, dst, dst_2d = io["cmatrix"], io["dst"], io["dst_2d"]

    matrix_args = [scalar_arg(f"m{r}{c}", ti.f32) for r in range(3) for c in range(3)]
    denoise_strength = scalar_arg("denoise_strength", ti.f32)
    eps = scalar_arg("eps", ti.f32)

    common = [
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"],
        s["c00"], s["c01"], s["c10"], s["c11"],
    ]
    cfa = [s["c00"], s["c01"], s["c10"], s["c11"]]

    is_vulkan = arch == ti.vulkan

    def dispatch_preprocess(graph):
        graph.dispatch(kernels["preprocess"], bayer, wb_bayer, *common)

    def dispatch_denoise_green_diff(graph):
        graph.dispatch(kernels["denoise"], wb_bayer, temp_a, s["h"], s["w"], denoise_strength)
        graph.dispatch(kernels["gbtf_green"], temp_a, green, s["h"], s["w"], *cfa)
        graph.dispatch(kernels["init_diff"], temp_a, green, r_diff, b_diff, s["h"], s["w"], *cfa)

    def dispatch_guided(graph):
        graph.dispatch(kernels["gf_coeff"], green, r_diff, temp_a, temp_b, s["h"], s["w"], eps)
        graph.dispatch(kernels["gf_apply"], green, temp_a, temp_b, r_diff, s["h"], s["w"])
        graph.dispatch(kernels["gf_coeff"], green, b_diff, temp_a, temp_b, s["h"], s["w"], eps)
        graph.dispatch(kernels["gf_apply"], green, temp_a, temp_b, b_diff, s["h"], s["w"])

    def dispatch_admm_step1(graph):
        if is_vulkan:
            graph.dispatch(kernels["admm1_red"], green, r_diff, temp_a, s["h"], s["w"])
            graph.dispatch(kernels["admm1_blue"], green, b_diff, temp_b, s["h"], s["w"])
        else:
            graph.dispatch(kernels["admm1"], green, r_diff, b_diff, temp_a, temp_b, s["h"], s["w"])

    def dispatch_admm_step2(graph):
        if is_vulkan:
            graph.dispatch(kernels["admm2_red"], wb_bayer, r_diff, temp_a, s["h"], s["w"], *cfa)
            graph.dispatch(kernels["admm2_blue"], wb_bayer, b_diff, temp_b, s["h"], s["w"], *cfa)
            graph.dispatch(kernels["admm2_green"], wb_bayer, green, s["h"], s["w"], *cfa)
        else:
            graph.dispatch(
                kernels["admm2"],
                wb_bayer, green, r_diff, b_diff, temp_a, temp_b, s["h"], s["w"], *cfa,
            )

    def dispatch_reconstruct(graph, grayscale=False):
        if is_vulkan:
            graph.dispatch(
                kernels["reconstruct_portable"] if not grayscale else kernels["gray_portable"],
                green, r_diff, b_diff,
                dst if not grayscale else dst_2d,
                *matrix_args, s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"], s["h"], s["w"],
            )
        else:
            graph.dispatch(
                kernels["reconstruct"] if not grayscale else kernels["gray"],
                green, r_diff, b_diff,
                cmatrix if not grayscale else cmatrix,
                dst if not grayscale else dst_2d,
                s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"], s["h"], s["w"],
            )

    # 1. mlri_admm_demosaic
    g = ti.graph.GraphBuilder()
    dispatch_preprocess(g)
    dispatch_denoise_green_diff(g)
    dispatch_guided(g)
    dispatch_admm_step1(g)
    dispatch_admm_step2(g)
    dispatch_reconstruct(g)
    module.add_graph("mlri_admm_demosaic", g.compile())

    # 2. mlri_admm_demosaic_tonemapped
    g = ti.graph.GraphBuilder()
    dispatch_preprocess(g)
    dispatch_denoise_green_diff(g)
    dispatch_guided(g)
    for _ in range(3):
        dispatch_admm_step1(g)
        dispatch_admm_step2(g)
    dispatch_reconstruct(g)
    g.dispatch(kernels["srgb_tonemap"], dst, cmatrix, dst, s["h"], s["w"])
    module.add_graph("mlri_admm_demosaic_tonemapped", g.compile())

    # 3. mlri_admm_demosaic_1channel
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["gray_1ch"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"], *cfa,
    )
    module.add_graph("mlri_admm_demosaic_1channel", g.compile())

    # 4. mlri_admm_demosaic_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["green_half_res"],
        bayer, dst_2d,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"], *cfa,
    )
    module.add_graph("mlri_admm_demosaic_half_res", g.compile())

    # 5. mlri_admm_demosaic_rgb_half_res
    g = ti.graph.GraphBuilder()
    g.dispatch(
        kernels["rgb_half_res"],
        bayer, cmatrix, dst,
        s["wb_r"], s["wb_g1"], s["wb_b"], s["wb_g2"],
        s["black"], s["white"], s["h"], s["w"], *cfa,
    )
    module.add_graph("mlri_admm_demosaic_rgb_half_res", g.compile())

    # 6. mlri_admm_demosaic_3channel (full grayscale)
    g = ti.graph.GraphBuilder()
    dispatch_preprocess(g)
    dispatch_denoise_green_diff(g)
    dispatch_guided(g)
    for _ in range(3):
        dispatch_admm_step1(g)
        dispatch_admm_step2(g)
    dispatch_reconstruct(g, grayscale=True)
    module.add_graph("mlri_admm_demosaic_3channel", g.compile())

    return module


# ---------------------------------------------------------------------------
# Concise multi-backend build orchestrator
# ---------------------------------------------------------------------------
import importlib
import os as _os

_TCM_DIR = _os.path.abspath(
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "aot_tcm")
)

FAMILY_COMPILER_MODULE = {
    "bilinear": "compile_bilinear_demosaice_tcm",
    "hamilton": "compile_hamilton_tcm",
    "arm": "compile_arm_tcm",
    "dcb": "compile_dcb_tcm",
    "mlri": "compile_mlri_admm_tcm",
}
FAMILY_COMPILER_FUNC = {
    "bilinear": "compile_bilinear_demosaice_tcm",
    "hamilton": "compile_hamilton_tcm",
    "arm": "compile_arm_tcm",
    "dcb": "compile_dcb_tcm",
    "mlri": "compile_mlri_admm_tcm",
}
FAMILY_ARTIFACT = {
    "bilinear": "bilinear_demosaice",
    "hamilton": "hamilton",
    "arm": "arm",
    "dcb": "dcb",
    "mlri": "mlri_admm",
}

BACKEND_ARCH = {
    "cpu": ti.cpu,
    "vulkan": ti.vulkan,
    "opengl": ti.opengl,
    "cuda": ti.cuda,
    "gles": ti.gles,
}

# backend -> default target-qualified directory under aot_tcm/
DESKTOP_TARGETS = {
    "cpu": "cpu_x86_64_windows",
    "vulkan": "vulkan_x86_64_windows",
    "opengl": "opengl_x86_64_windows_nvidia",
    "cuda": "cuda_x86_64_windows_nvidia",
}
ANDROID_TARGETS = {
    "vulkan": "vulkan_arm64_android",
    "gles": "gles_arm64_android",
}


def compile_demosaic_family(family, backend, target_id=None):
    """Compile one demosaic family for one backend into a target-qualified TCM.

    Returns the written artifact path.  ``target_id`` overrides the default
    target directory for the backend (e.g. for ARM/Android cross targets).
    """
    artifact = FAMILY_ARTIFACT[family]
    arch = BACKEND_ARCH[backend]
    target = target_id or DESKTOP_TARGETS[backend]
    save_path = _os.path.join(_TCM_DIR, target, f"{artifact}_{target}.tcm")
    _os.makedirs(_os.path.dirname(save_path), exist_ok=True)
    module_name = (
        f"taichi_vision.taichi_algorithm.demosaicing.{FAMILY_COMPILER_MODULE[family]}"
    )
    mod = importlib.import_module(module_name)
    fn = getattr(mod, FAMILY_COMPILER_FUNC[family])
    fn(arch=arch, save_path=save_path)
    return save_path


def build_demosaic_family(family, backends=("cuda", "vulkan", "opengl", "cpu")):
    """Compile one family for several backends.  Returns {backend: path}."""
    return {b: compile_demosaic_family(family, b) for b in backends}


def build_all_demosaic(
    backends=("cuda", "vulkan", "opengl", "cpu"),
    families=("bilinear", "hamilton", "arm", "dcb", "mlri"),
):
    """Compile every demosaic family for every backend (concise one-liner).

    Example: ``build_all_demosaic()`` builds bilinear/hamilton/arm/dcb/mlri
    for cuda/vulkan/opengl/cpu.
    """
    return {f: build_demosaic_family(f, backends) for f in families}


if __name__ == "__main__":
    import argparse

    _p = argparse.ArgumentParser(description="Build demosaic AOT TCMs")
    _p.add_argument(
        "--family",
        default="all",
        help="family to build: bilinear|hamilton|arm|dcb|mlri|all",
    )
    _p.add_argument(
        "--backend",
        default="cuda,vulkan,opengl,cpu",
        help="comma-separated backends to build",
    )
    _args = _p.parse_args()
    _families = (
        tuple(FAMILY_COMPILER_MODULE)
        if _args.family == "all"
        else (_args.family,)
    )
    _backends = tuple(b.strip() for b in _args.backend.split(",") if b.strip())
    _results = build_all_demosaic(_backends, _families)
    for _f, _paths in _results.items():
        for _b, _pth in _paths.items():
            print(f"[built] {_f} {_b}: {_pth}")


