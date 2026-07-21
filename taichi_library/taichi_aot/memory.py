"""Realtime host-memory policy and cache telemetry for block execution."""

from __future__ import annotations

import ctypes
import os
import sys
import threading
import time
from dataclasses import asdict, dataclass
from enum import IntEnum
from typing import Callable, Optional


GIB = 1024 ** 3


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
    allow_cache: bool
    allow_pinned_spill: bool
    allow_prefetch: bool
    max_concurrency: int
    snapshot: MemorySnapshot


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
        return MemorySnapshot(int(status.ullTotalPhys), int(status.ullAvailPhys), time.monotonic())

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
    ):
        self.provider = provider
        self.configured_max_bytes = configured_max_bytes
        self.sample_interval = max(0.05, float(sample_interval))
        self._lock = threading.Lock()
        self._decision = None
        self._pressure = MemoryPressure.HEALTHY

    def configure(self, configured_max_bytes=None):
        with self._lock:
            self.configured_max_bytes = configured_max_bytes
            self._decision = None

    def _classify(self, snapshot):
        ratio = snapshot.available_ratio
        absolute = snapshot.available_bytes
        current = self._pressure
        if absolute < 512 * 1024 ** 2 or ratio < 0.05:
            return MemoryPressure.EMERGENCY
        if absolute < GIB or ratio < 0.08:
            return MemoryPressure.CRITICAL
        if current >= MemoryPressure.LOW:
            if ratio < 0.19 or absolute < 2 * GIB:
                return MemoryPressure.LOW
        elif ratio < 0.15 or absolute < 1536 * 1024 ** 2:
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
            self._pressure = pressure
            reserve = max(int(snapshot.total_bytes * 0.10), int(1.5 * GIB))
            safe_available = max(0, snapshot.available_bytes - reserve)
            configured = self.configured_max_bytes
            if configured is None:
                configured = int(snapshot.total_bytes * 0.15)
            budget = min(int(configured), int(snapshot.total_bytes * 0.15), int(safe_available * 0.35))
            if pressure == MemoryPressure.CAUTIOUS:
                budget //= 2
            elif pressure >= MemoryPressure.LOW:
                budget = 0
            allow_cache = budget > 0 and pressure < MemoryPressure.LOW
            self._decision = MemoryDecision(
                pressure=pressure,
                host_cache_budget=max(0, budget),
                allow_cache=allow_cache,
                allow_pinned_spill=pressure <= MemoryPressure.CAUTIOUS,
                allow_prefetch=pressure == MemoryPressure.HEALTHY,
                max_concurrency=4 if pressure == MemoryPressure.HEALTHY else (2 if pressure == MemoryPressure.CAUTIOUS else 1),
                snapshot=snapshot,
            )
            return self._decision

    def snapshot(self, force=False):
        decision = self.refresh(force=force)
        result = asdict(decision)
        result["pressure"] = decision.pressure.name.lower()
        return result
