from bm3d import bm3d_rgb
import traceback
import cv2
import numpy as np
import sqlite3
import os
from PyQt6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
import h5py
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import extra_denoising, extract_all_metadata, gaussian_window, get_all_image_paths_for_single_process, load_images_from_paths, normalize_image, resize_all_with_padding, save_image
from UI.enhance_stack.algorithm.denoising.extra_code.extra_algorithm import SimilarityFrequencyInterface, SimilaritySpatialInterface
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
    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        # Pastikan folder HDF5 ada
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

    def _spatial_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                         reference_image_float, tile_size, overlap,
                         motion_sensitivity, noise_offset_factor,
                         update_progress=None, stop_requested=None,
                         total_overall_images=None, images_processed_so_far=0,
                         lib_path='UI/data/similarity_spatial_merging.dll',
                         **unused_kwargs):
        tile_h, tile_w = map(int, tile_size)
        try:
            c_interface = SimilaritySpatialInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal C++ interface_spatial_merging: {e}")

        final_image_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), dtype=np.float32))
        weight_map_sum = np.ascontiguousarray(np.zeros((ref_image_h, ref_image_w), dtype=np.float32))
        step_y = max(int(tile_h * (1 - overlap)), 1); step_x = max(int(tile_w * (1 - overlap)), 1)
        if ref_image_h >= tile_h:
            row_starts = np.arange(0, ref_image_h - tile_h + 1, step_y)
            if ref_image_h > tile_h and (not row_starts.size or row_starts[-1] != ref_image_h - tile_h): row_starts = np.append(row_starts, ref_image_h - tile_h)
            elif ref_image_h == tile_h: row_starts = np.array([0])
        else: row_starts = np.array([0])
        if ref_image_w >= tile_w:
            col_starts = np.arange(0, ref_image_w - tile_w + 1, step_x)
            if ref_image_w > tile_w and (not col_starts.size or col_starts[-1] != ref_image_w - tile_w): col_starts = np.append(col_starts, ref_image_w - tile_w)
            elif ref_image_w == tile_w: col_starts = np.array([0])
        else: col_starts = np.array([0])
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))
        base_window = gaussian_window(tile_size)
        block_h, block_w, search_radius = tile_h, tile_w, 0
        num_images, processed_frames_spatial, progress_cap_percent = len(images), 0, 95
        orig_h, orig_w = images[0].shape[:2]

        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray): continue
            if update_progress:
                current_img_overall = images_processed_so_far + i + 1
                prog = int((current_img_overall / total_overall_images) * progress_cap_percent if total_overall_images and total_overall_images > 0 else ((i + 1) / num_images) * progress_cap_percent)
                msg = language_config.IMAGE_PROCESS_IN_PROGRESS.format(current_img_overall, total_overall_images) if total_overall_images and total_overall_images > 0 else language_config.ANALYZING_IMAGE.format(i + 1, num_images)
                update_progress(prog, msg)
            if stop_requested and stop_requested(): break
            try:
                if image_orig.shape[0] != orig_h or image_orig.shape[1] != orig_w or image_orig.dtype != ref_dtype: continue
                num_ch_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
                if num_ch_orig not in (1, 3): continue
            except Exception: continue
            current_image_float = normalize_image(image_orig, ref_dtype)
            if current_image_float.shape[2] != ref_channels_buffer: continue
            try:
                c_interface.call_accumulate_frame_weighted(
                    c_interface.clib, final_image_sum, weight_map_sum, current_image_float, reference_image_float,
                    base_window, row_starts, col_starts, tile_h, tile_w, ref_image_h, ref_image_w, ref_channels_buffer,
                    block_h, block_w, search_radius, motion_sensitivity, noise_offset_factor
                )
                processed_frames_spatial += 1
            except Exception as e: raise RuntimeError(f"C++ accumulation frame {i+1} spatial: {e}")
        if processed_frames_spatial > 0:
            try:
                c_interface.call_normalize_accumulated(c_interface.clib, final_image_sum, weight_map_sum, ref_image_h, ref_image_w, ref_channels_buffer)
                return final_image_sum, weight_map_sum, processed_frames_spatial
            except Exception as e: raise RuntimeError(language_config.NORMALIZATION_FAILED.format(e))
        return None, None, 0

    def _frequency_merging(self, images, ref_image_h, ref_image_w, ref_channels_buffer, ref_dtype,
                           reference_image_float,
                           freq_c_wiener_factor,
                           freq_tile_size,
                           freq_overlap_percent,
                           update_progress=None, stop_requested=None,
                           total_overall_images=None, images_processed_so_far=0,
                           lib_path='UI/data/similarity_frequency_merging.dll', 
                           **unused_kwargs):

        # Optimasi 1: Early validation dan caching
        if not images:
            return None, None, 0
        
        num_images = len(images)
        if num_images == 0:
            return None, None, 0
        
        # Unpack tile size once
        tile_h, tile_w = map(int, freq_tile_size)
        
        # Optimasi 2: Pre-compute constants
        step_y = max(int(tile_h * (1 - freq_overlap_percent)), 1)
        step_x = max(int(tile_w * (1 - freq_overlap_percent)), 1)
        progress_cap_percent = 95
        
        # Optimasi 3: Lazy loading C++ interface
        c_interface = None
        
        # Optimasi 4: Pre-compute row and column starts (moved up)
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
        
        # Optimasi 5: Pre-allocate arrays dengan dtype yang tepat
        final_image_sum = np.zeros((ref_image_h, ref_image_w, ref_channels_buffer), 
                                dtype=np.float32, order='C')
        weight_map_sum = np.zeros((ref_image_h, ref_image_w), dtype=np.float32, order='C')
        
        # Optimasi 6: Cache window computation
        base_window = gaussian_window(freq_tile_size)
        
        # Optimasi 7: Pre-validate first image untuk reference
        first_image = images[0]
        if not isinstance(first_image, np.ndarray):
            return None, None, 0
            
        orig_h, orig_w = first_image.shape[:2]
        orig_channels = first_image.shape[2] if first_image.ndim == 3 else 1
        
        # Optimasi 8: Batch validation dan filtering
        valid_images = []
        for i, image_orig in enumerate(images):
            if not isinstance(image_orig, np.ndarray):
                continue
                
            # Quick shape and dtype validation
            if (image_orig.shape[0] != orig_h or 
                image_orig.shape[1] != orig_w or 
                image_orig.dtype != ref_dtype):
                continue
                
            num_ch_orig = image_orig.shape[2] if image_orig.ndim == 3 else 1
            if num_ch_orig not in (1, 3):
                continue
                
            valid_images.append((i, image_orig))
        
        if not valid_images:
            return None, None, 0
        
        # Optimasi 9: Initialize C++ interface only when needed
        try:
            c_interface = SimilarityFrequencyInterface(lib_path)
        except (FileNotFoundError, OSError, AttributeError) as e:
            raise RuntimeError(f"Gagal C++ interface _frequency_merging: {e}")
        
        # Optimasi 10: Batch processing dengan error handling yang lebih efisien
        processed_frames_freq = 0
        block_h_cxx = tile_h
        block_w_cxx = tile_w
        
        # Pre-compute progress calculation factors
        if total_overall_images and total_overall_images > 0:
            progress_factor = progress_cap_percent / total_overall_images
            use_overall_progress = True
        else:
            progress_factor = progress_cap_percent / len(valid_images)
            use_overall_progress = False
        
        for idx, (original_idx, image_orig) in enumerate(valid_images):
            # Optimasi 11: Efficient progress updates
            if update_progress:
                if use_overall_progress:
                    current_img_overall = images_processed_so_far + original_idx + 1
                    prog_val = int(current_img_overall * progress_factor)
                    msg_val = language_config.IMAGE_PROCESS_IN_PROGRESS.format(
                        current_img_overall, total_overall_images)
                else:
                    prog_val = int((idx + 1) * progress_factor)
                    msg_val = language_config.ANALYZING_IMAGE.format(idx + 1, len(valid_images))
                update_progress(prog_val, msg_val)
            
            # Optimasi 12: Early stop check
            if stop_requested and stop_requested():
                break
            
            # Optimasi 13: Efficient image normalization
            try:
                current_image_float = normalize_image(image_orig, ref_dtype)
                if current_image_float.shape[2] != ref_channels_buffer:
                    continue
            except Exception:
                continue
            
            # Optimasi 14: Single C++ call with better error handling
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
                    tile_h, tile_w,
                    ref_image_h, ref_image_w, ref_channels_buffer,
                    block_h_cxx, block_w_cxx,
                    freq_c_wiener_factor
                )
                processed_frames_freq += 1
            except Exception as e_cxx:
                # Optimasi 15: More informative error without breaking the loop
                print(f"Warning: C++ accumulation failed for frame {original_idx+1}: {e_cxx}")
                continue
        
        # Optimasi 16: Final normalization with validation
        if processed_frames_freq > 0:
            try:
                c_interface.call_normalize_accumulated(
                    c_interface.clib,
                    final_image_sum,
                    weight_map_sum,
                    ref_image_h, ref_image_w, ref_channels_buffer
                )
                return final_image_sum, weight_map_sum, processed_frames_freq
            except Exception as e_norm:
                raise RuntimeError(f"{language_config.NORMALIZATION_FAILED.format(e_norm)} (frequency merging)")
        else:
            return None, None, 0

    def similarity_mnfr(self, images,
                        merging_type='spatial',
                        tile_size=None, overlap=None,
                        motion_sensitivity=None, noise_offset_factor=None,
                        update_progress=None, stop_requested=None,
                        save_weight_map_path=None, total_overall_images=None,
                        images_processed_so_far=0,
                        **merging_kwargs):

        if not isinstance(images, list) or not images: raise ValueError(language_config.IMAGE_DATA_MUST_BE_VALID)
        try:
            ref_image = images[0]
            if not isinstance(ref_image, np.ndarray): raise TypeError(language_config.IMAGE_DATA_MUST_BE_VALID)
            h_ref, w_ref, channels_ref_orig = ref_image.shape[0], ref_image.shape[1], (ref_image.shape[2] if ref_image.ndim == 3 else 1)
            dtype_ref = ref_image.dtype
            if channels_ref_orig not in (1, 3): raise ValueError(language_config.IMAGE_CHANNEL_DOES_NOT_SUPPORT.format(channels_ref_orig))
        except (AttributeError, IndexError, ValueError, TypeError) as e: raise ValueError(language_config.FIRST_IMAGE_CANNOT_BE_OBTAINED.format(e))
        if dtype_ref not in (np.uint8, np.uint16): raise TypeError(language_config.IMAGE_BIT_REQUIRED)

        channels_buffer = 3
        reference_image_float = normalize_image(ref_image, dtype_ref)
        h_ref_norm, w_ref_norm, _ = reference_image_float.shape
        final_image_normalized, final_weight_map, processed_frames = None, None, 0

        common_call_args = {
            "images": images, "ref_image_h": h_ref_norm, "ref_image_w": w_ref_norm,
            "ref_channels_buffer": channels_buffer, "ref_dtype": dtype_ref,
            "reference_image_float": reference_image_float,
            "update_progress": update_progress, "stop_requested": stop_requested,
            "total_overall_images": total_overall_images, "images_processed_so_far": images_processed_so_far
        }
        common_call_args.update(merging_kwargs)


        if merging_type == 'spatial':
            current_tile_size = tile_size if tile_size is not None else common_call_args.get('tile_size')
            current_overlap = overlap if overlap is not None else common_call_args.get('overlap')
            current_motion_sensitivity = motion_sensitivity if motion_sensitivity is not None else common_call_args.get('motion_sensitivity')
            current_noise_offset_factor = noise_offset_factor if noise_offset_factor is not None else common_call_args.get('noise_offset_factor')
            
            if any(p is None for p in [current_tile_size, current_overlap, current_motion_sensitivity, current_noise_offset_factor]):
                raise ValueError("Untuk spatial merging, tile_size, overlap, motion_sensitivity, dan noise_offset_factor harus disediakan baik sebagai argumen atau di merging_kwargs.")

            common_call_args.update({
                "tile_size": current_tile_size,
                "overlap": current_overlap,
                "motion_sensitivity": current_motion_sensitivity,
                "noise_offset_factor": current_noise_offset_factor
            })
            
            final_image_normalized, final_weight_map, processed_frames = self._spatial_merging(**common_call_args)

        elif merging_type == 'frequency':
            default_freq_tile_val = 24
            default_freq_overlap = 0.20
            default_freq_c_wiener = 5.0
            default_freq_lib_path = common_call_args.get('lib_path_freq', 
                                      common_call_args.get('lib_path', 'UI/data/similarity_frequency_merging.dll'))


            current_freq_c_wiener = common_call_args.get('freq_c_wiener_factor', default_freq_c_wiener)
            current_freq_tile_size_input = common_call_args.get('freq_tile_size', default_freq_tile_val)
            current_freq_overlap = common_call_args.get('freq_overlap_percent', default_freq_overlap)
            
            if isinstance(current_freq_tile_size_input, int):
                 current_freq_tile_size_tuple = (current_freq_tile_size_input, current_freq_tile_size_input)
            elif isinstance(current_freq_tile_size_input, (list,tuple)) and len(current_freq_tile_size_input) == 2:
                 current_freq_tile_size_tuple = tuple(map(int,current_freq_tile_size_input))
            else:
                print(f"WARNING: freq_tile_size dari merging_kwargs tidak valid ({current_freq_tile_size_input}), menggunakan default tuple.")
                current_freq_tile_size_tuple = (default_freq_tile_val, default_freq_tile_val)

            common_call_args.update({
                "freq_c_wiener_factor": current_freq_c_wiener,
                "freq_tile_size": current_freq_tile_size_tuple,
                "freq_overlap_percent": current_freq_overlap,
                "lib_path": default_freq_lib_path 
            })
            
            keys_to_remove_for_freq = ['tile_size', 'overlap', 'motion_sensitivity', 'noise_offset_factor']
            for key_to_remove in keys_to_remove_for_freq:
                common_call_args.pop(key_to_remove, None)


            final_image_normalized, final_weight_map, processed_frames = self._frequency_merging(**common_call_args)
        else:
            raise ValueError(f"Unsupported merging_type: {merging_type}. Choose 'spatial' or 'frequency'.")

        if processed_frames > 0 and final_image_normalized is not None:
            if save_weight_map_path and final_weight_map is not None:
                print(language_config.OUTPUT_SAVE_WEIGHT_MAP.format(save_weight_map_path))
                try:
                    max_w = np.max(final_weight_map)
                    norm_w_vis = final_weight_map / max_w if max_w > 1e-6 else np.zeros_like(final_weight_map)
                    norm_w_vis = np.clip(norm_w_vis, 0.0, 1.0)
                    w_map_vis = (norm_w_vis * 255).astype(np.uint8)
                    os.makedirs(os.path.dirname(save_weight_map_path), exist_ok=True)
                    if not cv2.imwrite(save_weight_map_path, w_map_vis):
                        print(language_config.FAILED_TO_SAVE_WEIGHT_MAP_TO_PATH.format(save_weight_map_path))
                    else: print(language_config.SAVING_WEIGHT_MAP)
                except Exception as e: print(f"Error saving weight map: {e}"); traceback.print_exc()
            scale_val = np.float32(np.iinfo(dtype_ref).max)
            final_img_scaled = final_image_normalized * scale_val
            final_img_out_ch = np.mean(final_img_scaled, axis=2) if channels_ref_orig == 1 else final_img_scaled
            min_v, max_v = 0, np.iinfo(dtype_ref).max
            final_img_output = np.clip(final_img_out_ch, min_v, max_v).astype(dtype_ref, copy=False)
            if stop_requested and stop_requested() and processed_frames < len(images):
                print(f"WARNING: Partial result {merging_type} merging {processed_frames} frames.")
            return final_img_output
        else:
            out_shape_fb = (h_ref, w_ref) if channels_ref_orig == 1 else (h_ref, w_ref, channels_ref_orig)
            print(f"No frames processed by {merging_type} merging. Returning zero image.")
            return np.zeros(out_shape_fb, dtype=dtype_ref)
        
