import gc
import weakref

import numpy as np
import pytest

from taichi_vision.taichi_algorithm import buffer_session as buffer_session_module


class _Buffer:
    def __init__(self, shape, dtype, payload=None):
        self.shape = tuple(shape)
        self.dtype = np.dtype(dtype)
        self.payload = payload
        self.released = False
        self.is_owner = True
        self.release_count = 0

    def release(self):
        self.released = True
        self.is_owner = False
        self.release_count += 1


class _Engine:
    def __init__(self):
        self.upload_count = 0
        self.all_buffers = []
        self.sync_count = 0

    def allocate(self, shape, dtype=np.float32, is_vector=False, vector_dim=None):
        del is_vector, vector_dim
        return self._new_buffer(shape, dtype)

    def upload(self, data, is_vector=False, vector_dim=3):
        del is_vector, vector_dim
        self.upload_count += 1
        return self._new_buffer(data.shape, data.dtype, np.array(data, copy=True))

    def _new_buffer(self, shape, dtype, payload=None):
        buffer = _Buffer(shape, dtype, payload)
        self.all_buffers.append(buffer)
        return buffer

    def sync(self):
        self.sync_count += 1


def _session(monkeypatch):
    monkeypatch.setattr(buffer_session_module, "TaichiGPUBuffer", _Buffer)
    engine = _Engine()
    return buffer_session_module.BufferSession(engine=engine), engine


def test_upload_cache_refresh_and_explicit_release(monkeypatch):
    session, engine = _session(monkeypatch)
    data = np.zeros((8, 8), dtype=np.float32)

    first, owned = session.upload_if_needed(data)
    cached, cached_owned = session.upload_if_needed(data)
    assert owned is True
    assert cached_owned is False
    assert cached is first
    assert engine.upload_count == 1

    data.fill(0.375)
    refreshed, refreshed_owned = session.upload_if_needed(data, refresh=True)
    assert refreshed_owned is True
    assert refreshed is not first
    np.testing.assert_array_equal(refreshed.payload, data)
    assert first.released is True

    session.release_upload(data)
    assert refreshed.released is True
    assert not session._upload_cache
    session.close()


def test_recycled_object_id_does_not_return_stale_upload(monkeypatch):
    session, engine = _session(monkeypatch)
    old_data = np.ones((4, 4), dtype=np.float32)
    stale_buffer, _ = session.upload_if_needed(old_data)
    old_ref = weakref.ref(old_data)
    del old_data
    gc.collect()
    assert old_ref() is None

    new_data = np.full((4, 4), 0.625, dtype=np.float32)
    # Model Python reusing the old object's integer id for the new array.
    session._upload_cache[id(new_data)] = (old_ref, stale_buffer)
    new_buffer, owned = session.upload_if_needed(new_data)

    assert owned is True
    assert new_buffer is not stale_buffer
    np.testing.assert_array_equal(new_buffer.payload, new_data)
    assert engine.upload_count == 2
    session.close()


def test_ring_reuses_slots_but_keeps_concurrent_slots_distinct(monkeypatch):
    session, _ = _session(monkeypatch)

    session.reset_ring()
    first = session.acquire_buffer((16, 16))
    second = session.acquire_buffer((16, 16))
    assert first is not second

    session.reset_ring()
    assert session.acquire_buffer((16, 16)) is first
    session.close()
    assert first.released and second.released


def test_reference_cache_replacement_releases_old_cached_buffers(monkeypatch):
    session, engine = _session(monkeypatch)
    gray = _Buffer((32, 32), np.float32)
    reference_level = _Buffer((16, 16), np.float32)
    external_level = _Buffer((8, 8), np.float32)
    source = np.zeros((32, 32), dtype=np.float32)
    source_ref = weakref.ref(source)
    for buffer in (gray, reference_level, external_level):
        session.own(buffer)
    session._reference_entry = (
        ("ref",), source_ref, gray, [gray, reference_level]
    )
    session._reference_pyramids[(1, 2, 3)] = (
        source_ref, [gray, external_level]
    )

    session._release_reference_caches()

    assert session._reference_entry is None
    assert not session._reference_pyramids
    assert gray.released and reference_level.released and external_level.released
    assert engine.sync_count == 1
    session.close()


def test_manually_releasing_reference_buffer_invalidates_its_pyramid(monkeypatch):
    session, _ = _session(monkeypatch)
    source = np.zeros((32, 32), dtype=np.float32)
    gray = _Buffer((32, 32), np.float32)
    level = _Buffer((16, 16), np.float32)
    session.own(gray)
    session.own(level)
    session._scratch_cache[("gray",)] = gray
    session._scratch_cache[("level",)] = level
    session._reference_entry = (
        ("reference",), weakref.ref(source), gray, [gray, level]
    )

    session.release_buffer(gray)

    assert session._reference_entry is None
    assert not session._scratch_cache
    assert gray.released and level.released
    assert not session._leased_buffers
    session.close()


