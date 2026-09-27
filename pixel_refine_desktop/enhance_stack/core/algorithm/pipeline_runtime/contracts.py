"""Backend-neutral contracts for frame-streaming algorithm pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Protocol, TypeVar


TReference = TypeVar("TReference")
TFrame = TypeVar("TFrame")
TState = TypeVar("TState")
TResult = TypeVar("TResult")


class PipelineCancelledError(RuntimeError):
    """Raised when a recipe execution is explicitly cancelled."""


@dataclass(frozen=True)
class PipelineOptions:
    """Execution settings shared by algorithms without imposing their schema."""

    prefetch_depth: int = 0
    values: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class PipelineExecutionContext:
    """Per-job services passed to a domain recipe."""

    session: Any
    options: PipelineOptions
    stop_event: Any = None
    progress_callback: Callable[..., None] | None = None

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


__all__ = [
    "PipelineCancelledError",
    "PipelineExecutionContext",
    "PipelineOptions",
    "PipelineRecipe",
    "PipelineSource",
]
