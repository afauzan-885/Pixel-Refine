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
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import (add_legend_heatmap, extract_all_metadata, 
                                                                                    gaussian_window, get_all_image_paths_for_single_process, load_images_from_paths, 
                                                                                    normalize_image, preprocess_in_python, resize_all_with_padding, save_image, setup_balanced_batching)
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityFrequencyInterface, SimilaritySpatialInterface, perform_image_alignment
from UI.enhance_stack.components.single_page_layout.parameter_denoising.similarity_parameter_settings import  load_similarity_config
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.Language import language_config

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
                batch_id=self.batch_id
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
            cursor.execute("""
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
            """, (batch_id,))
            return [row[0] for row in cursor.fetchall()]

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images
    
    def _spatial_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                    reference_image_float, tile_size, overlap,
                    motion_sensitivity, noise_offset_factor,
                    update_progress=None, stop_requested=None,
                    total_overall_images=None, images_processed_so_far=0,
                    lib_path='UI/data/similarity_spatial_merging.dll',
                    temporal_consistency=False, num_workers=-1,
                    save_temporal_std_path=None,
                    weight_of_each_image=False,
                    temporal_analysis_mode='one_pass',
                    enable_alignment=True,
                    scale_down_factor: float = 1.0,  # <--- Tambahan baru
                    **unused_kwargs):

        # --- LANGKAH 1: Inisialisasi dan Penentuan Resolusi Kerja ---
        tile_h, tile_w = map(int, tile_size)
        try:
            c_interface = SimilaritySpatialInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal memuat C++ interface_spatial_merging: {e}")

        num_images = len(images)
        work_res_h, work_res_w = ref_image_h, ref_image_w
        TARGET_MP = 12 * 1e6  # target maksimum megapixel untuk skala otomatis

        # --- Logika skala otomatis + manual ---
        if scale_down_factor != 1.0:
            if scale_down_factor < 1.0:
                # Skalakan ke resolusi lebih rendah sesuai faktor manual
                work_res_h = int(ref_image_h * scale_down_factor)
                work_res_w = int(ref_image_w * scale_down_factor)
                if update_progress:
                    update_progress(10, f"Menggunakan scale_down_factor={scale_down_factor:.2f} (downscale aktif)")
            else:
                # > 1.0: skip resize (anggap tidak perlu scaling ke atas)
                work_res_h, work_res_w = ref_image_h, ref_image_w
                if update_progress:
                    update_progress(10, f"scale_down_factor={scale_down_factor:.2f} > 1.0, menggunakan resolusi asli")
        else:
            # scale_down_factor == 1.0 → tidak ada resize, tetapi jika resolusi terlalu besar, otomatis di-scale
            if (ref_image_h * ref_image_w) > TARGET_MP:
                scale_factor = np.sqrt(TARGET_MP / (ref_image_h * ref_image_w))
                work_res_h, work_res_w = int(ref_image_h * scale_factor), int(ref_image_w * scale_factor)
                if update_progress:
                    update_progress(10, f"Resolusi tinggi terdeteksi, otomatis scale ke {scale_factor:.2f}x")
            else:
                # Tidak perlu resize (resolusi masih aman)
                work_res_h, work_res_w = ref_image_h, ref_image_w
                if update_progress:
                    update_progress(10, "Menggunakan resolusi asli (scale_down_factor=1.0)")

        # Pastikan resolusi genap (penting untuk tile processing)
        work_res_h, work_res_w = (work_res_h // 2) * 2, (work_res_w // 2) * 2

        
        base_window = gaussian_window((tile_h, tile_w))
        step_y = max(int(tile_h * (1 - overlap)), 1)
        step_x = max(int(tile_w * (1 - overlap)), 1)
        row_starts = np.arange(0, work_res_h - tile_h + 1, step_y) if work_res_h >= tile_h else np.array([0])
        if work_res_h > tile_h and (not row_starts.size or row_starts[-1] != work_res_h - tile_h):
            row_starts = np.append(row_starts, work_res_h - tile_h)
        col_starts = np.arange(0, work_res_w - tile_w + 1, step_x) if work_res_w >= tile_w else np.array([0])
        if work_res_w > tile_w and (not col_starts.size or col_starts[-1] != work_res_w - tile_w):
            col_starts = np.append(col_starts, work_res_w - tile_w)
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        is_two_pass = temporal_analysis_mode == 'two_pass_full'
        use_overall_progress = total_overall_images and total_overall_images > 0
        pass1_range = (0, 50)
        pass2_range = (50, 95) if is_two_pass else (0, 95)
        
        # --- (PASS 1): Membuat Peta Stabilitas (Tidak Berubah, Tetap Sekuensial) ---
        stability_map = None
        if is_two_pass:
            if update_progress:
                update_progress(pass1_range[0], language_config.ANALYSIS_STEP_ONE)
            
            downsampled_h, downsampled_w = work_res_h // 2, work_res_w // 2
            sum_map = np.zeros((downsampled_h, downsampled_w), dtype=np.float32)
            sum_sq_map = np.zeros((downsampled_h, downsampled_w), dtype=np.float32)
            frame_count = 0
            
            ref_work_res = cv2.resize(reference_image_float, (work_res_w, work_res_h), interpolation=cv2.INTER_NEAREST_EXACT)

            for i, image_orig in enumerate(images):
                if stop_requested and stop_requested(): return (None, None, 0)
                
                if update_progress:
                    progress_in_pass1 = (i + 1) / num_images
                    current_total_progress = pass1_range[0] + (progress_in_pass1 * (pass1_range[1] - pass1_range[0]))
                    update_progress(
                        int(current_total_progress),
                        language_config.ANALYSIS_STEP_ONE_PROGRESS.format(i + 1, num_images)
                    )
                
                curr_work_res = cv2.resize(normalize_image(image_orig, ref_dtype), (work_res_w, work_res_h), interpolation=cv2.INTER_NEAREST_EXACT)
                temp_weight_map = np.ascontiguousarray(np.zeros((work_res_h, work_res_w), dtype=np.float32))
                
                c_interface.call_generate_weight_map_jit(
                    weight_map_sum=temp_weight_map,
                    current_image=curr_work_res, reference_image=ref_work_res, base_window=base_window,
                    stability_map=None, row_starts=row_starts, col_starts=col_starts,
                    tile_h=tile_h, tile_w=tile_w, h=work_res_h, w=work_res_w, channels=ref_channels_buffer,
                    motion_sensitivity=motion_sensitivity, noise_offset_factor=noise_offset_factor
                )
                
                downsampled_map = cv2.resize(temp_weight_map, (downsampled_w, downsampled_h), interpolation=cv2.INTER_NEAREST_EXACT)
                sum_map += downsampled_map
                sum_sq_map += np.square(downsampled_map)
                frame_count += 1
                del temp_weight_map, curr_work_res, downsampled_map

            if frame_count >= 2:
                N = float(frame_count)
                mean_map = sum_map / N
                variance_map = (sum_sq_map / N) - np.square(mean_map)
                variance_map[variance_map < 0] = 0 
                std_weights_low_res = np.sqrt(variance_map)
                max_std = np.max(std_weights_low_res)
                stability_map_low_res = 1.0 - (std_weights_low_res / (max_std + 1e-6))
                stability_map_full_res = cv2.resize(stability_map_low_res.astype(np.float32), (ref_image_w, ref_image_h), interpolation=cv2.INTER_LINEAR_EXACT)
                stability_map = np.ascontiguousarray(np.clip(stability_map_full_res**2.0, 0.0, 1.0).astype(np.float32))
            
            del sum_map, sum_sq_map

        # --- LANGKAH 2: PROSES ALIGNMENT ---
        if enable_alignment and num_images > 1:
            if update_progress:
                update_progress(30, "Memulai proses alignment gambar...")
            
            # Panggil fungsi alignment yang sekarang memodifikasi 'images' secara langsung
            alignment_success = perform_image_alignment(
                images,
                reference_image_float, 
                work_res_h, work_res_w,
                tile_h, tile_w, 
                ref_dtype, 
                update_progress, 
                stop_requested,
                num_alignment_workers=num_workers
            )
            
            if alignment_success:
                if update_progress:
                    update_progress(40, "Alignment selesai, melanjutkan ke spatial merging...")
            else:
                if stop_requested and stop_requested():
                    return None, None, None
                
                # Jika hanya gagal (bukan dibatalkan), kita bisa lanjutkan dengan gambar asli.
                if update_progress:
                    update_progress(40, "Alignment gagal, menggunakan gambar asli...")
        
        # --- LANGKAH 3 (PASS 2 / UTAMA): TAHAP A - PEMROSESAN C++ PARALEL ---
        msg_pass = "Pass 2/2: " if is_two_pass else ""
        ref_gray_preprocessed, ref_noise_sigma = preprocess_in_python(reference_image_float)
        ref_work_res_pass2 = cv2.resize(ref_gray_preprocessed, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
        stability_map_work_res = None
        if stability_map is not None:
            stability_map_work_res = cv2.resize(stability_map, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)

        # --- Producer 'weight_map_producer' dengan penanganan berhenti yang tangguh ---
        def weight_map_producer(task_queue, result_queue, images_list_ref):
            # Prealokasi buffer sekali saja (grayscale channel 1)
            local_curr_work_res = np.empty((work_res_h, work_res_w, 1), dtype=np.float32)
            curr_work_gray = np.empty((work_res_h, work_res_w), dtype=np.float32)

            while True:
                if stop_requested and stop_requested():
                    break
                try:
                    item = task_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                if item is None:
                    break

                image_index = item
                image_orig = images_list_ref[image_index]
                if not isinstance(image_orig, np.ndarray):
                    # Jika gambar sudah dihapus (di set ke None) oleh mekanisme sebelumnya, 
                    # atau ada kegagalan, kirim None dan tandai tugas selesai.
                    result_queue.put((image_index, None))
                    task_queue.task_done()
                    continue

                # === Preprocess current image jadi grayscale ===
                curr_float = normalize_image(image_orig, ref_dtype)
                curr_preproc, _ = preprocess_in_python(curr_float, use_raft=False)
                cv2.resize(curr_preproc, (work_res_w, work_res_h), dst=curr_work_gray, interpolation=cv2.INTER_AREA)

                # Bungkus ke format 3D agar kompatibel dengan C++
                local_curr_work_res[:, :, 0] = curr_work_gray

                weight_map_work_res = np.zeros((work_res_h, work_res_w), dtype=np.float32, order='C')

                c_interface.call_generate_weight_map_jit(
                    weight_map_sum=weight_map_work_res,
                    current_image=local_curr_work_res,
                    reference_image_processed=ref_work_res_pass2,
                    base_window=base_window,
                    stability_map=stability_map_work_res,
                    row_starts=row_starts, col_starts=col_starts,
                    tile_h=tile_h, tile_w=tile_w, 
                    h=work_res_h, w=work_res_w,
                    channels=1,
                    motion_sensitivity=motion_sensitivity,
                    noise_offset_factor=noise_offset_factor,
                    precomputed_ref_noise_sigma=ref_noise_sigma
                )

                weight_map_work_res = np.clip(weight_map_work_res, 0.0, 1.0)
                weight_map_uint16 = (weight_map_work_res * 65535.0).astype(np.uint16)
                del weight_map_work_res  

                result_queue.put((image_index, weight_map_uint16))
                task_queue.task_done() # Penting: Beri tahu task_queue bahwa tugas ini selesai

        # --- LANGKAH 4: Arsitektur "Streaming Fusion" dengan Kontrol Konkurensi Ketat ---
        final_image_sum_full_res = np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32)
        weight_map_sum_full_res = np.zeros((ref_image_h, ref_image_w), dtype=np.float32)
        processed_frames_spatial = 0
        
        final_num_workers = num_workers
        if final_num_workers <= 0:  
            cpu_cores = os.cpu_count() or 2
            final_num_workers = max(1, min(cpu_cores // 2, 8))
            
        # task_queue (Unbounded): Digunakan untuk mengirimkan INDEX gambar ke worker.
        task_queue = queue.Queue()
        result_queue = queue.Queue(maxsize=final_num_workers) 
        
        # Inisialisasi thread workers
        threads = [threading.Thread(target=weight_map_producer, args=(task_queue, result_queue, images)) for _ in range(final_num_workers)]
        
        next_index_to_send = 0
        
        try:
            for t in threads: t.start()

            # --- Inisialisasi Pengiriman Tugas (Hanya Sejumlah Workers) ---
            # Ini memastikan bahwa HANYA num_workers frame yang diproses/menunggu pada satu waktu.
            initial_batch_size = min(num_images, final_num_workers)
            for i in range(initial_batch_size):
                task_queue.put(i)
                next_index_to_send += 1
            
            finished_count = 0
            gc_trigger_count = 0 
            
            # --- Konsumen Utama (Main Loop) ---
            while finished_count < num_images:
                if stop_requested and stop_requested():
                    break
                
                try:
                    # Ambil hasil dari worker (weight map)
                    image_index, weight_map_uint16 = result_queue.get(timeout=0.1)
                    result_queue.task_done() # Tandai item di result_queue selesai

                    if weight_map_uint16 is not None:
                        
                        weight_map_work_res = weight_map_uint16.astype(np.float32) / 65535.0
                        del weight_map_uint16
                        
                        image_orig = images[image_index]
                        
                        if image_orig is None:
                            # Ini seharusnya tidak terjadi jika kita mengelola 'images' dengan benar
                            finished_count += 1
                            continue
                            
                        # --- LANGKAH FUSI GAMBAR RESOLUSI PENUH (Terjadi di thread utama) ---
                        weight_map_full_res = cv2.resize(weight_map_work_res, (ref_image_w, ref_image_h), interpolation=cv2.INTER_LINEAR)
                        normalized_image_full_res = normalize_image(image_orig, ref_dtype)
                        
                        np.multiply(normalized_image_full_res, weight_map_full_res[:, :, np.newaxis], out=normalized_image_full_res)

                        final_image_sum_full_res += normalized_image_full_res.astype(np.float32)
                        weight_map_sum_full_res += weight_map_full_res.astype(np.float32)

                        del normalized_image_full_res, weight_map_full_res, weight_map_work_res
                        
                        # --- PELEPASAN MEMORI DAN PENGATURAN GC (KRUSIAL) ---
                        images[image_index] = None
                        gc_trigger_count += 1 
                        
                        if gc_trigger_count >= final_num_workers:
                            gc.collect()
                            gc_trigger_count = 0 
                        
                        processed_frames_spatial += 1
                        
                        # --- PENGGANTIAN TUGAS (MENGATUR KONKURENSI) ---
                        # Setelah FUSI selesai dan memori dilepaskan, 
                        # kita kirim tugas berikutnya ke task_queue.
                        if next_index_to_send < num_images:
                            task_queue.put(next_index_to_send)
                            next_index_to_send += 1
                        # ----------------------------------------------------

                    finished_count += 1
                    # if finished_count % 1 == 0:
                    #     gc.collect()

                    if update_progress:
                        current_frame_index_in_pass = finished_count
                        if use_overall_progress:
                            current_img_overall = images_processed_so_far + current_frame_index_in_pass
                            progress_in_pass2 = current_img_overall / total_overall_images
                            msg = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_img_overall, total_overall_images)
                        else:
                            progress_in_pass2 = current_frame_index_in_pass / num_images
                            msg = language_config.ANALYSIS_STEP_TWO_PROGRESS.format(msg_pass, current_frame_index_in_pass, num_images)
                        current_total_progress = pass2_range[0] + (progress_in_pass2 * (pass2_range[1] - pass2_range[0]))
                        update_progress(int(current_total_progress), msg)


                except queue.Empty:
                    # Jika antrian hasil kosong, pastikan kita tidak terjebak.
                    if finished_count == num_images:
                         break
                    if not any(t.is_alive() for t in threads):
                        # Jika semua thread mati tetapi kita belum selesai, mungkin ada error.
                        break
                    continue

            # --- Logika Penghentian yang Bersih ---
            if stop_requested and stop_requested():
                print("Stop requested detected. Cleaning up threads and queues...")
                # Kosongkan task_queue dan kirim sinyal 'None' ke worker
                while not task_queue.empty():
                    try: task_queue.get_nowait()
                    except queue.Empty: break
                task_queue.queue.clear()
            
            # Kirim sinyal 'None' hanya jika belum dikirim (misal, jika loop selesai secara normal)
            for _ in range(final_num_workers):
                task_queue.put(None) 
                
            # Tunggu semua thread selesai
            for i, thread in enumerate(threads):
                thread.join(timeout=2.0)
                if thread.is_alive():
                    print(f"Warning: Worker thread {i} did not terminate gracefully.")

            # --- LANGKAH 5: Normalisasi Akhir ---
            if stop_requested and stop_requested():
                return (None, None, 0, []) if weight_of_each_image else (None, None, 0)

            if processed_frames_spatial > 0:
                try:
                    final_image_sum = final_image_sum_full_res
                    weight_map_sum = weight_map_sum_full_res.astype(np.float32)
                    
                    valid_pixels = weight_map_sum > 1e-6
                    weight_map_sum_3d = weight_map_sum[:, :, np.newaxis]
                    final_image = np.zeros_like(final_image_sum, dtype=np.float32)
                    
                    np.divide(final_image_sum.astype(np.float32), 
                            weight_map_sum_3d, 
                            out=final_image, 
                            where=valid_pixels[:, :, np.newaxis])
                    
                    if weight_of_each_image:
                        print("Warning: weight_of_each_image=True tidak didukung penuh oleh pipeline baru.")
                        return (final_image, weight_map_sum, processed_frames_spatial, [])
                    else:
                        return (final_image, weight_map_sum, processed_frames_spatial)

                except Exception as e:
                    raise RuntimeError(f"Normalization failed: {e}")
            
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
        
        finally:
            # --- BLOK PEMBERSIHAN YANG DIJAMIN ---
            
            if 'threads' in locals(): del threads
            if 'task_queue' in locals(): del task_queue
            if 'result_queue' in locals(): del result_queue
            if 'ref_work_res_pass2' in locals(): del ref_work_res_pass2
            if 'stability_map_work_res' in locals(): del stability_map_work_res
            if 'base_window' in locals(): del base_window
            if 'final_image_sum_full_res' in locals(): del final_image_sum_full_res
            if 'weight_map_sum_full_res' in locals(): del weight_map_sum_full_res

            gc.collect()
            gc.collect()
            
    def _frequency_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                        reference_image_float,
                        freq_c_wiener_factor,
                        freq_tile_size,
                        freq_overlap_percent,
                        update_progress=None, stop_requested=None,
                        total_overall_images=None, images_processed_so_far=0,
                        lib_path='UI/data/similarity_frequency_merging.dll',
                        refinement_algorithm='none',
                        optical_flows=None,
                        temporal_consistency=True,
                        save_temporal_std_path=None,
                        weight_of_each_image=False,
                        **unused_kwargs):

        if not images:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
        
        num_images = len(images)
        if num_images == 0:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
        
        tile_h, tile_w = map(int, freq_tile_size)
        step_y = max(int(tile_h * (1 - freq_overlap_percent)), 1)
        step_x = max(int(tile_w * (1 - freq_overlap_percent)), 1)
        progress_cap_percent = 95
        
        c_interface = None
        
        def compute_starts(ref_size, tile_size, step_size):
            if ref_size >= tile_size:
                starts_temp = np.arange(0, ref_size - tile_size + 1, step_size)
                if ref_size > tile_size and (starts_temp.size == 0 or starts_temp[-1] != ref_size - tile_size):
                    starts_list = np.append(starts_temp, ref_size - tile_size)
                elif ref_size == tile_size:
                    starts_list = np.array([0])
                else:
                    starts_list = starts_temp
            else:
                starts_list = np.array([0])
            
            return np.ascontiguousarray(np.unique(starts_list.astype(np.int32)))
        
        row_starts = compute_starts(ref_image_h, tile_h, step_y)
        col_starts = compute_starts(ref_image_w, tile_w, step_x)
        
        final_image_sum = np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32, order='C')
        weight_map_sum = np.zeros((ref_image_h, ref_image_w), dtype=np.float32, order='C')
        
        base_window = gaussian_window(freq_tile_size)
        
        first_image = images[0]
        if not isinstance(first_image, np.ndarray):
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
            
        orig_h, orig_w = first_image.shape[:2]
        
        valid_images = []
        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray): continue
            if (image_orig.shape[0] != orig_h or image_orig.shape[1] != orig_w or image_orig.dtype != ref_dtype): continue
            num_ch_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
            if num_ch_orig not in (1, 3): continue
            valid_images.append((i, image_orig))
        
        if not valid_images:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
        
        try:
            c_interface = SimilarityFrequencyInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal C++ interface _frequency_merging: {e}")
        
        if temporal_consistency: weight_maps_all = []
        if weight_of_each_image: weight_maps_per_image = []

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
                    msg_val = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_img_overall, total_overall_images)
                else:
                    prog_val = int((idx + 1) * progress_factor)
                    msg_val = language_config.ANALYZING_IMAGE.format(idx + 1, len(valid_images))
                update_progress(prog_val, msg_val)
            
            if stop_requested and stop_requested(): break
            
            try:
                current_image_float = normalize_image(image_orig, ref_dtype)
                if current_image_float.shape[2] != ref_channels_buffer: continue
            except Exception: continue
            
            weight_map_sum_before_this_frame = weight_map_sum.copy()
            
            try:
                c_interface.call_accumulate_frame_weighted(
                    c_interface.clib, final_image_sum, weight_map_sum,
                    current_image_float, reference_image_float, base_window,
                    row_starts, col_starts, tile_h, tile_w, ref_image_h, ref_image_w,
                    ref_channels_buffer, block_h_cxx, block_w_cxx, freq_c_wiener_factor
                )
                
                temp_weight_map = weight_map_sum - weight_map_sum_before_this_frame

                map_for_refinement = temp_weight_map

                # Lakukan penyempurnaan (refinement) menggunakan peta bobot yang sudah dipilih
                if refinement_algorithm == 'optical_flow' and optical_flows is not None and original_idx < len(optical_flows):
                    if accumulated_weight_map is None:
                        refined_weight = map_for_refinement
                    else:
                        pass
                        # refined_weight = ml_driven_refinement(map_for_refinement, accumulated_weight_map, optical_flows[original_idx])
                    accumulated_weight_map = refined_weight.copy()
                elif refinement_algorithm == 'standard':
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
                print(f"Warning: C++ accumulation failed for frame {original_idx+1}: {e_cxx}")
                continue
        
        if processed_frames_freq > 0:
            try:
                c_interface.call_normalize_accumulated(c_interface.clib, final_image_sum, weight_map_sum, ref_image_h, ref_image_w, ref_channels_buffer)
                
                # --- [DINONAKTIFKAN SEMENTARA] ---
                # if temporal_consistency:
                #     temporal_consistency_refinement(weight_maps_all, weight_map_sum, save_temporal_std_path=save_temporal_std_path)
                
                return (final_image_sum, weight_map_sum, processed_frames_freq, weight_maps_per_image) if weight_of_each_image else (final_image_sum, weight_map_sum, processed_frames_freq)

            except Exception as e_norm:
                raise RuntimeError(f"{language_config.NORMALIZATION_FAILED.format(e_norm)} (frequency merging)")
        else:
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)       
                 
    def similarity_mnfr(self, images,
                    merging_type='spatial',
                    tile_size=None, overlap=None,
                    motion_sensitivity=None, noise_offset_factor=None,
                    update_progress=None, stop_requested=None,
                    save_weight_map_path=None, num_workers=None,
                    total_overall_images=None, images_processed_so_far=0, 
                    save_temporal_std_path=None,
                    weight_of_each_image=False, 
                    **merging_kwargs):
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
                ref_image.shape[0], ref_image.shape[1],
                (ref_image.shape[2] if ref_image.ndim == 3 else 1)
            )
            dtype_ref = ref_image.dtype
            if channels_ref_orig not in (1, 3):
                raise ValueError(language_config.IMAGE_CHANNEL_DOES_NOT_SUPPORT.format(channels_ref_orig))

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
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

        # --- Jalankan merging berdasarkan type ---
        results = None
        if merging_type == 'spatial':
            current_tile_size = tile_size if tile_size is not None else common_call_args.get('tile_size')
            current_overlap = overlap if overlap is not None else common_call_args.get('overlap')
            current_motion_sensitivity = motion_sensitivity if motion_sensitivity is not None else common_call_args.get('motion_sensitivity')
            current_noise_offset_factor = noise_offset_factor if noise_offset_factor is not None else common_call_args.get('noise_offset_factor')
            current_num_workers = num_workers if num_workers is not None else common_call_args.get('similarity_spatial_num_workers')

            # Jika parameter penting belum tersedia, hentikan aman
            if any(p is None for p in [current_tile_size, current_overlap, current_motion_sensitivity, current_noise_offset_factor]):
                out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
                return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

            common_call_args.update({
                "tile_size": current_tile_size,
                "overlap": current_overlap,
                "motion_sensitivity": current_motion_sensitivity,
                "noise_offset_factor": current_noise_offset_factor,
                "num_workers": current_num_workers,
                "temporal_consistency": True,
                "save_temporal_std_path": save_temporal_std_path
            })
            results = self._spatial_merging(**common_call_args)

        elif merging_type == 'frequency':
            default_freq_tile_val, default_freq_overlap, default_freq_c_wiener = 24, 0.20, 5.0
            default_freq_lib_path = common_call_args.get('lib_path_freq', common_call_args.get('lib_path', 'UI/data/similarity_frequency_merging.dll'))
            current_freq_c_wiener = common_call_args.get('freq_c_wiener_factor', default_freq_c_wiener)
            current_freq_tile_size_input = common_call_args.get('freq_tile_size', default_freq_tile_val)
            current_freq_overlap = common_call_args.get('freq_overlap_percent', default_freq_overlap)

            if isinstance(current_freq_tile_size_input, int):
                current_freq_tile_size_tuple = (current_freq_tile_size_input, current_freq_tile_size_input)
            elif isinstance(current_freq_tile_size_input, (list, tuple)) and len(current_freq_tile_size_input) == 2:
                current_freq_tile_size_tuple = tuple(map(int, current_freq_tile_size_input))
            else:
                current_freq_tile_size_tuple = (default_freq_tile_val, default_freq_tile_val)

            common_call_args.update({
                "freq_c_wiener_factor": current_freq_c_wiener,
                "freq_tile_size": current_freq_tile_size_tuple,
                "freq_overlap_percent": current_freq_overlap,
                "lib_path": default_freq_lib_path,
                # "num_workers": current_num_workers,
                "temporal_consistency": True,
                "save_temporal_std_path": save_temporal_std_path
            })

            # Hapus parameter spatial agar tidak kacau
            for key_to_remove in ['tile_size', 'overlap', 'motion_sensitivity', 'noise_offset_factor']:
                common_call_args.pop(key_to_remove, None)

            results = self._frequency_merging(**common_call_args)

        else:
            raise ValueError(f"Unsupported merging_type: {merging_type}. Choose 'spatial' or 'frequency'.")

        # --- Jika tidak ada hasil karena stop_requested() ---
        if results is None:
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

        # --- Unpack results aman ---
        if weight_of_each_image:
            final_image_normalized, final_weight_map, processed_frames, individual_maps = results
        else:
            final_image_normalized, final_weight_map, processed_frames = results
            individual_maps = []

        # --- Stop_requested setelah proses tapi sebelum semua frame selesai ---
        if stop_requested and stop_requested() and (processed_frames is None or processed_frames < len(images)):
            processed_frames = 0 if processed_frames is None else processed_frames
            all_final_weight_maps_to_return = individual_maps
            final_img_output = np.zeros((h_ref, w_ref, channels_ref_orig), dtype=dtype_ref) if final_image_normalized is None else final_image_normalized
            return final_img_output, final_weight_map, all_final_weight_maps_to_return

        # --- Finalisasi output ---
        if processed_frames > 0 and final_image_normalized is not None:
            all_final_weight_maps_to_return = individual_maps

            # Simpan weight map jika diminta
            if save_weight_map_path and final_weight_map is not None:
                try:
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    max_w = np.max(final_weight_map)
                    norm_w_vis = final_weight_map / max_w if max_w > 1e-6 else np.zeros_like(final_weight_map)
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
            final_img_output = np.clip(final_img_out_ch, min_v, max_v).astype(dtype_ref, copy=False)

            return final_img_output, final_weight_map, all_final_weight_maps_to_return

        else:
            # Jika tidak ada frame diproses
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []


