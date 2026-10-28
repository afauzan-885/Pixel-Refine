"""Compile isolated CPU INT64 V7 with generic broadcast elementwise kernels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compile import compile_pool
from .kernels.integer64 import ALL_I64_CANDIDATE_KERNELS
from .kernels.movement_i64 import ALL_I64_MOVEMENT_CANDIDATE_KERNELS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    kernels = ALL_I64_CANDIDATE_KERNELS + ALL_I64_MOVEMENT_CANDIDATE_KERNELS
    target = output_dir / "neural_cpu.tcm"
    compile_pool("cpu", target, extra_kernels=kernels)
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps({"kind": "neural_universal_int64_cpu_candidate_v7",
                    "graphs": [kernel.__name__ for kernel in kernels]}, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
