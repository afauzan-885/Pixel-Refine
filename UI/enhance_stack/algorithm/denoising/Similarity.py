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
                                                                                    normalize_image, optical_flow_refinement, resize_all_with_padding, save_image, setup_balanced_batching, 
                                                                                    standard_refinement, temporal_consistency_refinement)
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityFrequencyInterface, SimilaritySpatialInterface
# from UI.enhance_stack.algorithm.model_trainer.mobile_net_v2 import AlphaGenerator
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
    def __init__(self, db_path, hdf5_path=None, 
                 ml_model_path="path/to/your/model.pt"):
        self.db_path = db_path
        self.knowledge_model = None
        self.is_model_loaded = False
        self.model_type = None
        self.smart_alpha_generator = None
        # try:
        #     # Muat model hanya jika path diberikan dan valid
        #     if ml_model_path and os.path.exists(ml_model_path):
        #         # print(f"Memuat model Smart Alpha Generator dari: {ml_model_path}")
        #         self.smart_alpha_generator = AlphaGenerator(model_path=ml_model_path)
        #     else:
        #         print("PERINGATAN: Path model ML tidak valid atau tidak ada. Refinement ML akan dinonaktifkan.")
        # except Exception as e:
        #     print(f"ERROR: Gagal memuat model ML. Refinement ML dinonaktifkan. Kesalahan: {e}")
        #     self.smart_alpha_generator = None
            
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

    def load_images_from_hdf5(self, hdf5_path, stop_requested=None):
        images = []
        with h5py.File(hdf5_path, 'r') as h5f:
            for key in h5f.keys():
                if stop_requested and stop_requested():
                    break
                image = np.array(h5f[key])
                images.append(image)
        return images
    
    def _load_knowledge_model(self):
        """ 
        (VERSI SIMULASI) 
        Mensimulasikan pemuatan model. Tidak ada model AI yang dimuat dari disk.
        Menyiapkan kerangka untuk pemuatan model di masa depan.
        """
        print("\nModel Loader: [Simulasi] Pemuatan model AI diaktifkan.")
        
        # --- Logika Simulasi ---
        # Atur flag ini ke True agar bagian lain dari kode berpikir model sudah dimuat.
        self.knowledge_model = {} # Kosongkan karena tidak ada model nyata
        self.model_type = 'simulation' # Tandai bahwa ini adalah mode simulasi
        self.is_model_loaded = True
        print("  -> SUKSES: Mode simulasi model AI siap.")
        return True


    def _apply_knowledge_model(self, weight_map, blending_factor=0.7):
        """
        (VERSI SIMULASI) 
        Mensimulasikan penerapan model pada peta bobot. 
        Fungsi ini hanya akan mengembalikan peta bobot asli tanpa perubahan.
        """
        # Guard clause ini tetap berguna untuk memeriksa apakah _load_knowledge_model berhasil (atau disimulasikan berhasil).
        if not self.is_model_loaded:
            return weight_map
            
        # --- Logika Simulasi ---
        # Hanya cetak pesan dan langsung kembalikan input asli.
        print("  -> [Simulasi] Menerapkan model pengetahuan... (melewatkan proses AI)") # Uncomment untuk log yang lebih detail
        return weight_map
    
    def _create_weight_map_heatmap(self, float_map, labels=("Static (High Weight)", "Moving (Low Weight)")):
        """
        Mengubah peta bobot float 2D menjadi gambar heatmap BGR berwarna,
        dengan warna yang benar (tinggi=biru, rendah=merah) dan legenda.
        
        Ini meniru logika pembuatan heatmap temporal_std secara persis.
        """
        min_val, max_val = np.min(float_map), np.max(float_map)
        if max_val - min_val < 1e-8:
            return np.zeros((float_map.shape[0], float_map.shape[1], 3), dtype=np.uint8)

        # 1. Normalisasi peta bobot ke rentang [0, 1]
        norm_map = (float_map - min_val) / (max_val - min_val) 
        inverted_norm_map = 1.0 - norm_map
        
        # 2. Skalakan ke [0, 255] dan ubah tipe data menjadi uint8
        uint8_gray_map = (inverted_norm_map * 255).astype(np.uint8)
        
        # 3. Terapkan colormap (misalnya JET) untuk membuat gambar berwarna
        heatmap_color = cv2.applyColorMap(uint8_gray_map, cv2.COLORMAP_JET)
        
        heatmap_with_legend = add_legend_heatmap(
            heatmap_color,
            norm_values=inverted_norm_map,
            labels=labels
        )
        
        return heatmap_with_legend

    def _spatial_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                    reference_image_float, tile_size, overlap,
                    motion_sensitivity, noise_offset_factor,
                    refinement_algorithm='optical_flow',
                    optical_flows=None,
                    update_progress=None, stop_requested=None,
                    total_overall_images=None, images_processed_so_far=0,
                    lib_path='UI/data/similarity_spatial_merging.dll',
                    temporal_consistency=True,
                    save_temporal_std_path=None,
                    weight_of_each_image=False,
                    collect_raw_maps_for_learning=False,
                    use_ai_reconstruction=False,
                    temporal_analysis_mode='two_pass_full', # Opsi: 'one_pass', 'two_pass_full'
                    **unused_kwargs):

        # --- LANGKAH 1: Inisialisasi dan Penentuan Resolusi Kerja ---
        tile_h, tile_w = map(int, tile_size)
        try:
            c_interface = SimilaritySpatialInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal memuat C++ interface_spatial_merging: {e}")
        num_images = len(images)
        orig_h, orig_w = images[0].shape[:2]

        work_res_h, work_res_w = ref_image_h, ref_image_w
        TARGET_MP = 12 * 1e6
        if (ref_image_h * ref_image_w) > TARGET_MP:
            scale_factor = np.sqrt(TARGET_MP / (ref_image_h * ref_image_w))
            work_res_h, work_res_w = int(ref_image_h * scale_factor), int(ref_image_w * scale_factor)
        else:
            work_res_h, work_res_w = int(ref_image_h * 0.7), int(ref_image_w * 0.7)
        work_res_h, work_res_w = (work_res_h // 2) * 2, (work_res_w // 2) * 2
        
        # Gunakan ukuran tile asli untuk keandalan
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

        # ====================================================================================
        # === LANGKAH 2 (PASS 1): Membuat Peta Stabilitas ==================================
        # ====================================================================================
        stability_map = None
        if temporal_analysis_mode == 'two_pass_full':
            if update_progress:
                update_progress(5, "Pass 1/2: Menganalisis stabilitas adegan...")
            
            downsampled_h, downsampled_w = work_res_h // 2, work_res_w // 2
            sum_map = np.zeros((downsampled_h, downsampled_w), dtype=np.float32)
            sum_sq_map = np.zeros((downsampled_h, downsampled_w), dtype=np.float32)
            frame_count = 0
            
            ref_work_res = cv2.resize(reference_image_float, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)

            for i, image_orig in enumerate(images):
                if stop_requested and stop_requested(): return (None, None, 0)
                if update_progress:
                    update_progress(int(5 + ((i + 1) / num_images) * 45), f"Pass 1/2: Menganalisis frame {i+1}/{num_images}")
                
                curr_work_res = cv2.resize(normalize_image(image_orig, ref_dtype), (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
                temp_weight_map = np.ascontiguousarray(np.zeros((work_res_h, work_res_w), dtype=np.float32))
                dummy_image_sum = np.ascontiguousarray(np.zeros((work_res_h, work_res_w, ref_channels_buffer), dtype=np.float32))
                
                c_interface.call_accumulate_frame_weighted(
                    final_image_sum=dummy_image_sum, weight_map_sum=temp_weight_map,
                    current_image=curr_work_res, reference_image=ref_work_res, base_window=base_window,
                    stability_map=None, row_starts=row_starts, col_starts=col_starts,
                    tile_h=tile_h, tile_w=tile_w, h=work_res_h, w=work_res_w, channels=ref_channels_buffer,
                    block_h=tile_h, block_w=tile_w, search_radius=0,
                    motion_sensitivity=motion_sensitivity, noise_offset_factor=noise_offset_factor
                )
                
                downsampled_map = cv2.resize(temp_weight_map, (downsampled_w, downsampled_h), interpolation=cv2.INTER_AREA)
                sum_map += downsampled_map
                sum_sq_map += np.square(downsampled_map)
                frame_count += 1
                del temp_weight_map, dummy_image_sum, curr_work_res, downsampled_map

            if frame_count >= 2:
                N = float(frame_count)
                mean_map = sum_map / N
                variance_map = (sum_sq_map / N) - np.square(mean_map)
                variance_map[variance_map < 0] = 0 
                std_weights_low_res = np.sqrt(variance_map)
                max_std = np.max(std_weights_low_res)
                stability_map_low_res = 1.0 - (std_weights_low_res / (max_std + 1e-6))
                stability_map_full_res = cv2.resize(stability_map_low_res.astype(np.float32), (ref_image_w, ref_image_h), interpolation=cv2.INTER_CUBIC)
                stability_map = np.ascontiguousarray(np.clip(stability_map_full_res**2.0, 0.0, 1.0).astype(np.float32))
            
            del sum_map, sum_sq_map

        # =================================================================================
        # === LANGKAH 3 (PASS 2 / UTAMA): Akumulasi Final Terpandu ========================
        # =================================================================================
        msg_pass = "Pass 2/2: " if temporal_analysis_mode != 'one_pass' else ""
        if update_progress:
            update_progress(50, f"{msg_pass}Menggabungkan frame...")

        final_image_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w), dtype=np.float32))
        
        # Inisialisasi lain
        processed_frames_spatial = 0
        progress_cap_percent = 95
        if temporal_consistency: weight_maps_all = []
        if weight_of_each_image: weight_maps_per_image = []
        accumulated_weight_map, prev_weight_map_for_standard = None, None
        use_ai_reconstruction = use_ai_reconstruction and hasattr(self, 'is_model_loaded') and self.is_model_loaded
        use_ml_refinement = (refinement_algorithm == 'ml_driven' and hasattr(self, 'smart_alpha_generator') and self.smart_alpha_generator is not None)
        if refinement_algorithm == 'ml_driven' and not use_ml_refinement:
            refinement_algorithm = 'optical_flow'

        ref_work_res_pass2 = cv2.resize(reference_image_float, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
        stability_map_work_res = None
        if stability_map is not None:
            stability_map_work_res = cv2.resize(stability_map, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)

        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray): continue
            if update_progress:
                current_img_overall = images_processed_so_far + i + 1
                prog = int(50 + ((current_img_overall / total_overall_images) * (progress_cap_percent - 50) if total_overall_images and total_overall_images > 0 else ((i + 1) / num_images) * (progress_cap_percent - 50)))
                msg_pass_str = "Pass 2/2: " if temporal_analysis_mode != 'one_pass' else ""
                msg = f"{msg_pass_str}Membangun gambar frame {i+1}/{num_images}"
                update_progress(prog, msg)
            if stop_requested and stop_requested(): break
        
            curr_work_res_pass2 = cv2.resize(normalize_image(image_orig, ref_dtype), (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)

            try:
                temp_weight_map_work_res = np.ascontiguousarray(np.zeros((work_res_h, work_res_w), dtype=np.float32))
                # BUAT BUFFER DUMMY KARENA C++ TIDAK MELAKUKAN AKUMULASI GAMBAR FINAL DI SINI
                dummy_final_sum_work_res = np.ascontiguousarray(np.zeros((work_res_h, work_res_w, ref_channels_buffer), dtype=np.float32))

                # Panggil C++ untuk mendapatkan peta bobot yang sudah dipandu oleh `stability_map`
                c_interface.call_accumulate_frame_weighted(
                    final_image_sum=dummy_final_sum_work_res, 
                    weight_map_sum=temp_weight_map_work_res,
                    current_image=curr_work_res_pass2, reference_image=ref_work_res_pass2, base_window=base_window,
                    stability_map=stability_map_work_res, row_starts=row_starts, col_starts=col_starts,
                    tile_h=tile_h, tile_w=tile_w, h=work_res_h, w=work_res_w, channels=ref_channels_buffer,
                    block_h=tile_h, block_w=tile_w, search_radius=0,
                    motion_sensitivity=motion_sensitivity, noise_offset_factor=noise_offset_factor
                )
                
                temp_weight_map_full_res = cv2.resize(temp_weight_map_work_res, (ref_image_w, ref_image_h), interpolation=cv2.INTER_CUBIC)

                map_for_refinement = temp_weight_map_full_res
                if use_ai_reconstruction:
                    map_for_refinement = self._apply_knowledge_model(temp_weight_map_full_res)
                
                refined_weight = map_for_refinement
                if optical_flows is not None and i < len(optical_flows):
                    if accumulated_weight_map is not None:
                        current_flow, current_confidence = (optical_flows[i] if isinstance(optical_flows[i], tuple) else (optical_flows[i], None))
                        if use_ml_refinement:
                            refined_weight = map_for_refinement
                        elif refinement_algorithm == 'optical_flow':
                            refined_weight = optical_flow_refinement(map_for_refinement, accumulated_weight_map, current_flow, current_confidence)
                        elif refinement_algorithm == 'standard':
                            refined_weight = standard_refinement(map_for_refinement, prev_weight_map_for_standard, reference_image_float)
                            prev_weight_map_for_standard = refined_weight.copy()
                else:
                    refined_weight = map_for_refinement

                # Akumulasi final dilakukan pada buffer resolusi penuh
                weight_map_sum += refined_weight
                final_image_sum += normalize_image(image_orig, ref_dtype) * refined_weight[:, :, np.newaxis]
                
                if weight_of_each_image:
                    if collect_raw_maps_for_learning:
                        weight_maps_per_image.append(temp_weight_map_full_res.copy())
                    else:
                        weight_maps_per_image.append(refined_weight.copy())
                if temporal_consistency:
                    weight_maps_all.append(refined_weight.copy())
                processed_frames_spatial += 1
            except Exception as e:
                raise RuntimeError(f"C++ accumulation frame {i+1} spatial: {e}")

        # --- LANGKAH 5: Normalisasi Final di Python ---
        if processed_frames_spatial > 0:
            try:
                valid_pixels = weight_map_sum > 1e-6
                weight_map_sum_3d = weight_map_sum[:, :, np.newaxis]
                final_image = np.zeros_like(final_image_sum)
                np.divide(final_image_sum, weight_map_sum_3d, out=final_image, where=valid_pixels[:, :, np.newaxis])
                
                if temporal_consistency:
                    temporal_consistency_refinement(weight_maps_all, weight_map_sum, save_temporal_std_path=save_temporal_std_path)
                
                return (final_image, weight_map_sum, processed_frames_spatial, weight_maps_per_image) if weight_of_each_image else (final_image, weight_map_sum, processed_frames_spatial)
            except Exception as e:
                raise RuntimeError(f"Normalization failed: {e}")
        
        return (None, None, 0, []) if weight_of_each_image else (None, None, 0)
    
    def _frequency_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                        reference_image_float,
                        freq_c_wiener_factor,
                        freq_tile_size,
                        freq_overlap_percent,
                        update_progress=None, stop_requested=None,
                        total_overall_images=None, images_processed_so_far=0,
                        lib_path='UI/data/similarity_frequency_merging.dll',
                        refinement_algorithm='optical_flow',
                        optical_flows=None,
                        temporal_consistency=True,
                        save_temporal_std_path=None,
                        weight_of_each_image=False,
                        collect_raw_maps_for_learning=False, 
                        # ### PERUBAHAN: Parameter baru ditambahkan ###
                        use_ai_reconstruction=False,
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
        
        if use_ai_reconstruction:
            if self.is_model_loaded:
                print("  -> Mode Rekonstruksi AI untuk Peta Bobot diaktifkan.")
            else:
                print("  -> PERINGATAN: Rekonstruksi AI diminta, tetapi model tidak dimuat. Akan dilewati.")
                use_ai_reconstruction = False # Nonaktifkan jika model tidak ada

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
                if use_ai_reconstruction:
                    map_for_refinement = self._apply_knowledge_model(temp_weight_map)

                # Lakukan penyempurnaan (refinement) menggunakan peta bobot yang sudah dipilih
                if refinement_algorithm == 'optical_flow' and optical_flows is not None and original_idx < len(optical_flows):
                    if accumulated_weight_map is None:
                        refined_weight = map_for_refinement
                    else:
                        pass
                        # refined_weight = ml_driven_refinement(map_for_refinement, accumulated_weight_map, optical_flows[original_idx])
                    accumulated_weight_map = refined_weight.copy()
                elif refinement_algorithm == 'standard':
                    refined_weight = standard_refinement(map_for_refinement, prev_weight_map_for_standard, reference_image_float)
                    prev_weight_map_for_standard = refined_weight.copy()
                else:
                    refined_weight = map_for_refinement

                weight_map_sum = weight_map_sum_before_this_frame + refined_weight

                if weight_of_each_image:
                    if collect_raw_maps_for_learning:
                        weight_maps_per_image.append(temp_weight_map.copy()) 
                    else:
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
                if temporal_consistency:
                    temporal_consistency_refinement(weight_maps_all, weight_map_sum, save_temporal_std_path=save_temporal_std_path)
                
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
                save_weight_map_path=None, 
                total_overall_images=None, images_processed_so_far=0, 
                save_temporal_std_path= None #"database/stack.jpg",
                , weight_of_each_image=False, 
                collect_raw_maps_for_learning=False,
                use_learning_model=False,
                perform_learning=False,
                # ### PERUBAHAN: Parameter baru ditambahkan ###
                use_ai_reconstruction=False,
                **merging_kwargs):

        if not isinstance(images, list) or not images:
            raise ValueError(language_config.IMAGE_DATA_MUST_BE_VALID)
        try:
            ref_image = images[0]
            if not isinstance(ref_image, np.ndarray):
                raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)
            h_ref, w_ref, channels_ref_orig = ref_image.shape[0], ref_image.shape[1], (ref_image.shape[2] if ref_image.ndim == 3 else 1)
            dtype_ref = ref_image.dtype
            if channels_ref_orig not in (1, 3):
                raise ValueError(language_config.IMAGE_CHANNEL_DOES_NOT_SUPPORT.format(channels_ref_orig))
        except (AttributeError, IndexError, ValueError, TypeError) as e:
            raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))
        if dtype_ref not in (np.uint8, np.uint16):
            raise TypeError(language_config.IMAGE_BIT_REQUIRED)

        # <<< LOGIKA PEMBELAJARAN: Langkah 1 - Pemuatan Model & Persiapan >>>
        if (use_learning_model or use_ai_reconstruction) and not self.is_model_loaded:
            # print("Mode AI diaktifkan. Mencoba memuat model pengetahuan...")
            self._load_knowledge_model()
        
        channels_buffer = 3
        reference_image_float = normalize_image(ref_image, dtype_ref)
        h_ref_norm, w_ref_norm, _ = reference_image_float.shape
        
        final_image_normalized, final_weight_map, processed_frames = None, None, 0
        weight_maps_per_image = []

        common_call_args = {
            "images": images, "ref_image_h": h_ref_norm, "ref_image_w": w_ref_norm,
            "ref_channels_buffer": channels_buffer, "ref_dtype": dtype_ref,
            "reference_image_float": reference_image_float,
            "update_progress": update_progress, "stop_requested": stop_requested,
            "total_overall_images": total_overall_images, "images_processed_so_far": images_processed_so_far,
            "weight_of_each_image": weight_of_each_image,
            "collect_raw_maps_for_learning": collect_raw_maps_for_learning,
            # ### PERUBAHAN: Teruskan parameter rekonstruksi ###
            "use_ai_reconstruction": use_ai_reconstruction
        }
        common_call_args.update(merging_kwargs)
        
        if merging_type == 'spatial':
            current_tile_size = tile_size if tile_size is not None else common_call_args.get('tile_size')
            current_overlap = overlap if overlap is not None else common_call_args.get('overlap')
            current_motion_sensitivity = motion_sensitivity if motion_sensitivity is not None else common_call_args.get('motion_sensitivity')
            current_noise_offset_factor = noise_offset_factor if noise_offset_factor is not None else common_call_args.get('noise_offset_factor')
            
            if any(p is None for p in [current_tile_size, current_overlap, current_motion_sensitivity, current_noise_offset_factor]):
                if stop_requested and stop_requested():
                    return np.zeros((h_ref, w_ref, channels_ref_orig), dtype=dtype_ref), None, []
                # raise ValueError("Untuk spatial merging, tile_size, overlap, motion_sensitivity, dan noise_offset_factor harus disediakan.")

            common_call_args.update({
                "tile_size": current_tile_size, "overlap": current_overlap,
                "motion_sensitivity": current_motion_sensitivity, "noise_offset_factor": current_noise_offset_factor,
                "temporal_consistency": True, "save_temporal_std_path": save_temporal_std_path
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
            elif isinstance(current_freq_tile_size_input, (list,tuple)) and len(current_freq_tile_size_input) == 2:
                current_freq_tile_size_tuple = tuple(map(int,current_freq_tile_size_input))
            else:
                current_freq_tile_size_tuple = (default_freq_tile_val, default_freq_tile_val)

            common_call_args.update({
                "freq_c_wiener_factor": current_freq_c_wiener, "freq_tile_size": current_freq_tile_size_tuple,
                "freq_overlap_percent": current_freq_overlap, "lib_path": default_freq_lib_path,
                "temporal_consistency": True, "save_temporal_std_path": save_temporal_std_path
            })
            
            for key_to_remove in ['tile_size', 'overlap', 'motion_sensitivity', 'noise_offset_factor']:
                common_call_args.pop(key_to_remove, None)
            results = self._frequency_merging(**common_call_args)
        else:
            raise ValueError(f"Unsupported merging_type: {merging_type}. Choose 'spatial' or 'frequency'.")

        if weight_of_each_image:
            final_image_normalized, final_weight_map, processed_frames, individual_maps = results
        else:
            final_image_normalized, final_weight_map, processed_frames = results
            individual_maps = []

        # --- Bagian ini sekarang lebih bersih karena logika AI sudah dipindahkan ---
        if processed_frames > 0 and final_image_normalized is not None:
            
            all_final_weight_maps_to_return = []
            if individual_maps:
                # KASUS 1: Jika mode 'gunakan model' aktif, ini adalah saat di mana
                if use_learning_model and self.is_model_loaded:
                    # print(f"\n--- Menerapkan Pengetahuan Model (Final Pass) ---")
                    for i, w_map in enumerate(individual_maps):
                        final_w_map = self._apply_knowledge_model(w_map)
                        all_final_weight_maps_to_return.append(final_w_map)
                    # print("--- Penerapan Pengetahuan Selesai ---")
                else:
                    # KASUS 2: Jika tidak, teruskan saja hasil dari tahap merging.
                    all_final_weight_maps_to_return = individual_maps

            # Logika penyimpanan peta bobot (sekarang lebih sederhana)
            if save_weight_map_path and final_weight_map is not None:
                try:
                    max_w = np.max(final_weight_map)
                    norm_w_vis = final_weight_map / max_w if max_w > 1e-6 else np.zeros_like(final_weight_map)
                    w_map_vis = (np.clip(norm_w_vis, 0.0, 1.0) * 255).astype(np.uint8)
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    cv2.imwrite(save_weight_map_path, w_map_vis)
                except Exception as e:
                    # print(f"Error saat menyimpan peta bobot gabungan: {e}")
                    traceback.print_exc()

            if weight_of_each_image and save_weight_map_path and all_final_weight_maps_to_return and not perform_learning:
                # print(f"Mode Non-Pelatihan: Menyimpan {len(all_final_weight_maps_to_return)} peta bobot individual sebagai heatmap...")
                try:
                    base, ext = os.path.splitext(save_weight_map_path)
                    for i, w_map in enumerate(all_final_weight_maps_to_return):
                        individual_map_path = f"{base}_frame_{i}{ext}"
                        w_map_vis = self._create_weight_map_heatmap(w_map)
                        if not cv2.imwrite(individual_map_path, w_map_vis):
                            pass
                            # print(f"Gagal menyimpan peta bobot individual ke: {individual_map_path}")
                except Exception as e:
                    # print(f"Error saat menyimpan peta bobot individual: {e}")
                    traceback.print_exc()

            # --- Bagian 5: Finalisasi dan Return Value yang Konsisten ---
            scale_val = np.float32(np.iinfo(dtype_ref).max)
            final_img_scaled = final_image_normalized * scale_val
            
            if channels_ref_orig == 1:
                final_img_out_ch = np.mean(final_img_scaled, axis=2)
            else:
                final_img_out_ch = final_img_scaled
                
            min_v, max_v = 0, np.iinfo(dtype_ref).max
            final_img_output = np.clip(final_img_out_ch, min_v, max_v).astype(dtype_ref, copy=False)
            
            if stop_requested and stop_requested() and processed_frames < len(images):
                return final_img_output, final_weight_map, all_final_weight_maps_to_return
            
            # Selalu kembalikan TIGA nilai yang konsisten
            return final_img_output, final_weight_map, all_final_weight_maps_to_return

        else:
            # Jika tidak ada frame yang diproses
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            # print(f"Tidak ada frame yang diproses oleh {merging_type} merging. Mengembalikan nilai kosong.")
            
            # Kembalikan TIGA nilai yang konsisten
            return np.zeros(out_shape_fb, dtype=dtype_ref), None, []

def apply_temporal_filter(current_map, prev_smoothed_map, alpha=0.3):
    """Fungsi helper untuk menerapkan filter Exponential Moving Average (EMA)."""
    if prev_smoothed_map is None:
        return current_map.copy()
    return (alpha * current_map) + ((1.0 - alpha) * prev_smoothed_map)

def _setup_data_source_and_paths(db_path, single_process, batch_id, image_processor):
    """
    Menentukan sumber data (HDF5 atau list path), path gambar,
    nama dasar untuk file output, dan total gambar.
    """
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
            raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
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
        print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
        total_images = len(data_source)

    return data_source, image_paths, output_name_base, total_images

def _load_images_for_batch(data_source, batch_indices, stop_requested=None):
    """
    Memuat gambar untuk batch tertentu dari sumber data (HDF5 atau list path).
    """
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

# --- FUNGSI MAIN SIMILARITY YANG SUDAH DIREFAKTOR ---

def main(db_path, update_progress=None, stop_requested=None, batch_size=7,
         single_process=None, batch_id=None, save_final_weight_map=False,
         progress_bar=None):
    try:
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        # --- 1. KONFIGURASI SPESIFIK UNTUK PROSES SIMILARITY ---
        general_settings = load_similarity_config()
        perform_learning_setting = general_settings.get("perform_learning", False)
        use_learning_model_setting = general_settings.get("use_learning_model", False)

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
            custom_lib_path = general_settings.get("similarity_lib_path") 
            if custom_lib_path: extra_merging_params['lib_path'] = custom_lib_path
        elif merging_type_from_settings == 'frequency':
            extra_merging_params['freq_c_wiener_factor'] = general_settings.get("similarity_frequency_c_wiener_factor", 5.0)
            tile_val_fq = general_settings.get("similarity_frequency_tile_size", 16)
            extra_merging_params['freq_tile_size'] = tile_val_fq 
            extra_merging_params['freq_overlap_percent'] = general_settings.get("similarity_frequency_overlap_percent", 0.25)
        
        # --- 2. SETUP SUMBER DATA & PATH (MENGGUNAKAN HELPER) ---
        data_source, image_paths, output_name_base, total_images = \
            _setup_data_source_and_paths(db_path, single_process, batch_id, image_processor)

        if not total_images:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE); return

        # Ekstrak Metadata (jika bagian dari pipeline ini)
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
        print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
        print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

        # --- 5. PROSES INTI PER BATCH ---
        processed_batches_results = []
        raw_weight_maps_for_learning = []
        images_processed_count = 0
        should_get_weights = perform_learning_setting or use_learning_model_setting

        for batch_num, (batch_start, batch_end) in enumerate(batch_plan, 1):
            if stop_requested and stop_requested():
                print(language_config.PROCESS_TERMINATED_BY_USER)
                break
            
            print(f"\n{language_config.PROCESSING_BATCH.format(batch_num, total_batches, batch_start)}")

            # [REFAKTOR] Memuat gambar menggunakan fungsi helper
            batch_images_list = _load_images_for_batch(data_source, (batch_start, batch_end), stop_requested)

            if stop_requested and stop_requested(): break
            if not batch_images_list:
                print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(batch_num))
                continue

            # [LOGIKA INTI] Panggilan spesifik ke similarity_mnfr
            batch_result_img, _, individual_raw_maps = image_processor.similarity_mnfr(
                images=batch_images_list, merging_type=merging_type_from_settings,
                tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                update_progress=update_progress, stop_requested=stop_requested,
                total_overall_images=total_images, images_processed_so_far=images_processed_count,
                use_learning_model=use_learning_model_setting,
                perform_learning=False, # Pelatihan tidak pernah dipicu di sini
                weight_of_each_image=should_get_weights,
                collect_raw_maps_for_learning=perform_learning_setting, 
                **extra_merging_params
            )
            
            if stop_requested and stop_requested(): break
            
            if batch_result_img is not None:
                processed_batches_results.append(batch_result_img)
                images_processed_count += len(batch_images_list)
            if individual_raw_maps:
                raw_weight_maps_for_learning.extend(individual_raw_maps)

        if stop_requested and stop_requested():
            if update_progress and progress_bar: update_progress(progress_bar.value(), "Proses Dibatalkan.")
            return

        # --- 6. PENYIMPANAN DATA MENTAH UNTUK LEARNING (SPESIFIK SIMILARITY) ---
        raw_maps_db_path = os.path.join("database", "Learning_Model", "raw_weight_map_database.h5")
        if perform_learning_setting and raw_weight_maps_for_learning:
            training_resolution_setting = tuple(general_settings.get("training_resolution", (256, 256)))
            resized_maps = [cv2.resize(w_map, training_resolution_setting, interpolation=cv2.INTER_AREA) for w_map in raw_weight_maps_for_learning]

            try:
                with h5py.File(raw_maps_db_path, 'a') as hf:
                    last_index = max([int(k.split('_')[-1]) for k in hf.keys() if k.startswith('map_')] or [-1])
                    for i, w_map in enumerate(resized_maps):
                        hf.create_dataset(f'map_{last_index + 1 + i}', data=w_map, compression="gzip")
            except Exception as e:
                traceback.print_exc()

        # --- 7. PENGGABUNGAN AKHIR / FINE-TUNING ---
        final_result_img = None
        if processed_batches_results:
            if len(processed_batches_results) > 1:
                fine_tuning_start_progress, fine_tuning_end_progress = 95, 99
                def fine_tuning_update_progress(inner_progress, message):
                    mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                    if update_progress and not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))
                
                if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)
                
                # [LOGIKA INTI] Panggilan spesifik ke similarity_mnfr untuk fine-tuning
                final_result_img, _, _ = image_processor.similarity_mnfr(
                    images=processed_batches_results, merging_type=merging_type_from_settings,
                    tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                    motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                    update_progress=fine_tuning_update_progress, stop_requested=stop_requested,
                    save_weight_map_path=(weight_map_output_path if save_final_weight_map else None),
                    total_overall_images=len(processed_batches_results), images_processed_so_far=0,
                    use_learning_model=False, perform_learning=False, weight_of_each_image=False,
                    collect_raw_maps_for_learning=False, **extra_merging_params
                )
            else:
                final_result_img = processed_batches_results[0]
        
        # --- 8. PENYIMPANAN HASIL AKHIR & PEMBERSIHAN ---
        if final_result_img is not None:
            ref_path_for_save = image_paths[0] if image_paths else None
            save_success = save_image(final_result_img, output_path, reference_image_path=ref_path_for_save)
            
            final_message = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}" if save_success \
                else f"{language_config.FAILED_TO_SAVE_IMAGE}: {os.path.basename(output_path)}"
            if update_progress: update_progress(100, final_message)

            # Cleanup
            if not single_process and batch_id is not None:
                hdf5_path = os.path.join("database", "align", f"aligned_image_batch_{batch_id}.h5")
                if os.path.exists(hdf5_path):
                    try: os.remove(hdf5_path)
                    except OSError as e: print(f"Error removing temp file: {e}")
        else:
            if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

    # --- 9. PENANGANAN ERROR (UMUM) ---
    except Exception as e:
        error_message = language_config.RUN_ERROR_MESSAGE.format(error=str(e))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()):
            update_progress(0, error_message)

def running_similarity(parent=None, single_process=None, batch_id=None):
    process_finished = False
    """
    Menampilkan progress bar dengan gaya kustom dan memanfaatkan thread.
    """
    # Membuat dialog progress
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