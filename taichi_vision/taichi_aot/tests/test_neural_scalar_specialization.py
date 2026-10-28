"""Focused typed-specialization and composed-graph accuracy gates."""

import numpy as np
import pytest
import taichi as ti

from taichi_vision.taichi_aot.neural_universal.scalar_specialization import (
    specialize_kernel, typed_scalar, scalar_binding_key,
)


@ti.kernel
def _rebound(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1),
             n: ti.i32, value: ti.f32):
    value = value + 0.25
    for i in range(n):
        y[i] = x[i] + value


@ti.kernel
def _signed_i64(y: ti.types.ndarray(ti.i64, 1), large: ti.i64):
    for i in range(1):
        y[i] = large


@ti.kernel
def _zero_bits(y: ti.types.ndarray(ti.i32, 1), positive: ti.f32, negative: ti.f32):
    for i in range(1):
        y[0] = ti.bit_cast(positive, ti.i32)
        y[1] = ti.bit_cast(negative, ti.i32)


@pytest.mark.parametrize("value,dtype", [(2**31, ti.i32), (2**63, ti.i64),
    (1.5, ti.i32), (float("inf"), ti.f32), (float("nan"), ti.f32),
    (1e39, ti.f32), (True, ti.i32), (1.0, ti.f64)])
def test_typed_scalar_rejects_invalid_binding(value, dtype):
    with pytest.raises(ValueError):
        typed_scalar(value, dtype)


def test_typed_scalar_preserves_f32_rounding_and_i64():
    assert typed_scalar(0.1, ti.f32) == ("f32", float(np.float32(0.1)))
    assert typed_scalar(2**62 + 1, ti.i64) == ("i64", 2**62 + 1)
    assert np.signbit(typed_scalar(-0.0, ti.f32)[1])
    assert scalar_binding_key(-0.0, ti.f32) != scalar_binding_key(0.0, ti.f32)


@pytest.mark.parametrize("value", [float("inf"), float("-inf"), float("nan")])
def test_default_capture_key_accepts_nonfinite_but_specialization_rejects(value):
    assert scalar_binding_key(value, ti.f32) == ("f32", np.asarray(value, np.float32).tobytes())
    args = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=1) for name in ("x", "y")]
    args += [ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32), ti.graph.Arg(ti.graph.ArgKind.SCALAR, "value", ti.f32)]
    with pytest.raises(ValueError, match="finite"):
        specialize_kernel(_rebound, args, {"n": 3, "value": value}, backend="cpu", fast_math=False)


@pytest.mark.parametrize("bound", [np.float32(np.inf), np.float32(np.nan)])
def test_default_model_capture_keeps_nonfinite_attribute_scalars(bound):
    from onnx import helper as h, TensorProto as T, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.static_graph import capture_universal_session
    model = h.make_model(h.make_graph([h.make_node("Clip", ["x", "low", "high"], ["y"])],
        "nonfinite_capture", [h.make_tensor_value_info("x", T.FLOAT, [3])],
        [h.make_tensor_value_info("y", T.FLOAT, [3])],
        [numpy_helper.from_array(np.array(-np.inf, np.float32), "low"),
         numpy_helper.from_array(np.array(bound, np.float32), "high")]),
        opset_imports=[h.make_opsetid("", 17)], ir_version=9)
    capture = capture_universal_session(model.SerializeToString(), {"x": np.ones(3, np.float32)}, backend="cpu")
    assert any(not np.isfinite(value) for value in capture["scalar_values"].values())
    for kernel, args in capture["dispatch_specs"]:
        with pytest.raises(ValueError, match="finite"):
            specialize_kernel(kernel, args, capture["scalar_values"], backend="cpu", fast_math=False)


def test_specialization_rejects_ndarray_binding_and_missing_scalar():
    args = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=1) for name in ("x", "y")]
    args += [ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32), ti.graph.Arg(ti.graph.ArgKind.SCALAR, "value", ti.f32)]
    with pytest.raises(ValueError, match="non-scalar"):
        specialize_kernel(_rebound, args, {"x": 1, "n": 3, "value": 0.1}, backend="cpu", fast_math=False)
    with pytest.raises(ValueError, match="missing scalar"):
        specialize_kernel(_rebound, args, {"n": 3}, backend="cpu", fast_math=False)


@pytest.mark.parametrize("policy", [{}, {"source_sha256": "bad"}, {"fast_math": True}])
def test_static_session_rejects_tampered_compiler_policy(policy):
    from taichi_vision.taichi_aot.neural_universal.static_session import StaticGraphSession
    session = StaticGraphSession.__new__(StaticGraphSession)
    with pytest.raises(ValueError, match="compiler policy/source"):
        session._validate_profile({"compiler_policy": policy})


