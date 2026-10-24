"""
WeightNet resident inference engine.

Handles loading images (Taichi AOT Hamilton demosaic for RAW/DNG, Taichi AOT
imread for standard images), converting burst to NumPy array [1, N, 3, H, W]
float32 in [0.0, 1.0], resident TCM WeightNet confidence inference, and
full-resolution weighted average fusion.
Returns raw uncompressed float32 RGB array [H, W, 3] in range [0.0, 1.0].
"""

import os
import threading
from pathlib import Path
from typing import Callable, Optional, Sequence

import numpy as np
import cv2
from PIL import Image

from pixel_refine_desktop.enhance_stack.core.algorithm.shared_utils import (
    RAW_EXTENSIONS,
    apply_orientation as _apply_orientation,
    read_orientation as _read_image_orientation,
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

# RAW_EXTENSIONS and the EXIF orientation helpers come from shared_utils.

def load_rgb_linear_image(path: str | Path, is_raw: bool = False) -> np.ndarray:
    """
    Loads an image in pure linear [0.0, 1.0] RGB float32.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    from taichi_vision import taichi_aot

    if is_raw or path.suffix.lower() in RAW_EXTENSIONS:
        try:
            demosaiced = taichi_aot.demosaic(
                str(path),
                method="hamilton",
                return_gpu=False,
            )
            img_np = np.asarray(demosaiced, dtype=np.float32)
        except Exception as exc:
            import rawpy

            with rawpy.imread(str(path)) as raw:
                rgb = raw.postprocess(
                    gamma=(1, 1),
                    no_auto_bright=True,
                    output_bps=16,
                    use_camera_wb=True,
                    highlight_mode=rawpy.HighlightMode.Blend,
                )
            img_np = rgb.astype(np.float32) / 65535.0
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise ValueError(
                f"Raw decoding failed for {path}, got shape {img_np.shape}"
            )
        max_v = float(np.max(img_np)) if img_np.size > 0 else 1.0
        if max_v > 1.5:
            scale = 65535.0 if max_v > 255.0 else 255.0
            img_np /= scale
        return np.ascontiguousarray(np.clip(img_np, 0.0, 1.0), dtype=np.float32)

    image_bgr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    if image_bgr is None:
        raise ValueError(f"Failed to read image: {path}")

    orientation = _read_image_orientation(path)
    if orientation != 1:
        image_bgr = _apply_orientation(image_bgr, orientation)

    if image_bgr.ndim == 2:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    del image_bgr

    if np.issubdtype(image_rgb.dtype, np.integer):
        scale = 65535.0 if image_rgb.dtype == np.uint16 else 255.0
        return np.ascontiguousarray(
            image_rgb.astype(np.float32) / scale, dtype=np.float32
        )
    return np.ascontiguousarray(image_rgb.astype(np.float32), dtype=np.float32)


def load_rgb_linear_image_bytes(
    path: str | Path,
    encoded: bytes | bytearray | memoryview,
    is_raw: bool = False,
) -> np.ndarray:
    """Decode unchanged source-file bytes into the canonical linear RGB format.

    This mirrors :func:`load_rgb_linear_image` while avoiding a second disk read
    after a source payload has been prefetched into the RAM Queue.
    """
    from io import BytesIO

    path = Path(path)
    encoded_bytes = bytes(encoded)
    if not encoded_bytes:
        raise ValueError(f"Image payload is empty: {path}")

    from taichi_vision import taichi_aot

    if is_raw or path.suffix.lower() in RAW_EXTENSIONS:
        try:
            import rawpy

            with rawpy.imread(BytesIO(encoded_bytes)) as raw:
                demosaiced = taichi_aot.demosaic(
                    raw,
                    method="hamilton",
                    return_gpu=False,
                )
            img_np = np.asarray(demosaiced, dtype=np.float32)
        except Exception:
            import rawpy

            with rawpy.imread(BytesIO(encoded_bytes)) as raw:
                rgb = raw.postprocess(
                    gamma=(1, 1),
                    no_auto_bright=True,
                    output_bps=16,
                    use_camera_wb=True,
                    highlight_mode=rawpy.HighlightMode.Blend,
                )
            img_np = rgb.astype(np.float32) / 65535.0
        if img_np.ndim != 3 or img_np.shape[2] != 3:
            raise ValueError(
                f"Raw decoding failed for {path}, got shape {img_np.shape}"
            )
        max_v = float(np.max(img_np)) if img_np.size > 0 else 1.0
        if max_v > 1.5:
            scale = 65535.0 if max_v > 255.0 else 255.0
            img_np /= scale
        return np.ascontiguousarray(np.clip(img_np, 0.0, 1.0), dtype=np.float32)

    image_bgr = cv2.imdecode(
        np.frombuffer(encoded_bytes, dtype=np.uint8), cv2.IMREAD_UNCHANGED
    )
    if image_bgr is None:
        raise ValueError(f"Failed to decode image bytes: {path}")

    try:
        with Image.open(BytesIO(encoded_bytes)) as image:
            orientation = int(image.getexif().get(0x0112, 1))
    except Exception:
        orientation = 1
    if orientation != 1:
        image_bgr = _apply_orientation(image_bgr, orientation)

    if image_bgr.ndim == 2:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_GRAY2RGB)
    else:
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    del image_bgr

    if np.issubdtype(image_rgb.dtype, np.integer):
        scale = 65535.0 if image_rgb.dtype == np.uint16 else 255.0
        return np.ascontiguousarray(
            image_rgb.astype(np.float32) / scale, dtype=np.float32
        )
    return np.ascontiguousarray(image_rgb.astype(np.float32), dtype=np.float32)


def load_burst_images(paths: Sequence[str | Path]) -> list[np.ndarray]:
    """
    Loads burst images and applies AutoEnhance:
    - Analyzes histogram metrics ONCE on reference frame (paths[0]).
    - Applies AutoEnhance with the derived parameters to reference and all support frames.
    """
    if not paths:
        raise ValueError("Burst is empty.")

    from taichi_vision import taichi_aot

    # 1. Load Reference Frame
    ref_linear = load_rgb_linear_image(paths[0])
    target_h, target_w = ref_linear.shape[:2]

    # 2. Analyze Reference Frame ONCE
    params = taichi_aot.analyze_auto_enhance_params(ref_linear, mode="analysis")
    print(
        f"[AutoEnhance Burst] Analyzed ref={Path(paths[0]).name} -> "
        f"gain={params['gain']:.4f}, white={params['white_level']:.4f}, "
        f"shadow={params['shadow_lift']:.4f}, contrast={params['global_contrast']:.2f}"
    )

    # 3. Apply AutoEnhance to Reference Frame
    ref_enhanced = taichi_aot.AutoEnhance(ref_linear, params=params)
    normalized = [np.ascontiguousarray(ref_enhanced, dtype=np.float32)]

    # 4. Apply AutoEnhance to Support Frames
    for source_path in paths[1:]:
        supp_linear = load_rgb_linear_image(source_path)
        supp_enhanced = taichi_aot.AutoEnhance(supp_linear, params=params)

        if supp_enhanced.shape[:2] != (target_h, target_w):
            supp_enhanced = taichi_aot.resize(
                supp_enhanced,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )

        normalized.append(np.ascontiguousarray(supp_enhanced, dtype=np.float32))

    return normalized


def normalize_burst_frames(
    frames: Sequence[np.ndarray],
    is_raw: bool = False,
) -> list[np.ndarray]:
    """
    Normalizes a list of in-memory image frames (e.g. from FlowNet alignment):
    - Scales integer types (uint8, uint16) to float32 in [0.0, 1.0].
    """
    if not frames:
        raise ValueError("Frames list is empty.")

    target_h, target_w = frames[0].shape[:2]

    def _to_f32(img):
        img_arr = np.asarray(img)
        if np.issubdtype(img_arr.dtype, np.integer):
            scale = 65535.0 if img_arr.dtype.itemsize > 1 else 255.0
            return np.ascontiguousarray(
                img_arr.astype(np.float32) / scale, dtype=np.float32
            )
        elif np.issubdtype(img_arr.dtype, np.floating):
            max_v = float(np.max(img_arr)) if img_arr.size > 0 else 1.0
            if max_v > 1.5:
                scale = 65535.0 if max_v > 255.0 else 255.0
                return np.ascontiguousarray(
                    img_arr.astype(np.float32) / scale, dtype=np.float32
                )
            return np.ascontiguousarray(
                img_arr.astype(np.float32, copy=False), dtype=np.float32
            )
        return np.ascontiguousarray(img_arr.astype(np.float32), dtype=np.float32)

    normalized = []
    for f in frames:
        f32 = _to_f32(f)
        if f32.shape[:2] != (target_h, target_w):
            from taichi_vision import taichi_aot

            f32 = taichi_aot.resize(
                f32,
                (target_w, target_h),
                interpolation=taichi_aot.INTER_LINEAR,
            )
        normalized.append(np.ascontiguousarray(f32, dtype=np.float32))

    return normalized


def burst_images_to_array(images: Sequence[np.ndarray]) -> np.ndarray:
    if not images:
        raise ValueError("Cannot convert an empty burst to an array.")
    stacked = np.stack(images, axis=0)  # [N, H, W, 3]
    array = np.transpose(stacked, (0, 3, 1, 2))[np.newaxis, ...]  # [1, N, 3, H, W]
    return np.ascontiguousarray(array, dtype=np.float32)

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
