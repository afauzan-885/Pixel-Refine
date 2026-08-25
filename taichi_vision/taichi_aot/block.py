"""Internal block-processing primitives for the Taichi AOT runtime.

This module is intentionally independent from ``engine.py``.  It defines the
stable bookkeeping for GPU/CPU block transfers.  Only parity-qualified local
executors are eligible for automatic blocking; every other public algorithm
remains fail-closed on its full-frame path.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from hashlib import blake2b
from itertools import count
from types import MappingProxyType
from typing import Any, Callable, Iterator, Mapping, Optional, Sequence, Tuple, Union
import threading
import math
import zlib

import numpy as np


BlockSize = Union[int, Tuple[int, int]]


class ShapeTransform(str, Enum):
    """Shape semantics declared by an operation contract.

    ``SAME`` is deliberately the only shape class that can be selected by a
    conservative automatic block planner.  The other values are useful
    diagnostics and make shape-changing operations fail closed until a
    caller supplies a dedicated coordinate/merge contract.
    """

    SAME = "same"
    SAME_SHAPE = "same"  # backwards/wording-friendly alias
    CHANGING = "changing"
    SCALE = "scale"
    REDUCE = "reduce"
    EXPAND = "expand"
    VARIABLE = "variable"
    UNKNOWN = "unknown"


class PartitionStrategy(str, Enum):
    """How an operation is decomposed when a caller opts into block mode.

    ``OperationContract.allows_automatic_block`` remains the conservative
    same-shape/local gate used by the legacy planner.  This enum describes
    richer partition contracts without enabling any of them by itself.  A
    coordinate transform, reduction, multi-stage, iterative, or
    variable-cardinality operation needs an explicit :class:`BlockAdapter`
    with parity evidence before :func:`can_partition_block` can return true.
    """

    LOCAL = "local"
    STENCIL = "stencil"
    COORDINATE = "coordinate"
    MAP_REDUCE = "map_reduce"
    MULTI_STAGE = "multi_stage"
    ITERATIVE = "iterative"
    VARIABLE = "variable"


class HaloPolicy(str, Enum):
    """How a tile's read halo is defined."""

    NONE = "none"
    FIXED = "fixed"
    DYNAMIC = "dynamic"
    UNKNOWN = "unknown"


class BorderPolicy(str, Enum):
    """Border behaviour required when a halo reaches an image edge."""

    NONE = "none"
    CLAMP = "clamp"
    REFLECT = "reflect"
    CONSTANT = "constant"
    WRAP = "wrap"
    UNKNOWN = "unknown"


class ReductionPolicy(str, Enum):
    """Whether an operation requires a reduction across tiles."""

    NONE = "none"
    LOCAL = "local"
    GLOBAL = "global"
    UNKNOWN = "unknown"


class MergePolicy(str, Enum):
    """Output merge/cardinality semantics for a tiled operation."""

    FIXED = "fixed"
    OVERWRITE = "overwrite"
    REDUCE = "reduce"
    VARIABLE = "variable"
    CUSTOM = "custom"
    UNKNOWN = "unknown"


def _infer_partition_strategy(
    *,
    shape_transform: ShapeTransform,
    halo: int,
    halo_policy: HaloPolicy,
    reduction: ReductionPolicy,
    merge: MergePolicy,
    variable_cardinality: bool,
) -> PartitionStrategy:
    """Infer descriptive partition metadata without changing safety flags.

    The inference is intentionally descriptive only.  In particular, a
    ``COORDINATE`` or ``MAP_REDUCE`` classification does *not* make a
    contract block-safe; callers still need an explicit qualified adapter.
    """

    if shape_transform != ShapeTransform.SAME:
        return PartitionStrategy.COORDINATE
    if reduction in (ReductionPolicy.GLOBAL, ReductionPolicy.LOCAL):
        return PartitionStrategy.MAP_REDUCE
    if variable_cardinality or merge == MergePolicy.VARIABLE:
        return PartitionStrategy.VARIABLE
    if halo > 0 or halo_policy in (HaloPolicy.FIXED, HaloPolicy.DYNAMIC):
        return PartitionStrategy.STENCIL
    return PartitionStrategy.LOCAL


@dataclass(frozen=True)
class BackendCapability:
    """Backend-neutral capability and parity metadata.

    A missing backend entry is intentionally *not* treated as proof of
    support when ``require_parity`` is true.  ``"*"`` is the explicit way to
    say that a contract has been qualified for all backends represented by
    the application.
    """

    supported: Tuple[str, ...] = ("*",)
    parity_qualified: Tuple[str, ...] = ()
    same_backend_fallback: bool = True

    def __post_init__(self) -> None:
        supported = tuple(str(item).lower().strip() for item in self.supported if str(item).strip())
        parity = tuple(str(item).lower().strip() for item in self.parity_qualified if str(item).strip())
        object.__setattr__(self, "supported", supported or ("*",))
        object.__setattr__(self, "parity_qualified", parity)

    @classmethod
    def from_value(cls, value: Any) -> "BackendCapability":
        if isinstance(value, cls):
            return value
        if value is None:
            # No declaration is not evidence of backend parity.  Keep the
            # capability object inspectable but require an explicit contract
            # flag before automatic selection.
            return cls(supported=("*",), parity_qualified=())
        if isinstance(value, Mapping):
            supported = []
            parity = []
            for key, item in value.items():
                backend = str(key).lower().strip()
                if not backend:
                    continue
                if isinstance(item, Mapping):
                    enabled = bool(item.get("supported", item.get("available", False)))
                    qualified = bool(item.get("parity", item.get("parity_qualified", False)))
                else:
                    enabled = bool(item)
                    qualified = bool(item)
                if enabled:
                    supported.append(backend)
                if qualified:
                    parity.append(backend)
            return cls(tuple(supported), tuple(parity))
        if isinstance(value, str):
            return cls((value,), ())
        try:
            return cls(tuple(value), ())
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise TypeError("backend_capability must be a mapping or iterable") from exc

    def supports(self, backend: Optional[str] = None, *, require_parity: bool = True) -> bool:
        backend_name = str(backend or "").lower().strip()
        supported = "*" in self.supported or not backend_name or backend_name in self.supported
        if not supported:
            return False
        if not require_parity:
            return True
        return "*" in self.parity_qualified or not backend_name and bool(self.parity_qualified) or backend_name in self.parity_qualified


@dataclass(frozen=True)
class OperationContract:
    """Declarative, backend-neutral operation semantics (P3).

    The contract is metadata only; it does not execute a kernel.  Automatic
    native blocking is allowed only when the declaration is known, local,
    deterministic, parity-qualified, and free of reductions, side effects,
    or variable-cardinality merges.  Unknown/global/shape-changing contracts
    therefore fail closed without changing the legacy explicit APIs.
    """

    operation: str
    shape_transform: ShapeTransform | str = ShapeTransform.SAME
    input_coordinate_map: Any = "identity"
    halo: int = 0
    halo_policy: HaloPolicy | str = HaloPolicy.NONE
    border_policy: BorderPolicy | str = BorderPolicy.NONE
    reduction: ReductionPolicy | str = ReductionPolicy.NONE
    merge: MergePolicy | str = MergePolicy.FIXED
    variable_cardinality: bool = False
    deterministic: bool = True
    side_effect: bool = False
    side_effect_free: Optional[bool] = None
    scratch_bytes: int = 0
    backend_capability: BackendCapability | Mapping[str, Any] | None = None
    automatic_safe: bool = False
    parity_qualified: bool = False
    known: bool = True
    reason: str = ""
    # Rich partitioning is deliberately separate from the legacy
    # ``automatic_safe`` bit.  Setting this flag never changes
    # ``allows_automatic_block``; it only becomes actionable when a complete,
    # backend-qualified BlockAdapter is supplied to ``can_partition_block``.
    partition_strategy: PartitionStrategy | str | None = None
    partition_qualified: bool = False

    def __post_init__(self) -> None:
        name = str(self.operation).strip()
        if not name:
            raise ValueError("operation name must not be empty")
        object.__setattr__(self, "operation", name)
        for attr, enum_type, default in (
            ("shape_transform", ShapeTransform, ShapeTransform.UNKNOWN),
            ("halo_policy", HaloPolicy, HaloPolicy.UNKNOWN),
            ("border_policy", BorderPolicy, BorderPolicy.UNKNOWN),
            ("reduction", ReductionPolicy, ReductionPolicy.UNKNOWN),
            ("merge", MergePolicy, MergePolicy.UNKNOWN),
        ):
            value = getattr(self, attr)
            try:
                value = enum_type(value)
            except (TypeError, ValueError):
                value = default
            object.__setattr__(self, attr, value)
        strategy = self.partition_strategy
        if strategy is None:
            strategy = _infer_partition_strategy(
                shape_transform=self.shape_transform,
                halo=int(self.halo),
                halo_policy=self.halo_policy,
                reduction=self.reduction,
                merge=self.merge,
                variable_cardinality=bool(self.variable_cardinality),
            )
        else:
            try:
                strategy = PartitionStrategy(strategy)
            except (TypeError, ValueError):
                # Unknown strategies fail closed while retaining a stable,
                # inspectable value for diagnostics.
                strategy = None
        object.__setattr__(self, "partition_strategy", strategy)
        object.__setattr__(self, "partition_qualified", bool(self.partition_qualified))
        halo = int(self.halo)
        scratch = int(self.scratch_bytes)
        if halo < 0:
            raise ValueError("halo must be non-negative")
        if scratch < 0:
            raise ValueError("scratch_bytes must be non-negative")
        object.__setattr__(self, "halo", halo)
        object.__setattr__(self, "scratch_bytes", scratch)
        if self.side_effect_free is not None:
            object.__setattr__(self, "side_effect", not bool(self.side_effect_free))
        if self.backend_capability is None:
            capability = BackendCapability(
                supported=("*",),
                parity_qualified=("*",) if self.parity_qualified else (),
            )
        else:
            capability = BackendCapability.from_value(self.backend_capability)
        object.__setattr__(self, "backend_capability", capability)
        # A permissive caller cannot accidentally make an unsafe declaration
        # automatic: the safety bit is normalized from all contract fields.
        normalized_safe = bool(
            self.known
            and self.automatic_safe
            and self.parity_qualified
            and self.deterministic
            and not self.side_effect
            and not self.variable_cardinality
            and self.shape_transform == ShapeTransform.SAME
            and self.reduction == ReductionPolicy.NONE
            and self.merge in (MergePolicy.FIXED, MergePolicy.OVERWRITE)
            and self.halo_policy != HaloPolicy.UNKNOWN
            and self.border_policy != BorderPolicy.UNKNOWN
            and capability.supports(None, require_parity=True)
        )
        object.__setattr__(self, "automatic_safe", normalized_safe)

    @property
    def shape_changing(self) -> bool:
        return self.shape_transform != ShapeTransform.SAME

    @property
    def global_reduction(self) -> bool:
        return self.reduction in (ReductionPolicy.GLOBAL, ReductionPolicy.UNKNOWN)

    @property
    def allows_automatic_block(self) -> bool:
        return self.automatic_safe

    @property
    def allows_pipeline(self) -> bool:
        """Whether recording this operation is safe by metadata alone."""
        return bool(
            self.known
            and not self.shape_changing
            and not self.global_reduction
            and not self.variable_cardinality
            and not self.side_effect
            and self.merge not in (MergePolicy.VARIABLE, MergePolicy.UNKNOWN)
        )

    def supports_backend(self, backend: Optional[str] = None, *, require_parity: bool = True) -> bool:
        return self.backend_capability.supports(backend, require_parity=require_parity)

    def can_auto_block(self, backend: Optional[str] = None) -> bool:
        return bool(self.allows_automatic_block and self.supports_backend(backend, require_parity=True))

    @property
    def allows_partitioned_block(self) -> bool:
        """Whether an explicit adapter may partition this operation.

        This is intentionally broader than ``allows_automatic_block`` so a
        future coordinate/reduction/multi-stage adapter can carry its own
        reader and merger.  It is still opt-in: the default is false and the
        runtime gate additionally requires a complete adapter and backend
        parity evidence.
        """

        return bool(
            self.known
            and self.partition_qualified
            and self.deterministic
            and not self.side_effect
            and isinstance(self.partition_strategy, PartitionStrategy)
        )

    def can_partition(self, backend: Optional[str] = None) -> bool:
        """Check contract-local partition eligibility (adapter-independent)."""

        return bool(
            self.allows_partitioned_block
            and self.supports_backend(backend, require_parity=True)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "shape_transform": self.shape_transform.value,
            "input_coordinate_map": self.input_coordinate_map,
            "halo": self.halo,
            "halo_policy": self.halo_policy.value,
            "border_policy": self.border_policy.value,
            "reduction": self.reduction.value,
            "merge": self.merge.value,
            "variable_cardinality": self.variable_cardinality,
            "deterministic": self.deterministic,
            "side_effect": self.side_effect,
            "scratch_bytes": self.scratch_bytes,
            "backend_capability": {
                "supported": self.backend_capability.supported,
                "parity_qualified": self.backend_capability.parity_qualified,
                "same_backend_fallback": self.backend_capability.same_backend_fallback,
            },
            "automatic_safe": self.automatic_safe,
            "parity_qualified": self.parity_qualified,
            "known": self.known,
            "reason": self.reason,
            "partition_strategy": (
                self.partition_strategy.value
                if isinstance(self.partition_strategy, PartitionStrategy)
                else None
            ),
            "partition_qualified": self.partition_qualified,
            "allows_partitioned_block": self.allows_partitioned_block,
        }


