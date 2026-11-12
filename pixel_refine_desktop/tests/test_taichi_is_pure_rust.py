"""Guard: the installed `taichi` runtime is native Rust only.

These assertions exist because the Python fallbacks were removed deliberately.
A failure here means either the Rust extension stopped loading, a NumPy host
buffer path came back, or `taichi` started depending on `taichi_vision` again.
"""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import taichi as ti


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_import_taichi_does_not_load_taichi_vision():
    code = (
        "import sys, taichi; "
        "print('taichi_vision' in sys.modules); "
        "print(taichi.__version__)"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    loaded, version = proc.stdout.split()
    assert loaded == "False", "importing taichi must not import taichi_vision"
    assert version == "1.8.0"


def test_native_symbols_are_provided_by_the_extension():
    from taichi import taichi_python as tp

    for name in (
        "RustBuffer",
        "RustBufferSession",
        "RustAOTEngine",
        "TilePlan",
        "TileBox",
        "plan_tiles",
        "read_dng",
        "box_blur",
        "box_blur_into",
    ):
        assert hasattr(tp, name), f"taichi_python missing {name}"
    assert tp.engine_backend() == "rust-cpu-cranelift-jit"


def test_buffers_are_rust_backed_without_a_numpy_host_fallback():
    engine = ti.get_engine()
    assert type(engine._rust_engine).__name__ == "RustAOTEngine"
    buf = engine.allocate((4, 4), dtype="float32", host_accessible=True)
    try:
        assert type(buf._rust_buf).__name__ == "RustBuffer"
        assert not hasattr(buf, "_host_array")
        np.asarray(buf)[:] = 2.5
        assert float(np.asarray(buf)[0, 0]) == 2.5
    finally:
        buf.release()


def test_engine_requires_the_rust_orchestrator():
    import importlib

    engine_module = importlib.import_module("taichi.engine")
    engine_module._RustAOTEngine = None
    resolved = engine_module._rust_engine_class()
    assert resolved is not None
    assert type(ti.get_engine()._rust_engine).__name__ == "RustAOTEngine"


def test_algorithmic_entry_points_are_gone():
    for name in (
        "demosaic",
        "hamilton",
        "remap",
        "remap_with_flow",
        "resize",
        "box_filter",
        "gaussian_blur",
        "farneback_flow",
        "phase_correlation",
        "copy",
        "neural",
    ):
        assert not hasattr(ti, name), f"{name} is algorithmic and must live in taichi_vision"


def test_buffer_session_is_native():
    import taichi.buffer_session as session_module

    assert session_module._RustBufferSession is not None
    with ti.BufferSession(sync_on_exit=False, tag="pure-rust-guard") as session:
        host = np.zeros((4, 4), np.float32)
        buf, owned = session.upload_if_needed(host)
        assert owned is True
        session.release_borrow(buf)


def test_buffer_session_managed_api_requires_explicit_api():
    with ti.BufferSession(sync_on_exit=False) as session:
        with pytest.raises(ValueError):
            session.managed_api()
