"""
compile_lucas_kanade_tcm.py - AOT Compilation for Grid Lucas-Kanade Flow
=========================================================================

Graphs compiled:
  - flow_lk_zero
  - flow_lk_zero_stats
  - flow_lk_grid_track
  - flow_lk_motion_stats
  - flow_lk_adaptive_refine
  - flow_lk_dense_interpolate
  - flow_lk_dense_blocky
  - flow_lk_dense_blocky_clamped
"""

import os

os.environ["AOT_MODE"] = "0"

import sys
import taichi as ti

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

import importlib

lk = importlib.import_module("taichi_vision.taichi_algorithm.optical_flow.lucas_kanade")


def _package_tcm(module, out_dir, tcm_name):
    import shutil
    import zipfile

    tmp_dir = os.path.join(out_dir, "_tmp_lucas_kanade_aot")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    tcm_path = os.path.join(out_dir, tcm_name)
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(tmp_dir):
            for name in files:
                path = os.path.join(root, name)
                zf.write(path, os.path.relpath(path, tmp_dir))
    shutil.rmtree(tmp_dir)
    print(f"  -> {tcm_path}")
    return tcm_path


def compile_lucas_kanade_flow(arch=ti.vulkan, out_dir=None):
    print(f"\n>>> Compiling Lucas-Kanade Optical Flow AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    sym_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "prev", dtype=ti.f32, ndim=2)
    sym_next = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "next", dtype=ti.f32, ndim=2)
    sym_init_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "init_flow", dtype=ti.f32, ndim=3)
    sym_grid_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grid_flow", dtype=ti.f32, ndim=3)
    sym_grid_meta = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grid_meta", dtype=ti.f32, ndim=3)
    sym_flow_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_out", dtype=ti.f32, ndim=3)
    sym_stats = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "stats", dtype=ti.f32, ndim=1)

    sym_grid_step = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "grid_step", dtype=ti.i32)
    sym_border_margin = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "border_margin", dtype=ti.i32)
    sym_win_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "win_radius", dtype=ti.i32)
    sym_iterations = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "iterations", dtype=ti.i32)
    sym_epsilon = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "epsilon", dtype=ti.f32)
    sym_overlap = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "overlap", dtype=ti.f32)
    sym_class_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "class_threshold", dtype=ti.i32)
    sym_max_flow_px = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_flow_px", dtype=ti.f32)

    g_zero = ti.graph.GraphBuilder()
    g_zero.dispatch(lk._lk_zero_flow_kernel, sym_init_flow)
    module.add_graph("flow_lk_zero", g_zero.compile())
    print("  [OK] flow_lk_zero")

    g_zero_stats = ti.graph.GraphBuilder()
    g_zero_stats.dispatch(lk._lk_zero_stats_kernel, sym_stats)
    module.add_graph("flow_lk_zero_stats", g_zero_stats.compile())
    print("  [OK] flow_lk_zero_stats")

    g_track = ti.graph.GraphBuilder()
    g_track.dispatch(
        lk._lk_grid_track_kernel,
        sym_img,
        sym_next,
        sym_init_flow,
        sym_grid_flow,
        sym_grid_meta,
        sym_grid_step,
        sym_border_margin,
        sym_win_radius,
        sym_iterations,
        sym_epsilon,
    )
    module.add_graph("flow_lk_grid_track", g_track.compile())
    print("  [OK] flow_lk_grid_track")

    g_stats = ti.graph.GraphBuilder()
    g_stats.dispatch(
        lk._lk_motion_stats_kernel,
        sym_grid_flow,
        sym_grid_meta,
        sym_stats,
    )
    module.add_graph("flow_lk_motion_stats", g_stats.compile())
    print("  [OK] flow_lk_motion_stats")

    g_refine = ti.graph.GraphBuilder()
    g_refine.dispatch(
        lk._lk_adaptive_refine_kernel,
        sym_img,
        sym_next,
        sym_grid_flow,
        sym_grid_meta,
        sym_grid_step,
        sym_border_margin,
        sym_win_radius,
        sym_iterations,
        sym_epsilon,
        sym_class_threshold,
    )
    module.add_graph("flow_lk_adaptive_refine", g_refine.compile())
    print("  [OK] flow_lk_adaptive_refine")

    g_interp = ti.graph.GraphBuilder()
    g_interp.dispatch(
        lk._lk_dense_interpolate_kernel,
        sym_grid_flow,
        sym_flow_out,
        sym_grid_step,
        sym_border_margin,
        sym_overlap,
    )
    module.add_graph("flow_lk_dense_interpolate", g_interp.compile())
    print("  [OK] flow_lk_dense_interpolate")

    g_blocky = ti.graph.GraphBuilder()
    g_blocky.dispatch(
        lk._lk_dense_blocky_kernel,
        sym_grid_flow,
        sym_flow_out,
        sym_grid_step,
        sym_border_margin,
    )
    module.add_graph("flow_lk_dense_blocky", g_blocky.compile())
    print("  [OK] flow_lk_dense_blocky")

    g_blocky_clamped = ti.graph.GraphBuilder()
    g_blocky_clamped.dispatch(
        lk._lk_dense_blocky_clamped_kernel,
        sym_grid_flow,
        sym_flow_out,
        sym_grid_step,
        sym_border_margin,
        sym_max_flow_px,
    )
    module.add_graph("flow_lk_dense_blocky_clamped", g_blocky_clamped.compile())
    print("  [OK] flow_lk_dense_blocky_clamped")

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
    tcm_path = _package_tcm(module, out_dir, f"lucas_kanade_{arch_name}.tcm")

    ti.reset()
    print(f"Lucas-Kanade flow compiled: {tcm_path}")
    return tcm_path


if __name__ == "__main__":
    for arch, suffix in ((ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")):
        try:
            compile_lucas_kanade_flow(arch=arch)
        except Exception as exc:
            print(f"Skipping {suffix} due to error: {exc}")
