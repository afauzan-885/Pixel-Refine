import os

os.environ["AOT_MODE"] = "0"

import taichi as ti
import os


def compile_cast_tcm():
    arch_str = os.environ.get("AOT_ARCH", "vulkan").lower()
    arch = ti.vulkan
    if arch_str == "cuda":
        arch = ti.cuda
    elif arch_str == "cpu":
        arch = ti.x64

    ti.init(arch=arch)

    # Kernel untuk konversi ke Float32 (Standard untuk pemrosesan)
    @ti.kernel
    def cast_u8_to_f32(
        src: ti.types.ndarray(dtype=ti.u8, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        for I in ti.grouped(src):
            dst[I] = ti.cast(src[I], ti.f32) / 255.0

    @ti.kernel
    def cast_f32_to_u8(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.u8, ndim=3),
    ):
        for I in ti.grouped(src):
            dst[I] = ti.cast(ti.round(src[I] * 255.0), ti.u8)

    module = ti.aot.Module(arch)

    # Register Graphs
    def add_cast_graph(name, kernel, src_type, dst_type):
        src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", src_type, ndim=3)
        dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dst_type, ndim=3)
        g = ti.graph.GraphBuilder()
        g.dispatch(kernel, src_arg, dst_arg)
        module.add_graph(name, g.compile())

    add_cast_graph("u8_to_f32", cast_u8_to_f32, ti.u8, ti.f32)
    add_cast_graph("f32_to_u8", cast_f32_to_u8, ti.f32, ti.u8)

    save_dir = os.path.join(os.path.dirname(__file__), "aot_tcm")
    os.makedirs(save_dir, exist_ok=True)
    suffix = "vulkan"
    if arch == ti.cuda:
        suffix = "cuda"
    elif arch == ti.x64:
        suffix = "cpu"
    save_path = os.path.join(save_dir, f"cast_{suffix}.tcm")

    module.archive(save_path)
    print(f"Cast TCM archived to {save_path}")


if __name__ == "__main__":
    compile_cast_tcm()
