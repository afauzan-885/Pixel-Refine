"""
WeightNet ONNX Inference Engine.
Handles loading images (Taichi AOT Hamilton demosaic + naturalTonemapping for RAW/DNG, PIL RGB for standard images),
converting burst to NumPy array [1, N, 3, H, W] float32 in [0.0, 1.0],
tiled ONNX inference (256x256 tiles, Hann overlap-add blending),
and full-resolution weighted average fusion.
Returns raw uncompressed float32 RGB array [H, W, 3] in range [0.0, 1.0].
"""

import os
import threading
from pathlib import Path
from typing import Callable, Optional, Sequence

import cv2
import numpy as np
from PIL import Image, ImageOps

DEFAULT_WEIGHTNET_ONNX = Path(
    "database/Learning_Model/weightNet/GPU/weightnet_256_gpu_fp32.onnx"
)
RAW_EXTENSIONS = {
    ".dng",
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".rw2",
    ".orf",
    ".raf",
    ".pef",
    ".srw",
}


def _load_raw_rgb_linear(path: Path) -> np.ndarray:
    """Decode RAW through Taichi AOT Hamilton demosaic to linear RGB float32."""
    try:
        from taichi_vision import taichi_aot
    except ImportError as exc:
        raise RuntimeError("DNG/RAW input requires taichi_vision AOT package.") from exc

    try:
        rgb_linear = taichi_aot.demosaic(
            str(path),
            method="hamilton",
            return_gpu=False,
        )
        if rgb_linear is None:
            raise RuntimeError("Taichi AOT Hamilton demosaic returned None")

        rgb_linear = np.asarray(rgb_linear)
        if rgb_linear.ndim != 3 or rgb_linear.shape[2] != 3:
            raise ValueError(
                f"Taichi AOT demosaic returned unexpected shape {rgb_linear.shape}"
            )
        if not np.issubdtype(rgb_linear.dtype, np.floating):
            rgb_linear = rgb_linear.astype(np.float32)
        else:
            rgb_linear = rgb_linear.astype(np.float32, copy=False)

        return np.ascontiguousarray(rgb_linear, dtype=np.float32)
    except Exception as exc:
        raise RuntimeError(
            f"Taichi AOT RAW pipeline failed for {path.name}: {exc}"
        ) from exc


def load_rgb_linear_image(path: str | Path) -> np.ndarray:
    """Load one standard image or DNG/RAW as linear RGB float32 in [0, 1]."""
    path = Path(path)
    if path.suffix.lower() in RAW_EXTENSIONS:
        image = _load_raw_rgb_linear(path)
    else:
        with Image.open(path) as pil_image:
            image = np.asarray(ImageOps.exif_transpose(pil_image).convert("RGB"))

    image = np.asarray(image)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"Expected RGB image at {path}, got shape {image.shape}")
    if np.issubdtype(image.dtype, np.integer):
        scale = 65535.0 if image.dtype.itemsize > 1 else 255.0
    elif np.issubdtype(image.dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"Unsupported image dtype at {path}: {image.dtype}")
    return np.ascontiguousarray(image.astype(np.float32) / scale, dtype=np.float32)


