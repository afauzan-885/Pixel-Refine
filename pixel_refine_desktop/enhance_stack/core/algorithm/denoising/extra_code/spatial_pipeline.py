import numpy as np
import os
import cv2
import gc
import queue
import threading
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

    num_images = len(images)
    if num_images == 0:
        return (
            0,
            np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32),
            np.zeros((ref_image_h, ref_image_w), dtype=np.float32),
            0.0,
        )

    # 1. ALIGNMENT
    if enable_alignment and num_images > 1:
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
            index_offset=images_processed_so_far,
        )
        if not alignment_success and stop_requested and stop_requested():
            return 0, None, None, 0.0

    # 2. SETUP FOR MERGING
    ref_for_weight_calc = reference_image_float
    if is_linear_mode:
        ref_for_weight_calc = to_gamma_proxy(reference_image_float, scale=proxy_scale)

    # [MODIFIED] Menggunakan preprocess_in_python (CPU)
    ref_gray_preprocessed, ref_noise_sigma = preprocess_in_python(ref_for_weight_calc)

    # [MODIFIED] Menggunakan cv2.resize (OpenCV)
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
    def weight_map_producer(task_queue, result_queue, images_list_ref):
        local_curr_work_res = np.empty((work_res_h, work_res_w, 1), dtype=np.float32)
        weight_map_work_res = np.zeros(
            (work_res_h, work_res_w), dtype=np.float32, order="C"
        )
        while True:
            try:
                item = task_queue.get(timeout=0.1)
                if item is None:
                    break
                image_index = item
                image_orig = images_list_ref[image_index]
                if image_orig is None:
                    result_queue.put((image_index, None))
                    continue

                curr_float = normalize_image(image_orig, ref_dtype)
                if is_linear_mode:
                    curr_float = to_gamma_proxy(curr_float, scale=proxy_scale)

                # [MODIFIED] Menggunakan preprocess_in_python (CPU)
                curr_gray_preprocessed, _ = preprocess_in_python(curr_float)

                # [MODIFIED] Menggunakan cv2.resize (OpenCV)
                curr_work_gray = cv2.resize(
                    curr_gray_preprocessed,
                    (work_res_w, work_res_h),
                    interpolation=cv2.INTER_LINEAR,
                )
                local_curr_work_res[:, :, 0] = curr_work_gray
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
                result_queue.put(
                    (image_index, (weight_map_work_res * 65535.0).astype(np.uint16))
                )
            except Exception:
                result_queue.put((image_index, None))
                continue
            finally:
                task_queue.task_done()

    final_num_workers = (
        num_workers if num_workers > 0 else max(1, min((os.cpu_count() or 2) // 2, 8))
    )
    task_queue = queue.Queue()
    result_queue = queue.Queue(maxsize=final_num_workers * 2)
    threads = [
        threading.Thread(
            target=weight_map_producer, args=(task_queue, result_queue, images)
        )
        for _ in range(final_num_workers)
    ]
    for t in threads:
        t.start()
    for i in range(num_images):
        task_queue.put(i)
    for _ in range(final_num_workers):
        task_queue.put(None)

    finished_count = 0
    processed_frames = 0
    consumer_weight_full_buf = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)
    use_overall_progress = total_overall_images and total_overall_images > 0

    try:
        while finished_count < num_images:
            if stop_requested and stop_requested():
                break
            try:
                image_index, weight_map_uint16 = result_queue.get(timeout=0.1)
                if weight_map_uint16 is not None:
                    image_orig = images[image_index]
                    if image_orig is not None:
                        w_float = weight_map_uint16.astype(np.float32) * (1.0 / 65535.0)
                        cv2.resize(
                            w_float,
                            (ref_image_w, ref_image_h),
                            dst=consumer_weight_full_buf,
                            interpolation=cv2.INTER_LINEAR,
                        )
                        # [OPTIMIZATION] Pre-allocate norm_img_buf and use it
                        if "norm_img_buf" not in locals():
                            norm_img_buf = np.empty(
                                (ref_image_h, ref_image_w, ref_channels_buffer),
                                dtype=np.float32,
                            )

                        normalize_image(image_orig, ref_dtype, out=norm_img_buf)

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
                        images[image_index] = None
                        del image_orig, weight_map_uint16, w_float
                        if norm_img is not norm_img_buf:
                            del norm_img

                        processed_frames += 1

                        # [OPTIMIZATION] GC collect per frame to keep memory low
                        if processed_frames % 1 == 0:
                            gc.collect()
                finished_count += 1
                result_queue.task_done()
                if update_progress:
                    prog = int(
                        pass_merge_range[0]
                        + (finished_count / num_images)
                        * (pass_merge_range[1] - pass_merge_range[0])
                    )
                    msg = (
                        language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                            images_processed_so_far + finished_count,
                            total_overall_images,
                        )
                        if use_overall_progress
                        else f"Merging frames: {finished_count}/{num_images}"
                    )
                    update_progress(prog, msg)
            except queue.Empty:
                if not any(t.is_alive() for t in threads):
                    break

    finally:
        for t in threads:
            t.join(timeout=1.0)
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
    weight_method=0,
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
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.compute_spatial import (
        generate_spatial_weights_taichi,
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

    num_images = len(images)

    # 1. ALIGNMENT
    if enable_alignment and num_images > 1:
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
            index_offset=images_processed_so_far,
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

        use_overall_progress = total_overall_images and total_overall_images > 0

        try:
            for i, img_orig in enumerate(images):
                if stop_requested and stop_requested():
                    break
                if img_orig is None:
                    continue

                curr_full_gpu = preprocess.normalize_image_gpu(
                    img_orig, dtype=ref_dtype, buffer_provider="pool"
                )
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
                    motion_sensitivity=motion_sensitivity,
                    noise_offset_factor=noise_offset_factor,
                    equalize_brightness=False,
                    buffer_provider="pool",
                    weight_method=weight_method,
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
                if hasattr(img_orig, "to_numpy"):
                    release_taichi_ndarray(img_orig)

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
