"""GPU stress and resilience checks for block-based common.copy.

Run with:
    python -m taichi_vision.taichi_algorithm.aot_py.tests.stress_block_copy
"""

from __future__ import annotations

from time import perf_counter

import numpy as np

from taichi_vision import taichi_aot


CASES = (
    ("gray-f32", (192, 192), np.float32),
    ("gray-i32", (320, 256), np.int32),
    ("rgb-f32", (192, 256, 3), np.float32),
    ("large-gray-f32", (768, 1024), np.float32),
)


def _source(shape, dtype):
    values = np.arange(np.prod(shape), dtype=dtype).reshape(shape)
    return values / np.array(17, dtype=dtype) if dtype == np.float32 else values


def _copy_and_measure(source):
    start = perf_counter()
    result = taichi_aot.copy(source)
    elapsed = perf_counter() - start
    np.testing.assert_array_equal(result, source)
    return elapsed


def _run_performance_cases():
    print("\nPerformance (native common-copy graph per block)")
    print("case                 cache  cold MiB/s  warm MiB/s")
    for cache_entries in (2, 32):
        for name, shape, dtype in CASES:
            source = _source(shape, dtype)
            taichi_aot.set_block_mode(
                enabled=True,
                size=128,
                threshold_bytes=1,
                cache_entries=cache_entries,
            )
            taichi_aot.engine.clear_block_cache()
            cold_s = _copy_and_measure(source)
            warm_s = _copy_and_measure(source)
            mib = source.nbytes / (1024 * 1024)
            print(
                f"{name:20} {cache_entries:5} "
                f"{mib / cold_s:11.1f} {mib / warm_s:11.1f}"
            )


def _run_resilience_cases():
    print("\nResilience")
    source = _source((256, 256), np.float32)
    taichi_aot.set_block_mode(
        enabled=True,
        size=64,
        threshold_bytes=1,
        cache_entries=32,
    )
    taichi_aot.engine.clear_block_cache()
    _copy_and_measure(source)

    cached = next(iter(taichi_aot.engine.get_block_cache()._records.values()))
    cached.data.flat[0] += 1.0
    np.testing.assert_array_equal(taichi_aot.copy(source), source)
    print("corrupt cached tile: recovered by checksum validation and recompute")

    # A checksum alone cannot detect a malformed payload if a producer also
    # wrote a matching checksum.  The block dispatcher now validates the
    # cached core shape before using it and must recompute this tile too.
    taichi_aot.engine.clear_block_cache()
    _copy_and_measure(source)
    malformed = next(iter(taichi_aot.engine.get_block_cache()._records.values()))
    malformed.data = np.zeros((1, 1), dtype=np.float32)
    malformed.checksum = taichi_aot.checksum(malformed.data)
    np.testing.assert_array_equal(taichi_aot.copy(source), source)
    print("malformed cached tile shape: rejected and recomputed")

    # Multi-output records must reject a scalar or truncated checksum tuple;
    # otherwise a malformed producer could make ``zip`` validate only part of
    # the payload (or raise before the normal recompute path is reached).
    rgb_source = _source((128, 128, 3), np.float32)
    taichi_aot.engine.clear_block_cache()
    channels = taichi_aot.split_3ch(rgb_source)
    np.testing.assert_array_equal(np.stack(channels, axis=-1), rgb_source)
    multi = next(
        record
        for record in taichi_aot.engine.get_block_cache()._records.values()
        if record.owner == "split_3ch"
    )
    multi.checksum = 0
    recovered = taichi_aot.split_3ch(rgb_source)
    np.testing.assert_array_equal(np.stack(recovered, axis=-1), rgb_source)
    print("malformed multi-output checksum: rejected and recomputed")

    taichi_aot.engine.clear_block_cache()
    # Older stress harnesses monkey-patched a private package-level
    # ``_copy_tile`` hook.  Current AOT exposes the retry implementation only
    # through the engine, so do not fail the whole resilience run merely
    # because that test-only hook is absent.
    original_copy_tile = getattr(taichi_aot, "_copy_tile", None)
    if callable(original_copy_tile):
        calls = 0

        def fail_once(tile):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("injected transient tile failure")
            return original_copy_tile(tile)

        taichi_aot._copy_tile = fail_once
        try:
            np.testing.assert_array_equal(taichi_aot.copy(source), source)
        finally:
            taichi_aot._copy_tile = original_copy_tile
        assert calls >= 2
        print("transient tile failure: recovered by retry from source")
    else:
        np.testing.assert_array_equal(taichi_aot.copy(source), source)
        print("transient tile failure: skipped (private hook not exported)")

    try:
        taichi_aot.copy(np.arange(16, dtype=np.float32))
    except ValueError:
        print("unsupported 1D input: rejected without poisoning the runtime")
    else:
        raise AssertionError("1D copy unexpectedly succeeded")

    np.testing.assert_array_equal(taichi_aot.copy(source), source)
    print("valid request after rejected input: passed")

    non_contiguous = source[:, ::2]
    np.testing.assert_array_equal(taichi_aot.copy(non_contiguous), non_contiguous)
    print("non-contiguous source: normalized and copied correctly")

    non_finite = source.copy()
    non_finite[0, 0] = np.nan
    non_finite[0, 1] = np.inf
    result = taichi_aot.copy(non_finite)
    np.testing.assert_equal(result, non_finite)
    print("NaN/Inf payload: preserved without cache corruption")


def _run_full_frame_allocation_cache_case():
    """Prove allocation reuse also works when block execution is disabled."""
    print("\nFull-frame allocation cache")
    previous = taichi_aot.get_block_config()
    try:
        # Use a threshold above the test payload so the common-copy graph is
        # forced through its full-frame path.  The two calls deliberately use
        # different NumPy objects: reuse is based on physical allocation
        # compatibility, not Python object identity.
        taichi_aot.engine.configure_blocks(
            enabled=False,
            threshold_bytes=1 << 60,
            cache_entries=previous.cache_entries,
        )
        taichi_aot.engine.clear_block_cache()
        taichi_aot.engine.buffer_pool.clear()
        source = _source((128, 128), np.float32)
        first = taichi_aot.copy(source)
        before = taichi_aot.engine.buffer_pool.stats()
        second = taichi_aot.copy(source.copy())
        after = taichi_aot.engine.buffer_pool.stats()
        np.testing.assert_array_equal(first, second)
        if after["hits"] <= before["hits"]:
            raise AssertionError(
                "full-frame allocation cache did not record a same-size hit"
            )
        print(
            "same-size full-frame allocation: cache hit "
            f"({before['hits']} -> {after['hits']})"
        )
    finally:
        taichi_aot.engine.configure_blocks(
            enabled=previous.enabled,
            size=previous.size,
            threshold_bytes=previous.threshold_bytes,
            cache_entries=previous.cache_entries,
        )
        taichi_aot.engine.buffer_pool.clear()


def main():
    previous = taichi_aot.get_block_config()
    try:
        _run_performance_cases()
        _run_resilience_cases()
        _run_full_frame_allocation_cache_case()
    finally:
        taichi_aot.engine.configure_blocks(
            enabled=previous.enabled,
            size=previous.size,
            threshold_bytes=previous.threshold_bytes,
            cache_entries=previous.cache_entries,
        )
        taichi_aot.engine.clear_block_cache()


if __name__ == "__main__":
    main()
