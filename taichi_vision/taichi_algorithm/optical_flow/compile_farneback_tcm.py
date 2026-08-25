"""
compile_farneback_tcm.py Ã¢â‚¬â€ AOT Compilation for Farneback Optical Flow
=====================================================================
Compiles Farneback GPU kernels into .tcm modules for Vulkan / CUDA / CPU.

Graphs compiled:
  - poly_expansion_f32      : vertical + horizontal polynomial expansion
  - farneback_iteration     : single iteration (tensors Ã¢â€ â€™ blur Ã¢â€ â€™ solve)
  - farneback_multi_2/3/5   : batched N iterations in one dispatch
  - farneback_upsample_flow : bicubic flow upsampling (reuses pyramid kernel)
  - farneback_clear_flow    : zero-initialize flow field

Usage:
    python compile_farneback_tcm.py
"""

import os

os.environ.setdefault("AOT_MODE", "0")
os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

import taichi as ti
import numpy as np
import sys

# Add project root to sys.path
file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

import importlib
fb = importlib.import_module('taichi_vision.taichi_algorithm.optical_flow.farneback_flow')
pyr = importlib.import_module('taichi_vision.taichi_algorithm.pyramid.pyramid')


def _package_tcm(module, out_dir, tcm_name):
    """Save AOT module and package as .tcm (zip)."""
    import shutil, zipfile

    tmp_dir = os.path.join(out_dir, "_tmp_farneback_aot")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    tcm_path = os.path.join(out_dir, tcm_name)
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), tmp_dir))
    shutil.rmtree(tmp_dir)
    print(f"  -> {tcm_path}")
    return tcm_path


