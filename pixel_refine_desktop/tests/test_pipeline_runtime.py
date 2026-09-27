"""CPU-only tests for generic frame streaming and runtime lifecycle."""

from __future__ import annotations

import threading

import pytest

from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
    PREFETCH_SETTING_KEY,
    PipelineCancelledError,
    PipelineRuntime,
    normalize_prefetch_depth,
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
