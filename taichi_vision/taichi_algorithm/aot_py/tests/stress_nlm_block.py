"""Measure NLM block execution and verified cache reuse.

Run with:
    python -m taichi_vision.taichi_algorithm.aot_py.tests.stress_nlm_block
"""

from __future__ import annotations

from time import perf_counter

import numpy as np

from taichi_vision import taichi_aot


def _run(source):
    start = perf_counter()
    result = taichi_aot.non_local_means(
        source,
        h_param=0.1,
        search_window=3,
        patch_size=1,
    )
    return result, perf_counter() - start


def main():
    source = (np.arange(128 * 128, dtype=np.float32).reshape(128, 128) % 47) / 47.0
    previous = taichi_aot.get_block_config()
    try:
        taichi_aot.set_block_mode(enabled=False)
        _run(source)  # Load the graph before measuring full-frame execution.
        legacy, legacy_s = _run(source)

        taichi_aot.set_block_mode(
            enabled=True,
            size=64,
            threshold_bytes=1,
            cache_entries=16,
        )
        taichi_aot.engine.clear_block_cache()

        original_tile = taichi_aot._non_local_means_tile
        calls = 0

        def count_tile(*args):
            nonlocal calls
            calls += 1
            return original_tile(*args)

        taichi_aot._non_local_means_tile = count_tile
        try:
            cold, cold_s = _run(source)
            cold_calls = calls
            warm, warm_s = _run(source)
        finally:
            taichi_aot._non_local_means_tile = original_tile

        np.testing.assert_allclose(cold, legacy, rtol=0, atol=1e-6)
        np.testing.assert_array_equal(warm, cold)
        if calls != cold_calls:
            raise AssertionError("warm pass dispatched NLM tiles instead of using cache")

        mib = source.nbytes / (1024 * 1024)
        print("NLM block benchmark: PASS")
        print(f"input: {source.shape}, {mib:.3f} MiB, search radius=3, patch radius=1")
        print(f"legacy full-frame: {legacy_s:.4f}s")
        print(f"block cold:        {cold_s:.4f}s, tile dispatches={cold_calls}")
        print(f"block warm:        {warm_s:.4f}s, tile dispatches=0")
        print(f"warm cache speedup: {cold_s / warm_s:.2f}x")
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
