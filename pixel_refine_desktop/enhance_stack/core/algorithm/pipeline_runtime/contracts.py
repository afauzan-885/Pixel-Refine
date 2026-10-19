"""Backend-neutral contracts for frame-streaming algorithm pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Protocol, TypeVar


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


@dataclass
class PipelineExecutionContext:
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
