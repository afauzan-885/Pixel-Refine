"""Paired-process WeightNet 512 latency and RSS benchmark.

Run separately for each runtime to keep process RSS measurements isolated::

    python -m taichi_vision.taichi_aot.neural_universal.bench_weightnet --runtime ort --backend cpu
    python -m taichi_vision.taichi_aot.neural_universal.bench_weightnet --runtime taichi --backend cpu
    python -m taichi_vision.taichi_aot.neural_universal.bench_weightnet --runtime ort --backend vulkan --device-id 0
    python -m taichi_vision.taichi_aot.neural_universal.bench_weightnet --runtime taichi --backend vulkan --device-id 0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
import zipfile
from pathlib import Path

import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "database/Learning_Model/weightNet/weightnet_master.bundle"
PROFILES = {
    ("cpu", 512): "weightnet_512_cpu_1c_fp32.onnx",
    ("cpu", 1024): "weightnet_1024_cpu_1c_fp32.onnx",
    ("cuda", 512): "weightnet_512_gpu_1c_fp32.onnx",
    ("cuda", 1024): "weightnet_1024_gpu_1c_fp32.onnx",
    ("vulkan", 512): "weightnet_512_gpu_1c_fp32.onnx",
    ("vulkan", 1024): "weightnet_1024_gpu_1c_fp32.onnx",
}
WARMUP = 3
RUNS = 10
SEED = 20261025


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runtime", required=True,
        choices=("ort", "taichi", "taichi_static"),
    )
    parser.add_argument("--backend", choices=("cpu", "cuda", "vulkan"), default="cpu")
    parser.add_argument("--size", type=int, choices=(512, 1024), default=512)
    parser.add_argument("--device-id", type=int, default=0)
    parser.add_argument("--profile-variant", help="optional exact-profile static graph variant")
    parser.add_argument(
        "--pool-dir",
        help="optional explicit Taichi universal kernel pool directory (taichi runtime only)",
    )
    args = parser.parse_args()
    if args.pool_dir and args.runtime != "taichi":
        parser.error("--pool-dir is supported only with --runtime taichi")
    if args.pool_dir and args.backend != "cpu":
        parser.error("explicit candidate pools are currently benchmarked only on CPU")
    if args.profile_variant and (args.backend != "cpu" or args.size != 512):
        parser.error("profile variants are currently supported only for CPU512")
    profile = PROFILES[(args.backend, args.size)]

    with zipfile.ZipFile(BUNDLE) as archive:
        model = archive.read(profile)
    rng = np.random.default_rng(SEED)
    shape = (1, 1, args.size, args.size)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }

    dispatch_counter = [0]
    if args.runtime == "ort":
        import onnxruntime as ort

        if args.backend == "vulkan":
            session_options = ort.SessionOptions()
            session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            session_options.enable_mem_pattern = False
            session_options.add_session_config_entry(
                "session.disable_cpu_ep_fallback", "1"
            )
            providers = [("DmlExecutionProvider", {"device_id": args.device_id})]
            session = ort.InferenceSession(
                model, sess_options=session_options, providers=providers
            )
            provider = f"DmlExecutionProvider(device_id={args.device_id}, CPU fallback disabled)"
        elif args.backend == "cuda":
            session = ort.InferenceSession(
                model, providers=[("CUDAExecutionProvider", {"device_id": args.device_id})]
            )
            provider = f"CUDAExecutionProvider(device_id={args.device_id})"
        else:
            session = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
            provider = ",".join(session.get_providers())
        run = lambda: session.run(None, feeds)
    elif args.runtime == "taichi":
        from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

        session = UniversalSession(model, backend=args.backend, pool_dir=args.pool_dir)
        provider = f"native Taichi AOT {args.backend.upper()}"
        original_run = session.module.run

        def counted_run(*run_args, **run_kwargs):
            dispatch_counter[0] += 1
            return original_run(*run_args, **run_kwargs)

        session.module.run = counted_run
        run = lambda: session.run(None, feeds)
    else:
        from taichi_vision.taichi_aot.neural_universal.static_session import (
            StaticGraphSession,
        )

        session = StaticGraphSession(
            model, backend=args.backend, profile_variant=args.profile_variant
        )
        if not session.fast_path_active:
            raise RuntimeError(
                "static WeightNet profile is unavailable: "
                f"{session.last_fallback_reason}"
            )
        provider = f"native Taichi AOT static graph {args.backend.upper()}"
        original_run = session.static_module.run

        def counted_static_run(*run_args, **run_kwargs):
            dispatch_counter[0] += 1
            return original_run(*run_args, **run_kwargs)

        session.static_module.run = counted_static_run
        run = lambda: session.run(None, feeds)

    process = psutil.Process(os.getpid())
    baseline_rss = int(process.memory_info().rss)
    peak_rss = [baseline_rss]
    stop = threading.Event()

    def sample_memory() -> None:
        while not stop.is_set():
            try:
                peak_rss[0] = max(peak_rss[0], int(process.memory_info().rss))
            except psutil.Error:
                pass
            stop.wait(0.005)

    for _ in range(WARMUP):
        run()
    samples_ms = []
    dispatches_per_run = []
    sampler = threading.Thread(target=sample_memory, daemon=True)
    sampler.start()
    for _ in range(RUNS):
        dispatch_counter[0] = 0
        started = time.perf_counter()
        run()
        samples_ms.append((time.perf_counter() - started) * 1000.0)
        if args.runtime != "ort":
            dispatches_per_run.append(dispatch_counter[0])
    stop.set()
    sampler.join()
    peak_rss[0] = max(peak_rss[0], int(process.memory_info().rss))

    print(json.dumps({
        "runtime": args.runtime,
        "pool_dir": str(Path(args.pool_dir).resolve()) if args.pool_dir else None,
        "profile_variant": args.profile_variant if args.runtime == "taichi_static" else None,
        "provider": provider,
        "backend": args.backend.upper(),
        "device": (
            "host CPU"
            if args.backend == "cpu"
            else (getattr(session.engine, "gpu_name", None) or f"adapter {args.device_id}")
            if args.runtime in ("taichi", "taichi_static")
            else f"DirectML adapter {args.device_id}; physical adapter must be verified"
        ),
        "model_member": profile,
        "model_sha256": hashlib.sha256(model).hexdigest(),
        "input_shape": list(shape),
        "input_dtype": "float32",
        "seed": SEED,
        "warmup": WARMUP,
        "runs": RUNS,
        "latency_ms": samples_ms,
        "graph_dispatches_per_run": dispatches_per_run or None,
        "median_ms": float(np.median(samples_ms)),
        "p95_ms": float(np.percentile(samples_ms, 95)),
        "rss_baseline_bytes": baseline_rss,
        "rss_peak_bytes": peak_rss[0],
        "rss_delta_bytes": peak_rss[0] - baseline_rss,
        "device_memory_telemetry": "not collected",
        "boundary": "session.run includes input ingress and output egress; not compute-only",
    }))
    if hasattr(session, "close"):
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
