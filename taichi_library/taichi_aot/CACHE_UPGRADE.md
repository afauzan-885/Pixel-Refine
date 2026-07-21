# Adaptive Block Cache Upgrade

## Implemented Foundation

- Realtime physical-RAM sampling without a mandatory third-party dependency.
- Hysteretic memory-pressure states: healthy, cautious, low, critical, emergency.
- Dynamic host-cache byte budget and direct-compute fallback when admission is unsafe.
- Backward-compatible entry limit plus byte-aware LRU eviction.
- Public cache telemetry for hits, misses, admission, rejection, eviction, and bytes.
- Native `TaichiGPUBuffer` residency with byte budget, generation, lease, and fence hook.
- Automatic promotion, VRAM restore after RAM eviction, checksum validation, and recompute fallback.
- Elastic per-operation soft/hard reservations and borrowed-entry-first reclamation.
- Automatic per-operation ownership, weighted soft shares, borrowing, and reclamation.
- Cache-hit-first block ordering to avoid partial-working-set scan thrashing.
- RAM pressure automatically reduces the device-cache budget to zero.

## Public Configuration

```python
set_block_mode(
    enabled=True,
    size=512,
    threshold_bytes=0,
    cache_entries=512,
    cache_bytes=2 * 1024**3,
    adaptive_memory=True,
    # Optional overrides; defaults are enabled with a conservative 128 MiB budget.
    device_cache_enabled=True,
    device_cache_bytes=512 * 1024**2,
)

# Optional expert override. Normal applications do not need this.
configure_block_reservation(
    "farneback_flow",
    soft_bytes=128 * 1024**2,
    hard_bytes=384 * 1024**2,
    weight=2.0,
)
```

Use `get_memory_status()` and `get_block_cache_stats()` for observability.
`owner_bytes` and `owner_targets` expose the automatically assigned shares.

## Next Integration Stages

1. Add bounded pinned-host spill and asynchronous transfer fences.
2. Add single-flight loading for concurrent requests of the same cache key.
3. Add pipeline sessions and block-major dependency scheduling for zero-download chaining.
4. Enable controlled multi-algorithm concurrency after race and cancellation stress tests.

Device residency is automatic for block mode. Public NumPy APIs still materialize their final
arrays on the host; full zero-download chaining remains a future pipeline-session optimization.
