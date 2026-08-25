"""
compile_math_ops.py - AOT Compilation for GPU Math Operations
=============================================================

Graphs compiled:
  - math_abs
  - math_sqrt
  - math_log
  - math_exp
  - math_square
  - math_pow
  - math_mag
  - math_rsum
  - math_rmax
  - math_rmin
  - math_clip
  - math_where
  - math_meshgrid
  - math_sort
  - math_mat3_inv
  - math_mat3_det
  - math_matmul
"""

import os

os.environ["AOT_MODE"] = "0"

import sys
import taichi as ti

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_vision.taichi_algorithm.math_ops import math_ops_kernels


def compile_math_ops(arch=ti.vulkan, out_dir=None):
    print(f"\n>>> Compiling Math Ops AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)
    math_ops_kernels.register_graphs(module)

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
    save_path = os.path.abspath(os.path.join(out_dir, f"math_ops_{arch_name}.tcm"))
    module.archive(save_path)

    ti.reset()
    print(f"Math Ops compiled: {save_path}")
    return save_path


if __name__ == "__main__":
    for arch, suffix in ((ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")):
        try:
            compile_math_ops(arch=arch)
        except Exception as exc:
            print(f"Skipping {suffix} due to error: {exc}")
