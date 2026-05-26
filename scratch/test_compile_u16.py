import taichi as ti
import os

print("Initializing Taichi...")
ti.init(arch=ti.vulkan)

@ti.kernel
def test_u16_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=3),
    dst: ti.types.ndarray(dtype=ti.u16, ndim=3),
    h: ti.i32,
    w: ti.i32,
):
    for r, c in ti.ndrange(h, w):
        dst[r, c, 0] = ti.cast(src[r, c, 0] * 65535.0, ti.u16)
        dst[r, c, 1] = ti.cast(src[r, c, 1] * 65535.0, ti.u16)
        dst[r, c, 2] = ti.cast(src[r, c, 2] * 65535.0, ti.u16)

try:
    print("Building graph...")
    module = ti.aot.Module(ti.vulkan)
    g = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.u16, ndim=3)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    
    g.dispatch(test_u16_kernel, src_arg, dst_arg, h_arg, w_arg)
    module.add_graph("test_graph", g.compile())
    
    save_path = "scratch/test_u16.tcm"
    module.archive(save_path)
    print(f"Success! Saved test TCM to: {save_path}")
except Exception as e:
    import traceback
    traceback.print_exc()
