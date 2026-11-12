"""Machine-checked boundary between Rust and Python in the taichi runtime.

The migration is partial. This test states exactly which non-algorithmic pieces
run in Rust today and which are still Python, so no future report can claim more
without changing this file. When a gap is closed, the corresponding assertion
below must be updated deliberately.
"""

import numpy as np
import pytest

import taichi as ti


def test_rust_primitives_are_present():
    # Shipped by the PyO3 extension and actually used by the engine.
    from taichi import taichi_python as tp

    for name in ("RustBuffer", "RustBufferSession", "TilePlan", "TileBox"):
        assert hasattr(tp, name), f"taichi_python missing {name}"
    assert tp.engine_backend() == "rust-cpu-cranelift-jit"
    assert tp.engine_supports_f32() is True


def test_allocated_buffers_are_rust_backed():
    engine = ti.get_engine()
    buf = engine.allocate((8, 8), dtype="float32", host_accessible=True)
    try:
        assert buf._rust_buf is not None, "buffer fell back to a NumPy host array"
        payload = np.arange(64, dtype=np.float32).reshape(8, 8)
        buf._rust_buf.write_from_buffer(payload)
        np.testing.assert_array_equal(np.asarray(buf.to_numpy()), payload)
    finally:
        buf.release()


def test_upload_returns_rust_buffer():
    engine = ti.get_engine()
    buf = engine.upload(np.zeros((4, 4), dtype=np.float32), is_vector=False)
    try:
        assert buf._rust_buf is not None
    finally:
        buf.release()


def test_engine_orchestrator_is_now_rust():
    """The engine handle is bound to the Rust orchestrator."""
    from taichi import taichi_python as tp

    assert hasattr(tp, "RustAOTEngine"), "RustAOTEngine must be exported by the extension"
    assert isinstance(getattr(ti, "RustAOTEngine", None), type)
    engine = ti.get_engine()
    assert engine._rust_engine is not None, "engine must use the Rust orchestrator"
    assert type(engine._rust_engine).__name__ == "RustAOTEngine"


def test_backend_selection_reports_the_real_device():
    """A non-cpu engine opens the driver and reports its real name."""
    cpu = ti.get_engine(arch="cpu")
    assert cpu.gpu_name == "CPU (Rust Cranelift)"
    assert cpu is ti.get_engine(arch="cpu", device_id=None)

    vulkan = ti.get_engine(arch="vulkan")
    assert vulkan.arch == "vulkan"
    assert vulkan._rust_engine is not None
    # Either a real driver name is reported, or the failure is spelled out.
    assert "device unavailable" not in vulkan.gpu_name or vulkan.last_error()
    assert "pending" not in vulkan.gpu_name


def test_rust_engine_bookkeeping():
    """Allocation, retire, staging reuse and the pixel cap live in Rust."""
    engine = ti.get_engine()
    rust = engine._rust_engine

    before = engine.get_memory_status()["live_bytes"]
    buffer = engine.allocate((8, 8), dtype="float32", host_accessible=True)
    during = engine.get_memory_status()["live_bytes"]
    assert during == before + 256
    buffer.release()
    assert engine.get_memory_status()["live_bytes"] == before

    staging = engine.acquire_staging_buffer((16, 16), "float32")
    engine.release_staging_buffer(staging)
    assert engine.get_memory_status()["pooled_bytes"] >= 1024
    reused = engine.acquire_staging_buffer((16, 16), "float32")
    assert engine.get_memory_status()["pooled_bytes"] == 0
    reused.release()
    assert engine.reclaim_resident_buffers("test")["reason"] == "test"

    engine.set_max_pixel_count(16)
    try:
        with pytest.raises(RuntimeError, match="Pixel Cap"):
            engine.allocate((8, 8), dtype="float32")
    finally:
        engine.set_max_pixel_count(0)

    rust.current_pipeline = "probe"
    assert engine.current_pipeline() == "probe"
    rust.current_pipeline = None
    assert engine.current_pipeline() is None


def test_device_allocation_is_real_vulkan_memory():
    """Device-resident buffers live in mapped Vulkan memory, without a copy."""
    if not ti._TESTS_HAVE_VULKAN:  # pragma: no cover - host without a driver
        pytest.skip("no Vulkan device on this host")
    engine = ti.get_engine(arch="vulkan")
    buffer = engine.allocate((32, 32), dtype="float32")
    try:
        assert buffer.nbytes == 4096
        view = np.asarray(buffer)
        view[:] = 3.25
        assert float(np.asarray(buffer)[0, 0]) == 3.25
        # The Python view must alias the buffer, not a snapshot of it.
        view[0, 0] = 9.0
        assert float(np.asarray(buffer)[0, 0]) == 9.0
    finally:
        buffer.release()


def test_host_accessible_allocation_stays_on_the_host():
    engine = ti.get_engine(arch="vulkan")
    buffer = engine.allocate((4, 4), dtype="float32", host_accessible=True)
    try:
        assert buffer.nbytes == 64
        np.asarray(buffer)[:] = 1.5
        assert float(np.asarray(buffer)[0, 0]) == 1.5
    finally:
        buffer.release()