def _setup_data_source_and_paths(db_path, single_process, batch_id, image_processor):
    align_dir = os.path.join("database", "align")
    image_paths = []
    output_name_base = ""
    hdf5_path = ""

    if single_process:
        hdf5_path = os.path.join(align_dir, "aligned_images.h5")
        image_paths = get_all_image_paths_for_single_process(db_path)
        ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else "single_process"
        output_name_base = ref_name
    else:
        if batch_id is None:
            pass
        hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
        image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
        ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else f"batch_{batch_id}"
        output_name_base = ref_name

    data_source = hdf5_path if os.path.exists(hdf5_path) else image_paths
    
    total_images = 0
    if isinstance(data_source, str) and data_source.endswith('.h5'):
        print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(data_source))
        try:
            with h5py.File(data_source, 'r') as f:
                total_images = len(f.keys())
        except Exception as e_h5:
            raise IOError(f"Gagal membaca file HDF5: {e_h5}")
    elif isinstance(data_source, list):
        total_images = len(data_source)

    return data_source, image_paths, output_name_base, total_images

def _load_images_for_batch(data_source, batch_indices, stop_requested=None):
    batch_start, batch_end = batch_indices
    batch_images = []
    
    if isinstance(data_source, str) and data_source.endswith('.h5'):
        with h5py.File(data_source, 'r') as h5f:
            keys = list(h5f.keys())[batch_start:batch_end]
            batch_images = [np.array(h5f[key]) for key in keys if not (stop_requested and stop_requested())]
    elif isinstance(data_source, list):
        batch_paths = data_source[batch_start:batch_end]
        batch_images = load_images_from_paths(batch_paths, stop_requested)
        if 'resize_all_with_padding' in globals():
            batch_images, _ = resize_all_with_padding(batch_images, method="median")
            
    return batch_images