def load_burst_images(paths: Sequence[str | Path]) -> list[np.ndarray]:
    """
    Loads burst images:
    - For RAW/DNG: Analyzes histogram metrics ONCE on reference frame (paths[0])
      and applies AutoEnhance to reference and all support frames.
    - For Non-RAW (TIFF, PNG, JPEG, etc.): Loads images directly without AutoEnhance
      to preserve existing tone and color.
    """
    if not paths:
        raise ValueError("Burst is empty.")

    is_raw = any(Path(p).suffix.lower() in RAW_EXTENSIONS for p in paths)

    # 1. Load Reference Frame
    ref_image = load_rgb_linear_image(paths[0])
    target_h, target_w = ref_image.shape[:2]

    if is_raw:
        from taichi_vision import taichi_aot

        params = taichi_aot.analyze_auto_enhance_params(ref_image)
        print(
            f"[AutoEnhance Burst] Analyzed RAW ref={Path(paths[0]).name} -> "
            f"gain={params['gain']:.4f}, white={params['white_level']:.4f}, "
            f"shadow={params['shadow_lift']:.4f}, contrast={params['global_contrast']:.2f}"
        )
        ref_image = taichi_aot.AutoEnhance(ref_image, params=params)
    else:
        params = None
        print(f"[WeightNet Burst] Non-RAW mode: bypass AutoEnhance for {Path(paths[0]).name}")

    normalized = [np.ascontiguousarray(ref_image, dtype=np.float32)]

    # 2. Load Support Frames
    for source_path in paths[1:]:
        supp_image = load_rgb_linear_image(source_path)
        if is_raw and params is not None:
            from taichi_vision import taichi_aot

            supp_image = taichi_aot.AutoEnhance(supp_image, params=params)

        if supp_image.shape[:2] != (target_h, target_w):
            if Path(source_path).suffix.lower() in RAW_EXTENSIONS:
                supp_image = cv2.resize(
                    supp_image,
                    (target_w, target_h),
                    interpolation=cv2.INTER_LANCZOS4,
                ).astype(np.float32, copy=False)
            else:
                image_u8 = np.clip(supp_image * 255.0 + 0.5, 0, 255).astype(np.uint8)
                resized = Image.fromarray(image_u8, mode="RGB").resize(
                    (target_w, target_h), Image.Resampling.LANCZOS
                )
                supp_image = np.asarray(resized).astype(np.float32) / 255.0

        normalized.append(np.ascontiguousarray(supp_image, dtype=np.float32))

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
    patch_size: int = 256,
):
    try:
        import onnxruntime as ort
    except ImportError as exc:
        raise RuntimeError("ONNX inference requires the onnxruntime package.") from exc

    model_path = Path(model_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"WeightNet ONNX not found: {model_path}")

    runtime = str(runtime).strip().lower()
    available = set(ort.get_available_providers())
    if runtime == "auto":
        runtime = "dml" if "DmlExecutionProvider" in available else "cpu"
    if runtime == "dml":
        if "DmlExecutionProvider" not in available:
            raise RuntimeError(
                "DML runtime requested but DmlExecutionProvider is unavailable; "
                f"available={sorted(available)}"
            )
        providers = ["DmlExecutionProvider", "CPUExecutionProvider"]
    elif runtime == "cpu":
        providers = ["CPUExecutionProvider"]
    else:
        raise ValueError(
            f"Unsupported ONNX runtime {runtime!r}; choose auto, dml, or cpu."
        )

    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    options.enable_mem_pattern = runtime == "cpu"
    session = ort.InferenceSession(
        str(model_path), sess_options=options, providers=providers
    )

    inputs = {item.name: tuple(item.shape) for item in session.get_inputs()}
    outputs = {item.name for item in session.get_outputs()}
    expected_shape = (1, 1, int(patch_size), int(patch_size))
    if set(inputs) != {"ref_img", "support_img"}:
        raise RuntimeError(f"Unexpected WeightNet inputs: {inputs}")
    if any(shape != expected_shape for shape in inputs.values()):
        raise RuntimeError(
            f"Selected ONNX expects {inputs}, but tile size is {patch_size}."
        )
    if not {"weight_map", "alpha"}.issubset(outputs):
        raise RuntimeError(f"Unexpected WeightNet outputs: {sorted(outputs)}")

    print(
        f"[WeightNet ONNX] runtime={runtime} model={model_path.name} "
        f"providers={session.get_providers()} patch={patch_size}"
    )
    return session


