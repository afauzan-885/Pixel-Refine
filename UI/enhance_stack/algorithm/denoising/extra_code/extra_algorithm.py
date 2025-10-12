import ctypes
import os
import cv2
import numpy as np

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import normalize_image, preprocess_in_python

class SimilaritySpatialInterface:
    """
    Membungkus pemanggilan fungsi C++ yang telah dioptimalkan.
    Sekarang HANYA menghasilkan weight_map.
    """
    def __init__(self, lib_path):
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            self.clib = ctypes.CDLL(lib_path)
            if not hasattr(self.clib, 'generate_weight_map_jit'):
                 raise AttributeError("Function 'generate_weight_map_jit' not found in DLL. Check C++ extern \"C\" block.")
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

    def _define_argtypes(self):
        self.clib.generate_weight_map_jit.argtypes = [    
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS, WRITEABLE'), # Arg 1: weight_map_sum_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'),          # Arg 2: current_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),          # Arg 3: reference_image_processed_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),          # base_window_ptr
            ctypes.c_void_p,                                                                # stability_map_ptr
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),          # row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),          # col_starts
            ctypes.c_int, ctypes.c_int, # num_row_starts, num_col_starts
            ctypes.c_int, ctypes.c_int, # tile_h, tile_w
            ctypes.c_int, ctypes.c_int, # h_img, w_img
            ctypes.c_int,               # channels
            ctypes.c_float,             # motion_sensitivity
            ctypes.c_float,             # noise_offset_factor
            ctypes.c_float              # precomputed_ref_noise_sigma
        ]
        self.clib.generate_weight_map_jit.restype = None

    # --- PERBAIKAN KUNCI: Sederhanakan parameter fungsi ---
    def call_generate_weight_map_jit(self, weight_map_sum, current_image, 
                                     reference_image_processed,
                                     base_window, stability_map, row_starts, col_starts,
                                     tile_h, tile_w, h, w, channels, motion_sensitivity, noise_offset_factor, 
                                     precomputed_ref_noise_sigma):
        
        stability_map_ptr = None
        if stability_map is not None:
            if not stability_map.flags['C_CONTIGUOUS']:
                stability_map = np.ascontiguousarray(stability_map)
            stability_map_ptr = stability_map.ctypes.data_as(ctypes.c_void_p)
        
        # --- PERBAIKAN KUNCI: Panggil dengan argumen yang benar ---
        self.clib.generate_weight_map_jit(
            weight_map_sum, current_image, 
            reference_image_processed,
            base_window,
            stability_map_ptr, row_starts, col_starts, len(row_starts), len(col_starts),
            tile_h, tile_w, h, w, channels, motion_sensitivity, noise_offset_factor, 
            precomputed_ref_noise_sigma
        )   
                   
class SimilarityFrequencyInterface:
    """Membungkus pemanggilan fungsi C++ untuk similarity_mfnr_v2."""

    def __init__(self, lib_path):
        """
        Memuat library C++, mendefinisikan argtypes, dan menyimpan objek clib.
        """
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Shared library not found: {lib_path}")
        try:
            self.clib = ctypes.CDLL(lib_path)
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
             raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

    def _define_argtypes(self):
        """Mendefinisikan argtypes untuk semua fungsi C++ yang digunakan."""
      
        # --- Definisi untuk fungsi pertama (sudah benar) ---
        self.clib.accumulate_frame_weighted_jit.restype = None
        self.clib.accumulate_frame_weighted_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # final_image_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # weight_map_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # current_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # reference_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # base_window
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # col_starts
            ctypes.c_int, # num_row_starts
            ctypes.c_int, # num_col_starts
            ctypes.c_int, ctypes.c_int, # tile_h, tile_w
            ctypes.c_int, ctypes.c_int, ctypes.c_int, # h_img, w_img, channels
            ctypes.c_int, ctypes.c_int, # block_h, block_w
            ctypes.c_float
        ]

        # --- [PERBAIKAN] Tambahkan definisi untuk fungsi normalisasi ---
        self.clib.normalize_accumulated_image_jit.restype = None
        self.clib.normalize_accumulated_image_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # final_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # weight_map_sum_ptr
            ctypes.c_int, # h
            ctypes.c_int, # w
            ctypes.c_int  # channels
        ]

    def call_accumulate_frame_weighted(self, clib_instance, final_image_sum, weight_map_sum,
                                     current_image_float, reference_image_float,
                                     base_window, row_starts, col_starts,
                                     tile_h, tile_w, h_ref, w_ref, channels_buffer,
                                     block_h, block_w, 
                                     dft_wiener_c_factor):
        clib_instance.accumulate_frame_weighted_jit( 
            final_image_sum, weight_map_sum,
            current_image_float, reference_image_float,
            base_window, row_starts, col_starts,
            len(row_starts), len(col_starts), 
            tile_h, tile_w,
            h_ref, w_ref, channels_buffer,
            block_h, block_w,
            ctypes.c_float(dft_wiener_c_factor) # Ini juga sudah benar
        )

    def call_normalize_accumulated(self, lib, final_image_sum, weight_map_sum, h, w, channels):
        lib.normalize_accumulated_image_jit(final_image_sum, weight_map_sum, h, w, channels)
        