def test_specialization_preserves_reassignment_arrays_and_large_i64():
    ti.reset()
    ti.init(arch=ti.cpu, fast_math=False, offline_cache=False)
    args = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=1) for name in ("x", "y")]
    args += [ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32), ti.graph.Arg(ti.graph.ArgKind.SCALAR, "value", ti.f32)]
    kernel, kept, _ = specialize_kernel(_rebound, args, {"n": 3, "value": 0.1}, backend="cpu", fast_math=False)
    assert [arg.name for arg in kept] == ["x", "y"]
    x, y = ti.ndarray(ti.f32, shape=3), ti.ndarray(ti.f32, shape=3)
    for values in ([1, 2, 3], [-3, -2, -1]):
        data = np.asarray(values, np.float32)
        x.from_numpy(data)
        kernel(x, y)
        np.testing.assert_array_equal(y.to_numpy(), data + np.float32(np.float32(0.1) + np.float32(0.25)))
    output = ti.ndarray(ti.i64, shape=1)
    large = 2**62 + 1
    kernel, _, _ = specialize_kernel(_signed_i64, [
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "y", ti.i64, ndim=1),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "large", ti.i64)], {"large": large}, backend="cpu", fast_math=False)
    kernel(output)
    assert output.to_numpy()[0] == large
    ti.reset()


def test_specialized_composed_aot_graph_matches_ort(tmp_path):
    import onnx
    import onnxruntime as ort
    from onnx import helper as h, TensorProto as T, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.kernels.elementwise import (
        nu_binary_flat, nu_clip_f32,
    )
    from taichi_vision.taichi_aot.neural_universal.static_graph import compile_static_graph_from_capture
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

    n = 37
    def array(name):
        return ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=1)
    def scalar(name, dtype):
        return ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, dtype)
    capture = {"scalar_values": {"n": n, "code": 0, "low": -0.125, "high": 0.3},
        "dispatch_specs": [
            (nu_binary_flat, [array("a"), array("b"), array("tmp"), scalar("n", ti.i32), scalar("code", ti.i32)]),
            (nu_clip_f32, [array("tmp"), array("y"), scalar("n", ti.i32), scalar("low", ti.f32), scalar("high", ti.f32)]),
        ]}
    ti.reset()
    module = compile_static_graph_from_capture(capture, "cpu", "nu_toy", specialize_scalars=True, fast_math=False)
    zero_args = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bits", ti.i32, ndim=1),
        scalar("positive", ti.f32), scalar("negative", ti.f32)]
    zero_kernel, zero_kept, _ = specialize_kernel(_zero_bits, zero_args,
        {"positive": 0.0, "negative": -0.0}, backend="cpu", fast_math=False)
    zero_graph = ti.graph.GraphBuilder()
    zero_graph.dispatch(zero_kernel, *zero_kept)
    module.add_graph("nu_zero_bits", zero_graph.compile())
    artifact = tmp_path / "toy_cpu.tcm"
    archive_module(module, artifact)
    assert artifact.is_file()
    assert len(capture["specialization_keys"]) == 2
    graph = ti.graph.GraphBuilder()
    for kernel, args in capture["dispatch_specs"]:
        specialized, kept, key = specialize_kernel(kernel, args, capture["scalar_values"], backend="cpu", fast_math=False)
        assert specialize_kernel(kernel, args, capture["scalar_values"], backend="cpu", fast_math=False)[0] is specialized
        graph.dispatch(specialized, *kept)
    compiled = graph.compile()
    rng = np.random.default_rng(20261027)
    feeds = {name: rng.normal(size=n).astype(np.float32) for name in ("a", "b")}
    buffers = {name: ti.ndarray(ti.f32, shape=n) for name in ("a", "b", "tmp", "y")}
    for name, values in feeds.items():
        buffers[name].from_numpy(values)
    compiled.run(buffers)
    model = h.make_model(h.make_graph([
        h.make_node("Add", ["a", "b"], ["tmp"]),
        h.make_node("Clip", ["tmp", "low", "high"], ["y"])], "toy",
        [h.make_tensor_value_info(name, T.FLOAT, [n]) for name in ("a", "b")],
        [h.make_tensor_value_info("y", T.FLOAT, [n])],
        [numpy_helper.from_array(np.array(value, np.float32), name) for name, value in [("low", -0.125), ("high", 0.3)]]),
        opset_imports=[h.make_opsetid("", 17)], ir_version=9)
    expected = ort.InferenceSession(model.SerializeToString(), providers=["CPUExecutionProvider"]).run(None, feeds)[0]
    np.testing.assert_array_equal(buffers["y"].to_numpy(), expected)
    # Execute the archived TCM through the native bridge, not only Python graphs.
    from taichi_vision.taichi_aot.engine import AOTEngine
    engine = AOTEngine(arch="cpu")
    native = engine.load(str(artifact))
    native_buffers = {name: engine.upload(values, is_vector=False) for name, values in feeds.items()}
    native_buffers.update({name: engine.allocate((n,), dtype=np.float32, is_vector=False) for name in ("tmp", "y")})
    bits = engine.allocate((2,), dtype=np.int32, is_vector=False)
    try:
        native.run("nu_toy", **native_buffers)
        np.testing.assert_array_equal(native_buffers["y"].to_numpy().reshape(-1), expected)
        native.run("nu_zero_bits", bits=bits)
        np.testing.assert_array_equal(bits.to_numpy().reshape(-1).view(np.uint32), [0, 0x80000000])
    finally:
        engine.sync()
        for buffer in [*native_buffers.values(), bits]:
            buffer.destroy()
    ti.reset()
