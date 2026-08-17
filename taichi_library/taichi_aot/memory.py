"""Realtime host-memory policy and cache telemetry for block execution."""

from __future__ import annotations

import ctypes
import math
import numbers
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import Callable, Mapping, Optional


MIB = 1024**2
GIB = 1024**3


class MemoryPressure(IntEnum):
    HEALTHY = 0
    CAUTIOUS = 1
    LOW = 2
    CRITICAL = 3
    EMERGENCY = 4


@dataclass(frozen=True)
class MemorySnapshot:
    total_bytes: int
    available_bytes: int
    timestamp: float

    @property
    def available_ratio(self):
        return self.available_bytes / max(1, self.total_bytes)


@dataclass(frozen=True)
class MemoryDecision:
    pressure: MemoryPressure
    host_cache_budget: int
    shared_device_budget: int
    device_pool_budget: int
    pipeline_resident_limit: int
    target_chunk_bytes: int
    recommended_block_size: int
    system_reserve_bytes: int
    device_heap_budget: int
    device_heap_usage: int
    device_heap_available: int
    device_budget_source: str
    allow_cache: bool
    allow_pinned_spill: bool
    allow_prefetch: bool
    max_concurrency: int
    snapshot: MemorySnapshot
    # Lifecycle allocations are deliberately separate from the reusable
    # device-pool budget.  Staging buffers are host-visible and retired
    # buffers are still owned by the native queue until a safe point; counting
    # them explicitly keeps a transient upload/readback burst from turning
    # into unbounded resident growth.
    staging_pool_budget: int = 0
    retired_buffer_budget: int = 0


