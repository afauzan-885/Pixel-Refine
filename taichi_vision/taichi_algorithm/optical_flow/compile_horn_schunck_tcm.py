"""
compile_template_flow_tcm.py Ã¢â‚¬â€ AOT Compilation for Horn-Schunck Optical Flow
=============================================================================
Compiles Horn-Schunck optical flow kernels into .tcm modules for
Vulkan / CUDA / CPU backends.

Graphs compiled:
  Big graph (in-kernel Jacobi):
    - hs_align_3layer_10  : 3-level pyramid, 10 Jacobi iters per level
    - hs_align_3layer_20  : 3-level pyramid, 20 Jacobi iters per level
    - hs_align_3layer_50  : 3-level pyramid, 50 Jacobi iters per level

  External dispatch (for parity testing against OpenCV):
    - hs_gradients        : Compute Ix, Iy, It
    - hs_jacobi_step      : Single Jacobi iteration (dispatch N times externally)
    - hs_clear_flow       : Zero-init flow field
    - hs_copy_flow        : Copy flow buffer
    - hs_upsample_flow    : Bicubic flow upsampling

Usage:
    python compile_template_flow_tcm.py
"""

import argparse
import os

os.environ["AOT_MODE"] = "0"

import taichi as ti
import numpy as np
import sys

# Add project root to sys.path
file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_vision.taichi_algorithm.optical_flow import horn_schunck as tf

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import normalize_tcm
except ImportError:  # Direct script execution.
    from aot_artifact import normalize_tcm


def _package_tcm(module, out_dir, tcm_name):
    """Save AOT module and package as .tcm (zip)."""
    import shutil, zipfile

    tmp_dir = os.path.join(out_dir, "_tmp_hs_aot")
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    tcm_path = os.path.join(out_dir, tcm_name)
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(tmp_dir):
            for f in files:
                zf.write(
                    os.path.join(root, f),
                    os.path.relpath(os.path.join(root, f), tmp_dir),
                )
    shutil.rmtree(tmp_dir)
    normalize_tcm(tcm_path)
    # template_flow was the original deployment name. It has exactly the same
    # graph interface as horn_schunck and remains an API-compatible alias.
    if tcm_name.startswith("horn_schunck_"):
        legacy_path = os.path.join(out_dir, tcm_name.replace("horn_schunck_", "template_flow_", 1))
        shutil.copy2(tcm_path, legacy_path)
    print(f"  -> {tcm_path}")
    return tcm_path


