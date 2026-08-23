"""Lease-safe, byte-budgeted device residency primitives."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import count
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Reservation:
    soft_bytes: int = 0
    hard_bytes: Optional[int] = None
    weight: float = 1.0

    def __post_init__(self):
        if self.soft_bytes < 0 or (self.hard_bytes is not None and self.hard_bytes < self.soft_bytes):
            raise ValueError("reservation requires 0 <= soft_bytes <= hard_bytes")
        if self.weight <= 0:
            raise ValueError("reservation weight must be positive")


@dataclass
class ResidentEntry:
    key: str
    owner: str
    buffer: Any
    size_bytes: int
    generation: int = 0
    ref_count: int = 0
    pin_count: int = 0
    hit_count: int = 0
    last_access: float = 0.0
    dispose: Optional[Callable[[Any], None]] = None
    fence_ready: Optional[Callable[[], bool]] = None
    checksum: Any = None
    source_checksum: Any = None
    invalidated: bool = False

    @property
    def leased(self):
        return self.ref_count > 0 or self.pin_count > 0

    def can_evict(self):
        """Return whether disposal is safe, conservatively on fence errors.

        Fence callbacks are supplied by native runtimes and may transiently
        fail while a device/queue is being torn down.  An exception must never
        make cache maintenance dispose an in-flight buffer; treat it as
        ``not ready`` and let a later maintenance pass retry the callback.
        """
        if self.leased:
            return False
        if self.fence_ready is None:
            return True
        try:
            return bool(self.fence_ready())
        except Exception:
            return False


class DeviceResidencyCache:
    """Generic GPU-buffer cache; native ownership stays behind dispose callbacks."""

    def __init__(self, max_bytes=0):
        self.max_bytes = max(0, int(max_bytes))
        self._entries = OrderedDict()
        self._reservations = {}
        self._owner_bytes = {}
        self._size_bytes = 0
        self._generation = count(1)
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "admissions": 0, "rejects": 0,
                       "evictions": 0, "bytes_evicted": 0}

    @property
    def size_bytes(self):
        with self._lock:
            return self._size_bytes

    def configure_owner(self, owner, soft_bytes=0, hard_bytes=None, weight=1.0):
        with self._lock:
            self._reservations[str(owner)] = Reservation(
                int(soft_bytes), None if hard_bytes is None else int(hard_bytes), float(weight)
            )

    def set_budget(self, max_bytes):
        with self._lock:
            self.max_bytes = max(0, int(max_bytes))
            self._collect(0)

    def _owner_usage(self, owner):
        return self._owner_bytes.get(owner, 0)

    def _reservation(self, owner, requesting_owner=None):
        configured = self._reservations.get(owner)
        if configured is not None:
            return configured
        active = {name for name, size in self._owner_bytes.items() if size > 0}
        active.add(str(requesting_owner or owner))
        automatic = [name for name in active if name not in self._reservations]
        configured_soft = sum(
            reservation.soft_bytes
            for name, reservation in self._reservations.items()
            if name in active
        )
        available = max(0, self.max_bytes - configured_soft)
        soft = available // max(1, len(automatic))
        return Reservation(soft_bytes=soft, hard_bytes=self.max_bytes)

    def _eviction_candidates(self, requesting_owner):
        def priority(item):
            _, entry = item
            reservation = self._reservation(entry.owner, requesting_owner)
            borrowed = self._owner_usage(entry.owner) > reservation.soft_bytes
            same_owner = entry.owner == requesting_owner
            return (not borrowed, not same_owner, entry.hit_count, entry.last_access)
        return sorted(self._entries.items(), key=priority)

    def _evict(self, key, entry):
        self._entries.pop(key, None)
        self._size_bytes -= entry.size_bytes
        self._owner_bytes[entry.owner] = max(0, self._owner_usage(entry.owner) - entry.size_bytes)
        self._stats["evictions"] += 1
        self._stats["bytes_evicted"] += entry.size_bytes
        if entry.dispose is not None:
            entry.dispose(entry.buffer)

    def _collect(self, incoming_bytes, requesting_owner=""):
        for key, entry in self._eviction_candidates(requesting_owner):
            if self._size_bytes + incoming_bytes <= self.max_bytes:
                break
            if entry.can_evict():
                self._evict(key, entry)
        return self._size_bytes + incoming_bytes <= self.max_bytes

    def put(
        self, key, owner, buffer, size_bytes, dispose=None, fence_ready=None,
        checksum=None, source_checksum=None,
    ):
        key, owner, size_bytes = str(key), str(owner), int(size_bytes)
        if size_bytes <= 0:
            raise ValueError("resident entry size must be positive")
        with self._lock:
            reservation = self._reservation(owner, owner)
            if (
                self.max_bytes == 0
                or size_bytes > self.max_bytes
                or (reservation.hard_bytes is not None
                    and self._owner_usage(owner) + size_bytes > reservation.hard_bytes)
            ):
                self._stats["rejects"] += 1
                return None
            previous = self._entries.get(key)
            if previous is not None:
                # A producer fence is an ownership boundary even when no
                # Python lease is active yet.  Replacing an entry before its
                # fence signals would dispose an in-flight native buffer and
                # can race the queue.  Keep the old entry until it is safe;
                # the caller can retry admission after synchronization.
                if not previous.can_evict():
                    self._stats["rejects"] += 1
                    return None
                self._evict(key, previous)
            if not self._collect(size_bytes, owner):
                self._stats["rejects"] += 1
                return None
            entry = ResidentEntry(
                key, owner, buffer, size_bytes,
                generation=next(self._generation), last_access=time.monotonic(),
                dispose=dispose, fence_ready=fence_ready,
                checksum=checksum, source_checksum=source_checksum,
            )
            self._entries[key] = entry
            self._size_bytes += size_bytes
            self._owner_bytes[owner] = self._owner_usage(owner) + size_bytes
            self._stats["admissions"] += 1
            return entry

    def peek(self, key):
        with self._lock:
            return self._entries.get(str(key))

    def invalidate(self, key):
        with self._lock:
            entry = self._entries.get(str(key))
            # Invalidation disposes the native payload immediately.  Treat
            # both active leases and an unsignalled/failed producer fence as
            # non-evictable so explicit invalidation cannot race the queue.
            if entry is None or not entry.can_evict():
                return False
            self._evict(str(key), entry)
            return True

    def invalidate_owner(self, owner):
        """Evict idle resident entries owned by a quarantined operation."""
        owner = str(owner)
        invalidated = 0
        with self._lock:
            for key, entry in list(self._entries.items()):
                if entry.owner != owner:
                    continue
                # Do not dispose a buffer while another dispatch still leases
                # it. Mark it stale instead; ``lease`` removes it as soon as
                # the last consumer releases the entry.
                if not entry.can_evict():
                    entry.invalidated = True
                    invalidated += 1
                    continue
                self._evict(key, entry)
                invalidated += 1
        return invalidated

    def get(self, key):
        with self._lock:
            entry = self._entries.get(str(key))
            if entry is None or entry.invalidated:
                if entry is not None and entry.can_evict():
                    self._evict(str(key), entry)
                self._stats["misses"] += 1
                return None
            if entry.fence_ready is not None:
                try:
                    ready = bool(entry.fence_ready())
                except Exception:
                    ready = False
                if not ready:
                    # The producer has not signalled completion yet. Keep the
                    # entry resident, but do not hand its native handle to a
                    # consumer that could race the upload/dispatch.
                    self._stats["misses"] += 1
                    return None
            entry.hit_count += 1
            entry.last_access = time.monotonic()
            self._entries.move_to_end(str(key))
            self._stats["hits"] += 1
            return entry

    @contextmanager
    def lease(self, key):
        with self._lock:
            entry = self.get(key)
            if entry is not None:
                entry.ref_count += 1
                generation = entry.generation
            else:
                generation = None
        if entry is None:
            yield None
            return
        try:
            yield entry
        finally:
            with self._lock:
                current = self._entries.get(str(key))
                if current is not None and current.generation == generation:
                    current.ref_count = max(0, current.ref_count - 1)
                    if current.invalidated and current.can_evict():
                        self._evict(str(key), current)

    def clear(self):
        with self._lock:
            for key, entry in list(self._entries.items()):
                if entry.can_evict():
                    self._evict(key, entry)

    def stats(self):
        with self._lock:
            return {
                **self._stats,
                "entries": len(self._entries),
                "size_bytes": self._size_bytes,
                "max_bytes": self.max_bytes,
                "owner_bytes": dict(self._owner_bytes),
            }