class BlockPath(str, Enum):
    """How an operation can safely be evaluated."""

    DIRECT = "direct"
    BLOCK = "block"
    BLOCK_BORDER = "block_border"
    GLOBAL = "global"
    CUSTOM = "custom"


@dataclass(frozen=True)
class BlockCapability:
    """Dependency metadata used by the automatic block planner.

    ``explicit_safe`` intentionally describes the historical opt-in path, not
    a promise that every backend is bit-identical for that operation.  The
    automatic planner only uses ``automatic_safe`` and requires the declared
    halo.  This keeps experimental block implementations available to callers
    that explicitly opt in while preventing memory pressure from silently
    selecting an operation whose dependencies are not local.
    """

    operation: str
    path: BlockPath
    automatic_safe: bool = False
    explicit_safe: bool = False
    min_halo: int = 0
    dependencies: Tuple[str, ...] = ()
    reason: str = ""
    contract: Optional[OperationContract] = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not str(self.operation):
            raise ValueError("operation name must not be empty")
        if int(self.min_halo) < 0:
            raise ValueError("min_halo must be non-negative")
        if self.path == BlockPath.GLOBAL and self.explicit_safe:
            raise ValueError("global reductions cannot be block-explicit-safe")

    @property
    def contract_safe(self) -> bool:
        """Strict P3 gate, independent from legacy ``automatic_safe``."""
        return bool(self.contract is not None and self.contract.allows_automatic_block)


class BlockState(str, Enum):
    """Lifecycle states shared by cache and future GPU block pools."""

    EMPTY = "empty"
    LOADING = "loading"
    READY = "ready"
    PROCESSING = "processing"
    DONE = "done"
    DIRTY = "dirty"
    CORRUPT = "corrupt"
    RELEASED = "released"


@dataclass(frozen=True)
class BlockConfig:
    """Runtime policy. Disabled mode preserves today's full-frame behavior."""

    enabled: bool = False
    size: BlockSize = 512
    threshold_bytes: int = 512 * 1024 * 1024
    cache_entries: int = 64
    cache_bytes: Optional[int] = None
    adaptive_memory: bool = True
    device_cache_enabled: bool = True
    device_cache_bytes: int = 128 * 1024 * 1024

    def __post_init__(self) -> None:
        self.normalized_size()
        if int(self.threshold_bytes) < 0:
            raise ValueError("threshold_bytes must be non-negative")
        if int(self.cache_entries) < 1:
            raise ValueError("cache_entries must be positive")
        if self.cache_bytes is not None and int(self.cache_bytes) < 0:
            raise ValueError("cache_bytes must be non-negative or None")
        if int(self.device_cache_bytes) < 0:
            raise ValueError("device_cache_bytes must be non-negative")

    def normalized_size(self) -> Tuple[int, int]:
        return normalize_block_size(self.size)


@dataclass(frozen=True)
class BlockSpec:
    """One output block and the source region needed to calculate it."""

    index: int
    row: int
    column: int
    y0: int
    x0: int
    y1: int
    x1: int
    read_y0: int
    read_x0: int
    read_y1: int
    read_x1: int

    @property
    def shape(self) -> Tuple[int, int]:
        return self.y1 - self.y0, self.x1 - self.x0

    @property
    def read_shape(self) -> Tuple[int, int]:
        return self.read_y1 - self.read_y0, self.read_x1 - self.read_x0

    @property
    def write_slice(self) -> Tuple[slice, slice]:
        return slice(self.y0, self.y1), slice(self.x0, self.x1)

    @property
    def core_slice(self) -> Tuple[slice, slice]:
        """Output region relative to a source tile that includes the halo."""
        return (
            slice(self.y0 - self.read_y0, self.y1 - self.read_y0),
            slice(self.x0 - self.read_x0, self.x1 - self.read_x0),
        )

    @property
    def read_slice(self) -> Tuple[slice, slice]:
        return slice(self.read_y0, self.read_y1), slice(self.read_x0, self.read_x1)

    def make_id(
        self,
        source_id: str,
        operation: str,
        params: Optional[Mapping[str, Any]] = None,
        version: str = "v1",
    ) -> str:
        """Return a stable cache key for this block and operation."""
        params = params or {}
        encoded_params = repr(tuple(sorted((str(k), repr(v)) for k, v in params.items())))
        payload = "|".join(
            (
                str(source_id), operation, version, encoded_params,
                str(self.y0), str(self.x0), str(self.y1), str(self.x1),
                str(self.read_y0), str(self.read_x0), str(self.read_y1), str(self.read_x1),
            )
        ).encode("utf-8")
        return blake2b(payload, digest_size=16).hexdigest()


class BlockGrid:
    """Scanline iterator over a 2D image, with optional read halo."""

    def __init__(self, shape: Sequence[int], size: BlockSize = 512, halo: int = 0):
        if len(shape) < 2:
            raise ValueError("BlockGrid requires at least two dimensions")
        self.height, self.width = int(shape[0]), int(shape[1])
        if self.height < 0 or self.width < 0:
            raise ValueError("shape dimensions must be non-negative")
        self.block_height, self.block_width = normalize_block_size(size)
        if halo < 0:
            raise ValueError("halo must be non-negative")
        self.halo = int(halo)
        self.rows = (self.height + self.block_height - 1) // self.block_height
        self.columns = (self.width + self.block_width - 1) // self.block_width

    def __len__(self) -> int:
        return self.rows * self.columns

    def __iter__(self) -> Iterator[BlockSpec]:
        for row in range(self.rows):
            y0 = row * self.block_height
            y1 = min(y0 + self.block_height, self.height)
            for column in range(self.columns):
                x0 = column * self.block_width
                x1 = min(x0 + self.block_width, self.width)
                yield BlockSpec(
                    index=row * self.columns + column,
                    row=row,
                    column=column,
                    y0=y0,
                    x0=x0,
                    y1=y1,
                    x1=x1,
                    read_y0=max(0, y0 - self.halo),
                    read_x0=max(0, x0 - self.halo),
                    read_y1=min(self.height, y1 + self.halo),
                    read_x1=min(self.width, x1 + self.halo),
                )


@dataclass
class BlockRecord:
    """Cache metadata; ``data`` may be a CPU array or a GPU buffer later."""

    block_id: str
    state: BlockState = BlockState.EMPTY
    data: Any = None
    checksum: Optional[int] = None
    source_checksum: Any = None
    dirty: bool = False
    pinned: bool = False
    ref_count: int = 0
    generation: int = 0
    owner: str = "default"
    # Optional backend fence predicate.  A resident entry with a fence is not
    # evicted until the predicate reports completion; ordinary CPU records
    # leave it unset for backward compatibility.
    fence_ready: Any = None

    def is_valid(self) -> bool:
        return self.state not in (BlockState.CORRUPT, BlockState.RELEASED) and self.data is not None


