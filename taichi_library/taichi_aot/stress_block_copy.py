"""GPU stress and resilience checks for block-based common.copy.

Run with:
    python -m taichi_library.taichi_aot.stress_block_copy
"""

from __future__ import annotations

from time import perf_counter

import numpy as np

from taichi_library import taichi_aot


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

    taichi_aot.engine.clear_block_cache()
    original_copy_tile = taichi_aot._copy_tile
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


def main():
    previous = taichi_aot.get_block_config()
    try:
        _run_performance_cases()
        _run_resilience_cases()
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