ALIGN_LIB = None
try:
    lib_path = os.path.join("UI", "data", "alignment_tile.dll") 
    ALIGN_LIB = ctypes.CDLL(lib_path)

    # Definisikan tanda tangan fungsi compute_alignment_flow
    ALIGN_LIB.compute_alignment_flow.restype = ctypes.POINTER(ctypes.c_float)
    ALIGN_LIB.compute_alignment_flow.argtypes = [
        ctypes.POINTER(ctypes.c_float), # ref_work_data
        ctypes.POINTER(ctypes.c_float), # current_work_data
        ctypes.c_int, # work_h
        ctypes.c_int, # work_w
        ctypes.c_int, # tile_h
        ctypes.c_int, # tile_w
        ctypes.c_int, # n_layers
        ctypes.c_float # search_dist
    ]

    # Definisikan tanda tangan fungsi free_flow_memory
    ALIGN_LIB.free_flow_memory.argtypes = [ctypes.POINTER(ctypes.c_float)]
    ALIGN_LIB.free_flow_memory.restype = None

except (OSError, AttributeError) as e:
    ALIGN_LIB = None

def perform_image_alignment(images, reference_image_float, work_res_h, work_res_w,
                            tile_h, tile_w, ref_dtype, update_progress=None, stop_requested=None):
    """
    Alignment in-place dengan preallocated buffer supaya penggunaan RAM stabil.
    """
    if ALIGN_LIB is None:
        print("Error: Library C++ 'alignment_tile.dll' tidak tersedia.")
        if update_progress:
            update_progress(40, "Error: Library C++ tidak ditemukan.")
        return False

    try:
        num_images = len(images)
        if num_images <= 1:
            return True

        # --- Persiapan Referensi ---
        ref_preprocessed, ref_noise = preprocess_in_python(reference_image_float)
        ref_work = cv2.resize(ref_preprocessed, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR)
        if ref_work.dtype != np.float32:
            if np.issubdtype(ref_work.dtype, np.integer):
                ref_work = ref_work.astype(np.float32) / 255.0
            else:
                ref_work = ref_work.astype(np.float32)

        min_layer_res = min(tile_h, tile_w) * 2
        log_arg = min(work_res_h, work_res_w) / min_layer_res if min_layer_res > 0 else 1
        n_layers = max(1, int(np.ceil(np.log2(log_arg))) if log_arg > 0 else 1)

        # --- Preallocate Buffers ---
        flow_shape = (work_res_h, work_res_w, 2)
        flow_buf = np.empty(flow_shape, dtype=np.float32)  # buffer untuk flow
        flow_full_buf = None  # akan dibuat sesuai resolusi asli tiap gambar

        # --- Loop setiap gambar ---
        for i in range(1, num_images):
            if stop_requested and stop_requested():
                return False

            if update_progress:
                progress = 30 + (i / num_images) * 10
                update_progress(int(progress), f"Alignment C++ gambar {i+1}/{num_images}...")

            original_image = images[i]

            # --- Gambar saat ini ---
            current_img_float = normalize_image(original_image, ref_dtype)
            current_preprocessed, current_noise = preprocess_in_python(current_img_float)

            current_work = cv2.resize(current_preprocessed, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR)
            if current_work.dtype != np.float32:
                if np.issubdtype(current_work.dtype, np.integer):
                    current_work = current_work.astype(np.float32) / 255.0
                else:
                    current_work = current_work.astype(np.float32)

            if not ref_work.flags['C_CONTIGUOUS']:
                ref_work = np.ascontiguousarray(ref_work)
            if not current_work.flags['C_CONTIGUOUS']:
                current_work = np.ascontiguousarray(current_work)

            ref_work_ptr = ref_work.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            current_work_ptr = current_work.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

            # --- Panggil backend C++ ---
            flow_ptr = ALIGN_LIB.compute_alignment_flow(
                ref_work_ptr,
                current_work_ptr,
                work_res_h,
                work_res_w,
                tile_h,
                tile_w,
                n_layers,
                1.5
            )

            if flow_ptr:
                try:
                    flow_view = np.ctypeslib.as_array(flow_ptr, shape=flow_shape)
                    np.copyto(flow_buf, flow_view)  # salin ke buffer preallocated
                finally:
                    ALIGN_LIB.free_flow_memory(flow_ptr)
            else:
                print(f"Peringatan: Alignment gagal untuk gambar {i+1}.")
                continue

            # --- Scale flow ke resolusi penuh ---
            full_h, full_w = original_image.shape[:2]
            if (flow_full_buf is None) or (flow_full_buf.shape[0] != full_h or flow_full_buf.shape[1] != full_w):
                flow_full_buf = np.empty((full_h, full_w, 2), dtype=np.float32)

            flow_resized = cv2.resize(flow_buf, (full_w, full_h), interpolation=cv2.INTER_CUBIC)
            flow_resized[:, :, 0] *= full_w / work_res_w
            flow_resized[:, :, 1] *= full_h / work_res_h
            np.copyto(flow_full_buf, flow_resized)

            # --- Warp in-place ---
            aligned_img = cv2.remap(
                original_image,
                (np.arange(full_w)[None, :] + flow_full_buf[:, :, 0]).astype(np.float32),
                (np.arange(full_h)[:, None] + flow_full_buf[:, :, 1]).astype(np.float32),
                interpolation=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REFLECT_101
            )

            images[i] = aligned_img

            # --- Cleanup per frame ---
            del flow_resized, aligned_img
            import gc
            gc.collect()

        return True

    except Exception as e:
        import traceback
        print(f"Error perform_image_alignment_inplace: {e}")
        traceback.print_exc()
        return False

        
