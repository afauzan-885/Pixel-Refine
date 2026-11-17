"""Execution-strategy resolution for the public neural facade.

The resolver answers one question *before* any device work: which internal
implementation can run this graph on this backend, and why. It never executes a
kernel; it only validates the ONNX graph and inspects staged artifacts.

Strategy order (first match wins):

1. ``pool``     — universal kernel pool, when the operator registry admits the
                  graph, the pool artifact exists, and every operator that needs
                  INT64 device support has an enabled candidate pool.
2. ``resident`` — a per-model TCM artifact pre-baked for this graph/backend.
3. ``native``   — the native per-model graph lowering (limited operator set).

When nothing matches, :class:`CapabilityMissingError` lists the offending
operators and the concrete remedy.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from .capabilities import (
    INT64_CANDIDATE_OPS,
    NATIVE_GRAPH_OPS,
    find_prebaked_artifact,
    int64_candidate_enabled,
    pool_artifact_path,
    pool_graph_names,
)
from .errors import BackendUnavailable, CapabilityMissingError, ModelNotRunnable


@dataclass
class ResolutionRecord:
    """Auditable outcome of one resolution attempt."""

    status: str                      # "resolved" | "unresolved"
    strategy: Optional[str] = None
    backend: str = "cpu"
    reasons: List[str] = field(default_factory=list)
    attempts: List[str] = field(default_factory=list)
    missing_ops: Tuple[str, ...] = ()
    missing_features: Tuple[str, ...] = ()
    artifact: Optional[str] = None

    def describe(self) -> str:
        lines = [f"status={self.status} strategy={self.strategy} backend={self.backend}"]
        if self.artifact:
            lines.append(f"artifact={self.artifact}")
        if self.missing_ops:
            lines.append(f"missing_ops={list(self.missing_ops)}")
        if self.missing_features:
            lines.append(f"missing_features={list(self.missing_features)}")
        for attempt in self.attempts:
            lines.append(f"attempt: {attempt}")
        for reason in self.reasons:
            lines.append(f"reason: {reason}")
        return "\n".join(lines)


@dataclass
class Resolution:
    """A resolved strategy plus the pieces the facade needs to construct it."""

    strategy: str
    backend: str
    record: ResolutionRecord
    artifact: Optional[Path] = None
    graph_model_bytes: Optional[bytes] = None
    model_name: str = "neural_model"


def resolve_backend(backend: Optional[str]) -> str:
    """Normalise an explicit backend name; ``auto`` asks the runtime."""
    token = str(backend or "auto").strip().lower()
    if token in ("", "auto", "default"):
        from taichi.aot_engine import get_backend_name

        return str(get_backend_name()).lower()
    return token


def _plan_ops(model_bytes: bytes) -> Tuple[Optional[Set[str]], Optional[Any], Optional[str]]:
    """Validate the graph against the universal registry (import-safe)."""
    from ..taichi_algorithm.neural.universal.errors import UnsupportedONNXOperatorError
    from ..taichi_algorithm.neural.universal.plan import Plan

    try:
        plan = Plan.from_model_bytes(model_bytes)
    except UnsupportedONNXOperatorError as exc:
        return None, None, f"operator registry rejected the graph: {exc}"
    except Exception as exc:  # noqa: BLE001
        return None, None, f"graph could not be planned: {type(exc).__name__}: {exc}"
    return {node.op for node in plan.nodes}, plan, None


def _device_i64_ops(plan: Any, ops: Set[str]) -> Set[str]:
    """Operators that would need INT64 device support to execute."""
    from ..taichi_algorithm.neural.universal.dtypes import I64

    i64_values = {
        name for name, dtype in plan.dtypes.items()
        if dtype == I64 and name not in plan.constants and name not in plan.host_int_values
    }
    if not i64_values:
        return set()
    offending: Set[str] = set()
    for node in plan.nodes:
        touches = node.output in i64_values or any(
            name in i64_values for name in node.inputs if name
        )
        if touches and node.op in INT64_CANDIDATE_OPS:
            offending.add(node.op)
    return offending


#: Operators the native Rust surface can execute today, keyed by the capability
#: name it reports. Derived from ``i64_capabilities()`` so a new native operator
#: is picked up without editing this list twice.
_NATIVE_CAPABILITY_TO_OPS: Dict[str, Tuple[str, ...]] = {
    "i64_binary": ("Add", "Sub", "Mul", "Div", "Mod"),
    "i64_cmp": ("Less", "Greater", "Equal"),
    "i64_where": ("Where",),
    "cast": ("Cast",),
    "fill": ("ConstantOfShape",),
    "range_i64": ("Range",),
    "gather_i64": ("Gather",),
    "gather_elements_i64": ("GatherElements",),
    "transpose4_i64": ("Transpose",),
    "slice_axis_i64": ("Slice",),
    "concat_axis_i64": ("Concat",),
    "topk_last_i64": ("TopK",),
    "split_axis_i64": ("Split",),
    "expand_i64": ("Expand",),
    "nonzero_i64": ("NonZero",),
}


def native_int64_ops() -> FrozenSet[str]:
    """Operators the installed native extension can run for INT64 values.

    Empty unless the native path is actually usable against runtime buffers: the
    functions exist but need a device pointer the bridge does not expose.
    """
    from ..taichi_algorithm.neural.universal import native_i64

    if not native_i64.usable():
        return frozenset()
    module = native_i64.native_module()
    covered: Set[str] = set()
    for capability in module.i64_capabilities():
        covered.update(_NATIVE_CAPABILITY_TO_OPS.get(capability, ()))
    return frozenset(covered)


def _int64_uncovered(ops: Set[str]) -> Set[str]:
    """INT64-touching operators the native Rust surface does **not** cover.

    When the rebuilt extension exposes the native INT64 operators, most of the
    operators previously listed under ``INT64_CANDIDATE_OPS`` are handled without
    the candidate artifact. Anything outside that native coverage still needs the
    pool candidate (or a lowering we do not have), so it stays a listed gap.
    """
    from ..taichi_algorithm.neural.universal import native_i64

    if not native_i64.available():
        return ops & INT64_CANDIDATE_OPS
    return ops & (INT64_CANDIDATE_OPS - native_int64_ops())


#: INT64-touching operators with no native Rust implementation yet. Mirrors the
#: refusals documented in ``taichi_vision/documentation/NEURAL_ONNX_BLOCKERS.md``.
INT64_UNCOVERED_BY_NATIVE: FrozenSet[str] = frozenset({
    "Split", "Expand", "NonZero", "ArgMax", "ReduceMean", "ReduceSum",
    "ReduceMax", "ReduceMin", "ReduceL2", "AveragePool", "MaxPool",
    "GlobalAveragePool", "Conv", "ConvTranspose", "MatMul", "Gemm",
    "FusedMatMul", "InstanceNormalization", "LayerNormalization",
    "BatchNormalization", "Softmax", "LogSoftmax", "PRelu", "Clip", "Resize",
})


def resolve(
    model_bytes: bytes,
    *,
    backend: Optional[str] = None,
    model_name: str = "neural_model",
    asset_dir: Optional[Path] = None,
) -> Resolution:
    """Pick the execution strategy for ``model_bytes`` on ``backend``."""
    resolved_backend = resolve_backend(backend)
    record = ResolutionRecord(status="unresolved", backend=resolved_backend)

    ops, plan, plan_error = _plan_ops(model_bytes)

    # --- strategy 1: universal kernel pool -------------------------------
    pool_path = pool_artifact_path(resolved_backend, asset_dir)
    if plan_error is not None:
        record.attempts.append(f"pool: {plan_error}")
    elif pool_path is None:
        record.attempts.append(
            f"pool: no artifact for backend {resolved_backend!r} "
            "(universal/<backend>/neural_<backend>.tcm)"
        )
    else:
        blocks = _pool_blockers(plan, ops, pool_path)
        if blocks:
            record.attempts.extend(f"pool: {item}" for item in blocks)
        else:
            record.status = "resolved"
            record.strategy = "pool"
            record.artifact = str(pool_path)
            record.reasons.append(
                f"all {len(ops)} operators are admitted by the universal registry "
                f"and every artifact-declared kernel is present "
                f"({len(pool_graph_names(pool_path))} graphs)"
            )
            return Resolution(
                strategy="pool",
                backend=resolved_backend,
                record=record,
                artifact=pool_path,
                graph_model_bytes=model_bytes,
                model_name=model_name,
            )

    # --- strategy 2: resident per-model artifact ------------------------
    resident = find_prebaked_artifact(model_name, resolved_backend, asset_dir)
    if resident is not None:
        record.status = "resolved"
        record.strategy = "resident"
        record.artifact = str(resident)
        record.reasons.append(
            "a pre-baked per-model TCM matched this graph and backend"
        )
        return Resolution(
            strategy="resident",
            backend=resolved_backend,
            record=record,
            artifact=resident,
            graph_model_bytes=model_bytes,
            model_name=model_name,
        )
    record.attempts.append(
        f"resident: no pre-baked artifact named {model_name}_{resolved_backend}.tcm"
    )

    # --- strategy 3: native per-model graph ----------------------------
    if ops is not None:
        unsupported = sorted(ops - NATIVE_GRAPH_OPS)
        if not unsupported:
            record.status = "resolved"
            record.strategy = "native"
            record.reasons.append(
                f"all {len(ops)} operators are covered by the native graph lowering"
            )
            return Resolution(
                strategy="native",
                backend=resolved_backend,
                record=record,
                graph_model_bytes=model_bytes,
                model_name=model_name,
            )
        record.attempts.append(
            f"native: {len(unsupported)} operators outside NativeGraph.OPS "
            f"(e.g. {unsupported[:6]})"
        )
    else:
        record.attempts.append("native: graph could not be validated")

    missing_features: List[str] = []
    if pool_path is not None and not int64_candidate_enabled(pool_path) and plan is not None:
        i64_ops = _int64_uncovered(_device_i64_ops(plan, ops or set()))
        if i64_ops:
            missing_features.append(
                "int64 support (no native implementation for: "
                + ", ".join(sorted(i64_ops)) + ")"
            )
    if resolved_backend != "cpu":
        missing_features.append(f"pool artifact for backend {resolved_backend!r}")

    record.missing_ops = tuple(sorted((ops or set()) - NATIVE_GRAPH_OPS)) if ops else ()
    record.missing_features = tuple(missing_features)
    record.reasons.append("no execution strategy covers this graph")

    raise CapabilityMissingError(
        model_name,
        missing_ops=record.missing_ops,
        missing_features=record.missing_features,
        attempts=[*record.attempts, f"backend={resolved_backend}"],
        remedy=(
            "compile/enable the INT64 candidate pool for this backend "
            "(see taichi_vision/documentation/NEURAL_ONNX_BLOCKERS.md) "
            "or select a backend whose pool artifact is qualified"
        ),
    )


def _pool_blockers(plan: Any, ops: Optional[Set[str]], pool_path: Path) -> List[str]:
    """Reasons the universal pool cannot run this graph right now."""
    from ..taichi_algorithm.neural.universal.kernels import KERNEL_NAMES

    blockers: List[str] = []
    try:
        graphs = pool_graph_names(pool_path)
    except Exception as exc:  # noqa: BLE001
        return [f"artifact manifest unreadable: {type(exc).__name__}: {exc}"]

    missing_kernels = sorted(set(KERNEL_NAMES) - graphs)
    if missing_kernels:
        blockers.append(
            f"staged artifact lacks {len(missing_kernels)} declared kernels "
            f"(e.g. {missing_kernels[:4]})"
        )

    if plan is not None:
        i64_ops = _device_i64_ops(plan, ops or set())
        if i64_ops and not int64_candidate_enabled(pool_path):
            # The native INT64 surface covers most of these without the artifact.
            uncovered = _int64_uncovered(i64_ops)
            if uncovered:
                blockers.append(
                    "dynamic INT64 device tensors need an enabled candidate pool "
                    f"(no native implementation for: {sorted(uncovered)})"
                )
    return blockers


__all__ = [
    "Resolution",
    "ResolutionRecord",
    "resolve",
    "resolve_backend",
    "CapabilityMissingError",
    "BackendUnavailable",
    "ModelNotRunnable",
]
