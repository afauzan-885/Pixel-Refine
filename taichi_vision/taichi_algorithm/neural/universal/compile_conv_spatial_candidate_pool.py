"""Compile isolated CPU pool for the spatial 2x2 Conv4x4 candidate."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .compile import ROOT, compile_pool
from .kernels.conv import nu_conv2d_4x4_s2_spatial_2x2

MODEL_SHA256 = "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
DEFAULT_OUTPUT = (
    ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
    / MODEL_SHA256 / "cpu/conv4x4_spatial2x2_candidate_pool_v1/neural_cpu.tcm"
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args(argv)
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(f"refusing to overwrite candidate pool: {output}")
    compile_pool("cpu", output, extra_kernels=(nu_conv2d_4x4_s2_spatial_2x2,))
    manifest = {
        "model_sha256": MODEL_SHA256,
        "backend": "cpu",
        "kernel": nu_conv2d_4x4_s2_spatial_2x2.__name__,
        "pool_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "pool_path": str(output.resolve()),
    }
    (output.parent / "candidate_pool.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
