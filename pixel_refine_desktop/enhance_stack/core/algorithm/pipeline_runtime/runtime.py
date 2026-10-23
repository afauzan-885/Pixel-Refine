"""Bounded, ordered frame streaming and per-job resource lifecycle."""

from __future__ import annotations

from contextlib import contextmanager
import contextvars
import inspect
import json
import os
import queue
import sys
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Iterable, Iterator, Mapping

from .contracts import (
    PipelineCancelledError,
    PipelineExecutionContext,
    PipelineOptions,
    PipelineRecipe,
    PipelineSourceDescriptor,
    PipelineSupportCompletion,
    PipelineSource,
)


PREFETCH_SETTING_KEY = "pipeline_prefetch_depth"
PREFETCH_MIN = 0
PREFETCH_MAX = 4
IN_PROCESSING_SETTING_KEY = "pipeline_in_processing_depth"
IN_PROCESSING_MIN = 1
IN_PROCESSING_MAX = 4
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


def normalize_in_processing_depth(value: Any) -> int:
    """Return a valid 1..4 in-processing capacity; invalid values use 1."""
    if isinstance(value, bool) or value is None:
        return IN_PROCESSING_MIN
    try:
        if isinstance(value, float) and not value.is_integer():
            return IN_PROCESSING_MIN
        text = str(value).strip()
        if not text:
            return IN_PROCESSING_MIN
        depth = int(text, 10)
    except (TypeError, ValueError, OverflowError):
        return IN_PROCESSING_MIN
    return depth if IN_PROCESSING_MIN <= depth <= IN_PROCESSING_MAX else IN_PROCESSING_MIN


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