def main(db_path, update_progress=None, stop_requested=None, batch_size=10,
         single_process=None, batch_id=None, save_final_weight_map=False,
         progress_bar=None, denoising_method="none"):

    try:
        general_settings = load_similarity_config()
        image_processor = SimilarityAlgorithm(db_path) 

        merging_type_from_settings = general_settings.get("similarity_merging_type", "spatial")
        spatial_tile_size_arg = None
        spatial_overlap_arg = None
        spatial_motion_sensitivity_arg = None
        spatial_noise_offset_factor_arg = None

        extra_merging_params = {}

        if merging_type_from_settings == 'spatial':
            tile_val_sp = general_settings.get("similarity_spatial_tile_size", 24)
            spatial_tile_size_arg = (tile_val_sp, tile_val_sp) 
            spatial_overlap_arg = general_settings.get("similarity_spatial_overlap_percent", 0.6)
            spatial_motion_sensitivity_arg = general_settings.get("similarity_spatial_motion_sensitivity", 110.0)
            spatial_noise_offset_factor_arg = general_settings.get("similarity_spatial_noise_mad_offset_factor", 0.3)

            custom_lib_path = general_settings.get("similarity_lib_path") 
            if custom_lib_path:
                extra_merging_params['lib_path'] = custom_lib_path
        
        elif merging_type_from_settings == 'frequency':
            extra_merging_params['freq_c_wiener_factor'] = general_settings.get("similarity_frequency_c_wiener_factor", 5.0)
            tile_val_fq = general_settings.get("similarity_frequency_tile_size", 16)
            extra_merging_params['freq_tile_size'] = tile_val_fq 
            extra_merging_params['freq_overlap_percent'] = general_settings.get("similarity_frequency_overlap_percent", 0.25)
        
        output_name_base = ""
        image_paths = []
        align_dir = os.path.join("database", "align")

        if single_process:
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name_base = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths and isinstance(image_paths[0], str) else "single_default"
            output_name_base = f"{ref_name_base}"
        else:
            if batch_id is None: 
                raise ValueError(language_config.BATCH_ID_MUST_BE_PRESENT_DURING_BATCH_PROCESS)
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

        global_hdf5_path = os.path.join(align_dir, "aligned_images.h5" if single_process else f"aligned_image_batch_{batch_id}.h5")
        processed_batches_results = []
        images_processed_count = 0
        total_images = 0
        use_hdf5 = os.path.exists(global_hdf5_path)

        if use_hdf5:
            print(language_config.PROCESSING_IMAGE_FROM_HDF5.format(global_hdf5_path))
            try:
                with h5py.File(global_hdf5_path, 'r') as h5f_check: total_images = len(h5f_check.keys())
                if total_images == 0:
                    if update_progress: update_progress(100, "File HDF5 kosong."); return
                print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
                total_batches = (total_images + batch_size - 1) // batch_size
                print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

                with h5py.File(global_hdf5_path, 'r') as h5f:
                    keys = list(h5f.keys())
                    for batch_start_idx in range(0, total_images, batch_size):
                        current_batch_num = (batch_start_idx // batch_size) + 1
                        print(f"\n{language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start_idx)}")
                        if stop_requested and stop_requested(): print(language_config.PROCESS_TERMINATED_BY_USER); break
                        
                        batch_keys = keys[batch_start_idx : min(batch_start_idx + batch_size, total_images)]
                        print(language_config.LOAD_IMAGE_FROM_HDF5.format(len(batch_keys)))
                        batch_images_list = []
                        for key_h5 in batch_keys:
                            if stop_requested and stop_requested(): break
                            try: batch_images_list.append(np.array(h5f[key_h5]))
                            except Exception as e_h5: print(language_config.ERROR_WHILE_RETRIEVING_KEY_FROM_HD5F.format(key_h5, e_h5))
                        if stop_requested and stop_requested(): break
                        if not batch_images_list: print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num)); continue
                        
                        print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images_list)))
                        try:
                            batch_result_img = image_processor.similarity_mnfr(
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
                                **extra_merging_params 
                            )
                        except Exception as e_sim_b: traceback.print_exc(); batch_result_img = None
                        if stop_requested and stop_requested(): break
                        if batch_result_img is not None:
                            processed_batches_results.append(batch_result_img)
                            images_processed_count += len(batch_images_list)
                        else:
                            pass
            except Exception as e_h5_main:
                print(language_config.ERROR_IN_READING_FILE_HDF5.format(e_h5_main)); traceback.print_exc()
                if update_progress: update_progress(0, language_config.ERROR_IN_READING_FILE_HDF5.format(e_h5_main)); return
        
        else:
            print(language_config.NO_HDF5_FILE_PROCESSING_FROM_PATH)
            total_images = len(image_paths)
            if total_images == 0:
                if update_progress: update_progress(100, language_config.NO_IMAGE_PATH_PROCESSED_IMAGE); return
            print(language_config.NUMBER_OF_IMAGES_TO_BE_PROCESSED.format(total_images))
            total_batches = (total_images + batch_size - 1) // batch_size
            print(language_config.NUMBER_OF_BATCHES_TO_BE_PROCESSED.format(total_batches))

            for batch_start_idx in range(0, total_images, batch_size):
                current_batch_num = (batch_start_idx // batch_size) + 1
                print(f"\n{language_config.PROCESSING_BATCH.format(current_batch_num, total_batches, batch_start_idx)}")
                if stop_requested and stop_requested(): print(language_config.PROCESS_TERMINATED_BY_USER); break

                current_batch_paths = image_paths[batch_start_idx : min(batch_start_idx + batch_size, total_images)]
                batch_images_list = load_images_from_paths(current_batch_paths, stop_requested)
                if stop_requested and stop_requested(): break
                if 'resize_all_with_padding' in globals():
                    batch_images_list, _ = resize_all_with_padding(batch_images_list, method="median")
                if not batch_images_list: print(language_config.SKIP_BATCH_BECAUSE_IMAGE_NOT_LOADED.format(current_batch_num)); continue

                print(language_config.START_IMAGE_ENHANCEMENT.format(len(batch_images_list)))
                try:
                    batch_result_img = image_processor.similarity_mnfr(
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
                        **extra_merging_params
                    )
                except Exception as e_sim_p: traceback.print_exc(); batch_result_img = None
                if stop_requested and stop_requested(): break
                if batch_result_img is not None:
                    processed_batches_results.append(batch_result_img)
                    images_processed_count += len(batch_images_list)
                else:
                    pass

        # 6. Fine-Tuning / Pemrosesan Akhir (jika ada hasil batch)
        if stop_requested and stop_requested(): pass
        elif processed_batches_results and any(res is not None for res in processed_batches_results):
            valid_batch_results = [res for res in processed_batches_results if res is not None]
            if not valid_batch_results:
                 print(language_config.DATA_FAILED_COMPLETION_CREATED)
                 if update_progress: update_progress(100, language_config.DATA_FAILED_COMPLETION_CREATED); return

            num_fine_tuning_inputs = len(valid_batch_results)
            print(f"\n--- {language_config.STARTING_ENHANCEMENT} ({num_fine_tuning_inputs} batch results) using {merging_type_from_settings} ---")
            fine_tuning_start_progress, fine_tuning_end_progress = 95, 99
            
            def fine_tuning_update_progress(inner_progress, message):
                mapped_progress = fine_tuning_start_progress + int((inner_progress / 100.0) * (fine_tuning_end_progress - fine_tuning_start_progress))
                if update_progress and not (stop_requested and stop_requested()):
                    update_progress(mapped_progress, language_config.ENHANCEMENT.format(message))
            if update_progress: update_progress(fine_tuning_start_progress, language_config.STARTING_ENHANCEMENT)
            
            final_weight_map_path_arg = weight_map_output_path if save_final_weight_map else None
            final_result_img = None
            try:
                final_result_img = image_processor.similarity_mnfr(
                    images=valid_batch_results, 
                    merging_type=merging_type_from_settings,
                    tile_size=spatial_tile_size_arg,
                    overlap=spatial_overlap_arg,
                    motion_sensitivity=spatial_motion_sensitivity_arg,
                    noise_offset_factor=spatial_noise_offset_factor_arg,
                    update_progress=fine_tuning_update_progress,
                    stop_requested=stop_requested,
                    save_weight_map_path=final_weight_map_path_arg,
                    total_overall_images=num_fine_tuning_inputs,
                    images_processed_so_far=0, 
                    **extra_merging_params
                )
            except Exception as e_fine: traceback.print_exc(); final_result_img = None
            
            if stop_requested and stop_requested(): pass
            
            elif final_result_img is not None:
                ref_path_for_save = image_paths[0] if image_paths and isinstance(image_paths[0], str) else None
                
                if denoising_method != "none":
                    print(f"Melakukan denoising menggunakan metode: {denoising_method}")
                    sigma_noise_estimate = 0.05 
                    aggressiveness_level = 2.0  # Default, tidak agresif. Coba 1.5, 2.0, 2.5, 3.0 untuk lebih agresif

                    final_result_img = extra_denoising(
                        image=final_result_img,
                        method=denoising_method,
                        sigma=sigma_noise_estimate,
                        bm3d_aggressiveness=aggressiveness_level
                    )

                save_success = save_image(final_result_img, output_path, reference_image_path=ref_path_for_save)
                if save_success:
                    final_msg = f"{language_config.IMAGE_PROCESS_FINISHED}: {os.path.basename(output_path)}"
                    print(final_msg)
                    if update_progress: update_progress(100, final_msg)
                    if not single_process and batch_id is not None and os.path.exists(global_hdf5_path):
                        try: os.remove(global_hdf5_path)
                        except Exception as e_del: 
                            pass
                else:
                    
                    if update_progress: update_progress(100, f"Gagal simpan: {os.path.basename(output_path)}")
            else:
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
        process_finished = True  # set flag ketika proses selesai
        dialog.close()
        worker.quit()  # Berhenti dari thread
        worker.wait()  # Tunggu thread selesai

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