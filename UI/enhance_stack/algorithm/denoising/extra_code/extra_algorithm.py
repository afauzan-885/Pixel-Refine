import ctypes
import os
import cv2
import numpy as np
import numba

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

def perform_image_alignment(images, reference_image_float, work_res_h, work_res_w, 
                            tile_h, tile_w, ref_dtype, update_progress=None, stop_requested=None):
        """
        Melakukan alignment gambar menggunakan optical flow pyramid dengan OpenCV dan NumPy.
        
        Args:
            images: List gambar yang akan di-align
            reference_image_float: Gambar referensi
            work_res_h, work_res_w: Resolusi kerja
            tile_h, tile_w: Ukuran tile untuk alignment
            ref_dtype: Tipe data referensi
            update_progress: Callback untuk update progress
            stop_requested: Callback untuk cek penghentian
        
        Returns:
            List gambar yang sudah di-align atau None jika gagal
        """
        try:
            num_images = len(images)
            if num_images <= 1:
                return images
            
            # Konversi referensi ke grayscale dan resize ke resolusi kerja
            if len(reference_image_float.shape) == 3:
                ref_gray = cv2.cvtColor(reference_image_float, cv2.COLOR_RGB2GRAY)
            else:
                ref_gray = reference_image_float.copy()
            
            ref_work = cv2.resize(ref_gray, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
            
            # Buat pyramid dari gambar referensi
            min_layer_res = min(tile_h, tile_w) * 2  # Ukuran minimum layer pyramid
            n_layers = max(1, int(np.ceil(np.log2(min(work_res_h, work_res_w) / min_layer_res))))
            ref_pyramid = build_pyramid_opencv(ref_work, n_layers)
            
            aligned_images = []
            aligned_images.append(images[0])  # Gambar pertama sebagai referensi
            
            for i in range(1, num_images):
                if stop_requested and stop_requested():
                    return None
                
                if update_progress:
                    progress = 30 + (i / num_images) * 10
                    update_progress(int(progress), f"Alignment gambar {i+1}/{num_images}...")
                
                # Normalisasi dan konversi ke grayscale
                current_img = normalize_image(images[i], ref_dtype)
                if len(current_img.shape) == 3:
                    current_gray = cv2.cvtColor(current_img, cv2.COLOR_RGB2GRAY)
                else:
                    current_gray = current_img.copy()
                
                current_work = cv2.resize(current_gray, (work_res_w, work_res_h), interpolation=cv2.INTER_AREA)
                
                # Buat pyramid dari gambar saat ini
                current_pyramid = build_pyramid_opencv(current_work, n_layers)
                
                # Hitung optical flow menggunakan pyramid
                flow = compute_optical_flow_pyramid(ref_pyramid, current_pyramid, tile_h, tile_w)
                
                if flow is not None:
                    # Warp gambar asli menggunakan flow yang sudah di-scale
                    flow_full_res = scale_flow_to_full_res(flow, work_res_h, work_res_w, 
                                                        images[i].shape[0], images[i].shape[1])
                    aligned_img = warp_image_opencv(images[i], flow_full_res)
                    aligned_images.append(aligned_img)
                else:
                    # Jika alignment gagal, gunakan gambar asli
                    aligned_images.append(images[i])
            
            return aligned_images
            
        except Exception as e:
            print(f"Error dalam proses alignment: {e}")
            return None

def build_pyramid_opencv(image, n_layers):
        """Membuat image pyramid menggunakan OpenCV"""
        pyramid = [image.copy()]
        current_layer = image.copy()
        
        for i in range(n_layers - 1):
            current_layer = cv2.pyrDown(current_layer)
            if current_layer.shape[0] < 16 or current_layer.shape[1] < 16:
                break
            pyramid.append(current_layer)
        
        return pyramid

def compute_optical_flow_pyramid(ref_pyramid, comp_pyramid, tile_h, tile_w, search_dist=2):
    """
    Hitung optical flow menggunakan pyramid coarse-to-fine.
    Fungsi ini menyiapkan jendela Gaussian untuk setiap layer sebelum memanggil
    fungsi refinement yang dikompilasi oleh Numba.
    """
    try:
        n_layers = min(len(ref_pyramid), len(comp_pyramid))
        if n_layers == 0:
            return None
        
        # Mulai dari layer paling kasar (top of the pyramid)
        flow = None
        
        # Loop dari layer terkasar (indeks terbesar) ke terhalus (indeks 0)
        for layer_idx in range(n_layers - 1, -1, -1):
            ref_layer = ref_pyramid[layer_idx]
            comp_layer = comp_pyramid[layer_idx]
            
            # --- Inisialisasi atau Upscaling Flow ---
            if layer_idx == n_layers - 1:
                # Untuk layer paling kasar, mulai dengan flow nol (tidak ada pergerakan)
                flow = np.zeros((ref_layer.shape[0], ref_layer.shape[1], 2), dtype=np.float32)
            else:
                # Untuk layer lainnya, perbesar flow dari layer sebelumnya
                scale_factor = 2.0
                new_h, new_w = ref_layer.shape[:2]
                
                # Periksa jika flow memiliki ukuran valid sebelum resize
                if flow.shape[0] > 0 and flow.shape[1] > 0:
                    flow = cv2.resize(flow, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
                    flow *= scale_factor
                else:
                    # Jika flow sebelumnya tidak valid, buat flow nol baru
                    flow = np.zeros((new_h, new_w, 2), dtype=np.float32)

            # --- PERUBAHAN UTAMA DI SINI ---
            # 1. Tentukan ukuran tile yang sesuai untuk resolusi layer saat ini.
            h, w = ref_layer.shape[:2]
            current_tile_h = min(tile_h, h // 4)
            current_tile_w = min(tile_w, w // 4)
            
            # Pastikan ukuran tile tidak nol
            if current_tile_h <= 0 or current_tile_w <= 0:
                continue # Lanjutkan ke layer berikutnya jika layer ini terlalu kecil

            # 2. Buat jendela Gaussian. Panggilan ini terjadi di Python,
            #    memanfaatkan lru_cache untuk efisiensi jika ukuran yang sama diminta lagi.
            window = gaussian_window((current_tile_h, current_tile_w))

            # 3. Panggil fungsi refinement Numba, sekarang dengan 'window' sebagai argumen.
            #    Perhatikan 'tile_h' dan 'tile_w' tidak lagi dilewatkan ke refine_flow_layer.
            flow = refine_flow_layer(
                ref_layer, 
                comp_layer, 
                flow, 
                window,         # <--- Jendela yang sudah dihitung
                search_dist
            )
        
        return flow
        
    except Exception as e:
        # Menambahkan traceback untuk debugging yang lebih mudah
        import traceback
        print(f"Error dalam compute_optical_flow_pyramid: {e}")
        traceback.print_exc()
        return None


@numba.jit(nopython=True, fastmath=True)
def refine_flow_layer(ref_layer, comp_layer, initial_flow,
                        window, search_dist=2):
    """
    Refine optical flow pada satu layer menggunakan template matching
    dengan blending berbobot Gaussian untuk hasil yang halus dan bebas artefak kotak-kotak.
    """
    h, w = ref_layer.shape[:2]
    
    # --- LOGIKA AKUMULATOR ---
    flow_accumulator = np.zeros((h, w, 2), dtype=np.float32)
    weight_accumulator = np.zeros((h, w), dtype=np.float32)

    current_tile_h, current_tile_w = window.shape
    
    if current_tile_h < 8 or current_tile_w < 8:
        return initial_flow.copy()
    
    step_y = max(current_tile_h // 2, 1)
    step_x = max(current_tile_w // 2, 1)
    
    for y in range(0, h - current_tile_h + 1, step_y):
        for x in range(0, w - current_tile_w + 1, step_x):
            ref_tile = ref_layer[y:y+current_tile_h, x:x+current_tile_w]
            center_y = y + current_tile_h // 2
            center_x = x + current_tile_w // 2
            
            init_dy = int(np.round(initial_flow[center_y, center_x, 1]))
            init_dx = int(np.round(initial_flow[center_y, center_x, 0]))
            
            best_match_score = np.inf
            best_dy, best_dx = init_dy, init_dx
            
            for dy in range(-search_dist, search_dist + 1):
                for dx in range(-search_dist, search_dist + 1):
                    test_y = y + init_dy + dy
                    test_x = x + init_dx + dx
                    
                    if (test_y < 0 or test_x < 0 or 
                        test_y + current_tile_h > h or test_x + current_tile_w > w):
                        continue
                    
                    comp_tile = comp_layer[test_y:test_y+current_tile_h, 
                                        test_x:test_x+current_tile_w]
                    
                    score = np.mean(np.abs(ref_tile.astype(np.float32) - comp_tile.astype(np.float32)))
                    
                    if score < best_match_score:
                        best_match_score = score
                        best_dy, best_dx = init_dy + dy, init_dx + dx
            
            tile_region_flow_acc = flow_accumulator[y:y+current_tile_h, x:x+current_tile_w]
            tile_region_flow_acc[:, :, 0] += best_dx * window
            tile_region_flow_acc[:, :, 1] += best_dy * window
            
            weight_accumulator[y:y+current_tile_h, x:x+current_tile_w] += window

    # --- NORMALISASI AKHIR (VERSI KOMPATIBEL NUMBA) ---
    final_flow = initial_flow.copy()
    epsilon = 1e-6

    # Gunakan loop eksplisit yang akan dikompilasi Numba menjadi sangat cepat
    for r in range(h):
        for c in range(w):
            weight = weight_accumulator[r, c]
            if weight > epsilon:
                final_flow[r, c, 0] = flow_accumulator[r, c, 0] / weight
                final_flow[r, c, 1] = flow_accumulator[r, c, 1] / weight
    
    return final_flow

def scale_flow_to_full_res(flow, work_h, work_w, full_h, full_w):
        """Scale optical flow dari resolusi kerja ke resolusi penuh"""
        try:
            scale_y = full_h / work_h
            scale_x = full_w / work_w
            
            # Resize flow field
            flow_full = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_LINEAR)
            
            # Scale flow vectors
            flow_full[:, :, 0] *= scale_x  # dx
            flow_full[:, :, 1] *= scale_y  # dy
            
            return flow_full
            
        except Exception as e:
            print(f"Error dalam scale_flow_to_full_res: {e}")
            return None

def warp_image_opencv(image, flow):
        """Warp gambar menggunakan optical flow dengan OpenCV"""
        try:
            h, w = image.shape[:2]
            
            # Buat coordinate grids
            y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
            
            # Apply flow
            new_x = x_coords + flow[:, :, 0]
            new_y = y_coords + flow[:, :, 1]
            
            # Remap image
            warped = cv2.remap(image, new_x, new_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            
            return warped
            
        except Exception as e:
            print(f"Error dalam warp_image_opencv: {e}")
            return image
    