"""Compile a separate CPU candidate pool with the unary->binary fusion kernel.

The generated pool is model-hash and backend qualified and never replaces the
default ``neural_cpu.tcm``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .compile import ROOT, compile_pool
from .kernels.elementwise import nu_fused_unary_binary

MODEL_SHA256 = "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
DEFAULT_OUTPUT = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / MODEL_SHA256 / "cpu/unary_binary_candidate_pool_v2/neural_cpu.tcm"
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite candidate pool: {output}")
    compile_pool("cpu", output, extra_kernels=(nu_fused_unary_binary,))
    manifest = {
        "model_sha256": MODEL_SHA256,
        "backend": "cpu",
        "kernel": nu_fused_unary_binary.__name__,
        "pool_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "pool_path": str(output.resolve()),
    }
    manifest_path = output.parent / "candidate_pool.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
