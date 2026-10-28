"""CPU-only tests for generic frame streaming and runtime lifecycle."""

from __future__ import annotations

import threading
import json

import pytest

from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
    IN_PROCESSING_SETTING_KEY,
    PREFETCH_SETTING_KEY,
    PipelineCancelledError,
    PipelineRuntime,
    PipelineSourceDescriptor,
    normalize_in_processing_depth,
    normalize_prefetch_depth,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime.runtime import (
    _BoundedSupportStream,
)
from pixel_refine_desktop.ui.views.settings.General.general_store import DEFAULTS


@pytest.mark.parametrize("depth", range(5))
def test_prefetch_depth_accepts_supported_integer_range(depth):
    assert normalize_prefetch_depth(depth) == depth
    assert normalize_prefetch_depth(str(depth)) == depth


@pytest.mark.parametrize("value", [-1, 5, 2.5, True, None, "bad", ""])
def test_invalid_prefetch_depth_disables_prefetch(value):
    assert normalize_prefetch_depth(value) == 0


def test_performance_store_defaults_to_no_prefetch():
    assert DEFAULTS[PREFETCH_SETTING_KEY] == 0
    assert DEFAULTS[IN_PROCESSING_SETTING_KEY] == 1
    assert "processing_format" not in DEFAULTS


@pytest.mark.parametrize("depth", range(1, 5))
def test_in_processing_depth_accepts_supported_integer_range(depth):
    assert normalize_in_processing_depth(depth) == depth
    assert normalize_in_processing_depth(str(depth)) == depth


@pytest.mark.parametrize("value", [0, -1, 5, 2.5, True, None, "bad", ""])
def test_invalid_in_processing_depth_uses_serial_default(value):
    assert normalize_in_processing_depth(value) == 1


def test_resolve_in_processing_depth_reads_saved_performance_setting(
    tmp_path, monkeypatch
):
    import config

    settings_path = tmp_path / "settings.json"
    settings_path.write_text(
        json.dumps({IN_PROCESSING_SETTING_KEY: 3}), encoding="utf-8"
    )
    monkeypatch.setattr(config, "GENERAL_SETTINGS_FILE", str(settings_path))
    assert resolve_in_processing_depth() == 3


def test_runtime_in_processing_slots_are_shared_and_idempotent():
    runtime = PipelineRuntime(in_processing_depth=2)
    first = runtime.acquire_in_processing_slot()
    second = runtime.acquire_in_processing_slot()
    assert first is not None and second is not None
    assert runtime.in_processing_frames == 2
    assert runtime.peak_in_processing_frames == 2

    started = threading.Event()
    acquired = threading.Event()
    result = []

    def wait_for_slot():
        started.set()
        lease = runtime.acquire_in_processing_slot()
        result.append(lease)
        acquired.set()

    worker = threading.Thread(target=wait_for_slot)
    worker.start()
    assert started.wait(1)
    assert not acquired.wait(0.1)

    first.release()
    first.release()
    assert acquired.wait(2)
    worker.join(timeout=2)
    assert not worker.is_alive()
    third = result[0]
    assert third is not None
    assert runtime.in_processing_frames == 2

    second.release()
    third.release()
    assert runtime.in_processing_frames == 0
    runtime.close()


def test_prepared_supports_use_the_runtime_shared_slot_pool():
    runtime = PipelineRuntime(in_processing_depth=2)
    held = runtime.acquire_in_processing_slot()
    assert held is not None
    prepared = runtime.iter_prepared_supports(
        [7],
        lambda index: f"raw-{index}",
        lambda index, raw: (index, raw, "decoded"),
    )
    try:
        index, frame = next(prepared)
        assert index == 7
        assert frame == (7, "raw-7", "decoded")
        assert runtime.in_processing_frames == 2
        assert runtime.peak_in_processing_frames == 2
    finally:
        prepared.close()
        held.release()
    assert runtime.in_processing_frames == 0
    runtime.close()


