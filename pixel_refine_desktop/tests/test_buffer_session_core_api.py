"""Contract tests for the three-API BufferSession surface."""

import numpy as np

from taichi import BufferSession


def _session():
    return BufferSession(tag="core-api-test", sync_on_exit=False)


def test_view_scratch_reuses_tagged_slot():
    session = _session()
    try:
        first = session.view((8, 8), dtype=np.float32, tag="scratch")
        second = session.view((8, 8), dtype=np.float32, tag="scratch")
        assert first is second
        assert first.shape == (8, 8)
    finally:
        session.close()


def test_view_tagged_slot_replaces_changed_signature():
    session = _session()
    try:
        first = session.view((8, 8), dtype=np.float32, tag="signature")
        changed_shape = session.view((16, 8), dtype=np.float32, tag="signature")
        assert changed_shape is not first
        assert first.handle is None

        changed_dtype = session.view((16, 8), dtype=np.float64, tag="signature")
        assert changed_dtype is not changed_shape
        assert changed_shape.handle is None
    finally:
        session.close()


def test_view_host_scratch_uses_exact_shape_and_dtype_signature():
    session = _session()
    try:
        first = session.view((8, 8), dtype=np.float32, host=True, tag="host-signature")
        second = session.view((8, 8), dtype=np.float32, host=True, tag="host-signature")
        changed = session.view((8, 9), dtype=np.float32, host=True, tag="host-signature")
        changed_dtype = session.view((8, 9), dtype=np.float64, host=True, tag="host-signature")
        assert second is first
        assert changed is not first
        assert changed.shape == (8, 9)
        assert changed_dtype.dtype == np.float64
    finally:
        session.close()



def test_view_buffer_is_zero_copy_alias():
    session = _session()
    try:
        source = session.view((8, 8), dtype=np.float32, tag="alias-source")
        plain = session.view(source)
        vector = session.view(source, is_vector=True, vector_dim=1)
        assert plain is source
        assert vector.handle == source.handle
        assert vector.is_owner is False
        assert vector._parent_ref is source
    finally:
        session.close()


def test_view_host_array_and_upload_cache():
    session = _session()
    try:
        host = session.view((4, 4), dtype=np.float32, host=True, tag="host")
        assert isinstance(host, np.ndarray)
        assert host.shape == (4, 4)

        array = np.ones((4, 4), dtype=np.float32)
        first = session.view(array)
        second = session.view(array)
        assert first is second
        session.release(array)
        third = session.view(array)
        assert third is not first
    finally:
        session.close()


def test_borrow_holds_release_until_lease_ends():
    session = _session()
    try:
        buffer = session.view((8, 8), dtype=np.float32, tag="borrow-source")
        lease = session.borrow(buffer)
        assert lease.resource is buffer
        session.release(buffer)
        assert buffer.handle is not None
        lease.release()
        assert buffer.handle is None
    finally:
        session.close()


def test_release_transfer_retain_keep_and_tree():
    session = _session()
    target = BufferSession(tag="core-api-target", sync_on_exit=False)
    try:
        kept = session.view((4, 4), dtype=np.float32, tag="kept")
        transferred = session.view((4, 4), dtype=np.float32, tag="transferred")
        retained = session.view((4, 4), dtype=np.float32, tag="retained")
        dropped = session.view((4, 4), dtype=np.float32, tag="dropped")

        session.release(transferred, to=target)
        assert transferred.handle is not None

        session.release(retained, retain=True)
        assert retained.handle is not None

        session.release(keep=(kept,))
        assert kept.handle is not None
        assert dropped.handle is not None
    finally:
        target.close()
        assert transferred.handle is None
        session.close()
        assert kept.handle is None
        assert retained.handle is not None
        assert dropped.handle is None


def test_borrow_context_manager_yields_resource():
    session = _session()
    try:
        buffer = session.view((4, 4), dtype=np.float32, tag="ctx")
        with session.borrow(buffer) as pinned:
            assert pinned is buffer
    finally:
        session.close()
