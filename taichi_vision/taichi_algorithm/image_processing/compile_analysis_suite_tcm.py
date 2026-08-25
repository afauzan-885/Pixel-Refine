"""
Compile Analysis Suite TCM — Color Convert, Otsu, CLAHE, Canny, Hough, Guided Filter
======================================================================================
AOT compilation script for the image analysis suite Taichi algorithm modules.
Algorithms with ti.template() (NLM) or dynamic kernel defs (Inpaint, Seamless Clone)
are JIT-only and tested via subprocess with AOT_MODE=0.

Usage:
  python compile_analysis_suite_tcm.py           # Compile target-qualified desktop defaults
  set PIXEL_REFINE_AOT_ARCH=vulkan && python ... # Compile vulkan only
  set PIXEL_REFINE_AOT_ARCH=gles && set PIXEL_REFINE_TARGET_VARIANT=gles_arm64_android && python ...

The output is always placed below ``aot_tcm/<target-id>/``.  Set
``PIXEL_REFINE_TARGET_VARIANT`` when producing a vendor/ABI-specific profile
(for example ``opengl_x86_64_windows_intel``); this prevents the old
``<name>_<backend>.tcm`` files from being recreated.
"""
import os
os.environ["AOT_MODE"] = "0"
# The analysis compiler must own Taichi's graphics context.  If the Pixel
# Refine AOT bridge initializes first, Taichi may fail to create an OpenGL
# compiler context and silently fall back to CPU while still writing an
# ``*_opengl.tcm`` filename.  Keep this suite native by default.
os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

import taichi as ti
import sys
import importlib

# Keep compiler outputs and shared AOT helpers in the canonical locations even
# though this family-local compiler lives next to the image-processing kernels.
file_dir = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py")
)
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import algorithm modules (JIT mode)
color_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.color_convert")
otsu_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.otsu")
clahe_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.clahe")
canny_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.canny")
hough_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.hough")
gf_mod = importlib.import_module("taichi_vision.taichi_algorithm.smoothing.guided_filter")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def _target_id_for_suffix(suffix):
    """Return the canonical artifact directory for one compiler backend."""

    override = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
    if override:
        return override
    defaults = {
        "cpu": "cpu_x86_64_windows" if os.name == "nt" else "cpu_x86_64_linux",
        "cuda": "cuda_x86_64_windows_nvidia" if os.name == "nt" else "cuda_arm64_linux_nvidia",
        "vulkan": "vulkan_x86_64_windows" if os.name == "nt" else "vulkan_x86_64_linux",
        "opengl": "opengl_x86_64_windows" if os.name == "nt" else "opengl_x86_64_linux",
        "gles": "gles_arm64_android" if os.name == "nt" else "gles_arm64_linux",
    }
    try:
        return defaults[suffix]
    except KeyError as exc:
        raise ValueError(f"Unsupported analysis compiler backend: {suffix!r}") from exc