class BlockCache:
    """Small LRU metadata cache used before GPU/CPU cache tiers are added."""

    def __init__(self, max_entries: int = 64, max_bytes: Optional[int] = None, telemetry=None):
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self.max_entries = int(max_entries)
        self.max_bytes = None if max_bytes is None else max(0, int(max_bytes))
        self._records: "OrderedDict[str, BlockRecord]" = OrderedDict()
        self._generation = count(1)
        self._size_bytes = 0
        self._owner_bytes = {}
        self._owner_hits = {}
        self._telemetry = telemetry
        self._lock = threading.RLock()

    @staticmethod
    def data_nbytes(data: Any) -> int:
        if data is None:
            return 0
        if isinstance(data, (tuple, list)):
            return sum(BlockCache.data_nbytes(item) for item in data)
        if hasattr(data, "nbytes"):
            return int(data.nbytes)
        if hasattr(data, "size_bytes"):
            return int(data.size_bytes)
        try:
            return int(np.asarray(data).nbytes)
        except Exception:
            return 0

    @property
    def size_bytes(self):
        with self._lock:
            return self._size_bytes

    @property
    def owner_bytes(self):
        with self._lock:
            return dict(self._owner_bytes)

    def _active_owners(self, requesting_owner=None):
        owners = {owner for owner, size in self._owner_bytes.items() if size > 0}
        if requesting_owner:
            owners.add(str(requesting_owner))
        return owners

    def owner_targets(self, requesting_owner=None):
        """Compute automatic soft shares; unused shares remain borrowable."""
        with self._lock:
            owners = self._active_owners(requesting_owner)
            if self.max_bytes is None or not owners:
                return {owner: None for owner in owners}
            weights = {
                owner: min(4.0, 1.0 + math.log2(1.0 + self._owner_hits.get(owner, 0)) / 4.0)
                for owner in owners
            }
            total_weight = sum(weights.values())
            return {
                owner: int(self.max_bytes * weights[owner] / total_weight)
                for owner in owners
            }

    def set_limits(self, max_entries=None, max_bytes=None):
        with self._lock:
            if max_entries is not None:
                self.max_entries = max(1, int(max_entries))
            self.max_bytes = None if max_bytes is None else max(0, int(max_bytes))
            self.collect()

    def get(self, block_id: str) -> Optional[BlockRecord]:
        with self._lock:
            record = self._records.get(block_id)
            if record is not None:
                self._records.move_to_end(block_id)
                if self._telemetry is not None:
                    self._telemetry.add("hits")
                owner = str(record.owner or "default")
                self._owner_hits[owner] = self._owner_hits.get(owner, 0) + 1
            elif self._telemetry is not None:
                self._telemetry.add("misses")
            return record

    def peek(self, block_id: str) -> Optional[BlockRecord]:
        """Inspect an entry for scheduling without changing LRU or telemetry."""
        with self._lock:
            return self._records.get(block_id)

    def put(self, record: BlockRecord) -> BlockRecord:
        with self._lock:
            entry_bytes = self.data_nbytes(record.data)
            if self.max_bytes is not None and (self.max_bytes == 0 or entry_bytes > self.max_bytes):
                if self._telemetry is not None:
                    self._telemetry.add("admission_rejects")
                return record
            previous = self._records.get(record.block_id)
            if previous is not None:
                previous_bytes = self.data_nbytes(previous.data)
                self._size_bytes -= previous_bytes
                previous_owner = str(previous.owner or "default")
                self._owner_bytes[previous_owner] = max(
                    0, self._owner_bytes.get(previous_owner, 0) - previous_bytes
                )
            record.owner = str(record.owner or "default")
            record.generation = next(self._generation)
            self._records[record.block_id] = record
            self._size_bytes += entry_bytes
            self._owner_bytes[record.owner] = self._owner_bytes.get(record.owner, 0) + entry_bytes
            self._records.move_to_end(record.block_id)
            if self._telemetry is not None:
                self._telemetry.add("admissions")
                self._telemetry.add("bytes_admitted", entry_bytes)
            self.collect(requesting_owner=record.owner)
            return record

    def invalidate(self, block_id: str) -> bool:
        with self._lock:
            record = self._records.get(block_id)
            if record is None:
                return False
            owner = str(record.owner or "default")
            # A checksum failure normally concerns an idle record.  Remove it
            # immediately so it cannot consume an entry/byte quota or be
            # returned by a later peek.  If another worker still leases the
            # record, detach it only after the lease is released; clearing its
            # payload here would create a use-after-free for that consumer.
            if record.pinned or record.ref_count:
                record.state = BlockState.CORRUPT
                record.checksum = None
                record.source_checksum = None
                record.dirty = False
                if self._telemetry is not None:
                    self._telemetry.add("invalidations")
                return True
            entry_bytes = self.data_nbytes(record.data)
            self._size_bytes = max(0, self._size_bytes - entry_bytes)
            self._owner_bytes[owner] = max(
                0, self._owner_bytes.get(owner, 0) - entry_bytes
            )
            record.state = BlockState.CORRUPT
            record.data = None
            record.checksum = None
            record.source_checksum = None
            record.dirty = False
            self._records.pop(block_id, None)
            if self._owner_bytes.get(owner, 0) == 0:
                self._owner_bytes.pop(owner, None)
                self._owner_hits.pop(owner, None)
            if self._telemetry is not None:
                self._telemetry.add("invalidations")
            return True

    def invalidate_owner(self, owner: str) -> int:
        """Invalidate cached records belonging to one quarantined operation.

        Idle records are removed immediately.  Leased/pinned records remain
        attached until their owner releases them, but are marked corrupt so
        another worker can never reuse their payload.
        """
        owner = str(owner)
        invalidated = 0
        with self._lock:
            for block_id, record in list(self._records.items()):
                if str(record.owner or "default") != owner:
                    continue
                # A quarantine can be raised by one worker while another
                # worker is still consuming a record.  Do not detach the
                # payload from a leased/pinned record: mark it unusable for
                # future lookups and let the normal lifecycle release it.
                if record.pinned or record.ref_count:
                    record.state = BlockState.CORRUPT
                    record.checksum = None
                    record.source_checksum = None
                    record.dirty = False
                    invalidated += 1
                    if self._telemetry is not None:
                        self._telemetry.add("invalidations")
                    continue
                entry_bytes = self.data_nbytes(record.data)
                self._size_bytes = max(0, self._size_bytes - entry_bytes)
                self._owner_bytes[owner] = max(
                    0, self._owner_bytes.get(owner, 0) - entry_bytes
                )
                record.state = BlockState.CORRUPT
                record.data = None
                record.checksum = None
                record.dirty = False
                self._records.pop(block_id, None)
                invalidated += 1
                if self._telemetry is not None:
                    self._telemetry.add("invalidations")
            if self._owner_bytes.get(owner, 0) == 0:
                self._owner_bytes.pop(owner, None)
                self._owner_hits.pop(owner, None)
        return invalidated

    def collect(self, requesting_owner=None) -> Tuple[str, ...]:
        """Evict oldest clean, unpinned, unused records until within capacity."""
        with self._lock:
            evicted = []
            targets = self.owner_targets(requesting_owner)
            candidates = list(self._records.items())
            if self.max_bytes is not None:
                indexed = list(enumerate(candidates))
                indexed.sort(key=lambda item: (
                    0 if self._owner_bytes.get(str(item[1][1].owner), 0)
                    > (targets.get(str(item[1][1].owner)) or 0) else 1,
                    1 if str(item[1][1].owner) == str(requesting_owner) else 0,
                    item[0],
                ))
                candidates = [item for _, item in indexed]
            for block_id, record in candidates:
                over_entries = len(self._records) > self.max_entries
                over_bytes = self.max_bytes is not None and self._size_bytes > self.max_bytes
                if not over_entries and not over_bytes:
                    break
                if record.pinned or record.dirty or record.ref_count:
                    continue
                entry_bytes = self.data_nbytes(record.data)
                self._size_bytes -= entry_bytes
                owner = str(record.owner or "default")
                was_borrowed = (
                    self.max_bytes is not None
                    and self._owner_bytes.get(owner, 0) > (targets.get(owner) or 0)
                )
                self._owner_bytes[owner] = max(
                    0, self._owner_bytes.get(owner, 0) - entry_bytes
                )
                record.state = BlockState.RELEASED
                record.data = None
                self._records.pop(block_id)
                evicted.append(block_id)
                if self._telemetry is not None:
                    self._telemetry.add("evictions")
                    self._telemetry.add("bytes_evicted", entry_bytes)
                    if was_borrowed:
                        self._telemetry.add("quota_reclaims")
            return tuple(evicted)

    def clear(self) -> None:
        """Release every cached record."""
        with self._lock:
            for record in self._records.values():
                record.state = BlockState.RELEASED
                record.data = None
            self._records.clear()
            self._size_bytes = 0
            self._owner_bytes.clear()
            self._owner_hits.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._records)


OPERATION_PATHS = {
    "copy": BlockPath.BLOCK,
    "copy_field": BlockPath.BLOCK,
    "absdiff": BlockPath.BLOCK,
    "rgb2gray": BlockPath.BLOCK,
    "split_3ch": BlockPath.BLOCK,
    "merge_3ch": BlockPath.BLOCK,
    "extract_channel": BlockPath.BLOCK,
    "insert_channel": BlockPath.BLOCK,
    "enhance_grayscale": BlockPath.BLOCK,
    "gaussian_blur": BlockPath.BLOCK_BORDER,
    "box_filter": BlockPath.BLOCK_BORDER,
    "median_filter": BlockPath.BLOCK_BORDER,
    "sobel": BlockPath.BLOCK_BORDER,
    "laplacian": BlockPath.BLOCK_BORDER,
    "non_local_means": BlockPath.BLOCK_BORDER,
    "smooth_flow": BlockPath.BLOCK_BORDER,
    "joint_bilateral_filter": BlockPath.BLOCK_BORDER,
    "guided_filter": BlockPath.BLOCK_BORDER,
    # Extended image kernels have independent tile executors.  Keep their
    # names separate from the older ``*_filter`` aliases so diagnostics and
    # cache ownership remain unambiguous.
    "morphology": BlockPath.BLOCK_BORDER,
    "filter2d": BlockPath.BLOCK_BORDER,
    "threshold": BlockPath.BLOCK,
    "normalize": BlockPath.BLOCK,
    "joint_bilateral_guidance": BlockPath.BLOCK_BORDER,
    "enhance_image": BlockPath.BLOCK,
    "highlight_recovery": BlockPath.BLOCK_BORDER,
    "cvtColor_extended": BlockPath.BLOCK,
    "resize": BlockPath.BLOCK,
    "image_pyramid": BlockPath.BLOCK,
    "remap": BlockPath.BLOCK,
    "remap_with_flow": BlockPath.BLOCK,
    "warp_perspective": BlockPath.BLOCK,
    "hamilton_demosaic": BlockPath.BLOCK_BORDER,
    "arm_demosaic": BlockPath.BLOCK_BORDER,
    "hamilton_demosaic_1channel": BlockPath.BLOCK_BORDER,
    "hamilton_demosaic_half_res": BlockPath.BLOCK,
    "dcb_demosaic": BlockPath.BLOCK,
    "dcb_demosaic_1channel": BlockPath.BLOCK,
    "dcb_demosaic_half_res": BlockPath.BLOCK,
    "dcb_demosaic_rgb_half_res": BlockPath.BLOCK,
    "dcb_demosaic_3channel": BlockPath.BLOCK,
    "hamilton_demosaic_rgb_half_res": BlockPath.BLOCK,
    "hamilton_demosaic_3channel": BlockPath.BLOCK_BORDER,
    "arm_demosaic_1channel": BlockPath.BLOCK_BORDER,
    "arm_demosaic_half_res": BlockPath.BLOCK,
    "arm_demosaic_rgb_half_res": BlockPath.BLOCK,
    "pure_arm_demosaic": BlockPath.BLOCK_BORDER,
    "farneback_flow": BlockPath.BLOCK_BORDER,
    "lucas_kanade": BlockPath.BLOCK_BORDER,
    "block_matching": BlockPath.BLOCK_BORDER,
    # These APIs currently have no validated tile executor.  Keep them
    # registered for diagnostics, but fail closed to their full-frame paths.
    "tone_map_srgb": BlockPath.DIRECT,
    "canny_aot": BlockPath.CUSTOM,
    "clahe_aot": BlockPath.CUSTOM,
    "otsu_threshold": BlockPath.GLOBAL,
    "joint_bilateral_upsample": BlockPath.GLOBAL,
    "fft": BlockPath.GLOBAL,
    "histogram": BlockPath.GLOBAL,
    # Public AOT algorithms without a validated block executor are listed
    # explicitly so diagnostics and planner telemetry never classify them as
    # an unknown operation. They stay fail-closed on the full-frame path.
    "generate_hanning_window_2d": BlockPath.DIRECT,
    "mean_division": BlockPath.GLOBAL,
    "normalize_accumulator": BlockPath.GLOBAL,
    "stitch_tile": BlockPath.GLOBAL,
    "stitch_tile_normalized": BlockPath.GLOBAL,
    "cvtColor": BlockPath.BLOCK,
    "normalize_image": BlockPath.DIRECT,
    "to_gamma_proxy": BlockPath.DIRECT,
    "fft2": BlockPath.GLOBAL,
    "ifft2": BlockPath.GLOBAL,
    "ransac_flow_cleanup": BlockPath.GLOBAL,
    "ransac_flow_cleanup_aot": BlockPath.GLOBAL,
    "ncc_alignment": BlockPath.GLOBAL,
    "zncc": BlockPath.GLOBAL,
    "bilateral_grid_filter": BlockPath.CUSTOM,
    "phase_correlation": BlockPath.GLOBAL,
    "build_flow_maps": BlockPath.CUSTOM,
    "mlri_admm_demosaic": BlockPath.CUSTOM,
    "mlri_admm_demosaic_1channel": BlockPath.CUSTOM,
    "mlri_admm_demosaic_half_res": BlockPath.CUSTOM,
    "mlri_admm_demosaic_rgb_half_res": BlockPath.CUSTOM,
    "mlri_admm_demosaic_3channel": BlockPath.CUSTOM,
    "naturalTonemapping": BlockPath.DIRECT,
    "rotate_by_flip": BlockPath.DIRECT,
    "demosaic": BlockPath.CUSTOM,
    "generate_brief_pattern": BlockPath.DIRECT,
    "ofb": BlockPath.GLOBAL,
    "akaze": BlockPath.GLOBAL,
    "find_homography": BlockPath.GLOBAL,
    "inpaint": BlockPath.CUSTOM,
    "seamless_clone": BlockPath.GLOBAL,
    "align_mtb": BlockPath.GLOBAL,
    "hough_lines_aot": BlockPath.GLOBAL,
    # Extended-module public names are aliases of the operation keys above.
    # Keeping them in the registry makes capability reports complete even
    # when an embedding application names the high-level API directly.
    "dilate_aot": BlockPath.BLOCK_BORDER,
    "erode_aot": BlockPath.BLOCK_BORDER,
    "filter2d_aot": BlockPath.BLOCK_BORDER,
    "threshold_aot": BlockPath.BLOCK,
    "normalize_aot": BlockPath.BLOCK,
    "joint_bilateral_guidance_aot": BlockPath.BLOCK_BORDER,
    "enhance_image_aot": BlockPath.BLOCK,
    "guided_filter_aot": BlockPath.BLOCK_BORDER,
    "non_local_means_aot": BlockPath.BLOCK_BORDER,
    "histogram_aot": BlockPath.GLOBAL,
    "ssim_aot": BlockPath.GLOBAL,
    "warp_affine_aot": BlockPath.DIRECT,
    "copy_make_border_aot": BlockPath.DIRECT,
    "gaussian_window_aot": BlockPath.DIRECT,
    "otsu_threshold_aot": BlockPath.GLOBAL,
    "inpaint_aot": BlockPath.CUSTOM,
    "seamless_clone_aot": BlockPath.GLOBAL,
    "bm3d": BlockPath.CUSTOM,
    # Public camel-case wrappers delegate to the conservative snake-case
    # operation names above; keep the aliases non-selectable if referenced
    # directly by a future caller.
    "lucasKanade": BlockPath.CUSTOM,
    "blockMatching": BlockPath.CUSTOM,
}

