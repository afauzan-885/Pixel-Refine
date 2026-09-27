"""Backend-neutral lifecycle policies for reusable transient allocations."""

import weakref


class LiveBufferRegistry:
    """Weak ownership registry for wrappers tied to one engine generation."""

    def __init__(self):
        self._buffers = weakref.WeakSet()

    def add(self, buffer):
        self._buffers.add(buffer)

    def discard(self, buffer):
        self._buffers.discard(buffer)

    def snapshot(self):
        return tuple(self._buffers)

    def __iter__(self):
        return iter(self._buffers)

    def __len__(self):
        return len(self._buffers)


class LifecycleManager:
    """Own lifecycle budgets while the engine retains native fence ownership.

    This first extraction is deliberately policy-focused.  The AOT engine
    still owns synchronization, native queue fences, and wrapper invalidation;
    this object centralizes the mutable limits and safe trim/accounting rules
    so those responsibilities can be moved behind a stronger boundary later.
    """

    def __init__(
        self,
        *,
        staging_budget=0,
        retired_budget=0,
        max_staging_entries=1,
        max_retired_entries=1,
    ):
        self.staging_budget = max(0, int(staging_budget or 0))
        self.retired_budget = max(0, int(retired_budget or 0))
        self.max_staging_entries = max(1, int(max_staging_entries or 1))
        self.max_retired_entries = max(1, int(max_retired_entries or 1))

    def configure(
        self,
        *,
        staging_budget=None,
        retired_budget=None,
        max_staging_entries=None,
        max_retired_entries=None,
    ):
        """Update limits without touching any allocation or native handle."""
        if staging_budget is not None:
            self.staging_budget = max(0, int(staging_budget or 0))
        if retired_budget is not None:
            self.retired_budget = max(0, int(retired_budget or 0))
        if max_staging_entries is not None:
            self.max_staging_entries = max(1, int(max_staging_entries or 1))
        if max_retired_entries is not None:
            self.max_retired_entries = max(1, int(max_retired_entries or 1))
        return self

    def retired_over_budget(self, *, bytes_used, count):
        """Return whether the retired queue requires a safe-point drain."""
        return (
            int(bytes_used or 0) > self.retired_budget
            or int(count or 0) > self.max_retired_entries
        )

    def trim_staging(self, pool, *, destroy):
        """Trim idle staging entries using the currently configured limits."""
        return trim_idle_staging_entries(
            pool,
            max_entries=self.max_staging_entries,
            max_bytes=self.staging_budget,
            destroy=destroy,
        )

    @staticmethod
    def retired_bytes(entries):
        return retired_bytes(entries)


def trim_idle_staging_entries(pool, *, max_entries, max_bytes, destroy):
    """Trim oldest unleased staging entries until count/bytes are bounded.

    ``pool`` is the engine's existing ``dict[key, list[entry]]`` shape.  The
    helper intentionally does not synchronize or inspect native handles;
    callers choose the safe point and provide the destruction callback.
    Leased entries are never removed, even when the budget is exceeded.
    """
    if not pool:
        return 0

    max_entries = max(0, int(max_entries))
    max_bytes = max(0, int(max_bytes))
    removed = 0

    def entries():
        for key, bucket in tuple(pool.items()):
            for entry in tuple(bucket):
                yield key, bucket, entry

    def totals():
        all_entries = list(entries())
        return len(all_entries), sum(
            int(getattr(item.get("buffer"), "size_bytes", 0) or 0)
            for _, _, item in all_entries
        )

    while True:
        count, resident = totals()
        if count <= max_entries and resident <= max_bytes:
            break
        candidates = [
            (float(item.get("last_used", 0.0) or 0.0), key, bucket, item)
            for key, bucket, item in entries()
            if not item.get("leased", False)
        ]
        if not candidates:
            break
        _, key, bucket, entry = min(candidates, key=lambda item: item[0])
        try:
            bucket.remove(entry)
        except ValueError:
            continue
        if not bucket:
            pool.pop(key, None)
        buffer = entry.get("buffer")
        if buffer is not None:
            try:
                destroy(buffer)
            except Exception:
                # Lifecycle trimming is best effort; dropping the pool
                # reference still bounds Python-side retention.
                try:
                    buffer.handle = None
                    buffer.is_owner = False
                except Exception:
                    pass
        removed += 1
    return removed


def retired_bytes(entries):
    """Return byte usage for ``(BufferKey, handle)`` retired records."""
    return sum(
        int(getattr(record[0], "size_bytes", 0) or 0)
        for record in entries
    )


__all__ = [
    "LifecycleManager",
    "LiveBufferRegistry",
    "retired_bytes",
    "trim_idle_staging_entries",
]
