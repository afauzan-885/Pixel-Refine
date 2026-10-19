"""AOT compiler for Pulse-Splat 3D Gaussian Splatting module.

Compiles projection and rasterization graphs into TCM archives across:
- CUDA (cuda_x86_64_windows_nvidia)
- Vulkan (vulkan_desktop)
- CPU (cpu_x86_64_windows)
"""

import os
import shutil
import taichi as ti

from taichi_vision.taichi_algorithm.gaussian_splatting.pulse_splat import (
    project_gaussians_kernel,
    project_and_init_sort_kernel,
    rasterize_tile_pulse_splat_kernel,
    rasterize_from_gpu_sorted_kernel,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AOT_TCM_DIR = os.path.join(BASE_DIR, "aot_tcm")


def compile_for_arch(arch, target_paths):
    print(f"[*] Compiling Pulse-Splat for {arch}...")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # 1. Project Gaussians Graph
    num_g_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_gaussians", ti.i32)
    means_3d_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "means_3d", ti.f32, ndim=2)
    scales_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "scales", ti.f32, ndim=2)
    rot_quats_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "rot_quats", ti.f32, ndim=2)
    view_mat_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "view_matrix", ti.f32, ndim=2)
    fx_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "fx", ti.f32)
    fy_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "fy", ti.f32)
    cx_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cx", ti.f32)
    cy_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cy", ti.f32)
    img_w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "img_w", ti.i32)
    img_h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "img_h", ti.i32)
    out_means_2d_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_means_2d", ti.f32, ndim=2)
    out_cov_2d_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_cov_2d", ti.f32, ndim=2)
    out_depths_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_depths", ti.f32, ndim=1)
    out_bounds_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_bounds", ti.f32, ndim=2)
    out_valid_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_valid", ti.i32, ndim=1)

    g_proj = ti.graph.GraphBuilder()
    g_proj.dispatch(
        project_gaussians_kernel,
        num_g_arg,
        means_3d_arg,
        scales_arg,
        rot_quats_arg,
        view_mat_arg,
        fx_arg,
        fy_arg,
        cx_arg,
        cy_arg,
        img_w_arg,
        img_h_arg,
        out_means_2d_arg,
        out_cov_2d_arg,
        out_depths_arg,
        out_bounds_arg,
        out_valid_arg,
    )
    module.add_graph("project_gaussians", g_proj.compile())

    # 2. Rasterize Tile Pulse-Splat Graph
    num_vis_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_visible", ti.i32)
    sorted_idx_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sorted_indices", ti.i32, ndim=1)
    colors_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "colors", ti.f32, ndim=2)
    opacities_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "opacities", ti.f32, ndim=1)
    out_img_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "out_image", ti.f32, ndim=3)

    g_rast = ti.graph.GraphBuilder()
    g_rast.dispatch(
        rasterize_tile_pulse_splat_kernel,
        img_w_arg,
        img_h_arg,
        num_vis_arg,
        sorted_idx_arg,
        out_means_2d_arg,
        out_cov_2d_arg,
        colors_arg,
        opacities_arg,
        out_bounds_arg,
        out_img_arg,
    )
    module.add_graph("rasterize_pulse_splat", g_rast.compile())

    # 3. Project and Init Sort Graph (Zero-Readback)
    padded_n_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "padded_n", ti.i32)
    sort_keys_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sort_keys", ti.f32, ndim=1)
    sort_idx_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sort_indices", ti.i32, ndim=1)

    g_proj_sort = ti.graph.GraphBuilder()
    g_proj_sort.dispatch(
        project_and_init_sort_kernel,
        num_g_arg,
        padded_n_arg,
        means_3d_arg,
        scales_arg,
        rot_quats_arg,
        view_mat_arg,
        fx_arg,
        fy_arg,
        cx_arg,
        cy_arg,
        img_w_arg,
        img_h_arg,
        out_means_2d_arg,
        out_cov_2d_arg,
        out_bounds_arg,
        sort_keys_arg,
        sort_idx_arg,
    )
    module.add_graph("project_and_init_sort", g_proj_sort.compile())

    # 4. Rasterize from GPU Sorted Graph (Zero-Readback)
    g_rast_gpu = ti.graph.GraphBuilder()
    g_rast_gpu.dispatch(
        rasterize_from_gpu_sorted_kernel,
        img_w_arg,
        img_h_arg,
        padded_n_arg,
        sort_keys_arg,
        sort_idx_arg,
        out_means_2d_arg,
        out_cov_2d_arg,
        colors_arg,
        opacities_arg,
        out_bounds_arg,
        out_img_arg,
    )
    module.add_graph("rasterize_from_gpu_sorted", g_rast_gpu.compile())

    primary_path = target_paths[0]
    os.makedirs(os.path.dirname(primary_path), exist_ok=True)
    module.archive(primary_path)
    print(f"[+] Archived {primary_path}")

    for alias in target_paths[1:]:
        os.makedirs(os.path.dirname(alias), exist_ok=True)
        shutil.copyfile(primary_path, alias)
        print(f"[+] Created alias: {alias}")

    ti.reset()


def compile_gaussian_splatting_tcm():
    # 1. CUDA
    cuda_dir = os.path.join(AOT_TCM_DIR, "cuda_x86_64_windows_nvidia")
    compile_for_arch(
        ti.cuda,
        [
            os.path.join(cuda_dir, "pulse_splat_cuda_x86_64_windows_nvidia.tcm"),
            os.path.join(cuda_dir, "gaussian_splatting_cuda_x86_64_windows_nvidia.tcm"),
        ],
    )

    # 2. Vulkan
    vk_dir = os.path.join(AOT_TCM_DIR, "vulkan_desktop")
    compile_for_arch(
        ti.vulkan,
        [
            os.path.join(vk_dir, "pulse_splat_vulkan_desktop.tcm"),
            os.path.join(vk_dir, "gaussian_splatting_vulkan_desktop.tcm"),
        ],
    )

    # 3. CPU
    cpu_dir = os.path.join(AOT_TCM_DIR, "cpu_x86_64_windows")
    compile_for_arch(
        ti.cpu,
        [
            os.path.join(cpu_dir, "pulse_splat_cpu_x86_64_windows.tcm"),
            os.path.join(cpu_dir, "gaussian_splatting_cpu_x86_64_windows.tcm"),
        ],
    )


if __name__ == "__main__":
    compile_gaussian_splatting_tcm()
