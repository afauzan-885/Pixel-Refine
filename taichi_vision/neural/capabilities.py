"""Capability registry for the public neural facade.

Declares, per execution strategy, which operators it can run, which runtime
features it requires, and how to probe availability. Probes are import-safe:
they never initialize a Taichi device, so ``import taichi_vision.neural`` stays
side-effect free.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

#: Default asset root for neural artifacts, mirroring the internal runtime.
DEFAULT_NEURAL_DIR = Path("pixel_refine_desktop/ui/data/aot_assets/neural")

#: Backend -> asset subdirectory used by the pool resolver.
POOL_BACKEND_SUBDIRS = {"cuda": "nvidia", "vulkan": "vulkan", "opengl": "opengl", "cpu": "cpu"}

#: Operators the native per-model graph lowering admits (NativeGraph.OPS).
NATIVE_GRAPH_OPS: FrozenSet[str] = frozenset({
    "Conv", "DmlFusedConv", "FusedConv", "Relu", "Sigmoid", "Softplus", "Gelu",
    "Abs", "Sqrt", "Tanh", "Clip", "Add", "Sub", "Mul", "Div", "Pow",
    "AveragePool", "SpaceToDepth", "Reshape", "Identity", "Concat",
    "Slice", "ReduceMean", "ConvTranspose", "Transpose", "Split", "Constant",
})

#: Operators whose lowering needs the isolated INT64 candidate pool.
INT64_CANDIDATE_OPS: FrozenSet[str] = frozenset({
    "Transpose", "Expand", "Concat", "Split", "Slice", "Gather", "GatherElements",
    "TopK", "NonZero", "Add", "Sub", "Mul", "Div", "Mod", "Where", "ArgMax",
    "Cast", "Range", "ConstantOfShape", "Less", "Greater", "Equal",
    "ReduceMean", "ReduceSum", "ReduceMax", "ReduceMin", "ReduceL2",
    "AveragePool", "MaxPool", "GlobalAveragePool",
    "InstanceNormalization", "LayerNormalization", "BatchNormalization",
    "Softmax", "LogSoftmax", "Conv", "ConvTranspose", "MatMul", "Gemm",
    "FusedMatMul", "PRelu", "Clip", "Resize",
})


@dataclass
class Strategy:
    """One execution strategy the resolver may pick."""

    name: str
    provider: str
    ops: Optional[FrozenSet[str]] = None
    requires: Tuple[str, ...] = ()
    description: str = ""


STRATEGIES: Tuple[Strategy, ...] = (
    Strategy(
        name="pool",
        provider="TaichiPool",
        ops=None,  # decided by the operator registry, not a static list
        requires=("pool_artifact",),
        description="Universal kernel pool: one compiled TCM serves any model "
                    "whose operators are in the registry.",
    ),
    Strategy(
        name="resident",
        provider="TaichiResident",
        ops=None,
        requires=("resident_artifact",),
        description="Per-model resident TCM artifact pre-baked for this graph.",
    ),
    Strategy(
        name="native",
        provider="TaichiNative",
        ops=NATIVE_GRAPH_OPS,
        requires=(),
        description="Native JIT/AOT per-model graph lowering (limited operator set).",
    ),
)


# ---------------------------------------------------------------------------
# artifact helpers (public; replace application imports of internal modules)
# ---------------------------------------------------------------------------


def neural_asset_dir(base: Optional[Path] = None) -> Path:
    """Resolve the neural artifact root, honouring the pool override env var."""
    if base is not None:
        return Path(base)
    override = os.environ.get("PIXEL_REFINE_NEURAL_POOL_DIR", "").strip()
    if override:
        return Path(override)
    return DEFAULT_NEURAL_DIR


def pool_artifact_path(backend: str, base: Optional[Path] = None) -> Optional[Path]:
    """Target-qualified universal pool TCM path, or ``None`` when absent."""
    root = neural_asset_dir(base)
    subdir = POOL_BACKEND_SUBDIRS.get(backend, backend)
    filename = f"neural_{backend}.tcm"
    for candidate in (
        root / filename,
        root / "universal" / subdir / filename,
        root / subdir / filename,
    ):
        if candidate.is_file():
            return candidate.resolve()
    return None


def find_prebaked_artifact(stem: str, backend: str, base: Optional[Path] = None) -> Optional[Path]:
    """Locate a pre-baked ``{stem}_{backend}.tcm`` artifact, if one exists."""
    root = neural_asset_dir(base)
    for candidate in (
        root / f"{stem}_{backend}.tcm",
        root / "universal" / POOL_BACKEND_SUBDIRS.get(backend, backend) / f"{stem}_{backend}.tcm",
    ):
        if candidate.is_file():
            return candidate.resolve()
    return None


def pool_graph_names(path: Path) -> FrozenSet[str]:
    """Read the ``cgraph:`` manifest of a pool TCM without loading a device."""
    import zipfile

    with zipfile.ZipFile(path) as archive:
        content = archive.read("__content__").decode("utf-8", errors="replace")
    return frozenset(
        line.split(":", 1)[1].strip()
        for line in content.splitlines()
        if line.startswith("cgraph:")
    )


def int64_candidate_enabled(pool_path: Optional[Path]) -> bool:
    """Whether a candidate manifest sits next to ``pool_path`` and declares INT64.

    Full validation happens inside the runtime session (source fingerprint, target
    identity, sha256). Here we only report a conservative, import-safe hint so
    ``capabilities()`` never claims more than the artifact states.
    """
    if pool_path is None:
        return False
    marker = Path(pool_path).parent / "candidate_manifest.json"
    if not marker.is_file():
        return False
    try:
        import json

        candidate = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return bool(candidate.get("graphs")) and candidate.get("backend") == "cpu"


# ---------------------------------------------------------------------------
# public capability summary
# ---------------------------------------------------------------------------


def capabilities(backend: str = "cpu", base: Optional[Path] = None) -> Dict[str, object]:
    """Report what the neural runtime can run right now, without a device."""
    from ..taichi_algorithm.neural.universal import registry

    pool_path = pool_artifact_path(backend, base)
    graphs: FrozenSet[str] = frozenset()
    if pool_path is not None:
        try:
            graphs = pool_graph_names(pool_path)
        except Exception:  # noqa: BLE001 - a broken artifact is reported, not raised
            graphs = frozenset()

    from ..taichi_algorithm.neural.universal.kernels import KERNEL_NAMES

    missing_kernels = sorted(set(KERNEL_NAMES) - graphs) if graphs else []
    int64_ready = int64_candidate_enabled(pool_path)

    strategies = []
    for strategy in STRATEGIES:
        strategies.append({
            "name": strategy.name,
            "provider": strategy.provider,
            "description": strategy.description,
            "available": _strategy_available(strategy.name, pool_path) is None,
        })

    return {
        "backend": backend,
        "pool_artifact": str(pool_path) if pool_path else None,
        "pool_graphs": len(graphs),
        "pool_missing_kernels": missing_kernels,
        "int64_candidate": int64_ready,
        "registry_operators": len(registry.OPS),
        "native_operators": len(NATIVE_GRAPH_OPS),
        "strategies": strategies,
        "blockers": _blockers(backend, pool_path, missing_kernels, int64_ready),
    }


def _strategy_available(name: str, pool_path: Optional[Path]) -> Optional[str]:
    """``None`` when available, else a one-line reason."""
    if name == "pool":
        return None if pool_path is not None else "no pool artifact for this backend"
    if name == "resident":
        return None  # per-model artifacts are resolved against the graph itself
    if name == "native":
        return None
    return f"unknown strategy {name!r}"


def _blockers(
    backend: str,
    pool_path: Optional[Path],
    missing_kernels: Sequence[str],
    int64_ready: bool,
) -> List[str]:
    blockers: List[str] = []
    if pool_path is None:
        blockers.append(
            f"B4/backend: no pool artifact for backend {backend!r} "
            "(only the CPU pool is staged today)"
        )
    elif missing_kernels:
        blockers.append(
            "B2/kernels: staged pool is missing declared kernels "
            f"({len(missing_kernels)} total, e.g. {list(missing_kernels[:5])})"
        )
    if pool_path is not None and not int64_ready:
        blockers.append(
            "B1/int64: dynamic INT64 device tensors are refused because no valid "
            "candidate manifest is enabled; models using TopK/GatherElements/"
            "Transpose on int64 values cannot run (see NEURAL_ONNX_BLOCKERS.md)"
        )
    return blockers


__all__ = [
    "DEFAULT_NEURAL_DIR",
    "POOL_BACKEND_SUBDIRS",
    "NATIVE_GRAPH_OPS",
    "INT64_CANDIDATE_OPS",
    "Strategy",
    "STRATEGIES",
    "neural_asset_dir",
    "pool_artifact_path",
    "find_prebaked_artifact",
    "pool_graph_names",
    "int64_candidate_enabled",
    "capabilities",
]
