import numpy as np
import os
import cv2
import gc
import traceback
import time


def process_in_cpu(
    images,
    reference_image_float,
    ref_image_h,
    ref_image_w,
    ref_channels_buffer,
    ref_dtype,
    work_res_h,
    work_res_w,
    tile_h,
    tile_w,
    row_starts,
    col_starts,
    base_window,
    motion_sensitivity,
    noise_offset_factor,
    num_workers,
    update_progress,
    stop_requested,
    pass_merge_range,
    p_align_start,
    p_align_end,
    p_merge_start,
    is_linear_mode,
    proxy_scale,
    images_processed_so_far,
    total_overall_images,
    lib_path,
    enable_alignment=True,
    **kwargs,
):
    """Pipeline terpadu untuk Alignment + Merging di CPU."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.extra_algorithm import (
        perform_image_alignment,
        SimilaritySpatialInterface,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        estimate_noise_in_python,
        normalize_image,
        to_gamma_proxy,
        preprocess_in_python,
    )
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    from pixel_refine_desktop.enhance_stack.core.logic.image_streamer import (
        ImageStreamer,
    )

    is_streamer = isinstance(images, ImageStreamer)
    num_images = images.total_images if is_streamer else len(images)

    if num_images == 0:
        return (
            0,
            np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32),
            np.zeros((ref_image_h, ref_image_w), dtype=np.float32),
            0.0,
        )

    # 1. ALIGNMENT
    if enable_alignment and not is_streamer and num_images > 1:
        if update_progress:
            update_progress(p_align_start, "Memulai proses alignment (CPU)...")

        align_ref_input = reference_image_float
        if is_linear_mode:
            align_ref_input = to_gamma_proxy(reference_image_float, scale=proxy_scale)

        alignment_success = perform_image_alignment(
            images,
            align_ref_input,
            work_res_h,
            work_res_w,
            tile_h,
            tile_w,
            ref_dtype,
            update_progress,
            stop_requested,
            optical_flow_type=kwargs.get("optical_flow_type", "alignment_tile"),
            num_alignment_workers=num_workers,
            progress_start=p_align_start,
            progress_end=p_align_end,
            is_linear_mode=is_linear_mode,
            proxy_scale=proxy_scale,
        )
        if not alignment_success and stop_requested and stop_requested():
            return 0, None, None, 0.0

    # 2. SETUP FOR MERGING
    ref_for_weight_calc = reference_image_float
    if is_linear_mode:
        ref_for_weight_calc = to_gamma_proxy(reference_image_float, scale=proxy_scale)

    ref_gray_preprocessed, ref_noise_sigma = preprocess_in_python(ref_for_weight_calc)
    ref_work_res_pass2 = cv2.resize(
        ref_gray_preprocessed, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR
    )

    final_image_sum_full_res = np.zeros(
        (ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32
    )
    weight_map_sum_full_res = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)

    try:
        c_interface = SimilaritySpatialInterface(lib_path)
    except Exception as e:
        raise RuntimeError(f"Gagal memuat C++ interface: {e}")

    # 3. MERGING LOOP (CPU)
    # [REFACTOR] Menghapus sistem Antrean (Queue) dan Thread internal yang redundan
    # karena ImageStreamer sudah memiliki ThreadPool internal untuk membaca gambar.
    # Kita proses secara linear untuk menghindari overhead context switching.

    local_curr_work_res = np.empty((work_res_h, work_res_w, 1), dtype=np.float32)
    weight_map_work_res = np.zeros(
        (work_res_h, work_res_w), dtype=np.float32, order="C"
    )
    consumer_weight_full_buf = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)

    is_alignment_enabled_for_stream = (
        enable_alignment and is_streamer and num_images > 1
    )
    align_ref_input = reference_image_float
    if is_linear_mode and is_alignment_enabled_for_stream:
        align_ref_input = to_gamma_proxy(reference_image_float, scale=proxy_scale)

    processed_frames = 0
    use_overall_progress = total_overall_images and total_overall_images > 0

    # Iterator tunggal yang seragam
    image_iterator = images.stream() if is_streamer else enumerate(images)

    # [OPTIMIZATION] Pre-allocate heavy buffers to avoid 2.2GB fragmented peak overhead
    norm_img_buf = np.empty(
        (ref_image_h, ref_image_w, ref_channels_buffer),
        dtype=np.float32,
    )
    # Buffers that might be populated later
    curr_float_buf = None
    curr_gray_preprocessed_buf = None

    for i, img_orig in image_iterator:
        if stop_requested and stop_requested():
            break
        if img_orig is None:
            continue

        print(
            f"[Streaming Log] Memproses dan mengambil frame ke-{i+1}/{num_images} dari ImageStreamer (CPU)"
        )

        # [NEW] Perform On-the-fly CPU Alignment before Merging
        current_process_image = img_orig
        if is_alignment_enabled_for_stream and i > 0:
            try:
                temp_list = [align_ref_input, img_orig]
                alignment_success = perform_image_alignment(
                    temp_list,
                    align_ref_input,
                    work_res_h,
                    work_res_w,
                    tile_h,
                    tile_w,
                    ref_dtype,
                    update_progress=None,  # Disable internal progress to avoid spam
                    stop_requested=stop_requested,
                    optical_flow_type=kwargs.get("optical_flow_type", "alignment_tile"),
                    num_alignment_workers=1,  # Synchronous alignment
                    progress_start=0,
                    progress_end=100,
                    is_linear_mode=is_linear_mode,
                    proxy_scale=proxy_scale,
                )
                if alignment_success and temp_list[1] is not img_orig:
                    current_process_image = temp_list[1]
                else:
                    print(f"[Warning] Streaming CPU alignment failed for frame {i}")
            except Exception as e:
                print(f"Error during on-the-fly CPU alignment for frame {i}: {e}")

        # 1. Hitung Weight Map Cache
        if (
            curr_float_buf is None
            or curr_float_buf.shape != current_process_image.shape
        ):
            curr_float_buf = np.empty(current_process_image.shape, dtype=np.float32)

        normalize_image(current_process_image, ref_dtype, out=curr_float_buf)
        if is_linear_mode:
            # Inline/in-place proxy calculation is harder, we tolerate 1 copy here
            curr_float = to_gamma_proxy(curr_float_buf, scale=proxy_scale)
        else:
            curr_float = curr_float_buf

        curr_gray_preprocessed, _ = preprocess_in_python(curr_float)

        cv2.resize(
            curr_gray_preprocessed,
            (work_res_w, work_res_h),
            dst=local_curr_work_res[:, :, 0],
            interpolation=cv2.INTER_LINEAR,
        )
        weight_map_work_res.fill(0)

        c_interface.call_generate_weight_map_jit(
            weight_map_sum=weight_map_work_res,
            current_image=local_curr_work_res,
            reference_image_processed=ref_work_res_pass2,
            base_window=base_window,
            stability_map=None,
            row_starts=row_starts,
            col_starts=col_starts,
            tile_h=tile_h,
            tile_w=tile_w,
            h=work_res_h,
            w=work_res_w,
            channels=1,
            motion_sensitivity=motion_sensitivity,
            noise_offset_factor=noise_offset_factor,
            precomputed_ref_noise_sigma=ref_noise_sigma,
        )
        np.clip(weight_map_work_res, 0.0, 1.0, out=weight_map_work_res)

        # 2. Akumulasi ke buffer penuh
        cv2.resize(
            weight_map_work_res,
            (ref_image_w, ref_image_h),
            dst=consumer_weight_full_buf,
            interpolation=cv2.INTER_LINEAR,
        )

        normalize_image(current_process_image, ref_dtype, out=norm_img_buf)

        if norm_img_buf.shape[:2] != (ref_image_h, ref_image_w):
            norm_img = cv2.resize(
                norm_img_buf,
                (ref_image_w, ref_image_h),
                interpolation=cv2.INTER_AREA,
            )
        else:
            norm_img = norm_img_buf

        final_image_sum_full_res += (
            norm_img * consumer_weight_full_buf[:, :, np.newaxis]
        )
        weight_map_sum_full_res += consumer_weight_full_buf

        # [OPTIMIZATION] Explicit deletion and cleaning
        if not is_streamer:
            images[i] = None
        if norm_img is not norm_img_buf:
            del norm_img

        # [RAM KILLER] Menyapu bersih referensi array Python yang tidak di-cache
        del current_process_image
        if curr_float is not curr_float_buf:
            del curr_float
        if curr_gray_preprocessed is not curr_gray_preprocessed_buf:
            del curr_gray_preprocessed
        if img_orig is not None:
            del img_orig

        # Paksa Python melepaskan memori yang *dangling*
        import gc

        gc.collect()

        processed_frames += 1

        # 3. Update Progress
        if update_progress:
            prog = int(
                pass_merge_range[0]
                + (processed_frames / num_images)
                * (pass_merge_range[1] - pass_merge_range[0])
            )
            msg = (
                language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                    images_processed_so_far + processed_frames,
                    total_overall_images,
                )
                if use_overall_progress
                else f"Merging frames: {processed_frames}/{num_images}"
            )
            update_progress(prog, msg)

    gc.collect()

    return (
        processed_frames,
        final_image_sum_full_res,
        weight_map_sum_full_res,
        ref_noise_sigma,
    )


def process_in_gpu(
    images,
    reference_image_float,
    ref_image_h,
    ref_image_w,
    ref_channels_buffer,
    ref_dtype,
    work_res_h,
    work_res_w,
    tile_h,
    tile_w,
    row_starts,
    col_starts,
    base_window,
    motion_sensitivity,
    noise_offset_factor,
    update_progress,
    stop_requested,
    pass_merge_range,
    p_align_start,
    p_align_end,
    p_merge_start,
    is_linear_mode,
    proxy_scale,
    images_processed_so_far,
    total_overall_images,
    enable_alignment=True,
    alignment_tile_size=None,
    **kwargs,
):
    """Pipeline terpadu untuk Alignment + Merging di GPU."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import (
        preprocess,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.extra_algorithm import (
        perform_alignment_gpu,
        get_taichi_worker,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
        create_taichi_ndarray,
        release_taichi_ndarray,
        download_taichi_ndarray,
        clear_vram,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.compute_similarity import (
        generate_weight_map_taichi,
        accumulate_spatial_merging_taichi,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.bilinear_interpolation import (
        bilinear_resize,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        estimate_noise_in_python,
        to_gamma_proxy,
    )
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    from pixel_refine_desktop.enhance_stack.core.logic.image_streamer import (
        ImageStreamer,
    )

    is_streamer = isinstance(images, ImageStreamer)
    num_images = images.total_images if is_streamer else len(images)

    # 1. ALIGNMENT
    if enable_alignment and not is_streamer and num_images > 1:
        perform_alignment_gpu(
            images,
            reference_image_float,
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
            **kwargs,
        )
        if stop_requested and stop_requested():
            return 0, None, None, 0.0

    # 2. SETUP FOR MERGING
    ref_for_weight_calc = reference_image_float
    if is_linear_mode:
        ref_for_weight_calc = to_gamma_proxy(reference_image_float, scale=proxy_scale)

    ref_gray_preprocessed_gpu = preprocess.preprocess_in_python_gpu(
        ref_for_weight_calc, use_sharpen=False
    )
    ref_noise_sigma = estimate_noise_in_python(ref_gray_preprocessed_gpu.to_numpy())
    ref_work_res_pass2_gpu = bilinear_resize(
        ref_gray_preprocessed_gpu, work_res_h, work_res_w
    )

    final_image_sum_full_res = np.zeros(
        (ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32
    )
    weight_map_sum_full_res = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)
    processed_frames_spatial = [0]

    def _run_gpu_merging_loop():
        _sum_gpu = create_taichi_ndarray(final_image_sum_full_res)
        _weight_sum_full_gpu = create_taichi_ndarray(weight_map_sum_full_res)
        _base_window_gpu = create_taichi_ndarray(base_window)
        _rows_gpu = create_taichi_ndarray(row_starts)
        _cols_gpu = create_taichi_ndarray(col_starts)
        _weight_work_gpu = create_taichi_ndarray(
            np.zeros((work_res_h, work_res_w), dtype=np.float32)
        )
        import traceback

        use_overall_progress = total_overall_images and total_overall_images > 0

        # [NEW] Setup reference for on-the-fly alignment if enabled
        is_alignment_enabled_for_stream = (
            enable_alignment and is_streamer and num_images > 1
        )
        n_layers = 1
        search_dist = kwargs.get("search_dist", 2.0)
        use_sharpen = kwargs.get("use_sharpen", False)

        if is_alignment_enabled_for_stream:
            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.alignment_tile_taichi import (
                    set_reference_hybrid_taichi,
                    compute_alignment_and_warp_hybrid_taichi,
                )

                min_layer_res = min(tile_h, tile_w) * 2
                log_arg = (
                    min(work_res_h, work_res_w) / min_layer_res
                    if min_layer_res > 0
                    else 1
                )
                n_layers = min(
                    3, max(1, int(np.ceil(np.log2(log_arg))) if log_arg > 0 else 1)
                )

                set_reference_hybrid_taichi(
                    reference_image_float,
                    work_h=work_res_h,
                    work_w=work_res_w,
                    is_linear=is_linear_mode,
                    proxy_scale=proxy_scale,
                    use_sharpen=use_sharpen,
                )
            except Exception as e:
                print(f"[GPU Streaming Alignment] Failed to initialize reference: {e}")
                is_alignment_enabled_for_stream = False

        try:
            image_iterator = images.stream() if is_streamer else enumerate(images)
            for i, img_orig in image_iterator:
                if stop_requested and stop_requested():
                    break
                if img_orig is None:
                    continue

                print(
                    f"[Streaming Log] Memproses dan mengambil frame ke-{i+1}/{num_images} dari ImageStreamer (GPU)"
                )

                # [NEW] Perform On-the-fly Alignment before Merging
                current_process_image = img_orig
                if is_alignment_enabled_for_stream and i > 0:
                    try:
                        warped_image = compute_alignment_and_warp_hybrid_taichi(
                            img_orig,
                            tile_h,
                            tile_w,
                            n_layers,
                            None,  # ALIGN_LIB not needed for GPU
                            is_linear=is_linear_mode,
                            proxy_scale=proxy_scale,
                            use_sharpen=use_sharpen,
                            search_dist=search_dist,
                        )
                        if warped_image is not None:
                            current_process_image = warped_image

                            # [DEBUG] Simpan gambar hasil warp agar kita bisa mengecek apakah alignment berjalan dengan benar
                            try:
                                from pixel_refine_desktop.ui.views.manager.GenericUILibrary import (
                                    GenericUILibrary,
                                )

                                batch_params = GenericUILibrary.get_data(
                                    "batch_parameter"
                                )

                                save_align_check = False
                                if batch_params:
                                    algo_params = (
                                        batch_params.get("batch_data", {})
                                        .get("algorithm_parameters", {})
                                        .get("Alignment Parameters", {})
                                    )
                                    save_align_check = algo_params.get(
                                        "save_align_image", False
                                    )

                                if save_align_check:
                                    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Similarity import (
                                        save_aligned_image,
                                    )

                                    save_aligned_image(
                                        current_process_image, i, "GPU_STREAM"
                                    )
                            except Exception as inner_e:
                                print(f"Error checking/saving aligned image: {inner_e}")

                        else:
                            print(
                                f"[Warning] Streaming GPU alignment failed for frame {i}"
                            )
                    except Exception as e:
                        print(
                            f"Error during on-the-fly GPU alignment for frame {i}: {e}"
                        )
                        traceback.print_exc()

                # If current_process_image is a Taichi ndarray (e.g. from compute_alignment_and_warp_hybrid_taichi)
                # We either need to download it or pass it safely. Since normalize_image_gpu expects a numpy array
                # or handles it internally, we'll ensure it's safely converted to numpy first for consistency.
                if hasattr(current_process_image, "to_numpy"):
                    import taichi as ti

                    if isinstance(current_process_image, ti.ndarray):
                        current_process_image = current_process_image.to_numpy()

                curr_full_gpu = preprocess.normalize_image_gpu(
                    current_process_image, dtype=ref_dtype, buffer_provider="pool"
                )

                # Cek dimensi (Taichi menggunakan (n, m, c) atau numpy (h, w, c))
                if curr_full_gpu.shape[:2] != (ref_image_h, ref_image_w):
                    new_full = bilinear_resize(curr_full_gpu, ref_image_h, ref_image_w)
                    release_taichi_ndarray(curr_full_gpu)
                    curr_full_gpu = new_full

                curr_work_gray_gpu = preprocess.preprocess_pipeline_gpu(
                    curr_full_gpu,
                    normalize=False,
                    apply_gamma=is_linear_mode,
                    extract_green=True,
                    target_size=(work_res_h, work_res_w),
                    scale=proxy_scale,
                    buffer_provider="pool",
                )

                generate_weight_map_taichi(
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
                    motion_sensitivity=motion_sensitivity,
                    noise_offset_factor=noise_offset_factor,
                    equalize_brightness=False,
                    buffer_provider="pool",
                    search_radius=kwargs.get("similarity_search_radius", 3),
                )

                release_taichi_ndarray(curr_work_gray_gpu)
                accumulate_spatial_merging_taichi(
                    current_image_full=curr_full_gpu,
                    weight_map_work=_weight_work_gpu,
                    final_image_sum=_sum_gpu,
                    weight_map_sum_full=_weight_sum_full_gpu,
                    buffer_provider="pool",
                )
                release_taichi_ndarray(curr_full_gpu)

                # Cleanup reference for garbage collection
                if hasattr(img_orig, "to_numpy"):
                    release_taichi_ndarray(img_orig)

                if not is_streamer:
                    images[i] = None

                processed_frames_spatial[0] += 1

                if update_progress:
                    prog = int(
                        pass_merge_range[0]
                        + ((i + 1) / num_images)
                        * (pass_merge_range[1] - pass_merge_range[0])
                    )
                    msg = (
                        language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                            images_processed_so_far + i + 1, total_overall_images
                        )
                        if use_overall_progress
                        else f"Spatial Merging: {i+1}/{num_images} (GPU)"
                    )
                    update_progress(prog, msg)
                time.sleep(0.01)

            download_taichi_ndarray(_sum_gpu, out=final_image_sum_full_res)
            download_taichi_ndarray(_weight_sum_full_gpu, out=weight_map_sum_full_res)
            return True
        except Exception as e:
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
                    release_taichi_ndarray(buf)
            clear_vram()

    worker = get_taichi_worker()
    success = worker.submit_and_wait(_run_gpu_merging_loop)
    return (
        processed_frames_spatial[0],
        final_image_sum_full_res,
        weight_map_sum_full_res,
        ref_noise_sigma,
    )
