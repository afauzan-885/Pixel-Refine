"""Small real-device stress probe for BufferSession cache/lifecycle behavior.

Select the backend in the environment before running this script. Example:
    $env:PIXEL_REFINE_AOT_ARCH = "opengl"
    $env:PIXEL_REFINE_TARGET_VENDOR = "nvidia"
    python taichi_vision/taichi_algorithm/aot_py/tests/stress_buffer_session.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))


def _parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--height", type=int, default=96)
    parser.add_argument("--width", type=int, default=96)
    args = parser.parse_args()
    if args.frames < 1 or args.height < 64 or args.width < 64:
        parser.error("frames must be positive and image dimensions at least 64")
    return args


def main():
    args = _parse_args()
    from taichi_vision.taichi_algorithm.aot_api import cvtColor, COLOR_BGR2GRAY
    from taichi_vision.taichi_algorithm.buffer_session import BufferSession
    from taichi_vision.taichi_aot.engine import (
        backend_info,
        engine,
        get_backend_name,
    )

    rng = np.random.default_rng(20260925)
    reference = rng.random((args.height, args.width, 3), dtype=np.float32)
    session = BufferSession()
    frame_records = []
    peak_live_bytes = 0
    try:
        reference_gray, _ = session.get_or_create_reference(
            reference, num_levels=2, min_size=8
        )
        reference_before = reference_gray.to_numpy().copy()

        # Resetting per-frame scratch must not alias the pinned reference slots.
        probe = np.roll(reference, (1, 2), axis=(0, 1)).copy()
        session.reset_ring()
        cvtColor(
            probe, COLOR_BGR2GRAY, return_gpu=True, session=session
        )
        reference_after = reference_gray.to_numpy()
        reference_drift = float(np.max(np.abs(reference_after - reference_before)))
        if reference_drift > 1e-6:
            raise AssertionError(f"reference cache was overwritten: {reference_drift}")
        session.release_upload(probe)

        for frame_index in range(args.frames):
            target = np.roll(
                reference,
                (frame_index % 7 + 1, frame_index % 5 + 1),
                axis=(0, 1),
            ).copy()
            aligned = session.align_and_warp(
                reference,
                target,
                algorithm="farneback",
                num_levels=2,
                num_iters=1,
                win_size=5,
                poly_n=5,
                poly_sigma=1.2,
                return_gpu=False,
            )
            if aligned.shape != reference.shape or not np.isfinite(aligned).all():
                raise AssertionError(f"invalid aligned result at frame {frame_index}")
            memory = engine.get_memory_status(force=True)
            live_bytes = int(memory.get("live_bytes", 0) or 0)
            peak_live_bytes = max(peak_live_bytes, live_bytes)
            frame_records.append(
                {
                    "frame": frame_index + 1,
                    "upload_cache_entries": len(session._upload_cache),
                    "leased_buffers": len(session._leased_buffers),
                    "live_bytes": live_bytes,
                    "pooled_bytes": int(memory.get("pooled_bytes", 0) or 0),
                    "retired_bytes": int(memory.get("retired_bytes", 0) or 0),
                }
            )
    finally:
        session.close()

    after_close = engine.get_memory_status(force=True)
    print(
        json.dumps(
            {
                "backend": get_backend_name(),
                "device": backend_info(),
                "shape": [args.height, args.width, 3],
                "dtype": "float32",
                "frames": args.frames,
                "reference_drift_max_abs": reference_drift,
                "peak_live_bytes": peak_live_bytes,
                "frame_records": frame_records,
                "after_close": {
                    key: int(after_close.get(key, 0) or 0)
                    for key in (
                        "live_bytes",
                        "pooled_bytes",
                        "retired_bytes",
                        "resident_bytes",
                    )
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