# Conservative automatic set. These operations have local dependency radii
# and existing halo-aware executors. Global reductions and the non-local flow
# families remain full-frame unless explicitly enabled and parity-tested.
AUTO_BLOCK_SAFE = frozenset({
    "copy",
    "copy_field",
    "absdiff",
    "rgb2gray",
    "split_3ch",
    "merge_3ch",
    "extract_channel",
    "insert_channel",
    "enhance_grayscale",
    "resize",
    "gaussian_blur",
    "box_filter",
    "median_filter",
    "sobel",
    "laplacian",
    "non_local_means",
    "smooth_flow",
    "joint_bilateral_filter",
    "guided_filter",
    "morphology",
    "filter2d",
    "threshold",
    "normalize",
    "joint_bilateral_guidance",
    "enhance_image",
    "highlight_recovery",
    "cvtColor",
    "cvtColor_extended",
    "dilate_aot",
    "erode_aot",
    "filter2d_aot",
    "threshold_aot",
    "normalize_aot",
    "joint_bilateral_guidance_aot",
    "enhance_image_aot",
    "guided_filter_aot",
    "non_local_means_aot",
    "remap",
    "remap_with_flow",
    "warp_perspective",
    "image_pyramid",
    "hamilton_demosaic",
    "hamilton_demosaic_1channel",
    "hamilton_demosaic_half_res",
    "hamilton_demosaic_rgb_half_res",
    "hamilton_demosaic_3channel",
    "dcb_demosaic",
    "dcb_demosaic_1channel",
    "dcb_demosaic_half_res",
    "dcb_demosaic_rgb_half_res",
    "dcb_demosaic_3channel",
    "arm_demosaic",
    "arm_demosaic_1channel",
    "arm_demosaic_half_res",
    "arm_demosaic_rgb_half_res",
    "pure_arm_demosaic",
})


# Spatial shape transforms that require a caller-owned coordinate map and
# output merge.  They remain available through the historical explicit APIs,
# but the P3 contract gate does not infer tile safety from their names.
SHAPE_CHANGING_OPERATIONS = frozenset({
    "resize",
    "image_pyramid",
    "hamilton_demosaic_half_res",
    "hamilton_demosaic_rgb_half_res",
    "dcb_demosaic_half_res",
    "dcb_demosaic_rgb_half_res",
    "arm_demosaic_half_res",
    "arm_demosaic_rgb_half_res",
    "generate_hanning_window_2d",
    "warp_affine_aot",
})


def _build_operation_contracts():
    """Build conservative P3 contracts for the native operation registry.

    Existing operation names intentionally retain their historical path and
    explicit safety bits.  The new contract is an additional, stricter gate:
    unknown names, global reductions, shape transforms, variable-cardinality
    results, and unqualified backend mappings never become automatic by
    accident.
    """

    contracts = {}
    all_backend_parity = BackendCapability(("*",), ("*",))
    variable_names = frozenset({
        "ofb", "akaze", "find_homography", "hough_lines_aot",
        "inpaint", "canny_aot", "clahe_aot",
    })
    for name, path_value in OPERATION_PATHS.items():
        path = BlockPath(path_value)
        shape = (
            ShapeTransform.CHANGING
            if name in SHAPE_CHANGING_OPERATIONS
            else ShapeTransform.SAME
        )
        reduction = ReductionPolicy.GLOBAL if path == BlockPath.GLOBAL else ReductionPolicy.NONE
        variable = name in variable_names or path in (BlockPath.GLOBAL, BlockPath.CUSTOM)
        merge = MergePolicy.VARIABLE if variable else MergePolicy.FIXED
        halo = 1 if path == BlockPath.BLOCK_BORDER else 0
        halo_policy = HaloPolicy.FIXED if halo else HaloPolicy.NONE
        border = BorderPolicy.CLAMP if halo else BorderPolicy.NONE
        candidate = bool(
            name in AUTO_BLOCK_SAFE
            and path != BlockPath.GLOBAL
            and shape == ShapeTransform.SAME
            and not variable
        )
        contracts[name] = OperationContract(
            operation=name,
            shape_transform=shape,
            input_coordinate_map="identity" if shape == ShapeTransform.SAME else "requires_contract",
            halo=halo,
            halo_policy=halo_policy,
            border_policy=border,
            reduction=reduction,
            merge=merge,
            variable_cardinality=variable,
            deterministic=True,
            side_effect=False,
            scratch_bytes=0,
            backend_capability=all_backend_parity,
            automatic_safe=candidate,
            parity_qualified=candidate,
            reason=(
                "same-shape local operation with declared halo/border"
                if candidate
                else "requires explicit shape/reduction/backend contract"
            ),
        )
    return contracts


OPERATION_CONTRACTS = _build_operation_contracts()


CANONICAL_OPERATION_ALIASES = MappingProxyType({
    # Extended image wrappers delegate to the canonical local operation.
    "dilate_aot": "morphology",
    "erode_aot": "morphology",
    "filter2d_aot": "filter2d",
    "threshold_aot": "threshold",
    "normalize_aot": "normalize",
    "joint_bilateral_guidance_aot": "joint_bilateral_guidance",
    "enhance_image_aot": "enhance_image",
    "guided_filter_aot": "guided_filter",
    "non_local_means_aot": "non_local_means",
    "histogram_aot": "histogram",
    "otsu_threshold_aot": "otsu_threshold",
    "inpaint_aot": "inpaint",
    "seamless_clone_aot": "seamless_clone",
    # Historical camel-case alignment names remain public aliases.
    "lucasKanade": "lucas_kanade",
    "blockMatching": "block_matching",
})

# Backwards/wording-friendly alias.  The mapping is immutable so a plugin
# cannot silently change the operation selected by another plugin at runtime.
OPERATION_ALIASES = CANONICAL_OPERATION_ALIASES


def canonical_operation_name(name: str) -> str:
    """Return the maintained operation key for a public alias.

    Alias normalization is deliberately separate from capability selection:
    resolving ``guided_filter_aot`` to ``guided_filter`` does not promote the
    operation to automatic blocking and does not mutate the legacy registry.
    The small cycle guard also keeps diagnostics safe if a future alias table
    is edited incorrectly.
    """

    current = str(name or "").strip()
    seen: set[str] = set()
    while current in CANONICAL_OPERATION_ALIASES and current not in seen:
        seen.add(current)
        current = str(CANONICAL_OPERATION_ALIASES[current]).strip()
    return current


