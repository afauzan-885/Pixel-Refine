import traceback
import cv2
import joblib
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import torch
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import add_legend_heatmap, extract_all_metadata, gaussian_window, get_all_image_paths_for_single_process, load_images_from_paths, normalize_image, optical_flow_refinement, resize_all_with_padding, save_image, standard_refinement, temporal_consistency_refinement
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityFrequencyInterface, SimilaritySpatialInterface
from UI.enhance_stack.algorithm.model_trainer.train_similarity_model import DBSCANClusterer, ViTAutoencoder, train_model
from UI.enhance_stack.components.single_page_layout.parameter_denoising.similarity_parameter_settings import  load_similarity_config
from UI.resources.stylesheet.stylesheet import PROGRESS_BAR
from UI.settings.General.Language import language_config

class ThreadWorker(QThread):
    progress_updated = pyqtSignal(int, str)  
    finished = pyqtSignal()  
    error_occurred = pyqtSignal(str)

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
                 encoder_path="database/Learning_Model/autoencoder_pytorch.pth",
                 model_path="database/Learning_Model/kmeans_model.pth"):
        self.encoder_path = encoder_path
        self.model_path = model_path
        self.db_path = db_path
        self.knowledge_model = None
        self.is_model_loaded = False
        self.model_type = None 

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
        """ Memuat model ViTAutoencoder dan DBSCAN. """
        encoder_path = "database/Learning_Model_ViT/vit_autoencoder_pytorch.pth"
        cluster_path = "database/Learning_Model_ViT/dbscan_clusters.pth"
        if not os.path.exists(self.encoder_path) or not os.path.exists(self.model_path):
            print(f"Model Loader: File model tidak lengkap. Membutuhkan '{os.path.basename(self.encoder_path)}' dan '{os.path.basename(self.model_path)}'.")
            self.is_model_loaded = False
            return False
            
        print(f"Model Loader: Ditemukan model CAE dan K-Means. Mencoba memuat ke '{self.device}'...")
        try:
            # Parameter harus sama
            training_resolution = (256, 256)
            encoding_dim = 64

            autoencoder = ViTAutoencoder(image_size=training_resolution[0], encoding_dim=encoding_dim)
            autoencoder.load_state_dict(torch.load(encoder_path, map_location=self.device, weights_only=True))
            autoencoder.to(self.device)
            autoencoder.eval()
            
            clusterer = DBSCANClusterer(device=self.device)
            clusterer.load_model(cluster_path)
            
            self.knowledge_model = {
                'autoencoder': autoencoder,
                'clusterer': clusterer, # Ganti nama dari 'kmeans'
                'training_resolution': training_resolution
            }
            self.model_type = 'vit_plus_dbscan'
            self.is_model_loaded = True
            print(f"  -> SUKSES: Model ConvAutoencoder dan K-Means berhasil dimuat di '{self.device}'.")
            return True
            
        except Exception as e:
            print(f"  -> GAGAL memuat model: {e}")
            traceback.print_exc() 
            self.is_model_loaded = False
            return False

    def _apply_knowledge_model(self, weight_map, blending_factor=0.7):
        """
        Menerapkan model ConvAutoencoder & K-Means untuk menyempurnakan peta bobot.
        """
        if not self.is_model_loaded or self.model_type != 'cae_plus_kmeans':
            return weight_map

        autoencoder = self.knowledge_model['autoencoder']
        clusterer = self.knowledge_model['clusterer'] # Gunakan clusterer
        training_resolution = self.knowledge_model['training_resolution']
        
        # Pra-pemrosesan (resize dan normalisasi, sama seperti sebelumnya)
        original_map_float = weight_map.astype(np.float32)
        resized_map = cv2.resize(original_map_float, training_resolution, interpolation=cv2.INTER_AREA)
        max_val = np.max(resized_map)
        normalized_map = resized_map / max_val if max_val > 0 else resized_map
        
        # Ubah input menjadi 3 channel untuk ViT
        input_tensor = torch.from_numpy(normalized_map).float().unsqueeze(0).unsqueeze(0)
        input_tensor_3ch = input_tensor.repeat(1, 3, 1, 1).to(self.device)

        with torch.no_grad():
            # 1. Dapatkan fitur dari ViT encoder
            encoded_input = autoencoder.encode(input_tensor_3ch)
            
            # 2. Ambil pusat-pusat cluster dari model DBSCAN
            cluster_centers = clusterer.centroids
            
            # 3. Hitung jarak dan temukan cluster terdekat
            distances = torch.sum((encoded_input - cluster_centers)**2, dim=1)
            cluster_id = torch.argmin(distances).item()
            
            # 4. Ambil vektor ideal dari pusat cluster yang menang
            ideal_encoded_vec = cluster_centers[cluster_id]
            
            # 5. Rekonstruksi gambar dari vektor ideal menggunakan decoder
            reconstructed_output = autoencoder.decode(ideal_encoded_vec.unsqueeze(0))
            
            ideal_map = reconstructed_output.cpu().numpy().squeeze()

        # Proses blending dan post-processing (tidak berubah)
        blended_map_resized = (blending_factor * ideal_map) + ((1 - blending_factor) * normalized_map)
        blended_map_original_scale = blended_map_resized * max_val if max_val > 0 else blended_map_resized
        return cv2.resize(blended_map_original_scale, (weight_map.shape[1], weight_map.shape[0]), interpolation=cv2.INTER_LINEAR)
    
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
                         weight_of_each_image=False, # <<< Perhatikan parameter ini sudah ada
                         **unused_kwargs):

        tile_h, tile_w = map(int, tile_size)
        try:
            c_interface = SimilaritySpatialInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal C++ interface_spatial_merging: {e}")

        final_image_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w), dtype=np.float32))
        step_y = max(int(tile_h * (1 - overlap)), 1)
        step_x = max(int(tile_w * (1 - overlap)), 1)

        row_starts = np.arange(0, ref_image_h - tile_h + 1, step_y) if ref_image_h >= tile_h else np.array([0])
        if ref_image_h > tile_h and (not row_starts.size or row_starts[-1] != ref_image_h - tile_h):
            row_starts = np.append(row_starts, ref_image_h - tile_h)
        if ref_image_h == tile_h:
            row_starts = np.array([0])
        col_starts = np.arange(0, ref_image_w - tile_w + 1, step_x) if ref_image_w >= tile_w else np.array([0])
        if ref_image_w > tile_w and (not col_starts.size or col_starts[-1] != ref_image_w - tile_w):
            col_starts = np.append(col_starts, ref_image_w - tile_w)
        if ref_image_w == tile_w:
            col_starts = np.array([0])

        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        base_window = gaussian_window(tile_size)
        block_h, block_w, search_radius = tile_h, tile_w, 0

        num_images = len(images)
        processed_frames_spatial = 0
        progress_cap_percent = 95
        orig_h, orig_w = images[0].shape[:2]

        if temporal_consistency:
            weight_maps_all = []

        if weight_of_each_image:
            weight_maps_per_image = []

        accumulated_weight_map = None
        prev_weight_map_for_standard = None

        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray):
                continue
            if update_progress:
                current_img_overall = images_processed_so_far + i + 1
                prog = int((current_img_overall / total_overall_images) * progress_cap_percent
                        if total_overall_images and total_overall_images > 0
                        else ((i + 1) / num_images) * progress_cap_percent)
                msg = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_img_overall, total_overall_images) \
                    if total_overall_images and total_overall_images > 0 \
                    else language_config.ANALYZING_IMAGE.format(i + 1, num_images)
                update_progress(prog, msg)
            if stop_requested and stop_requested():
                break
            try:
                if image_orig.shape[0] != orig_h or image_orig.shape[1] != orig_w or image_orig.dtype != ref_dtype:
                    continue
                num_ch_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
                if num_ch_orig not in (1, 3):
                    continue
            except Exception:
                continue

            current_image_float = normalize_image(image_orig, ref_dtype)
            if current_image_float.shape[2] != ref_channels_buffer:
                continue

            try:
                temp_weight_map = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w), dtype=np.float32))

                c_interface.call_accumulate_frame_weighted(
                    c_interface.clib, final_image_sum, temp_weight_map, current_image_float, reference_image_float,
                    base_window, row_starts, col_starts, tile_h, tile_w, ref_image_h, ref_image_w, ref_channels_buffer,
                    block_h, block_w, search_radius, motion_sensitivity, noise_offset_factor
                )

                if refinement_algorithm == 'optical_flow' and optical_flows is not None and i < len(optical_flows):
                    if accumulated_weight_map is None:
                        refined_weight = temp_weight_map
                    else:
                        refined_weight = optical_flow_refinement(temp_weight_map, accumulated_weight_map, optical_flows[i])
                    accumulated_weight_map = refined_weight

                elif refinement_algorithm == 'standard':
                    refined_weight = standard_refinement(temp_weight_map, prev_weight_map_for_standard, reference_image_float)
                    prev_weight_map_for_standard = refined_weight.copy()
                else:
                    refined_weight = temp_weight_map

                weight_map_sum += refined_weight

                if temporal_consistency:
                    weight_maps_all.append(refined_weight.copy())

                if weight_of_each_image:
                    weight_maps_per_image.append(refined_weight.copy())

                processed_frames_spatial += 1

            except Exception as e:
                raise RuntimeError(f"C++ accumulation frame {i+1} spatial: {e}")

        if processed_frames_spatial > 0:
            try:
                c_interface.call_normalize_accumulated(
                    c_interface.clib, final_image_sum, weight_map_sum,
                    ref_image_h, ref_image_w, ref_channels_buffer
                )

                if temporal_consistency:
                    temporal_consistency_refinement(
                        weight_maps_all,
                        weight_map_sum,
                        save_temporal_std_path=save_temporal_std_path
                    )
                # <<< DIUBAH: Mengembalikan daftar peta bobot jika diminta >>>
                if weight_of_each_image:
                    return final_image_sum, weight_map_sum, processed_frames_spatial, weight_maps_per_image
                else:
                    return final_image_sum, weight_map_sum, processed_frames_spatial

            except Exception as e:
                raise RuntimeError(f"Normalization failed: {e}")
        
        # <<< DIUBAH: Menyesuaikan nilai kembalian saat gagal >>>
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
                           weight_of_each_image=False, # <<< BARU: Parameter ditambahkan >>>
                           **unused_kwargs):

        if not images:
            # <<< DIUBAH: Menyesuaikan nilai kembalian saat gagal >>>
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
        
        if temporal_consistency:
            weight_maps_all = []
        
        # <<< BARU: Inisialisasi list untuk menyimpan peta bobot individual >>>
        if weight_of_each_image:
            weight_maps_per_image = []

        accumulated_weight_map = None
        prev_weight_map_for_standard = None
        
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

                if refinement_algorithm == 'optical_flow' and optical_flows is not None and original_idx < len(optical_flows):
                    if accumulated_weight_map is None:
                        refined_weight = temp_weight_map
                    else:
                        refined_weight = optical_flow_refinement(temp_weight_map, accumulated_weight_map, optical_flows[original_idx])
                    accumulated_weight_map = refined_weight.copy()
                elif refinement_algorithm == 'standard':
                    refined_weight = standard_refinement(temp_weight_map, prev_weight_map_for_standard, reference_image_float)
                    prev_weight_map_for_standard = refined_weight.copy()
                else:
                    refined_weight = temp_weight_map

                weight_map_sum = weight_map_sum_before_this_frame + refined_weight
                
                if temporal_consistency:
                    weight_maps_all.append(refined_weight.copy())

                # <<< BARU: Menyimpan peta bobot yang sudah di-refine untuk frame ini >>>
                if weight_of_each_image:
                    weight_maps_per_image.append(refined_weight.copy())

                processed_frames_freq += 1

            except Exception as e_cxx:
                print(f"Warning: C++ accumulation failed for frame {original_idx+1}: {e_cxx}")
                continue
        
        if processed_frames_freq > 0:
            try:
                c_interface.call_normalize_accumulated(
                    c_interface.clib, final_image_sum, weight_map_sum,
                    ref_image_h, ref_image_w, ref_channels_buffer
                )
                
                if temporal_consistency:
                    temporal_consistency_refinement(
                        weight_maps_all,
                        weight_map_sum,
                        save_temporal_std_path=save_temporal_std_path
                    )

                if weight_of_each_image:
                    return final_image_sum, weight_map_sum, processed_frames_freq, weight_maps_per_image
                else:
                    return final_image_sum, weight_map_sum, processed_frames_freq

            except Exception as e_norm:
                raise RuntimeError(f"{language_config.NORMALIZATION_FAILED.format(e_norm)} (frequency merging)")
        else:
            # <<< DIUBAH: Menyesuaikan nilai kembalian saat gagal >>>
            return (None, None, 0, []) if weight_of_each_image else (None, None, 0)    
    
    def similarity_mnfr(self, images,
                    merging_type='spatial',
                    tile_size=None, overlap=None,
                    motion_sensitivity=None, noise_offset_factor=None,
                    update_progress=None, stop_requested=None,
                    save_weight_map_path=None #"database/weight_map.png"
                    , total_overall_images=None, images_processed_so_far=0, save_temporal_std_path="database/stack.jpg",
                    weight_of_each_image=False,
                    # --- Parameter kontrol pembelajaran ---
                    use_learning_model=False,
                    perform_learning=False,
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
        if use_learning_model and not self.is_model_loaded:
            print("Mencoba memuat model pengetahuan...")
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
            "weight_of_each_image": weight_of_each_image
        }
        common_call_args.update(merging_kwargs)
        
        if merging_type == 'spatial':
            current_tile_size = tile_size if tile_size is not None else common_call_args.get('tile_size')
            current_overlap = overlap if overlap is not None else common_call_args.get('overlap')
            current_motion_sensitivity = motion_sensitivity if motion_sensitivity is not None else common_call_args.get('motion_sensitivity')
            current_noise_offset_factor = noise_offset_factor if noise_offset_factor is not None else common_call_args.get('noise_offset_factor')
            
            if any(p is None for p in [current_tile_size, current_overlap, current_motion_sensitivity, current_noise_offset_factor]):
                raise ValueError("Untuk spatial merging, tile_size, overlap, motion_sensitivity, dan noise_offset_factor harus disediakan.")

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
            final_image_normalized, final_weight_map, processed_frames, weight_maps_per_image = results
        else:
            final_image_normalized, final_weight_map, processed_frames = results
            weight_maps_per_image = []

        if processed_frames > 0 and final_image_normalized is not None:
            
            all_final_weight_maps_to_return = []
            if weight_maps_per_image:
                
                if use_learning_model and self.is_model_loaded:
                    print(f"\n--- Memulai Rekonstruksi Peta Bobot (Total: {len(weight_maps_per_image)}) ---")

                for i, w_map in enumerate(weight_maps_per_image):
                    final_w_map = w_map
                    if use_learning_model and self.is_model_loaded:
                        
                        print(f"  -> Model menerapkan pengetahuan pada peta bobot #{i+1}/{len(weight_maps_per_image)}...")
                        
                        final_w_map = self._apply_knowledge_model(w_map)
                    all_final_weight_maps_to_return.append(final_w_map)
                
                # <<< PERUBAHAN KUNCI #3: PESAN PENUTUP (OPSIONAL) >>>
                if use_learning_model and self.is_model_loaded:
                    print("--- Rekonstruksi Selesai ---")

            if save_weight_map_path and final_weight_map is not None:
                try:
                    max_w = np.max(final_weight_map)
                    norm_w_vis = final_weight_map / max_w if max_w > 1e-6 else np.zeros_like(final_weight_map)
                    w_map_vis = (np.clip(norm_w_vis, 0.0, 1.0) * 255).astype(np.uint8)
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    cv2.imwrite(save_weight_map_path, w_map_vis)
                except Exception as e:
                    print(f"Error saat menyimpan peta bobot gabungan: {e}")
                    traceback.print_exc()

            maps_to_save = all_final_weight_maps_to_return if all_final_weight_maps_to_return else weight_maps_per_image
            
            if weight_of_each_image and save_weight_map_path and maps_to_save and not perform_learning:
                print(f"Mode Non-Pelatihan: Menyimpan {len(maps_to_save)} peta bobot individual sebagai heatmap...")
                try:
                    base, ext = os.path.splitext(save_weight_map_path)
                    for i, w_map in enumerate(maps_to_save):
                        individual_map_path = f"{base}_frame_{i}{ext}"
                        w_map_vis = self._create_weight_map_heatmap(w_map)
                        if not cv2.imwrite(individual_map_path, w_map_vis):
                            print(f"Gagal menyimpan peta bobot individual ke: {individual_map_path}")
                except Exception as e:
                    print(f"Error saat menyimpan peta bobot individual: {e}")
                    traceback.print_exc()

            scale_val = np.float32(np.iinfo(dtype_ref).max)
            final_img_scaled = final_image_normalized * scale_val
            
            if channels_ref_orig == 1:
                final_img_out_ch = np.mean(final_img_scaled, axis=2)
            else:
                final_img_out_ch = final_img_scaled
                
            min_v, max_v = 0, np.iinfo(dtype_ref).max
            final_img_output = np.clip(final_img_out_ch, min_v, max_v).astype(dtype_ref, copy=False)
            
            if stop_requested and stop_requested() and processed_frames < len(images):
                print(f"PERINGATAN: Hasil parsial dari {merging_type} merging, {processed_frames} frame diproses.")
            
            # Kembalikan DUA nilai yang konsisten
            return final_img_output, all_final_weight_maps_to_return

        else:
            # Jika tidak ada frame yang diproses
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            print(f"Tidak ada frame yang diproses oleh {merging_type} merging. Mengembalikan nilai kosong.")
            
            # Kembalikan DUA nilai yang konsisten
            return np.zeros(out_shape_fb, dtype=dtype_ref), [] 