def test_saved_setting_wins_and_invalid_saved_value_disables_prefetch():
    class Store:
        def __init__(self, value):
            self.value = value

        def get(self, key, default=None):
            assert key == PREFETCH_SETTING_KEY
            return self.value

    assert resolve_prefetch_depth(store=Store(3), legacy_fallback=1) == 3
    assert resolve_prefetch_depth(store=Store(99), legacy_fallback=1) == 0


def test_zero_depth_loads_synchronously_on_consumer_thread():
    consumer_thread = threading.get_ident()
    loader_threads = []
    stream = _BoundedSupportStream(
        range(4),
        lambda index: loader_threads.append(threading.get_ident()) or index,
        depth=0,
    )
    try:
        assert list(stream) == list(enumerate(range(4)))
        assert stream.max_buffered_frames == 0
        assert loader_threads == [consumer_thread] * 4
    finally:
        stream.close()


def test_prefetch_stream_preserves_order_and_respects_queue_capacity():
    stream = _BoundedSupportStream(
        range(40), lambda index: index, depth=2
    )
    try:
        assert list(stream) == list(enumerate(range(40)))
        assert stream.max_buffered_frames == 2
        assert stream.peak_buffered_frames <= 2
    finally:
        stream.close()


def test_close_drains_queued_host_frames_and_stops_producer():
    disposed = []
    stream = _BoundedSupportStream(
        range(20),
        lambda index: index,
        depth=2,
        disposer=disposed.append,
    )
    try:
        assert stream._queue is not None
        for _ in range(100):
            if stream._queue.qsize() == 2:
                break
            threading.Event().wait(0.005)
        assert stream._queue.qsize() == 2
    finally:
        stream.close()
    assert sorted(disposed)[:2] == [0, 1]
    assert stream._thread is not None
    assert not stream._thread.is_alive()


def test_recipe_executes_reference_supports_and_finalize_in_order():
    calls = []

    class Session:
        def close(self):
            pass

    class Source:
        def load_reference(self):
            calls.append("reference")
            return "ref"

        def load_support(self, index):
            calls.append(("load", index))
            return f"support-{index}"

    class Recipe:
        def prepare_reference(self, reference, context):
            calls.append(("prepare", reference, context.options.prefetch_depth))
            return {"reference": reference, "supports": []}

        def process_support(self, index, support, state, context):
            calls.append(("process", index, support))
            state["supports"].append(support)

        def finalize(self, state, context):
            calls.append("finalize")
            return state

    session = Session()
    runtime = PipelineRuntime(
        prefetch_depth=1, session_factory=lambda _engine: session
    )
    result = runtime.execute(Source(), Recipe(), range(1, 4))

    assert result == {
        "reference": "ref",
        "supports": ["support-1", "support-2", "support-3"],
    }
    assert runtime._closed
    assert calls[0] == "reference"
    assert calls[-1] == "finalize"
    assert [entry[1] for entry in calls if isinstance(entry, tuple) and entry[0] == "process"] == [1, 2, 3]


def test_prepared_recipe_executes_support_lifecycle_in_order():
    calls = []

    class Session:
        def close(self):
            pass

    class Source:
        def load_reference(self):
            return "ref"

        def load_support(self, index):
            calls.append(("load", index))
            return f"source-{index}"

    class Recipe:
        def prepare_reference(self, reference, context):
            return {"reference": reference, "supports": []}

        def prepare_support(self, index, support, state, context):
            calls.append(("prepare", index, support))
            return f"prepared-{support}"

        def process_support(self, index, support, state, context):
            calls.append(("process", index, support))
            state["supports"].append(support)

        def release_support(self, support, state, context):
            calls.append(("release", support))

        def finalize(self, state, context):
            calls.append(("finalize",))
            return state

    session = Session()
    runtime = PipelineRuntime(
        prefetch_depth=1,
        in_processing_depth=2,
        session_factory=lambda _engine: session,
    )
    result = runtime.execute(Source(), Recipe(), range(1, 4))

    assert result == {
        "reference": "ref",
        "supports": ["prepared-source-1", "prepared-source-2", "prepared-source-3"],
    }
    assert [call[1] for call in calls if call[0] == "process"] == [1, 2, 3]
    assert [call[1] for call in calls if call[0] == "release"] == [
        "prepared-source-1",
        "prepared-source-2",
        "prepared-source-3",
    ]
    assert calls.index(("release", "prepared-source-1")) > calls.index(
        ("process", 1, "prepared-source-1")
    )
    assert calls.index(("finalize",)) > calls.index(
        ("release", "prepared-source-3")
    )
    assert runtime.in_processing_frames == 0
    assert runtime._closed