def validate_memory_decision(decision) -> dict:
    """Return structural diagnostics for a memory-governor decision.

    This is deliberately a pure, backend-neutral contract check.  It does not
    change a decision or attempt to query a device, so callers can include the
    result in telemetry and tests without introducing allocation or dispatch
    side effects.  A failed check means the decision must not be treated as a
    trustworthy admission policy.
    """

    if isinstance(decision, MemoryDecision):
        values = asdict(decision)
    elif isinstance(decision, Mapping):
        values = dict(decision)
    else:
        return {
            "valid": False,
            "issues": ["decision must be MemoryDecision or mapping"],
        }

    issues = []

    def _strict_integer(value) -> Optional[int]:
        """Parse an integer without silently truncating probe metadata.

        The governor emits integers, but JSON/driver telemetry can contain
        booleans, fractional values, or non-finite floats.  ``int(value)``
        would accept some of those (for example ``True`` or ``1.5``), which
        could make an invalid budget appear safe.  Decimal integer strings
        remain accepted for compatibility with serialized reports.
        """

        if isinstance(value, bool):
            return None
        if isinstance(value, numbers.Integral):
            return int(value)
        if isinstance(value, numbers.Real):
            numeric = float(value)
            if math.isfinite(numeric) and numeric.is_integer():
                return int(numeric)
            return None
        if isinstance(value, str):
            try:
                return int(value.strip(), 10)
            except (TypeError, ValueError):
                return None
        return None
    nonnegative = (
        "host_cache_budget",
        "shared_device_budget",
        "device_pool_budget",
        "pipeline_resident_limit",
        "target_chunk_bytes",
        "recommended_block_size",
        "system_reserve_bytes",
        "device_heap_budget",
        "device_heap_usage",
        "device_heap_available",
        "staging_pool_budget",
        "retired_buffer_budget",
    )
    for name in nonnegative:
        if name not in values:
            continue
        parsed = _strict_integer(values[name])
        if parsed is None:
            issues.append(f"{name} must be an integer")
        elif parsed < 0:
            issues.append(f"{name} must be non-negative")

    def _int(name):
        parsed = _strict_integer(values.get(name, 0) or 0)
        return parsed if parsed is not None else 0

    shared = _int("shared_device_budget")
    pipeline = _int("pipeline_resident_limit")
    pool = _int("device_pool_budget")
    target = _int("target_chunk_bytes")
    lifecycle = _int("staging_pool_budget") + _int("retired_buffer_budget")
    if pipeline > shared and shared:
        issues.append("pipeline_resident_limit exceeds shared_device_budget")
    if pool > shared:
        issues.append("device_pool_budget exceeds shared_device_budget")
    if target > pipeline and pipeline:
        issues.append("target_chunk_bytes exceeds pipeline_resident_limit")
    if lifecycle > shared and shared:
        issues.append("lifecycle budgets exceed shared_device_budget")

    # A driver-reported heap sample is only a safe admission signal when its
    # counters are internally bounded.  Some providers return zero for the
    # heap budget when the extension is unavailable; in that case the
    # availability/usage fields are intentionally treated as advisory.  Once
    # a positive heap budget is present, a value above it is contradictory and
    # must fail closed instead of allowing an oversized resident allocation.
    device_heap_budget = _int("device_heap_budget")
    if device_heap_budget > 0:
        if _int("device_heap_usage") > device_heap_budget:
            issues.append("device_heap_usage exceeds device_heap_budget")
        if _int("device_heap_available") > device_heap_budget:
            issues.append("device_heap_available exceeds device_heap_budget")

    block = _int("recommended_block_size")
    if block and (block < 256 or block > 2048):
        issues.append("recommended_block_size is outside the 256..2048 contract")

    # Snapshot counters are part of the admission telemetry.  They must be
    # internally consistent before a caller treats the decision as reliable;
    # an available value above total would otherwise produce an impossible
    # ratio and could over-admit shared-memory work.
    snapshot_present = "snapshot" in values
    snapshot = values.get("snapshot")
    if isinstance(snapshot, MemorySnapshot):
        snapshot_values = {
            "total_bytes": snapshot.total_bytes,
            "available_bytes": snapshot.available_bytes,
            "timestamp": snapshot.timestamp,
        }
    elif isinstance(snapshot, Mapping):
        snapshot_values = snapshot
    else:
        snapshot_values = None
        if snapshot_present:
            issues.append(
                "snapshot must be MemorySnapshot or mapping when provided"
            )
    if snapshot_values is not None:
        total = _strict_integer(snapshot_values.get("total_bytes"))
        available = _strict_integer(snapshot_values.get("available_bytes"))
        if total is None or total < 0:
            issues.append("snapshot.total_bytes must be a non-negative integer")
        if available is None or available < 0:
            issues.append("snapshot.available_bytes must be a non-negative integer")
        if total is not None and available is not None and available > total:
            issues.append("snapshot.available_bytes exceeds snapshot.total_bytes")
        # ``timestamp`` is telemetry rather than an admission counter, so
        # legacy mapping payloads may omit it.  When a producer supplies it,
        # however, NaN/inf (or another non-numeric value) makes freshness and
        # watchdog decisions unknowable and must fail closed.  Do not impose
        # a wall-clock/monotonic-origin policy here; only require a finite
        # numeric value to remain compatible with existing adapters.
        if "timestamp" in snapshot_values:
            raw_timestamp = snapshot_values.get("timestamp")
            if isinstance(raw_timestamp, bool):
                timestamp = None
            else:
                try:
                    timestamp = float(raw_timestamp)
                except (TypeError, ValueError):
                    timestamp = None
            if timestamp is None or not math.isfinite(timestamp):
                issues.append("snapshot.timestamp must be finite when provided")

    return {
        "valid": not issues,
        "issues": issues,
        "checked_fields": len(nonnegative),
    }


class CacheTelemetry:
    """Thread-safe counters with a deliberately small public surface."""

    def __init__(self):
        self._lock = threading.Lock()
        self._counters = {
            "hits": 0,
            "misses": 0,
            "admissions": 0,
            "admission_rejects": 0,
            "evictions": 0,
            "invalidations": 0,
            "bytes_admitted": 0,
            "bytes_evicted": 0,
        }

    def add(self, name, value=1):
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + int(value)

    def snapshot(self):
        with self._lock:
            return dict(self._counters)

    def reset(self):
        with self._lock:
            for name in self._counters:
                self._counters[name] = 0


