"""Unified-runtime buffer contract for algorithm dispatch.

The legacy Python engine has been retired. Algorithm calls now run on exactly
one native runtime (``taichi.aot_engine``), so the old "legacy vs migrated"
comparison is no longer meaningful. These tests keep the value-drift coverage by
comparing the buffer path against the host-array path on the same runtime, and
they pin the two facts that make mixing impossible:

- facade / aot_api / module alias all expose the same buffer class;
- a buffer from the separate Rust engine (``taichi.get_engine``) is rejected
  with a clear error instead of being handed to the bridge as a raw pointer.
"""
import taichi.aot_engine as _ti_rt

import numpy as np
import pytest

import taichi as ti
from taichi_vision import algorithm as legacy_runtime

aot_api = pytest.importorskip("taichi_vision.taichi_algorithm.aot_api")

IMG = (48, 64, 3)
GRAY = (48, 64)


def _upload(img, gray):
    return _ti_rt.upload(img), _ti_rt.upload(gray)


@pytest.fixture(scope="module")
def arrays():
    rng = np.random.default_rng(11)
    return (
        rng.random(IMG, dtype=np.float32),
        rng.random(GRAY, dtype=np.float32),
    )


def _values(value):
    return np.asarray(value)


def test_the_facade_and_algorithm_layer_share_one_runtime():
    assert aot_api.TaichiGPUBuffer is _ti_rt.TaichiGPUBuffer
    assert aot_api.AOTEngine is _ti_rt.AOTEngine
    assert aot_api.engine is _ti_rt.engine


def test_cvtcolor_buffer_matches_host_path(arrays):
    img, gray = arrays
    color_buf, _ = _upload(img, gray)
    try:
        buffered = _values(aot_api.cvtColor(color_buf, aot_api.COLOR_RGB2GRAY))
        host = _values(aot_api.cvtColor(img, aot_api.COLOR_RGB2GRAY))
        np.testing.assert_array_equal(buffered, host)
    finally:
        color_buf.release()


def test_resize_buffer_matches_host_path(arrays):
    img, gray = arrays
    _, gray_buf = _upload(img, gray)
    try:
        buffered = _values(
            aot_api.resize(gray_buf, (24, 32), interpolation=aot_api.INTER_AREA)
        )
        host = _values(
            aot_api.resize(gray, (24, 32), interpolation=aot_api.INTER_AREA)
        )
        np.testing.assert_array_equal(buffered, host)
    finally:
        gray_buf.release()


def test_remap_with_zero_flow_buffer_matches_host_path(arrays):
    img, gray = arrays
    color_buf, _ = _upload(img, gray)
    flow = np.zeros((IMG[0], IMG[1], 2), dtype=np.float32)
    try:
        buffered = _values(
            aot_api.remap_with_flow(color_buf, flow, IMG[0], IMG[1])
        )
        host = _values(aot_api.remap_with_flow(img, flow, IMG[0], IMG[1]))
        np.testing.assert_array_equal(buffered, host)
    finally:
        color_buf.release()


def test_box_filter_buffer_matches_host_path(arrays):
    img, gray = arrays
    _, gray_buf = _upload(img, gray)
    try:
        buffered = _values(aot_api.box_filter(gray_buf, kernel_size=3))
        host = _values(aot_api.box_filter(gray, kernel_size=3))
        np.testing.assert_array_equal(buffered, host)
    finally:
        gray_buf.release()


def test_rust_engine_buffer_is_rejected_before_the_bridge(arrays):
    from taichi.aot_dispatch import DynamicArg, populate_dynamic_arg

    img, _ = arrays
    rust_buf = ti.get_engine().upload(img)
    try:
        assert type(rust_buf).__name__ == "TaichiGPUBuffer"
        assert getattr(rust_buf, "_rust_buf", None) is not None
        arg = DynamicArg()
        with pytest.raises(TypeError, match="Rust-engine buffer|separate native runtimes"):
            populate_dynamic_arg(arg, b"src", rust_buf, context_name="guard-test")
    finally:
        rust_buf.release()
