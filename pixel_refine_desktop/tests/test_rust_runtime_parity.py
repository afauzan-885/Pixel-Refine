"""
Parity Harness: Taichi Vision (Legacy Oracle) vs Native Taichi (Rust 1.8.0)
============================================================================
Uji diferensial terbatas; hasil lulus tidak membuktikan parity menyeluruh.
Paket taichi yang terpasang dapat mengandung wrapper Python dan edit lokal.
"""
import taichi.aot_engine as _ti_rt

import numpy as np
import pytest
import taichi as ti

def test_backend_config_parity():
    import taichi.backend_config as tv_bc
    import taichi as ti
    
    # 1. CANONICAL_BACKENDS
    assert tuple(ti.CANONICAL_BACKENDS) == tuple(tv_bc.CANONICAL_BACKENDS)
    
    # 2. normalize_backend
    for b in ["CUDA", "vulkan", "HOST", "cpu_x86_64_windows", "gl", "auto"]:
        assert ti.normalize_backend(b) == tv_bc.normalize_backend(b)
        
    # 3. normalize_vendor
    for v in ["NVIDIA GeForce MX150", "Intel(R) UHD Graphics 620", "AMD Radeon"]:
        assert ti.normalize_vendor(v) == tv_bc.normalize_vendor(v)
        
    # 4. BackendConfig dataclass parity
    cfg_tv = tv_bc.BackendConfig(backend="vulkan", device_id=0)
    cfg_ti = ti.BackendConfig(backend="vulkan", device_id=0)
    assert cfg_tv.backend == cfg_ti.backend
    assert cfg_tv.device_id == cfg_ti.device_id
    assert cfg_tv.is_gpu == cfg_ti.is_gpu
    assert cfg_ti.target_family == cfg_tv.target_family
    
    # 5. backend_env
    env_ti = ti.backend_env(cfg_ti)
    assert env_ti.get('AOT_ARCH') == 'vulkan'
    assert env_ti.get('AOT_DEVICE') == '0'
    assert 'PIXEL_REFINE_AOT_ARCH' not in env_ti


def test_device_selection_parity():
    import taichi.device_selection as tv_ds
    import taichi.backend_config as tv_bc
    import taichi as ti
    
    # 1. scan_vulkan_device_records
    rec_tv = tv_ds.scan_vulkan_device_records()
    rec_ti = ti.scan_vulkan_device_records()
    assert len(rec_ti) == len(rec_tv)
    if len(rec_tv) > 0:
        assert rec_ti[0]["vendor"] == tv_bc.normalize_vendor(rec_tv[0]["name"])
        
    # 2. make_device_selector
    if len(rec_tv) > 0:
        sel_tv = tv_ds.make_device_selector(rec_tv[0])
        sel_ti = ti.make_device_selector(rec_tv[0])
        assert sel_ti.get("fingerprint") == sel_tv.get("fingerprint")


def test_tile_planner_parity():
    import taichi as ti
    
    # Plan tiles 1080p, tile size 512, halo 16
    plan = ti.plan_tiles(1080, 1920, 3, 512, 16)
    assert plan is not None
    tiles = plan.tiles() if callable(plan.tiles) else plan.tiles
    assert len(tiles) == 12  # (ceil(1080/512)=3) * (ceil(1920/512)=4) = 12 tiles
    
    tile0 = tiles[0]
    assert tile0.w_in > 0
    assert tile0.h_in > 0


