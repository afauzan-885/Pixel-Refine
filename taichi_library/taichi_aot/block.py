"""Internal block-processing primitives for the Taichi AOT runtime.

This module is intentionally independent from ``engine.py``.  It defines the
stable bookkeeping needed by future GPU block transfers while keeping existing
public algorithms on their current full-frame path until they opt in.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from hashlib import blake2b
from itertools import count
from typing import Any, Iterator, Mapping, Optional, Sequence, Tuple, Union
import threading
import math
import zlib

import numpy as np


BlockSize = Union[int, Tuple[int, int]]


class BlockPath(str, Enum):
    """How an operation can safely be evaluated."""

    DIRECT = "direct"
    BLOCK = "block"
    BLOCK_BORDER = "block_border"
    GLOBAL = "global"
    CUSTOM = "custom"


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
            self._size_bytes -= self.data_nbytes(record.data)
            owner = str(record.owner or "default")
            self._owner_bytes[owner] = max(
                0, self._owner_bytes.get(owner, 0) - self.data_nbytes(record.data)
            )
            record.state = BlockState.CORRUPT
            record.data = None
            record.checksum = None
            record.dirty = False
            if self._telemetry is not None:
                self._telemetry.add("invalidations")
            return True

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
    "resize": BlockPath.BLOCK,
    "image_pyramid": BlockPath.BLOCK,
    "remap": BlockPath.BLOCK,
    "remap_with_flow": BlockPath.BLOCK,
    "warp_perspective": BlockPath.BLOCK,
    "hamilton_demosaic": BlockPath.BLOCK_BORDER,
    "arm_demosaic": BlockPath.BLOCK_BORDER,
    "hamilton_demosaic_1channel": BlockPath.BLOCK_BORDER,
    "hamilton_demosaic_half_res": BlockPath.BLOCK,
    "hamilton_demosaic_rgb_half_res": BlockPath.BLOCK,
    "hamilton_demosaic_3channel": BlockPath.BLOCK_BORDER,
    "arm_demosaic_1channel": BlockPath.BLOCK_BORDER,
    "arm_demosaic_half_res": BlockPath.BLOCK,
    "arm_demosaic_rgb_half_res": BlockPath.BLOCK,
    "pure_arm_demosaic": BlockPath.BLOCK_BORDER,
    "farneback_flow": BlockPath.BLOCK_BORDER,
    "lucas_kanade": BlockPath.BLOCK_BORDER,
    "block_matching": BlockPath.BLOCK_BORDER,
    "fft": BlockPath.GLOBAL,
    "histogram": BlockPath.GLOBAL,
}


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


def should_use_blocks(name: str, nbytes: int, config: BlockConfig) -> bool:
    """True only for explicitly block-safe operations above the memory threshold."""
    path = operation_path(name)
    return bool(
        config.enabled
        and int(nbytes) >= config.threshold_bytes
        and path in (BlockPath.BLOCK, BlockPath.BLOCK_BORDER)
    )


def checksum(data: Any) -> int:
    """Compute a lightweight checksum for CPU-backed block validation."""
    array = np.ascontiguousarray(data)
    return zlib.crc32(memoryview(array).cast("B")) & 0xFFFFFFFF
