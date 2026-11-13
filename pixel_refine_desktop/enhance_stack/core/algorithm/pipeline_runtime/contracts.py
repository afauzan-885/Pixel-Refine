"""Backend-neutral contracts for frame-streaming algorithm pipelines."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol, TypeVar


TReference = TypeVar("TReference")
TFrame = TypeVar("TFrame")
TState = TypeVar("TState")
TResult = TypeVar("TResult")
TSourceFrame = TypeVar("TSourceFrame")
TPreparedFrame = TypeVar("TPreparedFrame")


@dataclass(frozen=True)
class PipelineSourceDescriptor:
    """Opaque input classification forwarded unchanged to a domain recipe."""

    kind: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


class PipelineCancelledError(RuntimeError):
    """Raised when a recipe execution is explicitly cancelled."""


@dataclass(frozen=True)
class PipelineOptions:
    """Execution settings shared by algorithms without imposing their schema."""

    prefetch_depth: int = 0
    in_processing_depth: int = 1
    values: Mapping[str, Any] = field(default_factory=dict)


class _BufferSessionFacade:
    """Shared lifecycle facade for contexts and their owning runtime."""

    def _buffer_session(self) -> Any:
        ensure_session = getattr(self, "ensure_session", None)
        if callable(ensure_session):
            return ensure_session()
        return self.session

    @contextmanager
    def borrowed(self, resource: Any, *, from_session: Any = None):
        """Scope a borrow lease while the resource is pinned."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "borrow") and resource is not None:
            with session.borrow(resource, from_session=from_session) as value:
                yield value
            return
        yield resource

    def borrow(self, resource: Any, *, from_session: Any = None) -> Any:
        """Pin a resource and return its lease."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "borrow") and resource is not None:
            lease = session.borrow(resource, from_session=from_session)
            active = getattr(self, "_active_source_borrows", None)
            if active is not None and lease is not None:
                active[id(resource)] = lease
            return lease
        return resource

    def release_borrow(self, resource: Any) -> None:
        """Release a borrow lease recorded by the underlying session."""
        active = getattr(self, "_active_source_borrows", None)
        lease = None
        if active is not None and resource is not None:
            lease = active.pop(id(resource), None)
        if lease is not None and hasattr(lease, "release"):
            lease.release()
            return
        session = self._buffer_session()
        if session is not None and hasattr(session, "borrow") and resource is not None:
            with session.borrow(resource):
                pass

    def own(self, resource: Any, releaser: Any = None) -> Any:
        """Return a resident resource through the three-API session surface."""
        session = self._buffer_session()
        if (
            session is not None
            and hasattr(session, "view")
            and resource is not None
            and hasattr(resource, "handle")
        ):
            return session.view(resource)
        return resource

    def acquire_buffer(
        self,
        shape: tuple[int, ...],
        dtype: Any = None,
        is_vector: bool = False,
        vector_dim: int = 1,
    ) -> Any:
        """Acquire a reusable scratch buffer from the session cache."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "acquire_buffer"):
            kwargs = {"dtype": dtype} if dtype is not None else {}
            return session.view(
                shape, is_vector=is_vector, vector_dim=vector_dim, **kwargs
            )
        raise RuntimeError("Current pipeline session does not provide a buffer allocator")

    def acquire_ring_buffer(
        self,
        name: str,
        shape: tuple[int, ...],
        depth: int = 4,
        dtype: Any = None,
        is_vector: bool = False,
        vector_dim: int = 1,
    ) -> Any:
        """Acquire or advance a ring buffer slot from the underlying session."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "acquire_ring_buffer"):
            kwargs = {"dtype": dtype} if dtype is not None else {}
            return session.acquire_ring_buffer(
                name, shape, depth=depth, is_vector=is_vector, vector_dim=vector_dim, **kwargs
            )
        raise RuntimeError("Current pipeline session does not provide a ring buffer allocator")

    def upload_if_needed(
        self, array: Any, is_vector: bool = False, vector_dim: int = 1
    ) -> tuple[Any, bool]:
        """Upload a host array or view an existing GPU buffer via the session."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "upload_if_needed"):
            buffer = session.view(array, is_vector=is_vector, vector_dim=vector_dim)
            return buffer, False
        return array, False

    def view(self, source: Any = None, **kwargs: Any) -> Any:
        """Get a resident handle without copying an existing buffer."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "view"):
            return session.view(source, **kwargs)
        return source

    def release(self, resource: Any = None, **kwargs: Any) -> Any:
        """Release or transfer ownership through the underlying session."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "release"):
            return session.release(resource, **kwargs)
        return resource

    @property
    def managed_api(self) -> Any:
        """Access the session's managed AOT API facade if available."""
        session = self._buffer_session()
        if session is not None and hasattr(session, "managed_api"):
            return session.managed_api
        return None


