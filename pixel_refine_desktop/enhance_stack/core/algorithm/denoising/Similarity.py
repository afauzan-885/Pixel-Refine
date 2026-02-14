import os

print("!!! [DEBUG] Similarity.py Module Loading... !!!")

from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import queue
import threading
import functools
import traceback
import sys
import numpy as np
import cv2
import sqlite3
import sqlite3
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    estimate_noise_in_python,
    extract_all_metadata,
    gaussian_window,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    normalize_image,
    # preprocess_in_python,  # REMOVED - now using preprocess.preprocess_in_python_gpu
    resize_all_with_padding,
    save_image,
    setup_balanced_batching,
    to_gamma_proxy,
    calculate_auto_scale,
    calculate_scale_from_gt_proxy,  # [SMART PROXY]
    save_linear_dng,  # [LINEAR DNG]
    preprocess_in_python,
    # to_gamma_proxy, # Replaced/Updated
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.extra_algorithm import (
    SimilaritySpatialInterface,
    perform_image_alignment,
    perform_alignment_gpu,
    get_taichi_worker,
    process_in_cpu,
    process_in_gpu,
)


# --- TAICHI SPATIAL DETECTION ---
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
    TAICHI_AVAILABLE as TAICHI_SPATIAL_AVAILABLE,
)

print(f"[DEBUG] TAICHI_SPATIAL_AVAILABLE detected as: {TAICHI_SPATIAL_AVAILABLE}")

from pixel_refine_desktop.ui.resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
    load_similarity_config,
)


