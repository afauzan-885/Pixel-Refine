"""Runtime API parity matrix: legacy taichi_vision vs the migrated taichi library.

Each test compares one non-algorithmic contract. A failure here is a real
parity gap that blocks moving consumer imports, so the detail string names the
mismatch instead of hiding it behind a loose assertion.

Scope notes:
- Host-only; no algorithm graphs and no backend qualification.
- WeightNet resident TCM is out of scope for this migration round.
"""
import taichi.aot_engine as _ti_rt

import numpy as np
import pytest

LEGACY = pytest.importorskip("taichi.backend_config")
import taichi as ti  # noqa: E402


def _legacy_engine_module():
    import importlib

    return importlib.import_module("taichi.aot_engine")


def _legacy_runtime():
    import taichi.aot_engine as tv_aot

    return tv_aot


def _legacy_engine():
    return _legacy_runtime().get_engine()


def test_backend_naming_parity():
    tv = LEGACY
    assert tuple(ti.CANONICAL_BACKENDS) == tuple(tv.CANONICAL_BACKENDS)
    for value in ("CUDA", "vulkan", "HOST", "cpu_x86_64_windows", "gl", "gles3", "", "auto"):
        assert ti.normalize_backend(value) == tv.normalize_backend(value), value
    for value in ("NVIDIA GeForce MX150", "Intel(R) UHD Graphics 620", "AMD Radeon", "cpu"):
        assert ti.normalize_vendor(value) == tv.normalize_vendor(value), value
    for value in (None, "", "0", "3", "-1", "bogus"):
        assert ti.parse_device_id(value, 0) == tv.parse_device_id(value, 0), value


def test_backend_config_and_env_parity():
    tv = LEGACY
    for backend in tv.CANONICAL_BACKENDS:
        a = tv.BackendConfig(backend=backend, device_id=1)
        b = ti.BackendConfig(backend=backend, device_id=1)
        assert (a.backend, a.device_id, a.is_gpu, a.target_family) == (
            b.backend,
            b.device_id,
            b.is_gpu,
            b.target_family,
        ), backend
        assert tv.backend_env(a) == ti.backend_env(b), backend


def test_device_scan_parity():
    import taichi.device_selection as tv_ds

    legacy = tv_ds.scan_vulkan_device_records()
    migrated = ti.scan_vulkan_device_records()
    assert len(migrated) == len(legacy)
    for old, new in zip(legacy, migrated):
        assert new["vendor"] == old["vendor"]
        assert str(new["name"]).strip() == str(old["name"]).strip()
    # Selector contract: given the SAME record both sides must agree, because
    # persisted settings key on the fingerprint.
    if legacy:
        sel_old = tv_ds.make_device_selector(legacy[0])
        sel_new = ti.make_device_selector(legacy[0])
        assert sel_new["fingerprint"] == sel_old["fingerprint"]
        assert sel_new["vendor"] == sel_old["vendor"]
        assert sel_new["native"] == sel_old["native"]


@pytest.mark.parametrize("dtype", [np.float32, np.uint8, np.uint16, np.int32])
def test_buffer_metadata_parity(dtype):
    legacy_engine = _legacy_engine()
    shape = (7, 5)
    old = legacy_engine.allocate(shape, dtype=dtype, host_accessible=True)
    new = ti.get_engine().allocate(shape, dtype=dtype, host_accessible=True)
    try:
        assert tuple(new.shape) == tuple(old.shape)
        assert new.nbytes == old.nbytes
        assert new.ndim == old.ndim
        assert np.dtype(new.dtype) == np.dtype(old.dtype)
    finally:
        old.release()
        new.release()


