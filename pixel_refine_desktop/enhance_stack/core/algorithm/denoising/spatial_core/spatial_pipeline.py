import numpy as np
import os
import cv2
import gc
import queue
import threading
import traceback
import time


_SPATIAL_CACHE = {
    "static_bufs": None,
    "_sum_gpu": None,
    "_weight_sum_full_gpu": None,
    "_base_window_gpu": None,
    "_rows_gpu": None,
    "_cols_gpu": None,
    "_weight_work_gpu": None,
    "ref_image_h": None,
    "ref_image_w": None,
    "ref_channels_buffer": None,
    "work_res_h": None,
    "work_res_w": None,
    "gpu_upload_threads": None,
}


def clear_spatial_cache():
    """Safely destroy all cached GPU buffers for spatial merging."""
    global _SPATIAL_CACHE
    print("[GPU Merging] Clearing persistent spatial merging cache...")
    if _SPATIAL_CACHE["static_bufs"] is not None:
        for buf in _SPATIAL_CACHE["static_bufs"]:
            try:
                buf.destroy()
            except:
                pass
    for key in [
        "_sum_gpu",
        "_weight_sum_full_gpu",
        "_base_window_gpu",
        "_rows_gpu",
        "_cols_gpu",
        "_weight_work_gpu",
    ]:
        buf = _SPATIAL_CACHE[key]
        if buf is not None:
            try:
                buf.destroy()
            except:
                pass
    for key in _SPATIAL_CACHE:
        _SPATIAL_CACHE[key] = None


