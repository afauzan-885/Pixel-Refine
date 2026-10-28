"""Fused multi-head attention universal kernel.

Supports the ``com.microsoft::MultiHeadAttention`` profile used by LightGlue:
separate Q/K/V tensors shaped ``(batch, sequence, hidden)``, no masks, and
``hidden = num_heads * head_dim``. The kernel performs a numerically stable
two-pass softmax per query so no ``scores`` scratch buffer is needed.
"""

import taichi as ti


@ti.kernel
def nu_attention(
    q: ti.types.ndarray(ti.f32, 1),
    k: ti.types.ndarray(ti.f32, 1),
    v: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    seq: ti.i32,
    hidden: ti.i32,
    heads: ti.i32,
    scale: ti.f32,
):
    head_dim = hidden // heads
    for idx in range(n_batch * heads * seq):
        q_pos = idx % seq
        head = (idx // seq) % heads
        b = idx // (seq * heads)
        q_base = (b * seq + q_pos) * hidden + head * head_dim
        # pass 1: running maximum of scaled dot products
        peak = -3.4028234663852886e38
        for kp in range(seq):
            k_base = (b * seq + kp) * hidden + head * head_dim
            dot = 0.0
            for d in range(head_dim):
                dot += q[q_base + d] * k[k_base + d]
            peak = ti.max(peak, dot * scale)
        # pass 2: accumulate normalizer and weighted values
        total = 0.0
        for kp in range(seq):
            k_base = (b * seq + kp) * hidden + head * head_dim
            dot = 0.0
            for d in range(head_dim):
                dot += q[q_base + d] * k[k_base + d]
            total += ti.exp(dot * scale - peak)
        inv = 1.0 / total
        for d in range(head_dim):
            acc = 0.0
            for kp in range(seq):
                k_base = (b * seq + kp) * hidden + head * head_dim
                v_base = (b * seq + kp) * hidden + head * head_dim
                dot = 0.0
                for e in range(head_dim):
                    dot += q[q_base + e] * k[k_base + e]
                acc += ti.exp(dot * scale - peak) * v[v_base + d]
            y[q_base + d] = acc * inv


@ti.kernel
def nu_attention_with_bias(
    q: ti.types.ndarray(ti.f32, 1),
    k: ti.types.ndarray(ti.f32, 1),
    v: ti.types.ndarray(ti.f32, 1),
    q_bias: ti.types.ndarray(ti.f32, 1),
    k_bias: ti.types.ndarray(ti.f32, 1),
    v_bias: ti.types.ndarray(ti.f32, 1),
    o_bias: ti.types.ndarray(ti.f32, 1),
    y: ti.types.ndarray(ti.f32, 1),
    n_batch: ti.i32,
    seq: ti.i32,
    hidden: ti.i32,
    heads: ti.i32,
    scale: ti.f32,
):
    head_dim = hidden // heads
    for idx in range(n_batch * heads * seq):
        q_pos = idx % seq
        head = (idx // seq) % heads
        b = idx // (seq * heads)
        q_base = (b * seq + q_pos) * hidden + head * head_dim
        peak = -3.4028234663852886e38
        for kp in range(seq):
            k_base = (b * seq + kp) * hidden + head * head_dim
            dot = 0.0
            for d in range(head_dim):
                dot += (q[q_base + d] + q_bias[head * head_dim + d]) * (
                    k[k_base + d] + k_bias[head * head_dim + d]
                )
            peak = ti.max(peak, dot * scale)
        total = 0.0
        for kp in range(seq):
            k_base = (b * seq + kp) * hidden + head * head_dim
            dot = 0.0
            for d in range(head_dim):
                dot += (q[q_base + d] + q_bias[head * head_dim + d]) * (
                    k[k_base + d] + k_bias[head * head_dim + d]
                )
            total += ti.exp(dot * scale - peak)
        inv = 1.0 / total
        for d in range(head_dim):
            acc = 0.0
            for kp in range(seq):
                k_base = (b * seq + kp) * hidden + head * head_dim
                v_base = (b * seq + kp) * hidden + head * head_dim
                dot = 0.0
                for e in range(head_dim):
                    dot += (q[q_base + e] + q_bias[head * head_dim + e]) * (
                        k[k_base + e] + k_bias[head * head_dim + e]
                    )
                acc += ti.exp(dot * scale - peak) * (v[v_base + d] + v_bias[head * head_dim + d])
            y[q_base + d] = acc * inv + o_bias[head * head_dim + d]


ALL_ATTENTION_KERNELS = [
    nu_attention,
    nu_attention_with_bias,
]