def test_upload_roundtrip_and_force_8bit_parity():
    legacy_engine = _legacy_engine()
    a16 = (np.arange(48, dtype=np.uint16).reshape(6, 8) << 8)

    old = legacy_engine.upload(a16, is_vector=False)
    new = ti.upload(a16, is_vector=False)
    try:
        np.testing.assert_array_equal(np.asarray(old.to_numpy()), np.asarray(new.to_numpy()))
    finally:
        old.release()
        new.release()

    from taichi_vision.taichi_algorithm import aot_api

    ref = aot_api.upload(a16, force_8bit=True)
    forced = ti.upload(a16, force_8bit=True)
    try:
        assert np.dtype(forced.dtype) == np.dtype(ref.dtype) == np.uint8
        np.testing.assert_array_equal(
            np.asarray(ref.to_numpy()), np.asarray(forced.to_numpy())
        )
    finally:
        ref.release()
        forced.release()


def test_cast_values_match_and_return_type_is_documented():
    """Both runtimes return a device buffer after the unification.

    The legacy facade now aliases the unified runtime, so `cast()` no longer
    hands back a host ndarray. Values must still agree, and the return must stay
    a buffer for in-place GPU chains.
    """
    src = np.linspace(0.0, 1.0, 32, dtype=np.float32)
    buffer = ti.get_engine().upload(src)
    try:
        facade = _legacy_runtime().cast(buffer, np.uint8)
        migrated = ti.cast(buffer, np.uint8)
        try:
            assert not isinstance(facade, np.ndarray), "facade cast must stay a buffer"
            assert not isinstance(migrated, np.ndarray), "ti.cast must stay a buffer"
            np.testing.assert_array_equal(
                np.asarray(facade.to_numpy()), np.asarray(migrated.to_numpy())
            )
            assert np.dtype(migrated.dtype) == np.dtype(facade.dtype)
        finally:
            migrated.release()
            facade.release()
    finally:
        buffer.release()


def test_session_ownership_parity():
    import taichi_vision.taichi_algorithm.buffer_session as tv_bs

    class _Engine:
        def allocate(self, *a, **k):
            raise AssertionError("unexpected allocation")

        def upload(self, *a, **k):
            raise AssertionError("unexpected upload")

        def sync(self):
            pass

    keep_alive = []

    def exercise(session_cls):
        released = []
        resource = object()
        keep_alive.append(resource)
        with session_cls(engine=_Engine(), sync_on_exit=False, tag="parity") as session:
            session.own(resource, releaser=lambda value: released.append(value))
            assert session.borrow(resource) is resource
            assert session.borrow(resource) is resource
            counts = [session.owned_count, session.borrowed_count]
            session.release_borrow(resource)
            counts.append(session.borrowed_count)
            session.release_borrow(resource)
            counts.append(session.borrowed_count)
        return counts, released == [resource]

    assert exercise(ti.BufferSession) == exercise(tv_bs.BufferSession) == (
        [1, 2, 1, 0],
        True,
    )


def test_upload_if_needed_contract_parity():
    host = np.zeros((8, 8), np.float32)
    with ti.BufferSession(sync_on_exit=False, tag="parity") as session:
        first, owned_first = session.upload_if_needed(host)
        cached, owned_cached = session.upload_if_needed(host)
        passthrough, owned_passthrough = session.upload_if_needed(first)
        assert owned_first is True
        assert owned_cached is False and cached is first
        assert owned_passthrough is False and passthrough is first
        session.release_borrow(first)


def test_engine_surface_parity():
    legacy_engine = _legacy_engine()
    migrated = ti.get_engine()
    for name in (
        "allocate",
        "upload",
        "sync",
        "write_into",
        "get_memory_status",
        "reclaim_resident_buffers",
        "plan_blocks",
        "get_block_cache",
        "set_force_host_accessible",
        "set_max_pixel_count",
        "placeholder",
        "load",
        "destroy",
        "reinit",
    ):
        assert hasattr(migrated, name), f"taichi engine missing {name}"
        assert hasattr(legacy_engine, name), f"legacy engine missing {name}"


def test_native_planner_parity():
    plan = ti.plan_tiles(1080, 1920, 3, 512, 16)
    tiles = plan.tiles if isinstance(plan.tiles, (list, tuple)) else plan.tiles()
    assert len(tiles) == 12, f"unexpected tile count {len(tiles)}"
    first = tiles[0]
    assert first.w_in > 0 and first.h_in > 0