@pytest.mark.parametrize("descriptor_source", ["execute", "source", "runtime"])
def test_runtime_forwards_opaque_source_descriptor(descriptor_source):
    descriptor = PipelineSourceDescriptor("raw", {"extension": ".DNG"})
    received = []

    class Session:
        def close(self):
            pass

    class Source:
        def load_reference(self):
            return "ref"

        def load_support(self, index):
            return index

    if descriptor_source == "source":
        Source.descriptor = descriptor

    class Recipe:
        def prepare_reference(self, reference, context):
            received.append(context.source_descriptor)
            return reference

        def process_support(self, index, support, state, context):
            received.append(context.source_descriptor)

        def finalize(self, state, context):
            received.append(context.source_descriptor)
            return state

    runtime_kwargs = (
        {"source_descriptor": descriptor} if descriptor_source == "runtime" else {}
    )
    runtime = PipelineRuntime(session_factory=lambda _engine: Session(), **runtime_kwargs)
    execute_kwargs = (
        {"source_descriptor": descriptor} if descriptor_source == "execute" else {}
    )
    assert runtime.execute(Source(), Recipe(), [0], **execute_kwargs) == "ref"
    assert received == [descriptor, descriptor, descriptor]


def test_prepared_recipe_requires_prepare_and_release_hooks_as_a_pair():
    class Source:
        def load_reference(self):
            return None

        def load_support(self, index):
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return None

        def prepare_support(self, index, support, state, context):
            return support

        def process_support(self, index, support, state, context):
            pass

        def finalize(self, state, context):
            return state

    runtime = PipelineRuntime(session_factory=lambda _engine: object())
    with pytest.raises(TypeError, match=r"both prepare_support\(\) and release_support\(\)"):
        runtime.execute(Source(), Recipe(), [1])
    assert runtime._closed


def test_prepared_recipe_waits_for_staged_completion_before_releasing_support():
    calls = []

    class Session:
        def close(self):
            pass

    class Completion:
        def __init__(self, index):
            self.index = index

        def result(self):
            calls.append(("complete", self.index))

    class Source:
        def load_reference(self):
            return "ref"

        def load_support(self, index):
            calls.append(("load", index))
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return reference

        def prepare_support(self, index, support, state, context):
            return support

        def process_support(self, index, support, state, context):
            calls.append(("submit", index))
            return Completion(index)

        def release_support(self, support, state, context):
            calls.append(("release", support))

        def finalize(self, state, context):
            calls.append(("finalize",))
            return state

    runtime = PipelineRuntime(
        prefetch_depth=0,
        in_processing_depth=2,
        session_factory=lambda _engine: Session(),
    )
    assert runtime.execute(Source(), Recipe(), range(1, 4)) == "ref"

    assert calls.index(("complete", 1)) < calls.index(("release", 1))
    assert calls.index(("release", 1)) < calls.index(("load", 3))
    assert calls.index(("complete", 2)) < calls.index(("release", 2))
    assert calls.index(("complete", 3)) < calls.index(("release", 3))
    assert calls.index(("finalize",)) > calls.index(("release", 3))
    assert runtime.in_processing_frames == 0
    assert runtime._closed