def test_buffer_allocation_and_upload_values():
    from taichi_vision import algorithm as tv_aot
    import taichi as ti
    
    # 1. Allocate buffer via engine
    eng_tv = _ti_rt.get_engine()
    eng_ti = ti.get_engine()
    
    buf_tv = eng_tv.allocate((64, 64, 3), dtype=np.float32, host_accessible=True)
    buf_ti = eng_ti.allocate((64, 64, 3), dtype=np.float32, host_accessible=True)
    
    ndim_tv = buf_tv.ndim() if callable(getattr(buf_tv, "ndim", None)) else buf_tv.ndim
    ndim_ti = buf_ti.ndim() if callable(getattr(buf_ti, "ndim", None)) else buf_ti.ndim
    assert ndim_tv == ndim_ti == 3
    
    nbytes_tv = buf_tv.nbytes() if callable(getattr(buf_tv, "nbytes", None)) else buf_tv.nbytes
    nbytes_ti = buf_ti.nbytes() if callable(getattr(buf_ti, "nbytes", None)) else buf_ti.nbytes
    assert nbytes_tv == nbytes_ti
    assert tuple(buf_tv.shape) == tuple(buf_ti.shape)
    
    # 2. Upload array
    arr = np.ones((32, 32, 4), dtype=np.float32)
    up_tv = _ti_rt.upload(arr)
    up_ti = ti.upload(arr)
    
    np.testing.assert_allclose(up_tv.to_numpy(), up_ti.to_numpy())
    
    # Cleanup
    buf_tv.release()
    buf_ti.release()
    up_tv.release()
    up_ti.release()


def test_buffer_session_ownership_parity():
    import taichi_vision.taichi_algorithm.buffer_session as tv_bs
    import taichi as ti
    
    # Test Scoped Session Context Manager
    with tv_bs.BufferSession(tag="test_tv") as sess_tv, ti.BufferSession(tag="test_ti") as sess_ti:
        arr = np.zeros((16, 16), dtype=np.float32)
        buf_tv = sess_tv.own(tv_bs.default_engine.upload(arr))
        buf_ti = sess_ti.own(ti.upload(arr))
        
        owned_tv = sess_tv.owned_count() if callable(sess_tv.owned_count) else sess_tv.owned_count
        owned_ti = sess_ti.owned_count() if callable(sess_ti.owned_count) else sess_ti.owned_count
        assert owned_tv == owned_ti == 1
        
        # Test Borrow
        borrow_tv = sess_tv.borrow(buf_tv)
        borrow_ti = sess_ti.borrow(buf_ti)
        borrowed_tv = sess_tv.borrowed_count() if callable(sess_tv.borrowed_count) else sess_tv.borrowed_count
        borrowed_ti = sess_ti.borrowed_count() if callable(sess_ti.borrowed_count) else sess_ti.borrowed_count
        assert borrowed_tv == borrowed_ti == 1
        
        sess_tv.release_borrow(buf_tv)
        sess_ti.release_borrow(buf_ti)
        borrowed_tv_after = sess_tv.borrowed_count() if callable(sess_tv.borrowed_count) else sess_tv.borrowed_count
        borrowed_ti_after = sess_ti.borrowed_count() if callable(sess_ti.borrowed_count) else sess_ti.borrowed_count
        assert borrowed_tv_after == borrowed_ti_after == 0


class _SessionEngine:
    def allocate(self, *args, **kwargs):
        raise AssertionError("unexpected allocation")

    def upload(self, *args, **kwargs):
        raise AssertionError("unexpected upload")

    def sync(self):
        pass


def test_native_session_repeated_borrow_matches_reference():
    """Exercise the PyO3 class directly without a device or Python facade."""
    from taichi.taichi_python import RustBufferSession
    from taichi_vision.taichi_algorithm.buffer_session import BufferSession

    def exercise(session_type):
        released = []
        resource = object()
        with session_type(engine=_SessionEngine(), sync_on_exit=False) as owner:
            owner.own(resource, releaser=lambda value: released.append(value))
            assert owner.borrow(resource) is resource
            assert owner.borrow(resource) is resource
            counts = [owner.borrowed_count]
            owner.release_borrow(resource)
            counts.append(owner.borrowed_count)
            owner.release_borrow(resource)
            counts.append(owner.borrowed_count)
        return counts, released == [resource]

    assert exercise(RustBufferSession) == exercise(BufferSession) == ([2, 1, 0], True)


def test_native_session_tag_matches_reference():
    from taichi.taichi_python import RustBufferSession
    from taichi_vision.taichi_algorithm.buffer_session import BufferSession

    for cls in (BufferSession, RustBufferSession):
        with cls(engine=_SessionEngine(), sync_on_exit=False, tag="audit") as session:
            assert session.tag == "audit"