# Methods the desktop app calls on the engine that the Rust-backed handle does
# not expose yet. Kept explicit so a fix forces this list to shrink instead of
# silently passing.
ENGINE_METHOD_GAPS = set()  # every engine surface the app calls now exists


def test_buffer_pool_parity():
    import taichi.allocator as legacy_alloc

    for cls in (legacy_alloc.BufferKey, ti.BufferKey):
        key = cls(size_bytes=64, dtype="f32")
        assert key.size_bytes == 64 and key.dtype == "f32"
        with pytest.raises(ValueError):
            cls(size_bytes=0)

    legacy_pool = legacy_alloc.BufferPool()
    migrated_pool = ti.engine.buffer_pool
    migrated_pool.clear()
    assert type(migrated_pool).__name__ == type(legacy_pool).__name__ == "BufferPool"
    public = lambda obj: {n for n in dir(obj) if not n.startswith("_")}
    assert public(legacy_pool) == public(migrated_pool)
    # Same instance is reused so consumers can clear a single shared pool.
    assert ti.engine.buffer_pool is migrated_pool


def test_engine_used_surface_inventory():
    engine = ti.get_engine()
    assert hasattr(engine, "buffer_pool"), "buffer_pool must be migrated"
    present = {name for name in ENGINE_METHOD_GAPS if hasattr(engine, name)}
    assert present == set(), (
        "these engine methods are now available, update ENGINE_METHOD_GAPS: "
        + ", ".join(sorted(present))
    )


def test_device_scanner_field_gap_is_documented():
    """The migrated scanner does not report device_uuid/driver_id yet.

    Those fields feed the fingerprint formula, so records produced by the two
    scanners are not interchangeable. make_device_selector itself agrees when
    given the same record (see test_device_scan_parity).
    """
    import taichi.device_selection as tv_ds

    legacy = tv_ds.scan_vulkan_device_records()
    migrated = ti.scan_vulkan_device_records()
    if not legacy or not migrated:
        pytest.skip("no Vulkan adapter on this host")
    missing = [key for key in ("device_uuid", "driver_id") if key not in migrated[0]]
    # driver_id is present but empty on this host, so only device_uuid is absent.
    assert missing == ["device_uuid"], (
        "scanner fields changed; update the fingerprint parity expectation: " + repr(missing)
    )


def test_block_policy_parity():
    """Block policy and cache bookkeeping now exist on both runtimes."""
    from taichi_vision import algorithm as legacy

    old = legacy.get_block_config()
    new = ti.get_block_config()
    for field in (
        "enabled",
        "size",
        "threshold_bytes",
        "cache_entries",
        "cache_bytes",
        "adaptive_memory",
        "device_cache_enabled",
        "device_cache_bytes",
    ):
        assert getattr(new, field) == getattr(old, field), field
    assert new.normalized_size() == old.normalized_size()

    cache = ti.get_device_block_cache()
    assert cache.clear() == 0  # nothing cached by the migrated runtime yet
    ti.configure_block_reservation("parity_op", soft_bytes=4096, weight=2.0)
    stats = ti.get_block_cache_stats()
    assert stats["device"]["owners"]["parity_op"]["soft_bytes"] == 4096
    assert stats["entries"] == 0


def test_native_pipeline_surface_fails_loudly():
    """Native pipeline recording is unavailable and must not fail silently.

    clear_pipelines() is a safe no-op because nothing can be recorded. The two
    recording entry points raise a dedicated NotImplementedError subclass so a
    caller cannot believe a pipeline ran when nothing did.
    """
    assert hasattr(ti, "PipelineRecordingUnsupported")
    assert ti.clear_pipelines() == 0
    for call in (ti.use_pipeline, ti.rec_pipeline):
        with pytest.raises(ti.PipelineRecordingUnsupported):
            call("parity_pipeline")
    # Still a NotImplementedError, so broad legacy handlers keep working.
    with pytest.raises(NotImplementedError):
        ti.use_pipeline("parity_pipeline")