def test_prepared_recipe_drains_pending_supports_after_stage_failure():
    released = []

    class Session:
        def close(self):
            pass

    class Completion:
        def __init__(self, index):
            self.index = index

        def result(self):
            if self.index == 1:
                raise RuntimeError("stage failed")

    class Source:
        def load_reference(self):
            return None

        def load_support(self, index):
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return None

        def prepare_support(self, index, support, state, context):
            return support

        def process_support(self, index, support, state, context):
            return Completion(index)

        def release_support(self, support, state, context):
            released.append(support)

        def finalize(self, state, context):
            raise AssertionError("finalize should not run after a stage failure")

    runtime = PipelineRuntime(
        prefetch_depth=0,
        in_processing_depth=2,
        session_factory=lambda _engine: Session(),
    )
    with pytest.raises(RuntimeError, match="stage failed"):
        runtime.execute(Source(), Recipe(), range(1, 4))

    assert released == [1, 2]
    assert runtime.in_processing_frames == 0
    assert runtime._closed


def test_runtime_closes_owned_session_when_recipe_raises():
    class Session:
        closed = False

        def close(self):
            self.closed = True

    class Source:
        def load_reference(self):
            return None

        def load_support(self, index):
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return None

        def process_support(self, index, support, reference_state, context):
            raise ValueError("recipe failed")

        def finalize(self, reference_state, context):
            pytest.fail("finalize must not run after a recipe error")

    session = Session()
    runtime = PipelineRuntime(session_factory=lambda _engine: session)
    with pytest.raises(ValueError, match="recipe failed"):
        runtime.execute(Source(), Recipe(), [1])
    assert session.closed
    assert runtime._closed


def test_runtime_raises_cancel_and_closes_session():
    stop_event = threading.Event()

    class Session:
        closed = False

        def close(self):
            self.closed = True

    class Source:
        def load_reference(self):
            return None

        def load_support(self, index):
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return None

        def process_support(self, index, support, reference_state, context):
            stop_event.set()

        def finalize(self, reference_state, context):
            pytest.fail("finalize must not run after cancellation")

    session = Session()
    runtime = PipelineRuntime(
        prefetch_depth=1,
        stop_event=stop_event,
        session_factory=lambda _engine: session,
    )
    with pytest.raises(PipelineCancelledError):
        runtime.execute(Source(), Recipe(), range(4))
    assert session.closed
    assert runtime._closed


def test_prefetch_loader_error_stops_stream_and_closes_session():
    class Session:
        closed = False

        def close(self):
            self.closed = True

    class Source:
        def load_reference(self):
            return "ref"

        def load_support(self, index):
            if index == 2:
                raise OSError("decode failed")
            return index

    class Recipe:
        def prepare_reference(self, reference, context):
            return []

        def process_support(self, index, support, reference_state, context):
            reference_state.append(support)

        def finalize(self, reference_state, context):
            return reference_state

    session = Session()
    runtime = PipelineRuntime(
        prefetch_depth=1,
        session_factory=lambda _engine: session,
    )
    with pytest.raises(OSError, match="decode failed"):
        runtime.execute(Source(), Recipe(), range(1, 5))

    assert session.closed
    assert runtime._closed
    assert not runtime._streams


@pytest.mark.parametrize("depth", range(1, 5))
def test_full_queue_does_not_decode_an_extra_frame(depth):
    decoded = []
    ready = threading.Event()

    def load(index):
        decoded.append(index)
        if len(decoded) == depth:
            ready.set()
        return object()

    stream = _BoundedSupportStream(range(20), load, depth=depth)
    try:
        assert ready.wait(2)
        threading.Event().wait(0.1)
        assert len(decoded) == depth
        assert stream.peak_buffered_frames <= depth
    finally:
        stream.close()
    assert not stream._thread.is_alive()


def test_runtime_workers_inherit_scope_and_stop_before_session_close():
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import current_pipeline_runtime
    calls = []
    started = threading.Event()

    class Session:
        def close(self):
            calls.append("session-close")

    runtime = PipelineRuntime(session_factory=lambda _: Session())
    runtime.ensure_session()

    def stage():
        assert current_pipeline_runtime() is runtime
        started.set()
        while not runtime.worker_stop_requested:
            threading.Event().wait(0.01)
        calls.append("worker-stopped")

    worker = runtime.start_worker(target=stage, name="test-pipeline-stage")
    assert started.wait(2)
    runtime.close()
    assert not worker.is_alive()
    assert calls == ["worker-stopped", "session-close"]