def test_borrow_returns_same_buffer_and_defers_owner_release(monkeypatch):
    owner, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    buffer = owner.own(engine.allocate((8, 8)))

    assert borrower.borrow(buffer, from_session=owner) is buffer
    owner.release_buffer(buffer)
    assert not buffer.released

    borrower.release_borrow(buffer)
    assert buffer.released
    owner.close()
    borrower.close()


def test_transfer_moves_ownership_without_copy_or_reallocation(monkeypatch):
    source, engine = _session(monkeypatch)
    target = buffer_session_module.BufferSession(engine=engine)
    buffer = source.own(engine.allocate((8, 8)))
    allocations = len(engine.all_buffers)

    assert source.transfer(buffer, target) is buffer
    assert len(engine.all_buffers) == allocations
    source.close()
    assert not buffer.released
    target.close()
    assert buffer.released


def test_transfer_rejects_active_borrow(monkeypatch):
    owner, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    target = buffer_session_module.BufferSession(engine=engine)
    buffer = owner.own(engine.allocate((8, 8)))
    borrower.borrow(buffer, from_session=owner)

    with pytest.raises(RuntimeError, match="active borrowers"):
        owner.transfer(buffer, target)
    with pytest.raises(RuntimeError, match="already has an owner"):
        target.own(buffer)

    borrower.close()
    assert owner.transfer(buffer, target) is buffer
    owner.close()
    target.close()
    assert buffer.released


def test_borrowed_scratch_is_not_reused_at_ring_reset(monkeypatch):
    owner, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    first = owner.acquire_buffer((8, 8))
    borrower.borrow(first, from_session=owner)

    owner.reset_ring()
    second = owner.acquire_buffer((8, 8))
    assert second is not first

    borrower.release_borrow(first)
    owner.reset_ring()
    assert owner.acquire_buffer((8, 8)) is first
    owner.close()
    borrower.close()


def test_host_buffer_borrow_and_transfer_use_original_object(monkeypatch):
    source, engine = _session(monkeypatch)
    target = buffer_session_module.BufferSession(engine=engine)
    host = np.empty((4, 4), dtype=np.float32)
    released = []
    source.own(host, releaser=released.append)

    with target.borrowed(host, from_session=source) as borrowed:
        assert borrowed is host
        with pytest.raises(RuntimeError, match="active borrowers"):
            source.transfer(host, target)
    assert source.transfer(host, target) is host
    source.close()
    assert released == []
    target.close()
    assert released[0] is host


def test_closing_owner_waits_for_other_session_borrow(monkeypatch):
    owner, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    buffer = owner.own(engine.allocate((8, 8)))
    borrower.borrow(buffer, from_session=owner)

    owner.close()
    assert not buffer.released
    borrower.close()
    assert buffer.released


def test_transfer_rejects_different_gpu_engine(monkeypatch):
    owner, engine = _session(monkeypatch)
    other_engine = _Engine()
    target = buffer_session_module.BufferSession(engine=other_engine)
    buffer = engine.allocate((8, 8))
    buffer.engine = engine
    owner.own(buffer)

    with pytest.raises(ValueError, match="another engine"):
        owner.transfer(buffer, target)
    assert not buffer.released
    owner.close()
    target.close()
    assert buffer.released


def test_borrowed_scope_releases_after_exception(monkeypatch):
    owner, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    buffer = owner.own(engine.allocate((8, 8)))

    with pytest.raises(RuntimeError, match="sentinel"):
        with borrower.borrowed(buffer, from_session=owner) as same:
            assert same is buffer
            raise RuntimeError("sentinel")
    assert owner.transfer(buffer, borrower) is buffer
    owner.close()
    borrower.close()
    assert buffer.released


def test_non_owning_gpu_view_cannot_become_separate_owner(monkeypatch):
    session, engine = _session(monkeypatch)
    view = engine.allocate((8, 8))
    view.is_owner = False

    with pytest.raises(ValueError, match="non-owning GPU views"):
        session.own(view)
    assert not session._leased_buffers
    session.close()


def test_managed_api_captures_outputs_without_patching_or_host_retention(monkeypatch):
    session, engine = _session(monkeypatch)
    original_upload = engine.upload
    api = session.managed_api(engine)
    assert session.managed_api(engine) is api
    assert session.managed_api(api) is api
    host = np.zeros((8, 8), dtype=np.float32)
    buffer = api.upload(host)
    assert session.owned_count == 1
    assert engine.upload == original_upload
    assert buffer.payload is not host  # Only the normal upload copies data.
    assert session.track_result((host, buffer)) == (host, buffer)
    assert session.owned_count == 1
    session.release_tree((buffer, buffer))
    assert buffer.release_count == 1
    assert session.owned_count == 0
    session.close()