def main(db_path, update_progress=None, stop_requested=None, batch_size=7,
         single_process=None, batch_id=None, save_final_weight_map=False,
         progress_bar=None):

    try:
        general_settings = load_similarity_config()
        use_learning_model_setting = general_settings.get("use_learning_model", False)
        perform_learning_setting = general_settings.get("perform_learning", True)
        
        print("\n--- Konfigurasi Proses ---")
        print(f"  Mode Pembelajaran (Gunakan Model): {'Aktif' if use_learning_model_setting else 'Nonaktif'}")
        print(f"  Mode Pembelajaran (Lakukan Pelatihan): {'Aktif' if perform_learning_setting else 'Nonaktif'}")
        print("--------------------------\n")
        
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
        
        output_name_base, image_paths = "", []
        align_dir = os.path.join("database", "align")

        if single_process:
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name_base = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths and isinstance(image_paths[0], str) else "single_default"
            output_name_base = f"{ref_name_base}"
        else:
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            ref_name_base = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths and isinstance(image_paths[0], str) else "batch_default"
            output_name_base = f"{ref_name_base}"
           
        if not image_paths:
            if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE); return
        
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)
        output_name_base_safe = "".join(c for c in output_name_base if c.isalnum() or c in ('_', '-')).rstrip() or "stack_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_{merging_type_from_settings}.tif")
        weight_map_output_path = os.path.join(output_folder_stack, f"{output_name_base_safe}_similarity_{merging_type_from_settings}_weight_map.png")
        print(language_config.OUTPUT_IMAGE_TO_BE_SAVED.format(output_path))
        if save_final_weight_map: print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(weight_map_output_path))
        
        metadata_folder = align_dir 
        os.makedirs(metadata_folder, exist_ok=True) 
        metadata_file = os.path.join(metadata_folder, "metadata.json")
        if image_paths and 'extract_all_metadata' in globals():
            try: extract_all_metadata(image_paths, metadata_file=metadata_file)
            except Exception as e_meta: traceback.print_exc()
        if update_progress: update_progress(0, language_config.RUN_IMAGE_PROCESS_STARTED)

        # --- 2. Inisialisasi Penampung Global ---
        all_weight_maps_for_global_training = []
        processed_batches_results = []
        images_processed_count = 0
        total_images = 0
        
        global_hdf5_path = os.path.join(align_dir, "aligned_images.h5" if single_process else f"aligned_image_batch_{batch_id}.h5")
        use_hdf5 = os.path.exists(global_hdf5_path)

        # --- 3. Tahap Pengumpulan Data (Loop Batch) ---
        should_get_weights = perform_learning_setting or use_learning_model_setting

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys())
                    total_images = len(keys)
                    if total_images == 0:
                        if update_progress: update_progress(100, "File HDF5 kosong."); return
                    total_batches = (total_images + batch_size - 1) // batch_size
                    print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
                    print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))
                    
                    for batch_start_idx in range(0, total_images, batch_size):
                        current_batch_num = (batch_start_idx // batch_size) + 1
                        print(f"\n{language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start_idx)}")
                        if stop_requested and stop_requested(): print(language_config.PROCESS_TERMINATED_BY_USER); break
                        
                        batch_keys = keys[batch_start_idx : min(batch_start_idx + batch_size, total_images)]
                        batch_images_list = [np.array(h5f[key]) for key in batch_keys if not (stop_requested and stop_requested())]
                        if not batch_images_list: print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num)); continue
                        
                        batch_result_img, weight_maps_from_batch = image_processor.similarity_mnfr(
                            images=batch_images_list, merging_type=merging_type_from_settings,
                            tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                            motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                            update_progress=update_progress, stop_requested=stop_requested,
                            total_overall_images=total_images, images_processed_so_far=images_processed_count,
                            use_learning_model=use_learning_model_setting,
                            perform_learning=False, weight_of_each_image=should_get_weights,
                            **extra_merging_params
                        )
                        
                        if stop_requested and stop_requested(): 
                            break
                        if batch_result_img is not None:
                            processed_batches_results.append(batch_result_img)
                            images_processed_count += len(batch_images_list)
                        if weight_maps_from_batch:
                            all_weight_maps_for_global_training.extend(weight_maps_from_batch)
            except Exception as e_h5_main:
                 print(language_config.ERROR_IN_READING_FILE_HDF5.format(e_h5_main)); traceback.print_exc()
                 if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e_h5_main)); return
        else:
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            if total_images == 0:
                if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE); return
            total_batches = (total_images + batch_size - 1) // batch_size
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
            print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

            for batch_start_idx in range(0, total_images, batch_size):
                current_batch_num = (batch_start_idx // batch_size) + 1
                print(f"\n{language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start_idx)}")
                if stop_requested and stop_requested(): print(language_config.PROCESS_TERMINATED_BY_USER); break

                current_batch_paths = image_paths[batch_start_idx : min(batch_start_idx + batch_size, total_images)]
                batch_images_list = load_images_from_paths(current_batch_paths, stop_requested)
                if stop_requested and stop_requested(): break
                if 'resize_all_with_padding' in globals(): batch_images_list, _ = resize_all_with_padding(batch_images_list, method="median")
                if not batch_images_list: print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num)); continue

                batch_result_img, weight_maps_from_batch = image_processor.similarity_mnfr(
                    images=batch_images_list, merging_type=merging_type_from_settings,
                    tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                    motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                    update_progress=update_progress, stop_requested=stop_requested,
                    total_overall_images=total_images, images_processed_so_far=images_processed_count,
                    use_learning_model=use_learning_model_setting,
                    perform_learning=False, weight_of_each_image=should_get_weights,
                    **extra_merging_params
                )
                
                if stop_requested and stop_requested(): break
                if batch_result_img is not None:
                    processed_batches_results.append(batch_result_img)
                    images_processed_count += len(batch_images_list)
                if weight_maps_from_batch:
                    all_weight_maps_for_global_training.extend(weight_maps_from_batch)
        
        # --- 4. Tahap Pelatihan (Jika Diaktifkan) ---
        if perform_learning_setting and all_weight_maps_for_global_training:
            print("\n" + "="*50)
            print("MEMPERSIAPKAN SESI PELATIHAN CANGGIH DENGAN PANDUAN...")
            
            final_ground_truth_for_training = None
            print("  -> Mensimulasikan 'stack.jpg' untuk membuat target pelatihan (ground truth)...")
            try:
                temp_weight_sum = np.sum(np.stack(all_weight_maps_for_global_training, axis=0), axis=0)
                
                temporal_consistency_refinement(all_weight_maps_for_global_training, temp_weight_sum)
                
                max_val = np.max(temp_weight_sum)
                final_ground_truth_for_training = temp_weight_sum / max_val if max_val > 0 else temp_weight_sum
                print("  -> SUKSES: Ground truth untuk pelatihan berhasil dibuat.")
            except Exception as e:
                print(f"  -> PERINGATAN: Gagal membuat ground truth. Pelatihan berjalan tanpa panduan. Error: {e}")
                traceback.print_exc()

            dbscan_eps_setting = general_settings.get("dbscan_eps", 0.75)
            dbscan_min_samples_setting = general_settings.get("dbscan_min_samples", 5)
            loss_alpha_setting = general_settings.get("loss_alpha", 0.85)
            loss_beta_setting = general_settings.get("loss_beta", 0.15)
            
            train_model(
                new_weight_maps=all_weight_maps_for_global_training,
                ground_truth_map=final_ground_truth_for_training,
                
                model_dir="database/Learning_Model_ViT/", 
                database_path="database/Learning_Model_ViT/training_database.h5", # <-- DIUBAH
                
                update_callback=update_progress,
                guidance_weight=1.0,
                
                dbscan_eps=dbscan_eps_setting,                 
                dbscan_min_samples=dbscan_min_samples_setting, 
                loss_alpha=loss_alpha_setting,                 
                loss_beta=loss_beta_setting                    
                
            )
        
        # --- 5. Tahap Fine-Tuning dan Penyimpanan Hasil Akhir ---
        if stop_requested and stop_requested():
            pass
        elif processed_batches_results and any(res is not None for res in processed_batches_results):
            valid_batch_results = [res for res in processed_batches_results if res is not None]
            if not valid_batch_results:
                 print(language_config.DATA_FAILED_COMPLETION_CREATED)
                 if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED); return

            final_result_img = None
            num_valid_results = len(valid_batch_results)

            if num_valid_results > 1:
                print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_valid_results} batch results) using {merging_type_from_settings} ---")
                fine_tuning_start_progress, fine_tuning_end_progress = 95, 99
                
                def fine_tuning_update_progress(inner_progress, message):
                    mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                    if update_progress and not (stop_requested and stop_requested()):
                        update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))
                
                if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)
                
                final_weight_map_path_arg = weight_map_output_path if save_final_weight_map else None
                try:
                    final_result_img, _ = image_processor.similarity_mnfr(
                        images=valid_batch_results, merging_type=merging_type_from_settings,
                        tile_size=spatial_tile_size_arg, overlap=spatial_overlap_arg,
                        motion_sensitivity=spatial_motion_sensitivity_arg, noise_offset_factor=spatial_noise_offset_factor_arg,
                        update_progress=fine_tuning_update_progress, stop_requested=stop_requested,
                        save_weight_map_path=final_weight_map_path_arg,
                        total_overall_images=num_valid_results, images_processed_so_far=0,
                        use_learning_model=False,
                        perform_learning=False,
                        **extra_merging_params
                    )
                except Exception as e_fine:
                    traceback.print_exc()
                    final_result_img = None

            elif num_valid_results == 1:
                final_result_img = valid_batch_results[0]
                if update_progress:
                    update_progress(95, "Melewatkan fine-tuning, persiapan menyimpan hasil.")
            
            if final_result_img is not None and not (stop_requested and stop_requested()):
                ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                
                save_success = save_image(final_result_img, output_path, reference_image_path=ref_path_for_save)
                if save_success:
                    final_msg = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_msg)
                    if update_progress: update_progress(100, final_msg)
                    if not single_process and batch_id is not None and os.path.exists(global_hdf5_path):
                        try: os.remove(global_hdf5_path)
                        except Exception as e_del: pass
                else:
                    if update_progress: update_progress(100, f"Gagal simpan: {os.path.basename(output_path)}")
            
            elif not (stop_requested and stop_requested()):
                print(language_config.FAILED_IMAGE_ENHANCEMENT)
                if update_progress: update_progress(100, language_config.FAILED_IMAGE_ENHANCEMENT)
        
        elif not (stop_requested and stop_requested()): 
            print(language_config.DATA_FAILED_COMPLETION_CREATED)
            if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED)

        if stop_requested and stop_requested() and update_progress and progress_bar:
            update_progress(progress_bar.value(), "Proses Dibatalkan.")

    except ValueError as ve:
        error_msg = language_config.RUN_ERROR_MESSAGE.format(error=str(ve))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()): update_progress(0, error_msg)
    except Exception as e_main:
        error_msg = language_config.RUN_ERROR_MESSAGE.format(error=str(e_main))
        traceback.print_exc()
        if update_progress and not (stop_requested and stop_requested()): update_progress(0, error_msg)
    finally:
       pass

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

    worker.start()
    main("pixel_refine_database.db", update_progress=worker.progress_updated.emit, stop_requested=worker.stop_requested, progress_bar=progress_bar_instance)
    worker.start()
    dialog.exec()

if __name__ == "__main__":
    db_path = "pixel_refine_database.db"
    main(db_path)