@dataclass
class PipelineExecutionContext(_BufferSessionFacade):
    """Per-job services passed to a domain recipe."""

    session: Any
    options: PipelineOptions
    stop_event: Any = None
    progress_callback: Callable[..., None] | None = None
    source_descriptor: PipelineSourceDescriptor | None = None

    def is_cancelled(self) -> bool:
        event = self.stop_event
        if event is None:
            return False
        if hasattr(event, "is_set"):
            return bool(event.is_set())
        if callable(event):
            return bool(event())
        return bool(event)

    def check_cancelled(self) -> None:
        if self.is_cancelled():
            raise PipelineCancelledError("Pipeline execution cancelled")

    def report(self, *args: Any, **kwargs: Any) -> None:
        if self.progress_callback is not None:
            self.progress_callback(*args, **kwargs)


class PipelineSource(Protocol[TReference, TFrame]):
    """Lazy source of one reference and indexed support frames."""

    descriptor: PipelineSourceDescriptor | None

    def load_reference(self) -> TReference:
        ...

    def load_support(self, index: int) -> TFrame:
        ...


class PipelineRecipe(Protocol[TReference, TFrame, TState, TResult]):
    """Domain-specific operations executed by the generic frame runtime."""

    def prepare_reference(
        self, reference: TReference, context: PipelineExecutionContext
    ) -> TState:
        ...

    def process_support(
        self,
        index: int,
        support: TFrame,
        reference_state: TState,
        context: PipelineExecutionContext,
    ) -> None:
        ...

    def finalize(
        self, reference_state: TState, context: PipelineExecutionContext
    ) -> TResult:
        ...


class PreparedPipelineRecipe(
    Protocol[TReference, TSourceFrame, TPreparedFrame, TState, TResult]
):
    """Optional recipe contract for bounded support preparation and cleanup."""

    def prepare_reference(
        self, reference: TReference, context: PipelineExecutionContext
    ) -> TState:
        ...

    def prepare_support(
        self,
        index: int,
        support: TSourceFrame,
        reference_state: TState,
        context: PipelineExecutionContext,
    ) -> TPreparedFrame:
        ...

    def process_support(
        self,
        index: int,
        support: TPreparedFrame,
        reference_state: TState,
        context: PipelineExecutionContext,
    ) -> PipelineSupportCompletion | None:
        ...

    def release_support(
        self,
        support: TPreparedFrame,
        reference_state: TState,
        context: PipelineExecutionContext,
    ) -> None:
        ...

    def finalize(
        self, reference_state: TState, context: PipelineExecutionContext
    ) -> TResult:
        ...


class PipelineSupportCompletion(Protocol):
    """Completion token for support work submitted to a staged pipeline."""

    def result(self) -> Any:
        """Wait for all consumers to finish and raise any stage failure."""
        ...


__all__ = [
    "PipelineCancelledError",
    "PipelineExecutionContext",
    "PipelineOptions",
    "PipelineSourceDescriptor",
    "PipelineRecipe",
    "PipelineSupportCompletion",
    "PreparedPipelineRecipe",
    "PipelineSource",
]