def _choose_block_size(
    target_chunk_bytes: int,
    *,
    pressure: MemoryPressure,
    shared_budget: int,
    channels: int = 3,
    sample_bytes: int = 4,
    live_buffers: int = 4,
) -> int:
    """Choose a bounded square block for the current memory decision.

    The previous policy assumed every operation was four live RGB-f32
    buffers.  That was safe but unnecessarily conservative for grayscale or
    two-channel work.  Keep the same hard candidate cap while deriving the
    resident estimate from the actual operation shape/dtype supplied by the
    planner.
    """

    if shared_budget <= 0:
        return 256 if pressure >= MemoryPressure.CRITICAL else 512

    # Pressure is an admission signal as well as a budget signal.  A large
    # target chunk can still mathematically fit a 2048 tile while the host or
    # device is already under pressure; retaining that tile would increase
    # transient peaks and make recovery less predictable.  Keep the policy
    # monotonic and bounded: healthy may use the full native cap, while each
    # pressure tier lowers the maximum independently of dtype/shape math.
    if pressure >= MemoryPressure.EMERGENCY:
        pressure_cap = 256
    elif pressure >= MemoryPressure.CRITICAL:
        pressure_cap = 512
    elif pressure >= MemoryPressure.LOW:
        pressure_cap = 1024
    elif pressure >= MemoryPressure.CAUTIOUS:
        pressure_cap = 1536
    else:
        pressure_cap = 2048
    channels = max(1, int(channels))
    sample_bytes = max(1, int(sample_bytes))
    live_buffers = max(1, int(live_buffers))
    bytes_per_pixel = channels * sample_bytes * live_buffers
    max_side = int((max(0, int(target_chunk_bytes)) / max(1, bytes_per_pixel)) ** 0.5)
    for candidate in (2048, 1536, 1024, 768, 512, 256):
        if candidate > pressure_cap:
            continue
        if candidate <= max_side:
            return candidate
    return 256