def scale_flow_to_full_res(flow, work_h, work_w, full_h, full_w):
    """Scale optical flow dari resolusi kerja ke resolusi penuh dengan interpolasi yang lebih baik."""
    try:
        scale_y = full_h / work_h
        scale_x = full_w / work_w
        
        # Resize flow field menggunakan interpolasi CUBIC untuk hasil yang lebih mulus
        flow_full = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_CUBIC)
        
        # Scale vektor flow
        flow_full[:, :, 0] *= scale_x  # dx
        flow_full[:, :, 1] *= scale_y  # dy
        
        return flow_full
        
    except Exception as e:
        print(f"Error dalam scale_flow_to_full_res_enhanced: {e}")
        return None

def warp_image_opencv(image, flow, interpolation=cv2.INTER_LANCZOS4, border_mode=cv2.BORDER_REFLECT_101):
    """
    Warp gambar menggunakan optical flow dengan opsi untuk interpolasi berkualitas tinggi.
    
    Args:
        image: Gambar input.
        flow: Flow field yang akan digunakan.
        interpolation: Metode interpolasi OpenCV (misalnya, cv2.INTER_LINEAR, cv2.INTER_CUBIC, cv2.INTER_LANCZOS4).
        border_mode: Metode penanganan tepi gambar.
    """
    try:
        h, w = image.shape[:2]
        
        # Buat grid koordinat
        y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
        
        # Terapkan flow
        new_x = x_coords + flow[:, :, 0]
        new_y = y_coords + flow[:, :, 1]
        
        # Remap gambar dengan metode interpolasi yang dipilih
        warped = cv2.remap(image, new_x, new_y, interpolation, borderMode=border_mode)
        
        return warped
        
    except Exception as e:
        print(f"Error dalam warp_image_opencv_enhanced: {e}")
        return image
    