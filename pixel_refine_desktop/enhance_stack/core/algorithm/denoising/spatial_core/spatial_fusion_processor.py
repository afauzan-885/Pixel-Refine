"""
SpatialFusionProcessor — GPU AOT Spatial Fusion for MFDenoiser.

Uses compute_spatial module's Taichi AOT kernels for ghost rejection.
Requires GPU AOT engine — raises error if unavailable.

Algorithm (per frame):
  1. Precompute gradients + coarse analysis → guidance map
  2. Fine analysis (4-pass sliding window MAD) → per-frame weight map
  3. Bilinear upsample work-res weights → full-res
  4. Accumulate: sum += frame * weight
  5. Finalize: result = sum / weight_sum
"""

import os
import gc
import numpy as np


class SpatialFusionProcessor:
    """GPU AOT Spatial Fusion processor for MFDenoiser.

    Uses compute_spatial module's Taichi AOT kernels for ghost rejection.
    Requires GPU AOT engine — raises RuntimeError if unavailable.

    Args:
        motion_sensitivity: Higher = more aggressive ghost rejection (default 150.0).
        noise_offset_factor: Noise floor offset for weight calculation (default 0.15).
        early_exit_threshold: Skip tiles below this confidence (default 0.05).
        equalize_brightness: Enable brightness equalization before weight calc.
    """

    def __init__(
        self,
        motion_sensitivity=150.0,
        noise_offset_factor=0.15,
        early_exit_threshold=0.05,
        equalize_brightness=False,
    ):
        self.motion_sensitivity = motion_sensitivity
        self.noise_offset_factor = noise_offset_factor
        self.early_exit_threshold = early_exit_threshold
        self.equalize_brightness = equalize_brightness

    def process(
        self,
        images,
        reference_image_float,
        ref_h,
        ref_w,
        ref_dtype,
        work_res_h=None,
        work_res_w=None,
        update_progress=None,
        stop_requested=None,
        is_linear_mode=False,
        proxy_scale=1.0,
        **kwargs,
    ):
        """Run full GPU spatial fusion pipeline.

        Args:
            images: Either a list of images or path to HDF5 file.
            reference_image_float: Normalized reference image (H, W, C) float32 [0,1].
            ref_h, ref_w: Reference image dimensions.
            ref_dtype: Original dtype of reference image (e.g. np.uint16).
            work_res_h, work_res_w: Working resolution (default: same as ref).
            update_progress: Progress callback (progress_percent, message).
            stop_requested: Stop check callback.
            is_linear_mode: Enable linear mode processing.
            proxy_scale: Proxy scale factor for linear mode.
            **kwargs: Additional parameters (image_paths, etc.).

        Returns:
            (frame_count, final_image_sum, weight_sum, ref_noise_sigma)

        Raises:
            RuntimeError: If GPU AOT engine is not available.
        """
        from taichi_vision import taichi_aot
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
            taichi_bridge,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            SpatialScratchCache,
            generate_spatial_weights_taichi,
            accumulate_spatial_merging_taichi,
        )

        engine = taichi_aot.engine
        if str(getattr(engine, "arch", "")).lower() == "cpu":
            raise RuntimeError(
                "[SpatialFusion] GPU AOT engine is running on CPU fallback. "
                "Spatial fusion requires the active taichi_aot Vulkan/CUDA engine."
            )

        # Defaults
        if work_res_h is None:
            work_res_h = ref_h
        if work_res_w is None:
            work_res_w = ref_w

        # Reserve a bounded resident working set for the repeated frame loop.
        # The runtime may reclaim it under pressure; callers never need to
        # manage block ownership manually.
        channels = (
            reference_image_float.shape[2] if reference_image_float.ndim == 3 else 1
        )
        frame_bytes = (
            int(ref_h) * int(ref_w) * max(channels, 1) * np.dtype(np.float32).itemsize
        )
        block_config = taichi_aot.get_block_config()
        cache_budget = int(
            (
                block_config.get("device_cache_bytes", 0)
                if isinstance(block_config, dict)
                else getattr(block_config, "device_cache_bytes", 0)
            )
            or 0
        )
        soft_reservation = min(
            max(frame_bytes // 4, 8 * 1024 * 1024),
            max(cache_budget // 2, 8 * 1024 * 1024),
        )
        taichi_aot.configure_block_reservation(
            "spatial_fusion",
            soft_bytes=soft_reservation,
            hard_bytes=max(soft_reservation, min(frame_bytes, cache_budget)),
            weight=2.0,
        )

        # Tile configuration for internal tiling
        tile_h = kwargs.get("tile_h", 16)
        tile_w = kwargs.get("tile_w", 16)

        # Compute tile starts for internal tiling
        row_starts = self._compute_tile_starts(
            work_res_h, tile_h, overlap=kwargs.get("overlap", 0.3)
        )
        col_starts = self._compute_tile_starts(
            work_res_w, tile_w, overlap=kwargs.get("overlap", 0.3)
        )

        # Determine number of images
        data_source = kwargs.get("data_source", images)
        image_paths = kwargs.get("image_paths", None)

        if isinstance(data_source, str) and data_source.endswith(".h5"):
            import h5py

            with h5py.File(data_source, "r") as f:
                num_images = sum(1 for k in f.keys() if k.startswith("image_"))
        elif isinstance(data_source, list):
            num_images = len(data_source)
        elif images is not None and isinstance(images, list):
            num_images = len(images)
            data_source = None
        else:
            print("[SpatialFusion] No images to process.")
            return 0, None, None, 0.0

        if num_images == 0:
            print("[SpatialFusion] No images to process.")
            return 0, None, None, 0.0

        print(f"[SpatialFusion] Processing {num_images} images with GPU AOT...")
        print(f"[SpatialFusion] Work resolution: {work_res_w}x{work_res_h}")
        print(
            "[SpatialFusion] Analysis buffer: "
            f"{'naturalTonemapping -> float32 -> grayscale' if is_linear_mode else 'standard normalized grayscale'}; "
            "fusion buffer: linear normalized float32"
        )
        print(
            f"[SpatialFusion] Tile size: {tile_w}x{tile_h}, Rows: {len(row_starts)}, Cols: {len(col_starts)}"
        )

        # Prepare reference on GPU
        ref_work_res_pass2_gpu, ref_noise_sigma = taichi_bridge.prepare_reference_aot(
            reference_image_float, is_linear_mode, proxy_scale, work_res_h, work_res_w
        )

        print(f"[SpatialFusion] Reference noise sigma: {ref_noise_sigma:.6f}")

        # Global accumulation buffers
        final_image_sum_full_res = np.zeros((ref_h, ref_w, channels), dtype=np.float32)
        weight_map_sum_full_res = np.zeros((ref_h, ref_w), dtype=np.float32)

        processed_count = 0
        # The frame loop is sequential, so these analysis buffers can be
        # safely reused between dispatches.  In particular, the reference
        # pyramid/gradients are invariant for the complete batch.
        spatial_scratch = SpatialScratchCache()

        try:
            _sum_gpu = taichi_aot.upload(final_image_sum_full_res)
            _weight_sum_full_gpu = taichi_aot.upload(weight_map_sum_full_res)
            _base_window_gpu = taichi_aot.hanning(
                (tile_h, tile_w), exclude_boundary=False
            )
            _rows_gpu = taichi_aot.upload(row_starts)
            _rows_gpu.dtype = np.int32
            _cols_gpu = taichi_aot.upload(col_starts)
            _cols_gpu.dtype = np.int32
            _weight_work_gpu = engine.allocate(
                (work_res_h, work_res_w), dtype=np.float32, host_accessible=True
            )

            try:
                batch_size = int(os.environ.get("SPATIAL_BATCH_SIZE", "2"))
            except (TypeError, ValueError):
                batch_size = 2
            batch_size = max(1, min(batch_size, 8))
            try:
                cleanup_interval = max(
                    1,
                    int(os.environ.get("SPATIAL_VRAM_CHECK_INTERVAL", "4")),
                )
            except (TypeError, ValueError):
                cleanup_interval = 4

            def cleanup_idle_vram(reason):
                try:
                    if hasattr(taichi_aot.engine, "sync"):
                        taichi_aot.engine.sync()
                    memory = taichi_aot.get_memory_status(force=True)
                    if (
                        memory.get("pressure") in ("high", "critical")
                        and hasattr(engine, "buffer_pool")
                        and engine.buffer_pool
                    ):
                        engine.buffer_pool.clear()
                except Exception as exc:
                    print(f"[SpatialFusion] VRAM cleanup skipped ({reason}): {exc}")
                gc.collect()

            try:
                for start_idx in range(0, num_images, batch_size):
                    if stop_requested and stop_requested():
                        break

                    end_idx = min(start_idx + batch_size, num_images)

                    # Load batch
                    chunk_images = []
                    if (
                        data_source is not None
                        and isinstance(data_source, str)
                        and data_source.endswith(".h5")
                    ):
                        import h5py

                        with h5py.File(data_source, "r") as h5f:
                            for idx in range(start_idx, end_idx):
                                chunk_images.append(h5f[f"image_{idx}"][:])
                    else:
                        source = (
                            images
                            if images is not None and isinstance(images, list)
                            else data_source
                        )
                        if isinstance(source, list):
                            chunk_images = source[start_idx:end_idx]
                        else:
                            print(
                                f"[SpatialFusion] Cannot load images from source: {type(source)}"
                            )
                            break

                    for chunk_i, img_orig in enumerate(chunk_images):
                        i = start_idx + chunk_i
                        if stop_requested and stop_requested():
                            break

                        if img_orig is None:
                            continue

                        # Preprocess frame on GPU
                        curr_full_gpu, curr_work_gray_gpu = (
                            taichi_bridge.prepare_frame_aot(
                                img_orig,
                                ref_dtype,
                                is_linear_mode,
                                proxy_scale,
                                work_res_h,
                                work_res_w,
                                ref_h,
                                ref_w,
                            )
                        )

                        # Compute spatial weights (ghost rejection)
                        generate_spatial_weights_taichi(
                            current_image=curr_work_gray_gpu,
                            reference_image=ref_work_res_pass2_gpu,
                            weight_map_sum=_weight_work_gpu,
                            base_window=_base_window_gpu,
                            stability_map=None,
                            row_starts=_rows_gpu,
                            col_starts=_cols_gpu,
                            tile_h=tile_h,
                            tile_w=tile_w,
                            noise_sigma=ref_noise_sigma,
                            motion_sensitivity=self.motion_sensitivity,
                            noise_offset_factor=self.noise_offset_factor,
                            equalize_brightness=self.equalize_brightness,
                            buffer_provider="pool",
                            search_radius=kwargs.get("similarity_search_radius", 3),
                            early_exit_threshold=self.early_exit_threshold,
                            scratch_cache=spatial_scratch,
                        )

                        # Cleanup work-res gray buffer
                        curr_work_gray_gpu.destroy()

                        # Accumulate weighted frame
                        accumulate_spatial_merging_taichi(
                            current_image_full=curr_full_gpu.view_as_vector(False),
                            weight_map_work=_weight_work_gpu,
                            final_image_sum=_sum_gpu.view_as_vector(False),
                            weight_map_sum_full=_weight_sum_full_gpu,
                            row_starts=_rows_gpu,
                            col_starts=_cols_gpu,
                            tile_h=tile_h,
                            tile_w=tile_w,
                            h_full=ref_h,
                            w_full=ref_w,
                            h_work=work_res_h,
                            w_work=work_res_w,
                        )

                        curr_full_gpu.destroy()
                        processed_count += 1

                        if update_progress:
                            prog = int(10 + (i + 1) / num_images * 85)
                            msg = f"Spatial Fusion: {i+1}/{num_images} (GPU AOT)"
                            update_progress(prog, msg)

                    # Free chunk.  Memory-pressure polling and Python GC are
                    # intentionally amortized; polling every tiny batch adds
                    # host-side overhead and does not improve GPU dispatch.
                    del chunk_images
                    batch_number = (start_idx // batch_size) + 1
                    if batch_number % cleanup_interval == 0 or end_idx >= num_images:
                        cleanup_idle_vram(f"chunk {start_idx}-{end_idx}")

                # Finalize: mean division
                if processed_count > 0:
                    if update_progress:
                        update_progress(95, "Finalizing with mean calculation...")

                    _ref_full_gpu = taichi_aot.upload(reference_image_float)
                    _final_image_gpu = engine.allocate(
                        _sum_gpu.shape,
                        dtype=_sum_gpu.dtype,
                        is_vector=getattr(_sum_gpu, "is_vector", False),
                        vector_dim=getattr(_sum_gpu, "vector_dim", 1),
                        host_accessible=True,
                    )
                    taichi_aot.mean_division(
                        sum_img=_sum_gpu,
                        sum_weight=_weight_sum_full_gpu,
                        ref_img=_ref_full_gpu,
                        dst=_final_image_gpu,
                    )
                    final_image_sum_full_res[:] = _final_image_gpu.to_numpy()
                    _ref_full_gpu.destroy()
                    _final_image_gpu.destroy()
                else:
                    final_image_sum_full_res[:] = _sum_gpu.to_numpy()

                weight_map_sum_full_res[:] = _weight_sum_full_gpu.to_numpy()

            finally:
                for buf in [
                    _sum_gpu,
                    _weight_sum_full_gpu,
                    _base_window_gpu,
                    _rows_gpu,
                    _cols_gpu,
                    _weight_work_gpu,
                ]:
                    if buf is not None:
                        try:
                            buf.destroy()
                        except:
                            pass
                cleanup_idle_vram("final")
                if os.environ.get("AOT_CLEAR_AFTER_OP", "0") == "1":
                    taichi_aot.unload_all_modules()
                    engine.buffer_pool.clear()

        finally:
            spatial_scratch.clear()
            if ref_work_res_pass2_gpu is not None:
                try:
                    ref_work_res_pass2_gpu.destroy()
                except:
                    pass

        print(f"[SpatialFusion] Done. Processed {processed_count}/{num_images} frames.")
        return (
            processed_count,
            final_image_sum_full_res,
            weight_map_sum_full_res,
            ref_noise_sigma,
        )

    @staticmethod
    def _compute_tile_starts(full_size, tile_size, overlap=0.3):
        """Compute tile start positions for a dimension."""
        if tile_size >= full_size:
            return np.array([0], dtype=np.int32)
        step = max(int(tile_size * (1.0 - overlap)), 1)
        starts = []
        y = 0
        while y + tile_size <= full_size:
            starts.append(y)
            if y + tile_size == full_size:
                break
            y = min(y + step, full_size - tile_size)
        return np.array(starts, dtype=np.int32)
