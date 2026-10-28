"""Full-model accuracy checks for the currently runnable neural profiles."""

from __future__ import annotations

import collections
import json
import zipfile
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import pytest

from taichi_vision.taichi_aot.neural_universal.plan import Plan
from taichi_vision.taichi_aot.neural_universal.errors import UnsupportedONNXOperatorError
from taichi_vision.taichi_aot.neural_universal.runtime import (
    _build_add_sqrt_clip_fusions,
    _build_sub_sub_div_fusions,
    _build_sub_clip_sqrt_fusions,
    _build_unary_binary_fusions,
    UniversalSession,
    _check_backend_dtype_support,
    _find_pool_tcm,
)

ROOT = Path(__file__).resolve().parents[3]
LIGHTGLUE = ROOT / "database/Learning_Model/disk_lightglue_pipeline.ort.onnx"
RAFT = ROOT / "database/Learning_Model/optical_flow_estimation_raft_2023aug.onnx"
WEIGHTNET = ROOT / "database/Learning_Model/weightNet/weightnet_master.bundle"
UNARY_BINARY_CANDIDATE_POOL = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/unary_binary_candidate_pool_v2"
)
SUB_SUB_DIV_CANDIDATE_POOL = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
    / "cpu/sub_sub_div_candidate_pool_v5"
)
OPS_MATRIX = ROOT / "ops_matrix.json"
ATOL = 1e-6
LEGACY_WEIGHTNET_MATRIX_KEYS = {
    "weightnet_512_gpu_2b_1c_fp32.onnx",
    "weightnet_attention_1024_cpu_fp32.onnx",
    "weightnet_attention_1024_gpu_fp32.onnx",
    "weightnet_attention_256_cpu_fp32.onnx",
    "weightnet_attention_256_gpu_fp32.onnx",
    "weightnet_attention_512_cpu_fp32.onnx",
    "weightnet_attention_512_gpu_fp32.onnx",
    "weightnet_encoder_1024_cpu_fp32.onnx",
    "weightnet_encoder_1024_gpu_fp32.onnx",
    "weightnet_encoder_256_cpu_fp32.onnx",
    "weightnet_encoder_256_gpu_fp32.onnx",
    "weightnet_encoder_512_cpu_fp32.onnx",
    "weightnet_encoder_512_gpu_fp32.onnx",
}


def test_weightnet_bundle_operator_matrix_matches_manifest_and_preserves_legacy():
    matrix = json.loads(OPS_MATRIX.read_text(encoding="utf-8"))
    assert LEGACY_WEIGHTNET_MATRIX_KEYS <= set(matrix)

    with zipfile.ZipFile(WEIGHTNET) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        manifest_names = {item["file_name"] for item in manifest["models"].values()}
        bundle_names = {name for name in archive.namelist() if name.endswith(".onnx")}
        assert len(manifest_names) == 12
        assert bundle_names == manifest_names
        assert manifest_names <= set(matrix)

        for name in sorted(manifest_names):
            model = onnx.load_model_from_string(archive.read(name))
            counts = collections.Counter(
                f"{node.domain or 'ai.onnx'}::{node.op_type}"
                for node in model.graph.node
            )
            assert matrix[name] == dict(sorted(counts.items())), name


def test_target_models_build_native_plans():
    lightglue = Plan.from_model_bytes(LIGHTGLUE.read_bytes())
    raft = Plan.from_model_bytes(RAFT.read_bytes())
    with zipfile.ZipFile(WEIGHTNET) as archive:
        weightnet = Plan.from_model_bytes(archive.read("weightnet_512_cpu_1c_fp32.onnx"))

    assert len(lightglue.nodes) == 1387
    assert len(raft.nodes) == 4326
    assert len(weightnet.nodes) == 82


def test_vulkan_dtype_preflight_is_fail_closed_for_runtime_int64_models():
    lightglue = Plan.from_model_bytes(LIGHTGLUE.read_bytes())
    raft = Plan.from_model_bytes(RAFT.read_bytes())
    with zipfile.ZipFile(WEIGHTNET) as archive:
        weightnet = Plan.from_model_bytes(archive.read("weightnet_512_gpu_1c_fp32.onnx"))

    _check_backend_dtype_support(weightnet, "vulkan")
    with pytest.raises(UnsupportedONNXOperatorError) as exc:
        _check_backend_dtype_support(lightglue, "vulkan")
    assert "dynamic INT64" in str(exc.value)
    with pytest.raises(UnsupportedONNXOperatorError) as exc:
        _check_backend_dtype_support(raft, "vulkan")
    assert "dynamic INT64" in str(exc.value)


