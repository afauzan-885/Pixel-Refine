"""Native multi-output SSA semantics and admission/storage regressions."""

import copy
import hashlib

import numpy as np
import pytest
import taichi as ti


def _model_and_feed():
    from onnx import helper as h, numpy_helper, TensorProto as T
    nodes = [h.make_node("Add", ["a", "epsilon"], ["v"]),
             h.make_node("Sqrt", ["v"], ["r"]),
             h.make_node("Clip", ["r", "low", "high"], ["denominator"]),
             h.make_node("Sub", ["b", "c"], ["d"]),
             h.make_node("Sub", ["a", "c"], ["t"]),
             h.make_node("Sub", ["t", "d"], ["u"]),
             h.make_node("Div", ["u", "denominator"], ["first"]),
             h.make_node("Div", ["d", "denominator"], ["second"]),
             h.make_node("Div", ["b", "c"], ["third"])]
    shape = (2, 8)
    tiny = np.nextafter(np.float32(0), np.float32(1))
    feed = {
        "a": np.array([4, -4, np.nan, 0., -0., np.inf, -np.inf, tiny, 3e38, 1., -1., 1e20, 1e20, 0., 2., 3.], np.float32).reshape(shape),
        "b": np.array([1, 2, 0, 1, -1, np.inf, np.inf, tiny, 3e38, 1., -1., 1e20, 1e20, -0., 2., 3.], np.float32).reshape(shape),
        "c": np.array([0., -0., 0., -0., 0., np.inf, -np.inf, tiny, -3e38, -0., 0., 1e20, 3., 0., 1., 2.], np.float32).reshape(shape),
        "epsilon": np.array([-0.], np.float32),
    }
    outputs = ["denominator", "first", "second", "third"]
    model = h.make_model(h.make_graph(nodes, "multi_output", [h.make_tensor_value_info(name, T.FLOAT, list(value.shape)) for name, value in feed.items()],
        [h.make_tensor_value_info(name, T.FLOAT, list(shape)) for name in outputs],
        [numpy_helper.from_array(np.array(-0., np.float32), "low"),
         numpy_helper.from_array(np.array(np.finfo(np.float32).max, np.float32), "high")]),
        opset_imports=[h.make_opsetid("", 17)], ir_version=9)
    return model.SerializeToString(), feed


@pytest.fixture(scope="module")
def native_results(tmp_path_factory):
    import onnxruntime as ort
    from taichi_vision.taichi_aot.neural_universal.static_graph import capture_universal_session, write_static_profile
    from taichi_vision.taichi_aot.neural_universal.static_session import StaticGraphSession
    tmp_path = tmp_path_factory.mktemp("native_multi_output")
    raw, stress = _model_and_feed()
    feed = {name: value.copy() for name, value in stress.items()}
    feed["a"][0, 7] = np.finfo(np.float32).tiny
    feed["epsilon"][0] = np.float32(0.0)
    oracle = ort.InferenceSession(raw, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feed)
    stress_expected = oracle.run(None, stress)
    outputs, captures = {}, {}
    for name, pairs, multi in [("unfused", False, False), ("pair", True, False), ("multi", True, True)]:
        capture = capture_universal_session(raw, feed, backend="cpu", enable_binary_chains=pairs, enable_pointwise_ssa=multi)
        captures[name] = capture
        if multi:
            assert len(capture["events"]) < len(captures["pair"]["events"])
            assert any(len(region["outputs"]) == 4 for region in capture["pointwise_regions"])
            for event in capture["events"]:
                if "output_buffer_ids" in event:
                    writes = [capture["graph_buffer_args"][identity] for identity in event["output_buffer_ids"]]
                    reads = [capture["graph_buffer_args"][identity] for identity in event["external_buffer_ids"]]
                    assert len(writes) == len(set(writes)) and not set(writes) & set(reads)
        ti.reset()
        folder = tmp_path / hashlib.sha256(raw).hexdigest() / "cpu" / name
        write_static_profile(capture, raw, "cpu", folder, "nu_ssa_" + name, specialize_scalars=True, fast_math=False)
        ti.reset()
        with StaticGraphSession(raw, backend="cpu", profile_root=tmp_path, profile_variant=name) as session:
            assert session.fast_path_active, session.last_fallback_reason
            outputs[name] = {"normal": session.run(None, feed), "stress": session.run(None, stress)}
            assert session.last_run_used_fast_path
    np.savez(tmp_path / "stress_inputs.npz", **stress)
    np.savez(tmp_path / "stress_outputs.npz", **{f"{name}_{index}": value.view(np.uint32)
        for name, results in outputs.items() for index, value in enumerate(results["stress"])},
        **{f"ort_{index}": value.view(np.uint32) for index, value in enumerate(stress_expected)})
    return outputs, expected, stress_expected, tmp_path, raw