def compile_color_convert(arch, save_path):
    """Compile 6 color conversion kernels."""
    print(f"\n>>> Compiling COLOR_CONVERT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    # BGR <-> HSV
    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._bgr2hsv_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("bgr2hsv_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._hsv2bgr_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("hsv2bgr_f32", g.compile())

    # BGR <-> YCrCb
    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._bgr2ycrcb_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("bgr2ycrcb_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._ycrcb2bgr_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("ycrcb2bgr_f32", g.compile())

    # BGR <-> LAB
    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._bgr2lab_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("bgr2lab_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(color_mod._lab2bgr_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("lab2bgr_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


def compile_otsu(arch, save_path):
    """Compile Otsu histogram + threshold kernels."""
    print(f"\n>>> Compiling OTSU for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    hist_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hist", ti.i32, ndim=1)
    thresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    maxval_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_val", ti.f32)
    type_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "thresh_type", ti.i32)
    num_bins_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_bins", ti.i32)

    # Histogram kernel (with max_val, num_bins for 16-bit support)
    g = ti.graph.GraphBuilder()
    g.dispatch(otsu_mod._compute_histogram_kernel, src_2d, hist_1d, h_arg, w_arg, maxval_arg, num_bins_arg)
    module.add_graph("otsu_histogram_f32", g.compile())

    # Threshold kernel
    g = ti.graph.GraphBuilder()
    g.dispatch(otsu_mod._threshold_kernel, src_2d, dst_2d, thresh_arg, maxval_arg, type_arg, h_arg, w_arg)
    module.add_graph("otsu_threshold_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


def compile_clahe(arch, save_path):
    """Compile CLAHE 3-stage pipeline."""
    print(f"\n>>> Compiling CLAHE for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    tile_h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
    tile_w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
    tiles_x_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tiles_x", ti.i32)
    tiles_y_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tiles_y", ti.i32)
    total_tiles_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "total_tiles", ti.i32)
    num_bins_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_bins", ti.i32)
    clip_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "clip_limit", ti.i32)
    tile_px_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_pixels", ti.i32)
    max_val_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_val", ti.f32)

    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    hist_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hist", ti.i32, ndim=2)
    lut_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "lut", ti.f32, ndim=2)

    # Full CLAHE pipeline as single graph
    g = ti.graph.GraphBuilder()
    g.dispatch(clahe_mod._clahe_histogram_kernel, src_2d, hist_2d, h_arg, w_arg, tile_h_arg, tile_w_arg, tiles_x_arg, tiles_y_arg, max_val_arg, num_bins_arg)
    g.dispatch(clahe_mod._clahe_clip_cdf_kernel, hist_2d, lut_2d, total_tiles_arg, num_bins_arg, clip_arg, tile_px_arg)
    g.dispatch(clahe_mod._clahe_interpolate_kernel, src_2d, lut_2d, dst_2d, h_arg, w_arg, tile_h_arg, tile_w_arg, tiles_x_arg, tiles_y_arg, max_val_arg, num_bins_arg)
    module.add_graph("clahe_pipeline_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


def compile_canny(arch, save_path):
    """Compile Canny edge detector kernels."""
    print(f"\n>>> Compiling CANNY for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    low_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "low_thresh", ti.f32)
    high_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "high_thresh", ti.f32)

    gx_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "gx", ti.f32, ndim=2)
    gy_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "gy", ti.f32, ndim=2)
    mag_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mag", ti.f32, ndim=2)
    nms_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "nms", ti.f32, ndim=2)
    edges_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "edges", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    changed_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "changed", ti.i32, ndim=1)

    # Keep magnitude and NMS as separate dispatches. NMS depends on complete
    # neighbouring magnitudes and cannot safely share a GPU kernel with them.
    g = ti.graph.GraphBuilder()
    g.dispatch(canny_mod._canny_magnitude_kernel, gx_2d, gy_2d, mag_2d, h_arg, w_arg)
    module.add_graph("canny_magnitude_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(canny_mod._canny_nms_kernel, gx_2d, gy_2d, mag_2d, nms_2d, h_arg, w_arg)
    module.add_graph("canny_nms_f32", g.compile())

    # Threshold
    g = ti.graph.GraphBuilder()
    g.dispatch(canny_mod._canny_threshold_kernel, nms_2d, edges_2d, low_arg, high_arg, h_arg, w_arg)
    module.add_graph("canny_threshold_f32", g.compile())

    # Hysteresis step
    g = ti.graph.GraphBuilder()
    g.dispatch(canny_mod._canny_hysteresis_kernel, edges_2d, changed_1d, h_arg, w_arg)
    module.add_graph("canny_hysteresis_f32", g.compile())

    # Finalize
    g = ti.graph.GraphBuilder()
    g.dispatch(canny_mod._canny_finalize_kernel, edges_2d, dst_2d, h_arg, w_arg)
    module.add_graph("canny_finalize_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


def compile_hough(arch, save_path):
    """Compile Hough Line Transform kernels."""
    print(f"\n>>> Compiling HOUGH for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    num_theta_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_theta", ti.i32)
    rho_offset_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "rho_offset", ti.i32)
    edge_thresh_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "edge_threshold", ti.f32)
    num_rho_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_rho", ti.i32)
    threshold_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.i32)
    nms_r_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "nms_radius", ti.i32)
    max_peaks_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_peaks", ti.i32)

    edges_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "edges", ti.f32, ndim=2)
    acc_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accumulator", ti.i32, ndim=2)
    cos_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cos_table", ti.f32, ndim=1)
    sin_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sin_table", ti.f32, ndim=1)
    peaks_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "peaks", ti.f32, ndim=2)
    count_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "peak_count", ti.i32, ndim=1)

    # Vote
    g = ti.graph.GraphBuilder()
    g.dispatch(hough_mod._hough_vote_kernel, edges_2d, acc_2d, cos_1d, sin_1d,
               h_arg, w_arg, num_theta_arg, rho_offset_arg, edge_thresh_arg)
    module.add_graph("hough_vote_f32", g.compile())

    # Peaks
    g = ti.graph.GraphBuilder()
    g.dispatch(hough_mod._hough_peaks_kernel, acc_2d, peaks_2d, count_1d,
               num_rho_arg, num_theta_arg, threshold_arg, nms_r_arg, max_peaks_arg)
    module.add_graph("hough_peaks_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


def compile_guided_filter(arch, save_path):
    """Compile Guided Filter element-wise kernels."""
    print(f"\n>>> Compiling GUIDED_FILTER for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    eps_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "epsilon", ti.f32)

    a_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "a", ti.f32, ndim=2)
    b_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)

    # Element-wise multiply
    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_mul_kernel, a_2d, b_2d, dst_2d, h_arg, w_arg)
    module.add_graph("gf_mul_f32", g.compile())

    # Compute var + cov
    mean_I_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_I", ti.f32, ndim=2)
    mean_p_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_p", ti.f32, ndim=2)
    mean_II_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_II", ti.f32, ndim=2)
    mean_Ip_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_Ip", ti.f32, ndim=2)
    var_I_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "var_I", ti.f32, ndim=2)
    cov_Ip_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cov_Ip", ti.f32, ndim=2)

    if arch != ti.vulkan:
        g = ti.graph.GraphBuilder()
        g.dispatch(gf_mod._gf_compute_var_cov_kernel, mean_I_2d, mean_p_2d, mean_II_2d, mean_Ip_2d, var_I_2d, cov_Ip_2d, h_arg, w_arg)
        module.add_graph("gf_var_cov_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_compute_var_kernel, mean_I_2d, mean_II_2d,
               var_I_2d, h_arg, w_arg)
    module.add_graph("gf_var_portable_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_compute_cov_kernel, mean_I_2d, mean_p_2d,
               mean_Ip_2d, cov_Ip_2d, h_arg, w_arg)
    module.add_graph("gf_cov_portable_f32", g.compile())

    # Compute a, b coefficients
    if arch != ti.vulkan:
        g = ti.graph.GraphBuilder()
        g.dispatch(gf_mod._gf_compute_ab_kernel, var_I_2d, cov_Ip_2d, mean_I_2d, mean_p_2d, a_2d, b_2d, eps_arg, h_arg, w_arg)
        module.add_graph("gf_ab_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_compute_a_kernel, var_I_2d, cov_Ip_2d, a_2d,
               eps_arg, h_arg, w_arg)
    module.add_graph("gf_a_portable_f32", g.compile())

    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_compute_b_kernel, mean_I_2d, mean_p_2d, a_2d,
               b_2d, h_arg, w_arg)
    module.add_graph("gf_b_portable_f32", g.compile())

    # Final output
    mean_a_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_a", ti.f32, ndim=2)
    mean_b_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_b", ti.f32, ndim=2)
    I_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "I", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(gf_mod._gf_output_kernel, mean_a_2d, mean_b_2d, I_2d, dst_2d, h_arg, w_arg)
    module.add_graph("gf_output_f32", g.compile())

    # The public AOT guided-filter API is one-channel. Legacy RGB graphs are
    # retained for CPU/OpenGL archives, but excluded from Vulkan because their
    # 16-SSBO signature needlessly rejects older Intel descriptor limits.
    if arch != ti.vulkan:
        src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
        guide_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", ti.f32, ndim=2)
        Ip0_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_Ip0", ti.f32, ndim=2)
        Ip1_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_Ip1", ti.f32, ndim=2)
        Ip2_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_Ip2", ti.f32, ndim=2)

        g = ti.graph.GraphBuilder()
        g.dispatch(gf_mod._gf_mul_3ch_kernel, src_3d, guide_2d, Ip0_2d, Ip1_2d, Ip2_2d, h_arg, w_arg)
        module.add_graph("gf_mul_3ch_f32", g.compile())

        mp0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_p0", ti.f32, ndim=2)
        mp1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_p1", ti.f32, ndim=2)
        mp2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_p2", ti.f32, ndim=2)
        mIp0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_Ip0", ti.f32, ndim=2)
        mIp1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_Ip1", ti.f32, ndim=2)
        mIp2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_Ip2", ti.f32, ndim=2)
        a0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "a0", ti.f32, ndim=2)
        a1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "a1", ti.f32, ndim=2)
        a2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "a2", ti.f32, ndim=2)
        b0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b0", ti.f32, ndim=2)
        b1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b1", ti.f32, ndim=2)
        b2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b2", ti.f32, ndim=2)

        g = ti.graph.GraphBuilder()
        g.dispatch(gf_mod._gf_compute_ab_3ch_kernel, var_I_2d, mean_I_2d,
                   mp0, mp1, mp2, mIp0, mIp1, mIp2,
                   a0, a1, a2, b0, b1, b2, eps_arg, h_arg, w_arg)
        module.add_graph("gf_ab_3ch_f32", g.compile())

        ma0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_a0", ti.f32, ndim=2)
        ma1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_a1", ti.f32, ndim=2)
        ma2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_a2", ti.f32, ndim=2)
        mb0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_b0", ti.f32, ndim=2)
        mb1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_b1", ti.f32, ndim=2)
        mb2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_b2", ti.f32, ndim=2)
        dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

        g = ti.graph.GraphBuilder()
        g.dispatch(gf_mod._gf_output_3ch_kernel, ma0, ma1, ma2, mb0, mb1, mb2, I_2d, dst_3d, h_arg, w_arg)
        module.add_graph("gf_output_3ch_f32", g.compile())

    module.archive(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # Determine which backends to compile
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "all").lower()
    if arch_str == "vulkan":
        archs = [(ti.vulkan, "vulkan")]
    elif arch_str == "opengl":
        archs = [(ti.opengl, "opengl")]
    elif arch_str == "gles":
        # GLES is a distinct Taichi architecture.  Do not compile desktop GL
        # and relabel it for Android: the shader/context capability contract
        # differs even when both archives contain SPIR-V.
        archs = [(ti.gles, "gles")]
    elif arch_str == "cuda":
        archs = [(ti.cuda, "cuda")]
    elif arch_str == "cpu":
        archs = [(ti.cpu, "cpu")]
    else:
        # ``all`` means every desktop backend supported by this compiler
        # suite.  OpenGL was historically omitted even though every analysis
        # graph has a target-qualified OpenGL artifact and the runtime can
        # execute it natively.  Keep GLES explicit: it is a mobile ABI and
        # must be compiled with an Android/GLES target profile rather than
        # being inferred from a desktop host.
        archs = [
            (ti.vulkan, "vulkan"),
            (ti.opengl, "opengl"),
            (ti.cuda, "cuda"),
            (ti.cpu, "cpu"),
        ]

    compilers = [
        ("color_convert", compile_color_convert),
        ("otsu", compile_otsu),
        ("clahe", compile_clahe),
        ("canny", compile_canny),
        ("hough", compile_hough),
        ("guided_filter", compile_guided_filter),
    ]

    results = []
    for name, func in compilers:
        for arch, suffix in archs:
            target_id = _target_id_for_suffix(suffix)
            target_dir = os.path.join(ASSETS_DIR, target_id)
            os.makedirs(target_dir, exist_ok=True)
            save_path = os.path.join(target_dir, f"{name}_{target_id}.tcm")
            try:
                func(arch, save_path)
                results.append(f"[PASS] {name}_{target_id}")
            except Exception as e:
                print(f"[FAIL] {name}_{target_id}: {e}")
                results.append(f"[FAIL] {name}_{target_id}: {e}")

    print("\n" + "=" * 60)
    print(" COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
