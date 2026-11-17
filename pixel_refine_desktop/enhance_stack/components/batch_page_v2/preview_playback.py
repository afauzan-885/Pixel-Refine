"""Pure planning helpers for the rolling burst-preview window.

The playback engine keeps a small, index-based window of decoded frames in RAM:
the current frame, ``ahead`` frames in the playback direction, and ``behind``
frames for quick stepping back. Frames outside that window are dropped so a
burst of hundreds of frames never needs an MPEG-style cache.

This module intentionally has no Qt or decoder dependency; it only decides
which frame indices to keep, request, and evict, plus the adaptive pacing
decision for each playback tick.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PreviewWindowConfig:
    """Tuning for the rolling preview window."""

    fps: int = 5
    ahead: int = 10
    behind: int = 2
    refill_threshold: int = 6
    max_frames: int = 15
    initial_buffer: int = 10
    max_bytes: int = 160 * 1024 * 1024
    adaptive_lag_ticks: int = 2
    adaptive_recover_ticks: int = 3

    @property
    def interval_ms(self) -> int:
        return max(16, int(round(1000.0 / max(1, self.fps))))

    @property
    def max_ahead(self) -> int:
        """Ahead window that still fits the total frame budget."""
        return max(1, self.max_frames - 1 - self.behind)


def normalise(index: int, count: int) -> int:
    """Map an index into ``[0, count)``; bursts loop end -> start."""
    return index % count if count else 0


def window_offsets(config: PreviewWindowConfig):
    """Relative offsets kept in RAM: current, ahead..., behind..."""
    ahead = min(config.ahead, config.max_ahead)
    offsets = [0]
    offsets.extend(range(1, ahead + 1))
    offsets.extend(-distance for distance in range(1, config.behind + 1))
    return tuple(offsets)


def window_indices(playhead: int, count: int, config: PreviewWindowConfig):
    if count <= 0:
        return frozenset()
    return frozenset(
        normalise(playhead + offset, count)
        for offset in window_offsets(config)
    )


def ahead_indices(playhead: int, count: int, config: PreviewWindowConfig, limit=None):
    """Playback-direction indices ordered nearest-first."""
    if count <= 0:
        return []
    ahead = min(config.ahead, config.max_ahead)
    if limit is not None:
        ahead = min(ahead, max(0, int(limit)))
    return [normalise(playhead + step, count) for step in range(1, ahead + 1)]


def cached_ahead(playhead, count, cached_indices, config) -> int:
    cached = set(cached_indices or ())
    return sum(
        1
        for index in ahead_indices(playhead, count, config)
        if index in cached
    )


def needs_refill(playhead, count, cached_indices, config) -> bool:
    """True when fewer than ``refill_threshold`` ahead frames are cached."""
    threshold = min(config.refill_threshold, min(config.ahead, config.max_ahead))
    return cached_ahead(playhead, count, cached_indices, config) < threshold


def initial_buffer_ready(cached_indices, count, config) -> bool:
    """True once enough frames exist to start playback without starving."""
    if count <= 0:
        return False
    target = min(config.initial_buffer, count)
    return len(set(cached_indices or ())) >= target


def prefetch_plan(playhead, count, cached_indices, pending_indices, config):
    """Indices to decode now, nearest-first, skipping cached and in-flight."""
    cached = set(cached_indices or ())
    pending = set(pending_indices or ())
    plan = []
    for index in ahead_indices(playhead, count, config):
        if index in cached or index in pending:
            continue
        plan.append(index)
    return plan


def indices_to_drop(playhead, count, cached_indices, config, protected=None):
    """Cached indices outside the active window, excluding ``protected``."""
    keep = set(window_indices(playhead, count, config))
    if protected is not None:
        keep.add(normalise(protected, count))
    return [
        index
        for index in set(cached_indices or ())
        if index not in keep
    ]


class AdaptivePacer:
    """Real-time playback first, frame-locked when decoding cannot keep up.

    ``tick(ready)`` returns:
      - ``"advance"``: the next frame is ready; show it and move the playhead.
      - ``"skip"``: real-time mode and the next frame is not ready; move the
        playhead anyway so playback stays time-accurate (frames are dropped).
      - ``"hold"``: frame-locked mode and the next frame is not ready; keep the
        current frame and try again on the next tick.
    """

    def __init__(self, config: PreviewWindowConfig):
        self._config = config
        self._locked = False
        self._miss_streak = 0
        self._ready_streak = 0

    @property
    def frame_locked(self) -> bool:
        return self._locked

    def reset(self):
        self._locked = False
        self._miss_streak = 0
        self._ready_streak = 0

    def tick(self, next_ready: bool) -> str:
        if next_ready:
            self._miss_streak = 0
            if self._locked:
                self._ready_streak += 1
                if self._ready_streak >= self._config.adaptive_recover_ticks:
                    self._locked = False
                    self._ready_streak = 0
            return "advance"

        self._ready_streak = 0
        self._miss_streak += 1
        if not self._locked and self._miss_streak >= self._config.adaptive_lag_ticks:
            self._locked = True
        return "hold" if self._locked else "skip"