def test_native_saved_tcm_multi_output_matches_unfused_pair_and_ort(native_results):
    outputs, expected, _, tmp_path, raw = native_results
    for result in (outputs["pair"]["normal"], outputs["multi"]["normal"]):
        for actual, baseline, reference in zip(result, outputs["unfused"]["normal"], expected):
            np.testing.assert_array_equal(actual.view(np.uint32), baseline.view(np.uint32))
            np.testing.assert_array_equal(np.isnan(actual), np.isnan(reference))
            np.testing.assert_array_equal(np.isposinf(actual), np.isposinf(reference))
            np.testing.assert_array_equal(np.isneginf(actual), np.isneginf(reference))
            finite = np.isfinite(reference)
            np.testing.assert_allclose(actual[finite], reference[finite], atol=1e-6, rtol=0)
        # Clip ties preserve captured baseline behavior, which can choose +0
        # where ORT chooses -0. Float tolerance is still zero error. Raw Div
        # signed-zero semantics must match ORT exactly on the third output.
        zeros = expected[3] == 0
        np.testing.assert_array_equal(result[3].view(np.uint32)[zeros], expected[3].view(np.uint32)[zeros])
    llvm = "\n".join(path.read_text() for path in (tmp_path / hashlib.sha256(raw).hexdigest() / "cpu/multi/.cpu_aot_cache").rglob("*.ll"))
    assert llvm and "llvm.fma." not in llvm and "llvm.fmuladd." not in llvm
    assert "fmul fast " not in llvm and "fdiv fast " not in llvm


def test_known_baseline_subnormal_and_clip_tie_ort_limitations(native_results):
    outputs, _, reference, _, _ = native_results
    baseline = outputs["unfused"]["stress"]
    for name in ("pair", "multi"):
        for actual, original in zip(outputs[name]["stress"], baseline):
            np.testing.assert_array_equal(actual.view(np.uint32), original.view(np.uint32))
    # Preserve and expose the existing failure; no masks or relaxed tolerance.
    assert baseline[0].view(np.uint32)[0, 7] == 0
    assert reference[0].view(np.uint32)[0, 7] == 0x1A3504F3
    for index in (1, 2):
        assert np.isnan(baseline[index][0, 7])
        assert np.isfinite(reference[index][0, 7]) and reference[index][0, 7] == 0
    assert baseline[3].view(np.uint32)[0, 7] == reference[3].view(np.uint32)[0, 7] == 0x3F800000
    # A tied Clip zero sign can propagate into later division signs. This is
    # deliberately retained as failing ORT stress coverage, not masked away.
    assert baseline[0].view(np.uint32)[0, 4] == 0
    assert reference[0].view(np.uint32)[0, 4] == 0x80000000
    assert any(baseline[index].view(np.uint32)[0, 4] != reference[index].view(np.uint32)[0, 4] for index in (1, 2))


@pytest.mark.parametrize("mutation", ["unary_code", "compound_graph", "compound_topology", "domain", "dtype", "shape", "extent"])
def test_invalid_capture_descriptor_is_region_barrier(mutation):
    from taichi_vision.taichi_aot.neural_universal.static_graph import capture_universal_session
    from taichi_vision.taichi_aot.neural_universal.pointwise_ssa import normalize
    from taichi_vision.taichi_aot.neural_universal.kernels import ALL_KERNELS
    raw, feed = _model_and_feed()
    capture = capture_universal_session(raw, feed, backend="cpu", enable_pointwise_ssa=False, enable_binary_chains=False)
    # Obtain compile-only logical shapes without running any numerical kernels.
    import onnx
    model = onnx.shape_inference.infer_shapes(onnx.load_model_from_string(raw))
    shapes = {v.name: tuple(int(d.dim_value) for d in v.type.tensor_type.shape.dim) for v in [*model.graph.input, *model.graph.value_info, *model.graph.output]}
    shapes.update({name: tuple(value.shape) for name, value in capture["plan"].constants.items()})
    event = {**capture["events"][0], "kwargs": dict(capture["events"][0]["kwargs"])}
    plan = capture["plan"]
    if mutation == "unary_code": event["graph"] = "nu_unary_f32";event["kwargs"]["code"] = 999
    elif mutation == "compound_graph": event["graph"] = "nu_sub_clip_sqrt_broadcast"
    elif mutation == "compound_topology": plan.producer["denominator"].inputs[0] = "v"
    elif mutation == "domain": plan.nodes[0].domain = "custom"
    elif mutation == "dtype": plan.dtypes["a"] = "i32"
    elif mutation == "shape": shapes.pop("a")
    elif mutation == "extent": event["kwargs"]["n"] += 1
    with pytest.raises((ValueError, KeyError)):
        normalize(event, plan, shapes, capture["metadata"], {kernel.__name__: kernel for kernel in ALL_KERNELS})