def compile_horn_schunck_flow(arch=ti.vulkan, out_dir=None):
    """Compile Horn-Schunck optical flow for the given architecture.

    Big Graph: hs_align_3layer_{N}
        5-step pipeline:
          1. _hs_coarsest_level_kernel (gradient + zero-init + N Jacobi)
          2. _upsample_flow_bicubic_kernel (L2 Ã¢â€ â€™ L1)
          3. _hs_refinement_level_kernel (gradient + project + N Jacobi)
          4. _upsample_flow_bicubic_kernel (L1 Ã¢â€ â€™ L0)
          5. _hs_refinement_level_kernel (gradient + project + N Jacobi)

    Graph Arguments:
        - ref_l0, ref_l1, ref_l2: Reference images at 3 pyramid levels (NDARRAY, f32, ndim=2)
        - comp_l0, comp_l1, comp_l2: Comparison images at 3 pyramid levels (NDARRAY, f32, ndim=2)
        - flow_l0, flow_l1, flow_l2: Flow fields at 3 pyramid levels (NDARRAY, f32, ndim=3)
        - flow_temp_l0, flow_temp_l1, flow_temp_l2: Temp flow buffers (NDARRAY, f32, ndim=3)
        - alpha: Smoothness weight (SCALAR, f32)
        - num_iters: Jacobi iterations per level (SCALAR, i32)
        - scale: Pyramid scale factor (SCALAR, f32, typically 2.0)
        - downscale: Level-to-level scale ratio (SCALAR, i32, typically 2)
    """
    print(f"\n>>> Compiling Horn-Schunck Optical Flow AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # ----- Symbolic arguments -----
    sym_ref_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l0", dtype=ti.f32, ndim=2)
    sym_ref_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l1", dtype=ti.f32, ndim=2)
    sym_ref_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l2", dtype=ti.f32, ndim=2)

    sym_comp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l0", dtype=ti.f32, ndim=2)
    sym_comp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l1", dtype=ti.f32, ndim=2)
    sym_comp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l2", dtype=ti.f32, ndim=2)

    sym_flow_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l0", dtype=ti.f32, ndim=3)
    sym_flow_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l1", dtype=ti.f32, ndim=3)
    sym_flow_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l2", dtype=ti.f32, ndim=3)

    sym_flow_temp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_temp_l0", dtype=ti.f32, ndim=3)
    sym_flow_temp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_temp_l1", dtype=ti.f32, ndim=3)
    sym_flow_temp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_temp_l2", dtype=ti.f32, ndim=3)

    sym_alpha = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "alpha", dtype=ti.f32)
    sym_num_iters = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_iters", dtype=ti.i32)
    sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32)
    sym_downscale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "downscale", dtype=ti.i32)

    # ===================================================================
    # BIG GRAPH: hs_align_3layer_{N} (for N = 10, 20, 50)
    # ===================================================================
    for N in (10, 20, 50):
        g = ti.graph.GraphBuilder()

        # Step 1: Coarsest level (L2) Ã¢â‚¬â€ gradient + zero-init + N Jacobi
        g.dispatch(
            tf._hs_coarsest_level_kernel,
            sym_ref_l2, sym_comp_l2,
            sym_flow_l2, sym_flow_temp_l2,
            sym_alpha, sym_num_iters,
        )

        # Step 2: Upsample flow from L2 to L1
        g.dispatch(
            tf._upsample_flow_bicubic_kernel,
            sym_flow_l2, sym_flow_l1, sym_scale,
        )

        # Step 3: Refinement at L1 Ã¢â‚¬â€ gradient + project + N Jacobi
        g.dispatch(
            tf._hs_refinement_level_kernel,
            sym_ref_l1, sym_comp_l1,
            sym_flow_l1, sym_flow_temp_l1,
            sym_flow_l2,
            sym_alpha, sym_num_iters, sym_downscale,
        )

        # Step 4: Upsample flow from L1 to L0
        g.dispatch(
            tf._upsample_flow_bicubic_kernel,
            sym_flow_l1, sym_flow_l0, sym_scale,
        )

        # Step 5: Refinement at L0 Ã¢â‚¬â€ gradient + project + N Jacobi
        g.dispatch(
            tf._hs_refinement_level_kernel,
            sym_ref_l0, sym_comp_l0,
            sym_flow_l0, sym_flow_temp_l0,
            sym_flow_l1,
            sym_alpha, sym_num_iters, sym_downscale,
        )

        graph_name = f"hs_align_3layer_{N}"
        module.add_graph(graph_name, g.compile())
        print(f"  [OK] {graph_name}")

    # ===================================================================
    # EXTERNAL DISPATCH GRAPHS (for parity testing against OpenCV)
    # ===================================================================

    # --- hs_gradients ---
    sym_Ix = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "Ix", dtype=ti.f32, ndim=2)
    sym_Iy = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "Iy", dtype=ti.f32, ndim=2)
    sym_It = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "It", dtype=ti.f32, ndim=2)
    sym_ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", dtype=ti.f32, ndim=2)
    sym_comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", dtype=ti.f32, ndim=2)

    g_grad = ti.graph.GraphBuilder()
    g_grad.dispatch(tf._hs_compute_gradients_kernel, sym_ref, sym_comp, sym_Ix, sym_Iy, sym_It)
    module.add_graph("hs_gradients", g_grad.compile())
    print("  [OK] hs_gradients")

    # --- hs_jacobi_step ---
    sym_flow_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_src", dtype=ti.f32, ndim=3)
    sym_flow_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_dst", dtype=ti.f32, ndim=3)

    g_jacobi = ti.graph.GraphBuilder()
    g_jacobi.dispatch(
        tf._hs_jacobi_step_kernel,
        sym_Ix, sym_Iy, sym_It,
        sym_flow_src, sym_flow_dst,
        sym_alpha,
    )
    module.add_graph("hs_jacobi_step", g_jacobi.compile())
    print("  [OK] hs_jacobi_step")

    # --- hs_clear_flow ---
    sym_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", dtype=ti.f32, ndim=3)

    g_clear = ti.graph.GraphBuilder()
    g_clear.dispatch(tf._hs_clear_flow_kernel, sym_flow)
    module.add_graph("hs_clear_flow", g_clear.compile())
    print("  [OK] hs_clear_flow")

    # --- hs_copy_flow ---
    g_copy = ti.graph.GraphBuilder()
    g_copy.dispatch(tf._hs_copy_flow_kernel, sym_flow_src, sym_flow_dst)
    module.add_graph("hs_copy_flow", g_copy.compile())
    print("  [OK] hs_copy_flow")

    # --- hs_upsample_flow ---
    sym_flow_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_coarse", dtype=ti.f32, ndim=3)
    sym_flow_fine = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_fine", dtype=ti.f32, ndim=3)

    g_up = ti.graph.GraphBuilder()
    g_up.dispatch(tf._upsample_flow_bicubic_kernel, sym_flow_coarse, sym_flow_fine, sym_scale)
    module.add_graph("hs_upsample_flow", g_up.compile())
    print("  [OK] hs_upsample_flow")

    # ===================================================================
    # SAVE
    # ===================================================================
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
    tcm_name = f"horn_schunck_{arch_name}.tcm"
    tcm_path = _package_tcm(module, out_dir, tcm_name)

    ti.reset()
    print(f"Horn-Schunck flow compiled: {tcm_path}")
    return tcm_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile Horn-Schunck flow AOT modules")
    parser.add_argument(
        "--backend",
        action="append",
        choices=("cpu", "vulkan", "opengl", "gles", "cuda"),
        help="Backend to compile; may be supplied more than once (default: all)",
    )
    arches = {
        "cpu": ti.cpu,
        "vulkan": ti.vulkan,
        "opengl": ti.opengl,
        "gles": ti.gles,
        "cuda": ti.cuda,
    }
    for suffix in parser.parse_args().backend or ["vulkan", "cuda", "cpu"]:
        try:
            compile_horn_schunck_flow(arch=arches[suffix])
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
