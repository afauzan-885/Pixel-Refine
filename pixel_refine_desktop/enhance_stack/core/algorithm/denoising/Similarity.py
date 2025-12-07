from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import queue
import threading
import traceback
import cv2
import numpy as np
import sqlite3
import os
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PySide6.QtCore import QThread, Signal, Qt
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    estimate_noise_in_python,
    extract_all_metadata,
    gaussian_window,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    normalize_image,
    preprocess_in_python,
    resize_all_with_padding,
    save_image,
    setup_balanced_batching,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.extra_code.extra_algorithm import (
    SimilarityFrequencyInterface,
    SimilaritySpatialInterface,
    perform_image_alignment,
)
from pixel_refine_desktop.ui.resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.single_page.parameter_denoising.similarity_parameter_settings import (
    load_similarity_config,
)


class ThreadWorker(QThread):
    progress_updated = Signal(int, str)
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, db_path, single_process=True, batch_id=None):
        super().__init__()
        self.db_path = db_path
        self.single_process = single_process
        self.batch_id = batch_id
        self.stop_requested = False

    def run(self):
        try:

            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            def is_stop_requested():
                return self.stop_requested

            main(
                self.db_path,
                update_progress=update_progress,
                stop_requested=is_stop_requested,
                single_process=self.single_process,
                batch_id=self.batch_id,
            )

            self.finished.emit()
        except Exception as e:
            print(f"Error: {str(e)}")
            self.error_occurred.emit(str(e))

    def stop(self):
        self.stop_requested = True


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
        max_threads = max(2, os.cpu_count() - 1)

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
        **unused_kwargs,
    ):

        # --- LANGKAH 1: Inisialisasi dan Resolusi Kerja ---
        tile_h, tile_w = map(int, tile_size)
        try:
            c_interface = SimilaritySpatialInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal memuat C++ interface_spatial_merging: {e}")

        num_images = len(images)
        work_res_h, work_res_w = ref_image_h, ref_image_w
        TARGET_MP = 12.5 * 1e6

        # --- Logika Scale Down ---
        if scale_down_factor != 1.0:
            if scale_down_factor < 1.0:
                work_res_h = int(ref_image_h * scale_down_factor)
                work_res_w = int(ref_image_w * scale_down_factor)
                if update_progress:
                    update_progress(5, f"Downscale aktif: {scale_down_factor:.2f}")
            else:
                if update_progress:
                    update_progress(5, "Menggunakan resolusi asli (scale > 1.0)")
        else:
            if (ref_image_h * ref_image_w) > TARGET_MP:
                scale_factor = np.sqrt(TARGET_MP / (ref_image_h * ref_image_w))
                work_res_h, work_res_w = int(ref_image_h * scale_factor), int(
                    ref_image_w * scale_factor
                )
                if update_progress:
                    update_progress(5, f"Auto-scale ke {scale_factor:.2f}x")
            else:
                if update_progress:
                    update_progress(5, "Menggunakan resolusi asli")

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

        col_starts = np.arange(0, work_res_w - tile_w + 1, step_x, dtype=np.int32)
        if work_res_w > tile_w and (
            col_starts.size == 0 or col_starts[-1] != work_res_w - tile_w
        ):
            col_starts = np.append(col_starts, work_res_w - tile_w)

        # Paksa cast ke int32 secara eksplisit
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        use_overall_progress = total_overall_images and total_overall_images > 0

        # Range progress bar disesuaikan (karena Pass 1 hilang)
        # 0-30%: Init & Alignment
        # 30-100%: Merging
        pass_merge_range = (30, 100)

        # --- LANGKAH 2: ALIGNMENT ---
        if enable_alignment and num_images > 1:
            if update_progress:
                update_progress(10, "Memulai proses alignment...")

            # perform_image_alignment dipanggil
            alignment_success = perform_image_alignment(
                images,
                reference_image_float,
                work_res_h,
                work_res_w,
                tile_h,
                tile_w,
                ref_dtype,
                update_progress,
                stop_requested,
                num_alignment_workers=num_workers,
            )

            if alignment_success:
                if update_progress:
                    update_progress(30, "Alignment selesai.")
            else:
                if stop_requested and stop_requested():
                    return None, None, None
                if update_progress:
                    update_progress(30, "Alignment gagal/skip, lanjut merging...")
        else:
            if update_progress:
                update_progress(30, "Alignment dinonaktifkan.")

        # --- LANGKAH 3: MAIN MERGING ---

        # 1. Preprocess Global Reference
        ref_gray_preprocessed = preprocess_in_python(reference_image_float)
        ref_noise_sigma = estimate_noise_in_python(ref_gray_preprocessed)
        ref_work_res_pass2 = cv2.resize(
            ref_gray_preprocessed,
            (work_res_w, work_res_h),
            interpolation=cv2.INTER_AREA,
        )

        # Stability map untuk C++ tetap None karena Pass 1 dihapus
        stability_map_work_res = None

        # --- Producer: Generate Weight Map ---
        def weight_map_producer(task_queue, result_queue, images_list_ref):
            # Pre-allocate buffer lokal per thread
            local_curr_work_res = np.empty(
                (work_res_h, work_res_w, 1), dtype=np.float32
            )
            curr_work_gray = np.empty((work_res_h, work_res_w), dtype=np.float32)
            weight_map_work_res = np.zeros(
                (work_res_h, work_res_w), dtype=np.float32, order="C"
            )

            while True:
                try:
                    item = task_queue.get(timeout=0.1)
                except queue.Empty:
                    if stop_requested and stop_requested():
                        break
                    continue

                if item is None:  # Signal stop
                    task_queue.task_done()
                    break

                image_index = item
                image_orig = images_list_ref[image_index]

                if image_orig is None:
                    result_queue.put((image_index, None))
                    task_queue.task_done()
                    continue

                # Preprocessing
                curr_float = normalize_image(image_orig, ref_dtype)
                curr_preproc = preprocess_in_python(curr_float, use_raft=False)

                # Resize ke buffer yang sudah ada (dst)
                cv2.resize(
                    curr_preproc,
                    (work_res_w, work_res_h),
                    dst=curr_work_gray,
                    interpolation=cv2.INTER_AREA,
                )
                local_curr_work_res[:, :, 0] = curr_work_gray

                # Bersihkan weight map buffer sebelum dipakai ulang
                weight_map_work_res.fill(0)

                # Panggil C++ dengan stability_map=None (Logic temporal dihapus)
                c_interface.call_generate_weight_map_jit(
                    weight_map_sum=weight_map_work_res,
                    current_image=local_curr_work_res,
                    reference_image_processed=ref_work_res_pass2,
                    base_window=base_window,
                    stability_map=stability_map_work_res,
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

                # Clip dan konversi ke uint16 untuk hemat bandwidth queue
                np.clip(weight_map_work_res, 0.0, 1.0, out=weight_map_work_res)
                weight_map_uint16 = (weight_map_work_res * 65535.0).astype(np.uint16)

                result_queue.put((image_index, weight_map_uint16))
                task_queue.task_done()

        # --- Setup Threading ---
        final_image_sum_full_res = np.zeros(
            (ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32
        )
        weight_map_sum_full_res = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)

        # Buffer reusable untuk Consumer (Thread Utama)
        consumer_weight_full_buf = np.zeros(
            (ref_image_h, ref_image_w), dtype=np.float32
        )

        processed_frames_spatial = 0
        final_num_workers = (
            num_workers
            if num_workers > 0
            else max(1, min((os.cpu_count() or 2) // 2, 8))
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
        gc_trigger_count = 0
        gc_threshold = max(5, final_num_workers * 2)

        try:
            while finished_count < num_images:
                if stop_requested and stop_requested():
                    break

                try:
                    image_index, weight_map_uint16 = result_queue.get(timeout=0.1)
                    result_queue.task_done()

                    if weight_map_uint16 is not None:
                        image_orig = images[image_index]
                        if image_orig is not None:
                            # 1. Konversi & 2. Resize Weight Map ke Buffer Full Res
                            weight_map_work_float = weight_map_uint16.astype(
                                np.float32
                            ) * (1.0 / 65535.0)

                            cv2.resize(
                                weight_map_work_float,
                                (ref_image_w, ref_image_h),
                                dst=consumer_weight_full_buf,
                                interpolation=cv2.INTER_LINEAR,
                            )

                            # 3. Normalize & 4. Akumulasi In-place
                            norm_img = normalize_image(image_orig, ref_dtype)
                            np.multiply(
                                norm_img,
                                consumer_weight_full_buf[:, :, np.newaxis],
                                out=norm_img,
                            )

                            final_image_sum_full_res += norm_img
                            weight_map_sum_full_res += consumer_weight_full_buf

                            del norm_img, weight_map_work_float
                            images[image_index] = None  # Free memory

                            processed_frames_spatial += 1
                            gc_trigger_count += 1
                            if gc_trigger_count >= gc_threshold:
                                gc.collect()
                                gc_trigger_count = 0

                    finished_count += 1

                    if update_progress:
                        if use_overall_progress:
                            cur_ov = images_processed_so_far + finished_count
                            update_progress(
                                int(
                                    pass_merge_range[0]
                                    + (cur_ov / total_overall_images)
                                    * (pass_merge_range[1] - pass_merge_range[0])
                                ),
                                language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                                    cur_ov, total_overall_images
                                ),
                            )
                        else:
                            prog = finished_count / num_images
                            update_progress(
                                int(
                                    pass_merge_range[0]
                                    + prog * (pass_merge_range[1] - pass_merge_range[0])
                                ),
                                f"Merging frames: {finished_count}/{num_images}",
                            )

                except queue.Empty:
                    if not any(t.is_alive() for t in threads):
                        break
                    continue

        finally:
            if stop_requested and stop_requested():
                while not task_queue.empty():
                    try:
                        task_queue.get_nowait()
                    except:
                        pass

            for t in threads:
                t.join(timeout=1.0)

            del task_queue, result_queue, consumer_weight_full_buf
            gc.collect()

        # --- LANGKAH 4: Normalisasi Akhir ---
        if stop_requested and stop_requested():
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        if processed_frames_spatial > 0:
            try:
                if update_progress:
                    update_progress(95, "Finalizing with Parallel Precision Fusion...")

                # Pastikan reference full res tersedia dalam float32
                ref_full_float = normalize_image(reference_image_float, ref_dtype)

                # --- PERUBAHAN UTAMA DI SINI ---
                # Kita panggil fungsi Tiled.
                # Fungsi ini akan menangani Normalisasi (Divide) DAN Structure Fusion
                # secara bertahap (per kotak) untuk menghemat memori.

                final_image = self._apply_final_fusion_tiled(
                    sum_img=final_image_sum_full_res,
                    sum_weight=weight_map_sum_full_res,
                    ref_img=ref_full_float,
                    noise_sigma=ref_noise_sigma,
                    tile_size=1024,  # Ukuran tile (sesuaikan dengan RAM, 1024 aman)
                    padding=16,  # Padding untuk Gaussian Blur overlap
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
                valid_mask = weight_map_sum_full_res > 1e-6
                fallback_img = np.zeros_like(final_image_sum_full_res)
                np.divide(
                    final_image_sum_full_res,
                    weight_map_sum_full_res[:, :, np.newaxis],
                    out=fallback_img,
                    where=valid_mask[:, :, np.newaxis],
                )
                return (fallback_img, weight_map_sum_full_res, processed_frames_spatial)

        return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

    def _frequency_merging(
        self,
        images,
        ref_image_h,
        ref_image_w,
        ref_channels_buffer,
        ref_dtype,
        reference_image_float,
        freq_c_wiener_factor,
        freq_tile_size,
        freq_overlap_percent,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
        lib_path="pixel_refine_desktop/ui/data/similarity_frequency_merging.dll",
        refinement_algorithm="none",
        optical_flows=None,
        temporal_consistency=True,
        save_temporal_std_path=None,
        weight_of_each_image=False,
        # --- Parameter Alignment dari Spatial Merging ---
        enable_alignment=True,
        num_workers=2,
        # -----------------------------------------------
        **unused_kwargs,
    ):

        if not images:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        num_images = len(images)
        if num_images == 0:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        tile_h, tile_w = map(int, freq_tile_size)
        step_y = max(int(tile_h * (1 - freq_overlap_percent)), 1)
        step_x = max(int(tile_w * (1 - freq_overlap_percent)), 1)

        # Range progress bar: 0-95
        progress_cap_percent_start = 10  # Ruang untuk noise estimation/alignment
        progress_cap_percent = 95

        _, ref_noise_sigma = preprocess_in_python(reference_image_float)
        # Pastikan sigma positif, fallback ke nilai aman jika gagal
        ref_noise_sigma = max(ref_noise_sigma, 1e-6)

        c_interface = None

        def compute_starts(ref_size, tile_size, step_size):
            if ref_size >= tile_size:
                starts_temp = np.arange(0, ref_size - tile_size + 1, step_size)
                if ref_size > tile_size and (
                    starts_temp.size == 0 or starts_temp[-1] != ref_size - tile_size
                ):
                    starts_list = np.append(starts_temp, ref_size - tile_size)
                elif ref_size == tile_size:
                    starts_list = np.array([0])
                else:
                    starts_list = starts_temp
            else:
                starts_list = np.array([0])

            return np.ascontiguousarray(np.unique(starts_list.astype(np.int32)))

        # --- LANGKAH 1: Inisialisasi Tile ---
        row_starts = compute_starts(ref_image_h, tile_h, step_y)
        col_starts = compute_starts(ref_image_w, tile_w, step_x)

        # --- LANGKAH 2: PROSES ALIGNMENT (Dicopy dari _spatial_merging) ---
        if enable_alignment and num_images > 1:
            if update_progress:
                update_progress(5, "Memulai proses alignment gambar...")

            # Di frequency merging, alignment biasanya dilakukan pada resolusi penuh
            align_h, align_w = ref_image_h, ref_image_w
            align_tile_h, align_tile_w = (
                tile_h,
                tile_w,
            )  # Menggunakan ukuran tile frekuensi

            try:
                alignment_success = perform_image_alignment(
                    images,
                    reference_image_float,
                    align_h,
                    align_w,
                    align_tile_h,
                    align_tile_w,
                    ref_dtype,
                    update_progress,
                    stop_requested,
                    num_alignment_workers=num_workers,
                )
            except Exception as e:
                # Handle kegagalan alignment tanpa harus menghentikan seluruh proses
                alignment_success = False
                if update_progress:
                    update_progress(
                        10, f"Peringatan: Alignment gagal secara teknis: {e}"
                    )

            if alignment_success:
                if update_progress:
                    update_progress(
                        progress_cap_percent_start,
                        "Alignment selesai, melanjutkan ke frequency merging...",
                    )
            else:
                if stop_requested and stop_requested():
                    return (
                        (None, None, 0, []) if weight_of_each_image else (None, None, 0)
                    )

                # Jika hanya gagal (bukan dibatalkan), kita bisa lanjutkan dengan gambar asli.
                if update_progress:
                    update_progress(
                        progress_cap_percent_start,
                        "Alignment gagal atau dibatalkan, menggunakan gambar asli...",
                    )

        # --- LANGKAH 3: Lanjutkan ke Merging Frekuensi ---

        final_image_sum = np.zeros(
            (ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32, order="C"
        )
        weight_map_sum = np.zeros(
            (ref_image_h, ref_image_w), dtype=np.float32, order="C"
        )

        base_window = gaussian_window(freq_tile_size)

        first_image = images[0]
        if not isinstance(first_image, np.ndarray):
            # Cek ulang setelah alignment, jika gambar pertama dihapus/diubah.
            # Biasanya alignment mempertahankan array atau menggantinya dengan array yang selaras.
            pass

        orig_h, orig_w = ref_image_h, ref_image_w  # Gunakan resolusi referensi

        valid_images = []
        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray):
                continue
            # Cek dimensi (Alignment harusnya sudah memastikan dimensi seragam)
            num_ch_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
            if num_ch_orig != ref_channels_buffer:
                continue
            valid_images.append((i, image_orig))

        if not valid_images:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

        try:
            c_interface = SimilarityFrequencyInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal C++ interface _frequency_merging: {e}")

        if temporal_consistency:
            weight_maps_all = []
        if weight_of_each_image:
            weight_maps_per_image = []

        accumulated_weight_map, prev_weight_map_for_standard = None, None
        processed_frames_freq = 0
        block_h_cxx, block_w_cxx = tile_h, tile_w

        accumulated_weight_map, prev_weight_map_for_standard = None, None
        processed_frames_freq = 0
        block_h_cxx, block_w_cxx = tile_h, tile_w

        if total_overall_images and total_overall_images > 0:
            progress_factor = progress_cap_percent / total_overall_images
            use_overall_progress = True
        else:
            progress_factor = progress_cap_percent / len(valid_images)
            use_overall_progress = False

        for idx, (original_idx, image_orig) in enumerate(valid_images):
            if update_progress:
                if use_overall_progress:
                    current_img_overall = images_processed_so_far + original_idx + 1
                    prog_val = int(current_img_overall * progress_factor)
                    msg_val = language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                        current_img_overall, total_overall_images
                    )
                else:
                    prog_val = int((idx + 1) * progress_factor)
                    msg_val = language_config.ANALYZING_IMAGE.format(
                        idx + 1, len(valid_images)
                    )
                update_progress(prog_val, msg_val)

            if stop_requested and stop_requested():
                break

            try:
                current_image_float = normalize_image(image_orig, ref_dtype)
                if current_image_float.shape[2] != ref_channels_buffer:
                    continue
            except Exception:
                continue

            weight_map_sum_before_this_frame = weight_map_sum.copy()

            try:
                c_interface.call_accumulate_frame_weighted(
                    c_interface.clib,
                    final_image_sum,
                    weight_map_sum,
                    current_image_float,
                    reference_image_float,
                    base_window,
                    row_starts,
                    col_starts,
                    tile_h,
                    tile_w,
                    ref_image_h,
                    ref_image_w,
                    ref_channels_buffer,
                    block_h_cxx,
                    block_w_cxx,
                    freq_c_wiener_factor,
                    ref_noise_sigma,  # <--- ARGUMEN BARU
                )

                temp_weight_map = weight_map_sum - weight_map_sum_before_this_frame

                map_for_refinement = temp_weight_map

                # Lakukan penyempurnaan (refinement) menggunakan peta bobot yang sudah dipilih
                if (
                    refinement_algorithm == "optical_flow"
                    and optical_flows is not None
                    and original_idx < len(optical_flows)
                ):
                    if accumulated_weight_map is None:
                        refined_weight = map_for_refinement
                    else:
                        pass
                        # refined_weight = ml_driven_refinement(map_for_refinement, accumulated_weight_map, optical_flows[original_idx])
                    accumulated_weight_map = refined_weight.copy()
                elif refinement_algorithm == "standard":
                    # refined_weight = standard_refinement(map_for_refinement, prev_weight_map_for_standard, reference_image_float)
                    prev_weight_map_for_standard = refined_weight.copy()
                else:
                    refined_weight = map_for_refinement

                weight_map_sum = weight_map_sum_before_this_frame + refined_weight

                if weight_of_each_image:
                    weight_maps_per_image.append(refined_weight.copy())

                if temporal_consistency:
                    weight_maps_all.append(refined_weight.copy())

                processed_frames_freq += 1

            except Exception as e_cxx:
                print(
                    f"Warning: C++ accumulation failed for frame {original_idx+1}: {e_cxx}"
                )
                continue

        if processed_frames_freq > 0:
            try:
                c_interface.call_normalize_accumulated(
                    c_interface.clib,
                    final_image_sum,
                    weight_map_sum,
                    ref_image_h,
                    ref_image_w,
                    ref_channels_buffer,
                )

                # --- [DINONAKTIFKAN SEMENTARA] ---
                # if temporal_consistency:
                #     temporal_consistency_refinement(weight_maps_all, weight_map_sum, save_temporal_std_path=save_temporal_std_path)

                return (
                    (
                        final_image_sum,
                        weight_map_sum,
                        processed_frames_freq,
                        weight_maps_per_image,
                    )
                    if weight_of_each_image
                    else (final_image_sum, weight_map_sum, processed_frames_freq)
                )

            except Exception as e_norm:
                raise RuntimeError(
                    f"{language_config.NORMALIZATION_FAILED.format(e_norm)} (frequency merging)"
                )
        else:
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
        **merging_kwargs,
    ):
        """
        Fungsi utama untuk menghitung kesamaan dan penggabungan frame (spatial/frequency).
        Sudah tahan stop_requested(), return value konsisten meski proses dibatalkan.
        """
        if not isinstance(images, list) or not images:
            raise ValueError(language_config.IMAGE_DATA_MUST_BE_VALID)

        try:
            ref_image = images[0]
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

        elif merging_type == "frequency":
            default_freq_tile_val, default_freq_overlap, default_freq_c_wiener = (
                24,
                0.20,
                5.0,
            )
            default_freq_lib_path = common_call_args.get(
                "lib_path_freq",
                common_call_args.get(
                    "lib_path",
                    "pixel_refine_desktop/ui/data/similarity_frequency_merging.dll",
                ),
            )
            current_freq_c_wiener = common_call_args.get(
                "freq_c_wiener_factor", default_freq_c_wiener
            )
            current_freq_tile_size_input = common_call_args.get(
                "freq_tile_size", default_freq_tile_val
            )
            current_freq_overlap = common_call_args.get(
                "freq_overlap_percent", default_freq_overlap
            )

            if isinstance(current_freq_tile_size_input, int):
                current_freq_tile_size_tuple = (
                    current_freq_tile_size_input,
                    current_freq_tile_size_input,
                )
            elif (
                isinstance(current_freq_tile_size_input, (list, tuple))
                and len(current_freq_tile_size_input) == 2
            ):
                current_freq_tile_size_tuple = tuple(
                    map(int, current_freq_tile_size_input)
                )
            else:
                current_freq_tile_size_tuple = (
                    default_freq_tile_val,
                    default_freq_tile_val,
                )

            common_call_args.update(
                {
                    "freq_c_wiener_factor": current_freq_c_wiener,
                    "freq_tile_size": current_freq_tile_size_tuple,
                    "freq_overlap_percent": current_freq_overlap,
                    "lib_path": default_freq_lib_path,
                    # "num_workers": current_num_workers,
                    "temporal_consistency": True,
                    "save_temporal_std_path": save_temporal_std_path,
                }
            )

            # Hapus parameter spatial agar tidak kacau
            for key_to_remove in [
                "tile_size",
                "overlap",
                "motion_sensitivity",
                "noise_offset_factor",
            ]:
                common_call_args.pop(key_to_remove, None)

            results = self._frequency_merging(**common_call_args)

        else:
            raise ValueError(
                f"Unsupported merging_type: {merging_type}. Choose 'spatial' or 'frequency'."
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
        if weight_of_each_image:
            (
                final_image_normalized,
                final_weight_map,
                processed_frames,
                individual_maps,
            ) = results
        else:
            final_image_normalized, final_weight_map, processed_frames = results
            individual_maps = []

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
        if processed_frames > 0 and final_image_normalized is not None:
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


def _load_images_for_batch(data_source, batch_indices, stop_requested=None):
    batch_start, batch_end = batch_indices
    batch_images = []

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
        batch_images = load_images_from_paths(batch_paths, stop_requested)
        if "resize_all_with_padding" in globals():
            batch_images, _ = resize_all_with_padding(batch_images, method="preserve")

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
            tile_val_sp = general_settings.get("similarity_spatial_tile_size", 24)
            spatial_tile_size_arg = (tile_val_sp, tile_val_sp)
            spatial_overlap_arg = general_settings.get(
                "similarity_spatial_overlap_percent", 0.6
            )
            spatial_motion_sensitivity_arg = general_settings.get(
                "similarity_spatial_motion_sensitivity", 110.0
            )
            spatial_noise_offset_factor_arg = general_settings.get(
                "similarity_spatial_noise_mad_offset_factor", 0.3
            )
            extra_merging_params["similarity_spatial_num_workers"] = (
                general_settings.get("similarity_spatial_num_workers", -1)
            )  # Default -1 (Auto)
            custom_lib_path = general_settings.get("similarity_lib_path")
            if custom_lib_path:
                extra_merging_params["lib_path"] = custom_lib_path

        elif merging_type_from_settings == "frequency":
            extra_merging_params["freq_c_wiener_factor"] = general_settings.get(
                "similarity_frequency_c_wiener_factor", 5.0
            )
            tile_val_fq = general_settings.get("similarity_frequency_tile_size", 16)
            extra_merging_params["freq_tile_size"] = tile_val_fq
            extra_merging_params["freq_overlap_percent"] = general_settings.get(
                "similarity_frequency_overlap_percent", 0.25
            )
            # extra_merging_params['num_workers'] = general_settings.get("similarity_spatial_num_workers", 2)

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
            f"{output_name_base_safe}_similarity_{merging_type_from_settings}.tif",
        )
        weight_map_output_path = os.path.join(
            output_folder_stack,
            f"{output_name_base_safe}_similarity_{merging_type_from_settings}_weight_map.png",
        )
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map:
            print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))

        # --- 4. PERENCANAAN BATCH (UMUM) ---
        batch_plan = setup_balanced_batching(total_images, language_config)
        if not batch_plan:
            if update_progress:
                update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return
        total_batches = len(batch_plan)

        # --- 5. PROSES INTI PER BATCH ---
        processed_batches_results = []
        images_processed_count = 0

        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break

            print(
                f"\n{language_config.PROCESSING_BATCH.format(batch_num, total_batches, batch_start)}"
            )

            batch_images_list = _load_images_for_batch(
                data_source, (batch_start, batch_end), stop_requested
            )

            if stop_requested and stop_requested():
                break
            if not batch_images_list:
                print(
                    language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(
                        batch_num
                    )
                )
                continue

            batch_result_img, _, _ = image_processor.similarity_mnfr(
                images=batch_images_list,
                merging_type=merging_type_from_settings,
                tile_size=spatial_tile_size_arg,
                overlap=spatial_overlap_arg,
                motion_sensitivity=spatial_motion_sensitivity_arg,
                noise_offset_factor=spatial_noise_offset_factor_arg,
                update_progress=update_progress,
                stop_requested=stop_requested,
                total_overall_images=total_images,
                images_processed_so_far=images_processed_count,
                weight_of_each_image=False,  # Tidak lagi membutuhkan peta bobot individual
                **extra_merging_params,
            )

            if stop_requested and stop_requested():
                break

            if batch_result_img is not None:
                processed_batches_results.append(batch_result_img)
                images_processed_count += len(batch_images_list)

        if stop_requested and stop_requested():
            if update_progress and progress_bar:
                update_progress(progress_bar.value(), "Proses Dibatalkan.")
            return

        # --- 6. PENGGABUNGAN AKHIR / FINE-TUNING ---
        final_result_img = None
        if processed_batches_results:

            # Panggil fungsi resize_all_with_padding pada hasil-hasil batch
            processed_batches_results, final_shape = resize_all_with_padding(
                processed_batches_results, method="preserve"
            )
            print(f"Semua hasil batch disesuaikan ke ukuran target: {final_shape}")
            # --- AKHIR PENAMBAHAN KODE ---

            if len(processed_batches_results) > 1:
                fine_tuning_start_progress, fine_tuning_end_progress = 95, 99

                def fine_tuning_update_progress(inner_progress, message):
                    mapped_progress = fine_tuning_start_progress + int(
                        (inner_progress / 100.0)
                        * (fine_tuning_end_progress - fine_tuning_start_progress)
                    )
                    if update_progress and not (stop_requested and stop_requested()):
                        update_progress(
                            mapped_progress, language_config.ENHANCEMENT.format(message)
                        )

                if update_progress:
                    update_progress(
                        fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT
                    )

                final_result_img, _, _ = image_processor.similarity_mnfr(
                    images=processed_batches_results,
                    merging_type=merging_type_from_settings,
                    tile_size=spatial_tile_size_arg,
                    overlap=spatial_overlap_arg,
                    motion_sensitivity=spatial_motion_sensitivity_arg,
                    noise_offset_factor=spatial_noise_offset_factor_arg,
                    update_progress=fine_tuning_update_progress,
                    stop_requested=stop_requested,
                    save_weight_map_path=(
                        weight_map_output_path if save_final_weight_map else None
                    ),
                    total_overall_images=len(processed_batches_results),
                    images_processed_so_far=0,
                    weight_of_each_image=False,
                    **extra_merging_params,
                )
            else:
                final_result_img = processed_batches_results[0]

        # --- 7. PENYIMPANAN HASIL AKHIR & PEMBERSIHAN ---
        if final_result_img is not None:
            ref_path_for_save = image_paths[0] if image_paths else None
            save_success = save_image(
                final_result_img, output_path, reference_image_path=ref_path_for_save
            )

            final_message = (
                f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                if save_success
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            )
            if update_progress:
                update_progress(100, final_message)

            if not single_process and batch_id is not None:
                hdf5_path = os.path.join(
                    "database", "align", f"aligned_image_batch_{batch_id}.h5"
                )
                if os.path.exists(hdf5_path):
                    try:
                        os.remove(hdf5_path)
                    except OSError as e:
                        print(f"Error removing temp file: {e}")
        else:
            if update_progress:
                update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

    # --- 8. PENANGANAN ERROR (UMUM) ---
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)


def running_similarity(
    parent=None, single_process=None, batch_id=None, progress_callback=None
):

    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
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
    worker = ThreadWorker(
        "pixel_refine_database.db", single_process=single_process, batch_id=batch_id
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
    main(
        "pixel_refine_database.db",
        update_progress=worker.progress_updated.emit,
        stop_requested=worker.stop_requested,
        progress_bar=progress_bar_instance,
    )
    dialog.exec()


if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)
