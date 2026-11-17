"""The public operator API: `neural.ops.relu(x)` and friends.

Every reference is NumPy, computed here rather than restated from the Rust code, so
a wrong implementation cannot agree with itself.
"""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("taichi.taichi_python")

import taichi_vision.neural as neural  # noqa: E402

ops = neural.ops


def test_ops_is_reachable_from_the_package():
    # The advertised surface: `import taichi_vision.neural as neural` then
    # `neural.ops.relu`. Anything else and the documentation is wrong.
    assert hasattr(neural, "ops")
    assert callable(neural.ops.relu)


def test_relu_matches_numpy():
    x = np.asarray([-2.0, -0.5, 0.0, 0.5, 2.0], dtype=np.float32)
    np.testing.assert_array_equal(ops.relu(x), np.maximum(x, 0))


def test_tanh_matches_numpy():
    # The mistake this guards against is `tanh(2x)`, which reached a real model.
    x = np.linspace(-3, 3, 25, dtype=np.float32)
    np.testing.assert_allclose(ops.tanh(x), np.tanh(x), rtol=1e-6, atol=1e-6)


def test_sigmoid_matches_numpy():
    x = np.linspace(-6, 6, 25, dtype=np.float32)
    expected = 1.0 / (1.0 + np.exp(-x))
    np.testing.assert_allclose(ops.sigmoid(x), expected, rtol=1e-6, atol=1e-6)


def test_gelu_default_is_the_exact_form():
    # ONNX's default is the erf definition. Comparing against scipy-free erf here
    # keeps the assertion independent of the primitive's polynomial.
    from math import erf, sqrt

    x = np.asarray([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float32)
    expected = np.asarray(
        [0.5 * v * (1.0 + erf(float(v) / sqrt(2.0))) for v in x], dtype=np.float32
    )
    np.testing.assert_allclose(ops.gelu(x), expected, rtol=1e-5, atol=1e-6)


def test_gelu_tanh_differs_from_exact_but_stays_close():
    x = np.asarray([0.5, 1.0, -1.5], dtype=np.float32)
    exact = ops.gelu(x)
    approximate = ops.gelu(x, approximate="tanh")
    assert not np.array_equal(exact, approximate)
    np.testing.assert_allclose(approximate, exact, atol=5e-3)


def test_gelu_refuses_an_unknown_approximation():
    with pytest.raises(neural.NeuralError, match="'none' or 'tanh'"):
        ops.gelu(np.zeros(2, dtype=np.float32), approximate="fast")


@pytest.mark.parametrize("name", ["add", "sub", "mul", "div", "minimum", "maximum"])
def test_binary_matches_numpy(name):
    rng = np.random.default_rng(21)
    a = rng.uniform(0.5, 3.0, size=(4,)).astype(np.float32)
    b = rng.uniform(0.5, 3.0, size=(4,)).astype(np.float32)
    expected = {
        "add": a + b,
        "sub": a - b,
        "mul": a * b,
        "div": a / b,
        "minimum": np.minimum(a, b),
        "maximum": np.maximum(a, b),
    }[name]
    np.testing.assert_allclose(getattr(ops, name)(a, b), expected, rtol=1e-6)


def test_binary_broadcasts_like_onnx():
    a = np.arange(6, dtype=np.float32).reshape(2, 3)
    b = np.asarray([10.0, 20.0, 30.0], dtype=np.float32)
    np.testing.assert_array_equal(ops.add(a, b), a + b)
    np.testing.assert_array_equal(ops.mul(a, np.float32(2.0)), a * 2.0)


def test_mod_takes_the_divisor_sign():
    a = np.asarray([-3.0, 3.0], dtype=np.float32)
    b = np.asarray([2.0, -2.0], dtype=np.float32)
    np.testing.assert_allclose(ops.mod(a, b), np.mod(a, b))


def test_clip_with_one_bound_leaves_the_other_open():
    x = np.asarray([-100.0, -1.0, 0.0, 1.0, 100.0], dtype=np.float32)
    np.testing.assert_array_equal(ops.clip(x, min=-1.0), np.maximum(x, -1.0))
    np.testing.assert_array_equal(ops.clip(x, max=1.0), np.minimum(x, 1.0))


def test_clip_refuses_inverted_bounds():
    with pytest.raises(neural.NeuralError, match="greater than"):
        ops.clip(np.zeros(2, dtype=np.float32), min=2.0, max=1.0)


def test_where_matches_numpy():
    condition = np.asarray([1, 0, 1, 0], dtype=np.int32)
    x = np.asarray([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    y = np.asarray([9.0, 8.0, 7.0, 6.0], dtype=np.float32)
    np.testing.assert_array_equal(
        ops.where(condition, x, y), np.where(condition.astype(bool), x, y)
    )


def test_where_accepts_a_bool_condition():
    # A caller writing `np.where(x > 0, ...)` has a bool array; widening it here is
    # the friendly behaviour and matches what the primitive reads.
    condition = np.asarray([True, False])
    x = np.asarray([1.0, 2.0], dtype=np.float32)
    y = np.asarray([0.0, 0.0], dtype=np.float32)
    np.testing.assert_array_equal(ops.where(condition, x, y), [1.0, 0.0])


def test_an_integer_array_is_refused_rather_than_promoted():
    # A promotion rule invented here would diverge from ONNX's; refusing keeps the
    # conversion the caller's visible decision.
    with pytest.raises(neural.NeuralError, match="expected a float array"):
        ops.relu(np.asarray([1, 2], dtype=np.int32))


def test_a_float64_input_is_narrowed_and_returns_float32():
    result = ops.relu(np.asarray([-1.0, 2.0], dtype=np.float64))
    assert result.dtype == np.float32
    np.testing.assert_array_equal(result, [0.0, 2.0])


def test_the_result_is_a_new_array():
    x = np.asarray([-1.0, 2.0], dtype=np.float32)
    out = ops.relu(x)
    assert out is not x
    np.testing.assert_array_equal(x, [-1.0, 2.0], "the input must not be modified")


def test_capabilities_reports_the_extension_view():
    report = ops.capabilities()
    assert "plan_ready" in report
    assert "Conv" in report["plan_ready"]


def test_available_lists_every_exposed_name():
    names = ops.available()
    assert "relu" in names and "add" in names
    assert names == sorted(names)
