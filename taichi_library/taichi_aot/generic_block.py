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

import numpy as np

from .block import BlockGrid, BlockRecord, BlockSpec, BlockState, BlockSize, checksum


BlockInputs = Tuple[np.ndarray, ...]
TileRunner = Callable[["BlockTileContext"], Any]
TileReader = Callable[[BlockSpec, BlockInputs], BlockInputs]
TileValidator = Callable[[Any, "BlockTileContext"], bool]
TileMerger = Callable[[Any, Any, "BlockTileContext"], None]
FullFrameRunner = Callable[[BlockInputs], Any]


class BlockPlanUnavailable(RuntimeError):
    """Raised when a caller requested an error instead of a fallback."""


class BlockExecutionError(RuntimeError):
    """Raised after a custom tile failed and no recovery was requested."""


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

    def _plan(self, spec: BlockComputeSpec, grid_shape, nbytes):
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
        return tuple(np.ascontiguousarray(array[block.read_slice]) for array in arrays)

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
            "output_shape": spec.output_shape,
            "output_dtype": np.dtype(spec.output_dtype).str if spec.output_dtype is not None else None,
            "grid_shape": spec.grid_shape,
            "halo": int(spec.halo),
            "tile_includes_halo": bool(spec.tile_includes_halo),
            "infer_output_shape": bool(spec.infer_output_shape),
            "input_signature": tuple(
                (tuple(array.shape), array.dtype.str) for array in (inputs or ())
            ),
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
        report = GenericBlockReport(
            spec.name, bool(selected), int(block_count), int(cache_hits),
            int(computed), int(retries), fallback, bool(quarantined), str(reason),
        )
        return GenericBlockResult(value, report) if return_report else value

    def run(self, inputs: Sequence[np.ndarray], spec: BlockComputeSpec, *, return_report=False):
        if not isinstance(spec, BlockComputeSpec):
            raise TypeError("spec must be a BlockComputeSpec")
        arrays = tuple(np.ascontiguousarray(value) for value in inputs)
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
            )

        result = None
        cache_hits = computed = retry_count = 0
        # A block cache entry is valid only when the source frame is the same.
        # Fingerprinting each tile repeatedly made the generic executor spend
        # O(number_of_tiles * frame_bytes) in CRC work.  A full-frame source
        # fingerprint is conservative and correct: any changed pixel causes
        # all tiles for that invocation to be recomputed.
        frame_source_checksum = tuple(_payload_checksum(array) for array in arrays)
        blocks = list(grid)
        cache = self.runtime.get_block_cache() if spec.cache else None
        # Cached-first ordering reduces residency churn for ordinary image
        # stitching.  Custom mergers may be order-sensitive (keypoint lists,
        # feature matches, or reductions), so preserve scanline order there.
        if cache is not None and spec.merge_tile is None and spec.output_shape is not None:
            blocks.sort(
                key=lambda block: (
                    cache.peek(self._cache_id(spec, block, arrays)) is None,
                    block.index,
                )
            )
        else:
            blocks.sort(key=lambda block: block.index)

        reader = spec.input_reader or self._default_reader
        for block in blocks:
            tile_inputs = tuple(np.ascontiguousarray(value) for value in reader(block, arrays))
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
            block_id = self._cache_id(spec, block, arrays)
            cached = self._cached(spec, block, context, block_id)
            if cached is not None:
                if result is None:
                    result = self._make_result(spec, cached.data)
                merger = spec.merge_tile or (lambda out, payload, ctx: self._default_merge(out, payload, ctx, spec))
                merger(result, cached.data, context)
                cache_hits += 1
                continue

            last_error = None
            payload = None
            attempts = max(1, int(spec.retries) + 1)
            for attempt in range(attempts):
                try:
                    payload = spec.run_tile(context)
                    validator = spec.validate_tile or (lambda value, ctx: self._default_validate(value, ctx, spec))
                    if not validator(payload, context):
                        raise ValueError(f"{spec.name} tile validation failed")
                    if result is None:
                        result = self._make_result(spec, payload)
                    if spec.cache:
                        self.runtime.put_block_record(
                            BlockRecord(
                                block_id,
                                state=BlockState.READY,
                                data=_copy_payload(payload),
                                checksum=_payload_checksum(payload),
                                source_checksum=source_checksum,
                                owner=spec.name,
                            )
                        )
                    merger = spec.merge_tile or (lambda out, value, ctx: self._default_merge(out, value, ctx, spec))
                    merger(result, payload, context)
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
                )

        report = GenericBlockReport(
            spec.name, True, len(blocks), cache_hits, computed, retry_count,
            "none", False, "generic block execution completed",
        )
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
]
