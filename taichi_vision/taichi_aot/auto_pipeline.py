"""Backend-neutral automatic pipeline planning.

The planner is intentionally side-effect free.  It decides whether a list of
graph dispatches can share one recorded pipeline, must be segmented, or is
cheaper/safer as direct dispatches.  Execution remains in ``engine.py`` and
the existing C++ bridge, so this layer can be validated independently before
wrapping every public algorithm.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field, fields, is_dataclass
from math import isfinite
from threading import RLock
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence


class EWMA:
    """Small thread-safe exponentially weighted moving average.

    EWMA is deliberately backend-neutral: values are observations supplied by
    the caller, never measurements inferred from a device queue.  Invalid or
    non-finite samples are ignored so one malformed telemetry record cannot
    make the planner select an aggressive configuration.
    """

    def __init__(self, alpha: float = 0.2, value: Optional[float] = None) -> None:
        alpha = float(alpha)
        if not 0.0 < alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.value = None if value is None else float(value)
        self.samples = 0 if value is None else 1
        self._lock = RLock()

    @property
    def initialized(self) -> bool:
        with self._lock:
            return self.value is not None and self.samples > 0

    def update(self, sample: Any) -> Optional[float]:
        try:
            sample_value = float(sample)
        except (TypeError, ValueError):
            return self.value
        if not isfinite(sample_value):
            return self.value
        with self._lock:
            if self.value is None:
                self.value = sample_value
            else:
                self.value = self.alpha * sample_value + (1.0 - self.alpha) * self.value
            self.samples += 1
            return self.value

    observe = update

    def reset(self) -> None:
        with self._lock:
            self.value = None
            self.samples = 0

    def snapshot(self) -> Optional[float]:
        with self._lock:
            return None if self.value is None else float(self.value)

    def as_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                "value": None if self.value is None else float(self.value),
                "samples": int(self.samples),
                "alpha": float(self.alpha),
            }


def _pressure_value(value: Any) -> Optional[float]:
    """Map memory pressure labels to a conservative [0, 1] severity."""
    if isinstance(value, str):
        levels = {
            "healthy": 0.0,
            "normal": 0.0,
            "low": 0.25,
            "warning": 0.55,
            "elevated": 0.65,
            "high": 0.75,
            "critical": 0.9,
            "emergency": 1.0,
        }
        value = levels.get(value.lower().strip())
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(value):
        return None
    return max(0.0, min(1.0, value))


class PlannerTelemetry:
    """EWMA telemetry used by pipeline planning/autotuning (P4).

    Metrics are intentionally host-side observations.  In particular,
    ``max_concurrency`` and ``pipeline_depth`` are planning hints only; this
    class never claims that queue submissions overlap on a GPU.
    """

    _ALIASES = {
        "latency": "latency_ms",
        "latency_s": "latency_ms",
        "transfer": "transfer_bytes",
        "bytes_transferred": "transfer_bytes",
        "peak_resident": "peak_resident_bytes",
        "resident_bytes": "peak_resident_bytes",
        "hit_rate": "cache_hit_rate",
    }

    def __init__(self, alpha: float = 0.2) -> None:
        self.alpha = float(alpha)
        if not 0.0 < self.alpha <= 1.0:
            raise ValueError("alpha must be in (0, 1]")
        self.latency_ms = EWMA(self.alpha)
        self.transfer_bytes = EWMA(self.alpha)
        self.peak_resident_bytes = EWMA(self.alpha)
        self.cache_hit_rate = EWMA(self.alpha)
        self.pressure = EWMA(self.alpha)
        self.samples = 0
        self._lock = RLock()

    @property
    def sample_count(self) -> int:
        return int(self.samples)

    def observe(
        self,
        telemetry: Optional[Mapping[str, Any]] = None,
        *,
        latency_ms: Any = None,
        transfer_bytes: Any = None,
        peak_resident_bytes: Any = None,
        cache_hit_rate: Any = None,
        pressure: Any = None,
        **extra: Any,
    ) -> "PlannerTelemetry":
        values = dict(telemetry or {})
        values.update(extra)
        explicit = {
            "latency_ms": latency_ms,
            "transfer_bytes": transfer_bytes,
            "peak_resident_bytes": peak_resident_bytes,
            "cache_hit_rate": cache_hit_rate,
            "pressure": pressure,
        }
        for key, value in explicit.items():
            if value is not None:
                values[key] = value
        normalized = {}
        for key, value in values.items():
            normalized[self._ALIASES.get(str(key), str(key))] = value
        updated = False
        with self._lock:
            for key, metric in (
                ("latency_ms", self.latency_ms),
                ("transfer_bytes", self.transfer_bytes),
                ("peak_resident_bytes", self.peak_resident_bytes),
                ("cache_hit_rate", self.cache_hit_rate),
            ):
                if key in normalized and metric.update(normalized[key]) is not None:
                    updated = True
            if "cache_hits" in normalized or "cache_misses" in normalized:
                hits = normalized.get("cache_hits")
                misses = normalized.get("cache_misses")
                try:
                    total = float(hits or 0) + float(misses or 0)
                    if total > 0:
                        self.cache_hit_rate.update(float(hits or 0) / total)
                        updated = True
                except (TypeError, ValueError):
                    pass
            if "pressure" in normalized:
                pressure_value = _pressure_value(normalized["pressure"])
                if pressure_value is not None and self.pressure.update(pressure_value) is not None:
                    updated = True
            if updated:
                self.samples += 1
        return self

    record = observe

    def reset(self) -> None:
        with self._lock:
            for metric in (
                self.latency_ms,
                self.transfer_bytes,
                self.peak_resident_bytes,
                self.cache_hit_rate,
                self.pressure,
            ):
                metric.reset()
            self.samples = 0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            pressure = self.pressure.snapshot()
            return {
                "latency_ms": self.latency_ms.snapshot(),
                "transfer_bytes": self.transfer_bytes.snapshot(),
                "peak_resident_bytes": self.peak_resident_bytes.snapshot(),
                "cache_hit_rate": self.cache_hit_rate.snapshot(),
                "pressure": pressure,
                "samples": int(self.samples),
                "ewma_alpha": float(self.alpha),
            }

    as_dict = snapshot


PipelineTelemetry = PlannerTelemetry
EWMATelemetry = PlannerTelemetry


@dataclass(frozen=True)
class AutoTuneConfig:
    """Conservative candidate bounds for EWMA autotuning."""

    default_block_size: int = 512
    min_block_size: int = 128
    max_block_size: int = 2048
    block_candidates: tuple[int, ...] = ()
    min_pipeline_depth: int = 1
    max_pipeline_depth: int = 2
    warmup_samples: int = 3
    pressure_reduce_at: float = 0.70
    pressure_critical_at: float = 0.85
    cache_hit_increase_at: float = 0.80

    def __post_init__(self) -> None:
        minimum = max(1, int(self.min_block_size))
        maximum = max(minimum, int(self.max_block_size))
        default = min(maximum, max(minimum, int(self.default_block_size)))
        candidates = tuple(sorted({
            max(minimum, min(maximum, int(item)))
            for item in (self.block_candidates or ())
        }))
        if not candidates:
            candidates = tuple(
                item for item in (128, 256, 512, 1024, 2048)
                if minimum <= item <= maximum
            ) or (default,)
        if default not in candidates:
            candidates = tuple(sorted(set(candidates + (default,))))
        object.__setattr__(self, "min_block_size", minimum)
        object.__setattr__(self, "max_block_size", maximum)
        object.__setattr__(self, "default_block_size", default)
        object.__setattr__(self, "block_candidates", candidates)
        object.__setattr__(self, "min_pipeline_depth", max(1, int(self.min_pipeline_depth)))
        object.__setattr__(self, "max_pipeline_depth", max(self.min_pipeline_depth, int(self.max_pipeline_depth)))
        object.__setattr__(self, "warmup_samples", max(0, int(self.warmup_samples)))
        # Clamp thresholds to the valid severity range and preserve their
        # ordering.  A malformed config with ``critical < reduce`` used to
        # make the critical branch unreachable (the elevated branch was
        # evaluated first), which could lead to a deceptively aggressive
        # recommendation under critical pressure.  Critical pressure must be
        # at least as severe as the reduction threshold.
        reduce_at = max(0.0, min(1.0, float(self.pressure_reduce_at)))
        critical_at = max(0.0, min(1.0, float(self.pressure_critical_at)))
        cache_at = max(0.0, min(1.0, float(self.cache_hit_increase_at)))
        critical_at = max(reduce_at, critical_at)
        object.__setattr__(self, "pressure_reduce_at", reduce_at)
        object.__setattr__(self, "pressure_critical_at", critical_at)
        object.__setattr__(self, "cache_hit_increase_at", cache_at)


@dataclass(frozen=True)
class AutoTuneRecommendation:
    """One bounded recommendation; no GPU-overlap claim is implied."""

    block_size: int = 512
    pipeline_depth: int = 1
    confidence: float = 0.0
    reason: str = "warmup"
    samples: int = 0
    overlap_verified: bool = False
    telemetry: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "block_size", max(1, int(self.block_size)))
        object.__setattr__(self, "pipeline_depth", max(1, int(self.pipeline_depth)))
        object.__setattr__(self, "confidence", max(0.0, min(1.0, float(self.confidence))))
        object.__setattr__(self, "telemetry", dict(self.telemetry or {}))

    @property
    def depth(self) -> int:
        return self.pipeline_depth

    def as_dict(self) -> dict[str, Any]:
        return {
            "block_size": self.block_size,
            "pipeline_depth": self.pipeline_depth,
            "confidence": self.confidence,
            "reason": self.reason,
            "samples": self.samples,
            "overlap_verified": bool(self.overlap_verified),
            "telemetry": dict(self.telemetry),
        }


def validate_autotune_recommendation(
    recommendation: AutoTuneRecommendation | Mapping[str, Any],
    config: Optional[AutoTuneConfig] = None,
) -> dict[str, Any]:
    """Validate a tuner result before it is used as a planning hint.

    This is a pure, backend-neutral diagnostic.  It intentionally does not
    clamp or mutate a recommendation: callers can use ``valid`` to fail
    closed and retain the established full-frame/direct path.  The check is
    useful for callers that deserialize a recommendation or combine telemetry
    from another process, where the dataclass ``__post_init__`` guarantees no
    longer apply.
    """

    if isinstance(recommendation, AutoTuneRecommendation):
        values = recommendation.as_dict()
    elif isinstance(recommendation, Mapping):
        values = dict(recommendation)
    else:
        return {"valid": False, "issues": [
            "recommendation must be AutoTuneRecommendation or mapping"
        ]}

    cfg = config if config is not None else AutoTuneConfig()
    issues: list[str] = []

    def _int(name: str, *, required: bool = True) -> Optional[int]:
        if name not in values:
            if required:
                issues.append(f"{name} is missing")
            return None
        try:
            value = int(values[name])
        except (TypeError, ValueError, OverflowError):
            issues.append(f"{name} must be an integer")
            return None
        return value

    block_size = _int("block_size")
    if block_size is not None:
        if block_size not in cfg.block_candidates:
            issues.append("block_size is not an allowed autotune candidate")
        if not cfg.min_block_size <= block_size <= cfg.max_block_size:
            issues.append("block_size is outside configured bounds")

    depth = _int("pipeline_depth")
    if depth is not None and not cfg.min_pipeline_depth <= depth <= cfg.max_pipeline_depth:
        issues.append("pipeline_depth is outside configured bounds")

    confidence = values.get("confidence")
    try:
        confidence_value = float(confidence)
    except (TypeError, ValueError, OverflowError):
        issues.append("confidence must be finite and in [0, 1]")
    else:
        if not isfinite(confidence_value) or not 0.0 <= confidence_value <= 1.0:
            issues.append("confidence must be finite and in [0, 1]")

    samples = _int("samples")
    if samples is not None and samples < 0:
        issues.append("samples must be non-negative")

    if "overlap_verified" in values and not isinstance(values["overlap_verified"], bool):
        issues.append("overlap_verified must be boolean")

    return {
        "valid": not issues,
        "issues": issues,
        "checked_fields": ("block_size", "pipeline_depth", "confidence", "samples", "overlap_verified"),
    }


class ConservativeAutoTuner:
    """EWMA-based bounded tuner for block size and planning depth.

    The tuner changes one candidate step at a time and falls back to a
    single-depth plan whenever telemetry is missing, pressure is elevated, or
    the operation contract is not explicitly local.  ``pipeline_depth`` is a
    serial planning/queue hint; ``overlap_verified`` is always false unless a
    caller explicitly provides verified evidence (which this class does not
    infer from ``max_concurrency``).
    """

    def __init__(
        self,
        config: Optional[AutoTuneConfig] = None,
        telemetry: Optional[PlannerTelemetry] = None,
        *,
        alpha: float = 0.2,
    ) -> None:
        self.config = config if config is not None else AutoTuneConfig()
        self.telemetry = telemetry if telemetry is not None else PlannerTelemetry(alpha)
        self._profiles: dict[tuple[str, str], PlannerTelemetry] = {}
        self._lock = RLock()

    def _profile(self, operation: Optional[str] = None, backend: Optional[str] = None) -> PlannerTelemetry:
        key = (str(backend or "*").lower(), str(operation or "*").lower())
        with self._lock:
            profile = self._profiles.get(key)
            if profile is None:
                profile = PlannerTelemetry(self.telemetry.alpha)
                self._profiles[key] = profile
            return profile

    def observe(
        self,
        telemetry: Optional[Mapping[str, Any]] = None,
        *,
        operation: Optional[str] = None,
        backend: Optional[str] = None,
        **metrics: Any,
    ) -> "ConservativeAutoTuner":
        values = dict(telemetry or {})
        values.update(metrics)
        self.telemetry.observe(values)
        self._profile(operation, backend).observe(values)
        return self

    record = observe

    @staticmethod
    def _contract_is_safe(contract: Any, backend: Optional[str]) -> bool:
        if contract is None:
            return True
        try:
            method = getattr(contract, "can_auto_block", None)
            if callable(method):
                return bool(method(backend))
            if hasattr(contract, "allows_automatic_block"):
                return bool(contract.allows_automatic_block)
            if isinstance(contract, Mapping):
                shape = str(contract.get("shape_transform", "unknown")).lower()
                reduction = str(contract.get("reduction", "unknown")).lower()
                return bool(
                    contract.get("automatic_safe", False)
                    and contract.get("parity_qualified", False)
                    and shape in {"same", "same_shape"}
                    and reduction in {"none", "local"}
                    and not contract.get("variable_cardinality", False)
                    and not contract.get("side_effect", contract.get("side_effects", False))
                )
        except Exception:
            return False
        return False

    @staticmethod
    def _nearest_candidate(value: Any, candidates: Sequence[int]) -> int:
        try:
            value = int(value)
        except (TypeError, ValueError):
            return candidates[len(candidates) // 2]
        return min(candidates, key=lambda item: abs(item - value))

    def recommend(
        self,
        operation: Optional[str] = None,
        backend: Optional[str] = None,
        *,
        current_block_size: Any = None,
        resident_limit: Optional[int] = None,
        contract: Any = None,
        telemetry: Optional[PlannerTelemetry] = None,
    ) -> AutoTuneRecommendation:
        config = self.config
        profile = telemetry or self._profile(operation, backend)
        snapshot = profile.snapshot()
        samples = int(snapshot.get("samples", 0) or 0)
        candidates = config.block_candidates
        current = self._nearest_candidate(
            config.default_block_size if current_block_size is None else current_block_size,
            candidates,
        )
        pressure = snapshot.get("pressure")
        pressure = _pressure_value(pressure)
        cache_hit = snapshot.get("cache_hit_rate")
        cache_hit = None if cache_hit is None else max(0.0, min(1.0, float(cache_hit)))
        peak = snapshot.get("peak_resident_bytes")
        latency = snapshot.get("latency_ms")
        reason = "warmup"
        target = current
        depth = config.min_pipeline_depth

        # Missing/unsafe contracts are always conservative.  This check is
        # intentionally separate from the native registry so a new caller
        # cannot opt in merely by naming an unknown operation.
        if contract is not None and not self._contract_is_safe(contract, backend):
            reason = "operation contract is not automatic-block-safe"
        elif samples < config.warmup_samples:
            reason = "insufficient EWMA samples"
        elif pressure is None:
            reason = "pressure telemetry unavailable"
        elif pressure >= config.pressure_critical_at:
            target = candidates[max(0, candidates.index(current) - 1)]
            reason = "critical resident-memory pressure"
        elif pressure >= config.pressure_reduce_at:
            target = candidates[max(0, candidates.index(current) - 1)]
            reason = "elevated resident-memory pressure"
        else:
            # A resident-limit ratio above 80% is treated like elevated
            # pressure even if a backend reports a coarse pressure label.
            resident_ratio = None
            if resident_limit and peak is not None:
                try:
                    resident_ratio = float(peak) / max(1, int(resident_limit))
                except (TypeError, ValueError):
                    resident_ratio = None
            if resident_ratio is not None and resident_ratio >= 0.80:
                target = candidates[max(0, candidates.index(current) - 1)]
                reason = "resident limit headroom is low"
            elif cache_hit is not None and cache_hit >= config.cache_hit_increase_at:
                index = candidates.index(current)
                if index + 1 < len(candidates):
                    target = candidates[index + 1]
                    reason = "healthy cache hit-rate permits one larger tile"
                else:
                    reason = "healthy telemetry at maximum tile"
                # Depth is a bounded serial planning hint.  It is not a claim
                # that Python dispatches or device queues overlap.
                depth = min(config.max_pipeline_depth, max(config.min_pipeline_depth, 2))
            else:
                reason = "stable telemetry; retain conservative tile"

        if pressure is not None and pressure >= config.pressure_reduce_at:
            depth = config.min_pipeline_depth
        confidence = 0.0 if samples < config.warmup_samples else min(1.0, samples / 20.0)
        return AutoTuneRecommendation(
            block_size=target,
            pipeline_depth=depth,
            confidence=confidence,
            reason=reason,
            samples=samples,
            overlap_verified=False,
            telemetry=snapshot,
        )

    def recommend_block_size(self, *args: Any, **kwargs: Any) -> int:
        return self.recommend(*args, **kwargs).block_size

    def recommend_pipeline_depth(self, *args: Any, **kwargs: Any) -> int:
        return self.recommend(*args, **kwargs).pipeline_depth

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            profiles = {
                f"{backend}:{operation}": profile.snapshot()
                for (backend, operation), profile in self._profiles.items()
            }
        return {"global": self.telemetry.snapshot(), "profiles": profiles}


AutoPipelineAutotuner = ConservativeAutoTuner
EWMATuner = ConservativeAutoTuner


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
    operation: Optional[str] = None
    contract: Any = None
    # Native AOT modules own their compute graphs and command caches.  A
    # recording may span modules only when the bridge explicitly proves that
    # boundary; keep the default unknown for compatibility and let the
    # planner split two *known, different* module keys conservatively.
    module_key: Optional[str] = None

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValueError("graph name must be non-empty")
        if int(self.resident_bytes) < 0:
            raise ValueError("resident_bytes must be non-negative")
        object.__setattr__(self, "resident_bytes", int(self.resident_bytes))
        object.__setattr__(self, "reads", tuple(str(item) for item in self.reads))
        object.__setattr__(self, "writes", tuple(str(item) for item in self.writes))
        object.__setattr__(self, "operation", None if self.operation is None else str(self.operation))
        object.__setattr__(self, "metadata", dict(self.metadata or {}))
        if self.contract is None and "contract" in self.metadata:
            object.__setattr__(self, "contract", self.metadata.get("contract"))
        if self.operation is None and "operation" in self.metadata:
            object.__setattr__(self, "operation", str(self.metadata.get("operation")))
        module_key = self.module_key
        if module_key is None:
            module_key = self.metadata.get("module_key", self.metadata.get("module"))
        object.__setattr__(
            self,
            "module_key",
            None if module_key is None or not str(module_key).strip() else str(module_key),
        )


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
    pipeline_depth: int = 1
    recommended_block_size: int = 512
    tuning: Mapping[str, Any] = field(default_factory=dict)
    overlap_verified: bool = False

    @property
    def graph_count(self) -> int:
        return sum(len(segment) for segment in self.segments)

    @property
    def is_recorded(self) -> bool:
        return self.mode == "recorded"

    @property
    def recordable_segment_count(self) -> int:
        """Number of segments eligible for one-shot recording.

        ``is_recorded`` intentionally keeps its historical meaning for a
        single contiguous recording.  Segmented plans expose this additive
        diagnostic so callers can distinguish direct singleton segments from
        qualified multi-graph segments without claiming queue overlap.
        """
        count = 0
        for segment in self.segments:
            if len(segment) < 2:
                continue
            if all(
                int(getattr(spec, "resident_bytes", 0) or 0) > 0
                and bool(getattr(spec, "backend_safe", True))
                and not (getattr(spec, "metadata", {}) or {}).get(
                    "_implicit_graph_name"
                )
                for spec in segment
            ):
                count += 1
        return count

    @property
    def has_recordable_segments(self) -> bool:
        return self.recordable_segment_count > 0

    @property
    def segment_resident_bytes(self) -> tuple[int, ...]:
        """Estimated resident footprint of each planned segment.

        This is diagnostic metadata only: it reflects the graph contracts used
        by the planner and does not claim that a native driver allocates these
        bytes exactly.  Exposing the per-segment values makes a segmented
        (block/full-frame) decision explainable without inspecting private
        planner state.
        """
        return tuple(
            sum(int(getattr(graph, "resident_bytes", 0) or 0) for graph in segment)
            for segment in self.segments
        )

    @property
    def resident_headroom_bytes(self) -> Optional[int]:
        """Signed headroom against the adaptive limit, when one exists."""
        if int(self.resident_limit) <= 0:
            return None
        return int(self.resident_limit) - int(self.resident_bytes)

    def as_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "segments": [[graph.name for graph in segment] for segment in self.segments],
            "resident_bytes": self.resident_bytes,
            "resident_limit": self.resident_limit,
            "backend": self.backend,
            "reason": self.reason,
            "max_concurrency": self.max_concurrency,
            "pipeline_depth": self.pipeline_depth,
            "recommended_block_size": self.recommended_block_size,
            "recordable_segment_count": self.recordable_segment_count,
            "segment_graph_counts": [len(segment) for segment in self.segments],
            "segment_resident_bytes": list(self.segment_resident_bytes),
            "resident_headroom_bytes": self.resident_headroom_bytes,
            "fits_resident_limit": (
                self.resident_headroom_bytes is not None
                and self.resident_headroom_bytes >= 0
            ),
            "autotune": dict(self.tuning),
            # A concurrency hint is not device-overlap evidence.  Keep this
            # explicit in diagnostics so callers do not overstate telemetry.
            "overlap_verified": bool(self.overlap_verified),
        }


def _coerce_spec(value: GraphSpec | Mapping[str, Any] | str) -> GraphSpec:
    if isinstance(value, GraphSpec):
        return value
    if isinstance(value, str):
        # A bare graph name is intentionally kept as a compatibility input,
        # but it does not carry a static footprint, dependency contract, or
        # backend qualification.  Mark it so ``plan`` can fail closed rather
        # than treating the default zero-byte estimate as proof that an
        # arbitrary graph sequence fits in one recorded pipeline.
        return GraphSpec(value, metadata={"_implicit_graph_name": True})
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
        telemetry: Optional[PlannerTelemetry] = None,
        autotuner: Optional[ConservativeAutoTuner] = None,
        autotune: bool = True,
        autotune_config: Optional[AutoTuneConfig] = None,
        plan_cache_size: int = 64,
        plan_cache_min_graphs: int = 8,
    ) -> None:
        self.backend = str(backend or "cpu").lower()
        self.memory_provider = memory_provider
        self.minimum_recorded_graphs = max(2, int(minimum_recorded_graphs))
        self.unsafe_backends = {str(item).lower() for item in unsafe_backends}
        self.telemetry = telemetry if telemetry is not None else PlannerTelemetry()
        self.autotune_enabled = bool(autotune)
        self.autotuner = autotuner if autotuner is not None else ConservativeAutoTuner(
            autotune_config,
            self.telemetry,
        )
        # Planning is pure with respect to a stable graph/resource contract,
        # but it is invoked for every automatic scope.  Keep a small bounded
        # LRU of immutable plans so repeated frames with the same shape do not
        # repeatedly rebuild segment boundaries.  The memory budget and tuner
        # recommendation are part of the key, and ``observe`` invalidates old
        # entries, so this optimization cannot reuse a plan after pressure or
        # capability telemetry changes.  This cache only removes host-side
        # planning work; it does not cache native command recordings or imply
        # queue overlap.
        self._plan_cache_size = max(0, int(plan_cache_size))
        # Very short plans are cheaper to recompute than to fingerprint.  The
        # default therefore only caches genuinely multi-stage scopes; callers
        # running a stable two-stage hot loop can opt in with ``0`` without
        # changing any execution semantics.
        self._plan_cache_min_graphs = max(0, int(plan_cache_min_graphs))
        self._plan_cache = OrderedDict()
        self._plan_cache_hits = 0
        self._plan_cache_misses = 0
        self._plan_cache_lock = RLock()

    _UNCACHEABLE = object()

    @classmethod
    def _freeze_cache_value(cls, value, *, _depth: int = 0):
        """Convert contract metadata into a deterministic cache key value.

        Planner metadata is normally made of scalar values, tuples, and small
        mappings.  Unknown mutable objects are rejected rather than keyed by a
        potentially unstable ``repr``; an uncacheable contract simply takes
        the established uncached planning path.
        """
        if _depth > 8:
            return cls._UNCACHEABLE
        if value is None or isinstance(value, (bool, int, str, bytes)):
            return value
        if isinstance(value, float):
            # NaN is not a useful cache discriminator and does not compare
            # equal to itself.  Keep such metadata off the cache path.
            return value if value == value else cls._UNCACHEABLE
        if isinstance(value, Mapping):
            items = []
            for key, item in value.items():
                frozen_key = cls._freeze_cache_value(key, _depth=_depth + 1)
                frozen_item = cls._freeze_cache_value(item, _depth=_depth + 1)
                if cls._UNCACHEABLE in (frozen_key, frozen_item):
                    return cls._UNCACHEABLE
                items.append((frozen_key, frozen_item))
            try:
                return ("mapping", tuple(sorted(items, key=repr)))
            except Exception:
                return cls._UNCACHEABLE
        if isinstance(value, (tuple, list)):
            frozen = tuple(
                cls._freeze_cache_value(item, _depth=_depth + 1)
                for item in value
            )
            return cls._UNCACHEABLE if cls._UNCACHEABLE in frozen else frozen
        if isinstance(value, (set, frozenset)):
            frozen = tuple(
                cls._freeze_cache_value(item, _depth=_depth + 1)
                for item in value
            )
            if cls._UNCACHEABLE in frozen:
                return cls._UNCACHEABLE
            return ("set", tuple(sorted(frozen, key=repr)))
        if is_dataclass(value) and not isinstance(value, type):
            values = []
            try:
                for item in fields(value):
                    frozen = cls._freeze_cache_value(
                        getattr(value, item.name), _depth=_depth + 1
                    )
                    if frozen is cls._UNCACHEABLE:
                        return cls._UNCACHEABLE
                    values.append((item.name, frozen))
            except Exception:
                return cls._UNCACHEABLE
            return (type(value).__qualname__, tuple(values))
        return cls._UNCACHEABLE

    @classmethod
    def _spec_cache_key(cls, spec: GraphSpec):
        metadata = dict(getattr(spec, "metadata", {}) or {})
        # ``GraphSpec.__post_init__`` mirrors these fields into metadata for
        # compatibility.  The normalized fields below are the authoritative
        # values, so omit duplicate contract/operation entries from metadata.
        metadata.pop("contract", None)
        metadata.pop("operation", None)
        frozen_metadata = cls._freeze_cache_value(metadata)
        if frozen_metadata is cls._UNCACHEABLE:
            return cls._UNCACHEABLE
        contract = getattr(spec, "contract", None)
        if contract is None:
            contract_key = None
        else:
            contract_key = cls._freeze_cache_value(contract)
            if contract_key is cls._UNCACHEABLE:
                return cls._UNCACHEABLE
        return (
            str(spec.name),
            int(spec.resident_bytes),
            tuple(spec.reads),
            tuple(spec.writes),
            bool(spec.backend_safe),
            bool(spec.force_boundary),
            frozen_metadata,
            None if spec.operation is None else str(spec.operation),
            contract_key,
            None if spec.module_key is None else str(spec.module_key),
        )

    def _plan_cache_key(self, specs, limit, concurrency, tuning, backend_unsafe):
        if (
            self._plan_cache_size <= 0
            or len(specs) < self._plan_cache_min_graphs
        ):
            return None
        frozen_specs = tuple(self._spec_cache_key(spec) for spec in specs)
        if self._UNCACHEABLE in frozen_specs:
            return None
        frozen_tuning = self._freeze_cache_value(tuning.as_dict())
        if frozen_tuning is self._UNCACHEABLE:
            return None
        config = self.autotuner.config
        config_key = self._freeze_cache_value(config)
        if config_key is self._UNCACHEABLE:
            return None
        return (
            str(self.backend),
            int(self.minimum_recorded_graphs),
            tuple(sorted(self.unsafe_backends)),
            bool(self.autotune_enabled),
            int(limit),
            int(concurrency),
            bool(backend_unsafe),
            frozen_specs,
            frozen_tuning,
            config_key,
        )

    def _plan_cache_get(self, key):
        if key is None:
            return None
        with self._plan_cache_lock:
            plan = self._plan_cache.pop(key, None)
            if plan is None:
                self._plan_cache_misses += 1
                return None
            self._plan_cache[key] = plan
            self._plan_cache_hits += 1
            return plan

    def _plan_cache_put(self, key, plan):
        if key is None or self._plan_cache_size <= 0:
            return
        with self._plan_cache_lock:
            self._plan_cache.pop(key, None)
            self._plan_cache[key] = plan
            while len(self._plan_cache) > self._plan_cache_size:
                self._plan_cache.popitem(last=False)

    def clear_plan_cache(self):
        """Invalidate host-side plans without affecting native pipelines."""
        with self._plan_cache_lock:
            self._plan_cache.clear()

    def plan_cache_stats(self) -> dict[str, Any]:
        """Return bounded planning-cache telemetry for diagnostics."""
        with self._plan_cache_lock:
            requests = self._plan_cache_hits + self._plan_cache_misses
            return {
                "enabled": self._plan_cache_size > 0,
                "entries": len(self._plan_cache),
                "max_entries": int(self._plan_cache_size),
                "min_graphs": int(self._plan_cache_min_graphs),
                "hits": int(self._plan_cache_hits),
                "misses": int(self._plan_cache_misses),
                "hit_rate": self._plan_cache_hits / requests if requests else 0.0,
            }

    def observe(self, telemetry: Optional[Mapping[str, Any]] = None, **metrics: Any) -> "AutoPipelinePlanner":
        """Record host-side dispatch telemetry for the next plan.

        This hook accepts measured latency/transfer/resident/cache/pressure
        values.  It intentionally does not infer overlap from a concurrency
        field or from the fact that a native backend was selected.
        """
        values = dict(telemetry or {})
        values.update(metrics)
        self.telemetry.observe(values)
        # Keep operation-agnostic observations available to the tuner.  A
        # caller that has per-operation data can use ``autotuner.observe``.
        self.autotuner.observe(values, backend=self.backend)
        # Observations can alter both the pressure gate and the EWMA tile/depth
        # recommendation.  Drop only the host plan cache; active/native
        # recordings and buffer residency remain untouched.
        self.clear_plan_cache()
        return self

    record_telemetry = observe

    def _tuning(self, specs: tuple[GraphSpec, ...], limit: int) -> AutoTuneRecommendation:
        if not self.autotune_enabled:
            return AutoTuneRecommendation(
                block_size=self.autotuner.config.default_block_size,
                pipeline_depth=self.autotuner.config.min_pipeline_depth,
                reason="autotune disabled",
                telemetry=self.telemetry.snapshot(),
            )
        operation = None
        contract = None
        if specs:
            first = specs[0]
            operation = first.operation or first.metadata.get("operation")
            contract = first.contract or first.metadata.get("contract")
        return self.autotuner.recommend(
            operation=operation,
            backend=self.backend,
            resident_limit=limit,
            contract=contract,
        )

    @staticmethod
    def _metadata_requires_boundary(spec: GraphSpec) -> bool:
        """Return whether metadata requests a hard sequencing boundary.

        A graph may be locally shape-safe while still depending on an external
        side effect, reduction, or a driver barrier.  These facts are not
        inferable from the graph name, so a caller can opt into a conservative
        boundary with additive metadata.  Unknown hazard labels fail closed;
        explicit ``hazard_policy='ordered'`` is reserved for a graph family
        that has independently validated its serial resource contract.
        """
        metadata = getattr(spec, "metadata", {}) or {}
        for key in ("requires_barrier", "force_boundary", "external_side_effect"):
            value = metadata.get(key)
            if isinstance(value, str):
                value = value.strip().lower() in {"1", "true", "yes", "required", "global"}
            if bool(value):
                return True
        hazards = metadata.get("hazards", metadata.get("hazard"))
        if hazards is None:
            return False
        if isinstance(hazards, bool):
            return hazards
        if isinstance(hazards, Mapping):
            hazards = [key for key, value in hazards.items() if value]
        elif isinstance(hazards, str):
            hazards = hazards.replace(",", " ").split()
        try:
            tokens = {str(item).strip().lower() for item in hazards if str(item).strip()}
        except TypeError:
            tokens = {str(hazards).strip().lower()}
        safe_tokens = {"none", "local", "ordered", "serial", "safe"}
        if not tokens or tokens <= safe_tokens:
            return False
        # Hazard labels are an opt-in safety declaration.  Any unrecognised
        # non-empty label is treated as unsafe rather than guessed to be local.
        return True

    @staticmethod
    def _shape_metadata(spec: GraphSpec) -> Optional[tuple[Any, ...]]:
        """Extract a comparable shape tuple from additive graph metadata."""
        metadata = getattr(spec, "metadata", {}) or {}
        for key in ("shape", "input_shape", "output_shape", "grid_shape"):
            value = metadata.get(key)
            if value is None or isinstance(value, (str, bytes)):
                continue
            try:
                shape = tuple(value)
            except TypeError:
                continue
            if shape:
                return shape
        return None

    @staticmethod
    def _shape_change_allowed(spec: GraphSpec) -> bool:
        metadata = getattr(spec, "metadata", {}) or {}
        if metadata.get("shape_compatible") is True or metadata.get("allow_shape_change") is True:
            return True
        policy = str(metadata.get("shape_policy", "") or "").strip().lower()
        return policy in {"ordered", "transform", "local", "same", "same_shape"}

    @classmethod
    def _shape_requires_boundary(cls, previous: GraphSpec, current: GraphSpec) -> bool:
        previous_shape = cls._shape_metadata(previous)
        current_shape = cls._shape_metadata(current)
        if previous_shape is None or current_shape is None or previous_shape == current_shape:
            return False
        return not (cls._shape_change_allowed(previous) or cls._shape_change_allowed(current))

    @staticmethod
    def _resource_hazard(previous: GraphSpec, current: GraphSpec) -> Optional[str]:
        """Classify a conservative inter-graph read/write hazard.

        Native command recording does not itself prove that two wrappers share
        compatible resource lifetimes.  If a caller supplies resource names,
        split RAW/WAR/WAW edges unless the graph family explicitly declares an
        ordered serial contract through ``hazard_policy='ordered'`` or
        ``allow_resource_hazards=True``.
        """
        def resources(spec: GraphSpec, key: str) -> set[str]:
            return {
                str(item).strip()
                for item in getattr(spec, key, ())
                if str(item).strip()
            }

        previous_metadata = getattr(previous, "metadata", {}) or {}
        current_metadata = getattr(current, "metadata", {}) or {}
        if any(
            bool(metadata.get("allow_resource_hazards"))
            or str(metadata.get("hazard_policy", "") or "").strip().lower()
            in {"ordered", "serial", "intra_pipeline", "safe"}
            for metadata in (previous_metadata, current_metadata)
        ):
            return None
        previous_reads = resources(previous, "reads")
        previous_writes = resources(previous, "writes")
        current_reads = resources(current, "reads")
        current_writes = resources(current, "writes")
        sequence_kind = str(
            previous_metadata.get("sequence_kind", "") or ""
        ).strip().lower()
        current_sequence_kind = str(
            current_metadata.get("sequence_kind", "") or ""
        ).strip().lower()
        # A few established wrappers publish a deterministic local sequence
        # contract (for example, a producer followed by its same-operation
        # consumer).  Their ordered dependency is safe to keep in one native
        # recording; arbitrary resource names without this declaration still
        # fail closed below.
        ordered_sequence = {
            "two_pass_local_stencil",
            "deterministic_local_prefix",
            "vote_then_peak",
        }
        if (
            sequence_kind
            and sequence_kind == current_sequence_kind
            and sequence_kind in ordered_sequence
            and previous.operation is not None
            and previous.operation == current.operation
        ):
            return None
        if previous_writes & current_reads:
            return "read-after-write resource dependency"
        if previous_reads & current_writes:
            return "write-after-read resource dependency"
        if previous_writes & current_writes:
            return "write-after-write resource alias"
        return None

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
        # The current governor proves residency/preload depth, not overlapping
        # queue submissions.  Keep the legacy max_concurrency field for API
        # compatibility while preferring the explicit depth telemetry.
        concurrency = int(
            telemetry.get("residency_depth", telemetry.get("max_concurrency", 1))
            or 1
        )
        return max(0, limit), max(1, concurrency)

    def _can_merge(self, previous: GraphSpec, current: GraphSpec) -> bool:
        if previous.force_boundary or current.force_boundary:
            return False
        if self._metadata_requires_boundary(previous) or self._metadata_requires_boundary(current):
            return False
        if self._shape_requires_boundary(previous, current):
            return False
        if self._resource_hazard(previous, current) is not None:
            return False
        # A graph name is not globally unique: the same operation can be
        # present in several AOT modules, each with an independent native
        # command cache.  Keep legacy GraphSpec callers compatible when no
        # module key is supplied, but never capture a boundary between two
        # explicitly different module owners in one recording.
        previous_module = previous.module_key or previous.metadata.get("module_key") or previous.metadata.get("module")
        current_module = current.module_key or current.metadata.get("module_key") or current.metadata.get("module")
        if (
            previous_module is not None
            and current_module is not None
            and str(previous_module).strip()
            and str(current_module).strip()
            and str(previous_module) != str(current_module)
        ):
            return False
        for spec in (previous, current):
            contract = spec.contract or spec.metadata.get("contract")
            if contract is not None:
                try:
                    allows = getattr(contract, "allows_pipeline", None)
                    if allows is None and isinstance(contract, Mapping):
                        allows = bool(
                            contract.get("known", True)
                            and str(contract.get("shape_transform", "unknown")).lower()
                            in {"same", "same_shape"}
                            and str(contract.get("reduction", "unknown")).lower()
                            in {"none", "local"}
                            and not contract.get("variable_cardinality", False)
                            and not contract.get("side_effect", contract.get("side_effects", False))
                        )
                    if not bool(allows):
                        return False
                    supports = getattr(contract, "supports_backend", None)
                    if callable(supports) and not supports(self.backend, require_parity=True):
                        return False
                except Exception:
                    return False
        # Resource, shape, and explicit metadata hazards above are deliberately
        # fail-closed.  The planner never claims that a driver will synthesize
        # a missing barrier or retain an aliased buffer for us.
        return previous.backend_safe and current.backend_safe

    def plan(self, graphs: Iterable[GraphSpec | Mapping[str, Any] | str]) -> PipelinePlan:
        specs = tuple(_coerce_spec(value) for value in graphs)
        limit, concurrency = self._limits()
        total = sum(spec.resident_bytes for spec in specs)
        backend_unsafe = self.backend in self.unsafe_backends
        tuning = self._tuning(specs, limit)
        tuning_dict = tuning.as_dict()
        cache_key = self._plan_cache_key(
            specs, limit, concurrency, tuning, backend_unsafe
        )
        cached = self._plan_cache_get(cache_key)
        if cached is not None:
            return cached

        def make_plan(
            mode: str,
            segments: tuple[tuple[GraphSpec, ...], ...],
            reason: str,
        ) -> PipelinePlan:
            plan = PipelinePlan(
                mode,
                segments,
                total,
                limit,
                self.backend,
                reason,
                concurrency,
                pipeline_depth=tuning.pipeline_depth,
                recommended_block_size=tuning.block_size,
                tuning=tuning_dict,
                overlap_verified=False,
            )
            self._plan_cache_put(cache_key, plan)
            return plan

        if not specs:
            return make_plan("direct", (), "empty graph list")
        if backend_unsafe or any(not spec.backend_safe for spec in specs):
            return make_plan(
                "segmented", tuple((spec,) for spec in specs),
                "backend or graph capability requires direct boundaries",
            )

        # A zero-byte estimate is not a safe lower bound for a native graph:
        # graph arguments may allocate transient/intermediate storage during
        # the first dispatch.  In particular, bare string names are used by
        # legacy callers (and by a few algorithm wrappers) without any shape,
        # dtype, dependency, or contract metadata.  Never record such a
        # sequence merely because ``total == 0``.  Explicit ``GraphSpec``
        # instances that provide a positive resident estimate retain the
        # historical behavior even when they omit a contract; this keeps the
        # compatibility API working while requiring the new automatic path to
        # provide a real footprint.
        incomplete = []
        for spec in specs:
            metadata = spec.metadata or {}
            if metadata.get("_implicit_graph_name"):
                incomplete.append(spec.name)
            elif int(spec.resident_bytes) <= 0:
                incomplete.append(spec.name)
        if incomplete:
            names = ", ".join(repr(name) for name in incomplete[:4])
            if len(incomplete) > 4:
                names += ", ..."
            mode = "direct" if len(specs) == 1 else "segmented"
            segments = (specs,) if mode == "direct" else tuple((spec,) for spec in specs)
            return make_plan(
                mode,
                segments,
                "graph footprint/contract metadata is incomplete; "
                f"recording disabled for {names}",
            )
        if len(specs) < self.minimum_recorded_graphs:
            return make_plan("direct", (specs,), "single graph has no recording amortization")
        if limit <= 0:
            return make_plan(
                "segmented", tuple((spec,) for spec in specs),
                "no resident-memory budget is available",
            )
        if total <= limit and all(self._can_merge(specs[i - 1], specs[i]) for i in range(1, len(specs))):
            return make_plan(
                "recorded", (specs,),
                "all graphs fit the adaptive resident-memory limit",
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
        return make_plan(
            "segmented", tuple(segments),
            "graphs exceed the adaptive resident-memory limit or contain boundaries",
        )


AutoTune = ConservativeAutoTuner


__all__ = [
    "EWMA", "PlannerTelemetry", "PipelineTelemetry", "EWMATelemetry",
    "AutoTuneConfig", "AutoTuneRecommendation", "validate_autotune_recommendation", "ConservativeAutoTuner",
    "AutoPipelineAutotuner", "EWMATuner", "AutoTune", "GraphSpec",
    "PipelinePlan", "AutoPipelinePlanner",
]
