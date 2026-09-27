from types import SimpleNamespace

from taichi_vision.taichi_aot.allocator import BufferKey, BufferPool
from taichi_vision.taichi_aot.lifecycle import (
    LifecycleManager,
    LiveBufferRegistry,
    retired_bytes,
    trim_idle_staging_entries,
)


def test_buffer_pool_reuses_domain_aware_key_and_releases_over_budget():
    released = []
    owner = SimpleNamespace(_buffer_cache_enabled=True)
    pool = BufferPool(owner, release_handle=released.append)
    pool.set_budget(16)

    key = BufferKey(8, host_accessible=True, dtype="<f4")
    pool.store(key, "first")
    assert pool.acquire(key) == "first"
    assert pool.stats()["hits"] == 1

    pool.store(key, "second")
    pool.store(key, "third")
    pool.store(key, "fourth")
    assert released == ["fourth"]
    assert pool.stats()["evictions"] == 1


def test_staging_trim_keeps_leased_and_removes_oldest_idle():
    destroyed = []
    idle_old = SimpleNamespace(size_bytes=8)
    leased = SimpleNamespace(size_bytes=8)
    idle_new = SimpleNamespace(size_bytes=8)
    pool = {
        (8, "f4"): [
            {"buffer": idle_old, "leased": False, "last_used": 1.0},
            {"buffer": leased, "leased": True, "last_used": 0.0},
            {"buffer": idle_new, "leased": False, "last_used": 2.0},
        ]
    }

    removed = trim_idle_staging_entries(
        pool,
        max_entries=2,
        max_bytes=16,
        destroy=destroyed.append,
    )

    assert removed == 1
    assert destroyed == [idle_old]
    assert pool[(8, "f4")][0]["buffer"] is leased
    assert pool[(8, "f4")][1]["buffer"] is idle_new
    assert retired_bytes([(BufferKey(8), object()), (BufferKey(4), object())]) == 12


def test_lifecycle_manager_keeps_budget_and_retired_queue_policy_together():
    lifecycle = LifecycleManager(
        staging_budget=16,
        retired_budget=24,
        max_staging_entries=2,
        max_retired_entries=3,
    )

    assert lifecycle.retired_over_budget(bytes_used=24, count=3) is False
    assert lifecycle.retired_over_budget(bytes_used=25, count=3) is True
    assert lifecycle.retired_over_budget(bytes_used=24, count=4) is True

    lifecycle.configure(staging_budget=8, max_retired_entries=2)
    assert lifecycle.staging_budget == 8
    assert lifecycle.max_retired_entries == 2


def test_live_buffer_registry_is_weak_and_generation_local():
    registry = LiveBufferRegistry()
    class Buffer:
        pass

    first = Buffer()
    second = Buffer()
    registry.add(first)
    registry.add(second)
    assert len(registry) == 2
    registry.discard(first)
    assert registry.snapshot() == (second,)
    del second
    assert len(registry) == 0
