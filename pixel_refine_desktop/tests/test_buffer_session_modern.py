"""Modern BufferSession contract: smart caches, leases, and recursive release.

These tests exercise the native ``RustBufferSession`` through the thin Python
facade. They cover the behaviours the pipeline depends on when it mixes
stage-level, frame-level, and tile-level allocation.
"""

import threading

import numpy as np

from taichi import BufferSession


def _session(**kwargs):
    return BufferSession(tag="modern-session", sync_on_exit=False, **kwargs)


def test_tagged_scratch_reuses_matching_signature():
    session = _session()
    try:
        first = session.view((8, 8), dtype=np.float32, tag="scratch")
        second = session.view((8, 8), dtype=np.float32, tag="scratch")
        assert first is second
        assert session.owned_count == 1
    finally:
        session.close()


def test_tagged_scratch_evicts_on_shape_and_dtype_change():
    session = _session()
    try:
        first = session.view((8, 8), dtype=np.float32, tag="scratch")
        reshaped = session.view((16, 8), dtype=np.float32, tag="scratch")
        assert reshaped is not first
        assert first.handle is None
        assert session.owned_count == 1

        retyped = session.view((16, 8), dtype=np.float64, tag="scratch")
        assert retyped is not reshaped
        assert reshaped.handle is None
        assert session.owned_count == 1
    finally:
        session.close()


def test_untagged_ring_buffer_cycles_slots():
    session = _session(ring_slots=2)
    try:
        first = session.view((8, 8), dtype=np.float32)
        second = session.view((8, 8), dtype=np.float32)
        third = session.view((8, 8), dtype=np.float32)
        assert first is not second
        assert third in (first, second)
        session.reset_ring()
        resumed = session.view((8, 8), dtype=np.float32)
        assert resumed in (first, second, third)
    finally:
        session.close()


def test_named_ring_buffer_respects_depth():
    session = _session()
    try:
        slots = {
            session.acquire_ring_buffer("stage", (8, 8), depth=2, dtype=np.float32)
            for _ in range(6)
        }
        assert len(slots) <= 2
    finally:
        session.close()


def test_borrow_lease_supports_both_usage_styles():
    session = _session()
    try:
        buffer = session.view((8, 8), dtype=np.float32, tag="lease")
        lease = session.borrow(buffer)
        assert lease.resource is buffer
        assert session.borrowed_count == 1
        session.release(buffer)
        assert buffer.handle is not None
        lease.release()
        assert buffer.handle is None
        assert session.borrowed_count == 0

        scoped = session.view((8, 8), dtype=np.float32, tag="scoped")
        with session.borrow(scoped) as pinned:
            assert pinned is scoped
            assert session.borrowed_count == 1
        assert session.borrowed_count == 0
    finally:
        session.close()


def test_release_borrow_accepts_buffer_or_lease():
    session = _session()
    try:
        buffer = session.view((8, 8), dtype=np.float32, tag="release-borrow")
        lease = session.borrow(buffer)
        session.release_borrow(lease)
        assert session.borrowed_count == 0
    finally:
        session.close()


def test_borrow_from_worker_thread_defers_physical_release():
    session = _session()
    released = threading.Event()
    try:
        buffer = session.view((8, 8), dtype=np.float32, tag="threaded")
        lease = session.borrow(buffer)

        def worker():
            session.release(buffer)
            assert buffer.handle is not None
            lease.release()
            released.set()

        thread = threading.Thread(target=worker)
        thread.start()
        assert released.wait(5)
        thread.join(timeout=5)
        assert buffer.handle is None
    finally:
        session.close()


def test_tagged_upload_updates_in_place_when_signature_matches():
    session = _session()
    try:
        first = np.zeros((8, 8), dtype=np.float32)
        buffer, created = session.upload_if_needed(first, tag="upload")
        assert created is True

        second = np.full((8, 8), 3.0, dtype=np.float32)
        updated, created_again = session.upload_if_needed(second, tag="upload")
        assert updated is buffer
        assert created_again is False

        readback = updated.to_numpy()
        np.testing.assert_allclose(readback, second)
    finally:
        session.close()


def test_release_host_array_drops_cached_upload():
    session = _session()
    try:
        array = np.ones((4, 4), dtype=np.float32)
        first = session.view(array)
        assert session.view(array) is first
        session.release(array)
        assert session.view(array) is not first
    finally:
        session.close()


def test_release_tree_walks_tuples_lists_and_dicts():
    session = _session()
    try:
        a = session.view((4, 4), dtype=np.float32, tag="tree-a")
        b = session.view((4, 4), dtype=np.float32, tag="tree-b")
        c = session.view((4, 4), dtype=np.float32, tag="tree-c")
        session.release_tree({"a": a, "nested": (b, [c])})
        assert a.handle is None
        assert b.handle is None
        assert c.handle is None
        assert session.owned_count == 0
    finally:
        session.close()


def test_release_all_except_keeps_transients_and_cache():
    session = _session()
    try:
        scratch = session.view((4, 4), dtype=np.float32, tag="cached")
        transient = session.own(session.engine.allocate((4, 4), np.float32))
        session.release(keep=(scratch,))
        assert scratch.handle is not None
        assert transient.handle is None
    finally:
        session.close()


def test_host_scratch_reuses_slot_and_can_zero_it():
    session = _session()
    try:
        block = session.view((4, 4), dtype=np.float32, host=True, tag="host")
        block[...] = 5.0
        again = session.view((4, 4), dtype=np.float32, host=True, tag="host")
        assert again is block
        assert again[0, 0] == 5.0

        zeroed = session.acquire_host((4, 4), np.float32, tag="host-zero", zero=True)
        assert isinstance(zeroed, np.ndarray)
        assert zeroed.sum() == 0
    finally:
        session.close()


def test_transfer_and_detach_move_ownership_without_copying():
    session = _session()
    target = BufferSession(tag="modern-target", sync_on_exit=False)
    try:
        moved = session.view((4, 4), dtype=np.float32, tag="moved")
        session.transfer(moved, target)
        assert session.owned_count == 0
        assert target.owned_count == 1

        detached = session.view((4, 4), dtype=np.float32, tag="detached")
        session.detach(detached)
        assert detached.handle is not None
        session.close()
        assert detached.handle is not None
    finally:
        target.close()