def main(db_path, update_progress=None, stop_requested=None,
         single_process=None, batch_id=None, save_final_weight_map=False,
         progress_bar=None):
    try:
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        # --- 1. KONFIGURASI SPESIFIK UNTUK PROSES SIMILARITY ---
        general_settings = load_similarity_config()
        image_processor = SimilarityAlgorithm(db_path) 

        merging_type_from_settings = general_settings.get("similarity_merging_type", "spatial")
        spatial_tile_size_arg, spatial_overlap_arg, spatial_motion_sensitivity_arg, spatial_noise_offset_factor_arg = None, None, None, None
        extra_merging_params = {}

        if merging_type_from_settings == 'spatial':
            tile_val_sp = general_settings.get("similarity_spatial_tile_size", 24)
            spatial_tile_size_arg = (tile_val_sp, tile_val_sp) 
            spatial_overlap_arg = general_settings.get("similarity_spatial_overlap_percent", 0.6)
            spatial_motion_sensitivity_arg = general_settings.get("similarity_spatial_motion_sensitivity", 110.0)
            spatial_noise_offset_factor_arg = general_settings.get("similarity_spatial_noise_mad_offset_factor", 0.3)
            extra_merging_params['similarity_spatial_num_workers'] = general_settings.get("similarity_spatial_num_workers", -1) # Default -1 (Auto)
            custom_lib_path = general_settings.get("similarity_lib_path") 
            if custom_lib_path: extra_merging_params['lib_path'] = custom_lib_path
        
        elif merging_type_from_settings == 'frequency':
            extra_merging_params['freq_c_wiener_factor'] = general_settings.get("similarity_frequency_c_wiener_factor", 5.0)
            tile_val_fq = general_settings.get("similarity_frequency_tile_size", 16)
            extra_merging_params['freq_tile_size'] = tile_val_fq 
            extra_merging_params['freq_overlap_percent'] = general_settings.get("similarity_frequency_overlap_percent", 0.25)
            # extra_merging_params['num_workers'] = general_settings.get("similarity_spatial_num_workers", 2)
        
        # --- 2. SETUP SUMBER DATA & PATH (MENGGUNAKAN HELPER) ---
        data_source, image_paths, output_name_base, total_images = \
            _setup_data_source_and_paths(db_path, single_process, batch_id, image_processor)

        if not total_images:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE); 
            return

        metadata_output_path = os.path.join("database", "align", "metadata.json")
        try:
            extract_all_metadata(image_paths, metadata_file=metadata_output_path)
        except Exception as e:
            pass 
        
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip() or "stack_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_{merging_type_from_settings}.tif")
        weight_map_output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_{merging_type_from_settings}_weight_map.png")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map: print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))
        
        # --- 4. PERENCANAAN BATCH (UMUM) ---
        batch_plan = setup_balanced_batching(total_images, language_config)
        if not batch_plan:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE)
            return
        total_batches = len(batch_plan)

        # --- 5. PROSES INTI PER BATCH ---
        processed_batches_results = []
        images_processed_count = 0

        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break
            
            print(f"\n{language_config.PROCESSING_BATCH.format(batch_num, total_batches, batch_start)}")

            batch_images_list = _load_images_for_batch(data_source, (batch_start, batch_end), stop_requested)

            if stop_requested and stop_requested(): break
            if not batch_images_list:
                print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(batch_num))
                continue

            batch_result_img, _, _ = image_processor.similarity_mnfr(
                images=batch_images_list, merging_type=merging_type_from_settings,
                tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                update_progress=update_progress, stop_requested=stop_requested,
                total_overall_images=total_images, images_processed_so_far=images_processed_count,
                weight_of_each_image=False, # Tidak lagi membutuhkan peta bobot individual
                **extra_merging_params
            )
            
            if stop_requested and stop_requested(): break
            
            if batch_result_img is not None:
                processed_batches_results.append(batch_result_img)
                images_processed_count += len(batch_images_list)

        if stop_requested and stop_requested():
            if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses Dibatalkan.")
            return

        # --- 6. PENGGABUNGAN AKHIR / FINE-TUNING ---
        final_result_img = None
        if processed_batches_results:
            
            # Panggil fungsi resize_all_with_padding pada hasil-hasil batch
            processed_batches_results, final_shape = resize_all_with_padding(
                processed_batches_results, 
                method="median" # 'median' atau 'max' biasanya pilihan yang aman di sini
            )
            print(f"Semua hasil batch disesuaikan ke ukuran target: {final_shape}")
            # --- AKHIR PENAMBAHAN KODE ---

            if len(processed_batches_results) > 1:
                fine_tuning_start_progress, fine_tuning_end_progress = 95, 99
                def fine_tuning_update_progress(inner_progress, message):
                    mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                    if update_progress and not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))
                
                if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)
                
                final_result_img, _, _ = image_processor.similarity_mnfr(
                    images=processed_batches_results, merging_type=merging_type_from_settings,
                    tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                    motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                    update_progress=fine_tuning_update_progress, stop_requested=stop_requested,
                    save_weight_map_path=(weight_map_output_path if save_final_weight_map else None),
                    total_overall_images=len(processed_batches_results), images_processed_so_far=0,
                    weight_of_each_image=False,
                    **extra_merging_params
                )
            else:
                final_result_img = processed_batches_results[0]
        
        # --- 7. PENYIMPANAN HASIL AKHIR & PEMBERSIHAN ---
        if final_result_img is not None:
            ref_path_for_save = image_paths[0] if image_paths else None
            save_success = save_image(final_result_img, output_path, reference_image_path=ref_path_for_save)
            
            final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}" if save_success \
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            if update_progress: update_progress(100, final_message)

            if not single_process and batch_id is not None:
                hdf5_path = os.path.join("database", "align", f"aligned_image_batch_{batch_id}.h5")
                if os.path.exists(hdf5_path):
                    try: os.remove(hdf5_path)
                    except OSError as e: print(f"Error removing temp file: {e}")
        else:
            if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

    # --- 8. PENANGANAN ERROR (UMUM) ---
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)
            
