"""Native Rust runtime-state contracts (allocator, residency, memory).

These replace the legacy tests that lived under the removed ``taichi_aot``
package. They exercise the PyO3 classes directly, so they keep validating the
Rust migration without importing any legacy runtime module.
"""

import pytest

from taichi import BufferKey, BufferPool
from taichi.memory import (
    CacheTelemetry,
    MemoryGovernor,
    MemorySnapshot,
    validate_memory_decision,
)
from taichi.residency import DeviceResidencyCache


def test_buffer_pool_reuses_keys_and_evicts_over_budget():
    released = []
    pool = BufferPool(release_handle=released.append)
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


def test_buffer_key_rejects_non_positive_size():
    with pytest.raises(ValueError):
        BufferKey(0)


def test_residency_put_lease_and_invalidate():
    cache = DeviceResidencyCache(1024)
    buffer = object()
    entry = cache.put("k", "own", buffer, 100, checksum=5)
    assert entry is not None
    assert cache.size_bytes == 100
    with cache.lease("k") as leased:
        assert leased is entry
        assert leased.ref_count == 1
        assert leased.leased is True
    assert entry.ref_count == 0
    assert cache.peek("k") is entry
    assert cache.invalidate("k") is True
    assert cache.size_bytes == 0


def test_residency_fence_blocks_consumer_until_ready():
    ready = [False]
    cache = DeviceResidencyCache(1024)
    cache.put("tile", "op", object(), 16, fence_ready=lambda: ready[0])
    with cache.lease("tile") as entry:
        assert entry is None
    ready[0] = True
    with cache.lease("tile") as entry:
        assert entry is not None


def test_cache_telemetry_known_and_unknown_counters():
    telemetry = CacheTelemetry()
    telemetry.add("hits", 2)
    telemetry.add("custom_counter", 3)
    snapshot = telemetry.snapshot()
    assert snapshot["hits"] == 2
    assert snapshot["custom_counter"] == 3
    telemetry.reset()
    assert telemetry.snapshot()["hits"] == 0


def test_memory_governor_decision_is_valid_and_deterministic():
    snapshot = MemorySnapshot(
        total_bytes=32 * 1024**3, available_bytes=16 * 1024**3, timestamp=100.0
    )
    governor = MemoryGovernor(provider=lambda: snapshot, configured_max_bytes=64 * 1024**2)
    decision = governor.refresh(force=True)
    assert validate_memory_decision(decision)["valid"] is True
    assert decision.pressure.name == "HEALTHY"
    assert decision.host_cache_budget == 64 * 1024**2
    assert 256 <= decision.recommended_block_size <= 2048
    assert governor.recommend_block_size() == decision.recommended_block_size
