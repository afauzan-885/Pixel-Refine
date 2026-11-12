"""Paired standalone 1x1 Conv CPU benchmark with the WeightNet CPU512 layer shape."""

from __future__ import annotations

import argparse
import hashlib
import json
import threading
import time

import numpy as np
import psutil

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL_SHA256 = "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
CANDIDATE_POOL = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / MODEL_SHA256 / "cpu/conv1x1_spatial4_candidate_pool_v1"
)

SEED = 20261030
WARMUP = 3
RUNS = 10
WIDTH = 127
CI = 23
CO = 44


def _model_and_arrays():
    from onnx import TensorProto as T, helper as h, numpy_helper

    x_shape = [1, CI, WIDTH, WIDTH]
    weight_shape = [CO, CI, 1, 1]
    graph = h.make_graph(
        [
            h.make_node("Conv", ["x", "w", "b"], ["conv"]),
            h.make_node("Gelu", ["conv"], ["y"], domain="com.microsoft"),
        ],
        "conv1x1_spatial_benchmark",
        [h.make_tensor_value_info("x", T.FLOAT, x_shape)],
        [h.make_tensor_value_info("y", T.FLOAT, [1, CO, WIDTH, WIDTH])],
    )
    weights = np.random.default_rng(SEED + 1).uniform(-0.01, 0.01, weight_shape).astype(np.float32)
    bias = np.random.default_rng(SEED + 2).uniform(-0.01, 0.01, [CO]).astype(np.float32)
    graph.initializer.extend([
        numpy_helper.from_array(weights, "w"),
        numpy_helper.from_array(bias, "b"),
    ])
    model = h.make_model(
        graph,
        opset_imports=[h.make_opsetid("", 17), h.make_opsetid("com.microsoft", 1)],
    )
    model.ir_version = 10
    x = np.random.default_rng(SEED).uniform(-1, 1, x_shape).astype(np.float32)
    return model.SerializeToString(), x, weights, bias


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", choices=("ort", "base", "spatial"), required=True)
    args = parser.parse_args()
    model_bytes, x, weights, bias = _model_and_arrays()
    feeds = {"x": x}
    session = None
    dispatches = []
    if args.runtime == "ort":
        import onnxruntime as ort

        session = ort.InferenceSession(model_bytes, providers=["CPUExecutionProvider"])
        provider = ",".join(session.get_providers())
        run = lambda: session.run(None, feeds)
    else:
        from .runtime import UniversalSession

        session = UniversalSession(model_bytes, backend="cpu", pool_dir=CANDIDATE_POOL)
        x_buf = session.upload("bench_x", x.reshape(-1))
        w_buf = session.upload("bench_w", weights.reshape(-1))
        b_buf = session.upload("bench_b", bias.reshape(-1))
        y_buf = session.engine.allocate((CO * WIDTH * WIDTH,), dtype=np.float32, is_vector=False)
        session._live.append(y_buf)
        graph_name = "nu_conv2d_1x1_spatial4" if args.runtime == "spatial" else "nu_conv2d_1x1"
        if graph_name not in session.pool_graph_names:
            raise RuntimeError(f"candidate pool does not contain {graph_name}")
        kwargs = {
            "x": x_buf, "w": w_buf, "b": b_buf, "y": y_buf,
            "n_batch": 1, "ci": CI, "co": CO, "hw": WIDTH * WIDTH,
            "has_bias": 1, "act": 5,
        }
        provider = "native Taichi AOT CPU"

        def run():
            session.module.run(graph_name, **kwargs)
            dispatches.append(graph_name)
            return y_buf

    process = psutil.Process()
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
        "target_weightnet_model_sha256": MODEL_SHA256,
        "benchmark_graph_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "input_shape": list(x.shape),
        "weight_shape": list(weights.shape),
        "output_shape": [1, CO, WIDTH, WIDTH],
        "input_dtype": "float32",
        "activation": "com.microsoft::Gelu (exact)",
        "seed": SEED,
        "warmup": WARMUP,
        "runs": RUNS,
        "latency_ms": samples_ms,
        "dispatches_per_run": dispatches[WARMUP:] or None,
        "median_ms": float(np.median(samples_ms)),
        "p95_ms": float(np.percentile(samples_ms, 95)),
        "rss_baseline_bytes": baseline_rss,
        "rss_peak_bytes": peak_rss[0],
        "rss_delta_bytes": peak_rss[0] - baseline_rss,
        "boundary": "one Conv+Gelu call; native module.run for Taichi, session.run for ORT",
    }))
    if hasattr(session, "close"):
        session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