@dataclass(frozen=True)
class LegacyPartitionEvidence:
    """Evidence that a maintained API already owns a tiled executor.

    This record is intentionally weaker than a parity qualification. It only
    records a source-level fact (for example ``_run_blockwise`` or a
    specialized offset loop exists in ``aot_api``). A separate explicit
    backend/parity proof is still required by
    :func:`can_auto_partition_dispatch` before an adapter can be considered
    for automatic dispatch.
    """

    operation: str
    executor: str
    strategy: PartitionStrategy
    specialized: bool = False
    source: str = "taichi_vision.taichi_algorithm.aot_api"
    requires_adapter: bool = True
    parity_qualified: bool = False
    backend_capability: BackendCapability = field(
        # A sentinel keeps ``backend_supported`` false for real devices until
        # a target-specific evidence record is intentionally supplied.
        default_factory=lambda: BackendCapability(
            supported=("__legacy_unverified__",), parity_qualified=()
        )
    )
    note: str = "existing legacy tiled executor; parity remains unverified"

    def __post_init__(self) -> None:
        operation = canonical_operation_name(self.operation)
        if not operation:
            raise ValueError("legacy evidence operation must not be empty")
        object.__setattr__(self, "operation", operation)
        try:
            object.__setattr__(self, "strategy", PartitionStrategy(self.strategy))
        except (TypeError, ValueError) as exc:
            raise ValueError("legacy evidence strategy is invalid") from exc
        object.__setattr__(self, "executor", str(self.executor or "unknown"))
        object.__setattr__(self, "source", str(self.source or "unknown"))
        object.__setattr__(self, "requires_adapter", bool(self.requires_adapter))
        object.__setattr__(self, "parity_qualified", bool(self.parity_qualified))
        capability = BackendCapability.from_value(self.backend_capability)
        # A source-level record cannot claim backend parity unless the
        # capability mapping explicitly contains a parity-qualified backend.
        if self.parity_qualified and not capability.parity_qualified:
            object.__setattr__(self, "parity_qualified", False)
        object.__setattr__(self, "backend_capability", capability)
        object.__setattr__(self, "note", str(self.note or ""))

    def supports_backend(self, backend: Optional[str] = None) -> bool:
        """Whether this record has explicit parity evidence for ``backend``."""

        return bool(
            self.parity_qualified
            and self.backend_capability.supports(backend, require_parity=True)
        )

    @property
    def status(self) -> str:
        return "parity_qualified" if self.parity_qualified else "executor_only"

    def as_dict(self, backend: Optional[str] = None) -> dict[str, Any]:
        return {
            "operation": self.operation,
            "executor": self.executor,
            "strategy": self.strategy.value,
            "specialized": self.specialized,
            "source": self.source,
            "requires_adapter": self.requires_adapter,
            "parity_qualified": self.parity_qualified,
            "backend": None if backend is None else str(backend),
            "backend_supported": self.backend_capability.supports(
                backend, require_parity=False
            ),
            "backend_parity_qualified": self.supports_backend(backend),
            "status": self.status,
            "note": self.note,
        }


def _legacy_partition_record(
    operation: str,
    executor: str,
    strategy: PartitionStrategy,
    *,
    specialized: bool = False,
    note: str = "existing legacy tiled executor; parity remains unverified",
) -> LegacyPartitionEvidence:
    """Create an executor-only record with conservative default evidence."""

    return LegacyPartitionEvidence(
        operation=operation,
        executor=executor,
        strategy=strategy,
        specialized=specialized,
        note=note,
    )


