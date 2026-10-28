"""Compile an opt-in, single-graph WeightNet profile from the generic lowerings."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np

from .static_graph import capture_universal_session, write_static_profile

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = ROOT / "database/Learning_Model/weightNet/weightnet_master.bundle"
DEFAULT_OUTPUT = ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
PROFILE_INPUTS = {
    "weightnet_512_cpu_1c_fp32.onnx": ("cpu", 512),
    "weightnet_1024_cpu_1c_fp32.onnx": ("cpu", 1024),
    "weightnet_512_gpu_1c_fp32.onnx": ("vulkan", 512),
}


def compile_profile(
    member: str,
    output_root: Path,
    *,
    fast_conv4x4_unroll: bool = False,
    fast_conv4x4_plain: bool = False,
    fast_conv4x4_linear_ci: bool = False,
    fast_conv4x4_ndrange: bool = False,
    fast_conv4x4_parallelize8: bool = False,
    fast_conv4x4_spatial_2x2: bool = False,
    fast_conv1x1_spatial4: bool = False,
) -> Path:
    if sum((fast_conv4x4_unroll, fast_conv4x4_plain, fast_conv4x4_linear_ci, fast_conv4x4_ndrange, fast_conv4x4_parallelize8, fast_conv4x4_spatial_2x2, fast_conv1x1_spatial4)) > 1:
        raise ValueError("select only one Conv4x4 static variant")
    try:
        backend, size = PROFILE_INPUTS[member]
    except KeyError as exc:
        raise ValueError(f"unsupported model profile {member!r}") from exc
    with zipfile.ZipFile(BUNDLE) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        model_bytes = archive.read(member)
    model_sha = hashlib.sha256(model_bytes).hexdigest()
    rng = np.random.default_rng(20261025)
    shape = (1, 1, size, size)
    feeds = {
        "ref_img": rng.uniform(-1, 1, shape).astype(np.float32),
        "support_img": rng.uniform(-1, 1, shape).astype(np.float32),
    }
    pool_root = ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural"
    capture = capture_universal_session(
        model_bytes, feeds, backend=backend, pool_dir=pool_root
    )
    profile_dir = Path(output_root) / model_sha / backend
    kernel_overrides = {}
    if fast_conv4x4_unroll:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("unrolled Conv variant is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_kahan_unrolled

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_kahan_unrolled
        profile_dir = profile_dir / "conv4x4_kahan_unroll"
    if fast_conv4x4_plain:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("plain accumulation is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_plain

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_plain
        profile_dir = profile_dir / "conv4x4_plain"
    if fast_conv4x4_linear_ci:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("linear-CI Conv variant is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_kahan_linear_ci

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_kahan_linear_ci
        profile_dir = profile_dir / "conv4x4_kahan_linear_ci"
    if fast_conv4x4_ndrange:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("ndrange Conv variant is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_kahan_ndrange

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_kahan_ndrange
        profile_dir = profile_dir / "conv4x4_kahan_ndrange"
    if fast_conv4x4_parallelize8:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("parallelize=8 Conv variant is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_kahan_p8

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_kahan_p8
        profile_dir = profile_dir / "conv4x4_kahan_parallelize8"
    if fast_conv4x4_spatial_2x2:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("spatial 2x2 Conv variant is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_4x4_s2_spatial_2x2

        kernel_overrides["nu_conv2d_4x4_s2"] = nu_conv2d_4x4_s2_spatial_2x2
        profile_dir = profile_dir / "conv4x4_spatial2x2"
    if fast_conv1x1_spatial4:
        if member != "weightnet_512_cpu_1c_fp32.onnx":
            raise ValueError("spatial-four Conv1x1 is approved only for canonical CPU512")
        from .kernels.conv import nu_conv2d_1x1_spatial4

        kernel_overrides["nu_conv2d_1x1"] = nu_conv2d_1x1_spatial4
        profile_dir = profile_dir / "conv1x1_spatial4"
    graph_name = f"wn_{size}_{backend}_{model_sha[:12]}"
    if fast_conv4x4_unroll:
        graph_name += "_conv4x4_unroll"
    if fast_conv4x4_plain:
        graph_name += "_conv4x4_plain"
    if fast_conv4x4_linear_ci:
        graph_name += "_conv4x4_kahan_linear_ci"
    if fast_conv4x4_ndrange:
        graph_name += "_conv4x4_kahan_ndrange"
    if fast_conv4x4_parallelize8:
        graph_name += "_conv4x4_kahan_parallelize8"
    if fast_conv4x4_spatial_2x2:
        graph_name += "_conv4x4_spatial2x2"
    if fast_conv1x1_spatial4:
        graph_name += "_conv1x1_spatial4"
    profile = write_static_profile(
        capture, model_bytes, backend, profile_dir, graph_name,
        kernel_overrides=kernel_overrides,
    )
    result = {
        "model_member": member,
        "bundle_profile": next(
            (name for name, info in manifest.get("models", {}).items()
             if info.get("file_name") == member),
            "unknown",
        ),
        "model_sha256": model_sha,
        "backend": backend,
        "input_shape": list(shape),
        "input_dtype": "float32",
        "graph_name": graph_name,
        "profile_dir": str(profile_dir.resolve()),
        "dispatches": profile["dispatches"],
        "slot_count": len(profile["slots"]),
        "slot_elements": sum(slot["elements"] for slot in profile["slots"]),
        "slot_bytes": profile["slot_bytes"],
        "graph_arguments": (
            len(profile["input_args"]) + len(profile["constant_args"])
            + len(profile["slots"]) + len(profile["scalar_values"])
        ),
    }
    print(json.dumps(result, sort_keys=True))
    return profile_dir


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--member", required=True, choices=sorted(PROFILE_INPUTS))
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT))
    parser.add_argument(
        "--fast-conv4x4-unroll", action="store_true",
        help="profile-only Kahan-preserving unroll variant for exact CPU512 model hash",
    )
    parser.add_argument(
        "--fast-conv4x4-plain", action="store_true",
        help="profile-only plain FP32 Conv4x4 accumulation for exact CPU512 model hash",
    )
    parser.add_argument(
        "--fast-conv4x4-linear-ci", action="store_true",
        help="profile-only direct CI loop preserving Kahan order for exact CPU512 model hash",
    )
    parser.add_argument(
        "--fast-conv4x4-ndrange", action="store_true",
        help="profile-only coordinate iteration preserving Kahan order for exact CPU512 model hash",
    )
    parser.add_argument(
        "--fast-conv4x4-parallelize8", action="store_true",
        help="profile-only CPU 8-thread scheduling with baseline Conv arithmetic for exact CPU512",
    )
    parser.add_argument(
        "--fast-conv4x4-spatial-2x2", action="store_true",
        help="profile-only 2x2 spatial tile preserving ordered Kahan sums for exact CPU512",
    )
    parser.add_argument(
        "--fast-conv1x1-spatial4", action="store_true",
        help="profile-only four-position spatial tile preserving Conv1x1 IC order for exact CPU512",
    )
    args = parser.parse_args(argv)
    compile_profile(
        args.member, Path(args.output_root),
        fast_conv4x4_unroll=args.fast_conv4x4_unroll,
        fast_conv4x4_plain=args.fast_conv4x4_plain,
        fast_conv4x4_linear_ci=args.fast_conv4x4_linear_ci,
        fast_conv4x4_ndrange=args.fast_conv4x4_ndrange,
        fast_conv4x4_parallelize8=args.fast_conv4x4_parallelize8,
        fast_conv4x4_spatial_2x2=args.fast_conv4x4_spatial_2x2,
        fast_conv1x1_spatial4=args.fast_conv1x1_spatial4,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
