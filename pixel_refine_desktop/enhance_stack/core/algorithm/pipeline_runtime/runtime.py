"""Bounded, ordered frame streaming and per-job resource lifecycle."""

from __future__ import annotations

import contextvars
import inspect
import json
import queue
import sys
import threading
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Iterable, Iterator, Mapping

from .contracts import (
    PipelineCancelledError,
    PipelineExecutionContext,
    PipelineOptions,
    PipelineRecipe,
    PipelineSource,
)


PREFETCH_SETTING_KEY = "pipeline_prefetch_depth"
PREFETCH_MIN = 0
PREFETCH_MAX = 4
_MISSING = object()
_DONE = object()


def normalize_prefetch_depth(value: Any) -> int:
    """Return a valid 0..4 prefetch depth; invalid values safely disable it."""
    if isinstance(value, bool) or value is None:
        return 0
    try:
        if isinstance(value, float) and not value.is_integer():
            return 0
        text = str(value).strip()
        if not text:
            return 0
        depth = int(text, 10)
    except (TypeError, ValueError, OverflowError):
        return 0
    return depth if PREFETCH_MIN <= depth <= PREFETCH_MAX else 0


def resolve_prefetch_depth(
    requested: Any = None,
    *,
    store: Any = None,
    legacy_fallback: Any = None,
) -> int:
    """Snapshot the UI setting once, falling back safely outside the desktop app."""
    if requested is not None:
        return normalize_prefetch_depth(requested)

    if store is None:
        try:
            from config import GENERAL_SETTINGS_FILE

            with open(GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as handle:
                persisted = json.load(handle)
            if isinstance(persisted, dict) and PREFETCH_SETTING_KEY in persisted:
                return normalize_prefetch_depth(persisted[PREFETCH_SETTING_KEY])
        except Exception:
            pass

    if store is not None:
        try:
            value = store.get(PREFETCH_SETTING_KEY, _MISSING)
            if value is not _MISSING:
                return normalize_prefetch_depth(value)
        except Exception:
            pass

    return normalize_prefetch_depth(legacy_fallback)


def _event_is_set(event: Any) -> bool:
    if event is None:
        return False
    if hasattr(event, "is_set"):
        return bool(event.is_set())
    if callable(event):
        return bool(event())
    return bool(event)


def _dispose(value: Any, disposer: Callable[[Any], None] | None) -> None:
    if disposer is None:
        return
    try:
        disposer(value)
    except Exception:
        # Cleanup must not replace the processing or cancellation error.
        pass


@dataclass(frozen=True)
class _Loaded:
    index: int
    value: Any


@dataclass(frozen=True)
class _Failed:
    error: BaseException


class _BoundedSupportStream(Iterator[tuple[int, Any]]):
    """One ordered loader with a bounded host queue and deterministic cleanup."""

    def __init__(
        self,
        indices: Iterable[int],
        loader: Callable[[int], Any],
        *,
        depth: int,
        stop_event: Any = None,
        stop_when: Callable[[], bool] | None = None,
        raise_on_cancel: bool = False,
        disposer: Callable[[Any], None] | None = None,
    ):
        self._indices = iter(indices)
        self._loader = loader
        self._depth = normalize_prefetch_depth(depth)
        self._stop_event = stop_event
        self._stop_when = stop_when
        self._raise_on_cancel = bool(raise_on_cancel)
        self._disposer = disposer
        self._closed = False
        self._done = False
        self._internal_stop = threading.Event()
        self._queue: queue.Queue[Any] | None = (
            queue.Queue(maxsize=self._depth) if self._depth > 0 else None
        )
        # Reserve a slot BEFORE decoding. A full queue must not retain an
        # additional decoded frame in the producer's local variable.
        self._slots = threading.BoundedSemaphore(self._depth) if self._depth else None
        self.peak_buffered_frames = 0
        self._thread: threading.Thread | None = None
        if self._queue is not None:
            self._thread = threading.Thread(
                target=self._produce,
                name="PipelineHostPrefetch",
                daemon=True,
            )
            self._thread.start()

    @property
    def max_buffered_frames(self) -> int:
        return 0 if self._queue is None else self._queue.maxsize

    def _stopped(self) -> bool:
        if self._internal_stop.is_set() or _event_is_set(self._stop_event):
            return True
        if self._stop_when is not None:
            try:
                return bool(self._stop_when())
            except Exception:
                return True
        return False

    def _enqueue(self, item: Any) -> bool:
        assert self._queue is not None
        while not self._internal_stop.is_set():
            try:
                self._queue.put(item, timeout=0.05)
                self.peak_buffered_frames = max(
                    self.peak_buffered_frames, self._queue.qsize()
                )
                return True
            except queue.Full:
                if self._stopped():
                    return False
        return False

    def _produce(self) -> None:
        assert self._queue is not None
        try:
            for raw_index in self._indices:
                if self._stopped():
                    break
                while not self._stopped():
                    if self._slots.acquire(timeout=0.05):
                        break
                else:
                    break
                index = int(raw_index)
                value = self._loader(index)
                if self._stopped():
                    _dispose(value, self._disposer)
                    break
                if not self._enqueue(_Loaded(index, value)):
                    _dispose(value, self._disposer)
                    break
                del value
        except BaseException as exc:
            self._enqueue(_Failed(exc))
        finally:
            self._enqueue(_DONE)

    def __iter__(self) -> _BoundedSupportStream:
        return self

    def __next__(self) -> tuple[int, Any]:
        if self._closed or self._done:
            raise StopIteration
        if self._stopped():
            self.close()
            if self._raise_on_cancel and _event_is_set(self._stop_event):
                raise PipelineCancelledError("Pipeline support stream cancelled")
            raise StopIteration

        if self._queue is None:
            try:
                index = int(next(self._indices))
            except StopIteration:
                self._done = True
                raise
            return index, self._loader(index)

        while not self._closed:
            if self._stopped():
                self.close()
                if self._raise_on_cancel and _event_is_set(self._stop_event):
                    raise PipelineCancelledError("Pipeline support stream cancelled")
                raise StopIteration
            try:
                item = self._queue.get(timeout=0.05)
            except queue.Empty:
                if self._thread is not None and not self._thread.is_alive():
                    self._done = True
                    raise StopIteration
                continue

            if item is _DONE:
                self._done = True
                raise StopIteration
            if isinstance(item, _Failed):
                self.close()
                raise item.error
            if isinstance(item, _Loaded):
                self._slots.release()
                return item.index, item.value
        raise StopIteration

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._internal_stop.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            # Decoders cannot be interrupted safely. Wait for the current decode
            # to return before releasing resources it can still access.
            self._thread.join()
        if self._queue is not None:
            while True:
                try:
                    item = self._queue.get_nowait()
                except queue.Empty:
                    break
                if isinstance(item, _Loaded):
                    _dispose(item.value, self._disposer)


_active_runtime: contextvars.ContextVar[PipelineRuntime | None] = contextvars.ContextVar(
    "pixel_refine_pipeline_runtime", default=None
)


class PipelineRuntime:
    """Per-job runtime for ordered frames, bounded prefetch, and session lifetime."""

    def __init__(
        self,
        *,
        prefetch_depth: Any = 0,
        stop_event: Any = None,
        progress_callback: Callable[..., None] | None = None,
        session: Any = None,
        session_factory: Callable[[Any], Any] | None = None,
    ):
        self.prefetch_depth = normalize_prefetch_depth(prefetch_depth)
        self.stop_event = stop_event
        self.progress_callback = progress_callback
        self._session = session
        self._owns_session = session is None
        self._session_factory = session_factory
        self._closed = False
        self._lock = threading.RLock()
        self._streams: set[_BoundedSupportStream] = set()
        self._worker_stop = threading.Event()
        self._workers: list[threading.Thread] = []

    @property
    def buffer_session(self):
        """Existing session, also available to cleanup callbacks while closing."""
        return self._session

    @property
    def worker_stop_requested(self) -> bool:
        return self._worker_stop.is_set()

    def start_worker(self, *, target, name):
        """Start a stage with this job's context, never a global API patch."""
        with self._lock:
            if self._closed or self._worker_stop.is_set():
                raise RuntimeError("PipelineRuntime is stopping")
            context = contextvars.copy_context()

            def run():
                token = _active_runtime.set(self)
                try:
                    target()
                finally:
                    _active_runtime.reset(token)

            worker = threading.Thread(target=lambda: context.run(run), name=name, daemon=True)
            self._workers.append(worker)
            worker.start()
            return worker

    def stop_workers(self):
        """Quiesce stages and host producers before any GPU lease is released."""
        self._worker_stop.set()
        self.close_streams()
        with self._lock:
            workers = tuple(self._workers)
        for worker in workers:
            if worker is not threading.current_thread():
                worker.join()

    @property
    def session(self) -> Any:
        return self.ensure_session()

    def ensure_session(self, engine: Any = None) -> Any:
        with self._lock:
            if self._closed:
                raise RuntimeError("PipelineRuntime is closed")
            if self._session is None:
                if self._session_factory is not None:
                    self._session = self._session_factory(engine)
                else:
                    from taichi_vision.taichi_algorithm.buffer_session import (
                        BufferSession,
                    )

                    if engine is None:
                        from taichi_vision.taichi_aot import get_engine

                        engine = get_engine()
                    self._session = BufferSession(engine=engine, sync_on_exit=False)
            return self._session

    def iter_supports(
        self,
        indices: Iterable[int],
        loader: Callable[[int], Any],
        *,
        stop_when: Callable[[], bool] | None = None,
        raise_on_cancel: bool = False,
        disposer: Callable[[Any], None] | None = None,
    ) -> Iterator[tuple[int, Any]]:
        if self._closed:
            raise RuntimeError("PipelineRuntime is closed")
        session = self._session
        release = disposer
        if session is not None and hasattr(session, "own"):
            def load_owned(index):
                value = loader(index)
                return session.own(value, releaser=disposer)
            stream_loader = load_owned
            release = session.release_buffer
        else:
            stream_loader = loader
        with self._lock:
            if self._closed:
                raise RuntimeError("PipelineRuntime is closed")
            if self._worker_stop.is_set():
                return
            stream = _BoundedSupportStream(
                indices,
                stream_loader,
                depth=self.prefetch_depth,
                stop_event=self.stop_event,
                stop_when=lambda: self._worker_stop.is_set() or (stop_when is not None and stop_when()),
                raise_on_cancel=raise_on_cancel,
                disposer=release,
            )
            self._streams.add(stream)
        try:
            for index, value in stream:
                try:
                    yield index, value
                finally:
                    _dispose(value, release)
        finally:
            stream.close()
            with self._lock:
                self._streams.discard(stream)

    def execute(
        self,
        source: PipelineSource,
        recipe: PipelineRecipe,
        support_indices: Iterable[int],
        *,
        options: Mapping[str, Any] | None = None,
        engine: Any = None,
    ) -> Any:
        """Run the common reference → ordered supports → finalize lifecycle."""
        try:
            session = self.ensure_session(engine)
            context = PipelineExecutionContext(
                session=session,
                options=PipelineOptions(
                    prefetch_depth=self.prefetch_depth,
                    values=dict(options or {}),
                ),
                stop_event=self.stop_event,
                progress_callback=self.progress_callback,
            )
            context.check_cancelled()
            reference = source.load_reference()
            if reference is not None and hasattr(session, "own"):
                session.own(reference)
            reference_state = recipe.prepare_reference(reference, context)
            for index, support in self.iter_supports(
                support_indices,
                source.load_support,
                raise_on_cancel=True,
            ):
                context.check_cancelled()
                recipe.process_support(index, support, reference_state, context)
            context.check_cancelled()
            return recipe.finalize(reference_state, context)
        finally:
            # execute() represents one complete job. Always stop prefetch and
            # release the owned session, including when a recipe or source
            # raises; callers using the context manager remain idempotent.
            active_error = sys.exc_info()[1]
            try:
                self.close()
            except Exception:
                if active_error is None:
                    raise

    def close_streams(self) -> None:
        """Stop host producers without ending the job-level resource session."""
        with self._lock:
            streams = tuple(self._streams)
        for stream in streams:
            stream.close()

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            session = self._session if self._owns_session else None
        try:
            self.stop_workers()
            if session is not None:
                session.close()
        finally:
            with self._lock:
                self._streams.clear()
                self._workers.clear()
                if self._owns_session:
                    self._session = None

    def __enter__(self) -> PipelineRuntime:
        if self._closed:
            raise RuntimeError("PipelineRuntime is closed")
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        try:
            self.close()
        except Exception:
            if exc_type is None:
                raise
        return False


def current_pipeline_runtime() -> PipelineRuntime | None:
    """Return the runtime scope installed by ``runtime_entrypoint`` if any."""
    return _active_runtime.get()


def runtime_entrypoint(function: Callable[..., Any]) -> Callable[..., Any]:
    """Snapshot prefetch settings and guarantee job-session cleanup for an entrypoint."""
    signature = inspect.signature(function)

    @wraps(function)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if current_pipeline_runtime() is not None:
            return function(*args, **kwargs)
        bound = signature.bind_partial(*args, **kwargs)
        requested = bound.arguments.get("prefetch_depth")
        depth = resolve_prefetch_depth(requested)
        runtime = PipelineRuntime(
            prefetch_depth=depth,
            stop_event=bound.arguments.get("stop_event"),
            progress_callback=bound.arguments.get("progress_callback"),
        )
        token = _active_runtime.set(runtime)
        try:
            return function(*args, **kwargs)
        finally:
            active_error = sys.exc_info()[1]
            try:
                runtime.close()
            except Exception:
                if active_error is None:
                    raise
            finally:
                _active_runtime.reset(token)

    return wrapped


__all__ = [
    "PREFETCH_MAX",
    "PREFETCH_MIN",
    "PREFETCH_SETTING_KEY",
    "PipelineRuntime",
    "current_pipeline_runtime",
    "normalize_prefetch_depth",
    "resolve_prefetch_depth",
    "runtime_entrypoint",
]
