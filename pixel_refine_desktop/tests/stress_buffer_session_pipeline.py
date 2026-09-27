"""Real AOT lifecycle/parity probe; synthetic providers, unchanged native graphs.

Run each backend in a separate process with PIXEL_REFINE_AOT_ARCH set explicitly.
This is not a camera decode, ONNX performance, or 12 MP application benchmark.
"""

from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
import sys
import threading
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--frames", type=int, default=5)
    parser.add_argument("--engines", default="average,spatial_fusion")
    parser.add_argument("--alignment", default="No Alignment")
    parser.add_argument("--faults", action="store_true", help="Inject decode/blend/readback failures and cancel")
    args = parser.parse_args()
    if args.frames < 2 or args.repeats < 1:
        parser.error("frames >= 2 and repeats >= 1 are required")

    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process import resident_pipeline as pipeline
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.raw_pipeline import provider as raw
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.pipeline_process.rgb_pipeline.provider import RGBFrameProvider
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import PipelineRuntime
    from taichi_vision.taichi_algorithm.compression.raw_frame import RawMosaicFrame
    from taichi_vision.taichi_aot.engine import TaichiGPUBuffer, backend_info, get_backend_name
    from taichi_vision.taichi_aot import get_engine

    engine = get_engine()
    sessions = []
    readbacks = []
    ensure = PipelineRuntime.ensure_session
    download = TaichiGPUBuffer.to_numpy

    def record_session(runtime, target_engine=None):
        session = ensure(runtime, target_engine)
        if not any(item is session for item in sessions):
            sessions.append(session)
        return session

    def record_download(buffer, *values, **options):
        readbacks.append(tuple(buffer.shape))
        return download(buffer, *values, **options)

    records = []
    for shape in ((96, 128), (128, 160)):
        yy, xx = np.indices(shape, dtype=np.uint32)

        def rgb(index):
            return np.stack(
                ((xx * 3 + index * 5) % 256, (yy * 7 + index * 3) % 256,
                 (xx + yy + index * 7) % 256), axis=-1
            ).astype(np.float32) / np.float32(255)

        def raw_frame(index):
            samples = (128 + (xx * 17 + yy * 13 + index * 3) % 14000).astype(np.uint16)
            return RawMosaicFrame.from_samples(
                samples, bits_per_sample=14, cfa_pattern=(0, 1, 1, 2),
                black_level=128, white_level=16384, source_id=f"synthetic-{index}.dng",
                metadata={"dng_tags": {50721: tuple(np.eye(3).reshape(-1)),
                                       50728: (1.0, 1.0, 1.0)}},
            )

        paths = [f"synthetic-{index}.dng" for index in range(args.frames)]
        with patch.object(PipelineRuntime, "ensure_session", record_session), \
             patch.object(TaichiGPUBuffer, "to_numpy", record_download), \
             patch.object(pipeline, "load_frame_to_gpu", lambda *_a, **_k: engine.upload(rgb(0))), \
             patch.object(RGBFrameProvider, "load_support_host", lambda _s, index: rgb(index)), \
             patch.object(raw.RawNativeProvider, "_read_frame", lambda _s, index: raw_frame(index)):
            for mode in ("rgb", "raw_native"):
                for weight_engine in args.engines.split(","):
                    baseline = None
                    for repeat in range(args.repeats):
                        depth = (0, 1, 4)[repeat % 3]
                        start_reads = len(readbacks)
                        output, alpha = pipeline.run_gpu_resident_pipeline(
                            paths, source_mode=mode, weight_engine=weight_engine,
                            alignment_plan=args.alignment, work_scale=0.5,
                            max_work_dimension=None, tile_size=512 if weight_engine == "fusionet" else 64,
                            spatial_config={"tile_size": 8, "noise_sigma": 0.01},
                            prefetch_depth=depth,
                        )
                        actual = output.normalized_mosaic if mode == "raw_native" else output
                        assert actual is not None and np.isfinite(actual).all()
                        if baseline is None:
                            baseline = actual.copy()
                        drift = float(np.max(np.abs(actual - baseline)))
                        assert drift <= 2e-6, (mode, weight_engine, drift)
                        oracle_error = None
                        if weight_engine == "average" and args.alignment == "No Alignment":
                            values = [raw._normalized_for_rgb_parity(raw_frame(index))
                                      if mode == "raw_native" else rgb(index)
                                      for index in range(args.frames)]
                            expected = np.mean(np.stack(values), axis=0, dtype=np.float32)
                            oracle_error = float(np.max(np.abs(actual - expected)))
                            assert oracle_error <= 2e-6, oracle_error
                        assert all(s._closed and s.owned_count == s.borrowed_count == 0 for s in sessions)
                        assert not any(t.name.startswith("Stage") or t.name == "PipelineHostPrefetch"
                                       for t in threading.enumerate())
                        engine.sync()
                        status = engine.get_memory_status(force=True)
                        records.append({
                            "mode": mode, "engine": weight_engine, "shape": list(actual.shape),
                            "dtype": str(actual.dtype), "prefetch_depth": depth,
                            "repeat": repeat + 1, "max_abs_repeat_drift": drift,
                            "max_abs_average_oracle_error": oracle_error,
                            "readbacks": len(readbacks) - start_reads, "alpha": alpha,
                            "session_owned_after_close": sessions[-1].owned_count,
                            "live_bytes_after_sync": int(status.get("live_bytes", 0)),
                            "live_buffers_after_sync": [
                                {"shape": list(buffer.shape), "dtype": str(buffer.dtype),
                                 "bytes": int(buffer.size_bytes)}
                                for buffer in tuple(engine._live_buffers)
                                if getattr(buffer, "is_owner", False) and getattr(buffer, "handle", None) is not None
                            ],
                            "pooled_bytes": int(status.get("pooled_bytes", 0)),
                            "retired_bytes": int(status.get("retired_bytes", 0)),
                        })
                if args.faults:
                    for fault in ("decode", "blend", "readback", "cancel"):
                        engine.sync()
                        native_cache_floor = int(engine.get_memory_status(force=True).get("live_bytes", 0))
                        stop = threading.Event()
                        kwargs = dict(source_mode=mode, weight_engine="average",
                                      alignment_plan="No Alignment", work_scale=0.5,
                                      max_work_dimension=None, prefetch_depth=4, stop_event=stop)

                        def load_fault(_provider, index):
                            if index == 2:
                                if fault == "cancel":
                                    stop.set()
                                elif fault == "decode":
                                    raise OSError("injected decode failure")
                            return raw_frame(index) if mode == "raw_native" else rgb(index)

                        def fail(*_a, **_k):
                            raise OSError(f"injected {fault} failure")

                        loader_patch = patch.object(
                            raw.RawNativeProvider if mode == "raw_native" else RGBFrameProvider,
                            "_read_frame" if mode == "raw_native" else "load_support_host", load_fault)
                        target = raw.RawNativeProvider if mode == "raw_native" else pipeline
                        blend_patch = patch.object(target, "accumulate" if mode == "raw_native"
                                                   else "_gpu_blend_frame", fail) if fault == "blend" else nullcontext()
                        read_patch = patch.object(TaichiGPUBuffer, "to_numpy", fail) if fault == "readback" else nullcontext()
                        caught = None
                        with loader_patch, blend_patch, read_patch:
                            try:
                                result, _ = pipeline.run_gpu_resident_pipeline(paths, **kwargs)
                                if fault != "cancel":
                                    assert result is None, f"fault {fault} was not observed"
                            except (OSError, RuntimeError) as error:
                                caught = str(error)
                        assert all(s._closed and s.owned_count == s.borrowed_count == 0 for s in sessions)
                        assert not any(t.name.startswith("Stage") or t.name == "PipelineHostPrefetch"
                                       for t in threading.enumerate())
                        engine.sync()
                        status = engine.get_memory_status(force=True)
                        # Native module constants can outlive application jobs.
                        # Fault cleanup must not add any live application data.
                        assert int(status.get("live_bytes", 0)) <= native_cache_floor, status
                        records.append({"mode": mode, "fault": fault, "observed_error": caught,
                                        "session_owned_after_close": 0,
                                        "live_bytes_after_sync": int(status.get("live_bytes", 0)),
                                        "native_cache_floor_before_fault": native_cache_floor})
    print(json.dumps({"backend": get_backend_name(), "device": backend_info(),
                      "alignment": args.alignment, "results": records}, indent=2))


if __name__ == "__main__":
    main()
