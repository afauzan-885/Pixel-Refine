"""Backend-neutral generic block computation.

The native algorithm wrappers keep their conservative capability table, but a
new algorithm should not have to become part of that table just to experiment
with tiles.  This module exposes an explicit, dependency-injected contract:
the caller describes how to read a tile, execute it, validate it, and merge it
back into the result.  The engine still owns memory planning, cache tiers,
checksums, retry, quarantine, and same-backend full-frame recovery.

The public entry point is :func:`run_generic_blocks`.  It is intentionally
agnostic about optical flow, feature matching, image filters, or AOT graph
names.  A custom algorithm can return an image tile, multiple arrays, or an
arbitrary payload when it supplies ``output_factory`` and ``merge_tile``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import blake2b
from typing import Any, Callable, Mapping, Optional, Sequence, Tuple
import copy
import time

import numpy as np

from .block import (
    BlockAdapter,
    BlockGrid,
    BlockRecord,
    BlockSpec,
    BlockState,
    BlockSize,
    can_partition_block,
    canonical_operation_name,
    checksum,
)


BlockInputs = Tuple[np.ndarray, ...]
TileRunner = Callable[["BlockTileContext"], Any]
TileReader = Callable[[BlockSpec, BlockInputs], BlockInputs]
TileValidator = Callable[[Any, "BlockTileContext"], bool]
TileMerger = Callable[[Any, Any, "BlockTileContext"], None]
FullFrameRunner = Callable[[BlockInputs], Any]


def _runtime_backend_name(runtime: Any) -> str:
    """Return a conservative canonical backend name for an engine-like object.

    The generic executor is also used by backend-free tests and embedders.  A
    missing ``arch`` therefore means the portable CPU contract, while an
    unknown value is deliberately kept unknown rather than guessed from a
    device ordinal.
    """

    value = getattr(runtime, "arch", None)
    if value is None:
        value = getattr(runtime, "backend", None)
    text = str(value or "cpu").strip().lower()
    if "vulkan" in text:
        return "vulkan"
    if "opengl" in text or "gles" in text:
        return "opengl"
    if "cuda" in text:
        return "cuda"
    if "cpu" in text or text in {"x64", "x86_64", "host"}:
        return "cpu"
    return text


def _adapter_device_name(runtime: Any, explicit: Any = None) -> Optional[str]:
    """Resolve an exact device identity for optional native-evidence checks."""

    if explicit is not None:
        return str(explicit)
    for attribute in ("gpu_name", "device_name", "renderer", "device_id"):
        value = getattr(runtime, attribute, None)
        if value not in (None, ""):
            return str(value)
    return None


def _coerce_registered_adapter(operation: str, adapter: Any = None) -> Optional[BlockAdapter]:
    """Resolve a registry adapter without mutating global capability tables."""

    from .block import canonical_operation_name, lookup_block_adapter

    canonical = canonical_operation_name(operation)
    if isinstance(adapter, BlockAdapter):
        return adapter if adapter.operation == canonical else None
    if adapter is None:
        return lookup_block_adapter(canonical)
    # A string is a convenient additive spelling for an explicitly selected
    # registry entry (``adapter="registered"`` or an alias).  It never
    # broadens automatic selection for an unknown operation.
    if isinstance(adapter, str):
        token = adapter.strip().lower()
        if token in {"", "auto", "registered", "registry"}:
            return lookup_block_adapter(canonical)
        return lookup_block_adapter(canonical_operation_name(adapter))
    return None


def _adapter_native_evidence_ok(
    operation: str,
    backend: str,
    runtime: Any,
    *,
    require_native_evidence: bool,
    device: Any = None,
) -> bool:
    """Check exact command-backed native evidence when the caller requests it."""

    if not require_native_evidence:
        return True
    try:
        from .native_evidence import native_partition_evidence_supported

        return bool(
            native_partition_evidence_supported(
                operation,
                backend,
                _adapter_device_name(runtime, device),
            )
        )
    except Exception:
        # Evidence is a safety gate, not a reason to infer support from an
        # artifact, semantic adapter, or successful import.
        return False


def _adapter_plan_block_size(
    operation: str,
    arrays: BlockInputs,
    runtime: Any,
    *,
    mode: str,
    automatic: bool,
    min_halo: int,
    block_size: Optional[BlockSize],
    threshold_bytes: Optional[int],
    halo: int,
) -> Optional[BlockSize]:
    """Ask the existing memory planner for an adapter tile size.

    This is intentionally a selection helper only.  It does not allocate a
    second cache or replace the engine planner.  Returning ``None`` in auto
    mode keeps the established same-backend full-frame fallback semantics.
    """

    shape = tuple(int(value) for value in arrays[0].shape[:2])
    nbytes = sum(int(getattr(value, "nbytes", 0) or 0) for value in arrays)
    planner = getattr(runtime, "plan_generic_blocks", None)
    if callable(planner):
        try:
            grid = planner(
                operation,
                shape,
                nbytes,
                halo=int(halo),
                mode=mode,
                automatic=bool(automatic),
                min_halo=int(min_halo),
                block_size=block_size,
                threshold_bytes=threshold_bytes,
            )
        except Exception:
            return None
        if grid is None:
            return None
        height = getattr(grid, "block_height", None)
        width = getattr(grid, "block_width", None)
        if height is not None and width is not None:
            return (int(height), int(width))
        return None
    if block_size is not None:
        return block_size
    if str(mode).lower().strip() == "force":
        return 512
    return None


def run_registered_block_adapter(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    runtime: Any = None,
    adapter: Any = None,
    block_size: Optional[BlockSize] = None,
    params: Optional[Mapping[str, Any]] = None,
    mode: str = "auto",
    automatic: bool = True,
    min_halo: int = 0,
    threshold_bytes: Optional[int] = None,
    halo: int = 0,
    require_native_evidence: bool = False,
    native_evidence_device: Any = None,
) -> Any:
    """Dispatch a decorated call through a registered semantic adapter.

    This bridge is additive and deliberately independent of the legacy native
    capability table.  ``mode='auto'`` requires a complete, backend-qualified
    adapter contract; ``mode='force'`` still requires explicit backend
    capability, but may be used for a controlled custom experiment.  Native
    evidence is an additional exact backend/device gate when requested.

    Adapter callbacks are owned by ``block_adapters``.  Their custom executor
    or deterministic adapter harness is invoked as one operation, preserving
    the adapter's own coordinate/reduction semantics.  Any selection or
    execution error is surfaced to the caller so the decorator can invoke its
    original same-backend full-frame function.
    """

    if runtime is None:
        # Do not eagerly import the native engine for a rejected adapter.  The
        # caller may supply a backend-free test runtime or explicit custom
        # adapter; absent runtime is treated as the portable CPU profile.
        try:
            from .engine import engine as runtime
        except Exception:
            runtime = None
    backend = _runtime_backend_name(runtime)
    canonical = canonical_operation_name(operation)
    custom_executor = None
    if callable(adapter) and not isinstance(adapter, BlockAdapter):
        # A callable custom executor is intentionally limited to explicit
        # ``force`` CPU experiments.  Without a target-qualified adapter
        # capability it cannot safely claim execution on a graphics backend.
        if str(mode).lower().strip() != "force" or backend != "cpu":
            raise BlockPlanUnavailable(
                f"custom adapter {canonical!r} requires explicit force CPU mode"
            )
        custom_executor = adapter
        selected = None
    else:
        selected = _coerce_registered_adapter(canonical, adapter)
    if selected is None and custom_executor is None:
        # Explicit adapter/operation selection opts into the maintained
        # registry.  Registration is lazy so ordinary generic calls and
        # diagnostics retain their previous import-time behaviour.
        try:
            from .block_adapters import ensure_default_block_adapters

            selected = ensure_default_block_adapters(canonical)
        except Exception:
            selected = None
    if selected is None and custom_executor is None:
        raise BlockPlanUnavailable(
            f"no registered block adapter for operation {canonical!r}"
        )
    if selected is not None and not selected.partition_ready:
        raise BlockPlanUnavailable(
            f"registered adapter {canonical!r} is incomplete"
        )
    if selected is not None and not selected.supports_backend(backend):
        raise BlockPlanUnavailable(
            f"adapter {canonical!r} has no parity-qualified {backend} capability"
        )
    contract = None if selected is None else selected.contract
    if selected is not None and str(mode).lower().strip() == "auto":
        from .block import can_partition_block

        if contract is None or not can_partition_block(
            canonical,
            backend,
            adapter=selected,
            contract=contract,
            require_adapter=True,
        ):
            raise BlockPlanUnavailable(
                f"adapter {canonical!r} is not eligible for automatic partitioning"
            )
    if not _adapter_native_evidence_ok(
        canonical,
        backend,
        runtime,
        require_native_evidence=bool(require_native_evidence),
        device=native_evidence_device,
    ):
        raise BlockPlanUnavailable(
            f"native evidence is unavailable for {canonical!r} on {backend}"
        )
    arrays = tuple(_as_contiguous(value) for value in inputs)
    if not arrays:
        raise BlockPlanUnavailable("registered adapter requires at least one input")
    tile_size = _adapter_plan_block_size(
        canonical,
        arrays,
        runtime,
        mode=str(mode).lower().strip(),
        automatic=bool(automatic),
        min_halo=int(min_halo),
        block_size=block_size,
        threshold_bytes=threshold_bytes,
        halo=int(halo),
    )
    if tile_size is None:
        raise BlockPlanUnavailable(
            f"memory planner selected full-frame for adapter {canonical!r}"
        )
    values = dict(params or {})
    if selected is not None:
        custom_executor = selected.metadata.get("custom_executor")
    if callable(custom_executor):
        result = custom_executor(
            canonical,
            arrays,
            block_size=tile_size,
            params=values,
        )
    else:
        # Keep the maintained adapter protocol (including output-domain and
        # map/reduce stages) in its owning module instead of translating
        # PartitionContext into the lower-level GenericBlockContext.
        from .block_adapters import run_adapter_tiled

        result = run_adapter_tiled(
            canonical,
            arrays,
            block_size=tile_size,
            params=values,
        )
    setter = getattr(runtime, "set_last_block_execution", None)
    if callable(setter):
        try:
            setter(
                {
                    "operation": canonical,
                    "selected": True,
                    "adapter": True,
                    "backend": backend,
                    "block_size": tuple(int(value) for value in tile_size)
                    if isinstance(tile_size, (tuple, list))
                    else int(tile_size),
                    "native_evidence_required": bool(require_native_evidence),
                    "reason": "registered adapter executed",
                }
            )
        except Exception:
            pass
    return result


class BlockPlanUnavailable(RuntimeError):
    """Raised when a caller requested an error instead of a fallback."""


class BlockExecutionError(RuntimeError):
    """Raised after a custom tile failed and no recovery was requested."""


def _as_contiguous(value: Any) -> np.ndarray:
    """Return a C-contiguous tile without re-normalizing an existing view."""
    if isinstance(value, np.ndarray) and value.flags.c_contiguous:
        return value
    return np.ascontiguousarray(value)


@dataclass(frozen=True)
class BlockTileContext:
    """Inputs and metadata for one custom tile invocation."""

    operation: str
    block: BlockSpec
    inputs: BlockInputs
    source_checksum: Any
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def core_slice(self):
        return self.block.core_slice

    @property
    def read_slice(self):
        return self.block.read_slice

    @property
    def output_slice(self):
        return self.block.write_slice


@dataclass(frozen=True)
class BlockComputeSpec:
    """Explicit policy and callbacks for one generic block operation.

    ``mode`` is deliberately local to this operation:

    * ``"auto"`` uses adaptive memory telemetry when ``automatic`` is true;
    * ``"force"`` selects a grid even when the native operation registry does
      not know the operation or the global block toggle is disabled;
    * ``"off"`` skips tiles and uses the selected fallback.

    A forced grid is still clamped by the engine's memory recommendation.  It
    is an opt-out from the *algorithm registry*, not an opt-out from OOM and
    lifecycle protection.
    """

    name: str
    run_tile: TileRunner
    output_shape: Optional[Tuple[int, ...]] = None
    output_dtype: Any = None
    grid_shape: Optional[Tuple[int, int]] = None
    halo: int = 0
    mode: str = "auto"
    automatic: bool = True
    min_halo: int = 0
    block_size: Optional[BlockSize] = None
    threshold_bytes: Optional[int] = None
    cache: bool = True
    cache_key: Optional[str] = None
    version: str = "v1"
    # Optional P3 contract.  Legacy generic callers may omit it; when a
    # contract is provided, automatic mode must prove the strict local
    # semantics while ``mode='force'`` remains an explicit caller decision.
    contract: Any = None
    retries: int = 1
    tile_includes_halo: bool = True
    infer_output_shape: bool = False
    input_reader: Optional[TileReader] = None
    validate_tile: Optional[TileValidator] = None
    output_factory: Optional[Callable[[], Any]] = None
    merge_tile: Optional[TileMerger] = None
    full_frame: Optional[FullFrameRunner] = None
    fallback: str = "return_none"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        name = str(self.name).strip()
        if not name:
            raise ValueError("generic block operation name must not be empty")
        if not callable(self.run_tile):
            raise TypeError("run_tile must be callable")
        object.__setattr__(self, "name", name)
        mode = str(self.mode).lower().strip()
        if mode not in {"auto", "force", "off"}:
            raise ValueError("block mode must be 'auto', 'force', or 'off'")
        object.__setattr__(self, "mode", mode)
        fallback = str(self.fallback).lower().strip()
        if fallback not in {"return_none", "full_frame", "error"}:
            raise ValueError(
                "fallback must be 'return_none', 'full_frame', or 'error'"
            )
        object.__setattr__(self, "fallback", fallback)
        if fallback == "full_frame" and self.full_frame is None:
            raise ValueError("fallback='full_frame' requires a full_frame callback")
        if int(self.halo) < 0 or int(self.min_halo) < 0:
            raise ValueError("halo and min_halo must be non-negative")
        if int(self.halo) < int(self.min_halo):
            raise ValueError("halo must be at least min_halo")
        if int(self.retries) < 0:
            raise ValueError("retries must be non-negative")
        if self.threshold_bytes is not None and int(self.threshold_bytes) < 0:
            raise ValueError("threshold_bytes must be non-negative")
        if self.output_shape is not None:
            shape = tuple(int(value) for value in self.output_shape)
            if len(shape) < 2 or any(value < 0 for value in shape):
                raise ValueError("output_shape must contain at least two dimensions")
            object.__setattr__(self, "output_shape", shape)
        if self.grid_shape is not None:
            grid_shape = tuple(int(value) for value in self.grid_shape)
            if len(grid_shape) != 2 or any(value < 0 for value in grid_shape):
                raise ValueError("grid_shape must be a non-negative (height, width)")
            object.__setattr__(self, "grid_shape", grid_shape)
        object.__setattr__(self, "metadata", dict(self.metadata or {}))
        if self.contract is None and "contract" in self.metadata:
            object.__setattr__(self, "contract", self.metadata.get("contract"))


@dataclass(frozen=True)
class GenericBlockReport:
    """Auditable result metadata returned with ``return_report=True``."""

    operation: str
    selected: bool
    block_count: int
    cache_hits: int = 0
    computed: int = 0
    retries: int = 0
    fallback: str = "none"
    quarantined: bool = False
    reason: str = ""
    elapsed_seconds: float = 0.0
    bytes_copied: int = 0
    cache_copy_bytes: int = 0
    checksum_seconds: float = 0.0
    reader_seconds: float = 0.0
    dispatch_seconds: float = 0.0
    merge_seconds: float = 0.0
    output_bytes: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "selected": self.selected,
            "block_count": self.block_count,
            "cache_hits": self.cache_hits,
            "computed": self.computed,
            "retries": self.retries,
            "fallback": self.fallback,
            "quarantined": self.quarantined,
            "reason": self.reason,
            "elapsed_seconds": self.elapsed_seconds,
            "bytes_copied": self.bytes_copied,
            "cache_copy_bytes": self.cache_copy_bytes,
            "checksum_seconds": self.checksum_seconds,
            "reader_seconds": self.reader_seconds,
            "dispatch_seconds": self.dispatch_seconds,
            "merge_seconds": self.merge_seconds,
            "output_bytes": self.output_bytes,
        }


@dataclass(frozen=True)
class GenericBlockResult:
    """Value plus report, used when ``return_report=True``."""

    value: Any
    report: GenericBlockReport


def _copy_payload(value: Any) -> Any:
    """Copy cache payloads without assuming an image-shaped result."""

    if isinstance(value, np.ndarray):
        return np.ascontiguousarray(value.copy())
    if isinstance(value, tuple):
        return tuple(_copy_payload(item) for item in value)
    if isinstance(value, list):
        return [_copy_payload(item) for item in value]
    if isinstance(value, dict):
        return {key: _copy_payload(item) for key, item in value.items()}
    try:
        return copy.deepcopy(value)
    except Exception:
        return value


def _payload_checksum(value: Any) -> Any:
    """Checksum arrays and deterministic arbitrary custom payloads."""

    if isinstance(value, np.ndarray):
        return checksum(value)
    if isinstance(value, tuple):
        return tuple(_payload_checksum(item) for item in value)
    if isinstance(value, list):
        return tuple(_payload_checksum(item) for item in value)
    if isinstance(value, dict):
        return tuple(
            (str(key), _payload_checksum(item))
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        )
    try:
        encoded = repr(value).encode("utf-8", errors="replace")
    except Exception:
        encoded = repr(type(value)).encode("utf-8")
    return blake2b(encoded, digest_size=16).hexdigest()


def _payload_nbytes(value: Any) -> int:
    """Return payload bytes for telemetry without forcing arbitrary copies."""

    if isinstance(value, np.ndarray):
        return int(value.nbytes)
    if isinstance(value, (tuple, list)):
        return sum(_payload_nbytes(item) for item in value)
    if isinstance(value, dict):
        return sum(_payload_nbytes(item) for item in value.values())
    return 0


def _stable_value(value: Any) -> Any:
    """Make metadata suitable for the deterministic block-id generator."""

    if isinstance(value, Mapping):
        return tuple(
            (str(key), _stable_value(item))
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        )
    if isinstance(value, (tuple, list)):
        return tuple(_stable_value(item) for item in value)
    if isinstance(value, np.dtype):
        return value.str
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    return repr(value)


class GenericBlockExecutor:
    """Execute a :class:`BlockComputeSpec` against an AOT engine-like object."""

    def __init__(self, runtime=None):
        if runtime is None:
            from .engine import engine as runtime  # lazy: tests need no native runtime
        self.runtime = runtime

    def _partition_contract_safe(self, spec: BlockComputeSpec) -> bool:
        """Check a rich partition contract for automatic generic execution.

        ``BlockComputeSpec`` already owns the callbacks required to handle
        coordinate transforms, reductions, or variable-cardinality payloads.
        Older versions only consulted ``OperationContract.can_auto_block``;
        that made every non-local contract fall back even when the caller had
        supplied a complete, backend-qualified adapter.  Build an ephemeral
        adapter from the spec so the existing fail-closed gate can validate
        the callbacks without registering global state or changing public
        APIs.  A missing contract or backend parity evidence remains a hard
        fallback to the same-backend full-frame path.
        """

        contract = spec.contract
        if contract is None or not getattr(contract, "allows_partitioned_block", False):
            return False

        def validator(payload, context):
            callback = spec.validate_tile
            if callback is not None:
                return bool(callback(payload, context))
            return self._default_validate(payload, context, spec)

        def merger(output, payload, context):
            callback = spec.merge_tile
            if callback is not None:
                callback(output, payload, context)
            else:
                self._default_merge(output, payload, context, spec)

        try:
            adapter = BlockAdapter(
                spec.name,
                reader=spec.input_reader,
                runner=spec.run_tile,
                validator=validator,
                merger=merger,
                contract=contract,
                metadata=spec.metadata,
                partition_strategy=getattr(contract, "partition_strategy", None),
                backend_capability=spec.metadata.get("backend_capability"),
            )
            backend = getattr(self.runtime, "arch", None)
            partition_safe = bool(
                can_partition_block(
                    spec.name,
                    backend,
                    adapter=adapter,
                    contract=contract,
                    require_adapter=True,
                )
            )
            if not partition_safe:
                return False
            # Semantic adapter parity is useful for development, but it is
            # not a native backend proof.  A caller that intends automatic
            # native dispatch can opt into this stricter check without
            # changing the historical generic-block API.
            if bool(
                spec.metadata.get(
                    "require_native_evidence",
                    spec.metadata.get("native_evidence_required", False),
                )
            ):
                from .native_evidence import native_partition_evidence_supported

                device = spec.metadata.get(
                    "native_evidence_device",
                    getattr(
                        self.runtime,
                        "gpu_name",
                        getattr(self.runtime, "device_name", None),
                    ),
                )
                if not native_partition_evidence_supported(
                    spec.name, str(backend or ""), device
                ):
                    return False
            return True
        except Exception:
            # Contract checks are a safety boundary.  A malformed adapter or
            # backend declaration must not enable automatic tiling.
            return False

    def _plan(self, spec: BlockComputeSpec, grid_shape, nbytes):
        contract = spec.contract
        if contract is not None and spec.mode == "auto":
            try:
                checker = getattr(contract, "can_auto_block", None)
                safe = bool(checker(getattr(self.runtime, "arch", None))) if callable(checker) else bool(
                    getattr(contract, "allows_automatic_block", False)
                )
                if not safe and not self._partition_contract_safe(spec):
                    return None
            except Exception:
                return None
        planner = getattr(self.runtime, "plan_generic_blocks", None)
        if planner is None:
            # Lightweight engines used by tests/embedders may not have the
            # extended planner yet.  Force mode remains deterministic; auto
            # mode stays fail-closed instead of consulting the native registry.
            if spec.mode != "force":
                return None
            return BlockGrid(
                grid_shape,
                size=spec.block_size or 512,
                halo=spec.halo,
            )
        return planner(
            spec.name,
            grid_shape,
            nbytes,
            halo=spec.halo,
            mode=spec.mode,
            automatic=spec.automatic,
            min_halo=spec.min_halo,
            block_size=spec.block_size,
            threshold_bytes=spec.threshold_bytes,
        )

    @staticmethod
    def _default_reader(block: BlockSpec, arrays: BlockInputs) -> BlockInputs:
        return tuple(_as_contiguous(array[block.read_slice]) for array in arrays)

    @staticmethod
    def _default_validate(payload: Any, context: BlockTileContext, spec: BlockComputeSpec) -> bool:
        if spec.output_shape is None and not spec.infer_output_shape:
            return True
        if not isinstance(payload, np.ndarray):
            return False
        expected = context.block.read_shape if spec.tile_includes_halo else context.block.shape
        return payload.ndim >= 2 and tuple(payload.shape[:2]) == tuple(expected)

    @staticmethod
    def _make_result(spec: BlockComputeSpec, payload: Any = None) -> Any:
        if spec.output_factory is not None:
            return spec.output_factory()
        if spec.output_shape is not None:
            dtype = spec.output_dtype
            if dtype is None and isinstance(payload, np.ndarray):
                dtype = payload.dtype
            return np.empty(spec.output_shape, dtype=np.dtype(dtype or np.float32))
        if spec.infer_output_shape:
            if not isinstance(payload, np.ndarray) or payload.ndim < 2:
                raise TypeError(
                    "infer_output_shape requires an image-like NumPy tile; "
                    "provide output_shape/output_factory for custom payloads"
                )
            if spec.grid_shape is None:
                raise ValueError("infer_output_shape requires grid_shape")
            trailing = tuple(int(value) for value in payload.shape[2:])
            return np.empty(
                tuple(int(value) for value in spec.grid_shape) + trailing,
                dtype=np.dtype(spec.output_dtype or payload.dtype),
            )
        # Variable-cardinality algorithms (e.g. keypoint extraction) can use
        # the default list and receive one payload per block.  A custom
        # ``merge_tile`` should normally be supplied for deterministic order.
        return []

    @staticmethod
    def _default_merge(result: Any, payload: Any, context: BlockTileContext, spec: BlockComputeSpec) -> None:
        if spec.output_shape is None:
            if spec.infer_output_shape:
                if not isinstance(result, np.ndarray) or not isinstance(payload, np.ndarray):
                    raise TypeError("inferred image output requires NumPy arrays")
                if spec.tile_includes_halo:
                    payload = payload[context.block.core_slice]
                result[context.block.write_slice] = payload
                return
            if isinstance(result, list):
                result.append(payload)
                return
            raise TypeError("output_shape=None requires output_factory/merge_tile")
        if not isinstance(payload, np.ndarray):
            raise TypeError("default image merge expects a NumPy tile")
        if spec.tile_includes_halo:
            payload = payload[context.block.core_slice]
        result[context.block.write_slice] = payload

    def _cache_id(
        self,
        spec: BlockComputeSpec,
        block: BlockSpec,
        inputs: Optional[BlockInputs] = None,
    ) -> str:
        params = {
            "metadata": _stable_value(spec.metadata),
            "contract": _stable_value(
                spec.contract.as_dict() if hasattr(spec.contract, "as_dict") else spec.contract
            ),
            "output_shape": spec.output_shape,
            "output_dtype": np.dtype(spec.output_dtype).str if spec.output_dtype is not None else None,
            "grid_shape": spec.grid_shape,
            "halo": int(spec.halo),
            "tile_includes_halo": bool(spec.tile_includes_halo),
            "infer_output_shape": bool(spec.infer_output_shape),
            "input_signature": tuple(
                (tuple(array.shape), array.dtype.str) for array in (inputs or ())
            ),
            # A block payload is not portable across backend/device/runtime
            # generations, even when the input shape and dtype match.
            "runtime_backend": str(getattr(self.runtime, "arch", "unknown")),
            "runtime_target": str(getattr(self.runtime, "target_id", "unknown")),
            "runtime_device": str(
                getattr(
                    self.runtime,
                    "gpu_name",
                    getattr(self.runtime, "device_id", "unknown"),
                )
            ),
            "runtime_generation": int(getattr(self.runtime, "_generation", 0) or 0),
        }
        return block.make_id(
            spec.cache_key or spec.name,
            spec.name,
            params=params,
            version=str(spec.version),
        )

    def _cached(self, spec, block, context, block_id):
        if not spec.cache:
            return None
        validator = spec.validate_tile or (
            lambda value, ctx: self._default_validate(value, ctx, spec)
        )
        cache = self.runtime.get_block_cache()
        record = cache.get(block_id)
        if record is not None:
            valid = False
            try:
                valid = bool(
                    record.is_valid()
                    and record.source_checksum == context.source_checksum
                    and _payload_checksum(record.data) == record.checksum
                )
                if valid:
                    valid = bool(validator(record.data, context))
            except Exception:
                valid = False
            if valid:
                return record
            cache.invalidate(block_id)

        restore = getattr(self.runtime, "restore_resident_block", None)
        if restore is None:
            return None
        record = restore(block_id, context.source_checksum)
        if record is None:
            return None
        valid = False
        try:
            valid = bool(
                record.is_valid()
                and _payload_checksum(record.data) == record.checksum
            )
            if valid:
                valid = bool(validator(record.data, context))
        except Exception:
            valid = False
        if not valid:
            try:
                self.runtime.get_device_block_cache().invalidate(block_id)
            except Exception:
                pass
            return None
        self.runtime.put_block_record(record)
        return record

    def _fallback(
        self,
        spec,
        arrays,
        *,
        selected,
        block_count,
        reason,
        cache_hits=0,
        computed=0,
        retries=0,
        quarantined=False,
        return_report=False,
        error_type=BlockPlanUnavailable,
        metrics=None,
    ):
        if spec.fallback == "full_frame" and spec.full_frame is not None:
            value = spec.full_frame(arrays)
            fallback = "full_frame"
        elif spec.fallback == "error":
            raise error_type(
                f"generic block operation {spec.name!r} was not executed: {reason}"
            )
        else:
            value = None
            fallback = "none"
        metric_values = dict(metrics or {})
        if fallback == "full_frame":
            metric_values["output_bytes"] = _payload_nbytes(value)
        report = GenericBlockReport(
            spec.name, bool(selected), int(block_count), int(cache_hits),
            int(computed), int(retries), fallback, bool(quarantined), str(reason),
            **metric_values,
        )
        setter = getattr(self.runtime, "set_last_block_execution", None)
        if callable(setter):
            try:
                setter(report.as_dict())
            except Exception:
                pass
        return GenericBlockResult(value, report) if return_report else value

    def run(self, inputs: Sequence[np.ndarray], spec: BlockComputeSpec, *, return_report=False):
        if not isinstance(spec, BlockComputeSpec):
            raise TypeError("spec must be a BlockComputeSpec")
        started = time.perf_counter()
        bytes_copied = 0
        arrays_list = []
        for value in inputs:
            normalized = _as_contiguous(value)
            if normalized is not value:
                bytes_copied += int(getattr(normalized, "nbytes", 0) or 0)
            arrays_list.append(normalized)
        arrays = tuple(arrays_list)
        if not arrays:
            raise ValueError("generic block computation requires at least one input")
        if any(array.ndim < 2 for array in arrays):
            raise ValueError("generic block inputs must have at least two dimensions")
        grid_shape = spec.grid_shape or (
            spec.output_shape[:2] if spec.output_shape is not None else arrays[0].shape[:2]
        )
        grid_shape = tuple(int(value) for value in grid_shape)
        if spec.input_reader is None and any(array.shape[:2] != grid_shape for array in arrays):
            raise ValueError(
                "default generic block reader requires inputs to match grid_shape; "
                "provide input_reader for custom coordinate mappings"
            )
        grid = self._plan(spec, grid_shape, sum(int(array.nbytes) for array in arrays))
        if grid is None:
            return self._fallback(
                spec, arrays, selected=False, block_count=0,
                reason="planner selected full-frame/off path", return_report=return_report,
                metrics={
                    "elapsed_seconds": time.perf_counter() - started,
                    "bytes_copied": bytes_copied,
                },
            )

        result = None
        cache_hits = computed = retry_count = 0
        checksum_seconds = reader_seconds = dispatch_seconds = merge_seconds = 0.0
        cache_copy_bytes = 0
        # A block cache entry is valid only when the source frame is the same.
        # Fingerprinting each tile repeatedly made the generic executor spend
        # O(number_of_tiles * frame_bytes) in CRC work.  A full-frame source
        # fingerprint is conservative and correct: any changed pixel causes
        # all tiles for that invocation to be recomputed.
        checksum_started = time.perf_counter()
        # A caller that owns an immutable frame/version counter may provide
        # ``metadata['source_version']``.  This avoids rereading a 50 MP frame
        # for every invocation while retaining the conservative CRC path for
        # ordinary callers.  The token is deliberately explicit; no implicit
        # object id is treated as a validity proof.
        source_version = spec.metadata.get("source_version")
        if spec.cache and source_version is not None:
            token = _stable_value(source_version)
            frame_source_checksum = ("version", token)
        else:
            frame_source_checksum = (
                tuple(_payload_checksum(array) for array in arrays)
                if spec.cache else None
            )
        checksum_seconds += time.perf_counter() - checksum_started
        blocks = list(grid)
        cache = self.runtime.get_block_cache() if spec.cache else None
        # Build IDs once: cached-first ordering previously derived each ID for
        # sorting and then derived it again during execution.
        planned_blocks = (
            [(block, self._cache_id(spec, block, arrays)) for block in blocks]
            if cache is not None else [(block, None) for block in blocks]
        )
        # Cached-first ordering reduces residency churn for ordinary image
        # stitching.  Custom mergers may be order-sensitive (keypoint lists,
        # feature matches, or reductions), so preserve scanline order there.
        if cache is not None and spec.merge_tile is None and spec.output_shape is not None:
            planned_blocks.sort(
                key=lambda item: (
                    cache.peek(item[1]) is None,
                    item[0].index,
                )
            )
        else:
            planned_blocks.sort(key=lambda item: item[0].index)

        reader = spec.input_reader or self._default_reader
        for block, block_id in planned_blocks:
            reader_started = time.perf_counter()
            raw_tile_inputs = reader(block, arrays)
            reader_seconds += time.perf_counter() - reader_started
            tile_inputs_list = []
            for value in raw_tile_inputs:
                normalized = _as_contiguous(value)
                if normalized is not value:
                    bytes_copied += int(getattr(normalized, "nbytes", 0) or 0)
                tile_inputs_list.append(normalized)
            tile_inputs = tuple(tile_inputs_list)
            if not tile_inputs:
                raise ValueError("input_reader must return at least one tile")
            source_checksum = frame_source_checksum
            context = BlockTileContext(
                operation=spec.name,
                block=block,
                inputs=tile_inputs,
                source_checksum=source_checksum,
                metadata=spec.metadata,
            )
            cached = self._cached(spec, block, context, block_id)
            if cached is not None:
                if result is None:
                    result = self._make_result(spec, cached.data)
                merger = spec.merge_tile or (lambda out, payload, ctx: self._default_merge(out, payload, ctx, spec))
                merge_started = time.perf_counter()
                merger(result, cached.data, context)
                merge_seconds += time.perf_counter() - merge_started
                cache_hits += 1
                continue

            last_error = None
            payload = None
            attempts = max(1, int(spec.retries) + 1)
            for attempt in range(attempts):
                try:
                    dispatch_started = time.perf_counter()
                    payload = spec.run_tile(context)
                    dispatch_seconds += time.perf_counter() - dispatch_started
                    validator = spec.validate_tile or (lambda value, ctx: self._default_validate(value, ctx, spec))
                    if not validator(payload, context):
                        raise ValueError(f"{spec.name} tile validation failed")
                    if result is None:
                        result = self._make_result(spec, payload)
                    if spec.cache:
                        cached_payload = _copy_payload(payload)
                        cache_copy_bytes += _payload_nbytes(cached_payload)
                        self.runtime.put_block_record(
                            BlockRecord(
                                block_id,
                                state=BlockState.READY,
                                data=cached_payload,
                                checksum=_payload_checksum(payload),
                                source_checksum=source_checksum,
                                owner=spec.name,
                            )
                        )
                    merger = spec.merge_tile or (lambda out, value, ctx: self._default_merge(out, value, ctx, spec))
                    merge_started = time.perf_counter()
                    merger(result, payload, context)
                    merge_seconds += time.perf_counter() - merge_started
                    computed += 1
                    retry_count += attempt
                    break
                except Exception as exc:
                    last_error = exc
            else:
                reason = f"block {block.index} failed after {attempts} attempt(s): {last_error}"
                try:
                    self.runtime.quarantine_block_operation(spec.name, reason)
                except Exception:
                    pass
                return self._fallback(
                    spec, arrays, selected=True, block_count=len(blocks),
                    reason=reason, cache_hits=cache_hits, computed=computed,
                    retries=retry_count, quarantined=True, return_report=return_report,
                    error_type=BlockExecutionError,
                    metrics={
                        "elapsed_seconds": time.perf_counter() - started,
                        "bytes_copied": bytes_copied,
                        "cache_copy_bytes": cache_copy_bytes,
                        "checksum_seconds": checksum_seconds,
                        "reader_seconds": reader_seconds,
                        "dispatch_seconds": dispatch_seconds,
                        "merge_seconds": merge_seconds,
                        "output_bytes": _payload_nbytes(result),
                    },
                )

        report = GenericBlockReport(
            spec.name, True, len(blocks), cache_hits, computed, retry_count,
            "none", False, "generic block execution completed",
            elapsed_seconds=time.perf_counter() - started,
            bytes_copied=bytes_copied,
            cache_copy_bytes=cache_copy_bytes,
            checksum_seconds=checksum_seconds,
            reader_seconds=reader_seconds,
            dispatch_seconds=dispatch_seconds,
            merge_seconds=merge_seconds,
            output_bytes=_payload_nbytes(result),
        )
        setter = getattr(self.runtime, "set_last_block_execution", None)
        if callable(setter):
            try:
                setter(report.as_dict())
            except Exception:
                pass
        return GenericBlockResult(result, report) if return_report else result


def run_generic_blocks(
    inputs: Sequence[np.ndarray],
    spec: BlockComputeSpec,
    *,
    runtime=None,
    return_report: bool = False,
):
    """Run an explicitly described custom block computation.

    This function does not consult ``OPERATION_CAPABILITIES``.  The supplied
    spec is the algorithm's local contract, while the engine still enforces
    adaptive block sizing, cache ownership, checksums, residency limits,
    retries, quarantine, and the caller-selected fallback.
    """

    return GenericBlockExecutor(runtime).run(
        inputs, spec, return_report=return_report
    )


__all__ = [
    "BlockComputeSpec",
    "BlockTileContext",
    "BlockPlanUnavailable",
    "BlockExecutionError",
    "GenericBlockExecutor",
    "GenericBlockReport",
    "GenericBlockResult",
    "run_generic_blocks",
    "run_registered_block_adapter",
]
