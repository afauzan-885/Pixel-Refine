"""Parity gates for real models, measured against ONNX Runtime.

These are the end-to-end gates the whole effort is for. They are marked `slow`
because they run four-hundred-megabyte models; the parity assertion is the point,
and it is stated in absolute terms because a relative-to-peak metric is misleading
when the reference values are themselves very small.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

onnxruntime = pytest.importorskip("onnxruntime")
pytest.importorskip("taichi.taichi_python")

from taichi_vision.neural.native_session import NativeSession  # noqa: E402

MODELS = Path(__file__).resolve().parents[2] / "database" / "Learning_Model" / "weightNet" / "CPU"

#: Absolute agreement required, in the model's own units.
#:
#: `1e-6` absolute is the project's f32 gate. The `erf` primitive is an
#: Abramowitz-Stegun polynomial with a measured 3.4e-7 error (about three f32
#: ulps), so every GELU in the graph carries that floor; requiring more than this
#: would be asking the polynomial to be exact.
ABSOLUTE_TOLERANCE = 1e-6


def _weightnet(name: str):
    path = MODELS / name
    if not path.exists():
        pytest.skip(f"{path.name} is not present")
    return path.read_bytes()


def _feeds(seed: int = 7):
    generator = np.random.default_rng(seed)
    return {
        "ref_img": generator.uniform(0, 1, (1, 1, 512, 512)).astype(np.float32),
        "support_img": generator.uniform(0, 1, (1, 1, 512, 512)).astype(np.float32),
        "ghost_sensitivity": np.asarray([1.0], dtype=np.float32),
    }


@pytest.mark.slow
@pytest.mark.parametrize("model_name", ["weightnet_512_cpu_fp32.onnx"])
def test_weightnet_matches_onnxruntime(model_name):
    model_bytes = _weightnet(model_name)
    feeds = _feeds()

    options = onnxruntime.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    reference = onnxruntime.InferenceSession(
        model_bytes, options, providers=["CPUExecutionProvider"]
    ).run(None, feeds)

    session = NativeSession(model_bytes, model_name=model_name)
    produced = session.run(None, feeds)

    assert len(produced) == len(reference)
    for index, name in enumerate(session.plan.output_names):
        got = np.asarray(produced[index]).ravel().astype(np.float64)
        want = np.asarray(reference[index]).ravel().astype(np.float64)
        assert got.shape == want.shape, f"{name}: shape {got.shape} vs {want.shape}"
        worst = float(np.abs(got - want).max())
        assert worst < ABSOLUTE_TOLERANCE, (
            f"{name}: max absolute difference {worst:.3e} exceeds "
            f"{ABSOLUTE_TOLERANCE:.0e}"
        )


@pytest.mark.slow
def test_the_output_is_finite_and_not_degenerate():
    # A graph that runs but produces zeros or NaNs is not "working". This checks
    # the output carries the structure the model is for.
    model_bytes = _weightnet("weightnet_512_cpu_fp32.onnx")
    session = NativeSession(model_bytes)
    produced = session.run(None, _feeds())
    weight_map = np.asarray(produced[0])
    assert weight_map.shape == (1, 1, 512, 512)
    assert np.isfinite(weight_map).all(), "the weight map contains NaN or infinity"
    assert weight_map.max() > 0.0, "the weight map is identically zero"
    # A weight map is a weighting, so it must vary across the image.
    assert weight_map.std() > 0.0, "the weight map is constant"


@pytest.mark.slow
def test_running_twice_gives_identical_bytes():
    # Determinism is a property the executor has to keep, and a graph this large is
    # where a race would show up.
    model_bytes = _weightnet("weightnet_512_cpu_fp32.onnx")
    session = NativeSession(model_bytes)
    feeds = _feeds()
    first = np.asarray(session.run(None, feeds)[0])
    second = np.asarray(session.run(None, feeds)[0])
    np.testing.assert_array_equal(
        first.view(np.uint32), second.view(np.uint32), "output changed between runs"
    )