def resolve_in_processing_depth(requested: Any = None) -> int:
    """Read the persisted in-processing capacity, falling back to one frame."""
    if requested is not None:
        return normalize_in_processing_depth(requested)
    try:
        from config import GENERAL_SETTINGS_FILE

        with open(GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as handle:
            persisted = json.load(handle)
        if isinstance(persisted, dict) and IN_PROCESSING_SETTING_KEY in persisted:
            return normalize_in_processing_depth(
                persisted[IN_PROCESSING_SETTING_KEY]
            )
    except Exception:
        pass
    return IN_PROCESSING_MIN


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


class InProcessingLease:
    """Idempotent ownership token for one admitted in-processing frame."""

    __slots__ = ("_runtime", "_token", "_lock", "_released")

    def __init__(self, runtime: PipelineRuntime, token: object):
        self._runtime = runtime
        self._token = token
        self._lock = threading.Lock()
        self._released = False

    def release(self) -> None:
        with self._lock:
            if self._released:
                return
            self._released = True
        self._runtime._release_in_processing_token(self._token)

    def __enter__(self) -> InProcessingLease:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.release()
        return False


class PipelineSupportLease:
    """Prepared payload whose admission and buffer ownership transfer together."""

    __slots__ = ("index", "value", "_release_value", "_lease", "_session", "_lock", "_released")

    def __init__(self, index, value, release_value, lease, *, retain_value=True, session=None):
        self.index = int(index)
        self.value = value if retain_value else None
        self._release_value = release_value
        self._lease = lease
        self._session = session
        self._lock = threading.Lock()
        self._released = False

    @contextmanager
    def borrowed(self):
        """Borrow the leased support value in the active session for safe zero-copy execution."""
        session = self._session
        if session is not None and hasattr(session, "borrowed") and self.value is not None:
            owned = getattr(session, "_owned_resources", None)
            if owned is not None and id(self.value) in owned:
                with session.borrowed(self.value) as val:
                    yield val
                return
        yield self.value

    def release(self) -> None:
        with self._lock:
            if self._released:
                return
            self._released = True
        try:
            _dispose(self.value, self._release_value)
        finally:
            self._lease.release()


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
        # Reserve a slot before loading so the producer cannot hold an extra
        # payload outside the bounded queue. Resident denoising loaders put
        # unchanged source-file bytes here and decode only after admission.
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
        in_processing_depth: Any = 1,
        stop_event: Any = None,
        progress_callback: Callable[..., None] | None = None,
        session: Any = None,
        session_factory: Callable[[Any], Any] | None = None,
        source_descriptor: PipelineSourceDescriptor | None = None,
    ):
        self.prefetch_depth = normalize_prefetch_depth(prefetch_depth)
        self.in_processing_depth = normalize_in_processing_depth(in_processing_depth)
        self.peak_in_processing_frames = 0
        self._in_processing_live = 0
        self._in_processing_slots = threading.BoundedSemaphore(
            self.in_processing_depth
        )
        self._in_processing_tokens: set[object] = set()
        self.stop_event = stop_event
        self.progress_callback = progress_callback
        self._session = session
        self._owns_session = session is None
        self._session_factory = session_factory
        self.source_descriptor = source_descriptor
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

    @property
    def in_processing_frames(self) -> int:
        with self._lock:
            return self._in_processing_live

    def acquire_in_processing_slot(
        self,
        *,
        stop_when: Callable[[], bool] | None = None,
        timeout: float | None = None,
    ) -> InProcessingLease | None:
        """Reserve one shared in-processing slot, observing cancellation."""

        while True:
            with self._lock:
                if self._closed:
                    return None
            if self._worker_stop.is_set() or _event_is_set(self.stop_event):
                return None
            if stop_when is not None:
                try:
                    if stop_when():
                        return None
                except Exception:
                    return None
            step_timeout = 0.05 if timeout is None else max(0.0, float(timeout))
            if not self._in_processing_slots.acquire(timeout=step_timeout):
                if timeout is not None:
                    return None
                continue
            with self._lock:
                if self._closed:
                    self._in_processing_slots.release()
                    return None
                token = object()
                self._in_processing_tokens.add(token)
                self._in_processing_live = len(self._in_processing_tokens)
                self.peak_in_processing_frames = max(
                    self.peak_in_processing_frames, self._in_processing_live
                )
            return InProcessingLease(self, token)

    def _release_in_processing_token(self, token: object) -> None:
        with self._lock:
            if token not in self._in_processing_tokens:
                return
            self._in_processing_tokens.remove(token)
            self._in_processing_live = len(self._in_processing_tokens)
        self._in_processing_slots.release()

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

    @contextmanager
    def borrowed(self, resource: Any, *, from_session: Any = None):
        """Scope a borrow lease on a GPU buffer/resource while passing it to the caller."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "borrowed") and resource is not None:
            owned = getattr(session, "_owned_resources", None)
            if owned is not None and id(resource) in owned:
                with session.borrowed(resource, from_session=from_session) as val:
                    yield val
                return
        yield resource

    def borrow(self, resource: Any, *, from_session: Any = None) -> Any:
        """Pin a buffer/resource in the underlying BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "borrow") and resource is not None:
            owned = getattr(session, "_owned_resources", None)
            if owned is not None and id(resource) in owned:
                return session.borrow(resource, from_session=from_session)
        return resource

    def release_borrow(self, resource: Any) -> None:
        """Release a previously pinned borrow on the underlying BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "release_borrow") and resource is not None:
            borrowed_res = getattr(session, "_borrowed_resources", None)
            if borrowed_res is not None and id(resource) in borrowed_res:
                session.release_borrow(resource)

    def own(self, resource: Any, releaser: Any = None) -> Any:
        """Register ownership of a buffer/resource with the underlying BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "own") and resource is not None:
            return session.own(resource, releaser=releaser)
        return resource

    def acquire_buffer(
        self,
        shape: tuple[int, ...],
        dtype: Any = None,
        is_vector: bool = False,
        vector_dim: int = 1,
    ) -> Any:
        """Acquire a reusable scratch buffer from the underlying BufferSession cache."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "acquire_buffer"):
            kwargs = {"dtype": dtype} if dtype is not None else {}
            return session.acquire_buffer(
                shape, is_vector=is_vector, vector_dim=vector_dim, **kwargs
            )
        raise RuntimeError("Current PipelineRuntime session does not provide a buffer allocator")

    def acquire_ring_buffer(
        self,
        name: str,
        shape: tuple[int, ...],
        depth: int = 4,
        dtype: Any = None,
        is_vector: bool = False,
        vector_dim: int = 1,
    ) -> Any:
        """Acquire or advance a ring buffer slot from the underlying BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "acquire_ring_buffer"):
            kwargs = {"dtype": dtype} if dtype is not None else {}
            return session.acquire_ring_buffer(
                name, shape, depth=depth, is_vector=is_vector, vector_dim=vector_dim, **kwargs
            )
        raise RuntimeError("Current PipelineRuntime session does not provide a ring buffer allocator")

    def upload_if_needed(
        self, array: Any, is_vector: bool = False, vector_dim: int = 1
    ) -> tuple[Any, bool]:
        """Upload a host array or view existing GPU buffer via BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "upload_if_needed"):
            return session.upload_if_needed(array, is_vector=is_vector, vector_dim=vector_dim)
        return array, False

    def get_or_create_grayscale(self, frame: Any, is_vector: bool = False) -> Any:
        """Get or compute cached grayscale representation in BufferSession."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "get_or_create_grayscale"):
            return session.get_or_create_grayscale(frame, is_vector=is_vector)
        return frame

    @property
    def managed_api(self) -> Any:
        """Access BufferSession's managed AOT API facade if available."""
        session = self.ensure_session()
        if session is not None and hasattr(session, "managed_api"):
            return session.managed_api
        return None

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

    def iter_prepared_supports(
        self,
        indices: Iterable[int],
        loader: Callable[[int], Any],
        prepare: Callable[[int, Any], Any],
        *,
        stop_when: Callable[[], bool] | None = None,
        raise_on_cancel: bool = False,
        source_disposer: Callable[[Any], None] | None = None,
        prepared_disposer: Callable[[Any], None] | None = None,
    ) -> Iterator[tuple[int, Any]]:
        """Prepare bounded host frames ahead while the consumer uses its current item.

        The in-processing limit includes the currently yielded item and frames
        being loaded/prepared. The loader's separate RAM queue continues to be
        bounded by ``prefetch_depth``. Preparation stays on a host worker; this
        API does not make GPU kernel execution concurrent.
        """
        yield from self._iter_prepared_supports(
            indices,
            loader,
            prepare,
            stop_when=stop_when,
            raise_on_cancel=raise_on_cancel,
            source_disposer=source_disposer,
            prepared_disposer=prepared_disposer,
            transfer_ownership=False,
        )

    def _iter_prepared_supports(
        self,
        indices: Iterable[int],
        loader: Callable[[int], Any],
        prepare: Callable[[int, Any], Any],
        *,
        stop_when: Callable[[], bool] | None = None,
        raise_on_cancel: bool = False,
        source_disposer: Callable[[Any], None] | None = None,
        prepared_disposer: Callable[[Any], None] | None = None,
        transfer_ownership: bool,
    ) -> Iterator[tuple[int, Any]]:
        """Shared prepared stream with optional explicit support ownership."""
        if self._closed:
            raise RuntimeError("PipelineRuntime is closed")

        def own_prepared(value):
            session = self._session
            if session is not None and hasattr(session, "own"):
                session.own(value, releaser=prepared_disposer)
                return value, session.release_buffer
            return value, prepared_disposer

        if self.in_processing_depth <= 1:
            source_stream = iter(self.iter_supports(
                indices,
                loader,
                stop_when=stop_when,
                raise_on_cancel=raise_on_cancel,
                disposer=source_disposer,
            ))
            try:
                while True:
                    lease = self.acquire_in_processing_slot(stop_when=stop_when)
                    if lease is None:
                        if raise_on_cancel and _event_is_set(self.stop_event):
                            raise PipelineCancelledError(
                                "Pipeline in-processing queue cancelled"
                            )
                        break
                    try:
                        index, source = next(source_stream)
                    except StopIteration:
                        lease.release()
                        break
                    except BaseException:
                        lease.release()
                        raise

                    prepared = None
                    release = None
                    try:
                        prepared = prepare(index, source)
                        prepared, release = own_prepared(prepared)
                        if transfer_ownership:
                            support_lease = PipelineSupportLease(
                                index,
                                prepared,
                                release or prepared_disposer,
                                lease,
                                retain_value=(release or prepared_disposer) is not None,
                                session=self._session,
                            )
                            yielded_item = (index, prepared, support_lease)
                            prepared = None
                            lease = None
                            yield yielded_item
                            yielded_item = None
                        else:
                            yield index, prepared
                    finally:
                        if prepared is not None:
                            _dispose(prepared, release or prepared_disposer)
                        if lease is not None:
                            lease.release()
            finally:
                try:
                    source_stream.close()
                except Exception:
                    pass
            return

        output: queue.Queue[Any] = queue.Queue(maxsize=self.in_processing_depth)
        local_stop = threading.Event()

        def stopped() -> bool:
            if local_stop.is_set() or self.worker_stop_requested:
                return True
            if _event_is_set(self.stop_event):
                return True
            if stop_when is not None:
                try:
                    return bool(stop_when())
                except Exception:
                    return True
            return False

        def put(item: Any) -> bool:
            while not local_stop.is_set() and not self.worker_stop_requested:
                try:
                    output.put(item, timeout=0.05)
                    return True
                except queue.Full:
                    continue
            return False

        def produce() -> None:
            source_stream = self.iter_supports(
                indices,
                loader,
                stop_when=lambda: local_stop.is_set()
                or self.worker_stop_requested
                or (stop_when is not None and stop_when()),
                raise_on_cancel=raise_on_cancel,
                disposer=source_disposer,
            )
            concurrency = max(1, min(self.in_processing_depth, os.cpu_count() or 4))
            executor = (
                ThreadPoolExecutor(
                    max_workers=concurrency,
                    thread_name_prefix="PipelineDecodeWorker",
                )
                if concurrency > 1
                else None
            )
            pending_futures: deque[tuple[int, Any, Any]] = deque()
            source_exhausted = False
            try:
                if executor is None:
                    while not stopped():
                        lease = self.acquire_in_processing_slot(stop_when=stopped)
                        if lease is None:
                            break
                        try:
                            index, source = next(source_stream)
                        except StopIteration:
                            lease.release()
                            break
                        except BaseException:
                            lease.release()
                            raise

                        prepared = None
                        release = None
                        try:
                            prepared = prepare(index, source)
                            prepared, release = own_prepared(prepared)
                            if not put(_Loaded(index, (prepared, release, lease))):
                                _dispose(prepared, release or prepared_disposer)
                                lease.release()
                                break
                            prepared = None  # Ownership moves to the consumer queue.
                            lease = None
                        except BaseException as exc:
                            if prepared is not None:
                                _dispose(prepared, release or prepared_disposer)
                            if lease is not None:
                                lease.release()
                            if not stopped():
                                put(_Failed(exc))
                            break
                else:
                    def _decode_task(idx, src, lse):
                        prep = None
                        rel = None
                        try:
                            prep = prepare(idx, src)
                            prep, rel = own_prepared(prep)
                            return idx, prep, rel, lse
                        except BaseException:
                            if prep is not None:
                                _dispose(prep, rel or prepared_disposer)
                            lse.release()
                            raise
                        finally:
                            self.release_borrow(src)

                    while not stopped():
                        # Fill pending futures up to in_processing_depth
                        while (
                            not stopped()
                            and not source_exhausted
                            and len(pending_futures) < self.in_processing_depth
                        ):
                            slot_timeout = None if not pending_futures else 0.0
                            lease = self.acquire_in_processing_slot(
                                stop_when=stopped, timeout=slot_timeout
                            )
                            if lease is None:
                                break
                            try:
                                index, source = next(source_stream)
                            except StopIteration:
                                source_exhausted = True
                                lease.release()
                                break
                            except BaseException:
                                lease.release()
                                raise

                            self.borrow(source)
                            fut = executor.submit(_decode_task, index, source, lease)
                            pending_futures.append((index, fut, lease, source))

                        if not pending_futures:
                            if source_exhausted:
                                break
                            continue

                        # Await and yield the next future in strict ordinal order
                        item_index, fut, lse, item_source = pending_futures[0]
                        res = None
                        while not stopped():
                            try:
                                res = fut.result(timeout=0.05)
                                break
                            except FutureTimeoutError:
                                continue
                            except BaseException as exc:
                                if not stopped():
                                    put(_Failed(exc))
                                res = None
                                break

                        if stopped() or res is None:
                            break

                        pending_futures.popleft()
                        idx, prep, rel, item_lease = res
                        if not put(_Loaded(idx, (prep, rel, item_lease))):
                            _dispose(prep, rel or prepared_disposer)
                            item_lease.release()
                            break
            except BaseException as exc:
                if not stopped():
                    put(_Failed(exc))
            finally:
                if executor is not None:
                    for _, fut, lse, src_item in pending_futures:
                        if fut.cancel():
                            lse.release()
                            self.release_borrow(src_item)
                    executor.shutdown(wait=True)
                    for _, fut, lse, src_item in pending_futures:
                        if fut.done() and not fut.cancelled():
                            try:
                                exc = fut.exception()
                                if exc is None:
                                    _, prep, rel, item_lease = fut.result()
                                    _dispose(prep, rel or prepared_disposer)
                                    item_lease.release()
                            except Exception:
                                pass
                    pending_futures.clear()
                try:
                    source_stream.close()
                except Exception:
                    pass
                put(_DONE)

        worker = self.start_worker(target=produce, name="PipelineInProcessing")
        try:
            while True:
                if stopped():
                    if raise_on_cancel and _event_is_set(self.stop_event):
                        raise PipelineCancelledError(
                            "Pipeline in-processing queue cancelled"
                        )
                    break
                try:
                    item = output.get(timeout=0.05)
                except queue.Empty:
                    if not worker.is_alive():
                        break
                    continue
                if item is _DONE:
                    break
                if isinstance(item, _Failed):
                    raise item.error
                assert isinstance(item, _Loaded)
                prepared, release, lease = item.value
                if transfer_ownership:
                    support_lease = PipelineSupportLease(
                        item.index,
                        prepared,
                        release or prepared_disposer,
                        lease,
                        retain_value=(release or prepared_disposer) is not None,
                        session=self._session,
                    )
                    yielded_item = (item.index, prepared, support_lease)
                    prepared = None
                    lease = None
                    yield yielded_item
                    yielded_item = None
                else:
                    try:
                        yield item.index, prepared
                    finally:
                        _dispose(prepared, release or prepared_disposer)
                        lease.release()
        finally:
            local_stop.set()
            if worker is not threading.current_thread():
                worker.join()
            while True:
                try:
                    item = output.get_nowait()
                except queue.Empty:
                    break
                if isinstance(item, _Loaded):
                    prepared, release, lease = item.value
                    _dispose(prepared, release or prepared_disposer)
                    lease.release()

    def iter_admitted_supports(
        self,
        indices: Iterable[int],
        loader: Callable[[int], Any],
        prepare: Callable[[int, Any], Any],
        *,
        stop_when: Callable[[], bool] | None = None,
        raise_on_cancel: bool = False,
        source_disposer: Callable[[Any], None] | None = None,
        prepared_disposer: Callable[[Any], None] | None = None,
    ) -> Iterator[tuple[int, Any, PipelineSupportLease]]:
        """Yield prepared supports with explicit ownership through the last stage.

        The consumer must release each returned lease only after every queued
        stage that uses its support has completed. Loading may prefetch, while
        preparation remains on the consuming stage thread.
        """
        source_stream = iter(
            self.iter_supports(
                indices,
                loader,
                stop_when=stop_when,
                raise_on_cancel=raise_on_cancel,
                disposer=source_disposer,
            )
        )
        try:
            while True:
                lease = self.acquire_in_processing_slot(stop_when=stop_when)
                if lease is None:
                    if raise_on_cancel and _event_is_set(self.stop_event):
                        raise PipelineCancelledError(
                            "Pipeline in-processing queue cancelled"
                        )
                    break
                try:
                    index, source = next(source_stream)
                except StopIteration:
                    lease.release()
                    break
                except BaseException:
                    lease.release()
                    raise

                prepared = None
                try:
                    prepared = prepare(index, source)
                    support_lease = PipelineSupportLease(
                        index,
                        prepared,
                        prepared_disposer,
                        lease,
                        retain_value=prepared_disposer is not None,
                        session=self._session,
                    )
                    yielded_item = (index, prepared, support_lease)
                    prepared = None
                    lease = None
                    yield yielded_item
                    yielded_item = None
                finally:
                    if prepared is not None:
                        _dispose(prepared, prepared_disposer)
                    if lease is not None:
                        lease.release()
        finally:
            try:
                source_stream.close()
            except Exception:
                pass

    def _execute_prepared_supports(
        self,
        source: PipelineSource,
        recipe: PipelineRecipe,
        support_indices: Iterable[int],
        reference_state: Any,
        context: PipelineExecutionContext,
        prepare_support: Callable[..., Any],
        release_support: Callable[..., Any],
    ) -> None:
        """Run a recipe whose support lifetime may extend past submission."""

        def prepare(index: int, support: Any) -> Any:
            context.check_cancelled()
            return prepare_support(index, support, reference_state, context)

        support_stream = self._iter_prepared_supports(
            support_indices,
            source.load_support,
            prepare,
            raise_on_cancel=True,
            prepared_disposer=lambda support: release_support(
                support, reference_state, context
            ),
            transfer_ownership=True,
        )
        pending: deque[
            tuple[PipelineSupportCompletion, PipelineSupportLease]
        ] = deque()

        def finish_oldest() -> None:
            completion, support_lease = pending.popleft()
            try:
                completion.result()
            finally:
                support_lease.release()

        try:
            for index, _support, support_lease in support_stream:
                completion_pending = False
                try:
                    context.check_cancelled()
                    completion = recipe.process_support(
                        index,
                        support_lease.value,
                        reference_state,
                        context,
                    )
                    if completion is None:
                        support_lease.release()
                        continue
                    wait_for_result = getattr(completion, "result", None)
                    if not callable(wait_for_result):
                        raise TypeError(
                            "process_support() must return None or a "
                            "completion with result()"
                        )
                    pending.append((completion, support_lease))
                    completion_pending = True
                    if len(pending) >= self.in_processing_depth:
                        finish_oldest()
                except BaseException:
                    if not completion_pending:
                        support_lease.release()
                    raise

            while pending:
                finish_oldest()
        except BaseException:
            while pending:
                try:
                    finish_oldest()
                except BaseException:
                    pass
            raise
        finally:
            support_stream.close()

    def _execute_legacy_supports(
        self,
        source: PipelineSource,
        recipe: PipelineRecipe,
        support_indices: Iterable[int],
        reference_state: Any,
        context: PipelineExecutionContext,
    ) -> None:
        """Run the original synchronous recipe contract."""
        support_stream = self.iter_supports(
            support_indices,
            source.load_support,
            raise_on_cancel=True,
        )
        for index, support in support_stream:
            context.check_cancelled()
            recipe.process_support(index, support, reference_state, context)

    def execute(
        self,
        source: PipelineSource,
        recipe: PipelineRecipe,
        support_indices: Iterable[int],
        *,
        options: Mapping[str, Any] | None = None,
        source_descriptor: PipelineSourceDescriptor | None = None,
        engine: Any = None,
        own_reference: bool = True,
    ) -> Any:
        """Run the common reference → ordered supports → finalize lifecycle.

        Set ``own_reference=False`` when the source or caller retains ownership
        of its reference payload beyond this execution.
        """
        try:
            session = self.ensure_session(engine)
            context = PipelineExecutionContext(
                session=session,
                options=PipelineOptions(
                    prefetch_depth=self.prefetch_depth,
                    in_processing_depth=self.in_processing_depth,
                    values=dict(options or {}),
                ),
                stop_event=self.stop_event,
                progress_callback=self.progress_callback,
                source_descriptor=(
                    source_descriptor
                    if source_descriptor is not None
                    else getattr(source, "descriptor", self.source_descriptor)
                ),
            )
            context.check_cancelled()
            reference = source.load_reference()
            if own_reference and reference is not None and hasattr(session, "own"):
                session.own(reference)
            with self.borrowed(reference):
                reference_state = recipe.prepare_reference(reference, context)
                with self.borrowed(reference_state):
                    prepare_support = getattr(recipe, "prepare_support", None)
                    release_support = getattr(recipe, "release_support", None)
                    if callable(prepare_support) != callable(release_support):
                        raise TypeError(
                            "PreparedPipelineRecipe must implement both "
                            "prepare_support() and release_support()"
                        )

                    if callable(prepare_support):
                        self._execute_prepared_supports(
                            source,
                            recipe,
                            support_indices,
                            reference_state,
                            context,
                            prepare_support,
                            release_support,
                        )
                    else:
                        self._execute_legacy_supports(
                            source,
                            recipe,
                            support_indices,
                            reference_state,
                            context,
                        )
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
            in_processing_depth=resolve_in_processing_depth(),
            stop_event=bound.arguments.get("stop_event"),
            progress_callback=bound.arguments.get("progress_callback"),
            source_descriptor=bound.arguments.get("source_descriptor"),
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
    "IN_PROCESSING_MAX",
    "IN_PROCESSING_MIN",
    "IN_PROCESSING_SETTING_KEY",
    "PREFETCH_MAX",
    "PREFETCH_MIN",
    "PREFETCH_SETTING_KEY",
    "InProcessingLease",
    "PipelineRuntime",
    "PipelineSupportLease",
    "current_pipeline_runtime",
    "normalize_prefetch_depth",
    "normalize_in_processing_depth",
    "resolve_in_processing_depth",
    "resolve_prefetch_depth",
    "runtime_entrypoint",
]
