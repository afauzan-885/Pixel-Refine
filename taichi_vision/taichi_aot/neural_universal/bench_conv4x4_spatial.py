"""Paired standalone Conv4x4/stride-2 CPU kernel benchmark.

Run each mode in a separate process so RSS baselines remain comparable::

    python -m taichi_vision.taichi_aot.neural_universal.bench_conv4x4_spatial --runtime ort
    python -m taichi_vision.taichi_aot.neural_universal.bench_conv4x4_spatial --runtime base
    python -m taichi_vision.taichi_aot.neural_universal.bench_conv4x4_spatial --runtime spatial
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
from pathlib import Path

import numpy as np
import psutil

ROOT = Path(__file__).resolve().parents[3]
MODEL_SHA256 = "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
CANDIDATE_POOL = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / MODEL_SHA256 / "cpu/conv4x4_spatial2x2_candidate_pool_v1"
)
WARMUP = 3
RUNS = 10
SEED = 20261027


def _model_bytes():
    import onnx
    from onnx import TensorProto as T, helper as h, numpy_helper

    x_shape = [1, 23, 256, 256]
    weight_shape = [20, 23, 4, 4]
    graph = h.make_graph(
        [
            h.make_node("Conv", ["x", "w", "b"], ["conv"], strides=[2, 2]),
            h.make_node("Gelu", ["conv"], ["y"], domain="com.microsoft"),
        ],
        "conv4x4_spatial_benchmark",
        [h.make_tensor_value_info("x", T.FLOAT, x_shape)],
        [h.make_tensor_value_info("y", T.FLOAT, [1, 20, 127, 127])],
    )
    weights = np.random.default_rng(SEED + 1).uniform(
        -0.01, 0.01, weight_shape
    ).astype(np.float32)
    bias = np.random.default_rng(SEED + 2).uniform(-0.01, 0.01, [20]).astype(np.float32)
    graph.initializer.extend([
        numpy_helper.from_array(weights, "w"),
        numpy_helper.from_array(bias, "b"),
    ])
    model = h.make_model(
        graph,
        opset_imports=[h.make_opsetid("", 17), h.make_opsetid("com.microsoft", 1)],
    )
    model.ir_version = 10
    return model.SerializeToString(), weights, bias


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=("ort", "base", "spatial"), required=True)
    args = parser.parse_args()

    model_bytes, weights, bias = _model_bytes()
    x_shape = (1, 23, 256, 256)
    y_shape = (1, 20, 127, 127)
    x = np.random.default_rng(SEED).uniform(-1, 1, x_shape).astype(np.float32)
    feeds = {"x": x}
    dispatches = []
    session = None
    if args.runtime == "ort":
        import onnxruntime as ort

        session = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"])
        provider = ",".join(session.get_providers())
        run = lambda: session.run(None, feeds)
    else:
        from taichi_vision.taichi_aot.neural_universal.runtime import UniversalSession

        session = UniversalSession(model_bytes, backend="cpu", pool_dir=CANDIDATE_POOL)
        x_buffer = session.upload("bench_x", x.reshape(-1))
        w_buffer = session.upload("bench_w", weights.reshape(-1))
        b_buffer = session.upload("bench_b", bias.reshape(-1))
        output = session.engine.allocate((int(np.prod(y_shape)),), dtype=np.float32, is_vector=False)
        session._live.append(output)
        kwargs = {
            "x": x_buffer, "w": w_buffer, "b": b_buffer, "y": output,
            "n_batch": 1, "ci": 23, "co": 20, "h": 256, "w_in": 256,
            "oh": 127, "ow": 127, "group": 1, "has_bias": 1, "act": 5,
        }
        graph_name = (
            "nu_conv2d_4x4_s2_spatial_2x2"
            if args.runtime == "spatial" else "nu_conv2d_4x4_s2"
        )
        if graph_name not in session.pool_graph_names:
            raise RuntimeError(f"candidate pool does not contain {graph_name}")
        provider = "native Taichi AOT CPU"

        def run():
            session.module.run(graph_name, **kwargs)
            dispatches.append(graph_name)
            return output

    process = psutil.Process(os.getpid())
    baseline_rss = int(process.memory_info().rss)
    peak_rss = [baseline_rss]
    stop = threading.Event()

    def sample_memory():
        while not stop.is_set():
            try:
                peak_rss[0] = max(peak_rss[0], int(process.memory_info().rss))
            except psutil.Error:
                pass
            stop.wait(0.005)

    for _ in range(WARMUP):
        run()
    samples_ms = []
    sampler = threading.Thread(target=sample_memory, daemon=True)
    sampler.start()
    for _ in range(RUNS):
        started = time.perf_counter()
        run()
        samples_ms.append((time.perf_counter() - started) * 1000.0)
    stop.set()
    sampler.join()
    peak_rss[0] = max(peak_rss[0], int(process.memory_info().rss))

    print(json.dumps({
        "runtime": args.runtime,
        "provider": provider,
        "backend": "CPU",
        "device": "host CPU",
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "input_shape": list(x_shape),
        "weight_shape": list(weights.shape),
        "output_shape": list(y_shape),
        "input_dtype": "float32",
        "activation": "com.microsoft::Gelu (exact)",
        "seed": SEED,
        "warmup": WARMUP,
        "runs": RUNS,
        "latency_ms": samples_ms,
        "dispatches_per_run": (
            dispatches[WARMUP:] if dispatches else None
        ),
        "median_ms": float(np.median(samples_ms)),
        "p95_ms": float(np.percentile(samples_ms, 95)),
        "rss_baseline_bytes": baseline_rss,
        "rss_peak_bytes": peak_rss[0],
        "rss_delta_bytes": peak_rss[0] - baseline_rss,
        "boundary": "one Conv call; native module.run for Taichi, session.run for ORT",
    }))
    if hasattr(session, "close"):
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
