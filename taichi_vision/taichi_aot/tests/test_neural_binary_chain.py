"""Native saved-TCM gates for opt-in generic adjacent binary regions."""

from types import SimpleNamespace as NS
import hashlib

import numpy as np
import pytest
import taichi as ti

from taichi_vision.taichi_aot.neural_universal.binary_chain import rewrite_events


def _fixture():
    nodes = [NS(index=0, op="Sub", domain="ai.onnx", attrs={}, inputs=["a", "b"], outputs=["t"], output="t"),
             NS(index=1, op="Mul", domain="ai.onnx", attrs={}, inputs=["t", "t"], outputs=["y"], output="y")]
    a, b, t, y = [object() for _ in range(4)]
    events = [{"graph": "nu_binary_flat", "step": 0, "kwargs": {"a": a, "b": b, "y": t, "code": 1, "n": 7}},
              {"graph": "nu_binary_flat", "step": 1, "kwargs": {"a": t, "b": t, "y": y, "code": 2, "n": 7}}]
    plan = NS(nodes=nodes, dtypes={name: "f32" for name in ["a", "b", "t", "y"]}, producer={"t": nodes[0], "y": nodes[1]})
    return events, plan, {name: (7,) for name in plan.dtypes}


def test_repeated_intermediate_has_one_consumer_node():
    events, plan, shapes = _fixture()
    rewritten, regions = rewrite_events(events, plan, shapes, {"y"})
    assert len(rewritten) == 1 and len(regions) == 1
    assert regions[0]["ops"] == ["Sub", "Mul"]


@pytest.mark.parametrize("failure", ["domain", "attrs", "dtype", "missing_shape", "broadcast", "fanout", "requested", "alias", "not_ready", "nonadjacent"])
def test_invalid_region_stays_unfused(failure):
    events, plan, shapes = _fixture()
    requested = {"y"}
    if failure == "domain": plan.nodes[0].domain = "custom"
    elif failure == "attrs": plan.nodes[0].attrs = {"broadcast": 1}
    elif failure == "dtype": plan.dtypes["a"] = "i32"
    elif failure == "missing_shape": del shapes["a"]
    elif failure == "broadcast": shapes["b"] = (3,)
    elif failure == "fanout": plan.nodes.append(NS(index=2, inputs=["t"]))
    elif failure == "requested": requested.add("t")
    elif failure == "alias": events[1]["kwargs"]["y"] = events[0]["kwargs"]["a"]
    elif failure == "not_ready": plan.producer["a"] = NS(index=3)
    elif failure == "nonadjacent": events.insert(1, {"graph": "unsupported"})
    rewritten, regions = rewrite_events(events, plan, shapes, requested)
    assert not regions
    assert rewritten == events