def run_collab_onnx_inference(
    session,
    burst_full: np.ndarray,
    *,
    tile_size: int = 256,
    work_scale: float = 0.50,
    overlap: float = 0.30,
    ghost_penalty: float = 1.0,
    ghost_cutoff: float = 0.0,
    stop_event: Optional[threading.Event] = None,
    progress: Optional[Callable[[int, str], None]] = None,
) -> tuple[np.ndarray, float]:
    """
    Run core ONNX inference on burst array [1, N, 3, H, W] and return
    uncompressed fused float32 RGB array [H, W, 3] in range [0.0, 1.0].
    """
    if (
        not isinstance(burst_full, np.ndarray)
        or burst_full.ndim != 5
        or burst_full.shape[0] != 1
    ):
        raise ValueError(
            f"Expected burst [1,N,3,H,W], got {getattr(burst_full, 'shape', type(burst_full))}"
        )
    if tile_size not in (256, 512, 1024):
        raise ValueError("tile_size must be 256, 512, or 1024")

    burst_full = np.ascontiguousarray(burst_full, dtype=np.float32)
    _, frame_count, channels, full_h, full_w = burst_full.shape
    if channels != 3 or frame_count < 1:
        raise ValueError("Burst must contain RGB frames and at least one image.")

    work_scale = float(work_scale)
    work_h = max(1, int(full_h * work_scale))
    work_w = max(1, int(full_w * work_scale))
    if (work_h, work_w) != (full_h, full_w):
        burst_work = np.zeros(
            (1, frame_count, channels, work_h, work_w), dtype=np.float32
        )
        for i in range(frame_count):
            for c in range(channels):
                burst_work[0, i, c] = cv2.resize(
                    burst_full[0, i, c],
                    (work_w, work_h),
                    interpolation=cv2.INTER_LINEAR,
                )
    else:
        burst_work = burst_full

    burst_gray = (
        0.299 * burst_work[:, :, 0:1]
        + 0.587 * burst_work[:, :, 1:2]
        + 0.114 * burst_work[:, :, 2:3]
    )
    overlap_size = int(tile_size * float(overlap))
    stride = max(1, tile_size - overlap_size)
    weight_maps_work = np.zeros((frame_count - 1, 1, work_h, work_w), dtype=np.float32)
    weight_stitch_work = np.zeros((1, 1, work_h, work_w), dtype=np.float32)
    hann_1d = np.hanning(tile_size).astype(np.float32)
    window_2d = np.outer(hann_1d, hann_1d).reshape(1, 1, tile_size, tile_size)

    total_tiles = len(range(0, work_h, stride)) * len(range(0, work_w, stride))
    tile_index = 0
    alpha_total = 0.0
    for y in range(0, work_h, stride):
        for x in range(0, work_w, stride):
            if stop_event is not None and stop_event.is_set():
                raise RuntimeError("Inference cancelled.")
            y_end, x_end = min(y + tile_size, work_h), min(x + tile_size, work_w)
            y_start, x_start = max(0, y_end - tile_size), max(0, x_end - tile_size)
            current_h, current_w = y_end - y_start, x_end - x_start
            ref_patch = np.ascontiguousarray(
                burst_gray[:, 0, :, y_start:y_end, x_start:x_end],
                dtype=np.float32,
            )
            current_window = window_2d[:, :, :current_h, :current_w]
            for index in range(1, frame_count):
                support_patch = np.ascontiguousarray(
                    burst_gray[:, index, :, y_start:y_end, x_start:x_end],
                    dtype=np.float32,
                )
                if current_h != tile_size or current_w != tile_size:
                    ref_pad = np.zeros((1, 1, tile_size, tile_size), dtype=np.float32)
                    supp_pad = np.zeros((1, 1, tile_size, tile_size), dtype=np.float32)
                    ref_pad[:, :, :current_h, :current_w] = ref_patch
                    supp_pad[:, :, :current_h, :current_w] = support_patch
                    ref_in, supp_in = ref_pad, supp_pad
                else:
                    ref_in, supp_in = ref_patch, support_patch

                weight_np, alpha_np = session.run(
                    ["weight_map", "alpha"],
                    {"ref_img": ref_in, "support_img": supp_in},
                )
                weight = np.asarray(weight_np, dtype=np.float32)[
                    :, :, :current_h, :current_w
                ]
                weight_maps_work[
                    index - 1 : index, :, y_start:y_end, x_start:x_end
                ] += (weight * current_window)
                alpha_values = np.asarray(alpha_np, dtype=np.float32)
                if np.isfinite(alpha_values).all():
                    alpha_total += float(alpha_values.mean())

            weight_stitch_work[:, :, y_start:y_end, x_start:x_end] += current_window
            tile_index += 1
            if progress:
                progress(
                    int(tile_index * 80 / max(1, total_tiles)),
                    f"FusionNet tile {tile_index}/{total_tiles}",
                )

    weight_maps_work = np.clip(weight_maps_work / (weight_stitch_work + 1e-8), 0.0, 1.0)

    # Apply Ghost Penalty (Power scaling) & Soft Thresholding Cutoff
    if ghost_penalty != 1.0:
        weight_maps_work = np.power(weight_maps_work, float(ghost_penalty))

    if ghost_cutoff > 0.0:
        weight_maps_work = np.clip(
            (weight_maps_work - float(ghost_cutoff)) / (1.0 - float(ghost_cutoff)),
            0.0,
            1.0,
        )

    if (work_h, work_w) != (full_h, full_w):
        weight_maps_full = np.zeros(
            (frame_count - 1, 1, full_h, full_w), dtype=np.float32
        )
        for i in range(frame_count - 1):
            weight_maps_full[i, 0] = cv2.resize(
                weight_maps_work[i, 0], (full_w, full_h), interpolation=cv2.INTER_LINEAR
            )
    else:
        weight_maps_full = weight_maps_work

    sum_img = burst_full[0, 0].copy()
    weight_sum = np.ones((1, full_h, full_w), dtype=np.float32)
    for index in range(1, frame_count):
        current_weight = weight_maps_full[index - 1, 0:1]
        sum_img += burst_full[0, index] * current_weight
        weight_sum += current_weight
    result = np.clip(sum_img / (weight_sum + 1e-8), 0.0, 1.0)
    mean_alpha = alpha_total / max(1, total_tiles * (frame_count - 1))

    result_hwc = np.transpose(result, (1, 2, 0))  # [H, W, 3] float32
    if progress:
        progress(100, f"Finished ONNX; alpha={mean_alpha:.4f}")
    return result_hwc, mean_alpha