def compile_farneback_flow(arch=ti.vulkan, out_dir=None):
    """Compile all Farneback flow graphs for the given architecture."""
    print(f"\n>>> Compiling Farneback Optical Flow AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # ----- Symbolic arguments -----
    sym_src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype=ti.f32, ndim=2)
    sym_vert_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "vert", dtype=ti.f32, ndim=3)
    sym_poly_5ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "poly", dtype=ti.f32, ndim=3)
    sym_R0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "R0", dtype=ti.f32, ndim=3)
    sym_R1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "R1", dtype=ti.f32, ndim=3)
    sym_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", dtype=ti.f32, ndim=3)
    sym_M = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "M", dtype=ti.f32, ndim=3)
    sym_M_smooth = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "M_smooth", dtype=ti.f32, ndim=3)

    sym_poly_weights = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "poly_weights", dtype=ti.f32, ndim=2
    )
    sym_smooth_weights = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "smooth_weights", dtype=ti.f32, ndim=1)

    sym_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)
    sym_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", dtype=ti.i32)
    sym_smooth_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "smooth_radius", dtype=ti.i32)
    sym_poly_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "poly_radius", dtype=ti.i32)

    sym_ig11 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ig11", dtype=ti.f32)
    sym_ig03 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ig03", dtype=ti.f32)
    sym_ig33 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ig33", dtype=ti.f32)
    sym_ig55 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ig55", dtype=ti.f32)

    sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32)

    # ----- 1. Poly Expansion (vertical + horizontal) -----
    g_poly = ti.graph.GraphBuilder()
    g_poly.dispatch(fb._poly_exp_vertical_kernel,
                    sym_src_2d, sym_vert_3d, sym_h, sym_w,
                    sym_poly_weights, sym_poly_radius)
    g_poly.dispatch(fb._poly_exp_horizontal_kernel,
                    sym_vert_3d, sym_poly_5ch, sym_h, sym_w,
                    sym_poly_weights,
                    sym_ig11, sym_ig03, sym_ig33, sym_ig55, sym_poly_radius)
    module.add_graph("poly_expansion_f32", g_poly.compile())
    print("  [OK] poly_expansion_f32")

    # ----- 2. Single iteration -----
    def _add_iteration(builder):
        builder.dispatch(fb._compute_tensors_kernel,
                         sym_R0, sym_R1, sym_flow, sym_M, sym_h, sym_w)
        builder.dispatch(fb._gaussian_blur_x_5ch_kernel,
                         sym_M, sym_M_smooth, sym_h, sym_w,
                         sym_smooth_weights, sym_smooth_radius)
        builder.dispatch(fb._gaussian_blur_y_5ch_kernel,
                         sym_M_smooth, sym_M, sym_h, sym_w,
                         sym_smooth_weights, sym_smooth_radius)
        builder.dispatch(fb._update_flow_kernel,
                         sym_M, sym_flow, sym_h, sym_w)

    g_iter = ti.graph.GraphBuilder()
    _add_iteration(g_iter)
    module.add_graph("farneback_iteration", g_iter.compile())
    print("  [OK] farneback_iteration")

    # ----- 3. Batched multi-iteration graphs -----
    for n in (2, 3, 5):
        g_multi = ti.graph.GraphBuilder()
        for _ in range(n):
            _add_iteration(g_multi)
        module.add_graph(f"farneback_multi_{n}", g_multi.compile())
        print(f"  [OK] farneback_multi_{n}")

    # ----- 4. Upsample flow (reuse pyramid kernel) -----
    sym_flow_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_coarse", dtype=ti.f32, ndim=3)
    sym_flow_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_fine", dtype=ti.f32, ndim=3)
    g_up = ti.graph.GraphBuilder()
    g_up.dispatch(pyr._upsample_flow_kernel, sym_flow_src, sym_flow_dst, sym_scale)
    module.add_graph("farneback_upsample_flow", g_up.compile())
    print("  [OK] farneback_upsample_flow")

    # ----- 5. Clear flow -----
    g_clear = ti.graph.GraphBuilder()
    g_clear.dispatch(fb._clear_flow_kernel, sym_flow)
    module.add_graph("farneback_clear_flow", g_clear.compile())
    print("  [OK] farneback_clear_flow")

    # ----- 6. Median Filter Flow -----
    g_median = ti.graph.GraphBuilder()
    g_median.dispatch(fb._median_filter_flow_kernel, sym_flow_src, sym_flow_dst, sym_h, sym_w)
    module.add_graph("farneback_median_filter", g_median.compile())
    print("  [OK] farneback_median_filter")

    # ----- 7. Copy Flow -----
    g_copy = ti.graph.GraphBuilder()
    g_copy.dispatch(fb._copy_flow_kernel, sym_flow_src, sym_flow_dst, sym_h, sym_w)
    module.add_graph("farneback_copy_flow", g_copy.compile())
    print("  [OK] farneback_copy_flow")

    # ----- Save -----
    if out_dir is None:
        out_dir = os.path.join(file_dir, "..", "aot_tcm")
    os.makedirs(out_dir, exist_ok=True)

    arch_name = {
        ti.vulkan: "vulkan",
        ti.cuda: "cuda",
        ti.cpu: "cpu",
        ti.opengl: "opengl",
        ti.gles: "gles",
    }.get(arch, str(arch))
    tcm_name = f"farneback_flow_{arch_name}.tcm"
    tcm_path = _package_tcm(module, out_dir, tcm_name)

    ti.reset()
    print(f"Farneback flow compiled: {tcm_path}")
    return tcm_path


if __name__ == "__main__":
    requested_arch = os.environ.get("PIXEL_REFINE_AOT_ARCH", "").strip().lower()
    supported_archs = {
        "vulkan": ti.vulkan,
        "cuda": ti.cuda,
        "cpu": ti.cpu,
        "opengl": ti.opengl,
        "gles": ti.gles,
    }
    if requested_arch:
        if requested_arch not in supported_archs:
            raise ValueError(
                "PIXEL_REFINE_AOT_ARCH must be one of: "
                + ", ".join(sorted(supported_archs))
            )
        archs = [(supported_archs[requested_arch], requested_arch)]
    else:
        archs = [
            (ti.vulkan, "vulkan"),
            (ti.cuda, "cuda"),
            (ti.cpu, "cpu"),
        ]
    for arch, suffix in archs:
        try:
            compile_farneback_flow(arch=arch)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
