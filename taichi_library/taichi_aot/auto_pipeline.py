"""Backend-neutral automatic pipeline planning.

The planner is intentionally side-effect free.  It decides whether a list of
graph dispatches can share one recorded pipeline, must be segmented, or is
cheaper/safer as direct dispatches.  Execution remains in ``engine.py`` and
the existing C++ bridge, so this layer can be validated independently before
wrapping every public algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional


@dataclass(frozen=True)
class GraphSpec:
    """Static resource summary for one graph dispatch."""

    name: str
    resident_bytes: int = 0
    reads: tuple[str, ...] = ()
    writes: tuple[str, ...] = ()
    backend_safe: bool = True
    force_boundary: bool = False
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValueError("graph name must be non-empty")
        if int(self.resident_bytes) < 0:
            raise ValueError("resident_bytes must be non-negative")
        object.__setattr__(self, "resident_bytes", int(self.resident_bytes))
        object.__setattr__(self, "reads", tuple(str(item) for item in self.reads))
        object.__setattr__(self, "writes", tuple(str(item) for item in self.writes))


@dataclass(frozen=True)
class PipelinePlan:
    """Decision returned by :class:`AutoPipelinePlanner`."""

    mode: str
    segments: tuple[tuple[GraphSpec, ...], ...]
    resident_bytes: int
    resident_limit: int
    backend: str
    reason: str
    max_concurrency: int = 1

    @property
    def graph_count(self) -> int:
        return sum(len(segment) for segment in self.segments)

    @property
    def is_recorded(self) -> bool:
        return self.mode == "recorded"

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "segments": [[graph.name for graph in segment] for segment in self.segments],
            "resident_bytes": self.resident_bytes,
            "resident_limit": self.resident_limit,
            "backend": self.backend,
            "reason": self.reason,
            "max_concurrency": self.max_concurrency,
        }


def _coerce_spec(value: GraphSpec | Mapping[str, Any] | str) -> GraphSpec:
    if isinstance(value, GraphSpec):
        return value
    if isinstance(value, str):
        return GraphSpec(value)
    if isinstance(value, Mapping):
        return GraphSpec(**value)
    raise TypeError("graphs must contain GraphSpec, mapping, or graph-name values")


class AutoPipelinePlanner:
    """Choose a safe pipeline shape from runtime memory/capability telemetry."""

    def __init__(
        self,
        backend: str = "cpu",
        memory_provider: Optional[Callable[[], Mapping[str, Any]]] = None,
        *,
        minimum_recorded_graphs: int = 2,
        unsafe_backends: Iterable[str] = (),
    ) -> None:
        self.backend = str(backend or "cpu").lower()
        self.memory_provider = memory_provider
        self.minimum_recorded_graphs = max(2, int(minimum_recorded_graphs))
        self.unsafe_backends = {str(item).lower() for item in unsafe_backends}

    def _limits(self) -> tuple[int, int]:
        telemetry: Mapping[str, Any] = {}
        if self.memory_provider is not None:
            try:
                candidate = self.memory_provider()
                if isinstance(candidate, Mapping):
                    telemetry = candidate
            except Exception:
                telemetry = {}
        limit = int(telemetry.get("pipeline_resident_limit", 0) or 0)
        concurrency = int(telemetry.get("max_concurrency", 1) or 1)
        return max(0, limit), max(1, concurrency)

    @staticmethod
    def _can_merge(previous: GraphSpec, current: GraphSpec) -> bool:
        if previous.force_boundary or current.force_boundary:
            return False
        # A write/read or write/write hazard is fine inside a recorded graph;
        # a graph with an explicit resource boundary is not.  The planner
        # leaves detailed barrier synthesis to the backend runtime.
        return previous.backend_safe and current.backend_safe

    def plan(self, graphs: Iterable[GraphSpec | Mapping[str, Any] | str]) -> PipelinePlan:
        specs = tuple(_coerce_spec(value) for value in graphs)
        limit, concurrency = self._limits()
        total = sum(spec.resident_bytes for spec in specs)
        backend_unsafe = self.backend in self.unsafe_backends

        if not specs:
            return PipelinePlan("direct", (), 0, limit, self.backend, "empty graph list", concurrency)
        if len(specs) < self.minimum_recorded_graphs:
            return PipelinePlan(
                "direct", (specs,), total, limit, self.backend,
                "single graph has no recording amortization", concurrency,
            )
        if backend_unsafe or any(not spec.backend_safe for spec in specs):
            return PipelinePlan(
                "segmented", tuple((spec,) for spec in specs), total, limit, self.backend,
                "backend or graph capability requires direct boundaries", concurrency,
            )
        if limit <= 0:
            return PipelinePlan(
                "segmented", tuple((spec,) for spec in specs), total, limit, self.backend,
                "no resident-memory budget is available", concurrency,
            )
        if total <= limit and all(self._can_merge(specs[i - 1], specs[i]) for i in range(1, len(specs))):
            return PipelinePlan(
                "recorded", (specs,), total, limit, self.backend,
                "all graphs fit the adaptive resident-memory limit", concurrency,
            )

        # Greedy segmentation keeps graph order and never creates a segment
        # larger than the current resident budget.  A single oversized graph
        # remains a one-item segment so the executor can choose its own
        # streaming/full-frame policy rather than silently overcommitting.
        segments: list[tuple[GraphSpec, ...]] = []
        current: list[GraphSpec] = []
        current_bytes = 0
        for spec in specs:
            would_overflow = current and current_bytes + spec.resident_bytes > limit
            if would_overflow or (current and not self._can_merge(current[-1], spec)):
                segments.append(tuple(current))
                current = []
                current_bytes = 0
            current.append(spec)
            current_bytes += spec.resident_bytes
        if current:
            segments.append(tuple(current))
        return PipelinePlan(
            "segmented", tuple(segments), total, limit, self.backend,
            "graphs exceed the adaptive resident-memory limit or contain boundaries", concurrency,
        )

