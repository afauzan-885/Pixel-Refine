"""Shared device helpers for the universal kernel pool."""

import taichi as ti

# Elementwise binary op codes. Kept as integers so one kernel covers many
# ONNX operators without generating a kernel per combination.
OP_ADD = 0
OP_SUB = 1
OP_MUL = 2
OP_DIV = 3
OP_POW = 4
OP_MIN = 5
OP_MAX = 6
OP_LESS = 7
OP_GREATER = 8
OP_EQUAL = 9
OP_MOD = 10
OP_AND = 11
OP_FMOD = 12

# Activation kinds used by fused conv / norm kernels.
ACT_NONE = 0
ACT_RELU = 1
ACT_SIGMOID = 2
ACT_TANH = 3
ACT_GELU = 4

# Unary op codes.
UN_RELU = 1
UN_SIGMOID = 2
UN_TANH = 3
UN_GELU = 4
UN_GELU_TANH = 5
UN_SQRT = 6
UN_ABS = 7
UN_NEG = 8
UN_ERF = 9
UN_SOFTPLUS = 10
UN_FLOOR = 11
UN_EXP = 12
UN_LOG = 13
UN_SIN = 14
UN_COS = 15
UN_SQUARE = 16
UN_RECIPROCAL = 17
UN_CEIL = 18
UN_SIGN = 19
UN_LEAKY_RELU = 20

MAX_RANK = 8


@ti.func
def nu_erf(v: ti.f32) -> ti.f32:
    """Abramowitz & Stegun 7.1.26; |error| < 1.5e-7, safe on every backend."""
    p = ti.cast(0.3275911, ti.f32)
    a1 = ti.cast(0.254829592, ti.f32)
    a2 = ti.cast(-0.284496736, ti.f32)
    a3 = ti.cast(1.421413741, ti.f32)
    a4 = ti.cast(-1.453152027, ti.f32)
    a5 = ti.cast(1.061405429, ti.f32)
    sign = 1.0
    if v < 0.0:
        sign = -1.0
    av = ti.abs(v)
    t = 1.0 / (1.0 + p * av)
    poly = t * (a1 + t * (a2 + t * (a3 + t * (a4 + t * a5))))
    return sign * (1.0 - poly * ti.exp(-av * av))


@ti.func
def nu_stable_sigmoid(v: ti.f32) -> ti.f32:
    clamped = ti.max(ti.cast(-88.0, ti.f32), ti.min(ti.cast(88.0, ti.f32), v))
    return 1.0 / (1.0 + ti.exp(-clamped))


@ti.func
def nu_softplus(v: ti.f32) -> ti.f32:
    result = 0.0
    if v > 20.0:
        result = v
    elif v < -20.0:
        result = ti.exp(v)
    else:
        result = ti.log(1.0 + ti.exp(v))
    return result


@ti.func
def nu_gelu_exact(v: ti.f32) -> ti.f32:
    return 0.5 * v * (1.0 + nu_erf(v * ti.cast(0.7071067811865476, ti.f32)))


@ti.func
def nu_gelu_tanh(v: ti.f32) -> ti.f32:
    c1 = ti.cast(0.7978845608028654, ti.f32)
    c2 = ti.cast(0.044715, ti.f32)
    return 0.5 * v * (1.0 + ti.tanh(c1 * (v + c2 * v * v * v)))


@ti.func
def nu_activate(v: ti.f32, kind: ti.i32) -> ti.f32:
    out = v
    if kind == 1:
        out = ti.max(0.0, v)
    elif kind == 2:
        out = nu_stable_sigmoid(v)
    elif kind == 3:
        out = ti.tanh(v)
    elif kind == 4:
        out = nu_gelu_tanh(v)
    elif kind == 5:
        out = nu_gelu_exact(v)
    elif kind == 6:
        out = nu_softplus(v)
    return out


@ti.func
def nu_unary(v: ti.f32, code: ti.i32, lo: ti.f32, hi: ti.f32) -> ti.f32:
    out = v
    if code == 1:
        out = ti.max(0.0, v)
    elif code == 2:
        out = nu_stable_sigmoid(v)
    elif code == 3:
        out = ti.tanh(v)
    elif code == 4:
        out = nu_gelu_exact(v)
    elif code == 5:
        out = nu_gelu_tanh(v)
    elif code == 6:
        out = ti.sqrt(v)
    elif code == 7:
        out = ti.abs(v)
    elif code == 8:
        out = -v
    elif code == 9:
        out = nu_erf(v)
    elif code == 10:
        out = nu_softplus(v)
    elif code == 11:
        out = ti.floor(v)
    elif code == 12:
        out = ti.exp(v)
    elif code == 13:
        out = ti.log(v)
    elif code == 14:
        out = ti.sin(v)
    elif code == 15:
        out = ti.cos(v)
    elif code == 16:
        out = v * v
    elif code == 17:
        out = 1.0 / v
    elif code == 18:
        out = ti.ceil(v)
    elif code == 19:
        if v > 0.0:
            out = 1.0
        elif v < 0.0:
            out = -1.0
        else:
            out = 0.0
    elif code == 20:
        out = v if v >= 0.0 else lo * v
    elif code == 21:
        out = ti.max(lo, ti.min(hi, v))
    else:
        out = v
    return out


@ti.func
def nu_binop(a: ti.f32, b: ti.f32, code: ti.i32) -> ti.f32:
    out = 0.0
    if code == 0:
        out = a + b
    elif code == 1:
        out = a - b
    elif code == 2:
        out = a * b
    elif code == 3:
        out = a / b
    elif code == 4:
        out = ti.pow(a, b)
    elif code == 5:
        out = ti.min(a, b)
    elif code == 6:
        out = ti.max(a, b)
    elif code == 7:
        out = 1.0 if a < b else 0.0
    elif code == 8:
        out = 1.0 if a > b else 0.0
    elif code == 9:
        out = 1.0 if a == b else 0.0
    elif code == 10:
        out = a - b * ti.floor(a / b)
    elif code == 11:
        out = 1.0 if (a != 0.0 and b != 0.0) else 0.0
    return out


@ti.func
def nu_pad_list(v0: ti.i32, v1: ti.i32, v2: ti.i32, v3: ti.i32,
                v4: ti.i32, v5: ti.i32, v6: ti.i32, v7: ti.i32, axis: ti.i32) -> ti.i32:
    out = 1
    if axis == 0:
        out = v0
    elif axis == 1:
        out = v1
    elif axis == 2:
        out = v2
    elif axis == 3:
        out = v3
    elif axis == 4:
        out = v4
    elif axis == 5:
        out = v5
    elif axis == 6:
        out = v6
    elif axis == 7:
        out = v7
    return out