def test_in_processing_queue_preserves_order_bounds_frames_and_releases_each():
    prepared_threads = []
    released = []
    runtime = PipelineRuntime(prefetch_depth=0, in_processing_depth=2)

    def prepare(index, value):
        prepared_threads.append(threading.get_ident())
        return value * 10

    stream = runtime.iter_prepared_supports(
        range(8),
        lambda index: index,
        prepare,
        prepared_disposer=released.append,
    )
    try:
        result = []
        for index, value in stream:
            result.append((index, value))
            threading.Event().wait(0.01)
        assert result == [(index, index * 10) for index in range(8)]
        assert runtime.peak_in_processing_frames <= 2
        assert runtime.peak_in_processing_frames == 2
        assert sorted(released) == [index * 10 for index in range(8)]
        assert prepared_threads
        assert set(prepared_threads) != {threading.get_ident()}
    finally:
        stream.close()
        runtime.close()


def test_in_processing_queue_drains_prepared_frames_when_consumer_stops_early():
    prepared = []
    released = []
    enough_prepared = threading.Event()
    runtime = PipelineRuntime(prefetch_depth=0, in_processing_depth=2)

    def prepare(index, value):
        prepared.append(value)
        if len(prepared) >= 2:
            enough_prepared.set()
        return value

    stream = runtime.iter_prepared_supports(
        range(20),
        lambda index: index,
        prepare,
        prepared_disposer=released.append,
    )
    try:
        assert next(stream) == (0, 0)
        assert enough_prepared.wait(2)
    finally:
        stream.close()
        runtime.close()

    assert sorted(released) == sorted(prepared)


def test_close_waits_for_in_progress_decode_before_session_cleanup():
    started = threading.Event()
    finish_decode = threading.Event()
    closed = threading.Event()
    disposed = []

    class Session:
        def close(self):
            closed.set()

    def load(index):
        started.set()
        assert finish_decode.wait(3)
        return index

    runtime = PipelineRuntime(prefetch_depth=1, session_factory=lambda _: Session())
    runtime.ensure_session()
    stream = runtime.iter_supports([1], load, disposer=disposed.append)
    consumer = runtime.start_worker(target=lambda: list(stream), name="test-decode-consumer")
    assert started.wait(2)
    closer = threading.Thread(target=runtime.close)
    closer.start()
    try:
        assert not closed.wait(0.1)
    finally:
        finish_decode.set()
        closer.join(3)
        consumer.join(3)
    assert closed.is_set()
    assert not closer.is_alive() and not consumer.is_alive()
    assert disposed == [1]


def test_recipe_error_is_not_masked_by_session_cleanup_error():
    class Session:
        def close(self):
            raise OSError("cleanup failed")

    class Source:
        def load_reference(self):
            raise ValueError("source failed")

    runtime = PipelineRuntime(session_factory=lambda _: Session())
    with pytest.raises(ValueError, match="source failed"):
        runtime.execute(Source(), object(), [])


