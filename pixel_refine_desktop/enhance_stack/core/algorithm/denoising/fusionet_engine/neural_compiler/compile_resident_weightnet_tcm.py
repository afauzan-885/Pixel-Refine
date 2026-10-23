"""Compile target-qualified Ahead-Of-Time (.tcm) artifacts for resident WeightNet."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import zipfile

_ROOT = Path(__file__).resolve().parents[7]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from taichi_vision.taichi_aot.artifact_targets import detect_target
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.neural_compiler.onnx_resident_aot import compile_resident_onnx


DEFAULT_BUNDLE = Path("database/Learning_Model/weightNet/weightnet_master.bundle")
DEFAULT_TCM_DIR = Path("pixel_refine_desktop/ui/data/aot_assets/neural")


def compile_single_target(
    backend: str,
    patch_size: int,
    *,
    bundle_path: Path = DEFAULT_BUNDLE,
    output_dir: Path = DEFAULT_TCM_DIR,
) -> Path:
    """Compile one target backend and patch size to its pre-baked neural AOT TCM."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"weightnet_{patch_size}_{backend}.tcm"

    member_name = f"weightnet_{patch_size}_gpu_1c_fp32.onnx"
    with zipfile.ZipFile(bundle_path) as z:
        if member_name not in z.namelist():
            raise FileNotFoundError(f"Member {member_name} not found in {bundle_path}")
        model_bytes = z.read(member_name)

    print(f"[WeightNet AOT Compiler] Compiling backend={backend} patch={patch_size} -> {out_path.name}...")
    compile_resident_onnx(model_bytes, out_path, backend=backend, patch_tools=True)
    size_kb = out_path.stat().st_size / 1024
    print(f"[WeightNet AOT Compiler] Output ready: {out_path} ({size_kb:.1f} KB)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Compile Ahead-Of-Time TCM models for resident WeightNet.")
    parser.add_argument("--backend", choices=("cpu", "cuda", "vulkan", "opengl", "all"), default="all")
    parser.add_argument("--patch-size", choices=("512", "1024", "all"), default="all")
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE))
    parser.add_argument("--output-dir", default=str(DEFAULT_TCM_DIR))
    parser.add_argument("--worker", action="store_true", help="Internal worker mode for isolated process")

    args = parser.parse_args()
    bundle_path = Path(args.bundle).resolve()
    output_dir = Path(args.output_dir).resolve()

    if args.worker:
        compile_single_target(
            backend=args.backend,
            patch_size=int(args.patch_size),
            bundle_path=bundle_path,
            output_dir=output_dir,
        )
        return

    backends = ["cuda", "vulkan", "opengl", "cpu"] if args.backend == "all" else [args.backend]
    patches = [512, 1024] if args.patch_size == "all" else [int(args.patch_size)]

    total_tasks = len(backends) * len(patches)
    print(f"[WeightNet AOT Compiler] Starting batch compilation: {total_tasks} target(s)...")

    results = []
    for b in backends:
        for p in patches:
            cmd = [
                sys.executable,
                __file__,
                "--backend", b,
                "--patch-size", str(p),
                "--bundle", str(bundle_path),
                "--output-dir", str(output_dir),
                "--worker",
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode != 0:
                print(f"[ERROR] Failed to compile backend={b} patch={p}:")
                print(proc.stdout)
                print(proc.stderr)
                sys.exit(proc.returncode)
            else:
                out_lines = [l for l in proc.stdout.splitlines() if "[WeightNet AOT Compiler]" in l]
                for l in out_lines:
                    print(f"  {l}")
                results.append((b, p))

    print(f"\n[WeightNet AOT Compiler] Successfully compiled all {len(results)} TCM targets!")


if __name__ == "__main__":
    main()