@pytest.mark.skipif(_find_pool_tcm("vulkan") is None, reason="compile the Vulkan neural pool first")
def test_weightnet_512_gpu_profile_vulkan_matches_directml_onnxruntime(tmp_path):
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_gpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    feeds = {
        "ref_img": rng.uniform(-1, 1, (1, 1, 512, 512)).astype(np.float32),
        "support_img": rng.uniform(-1, 1, (1, 1, 512, 512)).astype(np.float32),
    }
    options = ort.SessionOptions()
    options.enable_profiling = True
    options.profile_file_prefix = str(tmp_path / "weightnet_gpu_ort")
    oracle = ort.InferenceSession(model, options, providers=["DmlExecutionProvider"])
    expected = oracle.run(None, feeds)
    profile_path = Path(oracle.end_profiling())
    node_providers = {
        event.get("args", {}).get("provider", "unknown")
        for event in json.loads(profile_path.read_text(encoding="utf-8"))
        if event.get("cat") == "Node"
    }
    with UniversalSession(model, backend="vulkan") as session:
        actual = session.run(None, feeds)

    assert session.get_providers() == ["TaichiUniversal_VULKANExecutionProvider"]
    assert "DmlExecutionProvider" in oracle.get_providers()
    assert node_providers == {"DmlExecutionProvider"}
    for index, (got, want) in enumerate(zip(actual, expected)):
        got = np.asarray(got)
        want = np.asarray(want)
        assert got.shape == want.shape, f"output {index} shape mismatch"
        assert np.isfinite(got).all(), f"output {index} contains non-finite values"
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= ATOL, f"output {index} max_abs={max_abs:.3e} > {ATOL:.1e}"


@pytest.mark.skipif(_find_pool_tcm("cpu") is None, reason="compile the neural CPU pool first")
def test_weightnet_512_cpu_full_model_matches_onnxruntime():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    feeds = {
        "ref_img": rng.uniform(-1, 1, (1, 1, 512, 512)).astype(np.float32),
        "support_img": rng.uniform(-1, 1, (1, 1, 512, 512)).astype(np.float32),
    }
    expected = ort.InferenceSession(model, providers=["CPUExecutionProvider"]).run(None, feeds)
    with UniversalSession(model, backend="cpu") as session:
        actual = session.run(None, feeds)

    assert len(actual) == len(expected) == 2
    for index, (got, want) in enumerate(zip(actual, expected)):
        got = np.asarray(got)
        want = np.asarray(want)
        assert got.shape == want.shape, f"output {index} shape mismatch"
        assert np.isfinite(got).all(), f"output {index} contains non-finite values"
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= ATOL, f"output {index} max_abs={max_abs:.3e} > {ATOL:.1e}"


@pytest.mark.skipif(_find_pool_tcm("cpu") is None, reason="compile the neural CPU pool first")
def test_weightnet_1024_cpu_full_model_matches_onnxruntime():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_1024_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    feeds = {
        "ref_img": rng.uniform(-1, 1, (1, 1, 1024, 1024)).astype(np.float32),
        "support_img": rng.uniform(-1, 1, (1, 1, 1024, 1024)).astype(np.float32),
    }
    oracle = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)
    with UniversalSession(model, backend="cpu") as session:
        actual = session.run(None, feeds)

    assert oracle.get_providers() == ["CPUExecutionProvider"]
    assert len(actual) == len(expected) == 2
    for index, (got, want) in enumerate(zip(actual, expected)):
        got = np.asarray(got)
        want = np.asarray(want)
        assert got.shape == want.shape, f"output {index} shape mismatch"
        assert np.isfinite(got).all(), f"output {index} contains non-finite values"
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= ATOL, f"output {index} max_abs={max_abs:.3e} > {ATOL:.1e}"