def test_detach_transfers_to_caller_without_copy_or_release(monkeypatch):
    session, engine = _session(monkeypatch)
    buffer = session.own(engine.allocate((8, 8)))
    allocations = len(engine.all_buffers)
    session.borrow(buffer)
    with pytest.raises(RuntimeError, match="active borrowers"):
        session.detach(buffer)
    session.release_borrow(buffer)
    assert session.detach(buffer) is buffer
    assert session.owned_count == session.borrowed_count == 0
    session.close()
    assert not buffer.released
    assert len(engine.all_buffers) == allocations
    buffer.release()


def test_managed_api_skips_views_and_keeps_parent_owned(monkeypatch):
    session, engine = _session(monkeypatch)
    parent = session.own(engine.allocate((8, 8)))
    view = _Buffer((8, 8), np.float32)
    view.is_owner = False
    view.parent_ref = parent
    assert session.track_result(view) is view
    session.release_tree(view)
    assert not view.released and not parent.released
    assert session.owned_count == 1
    session.close()
    assert parent.release_count == 1


def test_close_releases_remaining_resources_even_when_component_close_fails(monkeypatch):
    session, engine = _session(monkeypatch)
    calls = []

    class Component:
        def close(self):
            calls.append("component")
            raise OSError("cleanup failed")

    session.own(Component())
    buffer = session.own(engine.allocate((8, 8)))
    with pytest.raises(OSError, match="cleanup failed"):
        session.close()
    assert calls == ["component"]
    assert buffer.release_count == 1
    assert session.owned_count == session.borrowed_count == 0
    assert not session._managed_apis
    session.close()


def test_session_name_is_native_without_legacy_alias():
    import importlib.util
    from taichi_vision import taichi_algorithm
    assert taichi_algorithm.BufferSession is buffer_session_module.BufferSession
    assert not hasattr(taichi_algorithm, "ResidentSession")
    assert importlib.util.find_spec("taichi_vision.taichi_algorithm.resident_session") is None


def test_phase_release_retains_only_explicit_accumulator(monkeypatch):
    session, engine = _session(monkeypatch)
    accumulator = session.own(engine.allocate((8, 8)))
    scratch = session.own(engine.allocate((4, 4)))
    closed = []
    session.own(object(), releaser=lambda _: closed.append(True))
    session.release_all_except(accumulator)
    assert scratch.release_count == 1 and not accumulator.released
    assert closed == [True] and session.owned_count == 1
    session.close()
    assert accumulator.release_count == 1


def test_host_scratch_reuses_identity_and_respects_borrow(monkeypatch):
    session, _ = _session(monkeypatch)
    host = session.acquire_host((8, 8), tag="stats")
    assert session.acquire_host((8, 8), tag="stats") is host
    session.borrow(host)
    with pytest.raises(RuntimeError, match="still borrowed"):
        session.acquire_host((8, 8), tag="stats")
    session.release_borrow(host)
    assert session.acquire_host((8, 8), tag="stats") is host
    session.release_buffer(host)
    assert not session._scratch_cache
    session.close()


def test_release_tree_does_not_steal_other_session_owner(monkeypatch):
    source, engine = _session(monkeypatch)
    other = buffer_session_module.BufferSession(engine=engine)
    buffer = source.own(engine.allocate((8, 8)))
    with pytest.raises(RuntimeError, match="another session"):
        other.release_tree(buffer)
    assert not buffer.released
    source.close()
    other.close()


def test_noise_statistics_scratch_is_job_owned_and_reused(monkeypatch):
    from taichi_vision.taichi_algorithm.enhancement.estimate_noise import _gpu_noise_scratch
    session, engine = _session(monkeypatch)
    gpu, host = _gpu_noise_scratch(engine, (256,), session=session)
    gpu2, host2 = _gpu_noise_scratch(engine, (256,), session=session)
    assert gpu2 is gpu and host2 is host
    assert not hasattr(engine, "_estimate_noise_block_mad")
    assert session.owned_count == 2
    session.close()
    assert gpu.release_count == 1
    assert session.owned_count == 0


def test_managed_api_preserves_borrowed_destination_ownership(monkeypatch):
    from types import SimpleNamespace
    source, engine = _session(monkeypatch)
    borrower = buffer_session_module.BufferSession(engine=engine)
    destination = source.own(engine.allocate((8, 8)))
    borrower.borrow(destination, from_session=source)
    api = borrower.managed_api(SimpleNamespace(write=lambda *, dst: dst))
    assert api.write(dst=destination) is destination
    assert source.owned_count == 1 and borrower.owned_count == 0
    assert borrower.borrowed_count == 1
    borrower.close()
    assert not destination.released
    source.close()
    assert destination.release_count == 1