class SimilarityAlgorithm:
    def __init__(self, db_path, hdf5_path=None):
        self.db_path = db_path

        if hdf5_path is None:
            self.hdf5_path = "database/align/aligned_images.h5"
        else:
            self.hdf5_path = hdf5_path

        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths_for_batch_process(self, batch_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
            """,
                (batch_id,),
            )
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, "r") as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images

    def _apply_final_fusion_tiled(
        self, sum_img, sum_weight, ref_img, noise_sigma, tile_size=512, padding=16
    ):
        """
        Menjalankan _apply_precision_structure_fusion secara Tiled & Paralel.
        Menghemat RAM drastis dan mempercepat proses akhir.
        """
        h, w = sum_img.shape[:2]
        final_output = np.zeros_like(sum_img)

        # Daftar tugas tile
        tasks = []

        # Generate koordinat tile
        for y in range(0, h, tile_size):
            for x in range(0, w, tile_size):
                # Koordinat inti tile
                y_end = min(y + tile_size, h)
                x_end = min(x + tile_size, w)

                # Koordinat dengan padding (untuk konteks Gaussian Blur agar tidak ada garis di sambungan)
                y_start_pad = max(0, y - padding)
                x_start_pad = max(0, x - padding)
                y_end_pad = min(h, y_end + padding)
                x_end_pad = min(w, x_end + padding)

                # Hitung offset crop untuk mengembalikan ke ukuran asli setelah diproses
                crop_y1 = y - y_start_pad
                crop_y2 = crop_y1 + (y_end - y)
                crop_x1 = x - x_start_pad
                crop_x2 = crop_x1 + (x_end - x)

                tasks.append(
                    {
                        "coords": (y, y_end, x, x_end),
                        "pad_coords": (y_start_pad, y_end_pad, x_start_pad, x_end_pad),
                        "crop": (crop_y1, crop_y2, crop_x1, crop_x2),
                    }
                )

        # Fungsi Worker untuk ThreadPool
        def process_single_tile(task):
            py1, py2, px1, px2 = task["pad_coords"]

            # 1. Ambil Slice Data (Copy kecil, hemat RAM)
            s_img_slice = sum_img[py1:py2, px1:px2]
            s_w_slice = sum_weight[py1:py2, px1:px2]
            ref_slice = ref_img[py1:py2, px1:px2]

            # 2. Normalisasi Lokal (Divide)
            valid_mask = s_w_slice > 1e-6
            fused_slice = np.zeros_like(s_img_slice)
            np.divide(
                s_img_slice,
                s_w_slice[:, :, np.newaxis],
                out=fused_slice,
                where=valid_mask[:, :, np.newaxis],
            )

            # 3. Jalankan Algoritma Berat (Structure Fusion) pada slice kecil
            #    Ini memanggil fungsi _apply_precision_structure_fusion yang sudah Anda miliki
            processed_pad = self._apply_precision_structure_fusion(
                fused_img=fused_slice,
                weight_map=s_w_slice,
                reference_img=ref_slice,
                base_noise_sigma=noise_sigma,
            )

            # 4. Potong Padding (Ambil bagian tengah yang valid saja)
            cy1, cy2, cx1, cx2 = task["crop"]
            result_core = processed_pad[cy1:cy2, cx1:cx2]

            return task["coords"], result_core

        # Eksekusi Paralel
        # Gunakan max_workers sesuai core CPU, tapi jangan terlalu banyak agar tidak overhead
        max_threads = max(2, (os.cpu_count() or 4) - 1)

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(process_single_tile, t) for t in tasks]

            for future in as_completed(futures):
                try:
                    (ty, ty2, tx, tx2), result_tile = future.result()
                    final_output[ty:ty2, tx:tx2] = result_tile
                except Exception as e:
                    print(f"Error processing tile: {e}")
                    # Fallback ke black atau original sum jika error (jarang terjadi)

        return final_output

    def _apply_precision_structure_fusion(
        self, fused_img, weight_map, reference_img, base_noise_sigma
    ):
        """
        Versi PENYEMPURNAAN: Smart Structure Fusion dengan 'Consistency Check'.

        Peta bobot hanya menjadi 'Saran', keputusan final diambil berdasarkan
        analisis kemiripan struktur antara Fused vs Reference.
        """
        # 1. Konversi Tipe Data
        fused = fused_img.astype(np.float32)
        ref = reference_img.astype(np.float32)

        if ref.shape[:2] != fused.shape[:2]:
            ref = cv2.resize(
                ref, (fused.shape[1], fused.shape[0]), interpolation=cv2.INTER_AREA
            )

        # =====================================================================
        # A. ANALISIS FREKUENSI (Tetap Menggunakan Parameter Favorit Anda)
        # =====================================================================
        k_radius = 3
        k_sigma = 0.5

        # Blur Reference & Fused
        mu_ref = cv2.GaussianBlur(ref, (k_radius, k_radius), k_sigma)
        mu_fused = cv2.GaussianBlur(fused, (k_radius, k_radius), k_sigma)

        # Detail Kasar (High Frequency)
        raw_detail_ref = ref - mu_ref
        raw_detail_fused = fused - mu_fused

        # Varians Reference (Kekayaan Tekstur)
        ref_sq = ref * ref
        mu_ref_sq = cv2.GaussianBlur(ref_sq, (k_radius, k_radius), k_sigma)
        var_ref = mu_ref_sq - (mu_ref * mu_ref)
        var_ref = np.maximum(var_ref, 0.0)

        # =====================================================================
        # B. MEMBUAT ULANG PETA KEPERCAYAAN (RE-EVALUASI BOBOT)
        # =====================================================================
        # Di sini kita tidak percaya buta pada weight_map.

        # 1. Peta Bobot Awal (Saran dari akumulasi)
        w_map_expanded = weight_map[:, :, np.newaxis] if fused.ndim == 3 else weight_map
        weight_factor = np.clip(w_map_expanded / 8.0, 0.0, 1.0)  # 0.0 s/d 1.0

        # 2. Analisis KONSISTENSI STRUKTUR (Verifikasi Kebenaran)
        # Kita cek apakah detail di Fused Image 'sejalan' dengan Reference Image.
        # Jika Fused Image blur (karena misalignment) tapi Reference tajam,
        # maka similarity akan rendah.

        # Hitung dot product sederhana dari detail (Correlation)
        # +1.0 : Detail identik (Sangat Bagus)
        #  0.0 : Fused blur/flat (Kurang Bagus)
        # -1.0 : Detail berlawanan/Ghosting (Buruk)

        # Normalisasi magnitude agar perbandingan adil
        mag_ref = np.abs(raw_detail_ref) + 1e-6
        mag_fused = np.abs(raw_detail_fused) + 1e-6

        # Peta Konsistensi (-1 s/d 1)
        consistency_map = (raw_detail_ref * raw_detail_fused) / (mag_ref * mag_fused)

        # Mapping ke range 0.0 - 1.0 dengan bias ke arah positif
        # Jika konsistensi > 0, kita mulai percaya. Jika < 0, tidak percaya.
        structure_validity = np.clip((consistency_map + 0.2) * 1.5, 0.0, 1.0)

        # Jika gambar berwarna, ambil rata-rata validitas channel
        if structure_validity.ndim == 3:
            structure_validity = np.mean(structure_validity, axis=2, keepdims=True)

        # 3. FINAL CONFIDENCE MASK
        # Kepercayaan Akhir = (Saran Bobot) x (Verifikasi Struktur)
        # Jadi meskipun bobot tinggi, kalau strukturnya ngaco/blur, confidence turun.
        final_confidence = weight_factor * structure_validity

        # =====================================================================
        # C. ESTIMASI NOISE & WIENER
        # =====================================================================
        epsilon = 1e-6
        base_noise_var = base_noise_sigma**2

        # Noise map tetap pakai weight map asli (karena ini hukum statistik jumlah sampel)
        noise_var_map = base_noise_var / (w_map_expanded + epsilon)
        local_noise_sigma = np.sqrt(noise_var_map)

        alpha = var_ref / (var_ref + noise_var_map + epsilon)

        # =====================================================================
        # D. STRUCTURE INJECTION (CLEAN)
        # =====================================================================

        # Threshold 0.6 (Detail halus lolos)
        shrinkage_threshold = 0.6 * local_noise_sigma

        magnitude = np.abs(raw_detail_ref)
        cleaned_detail_ref = (
            np.sign(raw_detail_ref)
            * np.maximum(0, magnitude - shrinkage_threshold)
            * 1.1
        )

        structure_injected_image = mu_fused + cleaned_detail_ref

        # =====================================================================
        # E. SHARPENING (Hanya jika Confidence VALID)
        # =====================================================================

        # Sharpening 1.2
        sharpened_fused = fused + (raw_detail_fused * 1.2)

        # =====================================================================
        # F. FINAL MIXING
        # =====================================================================

        # Masking keputusan akhir
        # alpha menjamin kita hanya menajamkan area detail, bukan area flat.
        decision_mask = final_confidence * alpha

        # Smooth blending
        final_output = (structure_injected_image * (1.0 - decision_mask)) + (
            sharpened_fused * decision_mask
        )

        return np.clip(final_output, 0.0, 1.0)

    def _spatial_merging(
        self,
        images,
        ref_image_h,
        ref_image_w,
        ref_channels_buffer,
        ref_dtype,
        reference_image_float,
        tile_size,
        overlap,
        motion_sensitivity,
        noise_offset_factor,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
        lib_path="pixel_refine_desktop/ui/data/similarity_spatial_merging.dll",
        num_workers=-1,
        weight_of_each_image=False,
        enable_alignment=True,
        scale_down_factor: float = 1.0,
        return_raw=False,
        is_linear_mode=False,
        proxy_scale=1.0,
        process_in=None,
        **unused_kwargs,
    ):

        # --- LANGKAH 1: Inisialisasi dan Resolusi Kerja ---
        tile_h, tile_w = map(int, tile_size)
        num_images = len(images)
        work_res_h, work_res_w = ref_image_h, ref_image_w
        TARGET_MP = 12.5 * 1e6
        # --- COSTUM PROGRESS CALCULATION (GLOBAL SCOPE) MOVED UP ---
        use_overall_progress = total_overall_images and total_overall_images > 0
        if use_overall_progress:
            # Batch processing: Hitung slot global untuk stack ini
            scope_start = (images_processed_so_far / total_overall_images) * 100.0
            scope_end = (
                (images_processed_so_far + num_images) / total_overall_images
            ) * 100.0
        else:
            # Single processing: Full 0-100
            scope_start = 0.0
            scope_end = 100.0

        scope_width = scope_end - scope_start

        # Partitioning Scope:
        # Align: 5% - 40% (relative to scope)
        # Merge: 40% - 95% (relative to scope)
        p_init = int(scope_start + scope_width * 0.05)
        p_align_start = p_init
        p_align_end = int(scope_start + scope_width * 0.40)
        p_merge_start = p_align_end
        p_merge_end = int(scope_start + scope_width * 0.95)

        pass_merge_range = (p_merge_start, p_merge_end)

        # Initialize return variables to prevent UnboundLocalError
        processed_frames_spatial = 0
        final_image_sum_full_res = None
        weight_map_sum_full_res = None
        ref_noise_sigma = 0.0

        # --- Logika Scale Down ---
        if scale_down_factor != 1.0:
            if scale_down_factor < 1.0:
                work_res_h = int(ref_image_h * scale_down_factor)
                work_res_w = int(ref_image_w * scale_down_factor)
                if update_progress:
                    update_progress(p_init, f"Downscale aktif: {scale_down_factor:.2f}")
            else:
                if update_progress:
                    update_progress(p_init, "Menggunakan resolusi asli (scale > 1.0)")
        else:
            if (ref_image_h * ref_image_w) > TARGET_MP:
                scale_factor = np.sqrt(TARGET_MP / (ref_image_h * ref_image_w))
                work_res_h, work_res_w = int(ref_image_h * scale_factor), int(
                    ref_image_w * scale_factor
                )
                if update_progress:
                    update_progress(p_init, f"Auto-scale ke {scale_factor:.2f}x")
            else:
                if update_progress:
                    update_progress(p_init, "Menggunakan resolusi asli")

        # Pastikan genap
        work_res_h, work_res_w = (work_res_h // 2) * 2, (work_res_w // 2) * 2

        # Setup tiling parameters
        base_window = gaussian_window((tile_h, tile_w))
        step_y = max(int(tile_h * (1 - overlap)), 1)
        step_x = max(int(tile_w * (1 - overlap)), 1)

        # --- FIX TIPE DATA (PENTING AGAR TIDAK CRASH DI C++) ---
        row_starts = np.arange(0, work_res_h - tile_h + 1, step_y, dtype=np.int32)
        if work_res_h > tile_h and (
            row_starts.size == 0 or row_starts[-1] != work_res_h - tile_h
        ):
            row_starts = np.append(row_starts, work_res_h - tile_h)
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))

        col_starts = np.arange(0, work_res_w - tile_w + 1, step_x, dtype=np.int32)
        if work_res_w > tile_w and (
            col_starts.size == 0 or col_starts[-1] != work_res_w - tile_w
        ):
            col_starts = np.append(col_starts, work_res_w - tile_w)
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        # Execution Path (GPU/CPU)
        if process_in is None or process_in == "auto":
            process_in = "gpu"

        print(f"[DEBUG] _spatial_merging active mode: {process_in}")

        if process_in == "gpu":
            # [MODIFIED] Local import to prevent any Taichi initialization in CPU path
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.compute_similarity import (
                generate_weight_map_taichi,
                accumulate_spatial_merging_taichi,
            )

            if not TAICHI_SPATIAL_AVAILABLE:
                print(
                    "Warning: GPU requested but Taichi Spatial not available. Falling back to CPU."
                )
                process_in = "cpu"
            else:
                (
                    processed_frames_spatial,
                    final_image_sum_full_res,
                    weight_map_sum_full_res,
                    ref_noise_sigma,
                ) = process_in_gpu(
                    images=images,
                    reference_image_float=reference_image_float,
                    ref_image_h=ref_image_h,
                    ref_image_w=ref_image_w,
                    ref_channels_buffer=ref_channels_buffer,
                    ref_dtype=ref_dtype,
                    work_res_h=work_res_h,
                    work_res_w=work_res_w,
                    tile_h=tile_h,
                    tile_w=tile_w,
                    row_starts=row_starts,
                    col_starts=col_starts,
                    base_window=base_window,
                    motion_sensitivity=motion_sensitivity,
                    noise_offset_factor=noise_offset_factor,
                    update_progress=update_progress,
                    stop_requested=stop_requested,
                    pass_merge_range=pass_merge_range,
                    p_align_start=p_align_start,
                    p_align_end=p_align_end,
                    p_merge_start=p_merge_start,
                    is_linear_mode=is_linear_mode,
                    proxy_scale=proxy_scale,
                    images_processed_so_far=images_processed_so_far,
                    total_overall_images=total_overall_images,
                    enable_alignment=enable_alignment,
                    num_images=num_images,  # Pass num_images for alignment check
                    num_workers=num_workers,  # Pass num_workers for alignment
                    alignment_tile_size=8,  # [ROLLBACK] Reverted to 8 for warp efficiency
                    **unused_kwargs,
                )

        if process_in == "cpu":
            (
                processed_frames_spatial,
                final_image_sum_full_res,
                weight_map_sum_full_res,
                ref_noise_sigma,
            ) = process_in_cpu(
                images=images,
                reference_image_float=reference_image_float,
                ref_image_h=ref_image_h,
                ref_image_w=ref_image_w,
                ref_channels_buffer=ref_channels_buffer,
                ref_dtype=ref_dtype,
                work_res_h=work_res_h,
                work_res_w=work_res_w,
                tile_h=tile_h,
                tile_w=tile_w,
                row_starts=row_starts,
                col_starts=col_starts,
                base_window=base_window,
                motion_sensitivity=motion_sensitivity,
                noise_offset_factor=noise_offset_factor,
                num_workers=num_workers,
                update_progress=update_progress,
                stop_requested=stop_requested,
                pass_merge_range=pass_merge_range,
                p_align_start=p_align_start,
                p_align_end=p_align_end,
                p_merge_start=p_merge_start,
                is_linear_mode=is_linear_mode,
                proxy_scale=proxy_scale,
                images_processed_so_far=images_processed_so_far,
                total_overall_images=total_overall_images,
                lib_path=lib_path,
                enable_alignment=enable_alignment,
                num_images=num_images,  # Pass num_images for alignment check
                **unused_kwargs,
            )

        if final_image_sum_full_res is None:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        # --- LANGKAH 4: Normalisasi Akhir atau Return Raw ---
        if stop_requested and stop_requested():
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        if processed_frames_spatial > 0:
            # Jika return_raw aktif, kita kembalikan akumulator mentah untuk ditumpuk nanti
            if return_raw:
                return (
                    final_image_sum_full_res,
                    weight_map_sum_full_res,
                    processed_frames_spatial,
                )

            try:
                if update_progress:
                    update_progress(
                        pass_merge_range[1],
                        "Finalizing with Parallel Precision Fusion...",
                    )

                # Pastikan reference full res tersedia dalam float32
                ref_full_float = reference_image_float

                # --- PERUBAHAN UTAMA DI SINI ---
                # Kita panggil fungsi Tiled.
                # Fungsi ini akan menangani Normalisasi (Divide) DAN Structure Fusion
                # secara bertahap (per kotak) untuk menghemat memori.

                # --- CPU Tiled Fusion (RESTORED TO SAFE VERSION) ---
                final_image = self._apply_final_fusion_tiled(
                    sum_img=final_image_sum_full_res,
                    sum_weight=weight_map_sum_full_res,
                    ref_img=ref_full_float,
                    noise_sigma=ref_noise_sigma,
                    tile_size=512,
                    padding=16,
                )

                # Return result
                if weight_of_each_image:
                    return (
                        final_image,
                        weight_map_sum_full_res,
                        processed_frames_spatial,
                        [],
                    )
                else:
                    return (
                        final_image,
                        weight_map_sum_full_res,
                        processed_frames_spatial,
                    )

            except Exception as e:
                print(f"Critical error in final stage: {e}")
                # Fallback darurat: Normalisasi global biasa tanpa struktur
                if weight_map_sum_full_res is not None:
                    valid_mask = np.asarray(weight_map_sum_full_res) > 1e-6
                    fallback_img = np.zeros_like(final_image_sum_full_res)
                    np.divide(
                        final_image_sum_full_res,
                        weight_map_sum_full_res[:, :, np.newaxis],
                        out=fallback_img,
                        where=valid_mask[:, :, np.newaxis],
                    )
                else:
                    fallback_img = np.zeros_like(final_image_sum_full_res)
                if weight_of_each_image:
                    return (
                        fallback_img,
                        weight_map_sum_full_res,
                        processed_frames_spatial,
                        [],
                    )
                else:
                    return (
                        fallback_img,
                        weight_map_sum_full_res,
                        processed_frames_spatial,
                    )

        return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

    def similarity_mnfr(
        self,
        images,
        merging_type="spatial",
        tile_size=None,
        overlap=None,
        motion_sensitivity=None,
        noise_offset_factor=None,
        update_progress=None,
        stop_requested=None,
        save_weight_map_path=None,
        num_workers=None,
        total_overall_images=None,
        images_processed_so_far=0,
        save_temporal_std_path=None,
        weight_of_each_image=False,
        ref_image_override=None,
        return_raw=False,
        is_linear_mode=False,
        proxy_scale=1.0,  # [AUTO-SCALE]
        **merging_kwargs,
    ):
        """
        Fungsi utama untuk menghitung kesamaan dan penggabungan frame (spatial/frequency).
        Sudah tahan stop_requested(), return value konsisten meski proses dibatalkan.
        """
        if not isinstance(images, list) or not images:
            raise ValueError(language_config.IMAGE_DATA_MUST_BE_VALID)

        try:
            ref_image = (
                ref_image_override if ref_image_override is not None else images[0]
            )
            if not isinstance(ref_image, np.ndarray):
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)

            h_ref, w_ref, channels_ref_orig = (
                ref_image.shape[0],
                ref_image.shape[1],
                (ref_image.shape[2] if ref_image.ndim == 3 else 1),
            )
            dtype_ref = ref_image.dtype
            if channels_ref_orig not in (1, 3):
                raise ValueError(
                    language_config.IMAGE_CHANNEL_DOES_NOT_SUPPORT.format(
                        channels_ref_orig
                    )
                )

        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))

        if dtype_ref not in (np.uint8, np.uint16):
            raise TypeError(language_config.IMAGE_BIT_REQUIRED)

        channels_buffer = 3
        reference_image_float = normalize_image(ref_image, dtype_ref)

        if reference_image_float is None:
            raise ValueError(
                f"normalize_image returned None! Dtype: {dtype_ref}, Shape: {ref_image.shape}"
            )

        h_ref_norm, w_ref_norm, _ = reference_image_float.shape

        final_image_normalized, final_weight_map, processed_frames = None, None, 0
        weight_maps_per_image = []

        # --- Persiapan argumen umum ---
        common_call_args = {
            "images": images,
            "ref_image_h": h_ref_norm,
            "ref_image_w": w_ref_norm,
            "ref_channels_buffer": channels_buffer,
            "ref_dtype": dtype_ref,
            "reference_image_float": reference_image_float,
            "update_progress": update_progress,
            "stop_requested": stop_requested,
            "total_overall_images": total_overall_images,
            "images_processed_so_far": images_processed_so_far,
            "weight_of_each_image": weight_of_each_image,
            "return_raw": return_raw,
            "is_linear_mode": is_linear_mode,
            "proxy_scale": proxy_scale,
        }
        common_call_args.update(merging_kwargs)

        # --- Cek stop_requested() di awal ---
        if stop_requested and stop_requested():
            out_shape_fb = (
                (h_ref, w_ref)
                if channels_ref_orig == 1
                else (h_ref, w_ref, channels_ref_orig)
            )
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

        # --- Jalankan merging berdasarkan type ---
        results = None
        if merging_type == "spatial":
            current_tile_size = (
                tile_size
                if tile_size is not None
                else common_call_args.get("tile_size")
            )
            current_overlap = (
                overlap if overlap is not None else common_call_args.get("overlap")
            )
            current_motion_sensitivity = (
                motion_sensitivity
                if motion_sensitivity is not None
                else common_call_args.get("motion_sensitivity")
            )
            current_noise_offset_factor = (
                noise_offset_factor
                if noise_offset_factor is not None
                else common_call_args.get("noise_offset_factor")
            )
            current_num_workers = (
                num_workers
                if num_workers is not None
                else common_call_args.get("similarity_spatial_num_workers")
            )

            # Jika parameter penting belum tersedia, hentikan aman
            if any(
                p is None
                for p in [
                    current_tile_size,
                    current_overlap,
                    current_motion_sensitivity,
                    current_noise_offset_factor,
                ]
            ):
                out_shape_fb = (
                    (h_ref, w_ref)
                    if channels_ref_orig == 1
                    else (h_ref, w_ref, channels_ref_orig)
                )
                return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

            common_call_args.update(
                {
                    "tile_size": current_tile_size,
                    "overlap": current_overlap,
                    "motion_sensitivity": current_motion_sensitivity,
                    "noise_offset_factor": current_noise_offset_factor,
                    "num_workers": current_num_workers,
                    "temporal_consistency": True,
                    "save_temporal_std_path": save_temporal_std_path,
                }
            )
            results = self._spatial_merging(**common_call_args)
            if return_raw:
                return results

        else:
            raise ValueError(
                f"Unsupported merging_type: {merging_type}. Merging type must be 'spatial'."
            )

        # --- Jika tidak ada hasil karena stop_requested() ---
        if results is None:
            out_shape_fb = (
                (h_ref, w_ref)
                if channels_ref_orig == 1
                else (h_ref, w_ref, channels_ref_orig)
            )
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

        # --- Unpack results aman ---
        final_image_normalized = results[0]
        final_weight_map = results[1]
        processed_frames = results[2]

        # Safe access to individual_maps if it exists (length 4)
        individual_maps = results[3] if len(results) > 3 else []

        # --- Stop_requested setelah proses tapi sebelum semua frame selesai ---
        if (
            stop_requested
            and stop_requested()
            and (processed_frames is None or processed_frames < len(images))
        ):
            processed_frames = 0 if processed_frames is None else processed_frames
            all_final_weight_maps_to_return = individual_maps
            final_img_output = (
                np.zeros((h_ref, w_ref, channels_ref_orig), dtype=dtype_ref)
                if final_image_normalized is None
                else final_image_normalized
            )
            return final_img_output, final_weight_map, all_final_weight_maps_to_return

        # --- Finalisasi output ---
        if (
            processed_frames is not None
            and processed_frames > 0
            and final_image_normalized is not None
        ):
            all_final_weight_maps_to_return = individual_maps

            # Simpan weight map jika diminta
            if save_weight_map_path and final_weight_map is not None:
                try:
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    max_w = np.max(final_weight_map)
                    norm_w_vis = (
                        final_weight_map / max_w
                        if max_w > 1e-6
                        else np.zeros_like(final_weight_map)
                    )
                    w_map_vis = (np.clip(norm_w_vis, 0.0, 1.0) * 255).astype(np.uint8)
                    cv2.imwrite(save_weight_map_path, w_map_vis)
                except Exception:
                    traceback.print_exc()

            # Skala ke tipe asli
            scale_val = np.float32(np.iinfo(dtype_ref).max)
            final_img_scaled = final_image_normalized * scale_val
            if channels_ref_orig == 1:
                final_img_out_ch = np.mean(final_img_scaled, axis=2)
            else:
                final_img_out_ch = final_img_scaled
            min_v, max_v = 0, np.iinfo(dtype_ref).max
            final_img_output = np.clip(final_img_out_ch, min_v, max_v).astype(
                dtype_ref, copy=False
            )

            return final_img_output, final_weight_map, all_final_weight_maps_to_return

        else:
            # Jika tidak ada frame diproses
            out_shape_fb = (
                (h_ref, w_ref)
                if channels_ref_orig == 1
                else (h_ref, w_ref, channels_ref_orig)
            )

            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []


def _setup_data_source_and_paths(db_path, single_process, batch_id, image_processor):
    align_dir = os.path.join("database", "align")
    image_paths = []
    output_name_base = ""
    hdf5_path = ""

    if single_process:
        hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        image_paths = get_all_image_paths_for_single_process(db_path)
        ref_name = (
            os.path.splitext(os.path.basename(image_paths[0]))[0]
            if image_paths
            else "single_process"
        )
        output_name_base = ref_name
    else:
        if batch_id is None:
            pass
        hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
        image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
        ref_name = (
            os.path.splitext(os.path.basename(image_paths[0]))[0]
            if image_paths
            else f"batch_{batch_id}"
        )
        output_name_base = ref_name

    data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths

    total_images = 0
    if isinstance(data_source, str) and data_source.endswith(".h5"):
        print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(data_source))
        try:
            with h5py.File(data_source, "r") as f:
                total_images = len(f.keys())
        except Exception as e_h5:
            raise IOError(f"Gagal membaca file HDF5: {e_h5}")
    elif isinstance(data_source, list):
        total_images = len(data_source)

    return data_source, image_paths, output_name_base, total_images


def _load_images_for_batch(
    data_source,
    batch_indices,
    stop_requested=None,
    linear_mode=True,
    capture_ref_proxy=False,
):
    batch_start, batch_end = batch_indices
    batch_images = []
    ref_proxy = None

    if isinstance(data_source, str) and data_source.endswith(".h5"):
        with h5py.File(data_source, "r") as h5f:
            keys = list(h5f.keys())[batch_start:batch_end]
            batch_images = [
                np.array(h5f[key])
                for key in keys
                if not (stop_requested and stop_requested())
            ]
    elif isinstance(data_source, list):
        batch_paths = data_source[batch_start:batch_end]
        # Pass linear_mode to loader
        load_res = load_images_from_paths(
            batch_paths,
            stop_requested,
            linear_mode=linear_mode,
            capture_ref_proxy=capture_ref_proxy,
        )

        if capture_ref_proxy and isinstance(load_res, tuple):
            batch_images, ref_proxy = load_res
        else:
            batch_images = load_res

        if "resize_all_with_padding" in globals():
            # Note: Resizing Linear Data requires care, but for now we assume same-size RAWs or handle it normally.
            # Ideally resize happens on both Linear and Proxy identically.
            resize_res = resize_all_with_padding(
                batch_images, method="preserve", stop_requested=stop_requested
            )
            # Proxy should also be resized to match reference if resizing happened!
            # But currently resize_all_with_padding assumes list of images.
            # Ref Proxy is single image.
            # If batch_images[0] was resized, ref_proxy MUST be resized too.
            # But handling that logic inside resize_all_with_padding is cleanest?
            # Or just ignore assuming all same size is safe for now?
            # User uses RAWs, usually same resolution.
            if resize_res and resize_res[0]:
                batch_images = resize_res[0]

    if capture_ref_proxy:
        return batch_images, ref_proxy

    return batch_images


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    save_final_weight_map=False,
    progress_bar=None,
):
    try:
        if update_progress:
            update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        # --- 1. KONFIGURASI SPESIFIK UNTUK PROSES SIMILARITY ---
        general_settings = load_similarity_config()
        image_processor = SimilarityAlgorithm(db_path)

        merging_type_from_settings = general_settings.get(
            "similarity_merging_type", "spatial"
        )
        (
            spatial_tile_size_arg,
            spatial_overlap_arg,
            spatial_motion_sensitivity_arg,
            spatial_noise_offset_factor_arg,
        ) = (None, None, None, None)
        extra_merging_params = {}

        if merging_type_from_settings == "spatial":
            tile_val_sp = general_settings.get("similarity_spatial_tile_size", 16)
            spatial_tile_size_arg = (tile_val_sp, tile_val_sp)
            spatial_overlap_arg = general_settings.get(
                "similarity_spatial_overlap_percent", 0.3
            )
            spatial_motion_sensitivity_arg = general_settings.get(
                "similarity_spatial_motion_sensitivity", 150.00
            )
            spatial_noise_offset_factor_arg = general_settings.get(
                "similarity_spatial_noise_mad_offset_factor", 1.0
            )
            extra_merging_params["similarity_spatial_num_workers"] = (
                general_settings.get("similarity_spatial_num_workers", 1)
            )  # Default -1 (Auto)
            custom_lib_path = general_settings.get("similarity_lib_path")
            if custom_lib_path:
                extra_merging_params["lib_path"] = custom_lib_path

            # [USER REQUEST] Logic gate untuk Linear Mode dipindahkan ke sini
            # Default ke True agar aktif, set ke False untuk mematikan feature ini
            extra_merging_params["enable_linear_mode"] = general_settings.get(
                "enable_linear_mode", False
            )

        # --- 2. SETUP SUMBER DATA & PATH ---
        data_source, image_paths, output_name_base, total_images = (
            _setup_data_source_and_paths(
                db_path, single_process, batch_id, image_processor
            )
        )

        if not total_images:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return

        metadata_output_path = os.path.join("database", "align", "metadata.json")
        try:
            extract_all_metadata(image_paths, metadata_file=metadata_output_path)
        except Exception as e:
            pass

        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = (
            "".join(
                c for c in output_name_base if c.isalnum() or c in ("_", "-")
            ).rstrip()
            or "stack_result"
        )
        output_path = os.path.join(
            output_folder_stack,
            f"{output_name_base_safe}_similarity.tif",
        )
        weight_map_output_path = os.path.join(
            output_folder_stack,
            f"{output_name_base_safe}_similarity_weight_map.png",
        )
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map:
            print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))

        # --- 4. PERENCANAAN BATCH (UMUM) ---
        # Gunakan max_batch_size=8 untuk menjaga RAM tetap aman
        batch_plan = setup_balanced_batching(
            total_images, language_config, max_batch_size=8
        )
        if not batch_plan:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return
        total_batches = len(batch_plan)

        # --- DEFINISI FORMAT YANG DIDUKUNG ---
        SUPPORTED_FORMATS = {
            "jpg": [".jpg", ".jpeg", ".jiff", ".jli"],
            "tiff": [".tif", ".tiff"],
            "png": [".png"],
            "raw": [
                ".dng",
                ".cr2",
                ".cr3",
                ".nef",
                ".nrw",
                ".arw",
                ".srf",
                ".sr2",
                ".orf",
                ".rw2",
                ".pef",
                ".raf",
                ".erf",
                ".mrw",
                ".kdc",
                ".3fr",
                ".fff",
                ".rwl",
                ".srw",
                ".x3f",
                ".mef",
                ".iiq",
            ],
        }

        # --- DETEKSI MODE LINEAR ---
        # Cek apakah input adalah DNG/RAW untuk mengaktifkan Linear Mode
        is_linear_mode = False
        enable_linear_mode = extra_merging_params.get("enable_linear_mode", True)

        if (
            enable_linear_mode
            and isinstance(image_paths, list)
            and len(image_paths) > 0
        ):
            _, ext = os.path.splitext(image_paths[0])
            if ext.lower() in SUPPORTED_FORMATS["raw"]:
                is_linear_mode = True
                print(
                    " [Linear Mode] RAW Input detected. Activating Linear DNG Pipeline."
                )

        # Muat gambar referensi (Frame #1) dengan Dual Conversion jika Linear Mode
        ref_proxy_gt = None
        if is_linear_mode:
            # Dual return: (list_of_images, gt_proxy)
            reference_image_list_res = _load_images_for_batch(
                data_source,
                (0, 1),
                stop_requested,
                linear_mode=is_linear_mode,
                capture_ref_proxy=True,
            )
            if isinstance(reference_image_list_res, tuple):
                reference_image_list, ref_proxy_gt = reference_image_list_res
            else:
                reference_image_list = reference_image_list_res
        else:
            reference_image_list = _load_images_for_batch(
                data_source, (0, 1), stop_requested, linear_mode=is_linear_mode
            )

        if reference_image_list and len(reference_image_list) > 0:
            reference_image = reference_image_list[0]
            ref_dtype = reference_image.dtype
            if is_linear_mode and reference_image.dtype != np.uint16:
                print(
                    " [Warning] Linear mode active but reference image is not uint16!"
                )
        else:
            if update_progress:
                update_progress(0, language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED)
            return

        # [AUTO-SCALE] Smart Scale Fitting dari GT Proxy
        global_proxy_scale = 1.0
        if is_linear_mode and reference_image is not None:
            if ref_proxy_gt is not None:
                global_proxy_scale = calculate_scale_from_gt_proxy(
                    reference_image, ref_proxy_gt, ref_dtype
                )
                print(
                    f" [Linear Mode] Fitted Proxy Scale from GT: {global_proxy_scale:.3f}"
                )
            else:
                # Fallback ke Auto-Scale sederhana jika GT gagal
                ref_float_temp = normalize_image(reference_image, ref_dtype)
                global_proxy_scale = calculate_auto_scale(
                    ref_float_temp, target_mean=0.25
                )
                del ref_float_temp
                print(
                    f" [Linear Mode] Auto-calculated Proxy Scale (Fallback): {global_proxy_scale:.3f}"
                )

        # --- 5. PROSES INTI PER BATCH & AKUMULASI STREAMING ---
        global_sum_img = None
        global_sum_weight = None
        global_total_frames = 0
        images_processed_count = 0

        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break

            print(
                f"\n--- Processing batch {batch_num}/{total_batches} (Completed: {images_processed_count}) ---"
            )

            # Muat batch gambar
            current_batch_images = _load_images_for_batch(
                data_source,
                (batch_start, batch_end),
                stop_requested,
                linear_mode=is_linear_mode,
            )

            if not current_batch_images:
                continue

            # Jalankan Algoritma Similarity
            batch_raw_res = image_processor.similarity_mnfr(
                current_batch_images,
                merging_type=merging_type_from_settings,
                # reference_image_float=None,  <-- REMOVED: Preventing overwrite of internal calculation
                ref_image_override=reference_image,
                total_overall_images=total_images,
                images_processed_so_far=images_processed_count,
                # Parameter Algoritma
                tile_size=spatial_tile_size_arg,
                is_linear_mode=is_linear_mode,  # Pass flag for proxy generation
                overlap=spatial_overlap_arg if spatial_overlap_arg else 0.3,
                motion_sensitivity=(
                    spatial_motion_sensitivity_arg
                    if spatial_motion_sensitivity_arg
                    else 1.0
                ),
                noise_offset_factor=(
                    spatial_noise_offset_factor_arg
                    if spatial_noise_offset_factor_arg
                    else 1.0
                ),
                stop_requested=stop_requested,
                update_progress=update_progress,
                return_raw=True,  # Penting: Kita butuh data mentah (float/16bit) dari batch ini untuk akumulasi
                save_temporal_std_path=None,  # Tidak perlu simpan intermediate std map
                **extra_merging_params,
            )
            if stop_requested and stop_requested():
                break

            if batch_raw_res is not None and len(batch_raw_res) == 3:
                batch_sum_img, batch_sum_weight, batch_processed_frames = batch_raw_res

                if global_sum_img is None:
                    global_sum_img = batch_sum_img
                    global_sum_weight = batch_sum_weight
                else:
                    global_sum_img += batch_sum_img
                    global_sum_weight += batch_sum_weight

                global_total_frames += batch_processed_frames
                print(
                    f"[DEBUG] Accumulated frames: {global_total_frames} (Batch added: {batch_processed_frames})"
                )
                # Update progress based on actual images processed in source data
                images_processed_count += batch_end - batch_start

            # Paksa cleanup memori setiap akhir batch
            del current_batch_images
            gc.collect()

        if stop_requested and stop_requested():
            if update_progress and progress_bar:
                update_progress(progress_bar.value(), "Proses Dibatalkan.")
            return

        # --- 6. PENGGABUNGAN AKHIR (PRECISION STRUCTURE FUSION) ---
        final_result_img = None
        if global_sum_img is not None and global_total_frames > 0:
            if update_progress:
                update_progress(95, "Finalizing with Parallel Precision Fusion...")

            # Hitung estimasi noise dari referensi sebelum fusi akhir
            # Jika Linear Mode, reference_image adalah Linear. Kita butuh Proxy untuk estimasi noise structure?
            # Sebenarnya estimate_noise_in_python bekerja pada grayscale, jadi aman di-normalize.
            # [MODIFIED] Menggunakan preprocess_in_python (CPU)
            ref_gray_preproc, ref_noise_sigma = preprocess_in_python(
                normalize_image(reference_image, reference_image.dtype)
            )

            # --- 7. PENYIMPANAN HASIL AKHIR & PEMBERSIHAN ---
            final_result_normalized = image_processor._apply_final_fusion_tiled(
                sum_img=global_sum_img,
                sum_weight=global_sum_weight,
                ref_img=normalize_image(reference_image, reference_image.dtype),
                noise_sigma=ref_noise_sigma,
                tile_size=1024,
                padding=16,
            )

            # Kawal konversi bit-depth agar konsisten
            dtype_ref = reference_image.dtype
            # Jika is_linear_mode (Reference 16-bit), pastikan output 16-bit
            # Jika is_linear_mode=False, tetap ikuti reference (uint8 atau uint16)
            max_val = np.iinfo(dtype_ref).max
            final_result_img = np.clip(
                final_result_normalized * max_val, 0, max_val
            ).astype(dtype_ref)

            # Bebaskan memori
            del global_sum_img, global_sum_weight, final_result_normalized
            gc.collect()
        else:
            if update_progress and not (stop_requested and stop_requested()):
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if final_result_img is not None:
            ref_path_for_save = image_paths[0] if image_paths else None

            # [LINEAR DNG LOGIC] (Reverted)
            if is_linear_mode:
                # Ganti ekstensi output ke .dng
                dng_output_path = os.path.splitext(output_path)[0] + ".dng"

                save_success = save_linear_dng(
                    final_result_img,
                    dng_output_path,
                    reference_image_path=ref_path_for_save,
                )
                # Update output_path agar pesan sukses mengarah ke file yang benar
                if save_success:
                    output_path = save_success
            else:
                # Normal TIFF/JPG Save
                save_success = save_image(
                    final_result_img,
                    output_path,
                    reference_image_path=ref_path_for_save,
                )

            final_message = (
                f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                if save_success
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            )
            if update_progress:
                update_progress(100, final_message)

            if not single_process and batch_id is not None:
                # Cleanup temp files
                hdf5_path = os.path.join(
                    "database", "align", f"aligned_image_batch_{batch_id}.h5"
                )
                if os.path.exists(hdf5_path):
                    try:
                        os.remove(hdf5_path)
                    except OSError:
                        pass

    # --- 8. PENANGANAN ERROR (UMUM) ---
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)


def running_similarity(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):

    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                stop_requested=stop_callback,
                single_process=False,
                batch_id=batch_id,
            )
        except Exception as e:
            raise e
        return

    # ==========================================================
    # KONDISI 2: MODE SINGLE (DENGAN GUI DIALOG)
    # ==========================================================
    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle(language_config.WINDOW_TITLE_SIMILARITY)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    # Layout untuk progress bar dan label
    layout = QVBoxLayout(dialog)
    label = QLabel(language_config.WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    # Inisialisasi thread worker
    worker = BaseAlgorithmWorker(
        main,
        "pixel_refine_database.db",
        single_process=single_process,
        batch_id=batch_id,
    )
    progress_bar_instance = progress_bar  # Pass progress_bar to main
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(
            dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                language_config.CANCEL_PROCESSING,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                worker.stop()
                worker.quit()
                worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)
