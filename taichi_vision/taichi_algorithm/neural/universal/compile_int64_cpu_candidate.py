"""Compile an isolated CPU candidate pool with dynamic-int64 kernels."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .compile import compile_pool
from .kernels.integer64 import ALL_I64_CANDIDATE_KERNELS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "neural_cpu.tcm"
    compile_pool("cpu", target, extra_kernels=ALL_I64_CANDIDATE_KERNELS)
    (output_dir / "candidate_manifest.json").write_text(
        json.dumps({"kind": "neural_universal_int64_cpu_candidate_v1",
                    "graphs": [kernel.__name__ for kernel in ALL_I64_CANDIDATE_KERNELS]},
                   indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
