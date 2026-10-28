"""Tests for liveness planning and Taichi's multi-dispatch AOT graph API."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import zipfile
import json
import shutil

import numpy as np
import onnxruntime as ort
import pytest

from taichi_vision.taichi_aot.neural_universal.liveness import (
    BufferSlot,
    LiveInterval,
    LivenessPlan,
    assign_liveness_slots,
)
from taichi_vision.taichi_aot.neural_universal.runtime import _find_pool_tcm
from taichi_vision.taichi_aot.neural_universal import (
    StaticGraphSession,
    StaticWeightNetSession,
)

ROOT = Path(__file__).resolve().parents[3]
WEIGHTNET = ROOT / "database/Learning_Model/weightNet/weightnet_master.bundle"
PROFILE_DIR = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184/cpu"
)
PROFILE_1024_DIR = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "00b2a16d77317c28f1c765b09a61edfa272d0bc7e0137c027ecc48f1ac0ad6e0/cpu"
)
PROFILE_GPU512_DIR = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / "272fcea44b99d850ad6267ed38f50704b4d383ee7e8589772c63c4b9542023ae/vulkan"
)


def test_static_graph_session_public_name_keeps_compatibility_alias():
    assert StaticWeightNetSession is StaticGraphSession
ATOL = 1e-6


def test_liveness_reuses_only_non_overlapping_same_dtype_intervals():
    intervals = [
        LiveInterval("first", "f32", 16, 0, 2),
        LiveInterval("touching", "f32", 8, 2, 4),
        LiveInterval("later", "f32", 32, 5, 6),
        LiveInterval("integer", "i32", 4, 3, 4),
        LiveInterval("pinned_input", "f32", 64, 0, 6, pinned=True),
    ]
    plan = assign_liveness_slots(intervals)

    assert plan.assignments["first"] != plan.assignments["touching"]
    assert plan.assignments["touching"] == plan.assignments["later"]
    assert plan.assignments["first"] != plan.assignments["later"]
    assert plan.assignments["integer"] != plan.assignments["touching"]
    assert "pinned_input" not in plan.assignments
    assert plan.slots[plan.assignments["later"]].elements == 32
    plan.validate(intervals)


def test_liveness_validator_rejects_same_slot_overlap():
    intervals = [
        LiveInterval("left", "f32", 4, 0, 3),
        LiveInterval("right", "f32", 4, 3, 4),
    ]
    plan = LivenessPlan(
        assignments={"left": 0, "right": 0},
        slots=(BufferSlot(0, "f32", 4, ["left", "right"], end=4),),
    )
    with pytest.raises(ValueError, match="liveness overlap"):
        plan.validate(intervals)


def test_taichi_graphbuilder_composes_dispatches_and_archives(tmp_path):
    script = r'''
import sys, zipfile
from pathlib import Path
import numpy as np
import taichi as ti
sys.path.insert(0, sys.argv[2])
from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

@ti.kernel
def scale(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1), n: ti.i32):
    for i in range(n):
        y[i] = x[i] * 2.0

@ti.kernel
def add_one(x: ti.types.ndarray(ti.f32, 1), y: ti.types.ndarray(ti.f32, 1), n: ti.i32):
    for i in range(n):
        y[i] = x[i] + 1.0

ti.init(arch=ti.cpu, offline_cache=False)
x_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'x', ti.f32, ndim=1)
tmp_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'tmp', ti.f32, ndim=1)
y_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'y', ti.f32, ndim=1)
n_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'n', ti.i32)
builder = ti.graph.GraphBuilder()
builder.dispatch(scale, x_arg, tmp_arg, n_arg)
builder.dispatch(add_one, tmp_arg, y_arg, n_arg)
graph = builder.compile()
module = ti.aot.Module(ti.cpu)
module.add_graph('toy_composed', graph)
archive_module(module, Path(sys.argv[1]))

x = ti.ndarray(ti.f32, shape=(4,))
tmp = ti.ndarray(ti.f32, shape=(4,))
y = ti.ndarray(ti.f32, shape=(4,))
x.from_numpy(np.asarray([1, 2, 3, 4], dtype=np.float32))
graph.run({'x': x, 'tmp': tmp, 'y': y, 'n': 4})
np.testing.assert_array_equal(y.to_numpy(), np.asarray([3, 5, 7, 9], dtype=np.float32))
with zipfile.ZipFile(sys.argv[1]) as archive:
    content = archive.read('__content__').decode('utf-8')
    assert 'cgraph:toy_composed' in content
'''
    artifact = tmp_path / "toy_composed.tcm"
    script_path = tmp_path / "toy_graph.py"
    script_path.write_text(script, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(script_path), str(artifact), str(Path(__file__).resolve().parents[3])],
        cwd=Path(__file__).resolve().parents[3],
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert artifact.is_file()


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None or not (PROFILE_DIR / "profile.json").is_file(),
    reason="build the universal CPU pool and WeightNet CPU512 static profile first",
)
def test_weightnet_cpu512_static_graph_matches_generic_and_ort():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 512, 512)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    oracle = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)

    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        generic_outputs = generic.run(None, feeds)
    with StaticGraphSession(model, backend="cpu") as static:
        assert static.fast_path_active, static.last_fallback_reason
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path
        assert static.last_fallback_reason is None
        assert oracle.get_providers() == ["CPUExecutionProvider"]
        assert len(actual) == len(generic_outputs) == len(expected) == 2
        for index, (got, baseline, reference) in enumerate(
            zip(actual, generic_outputs, expected)
        ):
            got = np.asarray(got)
            baseline = np.asarray(baseline)
            reference = np.asarray(reference)
            assert got.shape == reference.shape
            assert got.dtype == reference.dtype == np.float32
            assert np.isfinite(got).all()
            np.testing.assert_array_equal(got, baseline)
            diff = got.astype(np.float64) - reference.astype(np.float64)
            assert float(np.max(np.abs(diff))) <= 1e-6


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv4x4_spatial2x2" / "profile.json").is_file(),
    reason="compile the isolated WeightNet CPU512 spatial 2x2 profile first",
)
def test_weightnet_cpu512_spatial2x2_profile_matches_generic_and_ort():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 512, 512)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    oracle = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        generic_outputs = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_spatial2x2"
    ) as candidate:
        assert candidate.fast_path_active, candidate.last_fallback_reason
        assert candidate.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_spatial_2x2"
        }
        calls = []
        original_run = candidate.static_module.run

        def traced_run(name, *args, **kwargs):
            calls.append(name)
            return original_run(name, *args, **kwargs)

        candidate.static_module.run = traced_run
        candidate_outputs = candidate.run(None, feeds)
        assert candidate.last_run_used_fast_path
        assert calls == [candidate.profile["graph_name"]]

    assert oracle.get_providers() == ["CPUExecutionProvider"]
    assert len(candidate_outputs) == len(generic_outputs) == len(expected) == 2
    differences = []
    exact = 0
    elements = 0
    for index, (got, baseline, reference) in enumerate(
        zip(candidate_outputs, generic_outputs, expected)
    ):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        reference = np.asarray(reference)
        assert got.shape == reference.shape
        assert got.dtype == reference.dtype == np.float32
        assert np.isfinite(got).all()
        np.testing.assert_array_equal(got, baseline)
        diff = got.astype(np.float64) - reference.astype(np.float64)
        assert float(np.max(np.abs(diff))) <= 1e-6, (
            f"output {index} max_abs={np.max(np.abs(diff)):.3e} > 1e-6"
        )
        differences.append(diff.ravel())
        exact += int(np.count_nonzero(got == reference))
        elements += int(got.size)
    all_diff = np.concatenate(differences)
    print(
        "WeightNet CPU512 spatial 2x2: "
        f"max_abs={np.max(np.abs(all_diff)):.9g}, "
        f"rmse={np.sqrt(np.mean(all_diff * all_diff)):.9g}, "
        f"exact={exact}/{elements}, dispatches={len(calls)}"
    )
    disagreements = int(
        np.count_nonzero(
            (np.asarray(candidate_outputs[0]) >= 0.05)
            != (np.asarray(expected[0]) >= 0.05)
        )
    )
    assert disagreements == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv1x1_spatial4" / "profile.json").is_file(),
    reason="compile the isolated WeightNet CPU512 Conv1x1 spatial-four profile first",
)
def test_weightnet_cpu512_conv1x1_spatial4_profile_matches_generic_and_ort():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 512, 512)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    oracle = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
    expected = oracle.run(None, feeds)
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        generic_outputs = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv1x1_spatial4"
    ) as candidate:
        assert candidate.fast_path_active, candidate.last_fallback_reason
        assert candidate.profile["kernel_overrides"] == {
            "nu_conv2d_1x1": "nu_conv2d_1x1_spatial4"
        }
        calls = []
        original_run = candidate.static_module.run

        def traced_run(name, *args, **kwargs):
            calls.append(name)
            return original_run(name, *args, **kwargs)

        candidate.static_module.run = traced_run
        candidate_outputs = candidate.run(None, feeds)
        assert candidate.last_run_used_fast_path
        assert calls == [candidate.profile["graph_name"]]

    assert oracle.get_providers() == ["CPUExecutionProvider"]
    assert len(candidate_outputs) == len(generic_outputs) == len(expected) == 2
    differences = []
    exact = 0
    elements = 0
    for index, (got, baseline, reference) in enumerate(
        zip(candidate_outputs, generic_outputs, expected)
    ):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        reference = np.asarray(reference)
        assert got.shape == reference.shape
        assert got.dtype == reference.dtype == np.float32
        assert np.isfinite(got).all()
        diff_baseline = got.astype(np.float64) - baseline.astype(np.float64)
        diff_reference = got.astype(np.float64) - reference.astype(np.float64)
        assert float(np.max(np.abs(diff_baseline))) <= 1e-6, (
            f"output {index} generic max_abs={np.max(np.abs(diff_baseline)):.3e}"
        )
        assert float(np.max(np.abs(diff_reference))) <= 1e-6, (
            f"output {index} ORT max_abs={np.max(np.abs(diff_reference)):.3e}"
        )
        differences.append(diff_reference.ravel())
        exact += int(np.count_nonzero(got == reference))
        elements += int(got.size)
    all_diff = np.concatenate(differences)
    cutoff_disagreements = int(
        np.count_nonzero(
            (np.asarray(candidate_outputs[0]) >= 0.05)
            != (np.asarray(expected[0]) >= 0.05)
        )
    )
    print(
        "WeightNet CPU512 Conv1x1 spatial4: "
        f"max_abs={np.max(np.abs(all_diff)):.9g}, "
        f"rmse={np.sqrt(np.mean(all_diff * all_diff)):.9g}, "
        f"exact={exact}/{elements}, dispatches={len(calls)}, "
        f"cutoff_disagreements={cutoff_disagreements}"
    )
    assert cutoff_disagreements == 0


def test_weightnet_cpu1024_does_not_select_cpu512_conv1x1_spatial4_profile():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_1024_cpu_1c_fp32.onnx")
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv1x1_spatial4"
    ) as session:
        assert not session.fast_path_active
        assert session.last_fallback_reason is not None


def test_weightnet_cpu1024_does_not_select_cpu512_spatial2x2_profile():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_1024_cpu_1c_fp32.onnx")
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_spatial2x2"
    ) as session:
        assert not session.fast_path_active
        assert session.last_fallback_reason is not None


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (
        PROFILE_DIR / "conv4x4_kahan_unroll" / "profile.json"
    ).is_file(),
    reason="compile the exact WeightNet CPU512 Kahan-unroll static profile first",
)
def test_weightnet_cpu512_kahan_unroll_profile_matches_generic_and_ort():
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
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_kahan_unroll"
    ) as static:
        assert static.fast_path_active, static.last_fallback_reason
        assert static.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_kahan_unrolled"
        }
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path

    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all()
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= ATOL
    cutoff_disagreements = int(np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05)))
    assert cutoff_disagreements == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv4x4_plain" / "profile.json").is_file(),
    reason="compile the exact WeightNet CPU512 plain-sum static profile first",
)
def test_weightnet_cpu512_plain_profile_matches_generic_and_ort():
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
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_plain"
    ) as static:
        assert static.fast_path_active, static.last_fallback_reason
        assert static.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_plain"
        }
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path

    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        np.testing.assert_array_equal(got, np.asarray(baseline))
        diff = got.astype(np.float64) - np.asarray(want).astype(np.float64)
        assert np.isfinite(got).all()
        assert float(np.max(np.abs(diff))) <= ATOL
    cutoff_disagreements = int(np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05)))
    assert cutoff_disagreements == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv4x4_kahan_linear_ci" / "profile.json").is_file(),
    reason="compile the exact WeightNet CPU512 linear-CI static profile first",
)
def test_weightnet_cpu512_linear_ci_profile_matches_generic_and_ort():
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
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_kahan_linear_ci"
    ) as static:
        assert static.fast_path_active, static.last_fallback_reason
        assert static.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_kahan_linear_ci"
        }
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path

    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all()
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= 1e-6, f"linear-CI full-model max_abs={max_abs:.3e}"
    assert int(np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05))) == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv4x4_kahan_ndrange" / "profile.json").is_file(),
    reason="compile the exact WeightNet CPU512 ndrange static profile first",
)
def test_weightnet_cpu512_ndrange_profile_matches_generic_and_ort():
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
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_kahan_ndrange"
    ) as static:
        assert static.fast_path_active, static.last_fallback_reason
        assert static.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_kahan_ndrange"
        }
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path

    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all()
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= 1e-6, f"ndrange full-model max_abs={max_abs:.3e}"
    assert int(np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05))) == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None
    or not (PROFILE_DIR / "conv4x4_kahan_parallelize8" / "profile.json").is_file(),
    reason="compile the exact WeightNet CPU512 parallelize=8 static profile first",
)
def test_weightnet_cpu512_parallelize8_profile_matches_generic_and_ort():
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
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(
        model, backend="cpu", profile_variant="conv4x4_kahan_parallelize8"
    ) as static:
        assert static.fast_path_active, static.last_fallback_reason
        assert static.profile["kernel_overrides"] == {
            "nu_conv2d_4x4_s2": "nu_conv2d_4x4_s2_kahan_p8"
        }
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path

    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        baseline = np.asarray(baseline)
        want = np.asarray(want)
        np.testing.assert_array_equal(got, baseline)
        assert np.isfinite(got).all()
        max_abs = float(np.max(np.abs(got.astype(np.float64) - want.astype(np.float64))))
        assert max_abs <= 1e-6, f"parallelize=8 full-model max_abs={max_abs:.3e}"
    assert int(np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05))) == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None or not (PROFILE_1024_DIR / "profile.json").is_file(),
    reason="compile the WeightNet CPU1024 static graph profile first",
)
def test_weightnet_cpu1024_static_graph_matches_generic_and_ort():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_1024_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 1024, 1024)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    expected = ort.InferenceSession(
        model, providers=["CPUExecutionProvider"]
    ).run(None, feeds)
    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="cpu") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(model, backend="cpu") as static:
        assert static.fast_path_active, static.last_fallback_reason
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path
    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        np.testing.assert_array_equal(got, np.asarray(baseline))
        diff = got.astype(np.float64) - np.asarray(want).astype(np.float64)
        assert np.isfinite(got).all()
        assert float(np.max(np.abs(diff))) <= ATOL


@pytest.mark.skipif(
    _find_pool_tcm("vulkan") is None or not (PROFILE_GPU512_DIR / "profile.json").is_file(),
    reason="compile the WeightNet GPU512 Vulkan static graph profile first",
)
def test_weightnet_gpu512_static_graph_matches_generic_and_directml_ort(tmp_path):
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_gpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261025)
    shape = (1, 1, 512, 512)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    options = ort.SessionOptions()
    options.enable_profiling = True
    options.profile_file_prefix = str(tmp_path / "static_weightnet_gpu_ort")
    oracle = ort.InferenceSession(model, options, providers=["DmlExecutionProvider"])
    expected = oracle.run(None, feeds)
    events = json.loads(Path(oracle.end_profiling()).read_text(encoding="utf-8"))
    node_providers = {
        event.get("args", {}).get("provider", "unknown")
        for event in events if event.get("cat") == "Node"
    }

    from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

    with UniversalSession(model, backend="vulkan") as generic:
        reference = generic.run(None, feeds)
    with StaticGraphSession(model, backend="vulkan") as static:
        assert static.fast_path_active, static.last_fallback_reason
        actual = static.run(None, feeds)
        assert static.last_run_used_fast_path
        assert static.engine.gpu_name == "Intel(R) UHD Graphics 620"

    assert "DmlExecutionProvider" in oracle.get_providers()
    assert node_providers == {"DmlExecutionProvider"}
    for got, baseline, want in zip(actual, reference, expected):
        got = np.asarray(got)
        np.testing.assert_array_equal(got, np.asarray(baseline))
        diff = got.astype(np.float64) - np.asarray(want).astype(np.float64)
        assert np.isfinite(got).all()
        assert float(np.max(np.abs(diff))) <= ATOL
    cutoff_disagreements = int(
        np.count_nonzero((actual[0] >= 0.05) != (expected[0] >= 0.05))
    )
    assert cutoff_disagreements == 0


@pytest.mark.skipif(
    _find_pool_tcm("cpu") is None or not (PROFILE_DIR / "profile.json").is_file(),
    reason="build the universal CPU pool and WeightNet CPU512 static profile first",
)
def test_static_profile_fallback_for_dtype_and_borrowed_output_contract():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    rng = np.random.default_rng(20261026)
    shape = (1, 1, 512, 512)
    feeds64 = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float64),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float64),
    }
    with StaticGraphSession(model, backend="cpu") as session:
        assert session.fast_path_active
        generic_result = session.run(None, feeds64)
        assert not session.last_run_used_fast_path
        assert "dtype mismatch" in session.last_fallback_reason

        feeds32 = {name: array.astype(np.float32) for name, array in feeds64.items()}
        graph_calls = []
        original_run = session.static_module.run

        def record_run(name, **kwargs):
            graph_calls.append(name)
            return original_run(name, **kwargs)

        session.static_module.run = record_run
        borrowed = session.run(None, feeds32, return_gpu=True)
        assert session.last_run_used_fast_path
        assert graph_calls == [session.profile["graph_name"]]
        with (PROFILE_DIR / "profile.json").open("r", encoding="utf-8") as stream:
            profile = json.load(stream)
        for buffer, output_name in zip(borrowed, ("weight_map", "alpha")):
            shape_out = tuple(profile["outputs"][output_name]["shape"])
            elements = int(np.prod(shape_out, dtype=np.int64)) if shape_out else 1
            assert buffer.to_numpy().size == elements


def test_static_profile_model_hash_mismatch_falls_back_to_generic():
    with zipfile.ZipFile(WEIGHTNET) as archive:
        reference_model = archive.read("weightnet_512_cpu_1c_fp32_reference.onnx")
    with StaticGraphSession(reference_model, backend="cpu") as session:
        assert not session.fast_path_active
        assert "static profile unavailable/incompatible" in session.last_fallback_reason
        assert session.backend == "cpu"
        assert session.get_providers() == ["TaichiUniversal_CPUExecutionProvider"]


@pytest.mark.parametrize("mismatch", ["target_identity", "runtime_abi", "graph_name"])
def test_static_profile_manifest_mismatch_falls_back_same_backend(tmp_path, mismatch):
    with zipfile.ZipFile(WEIGHTNET) as archive:
        model = archive.read("weightnet_512_cpu_1c_fp32.onnx")
    target_root = tmp_path / "models"
    profile_dir = target_root / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184" / "cpu"
    shutil.copytree(PROFILE_DIR, profile_dir)
    profile_path = profile_dir / "profile.json"
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if mismatch == "target_identity":
        profile["target_identity"]["vendor"] = "wrong-target"
    elif mismatch == "runtime_abi":
        profile["runtime_abi"] += 1
    else:
        profile["graph_name"] = "missing_graph"
    profile_path.write_text(json.dumps(profile), encoding="utf-8")

    with StaticGraphSession(
        model, backend="cpu", profile_root=target_root
    ) as session:
        assert not session.fast_path_active
        assert session.backend == "cpu"
        assert session.get_providers() == ["TaichiUniversal_CPUExecutionProvider"]
        assert session.last_fallback_reason


def test_static_profile_loader_rejects_tcm_or_constant_hash_mismatch(tmp_path):
    from taichi_vision.taichi_aot.neural_universal.static_graph import load_static_profile

    profile = {
        "tcm": "profile.tcm",
        "constants": "constants.npz",
        "dispatches": 1,
        "dispatch_graph_counts": {"graph": 1},
        "tcm_sha256": "bad",
        "constants_sha256": "bad",
    }
    (tmp_path / "profile.tcm").write_bytes(b"tcm")
    (tmp_path / "constants.npz").write_bytes(b"constants")
    (tmp_path / "profile.json").write_text(json.dumps(profile), encoding="utf-8")
    with pytest.raises(ValueError, match="TCM hash"):
        load_static_profile(tmp_path)
