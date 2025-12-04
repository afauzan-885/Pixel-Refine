import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
import gc
import math
import os
import time
import traceback
import cv2
import numpy as np
import onnxruntime as ort

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
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS, WRITEABLE'), # weight_map_sum (2D)
            np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),                    # current_image (flattened 1D/3D OK)
            np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),                    # reference_image_processed
            np.ctypeslib.ndpointer(dtype=np.float32, flags='C_CONTIGUOUS'),                    # base_window
            ctypes.c_void_p,                                                                   # stability_map_ptr
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),              # row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),              # col_starts
            ctypes.c_int, ctypes.c_int,                                                        # num_row_starts, num_col_starts
            ctypes.c_int, ctypes.c_int,                                                        # tile_h, tile_w
            ctypes.c_int, ctypes.c_int,                                                        # h_img, w_img
            ctypes.c_int,                                                                      # channels
            ctypes.c_float,                                                                    # motion_sensitivity
            ctypes.c_float,                                                                    # noise_offset_factor
            ctypes.c_float                                                                     # precomputed_ref_noise_sigma
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
    """Membungkus pemanggilan fungsi C++ untuk similarity_mfnr_v2 (Frequency Merging)."""

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
      
        # --- Definisi untuk accumulate_frame_weighted_jit ---
        self.clib.accumulate_frame_weighted_jit.restype = None
        self.clib.accumulate_frame_weighted_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # 0: final_image_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # 1: weight_map_sum
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # 2: current_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # 3: reference_image
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # 4: base_window
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # 5: row_starts
            np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags='C_CONTIGUOUS'),   # 6: col_starts
            ctypes.c_int, # 7: num_row_starts
            ctypes.c_int, # 8: num_col_starts
            ctypes.c_int, ctypes.c_int, # 9, 10: tile_h, tile_w
            ctypes.c_int, ctypes.c_int, ctypes.c_int, # 11, 12, 13: h_img, w_img, channels
            ctypes.c_int, ctypes.c_int, # 14, 15: block_h, block_w
            ctypes.c_float, # 16: dft_wiener_c_factor
            ctypes.c_float  # 17: estimated_noise_sigma_for_block (BARU)
        ]

        # --- Definisi untuk fungsi normalisasi ---
        self.clib.normalize_accumulated_image_jit.restype = None
        self.clib.normalize_accumulated_image_jit.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=3, flags='C_CONTIGUOUS'), # final_image_ptr
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'), # weight_map_sum_ptr
            ctypes.c_int, # h
            ctypes.c_int, # w
            ctypes.c_int  # channels
        ]

    # MODIFIKASI: Menambahkan noise_sigma ke parameter fungsi Python
    def call_accumulate_frame_weighted(self, clib_instance, final_image_sum, weight_map_sum,
                                     current_image_float, reference_image_float,
                                     base_window, row_starts, col_starts,
                                     tile_h, tile_w, h_ref, w_ref, channels_buffer,
                                     block_h, block_w, 
                                     dft_wiener_c_factor,
                                     ref_noise_sigma): # <--- ARGUMEN BARU
        
        clib_instance.accumulate_frame_weighted_jit( 
            final_image_sum, weight_map_sum,
            current_image_float, reference_image_float,
            base_window, row_starts, col_starts,
            len(row_starts), len(col_starts), 
            tile_h, tile_w,
            h_ref, w_ref, channels_buffer,
            block_h, block_w,
            ctypes.c_float(dft_wiener_c_factor),
            ctypes.c_float(ref_noise_sigma) # <--- Meneruskan noise sigma
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
    
class ONNXSessionManager:
    """
    Sebuah Context Manager untuk memastikan session ONNX dan sumber daya GPU
    selalu dilepaskan dengan benar, bahkan jika terjadi error.
    """
    def __init__(self, model_path):
        self.model_path = model_path
        self.session = None
        # print("ONNXSessionManager: Inisialisasi.") # Pesan ini bisa dihapus agar tidak terlalu ramai

    def __enter__(self):
        """Dipanggil saat memasuki blok 'with'. Memuat model dan mengembalikan session."""
        # print("ONNXSessionManager: Memasuki blok 'with', memuat model...")
        self.session = self._initialize_raft_model(self.model_path)
        if self.session is None:
            # Jika _initialize_raft_model mengembalikan None, berarti gagal.
            raise RuntimeError(f"Gagal memuat atau menginisialisasi model ONNX dari {self.model_path}")
        
        # Mengembalikan objek session yang valid
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Dipanggil saat keluar dari blok 'with'. Menjamin pelepasan sumber daya."""
        # print("ONNXSessionManager: Keluar dari blok 'with', melepaskan sumber daya GPU...")
        if exc_type:
            print(f"ONNXSessionManager: Exception terjadi di dalam blok: {exc_val}")
        
        if self.session is not None:
            self.session = None
        
        gc.collect()
        # print("ONNXSessionManager: Sumber daya GPU seharusnya sudah dilepaskan.")

    def _initialize_raft_model(self, model_path):
        """
        Memuat session ONNX RAFT dengan logging minimal (hanya error fatal).

        Returns:
            ort.InferenceSession atau None jika gagal.
        """
        try:
            # print(f"Mencoba memuat model ONNX RAFT dari: {model_path}")
            available_providers = ort.get_available_providers()

            preferred_providers = [
                ('DmlExecutionProvider', {'device_id': 1}),
                ('CUDAExecutionProvider', {'device_id': 1}),
                'CPUExecutionProvider'
            ]

            # Filter provider yang tersedia
            providers_to_try = [
                p for p in preferred_providers
                if (p if isinstance(p, str) else p[0]) in available_providers
            ]

            if not providers_to_try:
                raise RuntimeError("Tidak ada provider ONNX Runtime yang tersedia.")

            # print(f"Provider yang tersedia dan akan dicoba: {[p if isinstance(p, str) else p[0] for p in providers_to_try]}")

            # SessionOptions dengan logging minimal
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.log_severity_level = 3  # 0=VERBOSE, 1=INFO, 2=WARNING, 3=ERROR, 4=FATAL

            # Buat session
            session = ort.InferenceSession(model_path, providers=providers_to_try, sess_options=session_options)
            # print(f"Model RAFT berhasil dimuat menggunakan: {session.get_providers()[0]}")

            return session

        except Exception as e:
            # print(f"Error fatal saat memuat model ONNX: {e}")
            traceback.print_exc()
            return None

# --- Global variable untuk menyimpan session ONNX agar tidak di-load berulang kali ---
MODEL_SESSION = None
FLOW_MODEL_PATH = "database/Learning_Model/optical_flow_estimation_raft_2023aug_int8bq.onnx" # Ganti dengan path model ONNX Anda

# ==============================================================================
# === BAGIAN A: Fungsi Helper Baru untuk ONNX RAFT
# ==============================================================================
def process_single_tile_resized(args, stop_requested=None):
    """
    Worker yang memproses satu tile (sudah di-resize sesuai ukuran model).
    """
    ref_tile_resized, current_tile_resized, session, original_coords = args
    if stop_requested and stop_requested():
        return None
    raw_flow_tile = compute_flow_with_raft(ref_tile_resized, current_tile_resized, session)
    if raw_flow_tile is None:
        return None

    model_h, model_w, _ = ref_tile_resized.shape
    h_flow, w_flow, _ = raw_flow_tile.shape
    if (h_flow != model_h) or (w_flow != model_w):
        flow_tile = scale_flow_to_full_res(raw_flow_tile, h_flow, w_flow, model_h, model_w)
    else:
        flow_tile = raw_flow_tile

    return (flow_tile, original_coords)

def create_blending_weights(tile_h, tile_w, overlap_h, overlap_w):
    """
    Membuat peta bobot blending 2D (smooth window) agar transisi antar tile halus.
    """
    y_ramp_up = np.linspace(0.0, 1.0, overlap_h, dtype=np.float32)
    y_ramp_down = np.linspace(1.0, 0.0, overlap_h, dtype=np.float32)
    y_flat = np.ones(tile_h - 2 * overlap_h, dtype=np.float32)
    y_weights = np.concatenate([y_ramp_up, y_flat, y_ramp_down])

    x_ramp_up = np.linspace(0.0, 1.0, overlap_w, dtype=np.float32)
    x_ramp_down = np.linspace(1.0, 0.0, overlap_w, dtype=np.float32)
    x_flat = np.ones(tile_w - 2 * overlap_w, dtype=np.float32)
    x_weights = np.concatenate([x_ramp_up, x_flat, x_ramp_down])

    weights_2d = y_weights[:, None] * x_weights[None, :]
    return weights_2d[:, :, None]

def compute_flow_raft(ref_img, current_img, session,
                                         grid_rows=2, grid_cols=2,
                                         model_input_size=(360, 480),
                                         overlap_ratio=0.1, progress_callback=None,
                                         stop_requested=None):
    """
    Menghitung optical flow dengan pembagian tile grid dinamis.
    Mendukung callback progres per tile untuk update progress UI secara real-time.

    Args:
        ref_img, current_img: np.uint8 [H, W, 3]
        session: ONNX session RAFT
        grid_rows, grid_cols: jumlah pembagian grid (vertikal x horizontal)
        model_input_size: resolusi model RAFT (H, W)
        overlap_ratio: proporsi overlap antar tile (0–1)
        progress_callback: callable(done_tiles, total_tiles) opsional
    Returns:
        final_flow: np.float32 [H, W, 2]
    """
    if session is None:
        print("❌ Session RAFT tidak tersedia.")
        return None

    full_h, full_w, _ = ref_img.shape
    model_h, model_w = model_input_size

    # --- Hitung ukuran tile dasar dan overlap ---
    tile_h = math.ceil(full_h / grid_rows)
    tile_w = math.ceil(full_w / grid_cols)
    overlap_h = math.ceil(tile_h * overlap_ratio)
    overlap_w = math.ceil(tile_w * overlap_ratio)

    # --- Buat koordinat tile dengan overlap ---
    coords = []
    for r in range(grid_rows):
        for c in range(grid_cols):
            y_start = max(0, r * tile_h - overlap_h)
            y_end = min(full_h, (r + 1) * tile_h + overlap_h)
            x_start = max(0, c * tile_w - overlap_w)
            x_end = min(full_w, (c + 1) * tile_w + overlap_w)
            coords.append((y_start, x_start, y_end, x_end))

    total_tiles = len(coords)
    # print(f"🧩 Memproses grid {grid_rows}x{grid_cols} (total {total_tiles} tile)...")

    # --- Penampung hasil sementara ---
    final_flow = np.zeros((full_h, full_w, 2), dtype=np.float32)
    weight_acc = np.zeros((full_h, full_w, 1), dtype=np.float32)

    # --- Proses tile satu per satu ---
    for tile_idx, (y_start, x_start, y_end, x_end) in enumerate(coords, 1):
        if stop_requested and stop_requested():
            # print(f"⏹ Stop requested, tile {tile_idx}/{total_tiles} dihentikan")
            return None
        try:
            # Ambil tile asli
            ref_tile = ref_img[y_start:y_end, x_start:x_end]
            cur_tile = current_img[y_start:y_end, x_start:x_end]

            # Resize agar sesuai model
            ref_tile_resized = cv2.resize(ref_tile, (model_w, model_h), interpolation=cv2.INTER_AREA)
            cur_tile_resized = cv2.resize(cur_tile, (model_w, model_h), interpolation=cv2.INTER_AREA)

            # Jalankan inferensi RAFT
            flow_model_res = process_single_tile_resized((ref_tile_resized, cur_tile_resized, session, (y_start, x_start, y_end, x_end)))
            if flow_model_res is None:
                print(f"⚠️ Gagal menghitung flow pada tile {tile_idx}/{total_tiles}")
                continue

            flow_res, (y_start, x_start, y_end, x_end) = flow_model_res
            orig_h, orig_w = y_end - y_start, x_end - x_start

            # Skala kembali flow ke ukuran tile asli
            flow_orig = scale_flow_to_full_res(flow_res, model_h, model_w, orig_h, orig_w)

            # Buat blending mask agar tepi tile halus
            blending = create_blending_weights(
                orig_h, orig_w,
                min(overlap_h, orig_h // 2),
                min(overlap_w, orig_w // 2)
            )

            final_flow[y_start:y_end, x_start:x_end] += flow_orig * blending
            weight_acc[y_start:y_end, x_start:x_end] += blending

            # Laporkan progress per tile ke callback
            if progress_callback is not None:
                progress_callback(tile_idx, total_tiles)

        except Exception as e:
            print(f"❌ Error tile {tile_idx}/{total_tiles}: {e}")

    # --- Normalisasi hasil gabungan ---
    final_flow /= (weight_acc + 1e-8)

    return final_flow

def compute_flow_with_raft(ref_img, current_img, session):
    """
    Menghitung optical flow menggunakan model RAFT ONNX.
    Gambar input harus dalam format (H, W, C) dengan nilai [0, 255].
    """
    if session is None:
        return None
    try:
        # RAFT ONNX biasanya mengharapkan input (1, 3, H, W) dengan tipe float32
        # 1. Ubah HWC -> CHW
        ref_tensor = np.transpose(ref_img, (2, 0, 1))
        current_tensor = np.transpose(current_img, (2, 0, 1))

        # 2. Tambahkan batch dimension (1, C, H, W) dan pastikan float32
        ref_tensor = np.expand_dims(ref_tensor, axis=0).astype('float32')
        current_tensor = np.expand_dims(current_tensor, axis=0).astype('float32')

        # 3. Jalankan inferensi
        input_names = [inp.name for inp in session.get_inputs()]
        ort_inputs = {input_names[0]: ref_tensor, input_names[1]: current_tensor}
        ort_outs = session.run(None, ort_inputs)

        # 4. Proses output
        # Output flow biasanya (1, 2, H, W). Kita ubah ke (H, W, 2)
        flow = ort_outs[0][0] # Ambil hasil pertama, buang batch dimension
        flow = np.transpose(flow, (1, 2, 0)) # Ubah 2,H,W -> H,W,2
        return flow

    except Exception as e:
        print(f"Error saat menjalankan inferensi RAFT: {e}")
        return None

# ==============================================================================
# === BAGIAN B: Fungsi Helper yang Sudah Anda Sediakan (sedikit disempurnakan)
# ==============================================================================
def scale_flow(flow, work_h, work_w, full_h, full_w, ksize=5):
    """
    Scale flow dengan interpolasi linear biasa, lalu dihaluskan dengan Median Filter.
    Cocok untuk menghilangkan noise 'salt-and-pepper' pada flow field.
    """
    scale_x = full_w / work_w
    scale_y = full_h / work_h

    # 1. Resize (Interpolasi Biasa - Linear sangat cepat)
    flow_full = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_LINEAR)

    # 2. Skalakan nilainya
    flow_full *= np.array([scale_x, scale_y], dtype=np.float32)

    # 3. Median Filter
    # MedianBlur OpenCV biasanya support 1, 3, atau 4 channel. 
    # Optical flow punya 2 channel, jadi lebih aman dipisah dulu.
    u = flow_full[..., 0]
    v = flow_full[..., 1]

    # ksize harus ganjil (3, 5, 7). Semakin besar, semakin halus tapi detail gerakan mikro bisa hilang.
    # ksize=5 adalah keseimbangan yang bagus.
    u_smooth = cv2.medianBlur(u, ksize)
    v_smooth = cv2.medianBlur(v, ksize)

    return np.dstack((u_smooth, v_smooth))

def scale_flow_to_full_res(flow, work_h, work_w, full_h, full_w):
    """
    Versi OPTIMASI: Scale optical flow dari resolusi kerja ke resolusi penuh.
    Menggunakan INTER_LINEAR untuk kecepatan maksimal dengan akurasi yang cukup.
    """
    # Hitung faktor skala
    scale_x = full_w / work_w
    scale_y = full_h / work_w # Note: Pastikan pembagi sesuai (work_w untuk x, work_h untuk y)
    # Koreksi baris di atas pada implementasi Anda sebelumnya mungkin terbalik/rancu,
    # Standardnya: scale_y = full_h / work_h, scale_x = full_w / work_w
    
    scale_y = full_h / work_h
    scale_x = full_w / work_w

    # OPTIMASI 1: Gunakan INTER_LINEAR (Jauh lebih cepat dari CUBIC/LANCZOS)
    flow_full = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_LINEAR)

    # OPTIMASI 2: Perkalian vektor (Broadcasting) daripada slicing satu per satu
    # Ini memanfaatkan instruksi SIMD pada CPU modern
    flow_full *= np.array([scale_x, scale_y], dtype=np.float32)

    return flow_full

def warp_image_opencv(image, flow, interpolation=cv2.INTER_CUBIC, border_mode=cv2.BORDER_REFLECT_101):
    """Warp gambar menggunakan optical flow."""
    h, w = image.shape[:2]
    y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
    new_x = x_coords + flow[:, :, 0]
    new_y = y_coords + flow[:, :, 1]
    warped = cv2.remap(image, new_x, new_y, interpolation, borderMode=border_mode)
    return warped

# ==============================================================================
# === BAGIAN C: Fungsi Utama yang Dimodifikasi
# ==============================================================================
def visualize_flow(flow):
    """
    Mengubah peta optical flow menjadi citra berwarna untuk visualisasi.
    Warna menunjukkan arah, kecerahan menunjukkan magnitudo.
    """
    h, w = flow.shape[:2]
    flow_uv = np.zeros((h, w, 2), dtype=np.float32)
    flow_uv[..., 0] = flow[..., 0]
    flow_uv[..., 1] = flow[..., 1]
    magnitude, angle = cv2.cartToPolar(flow_uv[..., 0], flow_uv[..., 1])
    hsv = np.zeros((h, w, 3), dtype=np.float32)
    hsv[..., 0] = (angle * 180 / np.pi) / 2  # arah → hue
    hsv[..., 1] = 1.0                         # saturasi penuh
    hsv[..., 2] = cv2.normalize(magnitude, None, 0.0, 1.0, cv2.NORM_MINMAX)
    flow_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return (flow_bgr * 255).astype(np.uint8)

def save_aligned_image(aligned_img, index, backend_name, save_folder="save_align_image"):
    """
    Menyimpan gambar RGB yang telah diselaraskan ke folder output dengan normalisasi dinamis.
    """
    if aligned_img is None:
        return

    # Tangani nilai NaN atau Inf
    aligned_img = np.nan_to_num(aligned_img)

    # Normalisasi berdasarkan nilai maksimum aktual
    max_val = np.max(aligned_img)
    if max_val > 0:
        norm_img = aligned_img / max_val
    else:
        norm_img = np.zeros_like(aligned_img)

    # Konversi ke uint8
    save_img = np.clip(norm_img * 255, 0, 255).astype(np.uint8)

    # Buat folder jika belum ada
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    # Buat nama file
    filename = f"aligned_{backend_name}_frame_{index:02d}.jpg"
    output_path = os.path.join(save_folder, filename)

    # Jangan konversi ke BGR — simpan langsung sebagai RGB
    cv2.imwrite(output_path, save_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    print(f"  [Save] {filename} disimpan sebagai RGB.")

def perform_image_alignment(images, reference_image_float, work_res_h, work_res_w,
                            tile_h, tile_w, ref_dtype, update_progress=None, stop_requested=None,
                            use_raft=False, num_alignment_workers=2, visualization=False,
                            save_align_image=False):
    """
    Menyelaraskan (align) gambar dengan manajemen sumber daya yang aman,
    menggunakan paralelisasi untuk RAFT (GPU) atau C++ (CPU/Legacy).
    """
    
    num_images = len(images)
    if num_images <= 1:
        return True

    # --- Preprocessing referensi (Dilakukan 1x di thread utama) ---
    ref_preprocessed_cpp = preprocess_in_python(reference_image_float, use_raft=False)
    ref_work_gray_cpp = cv2.resize(ref_preprocessed_cpp, (work_res_w, work_res_h),
                                interpolation=cv2.INTER_LINEAR).astype(np.float32)
    ref_work_gray_cpp = np.ascontiguousarray(ref_work_gray_cpp)
    ref_work_ptr = ref_work_gray_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    del ref_preprocessed_cpp

    # Siapkan variabel konfigurasi C++ (jika dibutuhkan)
    min_layer_res = min(tile_h, tile_w) * 2
    log_arg = min(work_res_h, work_res_w) / min_layer_res if min_layer_res > 0 else 1
    n_layers = max(1, int(np.ceil(np.log2(log_arg))) if log_arg > 0 else 1)


    # === BACKEND RAFT (GPU, multi-thread) ===
    if use_raft:
        print(f"Memulai alignment menggunakan backend RAFT dengan {num_alignment_workers} worker paralel...")

        try:
            # RAFT memerlukan sesi ONNX dan referensi gambar warna penuh
            with ONNXSessionManager(FLOW_MODEL_PATH) as MODEL_SESSION:
                ref_full_color_raft = (reference_image_float * 255).astype(np.uint8)
                model_input_size = (360, 480)
                grid_rows, grid_cols = 2, 2

                # --- Fungsi untuk 1 tugas alignment RAFT (dijalankan di worker) ---
                def process_single_alignment_raft(i, original_image, ref_full_color_raft, 
                                                  MODEL_SESSION, ref_dtype, stop_requested=None):
                    
                    if stop_requested and stop_requested(): return (i, None)
                    
                    current_img_float = normalize_image(original_image, ref_dtype)
                    current_full_color_raft = np.clip(current_img_float * 255, 0, 255).astype(np.uint8)

                    flow_full_res = compute_flow_raft(
                        ref_full_color_raft,
                        current_full_color_raft,
                        MODEL_SESSION,
                        grid_rows=grid_rows,
                        grid_cols=grid_cols,
                        model_input_size=model_input_size,
                        overlap_ratio=0.2,
                        stop_requested=stop_requested
                    )
                    
                    aligned_img = None
                    if flow_full_res is not None:
                        aligned_img = warp_image_opencv(original_image, flow_full_res)
                        if visualization:
                            flow_vis = visualize_flow(flow_full_res)
                            cv2.imwrite(f"flow_raft_{i+1:02d}.jpg", flow_vis)

                    return (i, aligned_img)

                # --- Jalankan paralel dengan ThreadPoolExecutor ---
                with ThreadPoolExecutor(max_workers=num_alignment_workers) as executor:
                    futures = {}
                    processed_count = 0
                    
                    for i in range(1, num_images):
                        if stop_requested and stop_requested():
                            executor.shutdown(wait=False, cancel_futures=True)
                            return False

                        if i > 1:
                            # Opsional: jeda 2 detik antar submit worker (untuk manajemen memori/GPU)
                            time.sleep(2.0) 

                        future = executor.submit(
                            process_single_alignment_raft, 
                            i, images[i], ref_full_color_raft, 
                            MODEL_SESSION, ref_dtype, 
                            stop_requested=stop_requested
                        )
                        futures[future] = i

                    for future in as_completed(futures):
                        i = futures[future]
                        if stop_requested and stop_requested():
                            executor.shutdown(wait=False, cancel_futures=True)
                            return False

                        try:
                            idx, aligned_img = future.result()
                            if aligned_img is not None:
                                # Tulis hasil alignment kembali ke list utama
                                images[idx] = aligned_img
                                
                                # <<< INTEGRASI SAVE IMAGE C++ >>>
                                if save_align_image:
                                    # Panggil save_aligned_image di sini
                                    save_aligned_image(aligned_img, idx, "CPP")
                                # <<< AKHIR INTEGRASI >>>
                                
                            else:
                                print(f"Peringatan: Alignment RAFT gagal untuk gambar {i+1}.")
                        except Exception as e:
                            print(f"❌ Worker RAFT gagal untuk gambar {i+1}: {e}")

                        processed_count += 1
                        if update_progress:
                            progress = 30 + (processed_count / (num_images - 1)) * 10
                            update_progress(int(progress), f"Alignment gambar {processed_count}/{num_images - 1} (RAFT)...")

                        gc.collect()

            print("✅ Alignment GPU RAFT selesai.")
            return True

        except Exception as e:
            print(f"Error kritis selama RAFT: {e}")
            traceback.print_exc()
            return False

    # =================================================================
    # === BACKEND C++ (grayscale legacy) - PARALEL ===
    # =================================================================
    else:
        if ALIGN_LIB is None:
            error_msg = "Error: Backend C++ dipilih tetapi library 'alignment_tile.dll' tidak tersedia."
            print(error_msg)
            if update_progress: update_progress(0, error_msg)
            return False
            
        try:
            # --- Fungsi untuk 1 tugas alignment C++ (dijalankan di worker) ---
            def process_single_alignment_cpp(i, 
                                             ref_work_ptr, work_res_h, work_res_w, 
                                             tile_h, tile_w, n_layers, 
                                             original_image, ref_dtype, 
                                             ALIGN_LIB, stop_requested,
                                             full_res_reference_image): 
                
                if stop_requested and stop_requested():
                    return (i, None)
                    
                flow_ptr = None
                
                # Buffer lokal yang harus dibersihkan setelah digunakan
                current_work_gray_cpp = None 
                
                try:
                    # 1. Preprocess Gambar Saat Ini
                    current_img_float = normalize_image(original_image, ref_dtype)
                    current_preprocessed_cpp= preprocess_in_python(current_img_float, use_raft=False)
                    current_work_gray_cpp = cv2.resize(current_preprocessed_cpp, (work_res_w, work_res_h),
                                                    interpolation=cv2.INTER_LINEAR).astype(np.float32)

                    current_work_gray_cpp = np.ascontiguousarray(current_work_gray_cpp)
                    current_work_ptr = current_work_gray_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
                    
                    # 2. Panggil fungsi C++
                    flow_ptr = ALIGN_LIB.compute_alignment_flow(
                        ref_work_ptr, current_work_ptr,
                        work_res_h, work_res_w,
                        tile_h, tile_w, n_layers, 2.0
                    )
                
                except Exception as e:
                    print(f"Error C++ setup/call for image {i+1}: {e}")
                    return (i, None)
                    
                finally:
                    # Pastikan referensi Python lokal dibersihkan
                    del current_work_gray_cpp, current_preprocessed_cpp, current_img_float
                
                aligned_img = None
                
                if flow_ptr:
                    try:
                        # 3. Baca Flow dan Rescale
                        flow_buf_cpp = np.empty((work_res_h, work_res_w, 2), dtype=np.float32)
                        ctypes.memmove(flow_buf_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float)), flow_ptr, flow_buf_cpp.nbytes)
                        
                        full_h, full_w = original_image.shape[:2]
                        
                        # === PERUBAHAN DI SINI ===
                        # Ganti scale_flow_to_full_res dengan scale_flow
                        # ksize=5 cukup ampuh hilangkan noise tanpa merusak gerakan besar
                        flow_full_res = scale_flow(flow_buf_cpp, work_res_h, work_res_w, full_h, full_w, ksize=5)
                        # =========================
                        
                        if visualization:
                            flow_vis = visualize_flow(flow_full_res)
                            cv2.imwrite(f"flow_cpp_{i+1:02d}.jpg", flow_vis)

                        # 4. Warp Gambar
                        aligned_img = warp_image_opencv(original_image, flow_full_res)

                    except Exception as e:
                        print(f"Error processing flow result for image {i+1}: {e}")
                    finally:
                        # 5. Pastikan C++ free memori yang dialokasikan
                        if flow_ptr:
                            ALIGN_LIB.free_flow_memory(flow_ptr)
                
                return (i, aligned_img)

            # --- Jalankan paralel dengan ThreadPoolExecutor ---
            with ThreadPoolExecutor(max_workers=num_alignment_workers) as executor:
                futures = {}
                processed_count = 0
                
                # Kirim tugas ke executor (Mulai dari indeks 1, karena indeks 0 adalah referensi)
                for i in range(1, num_images):
                    if stop_requested and stop_requested():
                        executor.shutdown(wait=False, cancel_futures=True)
                        return False

                    # --- PENAMBAHAN JEDA DI SINI ---
                    if i > 1:
                        time.sleep(0.1)
                    # ------------------------------

                    future = executor.submit(
                        process_single_alignment_cpp, 
                        i, 
                        ref_work_ptr, work_res_h, work_res_w, 
                        tile_h, tile_w, n_layers, 
                        images[i], ref_dtype, 
                        ALIGN_LIB, stop_requested,
                        # --- PASS PARAMETER BARU ---
                        reference_image_float 
                    )
                    futures[future] = i

                # Kumpulkan hasil (di thread utama)
                for future in as_completed(futures):
                    i = futures[future]
                    if stop_requested and stop_requested():
                        executor.shutdown(wait=False, cancel_futures=True)
                        return False

                    try:
                        idx, aligned_img = future.result()
                        if aligned_img is not None:
                            images[idx] = aligned_img
                            
                            # <<< INTEGRASI SAVE IMAGE RAFT >>>
                            if save_align_image:
                                save_aligned_image(aligned_img, idx, "RAFT")
                            # <<< AKHIR INTEGRASI >>>
                            
                        else:
                            # Jika worker gagal/dibatalkan, gunakan gambar asli
                            pass 
                            
                        processed_count += 1
                        
                    except Exception as e:
                        print(f"❌ Worker C++ gagal untuk gambar {i+1} (saat fetch result): {e}")
                        
                    if update_progress:
                        progress = 30 + (processed_count / (num_images - 1)) * 10 
                        update_progress(int(progress), f"Alignment gambar {processed_count}/{num_images - 1} (C++)...")

                    gc.collect() 

            # print("✅ Alignment C++ paralel selesai.")
            return True

        except Exception as e:
            print(f"Error fatal di luar blok alignment C++ utama: {e}")
            traceback.print_exc()
            return False
       