def system_memory_snapshot():
    """Read physical-memory availability without adding a psutil dependency."""
    if sys.platform == "win32":

        class MemoryStatusEx(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatusEx()
        status.dwLength = ctypes.sizeof(status)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            raise OSError("GlobalMemoryStatusEx failed")
        return MemorySnapshot(
            int(status.ullTotalPhys), int(status.ullAvailPhys), time.monotonic()
        )

    page_size = int(os.sysconf("SC_PAGE_SIZE"))
    total = page_size * int(os.sysconf("SC_PHYS_PAGES"))
    available = page_size * int(os.sysconf("SC_AVPHYS_PAGES"))
    return MemorySnapshot(total, available, time.monotonic())


class MemoryGovernor:
    """Converts realtime RAM availability into stable cache-admission policy."""

    def __init__(
        self,
        provider: Callable[[], MemorySnapshot] = system_memory_snapshot,
        configured_max_bytes: Optional[int] = None,
        sample_interval=0.5,
        device_provider: Optional[Callable[[], dict]] = None,
        device_sample_interval=2.0,
    ):
        self.provider = provider
        self.configured_max_bytes = configured_max_bytes
        self.sample_interval = max(0.05, float(sample_interval))
        self.device_provider = device_provider
        self.device_sample_interval = max(0.25, float(device_sample_interval))
        self._device_sample = None
        self._device_sample_time = 0.0
        self._lock = threading.Lock()
        self._decision = None
        self._pressure = MemoryPressure.HEALTHY

    def configure(self, configured_max_bytes=None):
        with self._lock:
            self.configured_max_bytes = configured_max_bytes
            self._decision = None

    def _read_device_budget(self, now):
        if self.device_provider is None:
            return None
        if (
            self._device_sample is not None
            and now - self._device_sample_time < self.device_sample_interval
        ):
            return self._device_sample
        try:
            sample = self.device_provider()
            if not isinstance(sample, dict):
                sample = None
        except Exception:
            sample = None
        self._device_sample = sample
        self._device_sample_time = now
        return sample

    def _classify(self, snapshot):
        ratio = snapshot.available_ratio
        absolute = snapshot.available_bytes
        current = self._pressure
        if absolute < 512 * 1024**2 or ratio < 0.05:
            return MemoryPressure.EMERGENCY
        if absolute < GIB or ratio < 0.08:
            return MemoryPressure.CRITICAL
        if current >= MemoryPressure.LOW:
            if ratio < 0.19 or absolute < 2 * GIB:
                return MemoryPressure.LOW
        elif ratio < 0.15 or absolute < 1536 * 1024**2:
            return MemoryPressure.LOW
        if current >= MemoryPressure.CAUTIOUS:
            if ratio < 0.28:
                return MemoryPressure.CAUTIOUS
        elif ratio < 0.25:
            return MemoryPressure.CAUTIOUS
        return MemoryPressure.HEALTHY

    def refresh(self, force=False):
        with self._lock:
            now = time.monotonic()
            if (
                not force
                and self._decision is not None
                and now - self._decision.snapshot.timestamp < self.sample_interval
            ):
                return self._decision
            snapshot = self.provider()
            pressure = self._classify(snapshot)
            device = self._read_device_budget(now)
            device_heap_budget = int((device or {}).get("device_local_budget", 0) or 0)
            device_heap_usage = int((device or {}).get("device_local_usage", 0) or 0)
            device_heap_available = int(
                (device or {}).get("device_local_available", 0) or 0
            )
            device_budget_source = (
                "vk_ext_memory_budget"
                if (device or {}).get("supported")
                else ("vulkan_heap_size" if device else "system_memory")
            )
            if device:
                ratio = device_heap_available / max(1, device_heap_budget)
                if device_heap_available < 512 * 1024**2 or ratio < 0.08:
                    pressure = max(pressure, MemoryPressure.LOW)
                elif device_heap_available < GIB or ratio < 0.15:
                    pressure = max(pressure, MemoryPressure.CAUTIOUS)
            self._pressure = pressure
            # Shared-memory GPUs compete with the OS and applications for the
            # same physical RAM. Reserve enough headroom for Windows, the
            # display compositor, and driver-private allocations.
            reserve = max(int(snapshot.total_bytes * 0.20), 4 * GIB)
            safe_available = max(0, snapshot.available_bytes - reserve)
            configured = self.configured_max_bytes
            if configured is None:
                configured = int(snapshot.total_bytes * 0.15)
            budget = min(
                int(configured),
                int(snapshot.total_bytes * 0.15),
                int(safe_available * 0.35),
            )

            configured_shared = os.environ.get("AOT_SHARED_MEMORY_MAX")
            try:
                configured_shared = (
                    int(configured_shared) if configured_shared is not None else 6 * GIB
                )
            except ValueError:
                configured_shared = 6 * GIB
            shared_budget = min(
                configured_shared,
                int(snapshot.total_bytes * 0.35),
                int(safe_available * 0.45),
            )
            if device_heap_available:
                # Keep 30% of the driver-reported available heap for display,
                # command buffers, pipeline internals, and other applications.
                shared_budget = min(shared_budget, int(device_heap_available * 0.70))
            if pressure == MemoryPressure.CAUTIOUS:
                budget //= 2
                shared_budget //= 2
            elif pressure >= MemoryPressure.LOW:
                budget = 0
                shared_budget = min(shared_budget, 512 * 1024**2)

            if pressure >= MemoryPressure.CRITICAL:
                shared_budget = 0

            # Keep a large reserve for the driver/display while allowing one
            # 24 MP full-frame graph to use more than the old fixed 25% share.
            # The shared budget above is already limited by available RAM,
            # current pressure, and (when exposed) the physical-device heap.
            # Vulkan's memory-budget extension reports the actual free heap;
            # multiplying that value by only 0.55 again was unnecessarily
            # conservative on 2 GB GPUs (a 24 MP graph needs about 1.07 GB).
            # Give a measured Vulkan heap a bounded 1.5 GB resident ceiling,
            # while retaining the stricter shared-memory rule for CUDA/CPU
            # paths that do not expose device-local availability.
            if shared_budget:
                pipeline_fraction = (
                    # A 24 MP RGB graph observed in production needs about
                    # 0.92 GiB resident.  Keep the one-gigabyte hard cap,
                    # but do not reject that graph merely because the
                    # shared-memory budget is just below 2.3 GiB.
                    0.55
                    if pressure == MemoryPressure.HEALTHY
                    else 0.40
                )
                if (
                    device_heap_available
                    and device_budget_source == "vk_ext_memory_budget"
                    and pressure == MemoryPressure.HEALTHY
                ):
                    measured_limit = max(
                        int(shared_budget * 0.85),
                        int(device_heap_available * 0.65),
                    )
                    pipeline_limit = min(
                        1536 * 1024**2,
                        max(256 * 1024**2, measured_limit),
                    )
                else:
                    pipeline_limit = min(
                        1024 * 1024**2,
                        max(
                            256 * 1024**2,
                            int(shared_budget * pipeline_fraction),
                        ),
                    )
                pool_budget = min(512 * 1024**2, int(shared_budget * 0.15))
                target_chunk = min(
                    int(pipeline_limit * 0.70),
                    int(shared_budget * 0.35),
                )
            else:
                pipeline_limit = 256 * 1024**2
                pool_budget = 0
                target_chunk = 64 * 1024**2

            # Keep lifecycle storage bounded independently of the long-lived
            # buffer pool.  A staging allocation may be larger than this
            # budget while leased (it cannot be evicted safely), but once it
            # is released the engine trims idle entries at the next safe
            # point.  Retired allocations receive a separate queue budget so
            # a frame burst cannot keep every old handle alive indefinitely.
            # The lower bounds avoid making a healthy small workload churn
            # one tiny staging slot, while a zero shared budget (critical
            # pressure) remains fail-closed and trims all idle lifecycle data.
            lifecycle_budget = int(max(0, shared_budget) * 0.20)
            if lifecycle_budget:
                staging_budget = min(
                    256 * 1024**2,
                    max(16 * 1024**2, int(lifecycle_budget * 0.40)),
                )
                retired_budget = min(
                    256 * 1024**2,
                    max(32 * 1024**2, int(lifecycle_budget * 0.60)),
                )
            else:
                staging_budget = 0
                retired_budget = 0

            # Preserve a conservative RGB-f32 default for telemetry.  The
            # operation planner can request a shape-aware recommendation via
            # ``recommend_block_size`` below.
            recommended = _choose_block_size(
                target_chunk,
                pressure=pressure,
                shared_budget=shared_budget,
                channels=3,
                sample_bytes=4,
                live_buffers=4,
            )
            allow_cache = budget > 0 and pressure < MemoryPressure.LOW
            self._decision = MemoryDecision(
                pressure=pressure,
                host_cache_budget=max(0, budget),
                shared_device_budget=max(0, shared_budget),
                device_pool_budget=max(0, pool_budget),
                pipeline_resident_limit=max(0, pipeline_limit),
                target_chunk_bytes=max(0, target_chunk),
                recommended_block_size=recommended,
                system_reserve_bytes=reserve,
                device_heap_budget=max(0, device_heap_budget),
                device_heap_usage=max(0, device_heap_usage),
                device_heap_available=max(0, device_heap_available),
                device_budget_source=device_budget_source,
                allow_cache=allow_cache,
                allow_pinned_spill=pressure <= MemoryPressure.CAUTIOUS,
                allow_prefetch=pressure == MemoryPressure.HEALTHY,
                max_concurrency=(
                    4
                    if pressure == MemoryPressure.HEALTHY
                    else (2 if pressure == MemoryPressure.CAUTIOUS else 1)
                ),
                snapshot=snapshot,
                staging_pool_budget=max(0, int(staging_budget)),
                retired_buffer_budget=max(0, int(retired_budget)),
            )
            return self._decision

    def recommend_block_size(
        self,
        *,
        channels: int = 3,
        sample_bytes: int = 4,
        live_buffers: int = 4,
        force: bool = False,
    ) -> int:
        """Return a shape-aware block side without changing public APIs.

        ``refresh()`` remains the single source of truth for pressure and
        budgets.  This helper only refines the block-size estimate for the
        current operation, allowing grayscale/f16/i16 workloads to use more of
        an iGPU's safe shared-memory budget while retaining the 2048 hard cap.
        """

        decision = self.refresh(force=force)
        return _choose_block_size(
            decision.target_chunk_bytes,
            pressure=decision.pressure,
            shared_budget=decision.shared_device_budget,
            channels=channels,
            sample_bytes=sample_bytes,
            live_buffers=live_buffers,
        )

    def snapshot(self, force=False):
        decision = self.refresh(force=force)
        result = asdict(decision)
        result["pressure"] = decision.pressure.name.lower()
        result["residency_depth"] = int(result.get("max_concurrency", 1) or 1)
        result["concurrency_verified"] = False
        return result
