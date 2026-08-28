"""
Spatial Merging — Public API (ghost reduction for multi-frame fusion).

Exposed as ``taichi_aot.spatial_merging``.  Supports two modes:

    mode="weights"   → frame-by-frame: returns one weight map per support
                       frame (list).  Each weight map expresses how much of
                       that frame should contribute to the fusion (ghost
                       rejection already baked in).
    mode="fuse"      → batch: returns a single fused RGB result computed from
                       all support frames and their weight maps.

Noise & motion thresholds are auto-estimated from the reference frame when
not supplied (see ``noise_estimation``).
"""

from typing import Callable, List, Optional, Sequence, Tuple, Union

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine


def _as_gpu_work_gray(
    engine,
    frame,
    work_h: int,
    work_w: int,
) -> TaichiGPUBuffer:
    """Convert a frame (numpy or GPU) to a work-resolution grayscale GPU buffer."""
    import taichi_vision.taichi_aot as taichi_aot

    if isinstance(frame, np.ndarray):
        arr = np.asarray(frame, dtype=np.float32)
        if np.issubdtype(frame.dtype, np.integer):
            scale = 65535.0 if frame.dtype.itemsize > 1 else 255.0
            arr = arr.astype(np.float32) / scale
        frame_gpu = taichi_aot.upload(np.ascontiguousarray(arr, dtype=np.float32))
    elif isinstance(frame, TaichiGPUBuffer):
        frame_gpu = frame
    else:
        raise TypeError(f"Unsupported frame type: {type(frame)}")

    try:
        gray_gpu = None
        if frame_gpu.ndim == 3 and frame_gpu.shape[2] == 3:
            gray_gpu = taichi_aot.cvtColor(frame_gpu, taichi_aot.COLOR_RGB2GRAY)
            if frame_gpu is not frame:
                frame_gpu.destroy()
        elif frame_gpu.ndim == 2:
            gray_gpu = frame_gpu
        else:
            raise ValueError(f"Frame must be HxW or HxWx3, got {frame_gpu.shape}")

        if gray_gpu.shape[:2] != (work_h, work_w):
            resized = taichi_aot.resize(
                gray_gpu, (work_w, work_h),
                interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
            )
            if gray_gpu is not frame:
                gray_gpu.destroy()
            gray_gpu = resized
        return gray_gpu
    except Exception:
        if frame_gpu is not frame:
            try:
                frame_gpu.destroy()
            except Exception:
                pass
        raise


def _as_gpu_full_hwc(
    engine,
    frame,
) -> TaichiGPUBuffer:
    """Convert a frame to a full-resolution HWC float32 GPU buffer."""
    import taichi_vision.taichi_aot as taichi_aot

    if isinstance(frame, np.ndarray):
        arr = np.asarray(frame, dtype=np.float32)
        if np.issubdtype(frame.dtype, np.integer):
            scale = 65535.0 if frame.dtype.itemsize > 1 else 255.0
            arr = arr.astype(np.float32) / scale
        return taichi_aot.upload(np.ascontiguousarray(arr, dtype=np.float32))
    if isinstance(frame, TaichiGPUBuffer):
        if frame.dtype != np.float32:
            return frame.cast(np.float32)
        return frame
    raise TypeError(f"Unsupported frame type: {type(frame)}")