def test_pipeline_execution_context_borrowed_and_buffer_delegation():
    class MockSession:
        def __init__(self):
            self._owned_resources = {}
            self._borrowed_resources = {}
            self.acquired = []

        def own(self, resource, releaser=None):
            self._owned_resources[id(resource)] = resource
            return resource

        def borrow(self, resource, from_session=None):
            self._borrowed_resources[id(resource)] = (resource, self._borrowed_resources.get(id(resource), (resource, 0))[1] + 1)
            return resource

        def release_borrow(self, resource):
            if id(resource) in self._borrowed_resources:
                del self._borrowed_resources[id(resource)]

        from contextlib import contextmanager
        @contextmanager
        def borrowed(self, resource, from_session=None):
            self.borrow(resource, from_session=from_session)
            try:
                yield resource
            finally:
                self.release_borrow(resource)

        def acquire_buffer(self, shape, **kwargs):
            buf = ("buf", shape)
            self.acquired.append(buf)
            return buf

        def upload_if_needed(self, array, **kwargs):
            return array, True

    session = MockSession()
    runtime = PipelineRuntime(session_factory=lambda _: session)
    ctx = runtime.ensure_session()

    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineExecutionContext,
        PipelineOptions,
    )
    context = PipelineExecutionContext(session=session, options=PipelineOptions())

    item = [1, 2, 3]
    context.own(item)
    assert id(item) in session._owned_resources

    with context.borrowed(item) as val:
        assert val is item
        assert id(item) in session._borrowed_resources
    assert id(item) not in session._borrowed_resources

    buf = context.acquire_buffer((10, 10))
    assert buf == ("buf", (10, 10))
    assert session.acquired == [("buf", (10, 10))]

    arr, uploaded = context.upload_if_needed("fake_array")
    assert arr == "fake_array" and uploaded is True


def test_runtime_and_context_share_ownership_aware_borrow_semantics():
    class MockSession:
        def __init__(self):
            self._owned_resources = {}
            self._borrowed_resources = {}
            self.borrow_calls = 0
            self.release_calls = 0
            self.borrowed_context_calls = 0

        def own(self, resource, releaser=None):
            self._owned_resources[id(resource)] = resource
            return resource

        def borrow(self, resource, from_session=None):
            self.borrow_calls += 1
            self._borrowed_resources[id(resource)] = (resource, 1)
            return resource

        def release_borrow(self, resource):
            self.release_calls += 1
            self._borrowed_resources.pop(id(resource), None)

        from contextlib import contextmanager

        @contextmanager
        def borrowed(self, resource, from_session=None):
            self.borrowed_context_calls += 1
            self.borrow(resource, from_session=from_session)
            try:
                yield resource
            finally:
                self.release_borrow(resource)

    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineExecutionContext,
        PipelineOptions,
    )

    session = MockSession()
    runtime = PipelineRuntime(session_factory=lambda _: session)
    context = PipelineExecutionContext(session=session, options=PipelineOptions())
    unowned = object()

    # Both facades pass unowned values through without creating a session lease.
    assert runtime.borrow(unowned) is unowned
    assert context.borrow(unowned) is unowned
    with runtime.borrowed(unowned) as value:
        assert value is unowned
    with context.borrowed(unowned) as value:
        assert value is unowned
    runtime.release_borrow(unowned)
    context.release_borrow(unowned)
    assert session.borrow_calls == 0
    assert session.release_calls == 0
    assert session.borrowed_context_calls == 0

    # Owned resources use the same delegated borrow/release path in both facades.
    owned = object()
    runtime.own(owned)
    assert runtime.borrow(owned) is owned
    runtime.release_borrow(owned)
    context.own(owned)
    with context.borrowed(owned) as value:
        assert value is owned
    assert session.borrow_calls == 2
    assert session.release_calls == 2
    assert session.borrowed_context_calls == 1


def test_pipeline_support_lease_borrowed_delegation():
    class MockSession:
        def __init__(self):
            self._owned_resources = {}
            self._borrowed = set()

        def own(self, res, releaser=None):
            self._owned_resources[id(res)] = res
            return res

        from contextlib import contextmanager
        @contextmanager
        def borrowed(self, res, from_session=None):
            self._borrowed.add(id(res))
            try:
                yield res
            finally:
                self._borrowed.discard(id(res))

    session = MockSession()
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime.runtime import (
        PipelineSupportLease,
    )
    runtime = PipelineRuntime(session_factory=lambda _: session)
    slot = runtime.acquire_in_processing_slot()
    payload = {"data": 42}
    session.own(payload)

    lease = PipelineSupportLease(0, payload, None, slot, session=session)
    with lease.borrowed() as val:
        assert val is payload
        assert id(payload) in session._borrowed
    assert id(payload) not in session._borrowed
    lease.release()

