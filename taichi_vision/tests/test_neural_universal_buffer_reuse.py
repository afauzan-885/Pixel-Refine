"""Contract tests for the BufferSession-backed universal runtime.

These verify ownership, reuse and lifecycle — not wall-clock performance, which
this machine cannot measure reliably. They run on CPU only and use the staged
WeightNet pool, so they are skipped when that artifact is absent.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import onnx
import pytest

from taichi_vision.taichi_algorithm.neural.universal import UniversalSession

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "database" / "Learning_Model" / "weightNet" / "weightnet_master.bundle"
POOL = (
    ROOT / "pixel_refine_desktop" / "ui" / "data" / "aot_assets" / "neural"
    / "universal" / "cpu" / "neural_cpu.tcm"
)


def _model_bytes() -> bytes:
    if not BUNDLE.is_file():
        pytest.skip("WeightNet bundle is not available")
    with zipfile.ZipFile(BUNDLE) as archive:
        return archive.read("weightnet_512_cpu_1c_fp32.onnx")


def _feed(model_bytes: bytes) -> dict:
    model = onnx.load_model_from_string(model_bytes)
    rng = np.random.default_rng(42)
    feed = {}
    for value in model.graph.input:
        dims = tuple(
            int(dim.dim_value) if dim.dim_value > 0 else 1
            for dim in value.type.tensor_type.shape.dim
        )
        feed[value.name] = rng.standard_normal(dims, dtype=np.float32)
    return feed


def _host(value):
    return np.asarray(value.to_numpy() if hasattr(value, "to_numpy") else value)


@pytest.fixture(scope="module")
def pool_ready() -> None:
    if not POOL.is_file():
        pytest.skip("staged universal pool is not available")


@pytest.fixture
def session(pool_ready):
    model_bytes = _model_bytes()
    instance = UniversalSession(model_bytes, backend="cpu", use_buffer_session=True)
    try:
        yield instance, _feed(model_bytes)
    finally:
        instance.close()


def test_buffer_session_is_the_owner(session):
    instance, feed = session
    assert instance.buffer_session_available is True
    assert instance.buffer_session is not None
    assert instance.buffer_session.owned_count == 0  # nothing claimed before a run
    instance.run(None, feed)
    assert instance.buffer_session.owned_count > 0


def test_repeated_runs_are_identical(session):
    instance, feed = session
    first = [_host(value) for value in instance.run(None, feed)]
    second = [_host(value) for value in instance.run(None, feed)]
    for a, b in zip(first, second):
        assert np.array_equal(a, b)


def test_default_contract_returns_host_arrays(session):
    instance, feed = session
    results = instance.run(None, feed)
    assert all(isinstance(value, np.ndarray) for value in results)


def test_borrowed_outputs_stay_device_resident(session):
    instance, feed = session
    reference = [_host(value) for value in instance.run(None, feed)]
    borrowed = instance.run(None, feed, borrowed_outputs=True)
    buffer = borrowed[0]
    assert hasattr(buffer, "handle") and buffer.handle is not None
    # Borrowed results are flat device buffers by contract.
    assert np.array_equal(
        _host(buffer).reshape(reference[0].shape), reference[0]
    )


def test_signature_change_reuses_session_and_keeps_results(session):
    instance, feed = session
    reference = _host(instance.run(None, feed)[0])
    changed = dict(feed)
    changed["ref_img"] = np.zeros_like(feed["ref_img"])
    instance.run(None, changed)
    assert instance.buffer_session.owned_count > 0
    assert np.array_equal(_host(instance.run(None, feed)[0]), reference)


def test_close_releases_all_owned_buffers():
    model_bytes = _model_bytes()
    feed = _feed(model_bytes)
    instance = UniversalSession(model_bytes, backend="cpu", use_buffer_session=True)
    instance.run(None, feed)
    owned_before_close = instance.buffer_session.owned_count
    instance.close()
    assert owned_before_close > 0
    assert instance.buffer_session is None


def test_disabling_buffer_session_keeps_previous_path(pool_ready):
    model_bytes = _model_bytes()
    feed = _feed(model_bytes)
    with_session = UniversalSession(model_bytes, backend="cpu", use_buffer_session=True)
    without_session = UniversalSession(model_bytes, backend="cpu", use_buffer_session=False)
    try:
        expected = [_host(value) for value in with_session.run(None, feed)]
        actual = [_host(value) for value in without_session.run(None, feed)]
        assert without_session.buffer_session is None
        for a, b in zip(expected, actual):
            assert np.array_equal(a, b)
    finally:
        with_session.close()
        without_session.close()
