"""
Compile AutoEnhance TCM — Taichi AOT Compilation Script.
=========================================================
Compiles the AutoEnhance GPU graph into portable .tcm archives for
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

auto_enhance_mod = importlib.import_module(
    "taichi_vision.taichi_algorithm.enhancement.auto_enhance"
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


def compile_auto_enhance(arch, save_path: str):
    print(f"\n>>> Compiling AutoEnhance AOT for: {arch} -> {save_path}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    gain_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gain", ti.f32)
    white_level_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "white_level", ti.f32)
    shadow_lift_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "shadow_lift", ti.f32)
    inv_gamma_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_gamma", ti.f32)
    contrast_s_curve_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "contrast_s_curve", ti.f32)
    global_contrast_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "global_contrast", ti.f32)
    saturation_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "saturation", ti.f32)
    use_adaptive_knee_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_adaptive_knee", ti.i32)

    g = ti.graph.GraphBuilder()
    g.dispatch(
        auto_enhance_mod.auto_enhance_kernel,
        src_arg,
        dst_arg,
        h_arg,
        w_arg,
        gain_arg,
        white_level_arg,
        shadow_lift_arg,
        inv_gamma_arg,
        contrast_s_curve_arg,
        global_contrast_arg,
        saturation_arg,
        use_adaptive_knee_arg,
    )
    module.add_graph("auto_enhance", g.compile())

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
            (ti.cuda, "cuda"),
            (ti.cpu, "cpu"),
        ]

    results = []
    for arch, suffix in archs:
        target_id = _target_id_for_suffix(suffix)
        target_dir = ASSETS_DIR / target_id
        target_dir.mkdir(parents=True, exist_ok=True)
        save_path = target_dir / f"auto_enhance_{target_id}.tcm"
        legacy_path = ASSETS_DIR / f"auto_enhance_{suffix}.tcm"
        try:
            compile_auto_enhance(arch, str(save_path))
            if not legacy_path.exists():
                import shutil
                shutil.copy2(str(save_path), str(legacy_path))
            results.append(f"[PASS] {target_id}")
        except Exception as exc:
            print(f"[FAIL] {target_id}: {exc}")
            results.append(f"[FAIL] {target_id}: {exc}")

    print("\n" + "=" * 50)
    print(" AutoEnhance TCM Compilation Summary:")
    print("=" * 50)
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