def run_weightnet_inference(
    image_paths: Sequence[str | Path],
    model_path: str | Path = DEFAULT_WEIGHTNET_ONNX,
    work_scale: float = 0.50,
    tile_size: int = 256,
    overlap: float = 0.30,
    ghost_penalty: Optional[float] = None,
    ghost_cutoff: Optional[float] = None,
    stop_event: Optional[threading.Event] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> tuple[np.ndarray, float]:
    """
    Self-contained inference engine:
    Accepts list of image paths -> loads burst -> executes tiled ONNX inference ->
    returns raw uncompressed float32 RGB array [H, W, 3] and mean alpha.
    """
    if progress_callback:
        progress_callback(5, "Loading FusionNet ONNX model...")
    session = load_weightnet_onnx(model_path, runtime="auto", patch_size=tile_size)

    is_raw = any(Path(p).suffix.lower() in RAW_EXTENSIONS for p in image_paths)
    if ghost_penalty is None:
        ghost_penalty = 1.30 if is_raw else 1.0
    if ghost_cutoff is None:
        ghost_cutoff = 0.05 if is_raw else 0.0

    print(
        f"[WeightNet Pipeline] RAW mode={is_raw} -> "
        f"ghost_penalty={ghost_penalty:.2f}, ghost_cutoff={ghost_cutoff:.2f}"
    )

    if progress_callback:
        progress_callback(10, f"Loading {len(image_paths)} burst images...")
    images = load_burst_images(image_paths)

    burst = burst_images_to_array(images)
    del images

    def internal_progress(val, msg):
        if progress_callback:
            mapped_val = 15 + int(val * 0.80)
            progress_callback(mapped_val, msg)

    result_fp32, alpha = run_collab_onnx_inference(
        session,
        burst,
        work_scale=work_scale,
        tile_size=tile_size,
        overlap=overlap,
        ghost_penalty=ghost_penalty,
        ghost_cutoff=ghost_cutoff,
        stop_event=stop_event,
        progress=internal_progress,
    )
    return result_fp32, alpha
