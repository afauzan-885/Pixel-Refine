"""Parity of the block-state support modules after the port into taichi.

These modules back the engine block cache: BlockCache/BlockRecord/BlockState,
checksum, MemoryGovernor, MemoryPolicy, LifecycleManager,
LiveBufferRegistry and DeviceResidencyCache. Everything here is deterministic
state management; parity is asserted by driving both implementations through
the identical operation sequence with fixed (fake) memory providers.
"""

from dataclasses import asdict

import numpy as np
import pytest

import taichi as ti

legacy_block = pytest.importorskip("taichi.block")
legacy_memory = pytest.importorskip("taichi.memory")
legacy_policy = pytest.importorskip("taichi.memory_policy")
legacy_lifecycle = pytest.importorskip("taichi.lifecycle")
legacy_residency = pytest.importorskip("taichi.residency")

DATA = np.random.default_rng(3).random((32, 64), dtype=np.float32)


def test_checksum_matches():
    assert ti.block_cache.checksum(DATA) == legacy_block.checksum(DATA)


def test_block_state_enum_matches():
    assert [s.value for s in ti.block_cache.BlockState] == [
        s.value for s in legacy_block.BlockState
    ]


def _drive(cache, record_cls):
    record = record_cls(
        block_id="b1",
        data=DATA,
        checksum=legacy_block.checksum(DATA),
        source_checksum=1,
        owner="op_a",
    )
    cache.put(record)
    cache.get("b1")
    cache.put(
        record_cls(
            block_id="b2",
            data=np.full((16, 16), 2.0, np.float32),
            checksum=123,
            source_checksum=2,
            owner="op_b",
        )
    )
    owners = cache.owner_bytes
    cache.set_limits(max_entries=1)
    evicted = cache.collect()
    length = len(cache)
    remaining = [key for key in ("b1", "b2") if cache.peek(key) is not None]
    cleared_after = (cache.size_bytes, len(cache))
    cache.clear()
    after_clear = (cache.size_bytes, len(cache))
    return dict(
        size_after_b2=None,
        owners=owners,
        evicted=evicted,
        length=length,
        remaining=remaining,
        cleared_after=cleared_after,
        after_clear=after_clear,
    )


def test_block_cache_sequence_matches():
    legacy = _drive(legacy_block.BlockCache(max_entries=64), legacy_block.BlockRecord)
    migrated = _drive(
        ti.block_cache.BlockCache(max_entries=64), ti.block_cache.BlockRecord
    )
    assert migrated["owners"] == legacy["owners"]
    assert migrated["evicted"] == legacy["evicted"]
    assert migrated["length"] == legacy["length"]
    assert migrated["remaining"] == legacy["remaining"]
    assert migrated["cleared_after"] == legacy["cleared_after"]
    assert migrated["after_clear"] == legacy["after_clear"]


def test_block_record_is_valid_matches():
    record = legacy_block.BlockRecord(block_id="x", data=DATA)
    migrated = ti.block_cache.BlockRecord(block_id="x", data=DATA)
    assert migrated.is_valid() == record.is_valid()
    migrated.state = ti.block_cache.BlockState.CORRUPT
    record.state = legacy_block.BlockState.CORRUPT
    assert migrated.is_valid() == record.is_valid() is False


SNAPSHOT_CASES = [
    (32 * 1024**3, 16 * 1024**3),
    (16 * 1024**3, 512 * 1024**2),
    (8 * 1024**3, 200 * 1024**2),
]


@pytest.mark.parametrize("available,total", SNAPSHOT_CASES)
def test_memory_governor_decision_matches(available, total):
    def make(governor_cls, snapshot_cls):
        return governor_cls(
            provider=lambda: snapshot_cls(
                total_bytes=total, available_bytes=available, timestamp=100.0
            ),
            configured_max_bytes=64 * 1024**2,
        )

    legacy = make(legacy_memory.MemoryGovernor, legacy_memory.MemorySnapshot)
    migrated = make(ti.memory.MemoryGovernor, ti.memory.MemorySnapshot)
    assert asdict(migrated.refresh(force=True)) == asdict(legacy.refresh(force=True))


def test_memory_policy_decision_matches():
    snapshot = legacy_memory.MemorySnapshot(
        total_bytes=32 * 1024**3, available_bytes=16 * 1024**3, timestamp=100.0
    )
    new_snapshot = ti.memory.MemorySnapshot(
        total_bytes=32 * 1024**3, available_bytes=16 * 1024**3, timestamp=100.0
    )
    legacy = legacy_policy.MemoryPolicy(
        configured_max_bytes=2048, provider=lambda: snapshot
    )
    migrated = ti.memory_policy.MemoryPolicy(
        configured_max_bytes=2048, provider=lambda: new_snapshot
    )
    fields = ("allow_cache", "host_cache_budget", "device_pool_budget")
    left = {f: getattr(legacy.refresh(force=True), f) for f in fields}
    right = {f: getattr(migrated.refresh(force=True), f) for f in fields}
    assert right == left


def test_lifecycle_manager_matches():
    legacy = legacy_lifecycle.LifecycleManager(
        staging_budget=100, retired_budget=100,
        max_staging_entries=5, max_retired_entries=5,
    )
    migrated = ti.lifecycle.LifecycleManager(
        staging_budget=100, retired_budget=100,
        max_staging_entries=5, max_retired_entries=5,
    )
    assert migrated.staging_budget == legacy.staging_budget
    assert migrated.retired_budget == legacy.retired_budget
    assert migrated.retired_over_budget(
        bytes_used=200, count=2
    ) == legacy.retired_over_budget(bytes_used=200, count=2)


def test_live_buffer_registry_matches():
    class Buffer:
        pass

    buffer = Buffer()
    legacy = legacy_lifecycle.LiveBufferRegistry()
    migrated = ti.lifecycle.LiveBufferRegistry()
    legacy.add(buffer)
    migrated.add(buffer)
    assert len(migrated) == len(legacy) == 1
    legacy.discard(buffer)
    migrated.discard(buffer)
    assert len(migrated) == len(legacy) == 0


class _FakeResidentBuffer:
    def __init__(self, size):
        self.size_bytes = size

    def destroy(self):
        pass


def test_device_residency_cache_matches():
    legacy = legacy_residency.DeviceResidencyCache(1024)
    migrated = ti.residency.DeviceResidencyCache(1024)
    entry_l = legacy.put(
        "k", "own", _FakeResidentBuffer(100), 100,
        dispose=lambda b: None, checksum=5, source_checksum=7,
    )
    entry_n = migrated.put(
        "k", "own", _FakeResidentBuffer(100), 100,
        dispose=lambda b: None, checksum=5, source_checksum=7,
    )
    for field in ("key", "owner", "size_bytes", "checksum", "source_checksum"):
        assert getattr(entry_n, field) == getattr(entry_l, field)
    assert entry_n.leased == entry_l.leased
    assert entry_n.can_evict() == entry_l.can_evict()
    assert migrated.size_bytes == legacy.size_bytes == 100
    with legacy.lease("k") as left, migrated.lease("k") as right:
        assert left.ref_count == right.ref_count == 1
        assert left.leased == right.leased is True
    assert entry_l.ref_count == entry_n.ref_count == 0
    assert migrated.peek("k") is entry_n
    assert migrated.stats() == legacy.stats()
    assert migrated.invalidate("k") == legacy.invalidate("k") is True
    assert migrated.size_bytes == legacy.size_bytes == 0