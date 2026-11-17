"""Unit tests for the rolling burst-preview window planning."""

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.preview_playback import (
    AdaptivePacer,
    PreviewWindowConfig,
    ahead_indices,
    cached_ahead,
    indices_to_drop,
    initial_buffer_ready,
    needs_refill,
    normalise,
    prefetch_plan,
    window_indices,
)


def test_default_config_matches_agreed_parameters():
    config = PreviewWindowConfig()
    assert config.fps == 5
    assert config.interval_ms == 200
    assert config.ahead == 10
    assert config.behind == 2
    assert config.initial_buffer == 10
    assert config.refill_threshold == 6
    assert config.max_frames == 15
    assert config.max_ahead == 12


def test_normalise_wraps_and_handles_empty():
    assert normalise(0, 5) == 0
    assert normalise(7, 5) == 2
    assert normalise(-1, 5) == 4
    assert normalise(3, 0) == 0


def test_window_indices_are_relative_and_wrap():
    config = PreviewWindowConfig(ahead=2, behind=1, max_frames=10)
    assert window_indices(0, 5, config) == frozenset({0, 1, 2, 4})
    assert window_indices(4, 5, config) == frozenset({4, 0, 1, 3})
    assert window_indices(0, 0, config) == frozenset()


def test_window_is_capped_by_max_frames():
    config = PreviewWindowConfig(ahead=20, behind=2, max_frames=6)
    assert config.max_ahead == 3
    indices = window_indices(0, 50, config)
    assert len(indices) == 6  # current + 3 ahead + 2 behind


def test_ahead_indices_are_nearest_first():
    config = PreviewWindowConfig(ahead=3, behind=2, max_frames=10)
    assert ahead_indices(3, 5, config) == [4, 0, 1]
    assert ahead_indices(3, 5, config, limit=2) == [4, 0]


def test_cached_ahead_and_refill_threshold():
    config = PreviewWindowConfig(ahead=4, behind=1, max_frames=10, refill_threshold=2)
    cached = {1, 2}
    assert cached_ahead(0, 10, cached, config) == 2
    assert needs_refill(0, 10, cached, config) is False
    assert needs_refill(0, 10, {1}, config) is True
    assert needs_refill(0, 10, set(), config) is True


def test_initial_buffer_ready_respects_small_bursts():
    config = PreviewWindowConfig(initial_buffer=10)
    assert initial_buffer_ready(range(9), 400, config) is False
    assert initial_buffer_ready(range(10), 400, config) is True
    assert initial_buffer_ready(range(3), 3, config) is True
    assert initial_buffer_ready(range(3), 0, config) is False


def test_prefetch_plan_skips_cached_and_pending_nearest_first():
    config = PreviewWindowConfig(ahead=5, behind=1, max_frames=10)
    plan = prefetch_plan(0, 10, {1, 3}, {2}, config)
    assert plan == [4, 5]


def test_indices_to_drop_keeps_window_and_protected_frame():
    config = PreviewWindowConfig(ahead=2, behind=1, max_frames=10)
    # playhead 5 wraps: window = {5, 6, 7, 4}
    dropped = set(indices_to_drop(5, 10, range(10), config))
    assert dropped == {0, 1, 2, 3, 8, 9}

    protected = 9
    protected_drop = set(indices_to_drop(5, 10, range(10), config, protected=protected))
    assert protected not in protected_drop


def test_pacer_is_real_time_then_frame_locked_then_recovers():
    config = PreviewWindowConfig(adaptive_lag_ticks=2, adaptive_recover_ticks=3)
    pacer = AdaptivePacer(config)

    assert pacer.tick(False) == "skip"
    assert pacer.frame_locked is False
    assert pacer.tick(False) == "hold"
    assert pacer.frame_locked is True
    assert pacer.tick(False) == "hold"

    assert pacer.tick(True) == "advance"
    assert pacer.tick(True) == "advance"
    assert pacer.frame_locked is True
    assert pacer.tick(True) == "advance"
    assert pacer.frame_locked is False

    assert pacer.tick(False) == "skip"
    assert pacer.tick(True) == "advance"


def test_pacer_reset_restores_real_time():
    pacer = AdaptivePacer(PreviewWindowConfig(adaptive_lag_ticks=1))
    pacer.tick(False)
    assert pacer.frame_locked is True
    pacer.reset()
    assert pacer.frame_locked is False
    assert pacer.tick(False) == "hold"  # one miss re-locks with lag=1


def test_thumbnail_suspension_reasons_are_independent():
    from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_policy import (
        set_thumbnail_generation_suspended,
        thumbnail_generation_suspended,
    )

    set_thumbnail_generation_suspended(False, reason="preview")
    set_thumbnail_generation_suspended(False, reason="compute")
    try:
        assert not thumbnail_generation_suspended()
        set_thumbnail_generation_suspended(True, reason="preview")
        assert thumbnail_generation_suspended()
        assert not thumbnail_generation_suspended(exclude_reason="preview")

        set_thumbnail_generation_suspended(True, reason="compute")
        assert thumbnail_generation_suspended(exclude_reason="preview")

        set_thumbnail_generation_suspended(False, reason="preview")
        assert thumbnail_generation_suspended()
        set_thumbnail_generation_suspended(False, reason="compute")
        assert not thumbnail_generation_suspended()
    finally:
        set_thumbnail_generation_suspended(False, reason="preview")
        set_thumbnail_generation_suspended(False, reason="compute")