@pytest.mark.parametrize("mode", ["mul_add", "sub_square", "sub_sub"])
def test_native_binary_chain_preserves_materialization_and_broadcast(tmp_path, mode):
    import onnxruntime as ort
    from onnx import helper as h, TensorProto as T
    from taichi_vision.taichi_aot.neural_universal.static_graph import capture_universal_session, write_static_profile
    from taichi_vision.taichi_aot.neural_universal.static_session import StaticGraphSession

    if mode == "sub_square":
        nodes = [h.make_node("Sub", ["a", "b"], ["t"]), h.make_node("Mul", ["t", "t"], ["y"])]
        feed = {"a": np.array([[1e20, np.inf, -np.inf, np.nan, 0.0, -0.0, 1.0000001]], np.float32),
                "b": np.array([[-0.0]], np.float32)}
    elif mode == "mul_add":
        nodes = [h.make_node("Mul", ["a", "b"], ["t"]), h.make_node("Add", ["t", "c"], ["y"])]
        feed = {"a": np.array([[1.0000001, 1e30, np.inf, -np.inf, np.nan, -0.0, 0.0]], np.float32),
                "b": np.array([[1.0000001, 1e30, 0.0, 1.0, 1.0, 1.0, -1.0]], np.float32),
                "c": np.array([[-1.0000002, -np.inf, 1.0, np.inf, 1.0, -0.0, -0.0]], np.float32)}
    else:
        nodes = [h.make_node("Sub", ["a", "b"], ["t"]), h.make_node("Sub", ["t", "c"], ["y"])]
        feed = {"a": np.array([[1e20, 3e38, np.inf, -np.inf, np.nan, -0.0, 0.0]], np.float32),
                "b": np.array([[1e20, -3e38, np.inf, -np.inf, 1.0, 0.0, -0.0]], np.float32),
                "c": np.array([[3.0, np.inf, 1.0, np.inf, 1.0, 0.0, -0.0]], np.float32)}
    model = h.make_model(h.make_graph(nodes, "binary_chain", [h.make_tensor_value_info(name, T.FLOAT, list(value.shape)) for name, value in feed.items()],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 7])]), opset_imports=[h.make_opsetid("", 17)], ir_version=9)
    raw = model.SerializeToString()
    capture = capture_universal_session(raw, feed, backend="cpu", enable_binary_chains=True)
    assert len(capture["binary_regions"]) == 1
    assert len(capture["events"]) == 1
    event = capture["events"][0]
    output_arg = capture["graph_buffer_args"][id(event["kwargs"]["y"])]
    assert all(capture["graph_buffer_args"][identity] != output_arg for identity in event["external_buffer_ids"])
    ti.reset()
    profile_parent = tmp_path / hashlib.sha256(raw).hexdigest() / "cpu"
    folder = profile_parent / "fused"
    write_static_profile(capture, raw, "cpu", folder, "nu_chain_toy", specialize_scalars=True, fast_math=False)
    ti.reset()
    baseline_capture = capture_universal_session(raw, feed, backend="cpu")
    write_static_profile(baseline_capture, raw, "cpu", profile_parent / "unfused", "nu_unfused_toy", specialize_scalars=True, fast_math=False)
    ti.reset()
    reference = ort.InferenceSession(raw, providers=["CPUExecutionProvider"]).run(None, feed)[0]
    with StaticGraphSession(raw, backend="cpu", profile_root=tmp_path, profile_variant="unfused") as session:
        assert session.fast_path_active, session.last_fallback_reason
        baseline = session.run(None, feed)[0]
    with StaticGraphSession(raw, backend="cpu", profile_root=tmp_path, profile_variant="fused") as session:
        assert session.fast_path_active, session.last_fallback_reason
        actual = session.run(None, feed)[0]
        assert session.last_run_used_fast_path
    np.testing.assert_array_equal(np.isnan(actual), np.isnan(reference))
    np.testing.assert_array_equal(np.isnan(actual), np.isnan(baseline))
    np.testing.assert_array_equal(actual.view(np.uint32), baseline.view(np.uint32))
    valid = ~np.isnan(reference)
    np.testing.assert_array_equal(actual.view(np.uint32)[valid], baseline.view(np.uint32)[valid])
    np.testing.assert_array_equal(actual.view(np.uint32)[valid], reference.view(np.uint32)[valid])
    # Strict mul/add must not contract the cancellation case to an FMA.
    if mode == "mul_add":
        assert actual[0, 0].view(np.uint32) == np.float32(0.0).view(np.uint32)
        assert np.isnan(actual[0, 1])  # overflow to materialized Inf, then + -Inf
    elif mode == "sub_sub":
        assert actual[0, 0] == np.float32(-3.0)
        assert np.isnan(actual[0, 1])
    llvm = "\n".join(path.read_text() for path in (folder / ".cpu_aot_cache").rglob("*.ll"))
    assert llvm and "llvm.fma." not in llvm and "llvm.fmuladd." not in llvm
    assert "fmul fast " not in llvm and "fadd fast " not in llvm


def test_capture_uses_logical_reshape_shape_and_replans_broadcast_scalar_lifetime():
    from onnx import helper as h, TensorProto as T, numpy_helper
    from taichi_vision.taichi_aot.neural_universal.static_graph import capture_universal_session
    nodes = [h.make_node("Reshape", ["a", "shape"], ["reshaped"]),
             h.make_node("Sub", ["reshaped", "b"], ["t"]),
             h.make_node("Mul", ["t", "t"], ["square"]),
             h.make_node("ReduceMean", ["g"], ["scalar"], axes=[0], keepdims=1),
             h.make_node("Mul", ["scalar", "square"], ["scaled"]),
             h.make_node("Add", ["scaled", "c"], ["shifted"]),
             h.make_node("ReduceMean", ["shifted"], ["y"], keepdims=0)]
    feed = {"a": np.ones((1, 1, 2, 2, 2, 2), np.float32), "b": np.ones((1, 1, 2, 2), np.float32),
            "g": np.ones((2,), np.float32), "c": np.ones((1,), np.float32)}
    model = h.make_model(h.make_graph(nodes, "alias_lifetime", [h.make_tensor_value_info(name, T.FLOAT, list(value.shape)) for name, value in feed.items()],
        [h.make_tensor_value_info("y", T.FLOAT, [])],
        [numpy_helper.from_array(np.array([1, 4, 2, 2], np.int64), "shape")]), opset_imports=[h.make_opsetid("", 17)], ir_version=9)
    capture = capture_universal_session(model.SerializeToString(), feed, backend="cpu", enable_binary_chains=True)
    assert len(capture["binary_regions"]) == 2
    first = capture["binary_regions"][0]
    assert first["external_names"][0] == "reshaped"
    assert first["external_shapes"][0] == (1, 4, 2, 2)
    for event in capture["events"]:
        if "external_buffer_ids" in event:
            output = capture["graph_buffer_args"][id(event["kwargs"]["y"])]
            assert all(capture["graph_buffer_args"][identity] != output for identity in event["external_buffer_ids"])
