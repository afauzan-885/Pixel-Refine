"""Reusable raw-allocation policy for the AOT engine.

The allocator owns only reusable storage and byte-budget accounting.  Native
handle destruction is injected by the owning engine so this module does not
need to import bridge globals or make backend assumptions.
"""

from dataclasses import dataclass
import threading


@dataclass(frozen=True)
class BufferKey:
    """Physical allocation identity used by the reusable buffer pool."""

    size_bytes: int
    host_accessible: bool = False
    dtype: str = "raw"
    is_vector: bool = False
    vector_dim: int = 1
    usage: str = "storage"

    def __post_init__(self):
        if int(self.size_bytes) <= 0:
            raise ValueError("buffer allocation size must be positive")
        object.__setattr__(self, "size_bytes", int(self.size_bytes))
        object.__setattr__(self, "host_accessible", bool(self.host_accessible))
        object.__setattr__(self, "dtype", str(self.dtype or "raw"))
        object.__setattr__(self, "is_vector", bool(self.is_vector))
        object.__setattr__(self, "vector_dim", max(1, int(self.vector_dim)))
        object.__setattr__(self, "usage", str(self.usage or "storage"))


class BufferPool:
    """Bounded reusable allocation pool with backend-neutral ownership."""

    def __init__(self, engine=None, release_handle=None):
        self.engine = engine
        self._release_handle_callback = release_handle
        self.free_buffers = {}  # BufferKey -> list of handles
        self.max_bytes = 0
        self.pooled_bytes = 0
        self._stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0,
            "evictions": 0,
        }
        self._lock = threading.Lock()

    @staticmethod
    def _key(
        size_or_key,
        *,
        host_accessible=False,
        dtype="raw",
        is_vector=False,
        vector_dim=1,
        usage="storage",
    ):
        if isinstance(size_or_key, BufferKey):
            return size_or_key
        return BufferKey(
            int(size_or_key),
            host_accessible=host_accessible,
            dtype=dtype,
            is_vector=is_vector,
            vector_dim=vector_dim,
            usage=usage,
        )

    def _release_handle(self, handle):
        callback = self._release_handle_callback
        if callback is None and self.engine is not None:
            callback = getattr(self.engine, "_free_buffer_handle", None)
        if callback is not None:
            try:
                callback(handle)
            except Exception:
                pass

    def acquire(self, size_or_key, **kwargs):
        key = self._key(size_or_key, **kwargs)
        with self._lock:
            handles = self.free_buffers.get(key)
            if handles:
                handle = handles.pop()
                self.pooled_bytes = max(0, self.pooled_bytes - key.size_bytes)
                self._stats["hits"] += 1
                if not handles:
                    self.free_buffers.pop(key, None)
                return handle
            self._stats["misses"] += 1
            return None

    def store(self, size_or_key, handle, **kwargs):
        """Store a handle for reuse; evict it when the budget cannot fit."""
        key = self._key(size_or_key, **kwargs)
        with self._lock:
            size = key.size_bytes
            if self.max_bytes <= 0 or self.pooled_bytes + size > self.max_bytes:
                self._release_handle(handle)
                self._stats["evictions"] += 1
                return
            if key not in self.free_buffers:
                self.free_buffers[key] = []
            self.free_buffers[key].append(handle)
            self.pooled_bytes += size
            self._stats["stores"] += 1

    def set_budget(self, max_bytes):
        """Apply an adaptive cap and evict largest idle buffers first."""
        with self._lock:
            self.max_bytes = max(0, int(max_bytes))
            for key in sorted(
                tuple(self.free_buffers),
                key=lambda item: item.size_bytes,
                reverse=True,
            ):
                handles = self.free_buffers.get(key, [])
                while handles and self.pooled_bytes > self.max_bytes:
                    handle = handles.pop()
                    self._release_handle(handle)
                    self.pooled_bytes = max(0, self.pooled_bytes - key.size_bytes)
                    self._stats["evictions"] += 1
                if not handles:
                    self.free_buffers.pop(key, None)

    def clear(self):
        """Force-free all pooled handles after promoting retired handles."""
        # ``destroy()``/``release()`` may have placed handles in the engine's
        # retired queue rather than directly in this free-list. Preserve the
        # historical public meaning of ``buffer_pool.clear()`` by promoting
        # that queue first; the engine performs one synchronization only.
        if self.engine and hasattr(self.engine, "_drain_retired"):
            try:
                self.engine._drain_retired(wait=True)
            except Exception:
                pass
        with self._lock:
            for handles in self.free_buffers.values():
                for handle in handles:
                    self._release_handle(handle)
            self.free_buffers = {}
            self.pooled_bytes = 0

    def stats(self):
        with self._lock:
            requests = self._stats["hits"] + self._stats["misses"]
            return {
                **self._stats,
                "enabled": bool(
                    self.engine is None
                    or getattr(self.engine, "_buffer_cache_enabled", True)
                ),
                "hit_rate": (self._stats["hits"] / requests if requests else 0.0),
                "pooled_bytes": self.pooled_bytes,
                "max_bytes": self.max_bytes,
                "size_classes": len(self.free_buffers),
            }


__all__ = ["BufferKey", "BufferPool"]
