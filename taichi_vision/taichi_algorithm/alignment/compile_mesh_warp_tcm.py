"""Compile APAP Sparse Mesh Grid Warp Kernel into Taichi AOT TCM Modules.

Generates pre-compiled .tcm artifacts for Vulkan, CPU, OpenGL, and CUDA backends,
enabling fast offline loading in the Taichi AOT runtime without runtime JIT compilation.
"""

import os
os.environ["AOT_MODE"] = "0"

import sys
import taichi as ti

# Ensure project root is in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from taichi_vision.taichi_algorithm.alignment.mesh_warp import (
    _sparse_mesh_warp_2d_kernel,
    _sparse_mesh_warp_3d_kernel,
    _adaptive_refine_2d_kernel,
)
from taichi_vision.taichi_algorithm.alignment.apap import (
    NATIVE_TPS_ITERATION_BUCKETS,
    _build_tps_system_kernel,
    _fit_apap_weighted_nodes_kernel,
    _initialize_tps_minres_kernel,
    _map_apap_points_kernel,
    _map_tps_points_kernel,
    _tps_minres_step_kernel,
)
from taichi_vision.taichi_aot.artifact_targets import detect_target
from taichi_vision.taichi_aot.tcm_contract import (
    attach_manifest,
    build_manifest_from_archive,
)

AOT_TCM_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "aot_tcm"))


