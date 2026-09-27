"""Optional resident-pipeline memory telemetry.

The Taichi engine already exposes live, pooled, and retired byte counters.
This wrapper keeps telemetry out of the hot path unless explicitly enabled
through the function argument or ``PIXEL_REFINE_PIPELINE_TELEMETRY=1``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MemorySnapshot:
    label: str
    live_bytes: int = 0
    pooled_bytes: int = 0
    retired_bytes: int = 0


class PipelineTelemetry:
    def __init__(self, engine: Any, enabled: bool | None = None):
        self.engine = engine
        self.enabled = (
            str(os.environ.get("PIXEL_REFINE_PIPELINE_TELEMETRY", "0"))
            .strip()
            .lower()
            in {"1", "true", "yes", "on"}
            if enabled is None
            else bool(enabled)
        )
        self.samples: list[MemorySnapshot] = []

    def snapshot(self, label: str) -> MemorySnapshot | None:
        if not self.enabled:
            return None
        try:
            status = self.engine.get_memory_status(force=True)
        except Exception:
            status = {}
        sample = MemorySnapshot(
            label=str(label),
            live_bytes=int(status.get("live_bytes", 0) or 0),
            pooled_bytes=int(status.get("pooled_bytes", 0) or 0),
            retired_bytes=int(status.get("retired_bytes", 0) or 0),
        )
        self.samples.append(sample)
        return sample

    def emit(self, label: str) -> None:
        sample = self.snapshot(label)
        if sample is None:
            return
        print(
            "[PipelineTelemetry] "
            f"stage={sample.label} "
            f"live_bytes={sample.live_bytes} "
            f"pooled_bytes={sample.pooled_bytes} "
            f"retired_bytes={sample.retired_bytes}"
        )

    def report(self) -> dict[str, Any]:
        if not self.samples:
            return {"enabled": False, "samples": []}
        return {
            "enabled": True,
            "samples": [sample.__dict__.copy() for sample in self.samples],
            "peak_live_bytes": max(sample.live_bytes for sample in self.samples),
            "peak_pooled_bytes": max(sample.pooled_bytes for sample in self.samples),
            "peak_retired_bytes": max(sample.retired_bytes for sample in self.samples),
        }


__all__ = ["MemorySnapshot", "PipelineTelemetry"]
