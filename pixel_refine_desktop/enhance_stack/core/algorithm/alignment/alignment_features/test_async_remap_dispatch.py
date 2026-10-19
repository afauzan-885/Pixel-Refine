from types import SimpleNamespace

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
    _reclaim_engine_vram,
)


def test_reclaim_engine_vram_drains_retired_and_clears_large_idle_pool():
    calls = []
    pool = SimpleNamespace(
        stats=lambda: {"pooled_bytes": 65 * 1024 * 1024},
        clear=lambda: calls.append("clear"),
    )
    engine = SimpleNamespace(
        current_pipeline=None,
        buffer_pool=pool,
        _drain_retired=lambda wait: calls.append(("drain", wait)),
    )

    _reclaim_engine_vram(engine)

    assert calls == [("drain", True), "clear"]
