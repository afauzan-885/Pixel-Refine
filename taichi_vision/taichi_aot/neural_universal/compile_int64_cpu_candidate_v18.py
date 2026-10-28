"""Compile isolated CPU V18 with MLAS-order AveragePool and packet-4 norm."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import taichi as ti

from taichi_vision.taichi_aot.neural_universal.static_graph import (
    _configured_runtime_abi,
    _kernel_source_fingerprint,
    _sha256_file,
    _target_identity,
)

from .compile import compile_pool
from .kernels.integer64 import ALL_I64_CANDIDATE_KERNELS
from .kernels.movement_i64 import ALL_I64_MOVEMENT_CANDIDATE_KERNELS
from .kernels.norm_candidate import ALL_INSTANCE_NORM_CANDIDATE_KERNELS
from .kernels.pool_candidate import ALL_POOL_CANDIDATE_KERNELS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    kernels = (
        ALL_I64_CANDIDATE_KERNELS
        + ALL_I64_MOVEMENT_CANDIDATE_KERNELS
        + ALL_POOL_CANDIDATE_KERNELS
        + ALL_INSTANCE_NORM_CANDIDATE_KERNELS
    )
    target = output_dir / "neural_cpu.tcm"
    compile_pool("cpu", target, extra_kernels=kernels, fast_math=False)
    taichi_version = ".".join(str(part) for part in ti.__version__)
    manifest = {
        "schema_version": 2,
        "kind": "neural_universal_int64_cpu_candidate_v18",
        "backend": "cpu",
        "runtime_abi": _configured_runtime_abi(),
        "target_identity": _target_identity("cpu"),
        "taichi_version": taichi_version,
        "kernel_sources_sha256": _kernel_source_fingerprint(),
        "tcm_sha256": _sha256_file(target),
        "compile_options": {"fast_math": False},
        "graphs": [kernel.__name__ for kernel in kernels],
    }
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