def spatial_merging(
    frames: Sequence[Union[np.ndarray, TaichiGPUBuffer]],
    reference: Optional[Union[np.ndarray, TaichiGPUBuffer]] = None,
    *,
    mode: str = "weights",
    work_scale: float = 1.0,
    tile_size: int = 16,
    overlap: float = 0.35,
    noise_sigma: Optional[float] = None,
    motion_sensitivity: Optional[float] = None,
    noise_offset_factor: Optional[float] = None,
    is_raw: bool = False,
    equalize_brightness: bool = False,
    search_radius: int = 3,
    early_exit_threshold: float = 0.05,
    return_gpu: bool = False,
    stop_event: Optional[object] = None,
    progress: Optional[Callable[[int, str], None]] = None,
    scratch_cache=None,
) -> Union[List[TaichiGPUBuffer], np.ndarray, TaichiGPUBuffer, Tuple[np.ndarray, float]]:
    """Ghost-reduction spatial merging for multi-frame burst fusion.

    Args:
        frames:   Support frames.  Reference is ``frames[0]`` unless provided.
        reference: Optional explicit reference frame (full resolution).
        mode:     ``"weights"`` (frame-by-frame weight maps) or
                  ``"fuse"`` (fused RGB result).
        work_scale: Downscale factor for weight analysis (1.0 = full res).
        tile_size:  Analysis tile size (e.g. 16).
        overlap:    Tile overlap ratio (0..1).
        noise_sigma: Explicit noise threshold; None → auto-estimate from ref.
        motion_sensitivity: Explicit motion/ghost sensitivity; None → default.
        noise_offset_factor: Noise offset before confidence decay; None → 0.15.
        is_raw:     Whether the burst is RAW/linear (tunes defaults).
        equalize_brightness: Pre-equalize brightness between frames.
        search_radius: Similarity search radius (ghost-rejection neighborhood).
        early_exit_threshold: Skip tiles below this confidence.
        return_gpu: Return GPU buffers instead of numpy (mode-dependent).
        stop_event: Cancellation event (callable ``is_set()``).
        progress:   Progress callback ``(percent, message)``.
        scratch_cache: Reusable :class:`SpatialScratchCache` for batched use.

    Returns:
        mode="weights": list of weight maps (one per support frame),
            work-resolution ``(work_h, work_w)`` float32 GPU/numpy.
        mode="fuse": fused RGB result ``(H, W, 3)`` float32 (GPU/numpy).
    """
    from .compute_spatial import (
        SpatialScratchCache,
        accumulate_spatial_merging_taichi,
        generate_spatial_weights_taichi,
        mean_division_vec3_weight_taichi,
    )
    from .noise_estimation import resolve_spatial_thresholds

    import taichi_vision.taichi_aot as taichi_aot

    mode = str(mode).strip().lower()
    if mode not in ("weights", "fuse"):
        raise ValueError(f"mode must be 'weights' or 'fuse', got {mode!r}")

    engine = get_engine()
    frame_list = list(frames)
    if not frame_list:
        raise ValueError("frames is empty")

    ref_frame = reference if reference is not None else frame_list[0]

    # Determine full resolution from the reference.
    ref_h, ref_w = ref_frame.shape[:2]
    work_h = max(8, int(ref_h * float(work_scale)))
    work_w = max(8, int(ref_w * float(work_scale)))

    if progress:
        progress(1, "Preparing reference (work-res grayscale)...")

    # Reference work-res grayscale GPU (reused for all support frames).
    ref_work_gray_gpu = _as_gpu_work_gray(engine, ref_frame, work_h, work_w)

    # Auto-resolve noise / motion thresholds from the reference directly in VRAM.
    noise_sigma, motion_sensitivity, noise_offset_factor = resolve_spatial_thresholds(
        ref_work_gray_gpu,
        noise_sigma=noise_sigma,
        motion_sensitivity=motion_sensitivity,
        noise_offset_factor=noise_offset_factor,
        is_raw=is_raw,
    )

    if progress:
        progress(3, f"noise_sigma={noise_sigma:.5f} "
                    f"motion_sensitivity={motion_sensitivity:.1f}")

    # Tile grid
    from .compute_spatial import _compute_tile_starts
    row_starts = _compute_tile_starts(work_h, tile_size, overlap=overlap)
    col_starts = _compute_tile_starts(work_w, tile_size, overlap=overlap)
    _rows_gpu = taichi_aot.upload(np.asarray(row_starts, dtype=np.int32))
    _cols_gpu = taichi_aot.upload(np.asarray(col_starts, dtype=np.int32))

    own_scratch = scratch_cache is None
    if own_scratch:
        scratch_cache = SpatialScratchCache()

    support_frames = frame_list[1:] if reference is None else frame_list

    try:
        # ------------------------------------------------------------------
        # Frame-by-frame weight generation
        # ------------------------------------------------------------------
        weight_maps: List[TaichiGPUBuffer] = []
        total = max(1, len(support_frames))
        for idx, frame in enumerate(support_frames):
            if stop_event is not None and stop_event.is_set():
                break

            # Work-res grayscale for the support frame.
            curr_work_gray_gpu = _as_gpu_work_gray(engine, frame, work_h, work_w)

            # Weight accumulator (work-res 2D, cleared in-place by the kernel).
            weight_work_gpu = engine.allocate(
                (work_h, work_w), dtype=np.float32, host_accessible=True
            )

            generate_spatial_weights_taichi(
                current_image=curr_work_gray_gpu,
                reference_image=ref_work_gray_gpu,
                weight_map_sum=weight_work_gpu,
                base_window=0,
                stability_map=None,
                row_starts=_rows_gpu,
                col_starts=_cols_gpu,
                tile_h=int(tile_size),
                tile_w=int(tile_size),
                noise_sigma=float(noise_sigma),
                motion_sensitivity=float(motion_sensitivity),
                noise_offset_factor=float(noise_offset_factor),
                equalize_brightness=bool(equalize_brightness),
                buffer_provider="pool",
                scratch_cache=scratch_cache,
                search_radius=int(search_radius),
                early_exit_threshold=float(early_exit_threshold),
            )

            # Release per-frame grayscale; keep the weight map.
            if curr_work_gray_gpu is not frame:
                curr_work_gray_gpu.destroy()
            weight_maps.append(weight_work_gpu)

            if progress:
                progress(
                    5 + int((idx + 1) / total * 60),
                    f"spatial weight {idx + 1}/{total}",
                )

        if mode == "weights":
            if return_gpu:
                return weight_maps
            try:
                return [w.to_numpy() for w in weight_maps]
            finally:
                for w in weight_maps:
                    try:
                        w.destroy()
                    except Exception:
                        pass

        # ------------------------------------------------------------------
        # Batch mode: fuse
        # ------------------------------------------------------------------
        if progress:
            progress(70, "Fusing weighted frames (GPU accumulate)...")

        # Full-res accumulators (HWC float32).  Reference seeds the sum.
        ref_full_gpu = _as_gpu_full_hwc(engine, ref_frame)
        sum_img_gpu = taichi_aot.copy(ref_full_gpu, return_gpu=True)

        try:
            # Use 2D accumulation for the classic luma-only batch path.
            weight_sum_2d = engine.upload(np.zeros((ref_h, ref_w), dtype=np.float32))
            for idx, frame in enumerate(support_frames):
                if stop_event is not None and stop_event.is_set():
                    break
                frame_full_gpu = _as_gpu_full_hwc(engine, frame)
                accumulate_spatial_merging_taichi(
                    current_image_full=frame_full_gpu.view_as_vector(False),
                    weight_map_work=weight_maps[idx],
                    final_image_sum=sum_img_gpu.view_as_vector(False),
                    weight_map_sum_full=weight_sum_2d,
                )
                if frame_full_gpu is not frame:
                    frame_full_gpu.destroy()
                if progress:
                    progress(
                        75 + int((idx + 1) / total * 20),
                        f"fusing frame {idx + 1}/{total}",
                    )

            # Per-channel mean division with reference fallback.
            weight_sum_3d = taichi_aot.upload(
                np.ascontiguousarray(
                    np.repeat(weight_sum_2d.to_numpy()[:, :, None], 3, axis=2),
                    dtype=np.float32,
                )
            )
            result_gpu = mean_division_vec3_weight_taichi(
                sum_img=sum_img_gpu,
                sum_weight=weight_sum_3d,
                ref_img=ref_full_gpu,
            )
            weight_sum_3d.destroy()
            weight_sum_2d.destroy()

            if progress:
                progress(97, "Spatial fusion complete.")

            if return_gpu:
                return result_gpu
            try:
                return np.ascontiguousarray(
                    result_gpu.to_numpy(), dtype=np.float32
                )
            finally:
                result_gpu.destroy()
        finally:
            sum_img_gpu.destroy()
            if isinstance(ref_full_gpu, TaichiGPUBuffer) and ref_full_gpu is not ref_frame:
                ref_full_gpu.destroy()
            for w in weight_maps:
                try:
                    w.destroy()
                except Exception:
                    pass
    finally:
        _rows_gpu.destroy()
        _cols_gpu.destroy()
        if ref_work_gray_gpu is not ref_frame:
            ref_work_gray_gpu.destroy()
        if own_scratch:
            scratch_cache.clear()
