"""
AOT Kernels: Math Operations
=============================
Element-wise, reduction, utility, and linear algebra kernels.

Standalone compilable + register_graphs() for fused TCM output.

Graphs:
  - math_abs        → Element-wise absolute value
  - math_sqrt       → Element-wise square root
  - math_log        → Element-wise natural logarithm
  - math_exp        → Element-wise exponential
  - math_square     → Element-wise square
  - math_pow        → Element-wise power
  - math_mag        → 2D vector magnitude
  - math_rsum       → Reduction sum
  - math_rmax       → Reduction max
  - math_rmin       → Reduction min
  - math_clip       → Element-wise clamp
  - math_where      → Conditional select
  - math_meshgrid   → IJ meshgrid
  - math_sort       → Bitonic sort step
  - math_mat3_inv   → Batch 3x3 matrix inverse
  - math_mat3_det   → Batch 3x3 matrix determinant
  - math_matmul     → Matrix multiplication
"""

import os
import taichi as ti


# ══════════════════════════════════════════════════════════════
#  KERNEL DEFINITIONS
# ══════════════════════════════════════════════════════════════

# ---- Element-wise kernels ----

@ti.kernel
def math_abs_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for I in ti.grouped(src): dst[I] = ti.abs(src[I])


@ti.kernel
def math_sqrt_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for I in ti.grouped(src): dst[I] = ti.sqrt(src[I])


@ti.kernel
def math_log_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for I in ti.grouped(src): dst[I] = ti.log(ti.max(src[I], 1e-10))


@ti.kernel
def math_exp_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for I in ti.grouped(src): dst[I] = ti.exp(src[I])


@ti.kernel
def math_power_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), exponent: ti.f32):
    for I in ti.grouped(src): dst[I] = ti.pow(src[I], exponent)


@ti.kernel
def math_square_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for I in ti.grouped(src): dst[I] = src[I] * src[I]


@ti.kernel
def math_magnitude_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                          h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        dst[y, x] = ti.sqrt(src[y, x, 0] * src[y, x, 0] + src[y, x, 1] * src[y, x, 1])


# ---- Reduction kernels ----

@ti.kernel
def math_reduce_sum_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    total = 0.0
    for I in ti.grouped(src):
        total += src[I]
    dst[0] = total


@ti.kernel
def math_reduce_max_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    val = -1e30
    for I in ti.grouped(src):
        val = ti.max(val, src[I])
    dst[0] = val


@ti.kernel
def math_reduce_min_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    val = 1e30
    for I in ti.grouped(src):
        val = ti.min(val, src[I])
    dst[0] = val


@ti.kernel
def math_clip_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                     lo: ti.f32, hi: ti.f32):
    for I in ti.grouped(src): dst[I] = ti.max(lo, ti.min(hi, src[I]))


@ti.kernel
def math_where_kernel(cond: ti.types.ndarray(),
                      src_true: ti.types.ndarray(), src_false: ti.types.ndarray(),
                      dst: ti.types.ndarray()):
    for I in ti.grouped(cond):
        dst[I] = ti.select(cond[I] > 0.5, src_true[I], src_false[I])


# ---- Utility kernels ----

@ti.kernel
def math_meshgrid_ij_kernel(dst_x: ti.types.ndarray(), dst_y: ti.types.ndarray(),
                            h: ti.i32, w: ti.i32):
    for y, x in ti.ndrange(h, w):
        dst_x[y, x] = float(x)
        dst_y[y, x] = float(y)


@ti.kernel
def math_bitonic_sort_step(src: ti.types.ndarray(), stage: ti.i32, step: ti.i32):
    n = src.shape[0]
    for i in range(n):
        pair_dis = 1 << step
        block_size = 1 << (stage + 1)
        block_idx = i >> (stage + 1)
        within_block = i % block_size
        partner_offset = 1 << step
        partner = i
        if within_block < partner_offset:
            partner = i + partner_offset
        else:
            partner = i - partner_offset
        if partner >= 0 and partner < n:
            ascending = ((i >> stage) & 1) == 0
            if ascending:
                if src[i] > src[partner]:
                    src[i], src[partner] = src[partner], src[i]
            else:
                if src[i] < src[partner]:
                    src[i], src[partner] = src[partner], src[i]


# ---- Linear algebra kernels ----

@ti.kernel
def math_batch_mat3_inv_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), n: ti.i32):
    for batch in range(n):
        a = src[batch, 0, 0]; b = src[batch, 0, 1]; c = src[batch, 0, 2]
        d = src[batch, 1, 0]; e = src[batch, 1, 1]; f = src[batch, 1, 2]
        g = src[batch, 2, 0]; h_val = src[batch, 2, 1]; i_val = src[batch, 2, 2]
        det = a*(e*i_val - f*h_val) - b*(d*i_val - f*g) + c*(d*h_val - e*g)
        if ti.abs(det) > 1e-10:
            inv_det = 1.0 / det
            dst[batch, 0, 0] = (e*i_val - f*h_val) * inv_det
            dst[batch, 0, 1] = (c*h_val - b*i_val) * inv_det
            dst[batch, 0, 2] = (b*f - c*e) * inv_det
            dst[batch, 1, 0] = (f*g - d*i_val) * inv_det
            dst[batch, 1, 1] = (a*i_val - c*g) * inv_det
            dst[batch, 1, 2] = (c*d - a*f) * inv_det
            dst[batch, 2, 0] = (d*h_val - e*g) * inv_det
            dst[batch, 2, 1] = (b*g - a*h_val) * inv_det
            dst[batch, 2, 2] = (a*e - b*d) * inv_det


