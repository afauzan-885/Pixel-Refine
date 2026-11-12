"""Compile isolated CPU V14 with pairwise 2x2 AveragePool candidate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compile import compile_pool
from .kernels.integer64 import ALL_I64_CANDIDATE_KERNELS
from .kernels.movement_i64 import ALL_I64_MOVEMENT_CANDIDATE_KERNELS
from .kernels.pool_candidate import ALL_POOL_CANDIDATE_KERNELS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    kernels = (ALL_I64_CANDIDATE_KERNELS + ALL_I64_MOVEMENT_CANDIDATE_KERNELS
               + ALL_POOL_CANDIDATE_KERNELS)
    target = output_dir / "neural_cpu.tcm"
    compile_pool("cpu", target, extra_kernels=kernels)
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps({"kind": "neural_universal_int64_cpu_candidate_v14",
                    "graphs": [kernel.__name__ for kernel in kernels]}, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
