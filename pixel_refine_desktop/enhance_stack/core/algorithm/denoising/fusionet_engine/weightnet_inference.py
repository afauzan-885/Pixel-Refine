"""
WeightNet resident inference engine.

Loads the resident TCM WeightNet session, computes per-support confidence
maps through it, and blends one support into the running fusion accumulators.
Burst frame IO lives in :mod:`.burst_io` (re-exported here for compatibility).
"""

import os
import threading
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.burst_io import (  # noqa: F401
    RAW_EXTENSIONS,
    _apply_orientation,
    _read_image_orientation,
    burst_images_to_array,
    load_burst_images,
    load_rgb_linear_image,
    load_rgb_linear_image_bytes,
    normalize_burst_frames,
)

DEFAULT_WEIGHTNET_ONNX = Path(
    "database/Learning_Model/weightNet/weightnet_master.bundle"
)
def _validate_weightnet_input_channels(session, expected_channels: int):
    try:
        shape = session.get_inputs()[0].shape
    except Exception:
        return session
    if len(shape) >= 2 and isinstance(shape[1], int) and shape[1] != expected_channels:
        raise RuntimeError(
            f"WeightNet model input channel mismatch: requested {expected_channels}, "
            f"artifact expects {shape[1]} (shape={shape})"
        )
    return session
def load_weightnet_onnx(
    model_path: str | Path,
    runtime: str = "auto",
    patch_size: int = 512,
    input_channels: int | None = 1,
    max_safety: float = 0.30,
):
    source = Path(model_path)
    # Direct TCM file path loading
    if source.is_file() and source.suffix.lower() == ".tcm":
        from taichi_vision.taichi_algorithm.denoising.resident_weightnet import ResidentWeightNet
        from taichi_vision.taichi_algorithm.denoising.weightnet_artifact_identity import resident_weightnet_load_kwargs
        session = ResidentWeightNet(source, **resident_weightnet_load_kwargs())
        session.max_safety = float(max_safety)
        return session

    # Normalize runtime: Default and "auto" are 100% full native Taichi AOT (TCM)
    norm_runtime = str(runtime).strip().lower()
    if norm_runtime in ("auto", "default", "", "taichi_aot", "taichi_cuda"):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.denoising.resident_weightnet import ResidentWeightNet
        from taichi_vision.taichi_algorithm.denoising.weightnet_artifact_identity import (
            resident_weightnet_load_kwargs,
            selected_weightnet_model_bytes,
        )
        from taichi_vision.taichi_aot import neural

        backend = taichi_aot.get_backend_name()
        search_dirs = [
            source.parent if source.is_file() else source,
            Path("database/Learning_Model/nanoFlow"),
            Path("database/Learning_Model/weightNet"),
            Path("pixel_refine_desktop/ui/data/models"),
        ]
        # 1. First priority: direct prebaked TCM from aot_assets/neural
        custom_artifact = os.environ.get("PIXEL_REFINE_WEIGHTNET_AOT_ARTIFACT", "")
        if custom_artifact and Path(custom_artifact).is_file():
            artifact = Path(custom_artifact)
        else:
            tcm_candidate = neural.DEFAULT_AOT_NEURAL_DIR / f"weightnet_{patch_size}_{backend}.tcm"
            if tcm_candidate.is_file():
                artifact = tcm_candidate
            else:
                artifact = neural.find_prebaked_tcm(f"weightnet_{patch_size}", backend)

        if artifact is not None and Path(artifact).is_file():
            model_bytes = selected_weightnet_model_bytes(
                source, patch_size, search_dirs
            )
            session = ResidentWeightNet(
                Path(artifact), **resident_weightnet_load_kwargs(model_bytes)
            )
            print(f"[WeightNet AOT] backend={session.engine.arch} patch={patch_size} model={Path(artifact).name} host_patch_readback=0")
            session.max_safety = float(max_safety)
            return session

        # 2. If TCM not pre-baked, resolve or compile from bundle
        if source.is_file() and source.suffix.lower() == ".bundle":
            bundle = source
        else:
            bundle = next((d / name for d in search_dirs
                           for name in ("weightnet_master.bundle", "weightnet_v3_master.bundle")
                           if (d / name).is_file()), None)
        if bundle is not None and bundle.is_file():
            import zipfile
            member = f"weightnet_{patch_size}_gpu_1c_fp32.onnx"
            with zipfile.ZipFile(bundle) as archive:
                if member in archive.namelist():
                    model_bytes = archive.read(member)
                    artifact = neural.resolve_or_compile_tcm(
                        model_bytes,
                        backend=backend,
                        model_name=f"weightnet_{patch_size}",
                        patch_tools=True,
                    )
                    session = ResidentWeightNet(
                        artifact, **resident_weightnet_load_kwargs(model_bytes)
                    )
                    session.max_safety = float(max_safety)
                    return session

        raise FileNotFoundError(f"WeightNet TCM artifact not found for backend={backend} patch={patch_size}")

    # The ONNX Runtime route (DML/CPU) and the unreachable taichi_cuda
    # fallback were removed: every supported runtime resolves through
    # ResidentWeightNet above, matching the resident TCM executor.
    raise RuntimeError(
        f"WeightNet runtime {runtime!r} is no longer supported; the ONNX Runtime "
        "route was replaced by the resident TCM executor (auto/taichi_aot)."
    )


def infer_single_support_weight_map(
    session,
    ref_work: np.ndarray,
    supp_work: np.ndarray,
    *,
    tile_size: int = 512,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.05,
    chroma_sensitivity: float = 6.0,
    stop_event: Optional[threading.Event] = None,
    progress: Optional[Callable[[int, str], None]] = None,
    return_scalar: bool = False,
    max_safety: Optional[float] = None,
) -> tuple[np.ndarray, float]:
    """
    Computes a 3-channel fusion weight map for one reference/support pair.
    Inputs may be RGB CHW or already converted luminance [1, H, W].
    Output: weight_map_work [3, work_h, work_w] by default, or the native
    scalar map [1, work_h, work_w] when ``return_scalar`` is requested.
    """
    if getattr(session, "runtime", None) == "taichi_aot":
        ms_val = max_safety if max_safety is not None else getattr(session, "max_safety", 0.30)
        return session.infer(ref_work, supp_work, overlap=overlap, ghost_penalty=ghost_penalty,
                             ghost_cutoff=ghost_cutoff, stop_event=stop_event, max_safety=ms_val)
    raise RuntimeError(
        "WeightNet inference requires a resident TCM session; got runtime "
        f"{getattr(session, 'runtime', None)!r}. Load the model with "
        "load_weightnet_onnx (auto/taichi_aot)."
    )


def fuse_support_frame_inplace(
    sum_img: np.ndarray,
    weight_sum: np.ndarray,
    supp_full_chw: np.ndarray,
    weight_map_work: np.ndarray,
    full_h: int,
    full_w: int,
):
    """
    Upsamples single-support weight map to full resolution and blends in-place into sum_img and weight_sum.
    All inputs and outputs are [3, full_h, full_w] float32 arrays.
    """
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
        taichi_bridge,
    )

    channels, work_h, work_w = weight_map_work.shape
    if (work_h, work_w) != (full_h, full_w):
        for c in range(channels):
            w_full_c = taichi_aot.resize(
                weight_map_work[c],
                (full_w, full_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )
            sum_img[c] += supp_full_chw[c] * w_full_c
            weight_sum[c] += w_full_c
            del w_full_c
    else:
        sum_img += supp_full_chw * weight_map_work
        weight_sum += weight_map_work