def compile_mesh_warp_aot(arch, save_path: str):
    """Compile sparse mesh warping and adaptive refine kernels into an AOT TCM module."""
    print(f"\n>>> Compiling APAP Sparse Mesh Warp AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # 1. 2D Graph (Grayscale / Burst Alignment)
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    mesh_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mesh", ti.types.vector(2, ti.f32), ndim=2)
    u_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "u_grid", ti.f32, ndim=1)
    v_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "v_grid", ti.f32, ndim=1)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    wsf = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src_f", ti.f32)
    hsf = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src_f", ti.f32)
    wmm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_mesh_max", ti.i32)
    hmm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_mesh_max", ti.i32)
    wsm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src_max", ti.i32)
    hsm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src_max", ti.i32)

    g2 = ti.graph.GraphBuilder()
    g2.dispatch(
        _sparse_mesh_warp_2d_kernel,
        src_2d,
        mesh_arg,
        u_arg,
        v_arg,
        dst_2d,
        wsf,
        hsf,
        wmm,
        hmm,
        wsm,
        hsm,
    )
    module.add_graph("sparse_mesh_warp_2d_f32", g2.compile())

    # 2. 3D Graph (Color RGB Panorama Alignment)
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)

    g3 = ti.graph.GraphBuilder()
    g3.dispatch(
        _sparse_mesh_warp_3d_kernel,
        src_3d,
        mesh_arg,
        u_arg,
        v_arg,
        dst_3d,
        wsf,
        hsf,
        wmm,
        hmm,
        wsm,
        hsm,
    )
    module.add_graph("sparse_mesh_warp_3d_f32", g3.compile())

    # 3. Adaptive Search & Refine Graph
    ref_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.f32, ndim=2)
    warped_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "warped", ti.f32, ndim=2)
    mov_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mov", ti.f32, ndim=2)
    x_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "x_grid", ti.f32, ndim=1)
    y_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "y_grid", ti.f32, ndim=1)
    cands_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cand_motions", ti.types.vector(2, ti.f32), ndim=1)
    nc_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_cands", ti.i32)
    dst_ref_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    eth_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "err_threshold", ti.f32)
    mi_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_iters", ti.i32)

    g_refine = ti.graph.GraphBuilder()
    g_refine.dispatch(
        _adaptive_refine_2d_kernel,
        ref_arg,
        warped_arg,
        mov_arg,
        mesh_arg,
        u_arg,
        v_arg,
        x_arg,
        y_arg,
        cands_arg,
        nc_arg,
        dst_ref_arg,
        eth_arg,
        mi_arg,
        wsf,
        hsf,
        wmm,
        hmm,
        wsm,
        hsm,
    )
    module.add_graph("adaptive_refine_2d_f32", g_refine.compile())

    fit_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "source", ti.f32, ndim=2)
    fit_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "target", ti.f32, ndim=2)
    fit_weights = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=2)
    fit_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "homographies", ti.f32, ndim=2)
    fit_support = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "support_counts", ti.i32, ndim=1)
    min_support = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "min_support", ti.i32)
    fit_graph = ti.graph.GraphBuilder()
    fit_graph.dispatch(
        _fit_apap_weighted_nodes_kernel,
        fit_src,
        fit_dst,
        fit_weights,
        fit_h,
        fit_support,
        min_support,
    )
    module.add_graph("algn_apap_fit_weighted_f32", fit_graph.compile())

    query = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "query", ti.f32, ndim=2)
    centers = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "centers", ti.f32, ndim=2)
    map_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "homographies", ti.f32, ndim=2)
    map_support = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "support_counts", ti.i32, ndim=1)
    global_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "global_homography", ti.f32, ndim=2)
    map_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.f32, ndim=2)
    sigma_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma_x", ti.f32)
    sigma_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma_y", ti.f32)
    map_graph = ti.graph.GraphBuilder()
    map_graph.dispatch(
        _map_apap_points_kernel,
        query,
        centers,
        map_h,
        map_support,
        global_h,
        map_out,
        sigma_x,
        sigma_y,
    )
    module.add_graph("algn_apap_map_points_f32", map_graph.compile())

    tps_source = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "source", ti.f32, ndim=2)
    tps_target = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "target", ti.f32, ndim=2)
    tps_system = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "system", ti.f32, ndim=2)
    tps_rhs = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "rhs", ti.f32, ndim=2)
    tps_regularization = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "regularization", ti.f32)
    tps_solution = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "solution", ti.f32, ndim=2)
    tps_residuals = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "residuals", ti.f32, ndim=2)
    tps_directions = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "directions", ti.f32, ndim=2)
    tps_products = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "products", ti.f32, ndim=2)
    tps_state = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "state", ti.f32, ndim=2)
    tps_reductions = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reductions", ti.f32, ndim=2)
    tps_tolerance = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tolerance", ti.f32)
    for iteration_bucket in NATIVE_TPS_ITERATION_BUCKETS:
        tps_graph = ti.graph.GraphBuilder()
        tps_graph.dispatch(
            _build_tps_system_kernel,
            tps_source,
            tps_target,
            tps_system,
            tps_rhs,
            tps_regularization,
        )
        tps_graph.dispatch(
            _initialize_tps_minres_kernel,
            tps_system,
            tps_rhs,
            tps_solution,
            tps_residuals,
            tps_directions,
            tps_state,
            tps_reductions,
        )
        for _ in range(iteration_bucket):
            tps_graph.dispatch(
                _tps_minres_step_kernel,
                tps_system,
                tps_rhs,
                tps_solution,
                tps_residuals,
                tps_directions,
                tps_products,
                tps_state,
                tps_reductions,
                tps_tolerance,
            )
        module.add_graph(
            f"algn_apap_tps_minres_{iteration_bucket}_f32", tps_graph.compile()
        )

    tps_query = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "query", ti.f32, ndim=2)
    tps_controls = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "controls", ti.f32, ndim=2)
    tps_weights = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=2)
    tps_affine = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "affine", ti.f32, ndim=2)
    tps_output = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.f32, ndim=2)
    tps_scalars = [
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, ti.f32)
        for name in (
            "source_center_x",
            "source_center_y",
            "source_scale",
            "destination_center_x",
            "destination_center_y",
            "destination_scale",
        )
    ]
    tps_map_graph = ti.graph.GraphBuilder()
    tps_map_graph.dispatch(
        _map_tps_points_kernel,
        tps_query,
        tps_controls,
        tps_weights,
        tps_affine,
        tps_output,
        *tps_scalars,
    )
    module.add_graph("algn_apap_tps_map_f32", tps_map_graph.compile())

    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    module.archive(save_path)
    if os.environ.get("APAP_TCM_STAGING_ROOT", "").strip():
        backend = os.environ.get("PIXEL_REFINE_AOT_ARCH", "cpu").strip().lower()
        device = "NVIDIA" if backend == "cuda" else None
        target = detect_target(backend=backend, device=device)
        graph_names = [
            "sparse_mesh_warp_2d_f32",
            "sparse_mesh_warp_3d_f32",
            "adaptive_refine_2d_f32",
            "algn_apap_fit_weighted_f32",
            "algn_apap_map_points_f32",
            *(f"algn_apap_tps_minres_{bucket}_f32" for bucket in NATIVE_TPS_ITERATION_BUCKETS),
            "algn_apap_tps_map_f32",
        ]
        manifest = build_manifest_from_archive(
            save_path,
            target=target.as_dict(),
            compiler_version=f"taichi-{ti.__version__}",
            kernels=[{"name": name, "graph": name, "args": []} for name in graph_names],
        )
        attach_manifest(save_path, manifest)
    print(f"  [SUCCESS] Archived to: {save_path}")
    ti.reset()


