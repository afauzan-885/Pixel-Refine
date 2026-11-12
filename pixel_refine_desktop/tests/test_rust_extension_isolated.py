"""Focused native extension checks; set RUST_AUDIT_EXTENSION to a built DLL.

These host-only tests do not establish application or GPU parity.
"""

import importlib.machinery
import importlib.util
import os

import numpy as np
import pytest
import taichi as ti


@pytest.fixture(scope="module")
def native():
    path = os.environ.get("RUST_AUDIT_EXTENSION")
    if not path:
        pytest.skip("set RUST_AUDIT_EXTENSION to test the isolated build")
    loader = importlib.machinery.ExtensionFileLoader("taichi_python", path)
    spec = importlib.util.spec_from_file_location("taichi_python", path, loader=loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_rejects_buffer_smaller_than_shape(native):
    with pytest.raises(ValueError, match="smaller than shape"):
        native.RustBuffer(1, None, (1024,), dtype="float32", host_accessible=True)


def test_exported_memoryview_survives_destroy(native):
    buf = native.RustBuffer(0, None, (4,), dtype="int8", host_accessible=True)
    view = memoryview(buf)
    array = np.asarray(view)
    expected = np.array([-128, -1, 0, 127], dtype=np.int8)
    array[:] = expected
    assert array.ctypes.data == buf.data_ptr()
    buf.destroy(force=True)
    np.testing.assert_array_equal(array, expected)
    del array
    view.release()


def test_to_numpy_copy_has_independent_storage(native):
    buf = native.RustBuffer(0, None, (4,), dtype="int8", host_accessible=True)
    view = buf.to_numpy(copy=False)
    view[:] = [-128, -1, 0, 127]
    copied = buf.to_numpy(copy=True)
    assert copied.ctypes.data != buf.data_ptr()
    view[0] = 42
    np.testing.assert_array_equal(copied, [-128, -1, 0, 127])
    del view
    buf.destroy()
    np.testing.assert_array_equal(copied, [-128, -1, 0, 127])


def test_taichi_dtype_widths(native):
    import taichi as ti

    for dtype, width in [("i8", 8), ("u8", 8), (ti.i8, 1), (ti.u8, 1)]:
        buf = native.RustBuffer(0, None, (4,), dtype=dtype, host_accessible=True)
        assert buf.nbytes == 4 * width
        buf.destroy()