# This list is intentionally limited to operations observed in
# ``aot_api/__init__.py`` calling ``_run_blockwise``/its pair, triplet, or GPU
# helpers, or owning an equivalent cached offset loop. It is *not* derived
# from ``OPERATION_PATHS``: a path label alone is not executor evidence.
_LEGACY_PARTITION_EVIDENCE = MappingProxyType({
    # Pointwise and fixed local executors.
    "copy": _legacy_partition_record("copy", "_run_blockwise", PartitionStrategy.LOCAL),
    "extract_channel": _legacy_partition_record("extract_channel", "_run_blockwise", PartitionStrategy.LOCAL),
    "split_3ch": _legacy_partition_record("split_3ch", "_run_blockwise_triplet", PartitionStrategy.LOCAL),
    "merge_3ch": _legacy_partition_record("merge_3ch", "_run_blockwise", PartitionStrategy.LOCAL),
    "insert_channel": _legacy_partition_record("insert_channel", "_run_blockwise", PartitionStrategy.LOCAL),
    "rgb2gray": _legacy_partition_record("rgb2gray", "_run_blockwise", PartitionStrategy.LOCAL),
    "absdiff": _legacy_partition_record("absdiff", "_run_blockwise", PartitionStrategy.LOCAL),
    "cvtColor": _legacy_partition_record("cvtColor", "_run_blockwise", PartitionStrategy.LOCAL),
    "cvtColor_extended": _legacy_partition_record("cvtColor_extended", "_run_blockwise", PartitionStrategy.LOCAL),
    # Halo-aware local/stencil executors.
    "box_filter": _legacy_partition_record("box_filter", "_run_blockwise", PartitionStrategy.STENCIL),
    "gaussian_blur": _legacy_partition_record("gaussian_blur", "_run_blockwise", PartitionStrategy.STENCIL),
    "median_filter": _legacy_partition_record("median_filter", "_run_blockwise", PartitionStrategy.STENCIL),
    "sobel": _legacy_partition_record("sobel", "_run_blockwise_pair", PartitionStrategy.STENCIL),
    "laplacian": _legacy_partition_record("laplacian", "_run_blockwise", PartitionStrategy.STENCIL),
    "joint_bilateral_filter": _legacy_partition_record("joint_bilateral_filter", "_run_blockwise", PartitionStrategy.STENCIL),
    "smooth_flow": _legacy_partition_record("smooth_flow", "_run_blockwise", PartitionStrategy.STENCIL),
    "enhance_grayscale": _legacy_partition_record("enhance_grayscale", "_run_blockwise", PartitionStrategy.LOCAL),
    "highlight_recovery": _legacy_partition_record("highlight_recovery", "_run_blockwise", PartitionStrategy.STENCIL),
    "non_local_means": _legacy_partition_record("non_local_means", "_run_blockwise", PartitionStrategy.STENCIL),
    "guided_filter": _legacy_partition_record("guided_filter", "_run_blockwise", PartitionStrategy.STENCIL),
    # Extended image-processing wrappers own the same guarded executor.  They
    # are recorded here as evidence-only paths; no operation is promoted to
    # automatic/native dispatch by this table alone.
    "morphology": _legacy_partition_record("morphology", "_run_blockwise", PartitionStrategy.STENCIL),
    "filter2d": _legacy_partition_record("filter2d", "_run_blockwise", PartitionStrategy.STENCIL),
    "threshold": _legacy_partition_record("threshold", "_run_blockwise", PartitionStrategy.LOCAL),
    "normalize": _legacy_partition_record("normalize", "_run_blockwise", PartitionStrategy.LOCAL),
    "joint_bilateral_guidance": _legacy_partition_record("joint_bilateral_guidance", "_run_blockwise", PartitionStrategy.STENCIL),
    "enhance_image": _legacy_partition_record("enhance_image", "_run_blockwise", PartitionStrategy.LOCAL),
    # Existing shape/coordinate-aware cached offset loops.
    "resize": _legacy_partition_record("resize", "specialized_offset_loop", PartitionStrategy.COORDINATE, specialized=True),
    "image_pyramid": _legacy_partition_record("image_pyramid", "specialized_pyramid_loop", PartitionStrategy.MULTI_STAGE, specialized=True),
    "remap": _legacy_partition_record("remap", "specialized_offset_loop", PartitionStrategy.COORDINATE, specialized=True),
    "remap_with_flow": _legacy_partition_record("remap_with_flow", "specialized_offset_loop", PartitionStrategy.COORDINATE, specialized=True),
    "warp_perspective": _legacy_partition_record("warp_perspective", "specialized_offset_loop", PartitionStrategy.COORDINATE, specialized=True),
    # Demosaic paths with explicit CFA/halo tile executors. DCB half-res and
    # DCB auxiliary variants are intentionally absent: their wrappers
    # dispatch full-frame graphs and provide no legacy tile evidence.
    "dcb_demosaic": _legacy_partition_record("dcb_demosaic", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "hamilton_demosaic": _legacy_partition_record("hamilton_demosaic", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "hamilton_demosaic_1channel": _legacy_partition_record("hamilton_demosaic_1channel", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "hamilton_demosaic_half_res": _legacy_partition_record("hamilton_demosaic_half_res", "_demosaic_half_blockwise", PartitionStrategy.COORDINATE, specialized=True),
    "hamilton_demosaic_rgb_half_res": _legacy_partition_record("hamilton_demosaic_rgb_half_res", "_demosaic_half_blockwise", PartitionStrategy.COORDINATE, specialized=True),
    "hamilton_demosaic_3channel": _legacy_partition_record("hamilton_demosaic_3channel", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "arm_demosaic": _legacy_partition_record("arm_demosaic", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "arm_demosaic_1channel": _legacy_partition_record("arm_demosaic_1channel", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    "arm_demosaic_half_res": _legacy_partition_record("arm_demosaic_half_res", "_demosaic_half_blockwise", PartitionStrategy.COORDINATE, specialized=True),
    "arm_demosaic_rgb_half_res": _legacy_partition_record("arm_demosaic_rgb_half_res", "_demosaic_half_blockwise", PartitionStrategy.COORDINATE, specialized=True),
    "pure_arm_demosaic": _legacy_partition_record("pure_arm_demosaic", "_demosaic_blockwise", PartitionStrategy.STENCIL, specialized=True),
    # Flow executors are iterative/multi-stage and remain evidence-only.
    "farneback_flow": _legacy_partition_record("farneback_flow", "_run_blockwise_gpu/_run_blockwise", PartitionStrategy.MULTI_STAGE, specialized=True),
    "lucas_kanade": _legacy_partition_record("lucas_kanade", "_dense_flow_blockwise", PartitionStrategy.ITERATIVE, specialized=True),
    "block_matching": _legacy_partition_record("block_matching", "_dense_flow_blockwise", PartitionStrategy.ITERATIVE, specialized=True),
})

LEGACY_PARTITION_EVIDENCE = _LEGACY_PARTITION_EVIDENCE


def legacy_partition_evidence(
    operation: Optional[str] = None,
    backend: Optional[str] = None,
) -> Any:
    """Return source-level legacy tile evidence for diagnostics.

    With no operation, a JSON-friendly snapshot of all registered records is
    returned. Unknown operations return ``None``. The ``status`` field is
    ``executor_only`` until an explicit parity proof is attached; this helper
    never promotes a contract or alters runtime dispatch.
    """

    if operation is None:
        return {
            name: evidence.as_dict(backend)
            for name, evidence in _LEGACY_PARTITION_EVIDENCE.items()
        }
    evidence = _LEGACY_PARTITION_EVIDENCE.get(canonical_operation_name(operation))
    return None if evidence is None else evidence.as_dict(backend)


@dataclass(frozen=True)
class BlockAdapter:
    """Caller-owned tile adapter metadata.

    An adapter is only a registration/lookup object.  Registering one never
    changes ``AUTO_BLOCK_SAFE`` or ``OPERATION_CONTRACTS``.  Automatic
    selection remains gated by the existing contract and backend evidence;
    this registry gives the next planner a stable place to find a reader,
    runner, validator, and merger once those gates are satisfied.
    """

    operation: str
    reader: Optional[Callable[..., Any]] = None
    runner: Optional[Callable[..., Any]] = None
    validator: Optional[Callable[..., Any]] = None
    merger: Optional[Callable[..., Any]] = None
    contract: Optional[OperationContract] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    version: str = "v1"
    partition_strategy: PartitionStrategy | str | None = None
    backend_capability: BackendCapability | Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        operation = canonical_operation_name(self.operation)
        if not operation:
            raise ValueError("block adapter operation must not be empty")
        object.__setattr__(self, "operation", operation)
        for callback_name in ("reader", "runner", "validator", "merger"):
            callback = getattr(self, callback_name)
            if callback is not None and not callable(callback):
                raise TypeError(f"{callback_name} must be callable when provided")
        if self.contract is not None and not isinstance(self.contract, OperationContract):
            raise TypeError("adapter contract must be an OperationContract")
        object.__setattr__(self, "metadata", dict(self.metadata or {}))
        object.__setattr__(self, "version", str(self.version or "v1"))
        strategy = self.partition_strategy
        if strategy is None and self.contract is not None:
            strategy = self.contract.partition_strategy
        if strategy is None:
            strategy = self.metadata.get("partition_strategy")
        if strategy is None:
            strategy = PartitionStrategy.LOCAL
        try:
            strategy = PartitionStrategy(strategy)
        except (TypeError, ValueError):
            strategy = None
        object.__setattr__(self, "partition_strategy", strategy)
        capability = self.backend_capability
        if capability is None:
            capability = self.metadata.get(
                "backend_capability",
                self.metadata.get("backend_parity"),
            )
        if capability is not None:
            capability = BackendCapability.from_value(capability)
        object.__setattr__(self, "backend_capability", capability)

    @property
    def ready(self) -> bool:
        """Whether the adapter has a callable tile runner."""

        return callable(self.runner)

    def contract_allows_auto_block(self, backend: Optional[str] = None) -> bool:
        """Check adapter-local contract evidence without changing selection."""

        if self.contract is None:
            return False
        try:
            return bool(self.contract.can_auto_block(backend))
        except Exception:
            return False

    @property
    def partition_ready(self) -> bool:
        """Whether callbacks needed for an explicit partition are present.

        ``reader`` is optional because callers may hand the runner an already
        sliced context.  Validation and merge callbacks are mandatory so an
        adapter cannot claim partition support while silently dropping halo,
        shape, or variable-cardinality semantics.
        """

        return bool(
            callable(self.runner)
            and callable(self.validator)
            and callable(self.merger)
        )

    def supports_backend(self, backend: Optional[str] = None) -> bool:
        """Return explicit adapter/backend parity evidence, if declared."""

        capability = self.backend_capability
        if capability is None and self.contract is not None:
            capability = self.contract.backend_capability
        if capability is None:
            return False
        try:
            return bool(capability.supports(backend, require_parity=True))
        except Exception:
            return False

    def contract_allows_partition(self, backend: Optional[str] = None) -> bool:
        """Check the adapter's richer partition contract and backend proof."""

        if self.contract is None or not self.partition_ready:
            return False
        try:
            return bool(
                self.contract.allows_partitioned_block
                and self.supports_backend(backend)
                and self.partition_strategy == self.contract.partition_strategy
            )
        except Exception:
            return False


BlockOperationAdapter = BlockAdapter

_BLOCK_ADAPTERS: dict[str, BlockAdapter] = {}
_BLOCK_ADAPTERS_LOCK = threading.RLock()


def register_block_adapter(
    operation: str,
    adapter: Any = None,
    *,
    reader: Optional[Callable[..., Any]] = None,
    runner: Optional[Callable[..., Any]] = None,
    validator: Optional[Callable[..., Any]] = None,
    merger: Optional[Callable[..., Any]] = None,
    contract: Optional[OperationContract] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    version: str = "v1",
    partition_strategy: PartitionStrategy | str | None = None,
    backend_capability: BackendCapability | Mapping[str, Any] | None = None,
    replace: bool = True,
) -> BlockAdapter:
    """Register a caller-owned adapter without enabling automatic blocking.

    ``adapter`` may be an existing :class:`BlockAdapter`, a callable tile
    runner, or a mapping containing the keyword fields above.  Registration is
    canonicalized through :func:`canonical_operation_name`; aliases therefore
    share one adapter and one cache namespace.  The operation capability and
    contract tables are intentionally untouched.
    """

    canonical = canonical_operation_name(operation)
    if not canonical:
        raise ValueError("adapter operation must not be empty")

    if isinstance(adapter, BlockAdapter):
        if any(value is not None for value in (
            reader, runner, validator, merger, contract, metadata,
            partition_strategy, backend_capability,
        )) or version != "v1":
            raise TypeError("adapter object cannot be combined with adapter fields")
        candidate = BlockAdapter(
            canonical,
            reader=adapter.reader,
            runner=adapter.runner,
            validator=adapter.validator,
            merger=adapter.merger,
            contract=adapter.contract,
            metadata=adapter.metadata,
            version=adapter.version,
            partition_strategy=adapter.partition_strategy,
            backend_capability=adapter.backend_capability,
        )
    else:
        if isinstance(adapter, Mapping):
            values = dict(adapter)
            aliases = {
                "input_reader": "reader",
                "run_tile": "runner",
                "validate_tile": "validator",
                "merge_tile": "merger",
            }
            unknown = set(values).difference({
                "reader", "runner", "validator", "merger", "contract", "metadata", "version",
                "partition_strategy", "backend_capability", *aliases,
            })
            if unknown:
                raise TypeError(f"unknown block adapter field(s): {sorted(unknown)}")
            for alias, target in aliases.items():
                if alias in values and target in values:
                    raise TypeError(f"adapter mapping cannot specify both {alias} and {target}")
                if alias in values:
                    values[target] = values.pop(alias)
            reader = values.get("reader", reader)
            runner = values.get("runner", runner)
            validator = values.get("validator", validator)
            merger = values.get("merger", merger)
            contract = values.get("contract", contract)
            metadata = values.get("metadata", metadata)
            version = values.get("version", version)
            partition_strategy = values.get("partition_strategy", partition_strategy)
            backend_capability = values.get("backend_capability", backend_capability)
        elif adapter is not None:
            if runner is not None:
                raise TypeError("adapter callable cannot be combined with runner")
            if not callable(adapter):
                raise TypeError("adapter must be a BlockAdapter, mapping, or callable")
            runner = adapter
        candidate = BlockAdapter(
            canonical,
            reader=reader,
            runner=runner,
            validator=validator,
            merger=merger,
            contract=contract,
            metadata=metadata or {},
            version=version,
            partition_strategy=partition_strategy,
            backend_capability=backend_capability,
        )

    with _BLOCK_ADAPTERS_LOCK:
        if not replace and canonical in _BLOCK_ADAPTERS:
            raise KeyError(f"block adapter already registered: {canonical}")
        _BLOCK_ADAPTERS[canonical] = candidate
    return candidate


def lookup_block_adapter(operation: str) -> Optional[BlockAdapter]:
    """Return the registered adapter for a canonical name or public alias."""

    canonical = canonical_operation_name(operation)
    with _BLOCK_ADAPTERS_LOCK:
        return _BLOCK_ADAPTERS.get(canonical)


get_block_adapter = lookup_block_adapter


def registered_block_adapters() -> Mapping[str, BlockAdapter]:
    """Return a snapshot of registered adapters for diagnostics/planners."""

    with _BLOCK_ADAPTERS_LOCK:
        return dict(_BLOCK_ADAPTERS)


def block_coverage_report(
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Return auditable registry, alias, contract, and adapter coverage.

    Adapter registrations are reported separately from strict automatic
    coverage.  This is intentional: an adapter declaration is not evidence
    of parity and must never make an unsafe operation automatic by itself.
    When ``device`` is supplied, native evidence is restricted to that exact
    observed device identity; omitting it reports all records for the selected
    backend but never infers support for another backend.
    """

    names = tuple(OPERATION_PATHS)
    strict_names = tuple(name for name in names if can_auto_block(name, backend))
    canonical_names = {canonical_operation_name(name) for name in names}
    canonical_strict = {canonical_operation_name(name) for name in strict_names}
    target = int(math.ceil(len(names) * 0.95))
    canonical_target = int(math.ceil(len(canonical_names) * 0.95))
    path_counts: dict[str, int] = {}
    for path in OPERATION_PATHS.values():
        key = getattr(path, "value", str(path))
        path_counts[key] = path_counts.get(key, 0) + 1

    adapters = registered_block_adapters()
    adapter_ready = {
        name for name, adapter in adapters.items() if adapter.ready
    }
    adapter_contract_safe = {
        name for name, adapter in adapters.items()
        if adapter.contract_allows_auto_block(backend)
    }
    adapter_partition_ready = {
        name for name, adapter in adapters.items() if adapter.partition_ready
    }
    adapter_partition_qualified = {
        name for name, adapter in adapters.items()
        if adapter.contract_allows_partition(backend)
    }
    partition_contract_names = tuple(
        name for name in names if operation_contract(name).can_partition(backend)
    )
    partition_names = tuple(
        name for name in names if can_partition_block(name, backend)
    )
    canonical_partition_contract = {
        canonical_operation_name(name) for name in partition_contract_names
    }
    canonical_partition = {
        canonical_operation_name(name) for name in partition_names
    }
    legacy_names = tuple(
        name for name in names if name in _LEGACY_PARTITION_EVIDENCE
    )
    legacy_backend_names = tuple(
        name for name in legacy_names
        if _LEGACY_PARTITION_EVIDENCE[name].backend_capability.supports(
            backend, require_parity=False
        )
    )
    legacy_parity_names = tuple(
        name for name in legacy_names
        if _LEGACY_PARTITION_EVIDENCE[name].supports_backend(backend)
    )
    legacy_dispatch_names = tuple(
        name for name in legacy_names
        if can_auto_partition_dispatch(name, backend)
    )
    native_dispatch_names = tuple(
        name for name in legacy_names
        if can_auto_partition_dispatch(
            name,
            backend,
            require_native_evidence=True,
            device=device,
        )
    )

    def percent(value: int, denominator: int) -> float:
        return round((100.0 * value / denominator), 4) if denominator else 0.0

    # Native execution evidence lives in a separate module to avoid making
    # this low-level registry import the AOT runtime.  Load it lazily here so
    # reports can distinguish source/contract coverage from records produced
    # by an actual backend/device probe.  A missing registry is equivalent to
    # zero evidence; it must never make an operation eligible implicitly.
    native_records: tuple[Any, ...] = ()
    native_qualified: tuple[Any, ...] = ()
    native_operations: tuple[str, ...] = ()
    native_qualified_operations: tuple[str, ...] = ()
    try:
        from .native_evidence import lookup_native_partition_evidence

        native_records = tuple(
            record
            for name in names
            for record in lookup_native_partition_evidence(name, backend, device)
        )
        native_qualified = tuple(record for record in native_records if record.qualified)
        native_operations = tuple(sorted({record.operation for record in native_records}))
        native_qualified_operations = tuple(
            sorted({record.operation for record in native_qualified})
        )
    except Exception:
        # Diagnostics must remain usable during partial package installation
        # or when a plugin has not shipped the optional evidence module.
        pass

    return {
        "backend": None if backend is None else str(backend),
        "device": None if device is None else str(device),
        "total_operations": len(names),
        "strict_auto_safe": len(strict_names),
        "strict_auto_safe_percent": percent(len(strict_names), len(names)),
        "strict_auto_safe_operations": tuple(sorted(strict_names)),
        "strict_auto_unsafe_operations": tuple(
            sorted(set(names).difference(strict_names))
        ),
        "target_95_operations": target,
        "remaining_to_95": max(0, target - len(strict_names)),
        "canonical_total_operations": len(canonical_names),
        "canonical_strict_auto_safe": len(canonical_strict),
        "canonical_strict_auto_safe_percent": percent(
            len(canonical_strict), len(canonical_names)
        ),
        "canonical_target_95_operations": canonical_target,
        "canonical_remaining_to_95": max(0, canonical_target - len(canonical_strict)),
        "alias_count": len(names) - len(canonical_names),
        "path_counts": dict(sorted(path_counts.items())),
        "canonical_aliases": dict(CANONICAL_OPERATION_ALIASES),
        "registered_adapters": len(adapters),
        "adapter_ready": len(adapter_ready),
        "adapter_contract_safe": len(adapter_contract_safe),
        "adapter_operations": tuple(sorted(adapters)),
        # Rich partition diagnostics are separate from strict automatic
        # coverage.  They remain zero until a qualified adapter is actually
        # registered and backend parity is declared.
        "partition_qualified_operations": len(partition_contract_names),
        "partition_qualified_percent": percent(
            len(partition_contract_names), len(names)
        ),
        "partition_adapter_ready": len(adapter_partition_ready),
        "partition_adapter_qualified": len(adapter_partition_qualified),
        "partition_safe_operations": len(partition_names),
        "partition_safe_percent": percent(len(partition_names), len(names)),
        "partition_target_95_operations": target,
        "partition_remaining_to_95": max(0, target - len(partition_names)),
        "canonical_partition_qualified_operations": len(canonical_partition_contract),
        "canonical_partition_qualified_percent": percent(
            len(canonical_partition_contract), len(canonical_names)
        ),
        "canonical_partition_safe_operations": len(canonical_partition),
        "canonical_partition_safe_percent": percent(
            len(canonical_partition), len(canonical_names)
        ),
        "canonical_partition_target_95_operations": canonical_target,
        "canonical_partition_remaining_to_95": max(
            0, canonical_target - len(canonical_partition)
        ),
        "legacy_partition_evidence_operations": len(legacy_names),
        "legacy_partition_evidence_percent": percent(len(legacy_names), len(names)),
        "legacy_partition_backend_operations": len(legacy_backend_names),
        "legacy_partition_parity_qualified": len(legacy_parity_names),
        "legacy_partition_dispatch_safe": len(legacy_dispatch_names),
        "native_partition_dispatch_safe": len(native_dispatch_names),
        "native_partition_dispatch_percent": percent(
            len(native_dispatch_names), len(names)
        ),
        "legacy_partition_operations": tuple(sorted(legacy_names)),
        "legacy_partition_parity_operations": tuple(sorted(legacy_parity_names)),
        "legacy_partition_dispatch_operations": tuple(sorted(legacy_dispatch_names)),
        "native_partition_dispatch_operations": tuple(sorted(native_dispatch_names)),
        # These are deliberately separate from strict/partition coverage:
        # a command-backed record proves only the exact backend/device scope
        # that was observed, not every driver or vendor sharing its API.
        "native_evidence_operations": len(native_operations),
        "native_evidence_percent": percent(len(native_operations), len(names)),
        "native_evidence_qualified_operations": len(native_qualified_operations),
        "native_evidence_qualified_percent": percent(
            len(native_qualified_operations), len(names)
        ),
        "native_evidence_operation_names": native_operations,
        "native_evidence_qualified_operation_names": native_qualified_operations,
    }


def _build_operation_capabilities():
    """Build one conservative capability record per known operation.

    The map is derived from ``OPERATION_PATHS`` so adding a new operation
    cannot accidentally make it eligible for automatic blocking.  Operations
    must be added to ``AUTO_BLOCK_SAFE`` after their tile executor, halo
    handling, and parity tests are complete.
    """

    capabilities = {}
    for name, path in OPERATION_PATHS.items():
        path = BlockPath(path)
        capabilities[name] = BlockCapability(
            operation=name,
            path=path,
            automatic_safe=name in AUTO_BLOCK_SAFE,
            explicit_safe=path in (BlockPath.BLOCK, BlockPath.BLOCK_BORDER),
            min_halo=1 if path == BlockPath.BLOCK_BORDER else 0,
            contract=OPERATION_CONTRACTS.get(name),
            reason=(
                "local pointwise/stencil executor is parity-tested"
                if name in AUTO_BLOCK_SAFE
                else "explicit/experimental block path; automatic selection disabled"
            ),
        )

    # These algorithms compose non-local or multi-stage dependencies.  Their
    # historical block executors remain opt-in, but the planner must not turn
    # them on solely because an input exceeds the memory threshold.
    dependency_overrides = {
        "image_pyramid": ("resize",),
        "remap_with_flow": ("remap",),
        "warp_perspective": ("remap",),
        "canny_aot": ("gaussian_blur", "sobel"),
        "hamilton_demosaic": ("gaussian_blur",),
        "arm_demosaic": ("gaussian_blur",),
        "farneback_flow": ("image_pyramid", "remap"),
        "lucas_kanade": ("image_pyramid", "remap"),
        "block_matching": ("image_pyramid", "remap"),
    }
    for name, dependencies in dependency_overrides.items():
        capability = capabilities.get(name)
        if capability is not None:
            capabilities[name] = BlockCapability(
                operation=capability.operation,
                path=capability.path,
                automatic_safe=capability.automatic_safe,
                explicit_safe=capability.explicit_safe,
                min_halo=capability.min_halo,
                dependencies=dependencies,
                contract=capability.contract,
                reason=(
                    "dependency-aware tiled executor is parity-tested"
                    if capability.automatic_safe
                    else "depends on non-local or multi-stage operations"
                ),
            )
    return capabilities


OPERATION_CAPABILITIES = _build_operation_capabilities()


def normalize_block_size(size: BlockSize) -> Tuple[int, int]:
    if isinstance(size, int):
        height = width = size
    elif isinstance(size, tuple) and len(size) == 2:
        height, width = size
    else:
        raise TypeError("block size must be an int or a (height, width) tuple")
    height, width = int(height), int(width)
    if height <= 0 or width <= 0:
        raise ValueError("block size dimensions must be positive")
    return height, width


def operation_path(name: str) -> BlockPath:
    """Return the conservative path classification for an operation."""
    return OPERATION_PATHS.get(name, BlockPath.DIRECT)


def operation_capability(name: str) -> BlockCapability:
    """Return dependency-aware block metadata for ``name``.

    Unknown operations deliberately resolve to a direct, non-blocked path.
    This is the fail-closed behavior required for newly added algorithms.
    """

    key = str(name)
    capability = OPERATION_CAPABILITIES.get(key)
    if capability is not None:
        return capability
    return BlockCapability(
        operation=key or "<unknown>",
        path=BlockPath.DIRECT,
        reason="operation is not registered in the block capability table",
        contract=OperationContract(
            operation=key or "<unknown>",
            shape_transform=ShapeTransform.UNKNOWN,
            halo_policy=HaloPolicy.UNKNOWN,
            border_policy=BorderPolicy.UNKNOWN,
            reduction=ReductionPolicy.UNKNOWN,
            merge=MergePolicy.UNKNOWN,
            automatic_safe=False,
            parity_qualified=False,
            known=False,
            reason="operation is not registered in the operation contract table",
        ),
    )


def operation_contract(name: str) -> OperationContract:
    """Return the P3 contract for ``name``; unknown names fail closed."""
    key = str(name)
    contract = OPERATION_CONTRACTS.get(key)
    if contract is not None:
        return contract
    return OperationContract(
        operation=key or "<unknown>",
        shape_transform=ShapeTransform.UNKNOWN,
        input_coordinate_map="unknown",
        halo_policy=HaloPolicy.UNKNOWN,
        border_policy=BorderPolicy.UNKNOWN,
        reduction=ReductionPolicy.UNKNOWN,
        merge=MergePolicy.UNKNOWN,
        automatic_safe=False,
        parity_qualified=False,
        known=False,
        reason="operation is not registered in the operation contract table",
    )


get_operation_contract = operation_contract


def operation_contracts() -> Mapping[str, OperationContract]:
    """Return a read-only snapshot of all built-in operation contracts."""
    return dict(OPERATION_CONTRACTS)


def register_operation_contract(contract: OperationContract, *, replace: bool = True) -> OperationContract:
    """Register an additive caller-owned operation contract.

    Registration never mutates ``OPERATION_PATHS`` or the legacy capability
    table.  It only supplies the strict P3 metadata gate used by
    :func:`can_auto_block` and diagnostics, so existing APIs remain stable.
    """
    if not isinstance(contract, OperationContract):
        raise TypeError("contract must be an OperationContract")
    name = contract.operation
    if not replace and name in OPERATION_CONTRACTS:
        raise KeyError(f"operation contract already exists: {name}")
    OPERATION_CONTRACTS[name] = contract
    # Keep a registered contract visible from the legacy capability object
    # when one already exists.  Reconstructing the frozen record preserves
    # all positional fields and does not change path/explicit semantics.
    capability = OPERATION_CAPABILITIES.get(name)
    if capability is not None:
        OPERATION_CAPABILITIES[name] = BlockCapability(
            operation=capability.operation,
            path=capability.path,
            automatic_safe=capability.automatic_safe,
            explicit_safe=capability.explicit_safe,
            min_halo=capability.min_halo,
            dependencies=capability.dependencies,
            reason=capability.reason,
            contract=contract,
        )
    return contract


def can_auto_block(
    name: str,
    backend: Optional[str] = None,
    *,
    contract: Optional[OperationContract] = None,
) -> bool:
    """Strict P3 automatic-block gate.

    Unlike :func:`is_auto_block_safe`, this helper requires an explicit
    operation contract and parity metadata.  It is intentionally the safe
    choice for new planners and diagnostics; the historical helper remains
    unchanged for compatibility with callers that already own an explicit
    parity decision.
    """
    candidate = contract if contract is not None else operation_contract(name)
    if not isinstance(candidate, OperationContract):
        return False
    return candidate.can_auto_block(backend)


def can_partition_block(
    name: str,
    backend: Optional[str] = None,
    *,
    adapter: Any = None,
    contract: Optional[OperationContract] = None,
    require_adapter: bool = True,
) -> bool:
    """Gate richer partition strategies without changing legacy selection.

    A partitioned operation may be shape-changing, reducing, multi-stage, or
    variable-cardinality.  Such operations are eligible only when an explicit
    qualified contract and a complete adapter (runner, validator, merger)
    exist, and backend parity is declared.  No built-in operation is promoted
    merely by this helper; all existing contracts default to
    ``partition_qualified=False``.

    ``require_adapter=False`` is available for metadata diagnostics, but the
    default is fail-closed and suitable for a runtime planner.
    """

    canonical = canonical_operation_name(name)
    candidate_adapter: Optional[BlockAdapter]
    if adapter is None:
        candidate_adapter = lookup_block_adapter(canonical)
    elif isinstance(adapter, BlockAdapter):
        candidate_adapter = adapter
    elif isinstance(adapter, Mapping):
        try:
            values = dict(adapter)
            aliases = {
                "input_reader": "reader",
                "run_tile": "runner",
                "validate_tile": "validator",
                "merge_tile": "merger",
            }
            for alias, target in aliases.items():
                if alias in values and target in values:
                    return False
                if alias in values:
                    values[target] = values.pop(alias)
            candidate_adapter = BlockAdapter(canonical, **values)
        except Exception:
            return False
    elif callable(adapter):
        candidate_adapter = BlockAdapter(canonical, runner=adapter)
    else:
        return False

    if require_adapter and candidate_adapter is None:
        return False

    # Prefer an explicitly supplied contract, then an adapter-local contract,
    # then the maintained operation contract.  The latter keeps registered
    # operation contracts useful without mutating them during lookup.
    candidate = contract
    if candidate is None and candidate_adapter is not None:
        candidate = candidate_adapter.contract
    if candidate is None:
        candidate = operation_contract(canonical)
    if not isinstance(candidate, OperationContract):
        return False
    if canonical_operation_name(candidate.operation) != canonical:
        return False
    if not candidate.can_partition(backend):
        return False

    if candidate_adapter is None:
        return not require_adapter
    if canonical_operation_name(candidate_adapter.operation) != canonical:
        return False
    if not candidate_adapter.partition_ready:
        return False
    if candidate_adapter.partition_strategy != candidate.partition_strategy:
        return False

    # Adapter-specific capability is preferred.  When it is omitted, the
    # qualified operation contract is the explicit backend evidence.  This is
    # intentionally not inferred from a wildcard artifact list.
    if candidate_adapter.backend_capability is not None:
        if not candidate_adapter.supports_backend(backend):
            return False
    elif candidate_adapter.contract is not None:
        if not candidate_adapter.supports_backend(backend):
            return False
    elif not candidate.supports_backend(backend, require_parity=True):
        return False
    return True


def _explicit_backend_parity(value: Any, backend: Optional[str] = None) -> bool:
    """Interpret an explicit parity declaration without guessing artifacts."""

    if value is None:
        return False
    if isinstance(value, Mapping):
        # Common record forms: {"parity_qualified": True},
        # {"cpu": True}, or {"cpu": {"parity": True}}.
        for key in ("parity_qualified", "parity", "validated", "passed"):
            if key in value and bool(value[key]):
                return True
        backend_name = str(backend or "").lower().strip()
        selected = value.get(backend_name, value.get("*")) if backend_name else value.get("*")
        if selected is None and backend_name:
            selected = value.get(backend)
        if isinstance(selected, Mapping):
            return any(
                bool(selected.get(key))
                for key in ("parity_qualified", "parity", "validated", "passed")
            )
        return bool(selected)
    return bool(value)


def _coerce_partition_adapter(operation: str, adapter: Any) -> Optional[BlockAdapter]:
    """Coerce a non-registered adapter for diagnostics without side effects."""

    if isinstance(adapter, BlockAdapter):
        return adapter
    canonical = canonical_operation_name(operation)
    if isinstance(adapter, Mapping):
        try:
            values = dict(adapter)
            aliases = {
                "input_reader": "reader",
                "run_tile": "runner",
                "validate_tile": "validator",
                "merge_tile": "merger",
            }
            for alias, target in aliases.items():
                if alias in values and target in values:
                    return None
                if alias in values:
                    values[target] = values.pop(alias)
            return BlockAdapter(canonical, **values)
        except Exception:
            return None
    if callable(adapter):
        return BlockAdapter(canonical, runner=adapter)
    return None


def can_auto_partition_dispatch(
    name: str,
    backend: Optional[str] = None,
    *,
    adapter: Any = None,
    contract: Optional[OperationContract] = None,
    parity_evidence: Any = None,
    require_native_evidence: bool = False,
    device: Optional[str] = None,
) -> bool:
    """Gate automatic dispatch for an evidence-backed legacy tile path.

    This gate is intentionally stricter than :func:`can_partition_block`:
    the operation must have a recorded legacy executor and either a complete
    explicit adapter/contract or an exact native evidence record for the
    maintained legacy path. It is diagnostic/opt-in only and is not consulted
    by the existing engine planner, so default behavior remains unchanged.
    Callers auditing native dispatch can set ``require_native_evidence=True``;
    that additional gate requires an exact command-backed backend/device
    record from :mod:`native_evidence` and never treats a semantic NumPy
    parity adapter as a native proof.
    """

    canonical = canonical_operation_name(name)
    evidence = _LEGACY_PARTITION_EVIDENCE.get(canonical)
    if evidence is None:
        return False
    candidate_adapter = (
        lookup_block_adapter(canonical)
        if adapter is None
        else _coerce_partition_adapter(canonical, adapter)
    )
    if candidate_adapter is None:
        # A maintained legacy executor is already the adapter for the native
        # path.  When the caller explicitly asks for native evidence, an
        # exact command-backed record plus the legacy strict contract is
        # sufficient; requiring a second semantic adapter would incorrectly
        # hide proven ``_run_blockwise``/stencil implementations.  This does
        # not alter dispatch by itself: callers still have to opt into this
        # diagnostic gate and supply the target backend/device.
        if not require_native_evidence:
            return False
        if not can_auto_block(canonical, backend):
            return False
        try:
            from .native_evidence import native_partition_evidence_supported

            return bool(
                native_partition_evidence_supported(
                    canonical, str(backend or ""), device
                )
            )
        except Exception:
            return False
    if not can_partition_block(
        canonical,
        backend,
        adapter=candidate_adapter,
        contract=contract,
        require_adapter=True,
    ):
        # A semantic adapter may intentionally be scoped to CPU (for example
        # the NumPy parity adapters).  Do not let that diagnostic registration
        # hide a separately verified native legacy executor for another
        # backend.  The fallback is only available for an explicit native
        # audit and still requires the strict operation contract plus an exact
        # backend/device evidence record.
        if require_native_evidence and can_auto_block(canonical, backend):
            try:
                from .native_evidence import native_partition_evidence_supported

                if native_partition_evidence_supported(
                    canonical, str(backend or ""), device
                ):
                    return True
            except Exception:
                pass
        return False

    metadata = dict(candidate_adapter.metadata or {})
    marker = metadata.get("legacy_partition_evidence")
    executor_marker = metadata.get("legacy_executor", metadata.get("executor"))
    if isinstance(marker, Mapping):
        if marker.get("operation") not in (None, canonical):
            return False
        if marker.get("executor") not in (None, evidence.executor):
            return False
        if parity_evidence is None:
            parity_evidence = marker.get(
                "parity_evidence",
                marker.get("parity_qualified", marker.get("parity")),
            )
    elif marker is not None and marker is not True and str(marker) not in {
        canonical,
        evidence.executor,
    }:
        return False
    if executor_marker not in (None, evidence.executor):
        return False
    if parity_evidence is None:
        parity_evidence = metadata.get(
            "parity_evidence",
            metadata.get(
                "full_frame_parity",
                metadata.get(
                    "legacy_parity_evidence", metadata.get("backend_parity")
                ),
            ),
        )
    if parity_evidence is None and evidence.supports_backend(backend):
        parity_evidence = True
    if not _explicit_backend_parity(parity_evidence, backend):
        return False
    if require_native_evidence:
        try:
            from .native_evidence import native_partition_evidence_supported

            selected_device = device
            if selected_device is None:
                metadata_device = metadata.get(
                    "native_evidence_device", metadata.get("device")
                )
                if metadata_device is not None:
                    selected_device = str(metadata_device)
            if not native_partition_evidence_supported(
                canonical, str(backend or ""), selected_device
            ):
                return False
        except Exception:
            # A missing or malformed evidence registry must fail closed when
            # the caller explicitly requests native qualification.
            return False
    return True


is_contract_auto_block_safe = can_auto_block
operation_allows_auto_block = can_auto_block
is_partition_block_safe = can_partition_block
operation_allows_partition_block = can_partition_block
is_legacy_partition_dispatch_safe = can_auto_partition_dispatch


def contract_allows_pipeline(name: str, backend: Optional[str] = None) -> bool:
    """Return whether metadata permits a recorded pipeline boundary."""
    candidate = operation_contract(name)
    return bool(candidate.allows_pipeline and candidate.supports_backend(backend, require_parity=False))


def should_use_contract_blocks(
    name: str,
    nbytes: int,
    config: BlockConfig,
    backend: Optional[str] = None,
) -> bool:
    """Strict variant of :func:`should_use_blocks` for new callers."""
    return bool(
        config.enabled
        and int(nbytes) >= config.threshold_bytes
        and can_auto_block(name, backend)
    )


def is_auto_block_safe(name: str) -> bool:
    """Whether adaptive memory pressure may enable blocking implicitly."""
    return operation_capability(name).automatic_safe


def should_use_blocks(name: str, nbytes: int, config: BlockConfig) -> bool:
    """True only for explicitly block-safe operations above the memory threshold."""
    capability = operation_capability(name)
    return bool(
        config.enabled
        and int(nbytes) >= config.threshold_bytes
        and capability.explicit_safe
    )


def checksum(data: Any) -> int:
    """Compute a lightweight checksum for CPU-backed block validation."""
    array = np.ascontiguousarray(data)
    return zlib.crc32(memoryview(array).cast("B")) & 0xFFFFFFFF


# Friendly aliases used by integrations that describe the same contract with
# slightly different terminology.  They are additive and intentionally point
# to the one maintained implementation above.
OperationShape = ShapeTransform
BlockPartitionStrategy = PartitionStrategy
OperationReduction = ReductionPolicy
OperationMerge = MergePolicy
BackendContract = BackendCapability
BlockOperationContract = OperationContract


__all__ = [
    "BlockSize", "BlockPath", "ShapeTransform", "OperationShape",
    "PartitionStrategy", "BlockPartitionStrategy",
    "HaloPolicy", "BorderPolicy", "ReductionPolicy", "OperationReduction",
    "MergePolicy", "OperationMerge", "BackendCapability", "BackendContract",
    "OperationContract", "BlockOperationContract", "BlockCapability",
    "BlockAdapter", "BlockOperationAdapter", "LegacyPartitionEvidence",
    "BlockState", "BlockConfig", "BlockSpec", "BlockGrid", "BlockRecord",
    "BlockCache", "OPERATION_PATHS", "AUTO_BLOCK_SAFE",
    "SHAPE_CHANGING_OPERATIONS", "OPERATION_CONTRACTS",
    "CANONICAL_OPERATION_ALIASES", "OPERATION_ALIASES",
    "LEGACY_PARTITION_EVIDENCE", "legacy_partition_evidence",
    "canonical_operation_name", "register_block_adapter",
    "lookup_block_adapter", "get_block_adapter", "registered_block_adapters",
    "block_coverage_report",
    "operation_path", "operation_capability", "operation_contract",
    "get_operation_contract", "operation_contracts", "register_operation_contract",
    "can_auto_block", "can_partition_block", "is_contract_auto_block_safe",
    "operation_allows_auto_block", "is_partition_block_safe",
    "can_auto_partition_dispatch", "is_legacy_partition_dispatch_safe",
    "operation_allows_partition_block",
    "contract_allows_pipeline", "is_auto_block_safe", "should_use_blocks",
    "should_use_contract_blocks", "normalize_block_size", "checksum",
]