def compile_all_targets():
    os.makedirs(AOT_TCM_DIR, exist_ok=True)
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "all").lower()

    targets = []
    staging_root = os.environ.get("APAP_TCM_STAGING_ROOT", "").strip()

    if staging_root:
        arch = {
            "cpu": ti.cpu,
            "cuda": ti.cuda,
            "vulkan": ti.vulkan,
            "opengl": ti.opengl,
        }.get(arch_str)
        if arch is None:
            raise ValueError(
                "APAP_TCM_STAGING_ROOT requires PIXEL_REFINE_AOT_ARCH to be "
                "cpu, cuda, vulkan, or opengl"
            )
        target = detect_target(backend=arch_str)
        targets.append(
            (
                arch,
                os.path.join(
                    staging_root,
                    target.target_id,
                    target.artifact_name("apap_native"),
                ),
            )
        )

    # Vulkan
    if not staging_root and arch_str in ("vulkan", "all"):
        vulkan_dir = os.path.join(AOT_TCM_DIR, "vulkan_x86_64_windows")
        targets.append((ti.vulkan, os.path.join(vulkan_dir, "apap_sparse_mesh_vulkan_x86_64_windows.tcm")))
        targets.append((ti.vulkan, os.path.join(AOT_TCM_DIR, "apap_sparse_mesh_vulkan.tcm")))

    # CPU
    if not staging_root and arch_str in ("cpu", "all"):
        cpu_dir = os.path.join(AOT_TCM_DIR, "cpu_x86_64_windows")
        targets.append((ti.cpu, os.path.join(cpu_dir, "apap_sparse_mesh_cpu_x86_64_windows.tcm")))
        targets.append((ti.cpu, os.path.join(AOT_TCM_DIR, "apap_sparse_mesh_cpu.tcm")))

    # OpenGL
    if not staging_root and arch_str in ("opengl", "all") and hasattr(ti, "opengl"):
        opengl_dir = os.path.join(AOT_TCM_DIR, "opengl_x86_64_windows")
        targets.append((ti.opengl, os.path.join(opengl_dir, "apap_sparse_mesh_opengl_x86_64_windows.tcm")))
        targets.append((ti.opengl, os.path.join(AOT_TCM_DIR, "apap_sparse_mesh_opengl.tcm")))

    # CUDA
    if not staging_root and arch_str in ("cuda", "all") and hasattr(ti, "cuda"):
        cuda_dir = os.path.join(AOT_TCM_DIR, "cuda_x86_64_windows")
        cuda_nv_dir = os.path.join(AOT_TCM_DIR, "cuda_x86_64_windows_nvidia")
        targets.append((ti.cuda, os.path.join(cuda_dir, "apap_sparse_mesh_cuda_x86_64_windows.tcm")))
        targets.append((ti.cuda, os.path.join(cuda_nv_dir, "apap_sparse_mesh_cuda_x86_64_windows_nvidia.tcm")))
        targets.append((ti.cuda, os.path.join(cuda_nv_dir, "apap_cuda_x86_64_windows_nvidia.tcm")))
        targets.append((ti.cuda, os.path.join(AOT_TCM_DIR, "apap_sparse_mesh_cuda.tcm")))

    results = []
    for arch, path in targets:
        try:
            compile_mesh_warp_aot(arch, path)
            results.append(f"[PASS] {os.path.basename(path)}")
        except Exception as e:
            print(f"[FAIL] {os.path.basename(path)}: {e}")
            results.append(f"[FAIL] {os.path.basename(path)}: {e}")

    print("\n" + "=" * 60)
    print(" APAP SPARSE MESH AOT TCM COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)


if __name__ == "__main__":
    compile_all_targets()
