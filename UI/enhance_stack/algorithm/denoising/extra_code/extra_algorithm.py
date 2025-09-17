import ctypes
import os
import cv2
import numpy as np

from UI.enhance_stack.algorithm.alignment.alignment_features.global_feature import gaussian_window, normalize_image

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
            # Pastikan nama fungsi di C++ adalah 'generate_weight_map_jit'
            if not hasattr(self.clib, 'generate_weight_map_jit'):
                 raise AttributeError("Function 'generate_weight_map_jit' not found in DLL. Check C++ extern \"C\" block.")
            self._define_argtypes()
        except OSError as e:
            raise OSError(f"Error loading shared library {lib_path}: {e}")
        except AttributeError as e:
            raise AttributeError(f"Function not found in DLL or error setting argtypes. Did you compile C++ correctly? Error: {e}")

    def _define_argtypes(self):
        # --- PERBAIKAN KUNCI: Sesuaikan dengan signature C++ yang baru ---
        self.clib.generate_weight_map_jit.argtypes = [
            # HAPUS: np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='...'), # final_image_sum_ptr
            
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
            # HAPUS: final_image_sum
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

    # ... sisa kelas (call_accumulate_frame_weighted dan call_normalize_accumulated) tidak perlu diubah ...
    # Metode call_normalize_accumulated Anda sudah benar.
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
    Melakukan alignment gambar secara IN-PLACE menggunakan backend C++ via ctypes.
    Fungsi ini memodifikasi list 'images' yang diberikan.
    
    Returns:
        Boolean: True jika berhasil, False jika gagal atau dibatalkan.
    """
    # Langkah 0: Periksa apakah library C++ berhasil dimuat
    if ALIGN_LIB is None:
        print("Error Kritis: Library C++ 'alignment_engine.dll' tidak tersedia. Proses alignment dibatalkan.")
        # Beri tahu pengguna melalui progress bar jika memungkinkan
        if update_progress:
            update_progress(40, "Error: Library C++ tidak ditemukan.")
        return False

    try:
        num_images = len(images)
        if num_images <= 1:
            return True

        # --- LANGKAH 1: Persiapan Gambar Referensi (dilakukan sekali di Python) ---
        if len(reference_image_float.shape) == 3:
            ref_gray = cv2.cvtColor(reference_image_float, cv2.COLOR_RGB2GRAY)
        else:
            ref_gray = reference_image_float.copy()

        # Buat gambar kerja float32, yang akan dikirim ke C++
        ref_work = cv2.resize(ref_gray, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR)
        if ref_work.dtype != np.float32:
            # Jika hasil normalize bukan float, konversi di sini. Asumsikan skala 0-1.
            if np.issubdtype(ref_work.dtype, np.integer):
                 ref_work = ref_work.astype(np.float32) / 255.0
            else:
                 ref_work = ref_work.astype(np.float32)

        # Hitung jumlah layer piramida untuk dikirim ke C++
        min_layer_res = min(tile_h, tile_w) * 2
        # Tambahkan pengaman untuk log(0)
        log_arg = min(work_res_h, work_res_w) / min_layer_res if min_layer_res > 0 else 1
        n_layers = max(1, int(np.ceil(np.log2(log_arg))) if log_arg > 0 else 1)
        
        # --- LANGKAH 2: Loop Melalui Setiap Gambar untuk Diselaraskan ---
        for i in range(1, num_images):
            if stop_requested and stop_requested():
                return False # Proses dibatalkan oleh pengguna
            
            if update_progress:
                progress = 30 + (i / num_images) * 10
                update_progress(int(progress), f"Alignment C++ gambar {i+1}/{num_images}...")
            
            original_image = images[i]
            
            # --- Persiapan Gambar Saat Ini (dilakukan di Python) ---
            current_img_float = normalize_image(original_image, ref_dtype)
            if len(current_img_float.shape) == 3:
                current_gray = cv2.cvtColor(current_img_float, cv2.COLOR_RGB2GRAY)
            else:
                current_gray = current_img_float.copy()
            
            current_work = cv2.resize(current_gray, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR)
            if current_work.dtype != np.float32:
                if np.issubdtype(current_work.dtype, np.integer):
                    current_work = current_work.astype(np.float32) / 255.0
                else:
                    current_work = current_work.astype(np.float32)

            # --- LANGKAH 3: Panggilan ke Mesin C++ ---
            # Pastikan array bersifat C-contiguous untuk keamanan
            if not ref_work.flags['C_CONTIGUOUS']:
                ref_work = np.ascontiguousarray(ref_work)
            if not current_work.flags['C_CONTIGUOUS']:
                current_work = np.ascontiguousarray(current_work)
            
            # Dapatkan pointer ke buffer data NumPy
            ref_work_ptr = ref_work.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
            current_work_ptr = current_work.ctypes.data_as(ctypes.POINTER(ctypes.c_float))

            # Panggil fungsi C++
            flow_ptr = ALIGN_LIB.compute_alignment_flow(
                ref_work_ptr,
                current_work_ptr,
                work_res_h,
                work_res_w,
                tile_h,
                tile_w,
                n_layers,
                1.5  # search_dist, bisa dijadikan parameter
            )
            
            flow = None
            if flow_ptr:
                try:
                    # Ubah pointer C kembali menjadi array NumPy
                    flow_shape = (work_res_h, work_res_w, 2)
                    # Buat salinan! Penting agar kita bisa membebaskan memori C++
                    flow = np.ctypeslib.as_array(flow_ptr, shape=flow_shape).copy()
                finally:
                    # SANGAT PENTING: Selalu bebaskan memori C++, bahkan jika ada error
                    ALIGN_LIB.free_flow_memory(flow_ptr)
            
            # --- LANGKAH 4: Proses Hasil (kembali di Python) ---
            if flow is not None:
                # Skalakan flow ke resolusi penuh
                flow_full_res = scale_flow_to_full_res(flow, work_res_h, work_res_w, 
                                                       original_image.shape[0], original_image.shape[1])
                
                # Warp gambar asli menggunakan flow yang sudah dihitung
                aligned_img = warp_image_opencv(original_image, flow_full_res)
                
                # Modifikasi list input secara in-place
                images[i] = aligned_img
            else:
                print(f"Peringatan: Alignment C++ gagal untuk gambar {i+1}. Menggunakan gambar asli.")

        return True # Sukses
        
    except Exception as e:
        # Menambahkan traceback untuk debugging yang lebih mudah
        import traceback
        print(f"Error dalam proses alignment C++: {e}")
        traceback.print_exc()
        return False # Mengindikasikan kegagalan
        
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