def _inventory_profile():
    from types import SimpleNamespace as NS
    from taichi_vision.taichi_aot.neural_universal.static_session import StaticGraphSession
    from taichi_vision.taichi_aot.neural_universal.static_graph import _kernel_source_fingerprint, _configured_runtime_abi, _target_identity
    from taichi_vision.taichi_aot.neural_universal.scalar_specialization import compiler_fingerprint, POLICY as SCALAR
    from taichi_vision.taichi_aot.neural_universal.pointwise_ssa import POLICY
    mode = "pointwise_ssa_scalar_specialized"
    shape = [2, 8]
    profile = {"schema_version": 2, "compiler_schema_version": 2, "compiler_mode": mode, "profile_variant": "multi",
        "compiler_policy": {"schema_version": 2, "mode": mode, "source_sha256": compiler_fingerprint(), "fast_math": False,
            "scalar_specialization": SCALAR, "original_scalar_values": {}, "specialization_keys": ["0" * 64], "pointwise_ssa": POLICY, "binary_chains": None},
        "scalar_values": {}, "dispatches": 1, "original_dispatch_count": 3, "binary_regions": [],
        "pointwise_regions": [{"policy": POLICY, "source_event_count": 3, "operation_count": 3,
            "external_names": ["input"], "outputs": ["first", "second"], "shape": shape,
            "source_event_indices": [0, 1, 2], "source_steps": [0, 1, 2], "operations": [["Add"], ["Sub"], ["Div"]]}],
        "logical_shapes": {"input": shape, "first": shape, "second": shape}, "model_sha256": "synthetic_inventory_unit",
        "backend": "cpu", "runtime_abi": _configured_runtime_abi(), "kernel_sources_sha256": _kernel_source_fingerprint(),
        "target_identity": _target_identity("cpu", ""), "model_input_dtypes": {"input": "f32"}, "model_input_shapes": {"input": shape},
        "outputs": {"first": {}, "second": {}}, "tcm_sha256": "0" * 64, "constants_sha256": "0" * 64}
    session = StaticGraphSession.__new__(StaticGraphSession)
    session.profile_variant = "multi";session.model_sha256 = profile["model_sha256"];session.backend = "cpu";session.engine = NS(gpu_name="")
    session.plan = NS(dtypes={"input": "f32"}, input_names=["input"], output_names=["first", "second"])
    return session, profile


def test_valid_synthetic_inventory_unit():
    session, profile = _inventory_profile()
    session._validate_profile(profile)


@pytest.mark.parametrize("mutation", ["output_type", "output_empty", "output_missing", "output_shape", "duplicate_output", "input_budget", "missing_shapes", "float_shape", "event_budget", "op_budget", "source_indices", "operations"])
def test_malformed_pointwise_inventory_rejected(mutation):
    session, profile = _inventory_profile();region = profile["pointwise_regions"][0]
    if mutation == "output_type": region["outputs"][0] = {"bad": 1}
    elif mutation == "output_empty": region["outputs"][0] = ""
    elif mutation == "output_missing": region["outputs"][0] = "unknown"
    elif mutation == "output_shape": profile["logical_shapes"]["first"] = [16]
    elif mutation == "duplicate_output": region["outputs"][1] = "first"
    elif mutation == "input_budget": region["external_names"] = ["input"] * 17
    elif mutation == "missing_shapes": profile.pop("logical_shapes")
    elif mutation == "float_shape": region["shape"] = [2., 8]
    elif mutation == "event_budget": region["source_event_count"] = 13
    elif mutation == "op_budget": region["operation_count"] = 25
    elif mutation == "source_indices": region["source_event_indices"] = [0, 2, 3]
    elif mutation == "operations": region["operations"][0] = ["Conv"]
    with pytest.raises(ValueError): session._validate_profile(profile)