@ti.kernel
def math_batch_mat3_det_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), n: ti.i32):
    for batch in range(n):
        a = src[batch, 0, 0]; b = src[batch, 0, 1]; c = src[batch, 0, 2]
        d = src[batch, 1, 0]; e = src[batch, 1, 1]; f = src[batch, 1, 2]
        g = src[batch, 2, 0]; h_val = src[batch, 2, 1]; i_val = src[batch, 2, 2]
        dst[batch] = a*(e*i_val - f*h_val) - b*(d*i_val - f*g) + c*(d*h_val - e*g)


@ti.kernel
def math_matmul_kernel(A: ti.types.ndarray(), B: ti.types.ndarray(), C: ti.types.ndarray(),
                       m: ti.i32, n: ti.i32, k: ti.i32):
    for i, j in ti.ndrange(m, n):
        total = 0.0
        for p in range(k):
            total += A[i, p] * B[p, j]
        C[i, j] = total


# ══════════════════════════════════════════════════════════════
#  GRAPH BUILDER (for fused compilation)
# ══════════════════════════════════════════════════════════════

def register_graphs(module):
    """Register Math Operations graphs into a TCM module."""
    a_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    a_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)

    # Element-wise graphs: abs, sqrt, log, exp, square
    for name, fn in [("abs", math_abs_kernel), ("sqrt", math_sqrt_kernel),
                     ("log", math_log_kernel), ("exp", math_exp_kernel),
                     ("square", math_square_kernel)]:
        g = ti.graph.GraphBuilder()
        g.dispatch(fn, a_src, a_dst)
        module.add_graph(f"math_{name}", g.compile())

    # Graph: math_pow
    g = ti.graph.GraphBuilder()
    a_exp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "exponent", ti.f32)
    g.dispatch(math_power_kernel, a_src, a_dst, a_exp)
    module.add_graph("math_pow", g.compile())

    # Graph: math_mag
    g = ti.graph.GraphBuilder()
    a_src3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    a_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    a_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g.dispatch(math_magnitude_kernel, a_src3, a_dst, a_h, a_w)
    module.add_graph("math_mag", g.compile())

    # Graph: math_rsum
    g = ti.graph.GraphBuilder()
    a_sum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=1)
    g.dispatch(math_reduce_sum_kernel, a_src, a_sum)
    module.add_graph("math_rsum", g.compile())

    # Graph: math_rmax
    g = ti.graph.GraphBuilder()
    g.dispatch(math_reduce_max_kernel, a_src, a_sum)
    module.add_graph("math_rmax", g.compile())

    # Graph: math_rmin
    g = ti.graph.GraphBuilder()
    g.dispatch(math_reduce_min_kernel, a_src, a_sum)
    module.add_graph("math_rmin", g.compile())

    # Graph: math_clip
    g = ti.graph.GraphBuilder()
    a_lo = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "lo", ti.f32)
    a_hi = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "hi", ti.f32)
    g.dispatch(math_clip_kernel, a_src, a_dst, a_lo, a_hi)
    module.add_graph("math_clip", g.compile())

    # Graph: math_where
    g = ti.graph.GraphBuilder()
    a_cond = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cond", ti.f32, ndim=2)
    a_st = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_true", ti.f32, ndim=2)
    a_sf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src_false", ti.f32, ndim=2)
    g.dispatch(math_where_kernel, a_cond, a_st, a_sf, a_dst)
    module.add_graph("math_where", g.compile())

    # Graph: math_meshgrid
    g = ti.graph.GraphBuilder()
    a_dx = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_x", ti.f32, ndim=2)
    a_dy = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_y", ti.f32, ndim=2)
    g.dispatch(math_meshgrid_ij_kernel, a_dx, a_dy, a_h, a_w)
    module.add_graph("math_meshgrid", g.compile())

    # Graph: math_sort
    g = ti.graph.GraphBuilder()
    a_src1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=1)
    a_stage = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stage", ti.i32)
    a_step = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step", ti.i32)
    g.dispatch(math_bitonic_sort_step, a_src1d, a_stage, a_step)
    module.add_graph("math_sort", g.compile())

    # Graph: math_mat3_inv
    g = ti.graph.GraphBuilder()
    a_src3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    a_dst3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    a_n = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32)
    g.dispatch(math_batch_mat3_inv_kernel, a_src3d, a_dst3d, a_n)
    module.add_graph("math_mat3_inv", g.compile())

    # Graph: math_mat3_det
    g = ti.graph.GraphBuilder()
    a_det = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=1)
    g.dispatch(math_batch_mat3_det_kernel, a_src3d, a_det, a_n)
    module.add_graph("math_mat3_det", g.compile())

    # Graph: math_matmul
    g = ti.graph.GraphBuilder()
    a_A = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "A", ti.f32, ndim=2)
    a_B = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "B", ti.f32, ndim=2)
    a_C = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "C", ti.f32, ndim=2)
    a_m = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "m", ti.i32)
    a_n = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32)
    a_k = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "k", ti.i32)
    g.dispatch(math_matmul_kernel, a_A, a_B, a_C, a_m, a_n, a_k)
    module.add_graph("math_matmul", g.compile())


# ══════════════════════════════════════════════════════════════
#  STANDALONE COMPILATION
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from aot_common import get_tcm_dir

    ti.init(arch=ti.vulkan, offline_cache=False)
    module = ti.aot.Module(arch=ti.vulkan)
    register_graphs(module)

    save_path = os.path.join(get_tcm_dir(), "math_ops_vulkan.tcm")
    module.archive(save_path)
    print(f"  Math Ops standalone → {save_path}")
    ti.reset()
