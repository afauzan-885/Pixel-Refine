"""
Compile Estimate Noise TCM — Taichi AOT Compilation Script.
===========================================================
Compiles the Estimate Noise GPU graph into portable .tcm archives for
OpenGL, Vulkan, CUDA, and CPU.
"""

import os
os.environ["AOT_MODE"] = "0"
os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

import importlib
import sys
from pathlib import Path

import taichi as ti

file_dir = Path(__file__).resolve().parent
project_root = file_dir.parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

estimate_noise_mod = importlib.import_module(
    "taichi_vision.taichi_algorithm.enhancement.estimate_noise"
)

ASSETS_DIR = project_root / "taichi_vision" / "taichi_algorithm" / "aot_tcm"


def _target_id_for_suffix(suffix: str) -> str:
    override = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
    if override:
        return override
    defaults = {
        "cpu": "cpu_x86_64_windows" if os.name == "nt" else "cpu_x86_64_linux",
        "cuda": "cuda_x86_64_windows_nvidia" if os.name == "nt" else "cuda_arm64_linux_nvidia",
        "vulkan": "vulkan_x86_64_windows" if os.name == "nt" else "vulkan_x86_64_linux",
        "opengl": "opengl_x86_64_windows" if os.name == "nt" else "opengl_x86_64_linux",
    }
    return defaults.get(suffix, f"{suffix}_x86_64_windows")


def compile_estimate_noise(arch, save_path: str):
    print(f"\n>>> Compiling Estimate Noise AOT for: {arch} -> {save_path}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    block_mad_out_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "block_mad_out", ti.f32, ndim=1)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    num_blocks_x_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_blocks_x", ti.i32)
    num_blocks_y_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_blocks_y", ti.i32)

    g = ti.graph.GraphBuilder()
    g.dispatch(
        estimate_noise_mod.estimate_noise_kernel,
        src_arg,
        block_mad_out_arg,
        h_arg,
        w_arg,
        num_blocks_x_arg,
        num_blocks_y_arg,
    )
    module.add_graph("estimate_noise", g.compile())

    module.archive(str(save_path))
    print(f"  [OK] Saved TCM: {save_path}")
    ti.reset()


def main():
    arch_str = (
        os.environ.get("PIXEL_REFINE_AOT_ARCH")
        or os.environ.get("TARGET_BACKEND")
        or os.environ.get("AOT_ARCH")
        or "all"
    ).lower()

    if arch_str == "vulkan":
        archs = [(ti.vulkan, "vulkan")]
    elif arch_str == "opengl":
        archs = [(ti.opengl, "opengl")]
    elif arch_str == "cuda":
        archs = [(ti.cuda, "cuda")]
    elif arch_str == "cpu":
        archs = [(ti.cpu, "cpu")]
    else:
        archs = [
            (ti.vulkan, "vulkan"),
            (ti.opengl, "opengl"),
            (ti.cpu, "cpu"),
        ]

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    success = 0
    for arch, suffix in archs:
        target_id = _target_id_for_suffix(suffix)
        out_path = ASSETS_DIR / f"estimate_noise_{target_id}.tcm"
        try:
            compile_estimate_noise(arch, str(out_path))
            success += 1
        except Exception as e:
            print(f"  [FAIL] {suffix}: {e}")

    print(f"\nCompleted: {success}/{len(archs)} backends compiled successfully.")


if __name__ == "__main__":
    main()
