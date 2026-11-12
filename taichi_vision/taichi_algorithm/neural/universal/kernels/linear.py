"""Dense linear algebra universal kernels."""

import taichi as ti


@ti.kernel
def nu_matmul(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    batch: ti.i32,
    m: ti.i32,
    k: ti.i32,
    n: ti.i32,
    a_batch_stride: ti.i32,
    b_batch_stride: ti.i32,
):
    """C[b] = A[b] @ B[b].

    ``a_batch_stride``/``b_batch_stride`` of 0 broadcast one operand across the
    batch dimension, which is how ONNX expresses a shared projection matrix.
    """
    for idx in range(batch * m * n):
        col = idx % n
        t = idx // n
        row = t % m
        bi = t // m
        acc = 0.0
        a_base = bi * a_batch_stride + row * k
        b_base = bi * b_batch_stride
        for kk in range(k):
            acc += a[a_base + kk] * b[b_base + kk * n + col]
        y[idx] = acc


@ti.kernel
def nu_matmul_transb(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    batch: ti.i32,
    m: ti.i32,
    k: ti.i32,
    n: ti.i32,
    a_batch_stride: ti.i32,
    b_batch_stride: ti.i32,
):
    """C[b] = A[b] @ B[b]^T where B is [n, k]."""
    for idx in range(batch * m * n):
        col = idx % n
        t = idx // n
        row = t % m
        bi = t // m
        acc = 0.0
        a_base = bi * a_batch_stride + row * k
        b_base = bi * b_batch_stride + col * k
        for kk in range(k):
            acc += a[a_base + kk] * b[b_base + kk]
        y[idx] = acc


@ti.kernel
def nu_gemm(
    a: ti.types.ndarray(ti.f32, 1),
    b: ti.types.ndarray(ti.f32, 1),
    c: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    m: ti.i32,
    k: ti.i32,
    n: ti.i32,
    trans_a: ti.i32,
    trans_b: ti.i32,
    alpha: ti.f32,
    beta: ti.f32,
    has_c: ti.i32,
):
    for idx in range(m * n):
        col = idx % n
        row = idx // n
        acc = 0.0
        for kk in range(k):
            av = a[kk * m + row] if trans_a != 0 else a[row * k + kk]
            bv = b[col * k + kk] if trans_b != 0 else b[kk * n + col]
            acc += av * bv
        if has_c != 0:
            y[idx] = alpha * acc + beta * c[idx]
        else:
            y[idx] = alpha * acc


ALL_LINEAR_KERNELS = [
    nu_matmul,
    nu_matmul_transb,
    nu_gemm,
]