def test_weightnet_bundle_profiles_exercise_guarded_fusion_candidates():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        for size in (512, 1024):
            for backend in ("cpu", "gpu"):
                profile_name = f"weightnet_{size}_{backend}_1c_fp32.onnx"
                model = archive.read(profile_name)
                plan = Plan.from_model_bytes(model)
                add_candidates = _build_add_sqrt_clip_fusions(plan, set(plan.output_names))
                sub_candidates = _build_sub_clip_sqrt_fusions(plan, set(plan.output_names))
                assert len(add_candidates) == 1
                assert len(sub_candidates) == 1
                if backend == "cpu":
                    triple_candidates = _build_sub_sub_div_fusions(
                        plan, set(plan.output_names)
                    )
                    expected_triples = 2 if "support" not in profile_name else 3
                    assert len(triple_candidates) == expected_triples
                add_index = next(iter(add_candidates))
                add_sqrt, add_clip, add_output, _low, _high = add_candidates[add_index]
                assert (plan.nodes[add_index].op, plan.nodes[add_sqrt].op,
                        plan.nodes[add_clip].op) == ("Add", "Sqrt", "Clip")
                assert add_output == plan.nodes[add_clip].output
                sub_index = next(iter(sub_candidates))
                sub_clip, sub_sqrt, sub_output, _clip_low, _clip_high = sub_candidates[sub_index]
                assert (plan.nodes[sub_index].op, plan.nodes[sub_clip].op,
                        plan.nodes[sub_sqrt].op) == ("Sub", "Clip", "Sqrt")
                assert sub_output == plan.nodes[sub_sqrt].output

                if backend == "cpu":
                    unary_binary = _build_unary_binary_fusions(
                        plan, set(plan.output_names)
                    )
                    assert len(unary_binary) == 1
                    unary_index = next(iter(unary_binary))
                    binary_index = unary_binary[unary_index][0]
                    assert (plan.nodes[unary_index].op, plan.nodes[binary_index].op) == (
                        "Softplus", "Add"
                    )


@pytest.mark.skipif(
    not (UNARY_BINARY_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated unary-binary candidate CPU pool first",
)
def test_weightnet_cpu512_unary_binary_candidate_matches_ort_and_saves_dispatch():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 512, 512)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    expected = ort.InferenceSession(
        model, providers=["CPUExecutionProvider"]
    ).run(None, feeds)

    def run_with_trace(pool_dir=None):
        calls = []
        with UniversalSession(model, backend="cpu", pool_dir=pool_dir) as session:
            original_run = session.module.run

            def traced_run(name, *args, **kwargs):
                calls.append(name)
                return original_run(name, *args, **kwargs)

            session.module.run = traced_run
            outputs = session.run(None, feeds)
            if pool_dir is not None:
                assert "nu_fused_unary_binary" in session.pool_graph_names
        return outputs, calls

    generic, generic_calls = run_with_trace()
    fused, fused_calls = run_with_trace(UNARY_BINARY_CANDIDATE_POOL)
    assert fused_calls.count("nu_fused_unary_binary") == 1
    assert len(fused_calls) == len(generic_calls) - 1
    for index, (got, baseline, want) in enumerate(zip(fused, generic, expected)):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all()
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= ATOL, f"output {index} max_abs={max_abs:.3e} > {ATOL:.1e}"


@pytest.mark.skipif(
    not (SUB_SUB_DIV_CANDIDATE_POOL / "neural_cpu.tcm").is_file(),
    reason="compile the isolated Sub-Sub-Div candidate CPU pool first",
)
@pytest.mark.parametrize("size", (512, 1024))
def test_weightnet_cpu_sub_sub_div_candidate_matches_ort_and_generic(size):
    member = f"weightnet_{size}_cpu_1c_fp32.onnx"
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read(member)
    rng = np.random.default_rng(20261025)
    shape = (1, 1, size, size)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    oracle = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)

    def run_with_trace(pool_dir=None):
        calls = []
        with UniversalSession(model, backend="cpu", pool_dir=pool_dir) as session:
            original_run = session.module.run

            def traced_run(name, *args, **kwargs):
                calls.append(name)
                return original_run(name, *args, **kwargs)

            session.module.run = traced_run
            outputs = session.run(None, feeds)
            if pool_dir is not None:
                assert "nu_fused_sub_sub_div" in session.pool_graph_names
        return outputs, calls

    generic, generic_calls = run_with_trace()
    fused, fused_calls = run_with_trace(SUB_SUB_DIV_CANDIDATE_POOL)
    expected_fusions = 2
    assert fused_calls.count("nu_fused_sub_sub_div") == expected_fusions
    assert len(fused_calls) == len(generic_calls) - 2 * expected_fusions
    errors = []
    exact = []
    for index, (got, baseline, want) in enumerate(zip(fused, generic, expected)):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all(), f"output {index} contains non-finite values"
        diff = got.astype(np.float64) - want.astype(np.float64)
        errors.append(diff)
        exact.append(np.count_nonzero(got == want))
        max_abs = float(np.max(np.abs(diff)))
        assert max_abs <= ATOL, f"output {index} max_abs={max_abs:.3e} > {ATOL:.1e}"
    flat_error = np.concatenate([value.ravel() for value in errors])
    print(
        f"Sub-Sub-Div WeightNet CPU{size}: max_abs={np.max(np.abs(flat_error)):.9g}, "
        f"rmse={np.sqrt(np.mean(flat_error * flat_error)):.9g}, "
        f"exact={sum(exact)}/{sum(np.asarray(x).size for x in fused)}, "
        f"dispatches={len(generic_calls)}->{len(fused_calls)}"
    )