def running_similarity(parent=None, single_process=None, batch_id=None, progress_callback=None):
    
    # ==========================================================
    # KONDISI 1: MODE BATCH (TANPA GUI)
    # ==========================================================
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                single_process=False, 
                batch_id=batch_id
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
        Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint |
        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
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
    worker = ThreadWorker("pixel_refine_database.db", single_process=single_process, batch_id=batch_id)
    progress_bar_instance = progress_bar  # Pass progress_bar to main
    # Menghubungkan signal worker ke fungsi pembaruan UI
    worker.progress_updated.connect(lambda progress, message: (
        progress_bar.setValue(progress),
        label.setText(message)
    ))

    def finish_handler():
        nonlocal process_finished
        process_finished = True  
        dialog.close()
        worker.quit()  
        worker.wait()  

    worker.finished.connect(finish_handler)

    def error_handler(error):
        QMessageBox.critical(dialog, "Error", language_config.RUN_ERROR_STATUS.format(error=error))
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        # Jika proses telah selesai, lewati konfirmasi
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(dialog, "Cancel Process",
                                        language_config.CANCEL_PROCESSING,
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
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
    main("pixel_refine_database.db", update_progress=worker.progress_updated.emit, stop_requested=worker.stop_requested, progress_bar=progress_bar_instance)
    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)