def process_in_gpu(
    images,
    reference_image_float,
    ref_image_h,
    ref_image_w,
    ref_channels_buffer=3,
    ref_dtype=None,
    work_res_h=None,
    work_res_w=None,
    tile_h=16,
    tile_w=16,
    row_starts=None,
    col_starts=None,
    base_window=None,
    motion_sensitivity=None,
    noise_offset_factor=None,
    update_progress=None,
    stop_requested=None,
    pass_merge_range=None,
    p_align_start=30,
    p_align_end=40,
    p_merge_start=40,
    is_linear_mode=False,
    proxy_scale=1.0,
    images_processed_so_far=0,
    total_overall_images=None,
    lib_path=None,
    alignment_tile_size=None,
    alignment_variant: str = "block_flow",
    **kwargs,
):
    """Pipeline GPU Alignment + Merging (Full GPU Path).

    Alignment: Selalu GPU Taichi.
    Merging:   Selalu Taichi (full GPU).

    alignment_variant:
        'block_flow'        — HDR+ optical-flow tile matching (default)
        'block_correlation' — Hierarchical Phase Correlation
    """
    from taichi_vision import taichi_aot
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
        taichi_bridge,
    )
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    data_source = kwargs.get("data_source")
    if not images and data_source:
        import h5py

        with h5py.File(data_source, "r") as f:
            num_images = sum(1 for k in f.keys() if k.startswith("image_"))
    else:
        num_images = len(images)

    if num_images == 0:
        return (
            0,
            np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32),
            np.zeros((ref_image_h, ref_image_w), dtype=np.float32),
            0.0,
        )

    # 1. ALIGNMENT (GPU Taichi)
    enable_alignment = kwargs.get("enable_alignment", True)
    if enable_alignment and num_images > 1:
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
            perform_alignment_gpu,
        )

        # Penentuan format return alignment (Selalu ti_ndarray untuk GPU merging)
        align_return_format = "ti_ndarray"

        # Samakan input reference untuk alignment (identik dengan CPU mode)
        ref_align_input = reference_image_float
        if is_linear_mode:
            # Gunakan proxy untuk alignment
            ref_align_gpu, _ = taichi_bridge.prepare_reference_aot(
                reference_image_float, True, proxy_scale, work_res_h, work_res_w
            )
            ref_align_input = ref_align_gpu.to_numpy()

        # Resolve flow_backend / optical_flow_type
        # If alignment_variant is "block_align" or optical_flow_type is "block_align", use it.
        # Otherwise default to optical_flow_type parameter.
        flow_backend = kwargs.get(
            "optical_flow_type", kwargs.get("flow_backend", "alignment_tile")
        )
        flow_backend = str(flow_backend or "alignment_tile").strip().lower()
        if alignment_variant == "block_align":
            flow_backend = "block_align"

        if flow_backend in ("none", "off", "disabled", "no_alignment"):
            success = True
            print("[GPU Alignment] Alignment bypassed by backend setting.")
        else:
            # Pop keys from kwargs to prevent multiple values for keyword argument error
            align_kwargs = dict(kwargs)
            align_kwargs.pop("optical_flow_type", None)
            align_kwargs.pop("flow_backend", None)

            success = perform_alignment_gpu(
                images,
                ref_align_input,
                work_res_h,
                work_res_w,
                alignment_tile_size if alignment_tile_size is not None else tile_h,
                alignment_tile_size if alignment_tile_size is not None else tile_w,
                ref_dtype,
                update_progress,
                stop_requested,
                progress_start=p_align_start,
                progress_end=p_align_end,
                is_linear_mode=is_linear_mode,
                proxy_scale=proxy_scale,
                index_offset=images_processed_so_far,
                return_format=align_return_format,
                optical_flow_type=flow_backend,
                **align_kwargs,
            )
        if kwargs.get("alignment_only", False):
            return success
        if not success:
            print("Warning: GPU alignment failed partially.")
        if stop_requested and stop_requested():
            return 0, None, None, 0.0

    # 2. TAICHI MERGING (Full GPU Path)
    print(f"[AOT Merging] Processing {num_images} images with Taichi AOT backend...")
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        estimate_noise_in_python,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
        get_taichi_worker,
    )
    from taichi_vision.taichi_algorithm.taichi_worker import (
        create_taichi_ndarray,
        release_taichi_ndarray,
        download_taichi_ndarray,
        clear_vram,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
        generate_spatial_weights_taichi,
        accumulate_spatial_merging_taichi,
        SpatialScratchCache,
    )
    from taichi_vision.taichi_algorithm.interpolation.bilinear_interpolation import (
        bilinear_resize,
    )

    # Preprocessing Gambar Referensi (Unified API)
    ref_for_weight_calc = reference_image_float
    ref_work_res_pass2_gpu, ref_noise_sigma = taichi_bridge.prepare_reference_aot(
        ref_for_weight_calc, is_linear_mode, proxy_scale, work_res_h, work_res_w
    )

    final_image_sum_full_res = np.zeros(
        (ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32
    )
    weight_map_sum_full_res = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)
    processed_frames_spatial = [0]
    # Reuse per-frame spatial analysis buffers for the lifetime of this batch.
    # The loop is sequential and each dispatch completes before the next frame,
    # so slots are safe to overwrite without changing algorithm ordering.
    spatial_scratch = SpatialScratchCache()

    def _run_gpu_merging_loop():
        engine = taichi_aot.engine

        _sum_gpu = taichi_aot.upload(final_image_sum_full_res)
        _weight_sum_full_gpu = taichi_aot.upload(weight_map_sum_full_res)
        # ``phase2_fine_analysis`` keeps ``base_window`` in its graph ABI for
        # compatibility, but the maintained kernel computes the window from
        # ``tile_h/tile_w`` and never reads that argument.  Do not allocate a
        # full device-side Hanning buffer here: at 12 MP this otherwise adds a
        # resident allocation that contributes no result and is destroyed only
        # after the complete batch.
        _base_window_gpu = None

        _rows_gpu = taichi_aot.upload(row_starts)
        _rows_gpu.dtype = np.int32

        _cols_gpu = taichi_aot.upload(col_starts)
        _cols_gpu.dtype = np.int32

        _weight_work_gpu = engine.allocate(
            (work_res_h, work_res_w), dtype=np.float32, host_accessible=True
        )

        batch_size = 4
        use_overall_progress = total_overall_images and total_overall_images > 0

        def _load_chunk(start, end):
            chunk = []
            if data_source is not None:
                import h5py

                with h5py.File(data_source, "r") as h5f:
                    for idx in range(start, end):
                        chunk.append(h5f[f"image_{idx}"][:])
            else:
                chunk = images[start:end]
            return chunk

        from concurrent.futures import ThreadPoolExecutor

        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future_chunk = executor.submit(
                    _load_chunk, 0, min(batch_size, num_images)
                )

                for start_idx in range(0, num_images, batch_size):
                    if stop_requested and stop_requested():
                        break

                    chunk_images = future_chunk.result()
                    end_idx = min(start_idx + batch_size, num_images)

                    next_start = start_idx + batch_size
                    if next_start < num_images:
                        next_end = min(next_start + batch_size, num_images)
                        future_chunk = executor.submit(
                            _load_chunk, next_start, next_end
                        )
                    else:
                        future_chunk = None

                    for chunk_i, img_orig in enumerate(chunk_images):
                        i = start_idx + chunk_i
                        if stop_requested and stop_requested():
                            break

                        if img_orig is None:
                            continue

                        # Preprocessing Frame (Unified API - Classic Way)
                        curr_full_gpu, curr_work_gray_gpu = (
                            taichi_bridge.prepare_frame_aot(
                                img_orig,
                                ref_dtype,
                                is_linear_mode,
                                proxy_scale,
                                work_res_h,
                                work_res_w,
                                ref_image_h,
                                ref_image_w,
                            )
                        )

                        generate_spatial_weights_taichi(
                            current_image=curr_work_gray_gpu,
                            reference_image=ref_work_res_pass2_gpu,
                            weight_map_sum=_weight_work_gpu,
                            # Retained as a public-wrapper argument; the AOT
                            # graph receives the compatibility scalar 0.
                            base_window=None,
                            stability_map=None,
                            row_starts=_rows_gpu,
                            col_starts=_cols_gpu,
                            tile_h=tile_h,
                            tile_w=tile_w,
                            noise_sigma=ref_noise_sigma,
                            motion_sensitivity=motion_sensitivity,
                            noise_offset_factor=noise_offset_factor,
                            equalize_brightness=False,
                            buffer_provider="pool",
                            scratch_cache=spatial_scratch,
                            search_radius=kwargs.get("similarity_search_radius", 3),
                            early_exit_threshold=kwargs.get(
                                "early_exit_threshold", 0.05
                            ),
                        )

                        curr_work_gray_gpu.destroy()

                        accumulate_spatial_merging_taichi(
                            current_image_full=curr_full_gpu.view_as_vector(False),
                            weight_map_work=_weight_work_gpu,
                            final_image_sum=_sum_gpu.view_as_vector(False),
                            weight_map_sum_full=_weight_sum_full_gpu,
                            row_starts=_rows_gpu,
                            col_starts=_cols_gpu,
                            tile_h=tile_h,
                            tile_w=tile_w,
                            h_full=ref_image_h,
                            w_full=ref_image_w,
                            h_work=work_res_h,
                            w_work=work_res_w,
                        )

                        curr_full_gpu.destroy()
                        processed_frames_spatial[0] += 1

                        if update_progress:
                            prog = int(
                                pass_merge_range[0]
                                + ((i + 1) / num_images)
                                * (pass_merge_range[1] - pass_merge_range[0])
                            )
                            msg = (
                                language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                                    images_processed_so_far + i + 1,
                                    total_overall_images,
                                )
                                if use_overall_progress
                                else f"Spatial Merging: {i+1}/{num_images} (GPU Taichi)"
                            )
                            update_progress(prog, msg)
                        # Progress callbacks are already dispatched through the
                        # UI-safe channel.  A fixed 10 ms sleep per frame made
                        # the native path pay an artificial latency tax and
                        # did not provide synchronization; the next native
                        # dispatch performs its own required ordering.
                        time.sleep(0)

                    # Free chunk RAM instantly
                    del chunk_images
                    if not data_source:
                        for idx in range(start_idx, end_idx):
                            images[idx] = None
                    import gc

                    gc.collect()

            return_raw = kwargs.get("return_raw", False)
            if not return_raw and processed_frames_spatial[0] > 0:
                if update_progress:
                    update_progress(
                        pass_merge_range[1],
                        "Finalizing with simple mean calculation on GPU...",
                    )
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
                # Read directly into the caller-owned output array.  The
                # previous form allocated a second full-resolution host
                # tensor and copied it into ``final_image_sum_full_res``;
                # avoiding that transient matters for large RAW frames.
                _final_image_gpu.to_numpy(out=final_image_sum_full_res)
                _ref_full_gpu.destroy()
                _final_image_gpu.destroy()
            else:
                _sum_gpu.to_numpy(out=final_image_sum_full_res)

            _weight_sum_full_gpu.to_numpy(out=weight_map_sum_full_res)
            return True
        except Exception:
            import traceback

            traceback.print_exc()
            return False
        finally:
            for buf in [
                _sum_gpu,
                _weight_sum_full_gpu,
                _base_window_gpu,
                _rows_gpu,
                _cols_gpu,
                _weight_work_gpu,
            ]:
                if buf:
                    try:
                        buf.destroy()
                    except:
                        pass
            if os.environ.get("AOT_CLEAR_AFTER_OP", "0") == "1":
                taichi_aot.unload_all_modules()
                engine.buffer_pool.clear()
            spatial_scratch.clear()

    try:
        is_aot = os.environ.get("AOT_MODE", "1") == "1"
        if is_aot:
            _run_gpu_merging_loop()
        else:
            worker = get_taichi_worker()
            worker.submit_and_wait(_run_gpu_merging_loop)
    finally:
        if ref_work_res_pass2_gpu:
            try:
                ref_work_res_pass2_gpu.destroy()
            except:
                pass
    return (
        processed_frames_spatial[0],
        final_image_sum_full_res,
        weight_map_sum_full_res,
        ref_noise_sigma,
    )
