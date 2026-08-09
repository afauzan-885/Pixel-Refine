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

    def __post_init__(self) -> None:
        if not str(self.operation):
            raise ValueError("operation name must not be empty")
        if int(self.min_halo) < 0:
            raise ValueError("min_halo must be non-negative")
        if self.path == BlockPath.GLOBAL and self.explicit_safe:
            raise ValueError("global reductions cannot be block-explicit-safe")


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
