import os

os.environ["TI_ENABLE_CUDA_MALLOC_ASYNC"] = "0"

import concurrent
from concurrent.futures import ThreadPoolExecutor, as_completed
import ctypes
import gc
import math
import time
import traceback
import cv2
import numpy as np
import onnxruntime as ort

# Importers moved into functions to avoid circular dependencies


def get_taichi_worker():
    """Compatibility wrapper for centralized Taichi worker."""
    from ...taichi_algorithm.taichi_worker import _get_worker

    worker = _get_worker()
    # Add compatibility method if needed inside Similarity.py
    if not hasattr(worker, "submit_and_wait"):
        worker.submit_and_wait = worker.submit
    return worker


# --- SimilarityFrequencyInterface REMOVED (Legacy) ---


from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_similarity import (
    SimilaritySpatialInterface,
)


ALIGN_LIB = None
try:
    lib_path = os.path.join("pixel_refine_desktop", "ui", "data", "alignment_tile.dll")
    ALIGN_LIB = ctypes.CDLL(lib_path)

    # Definisikan tanda tangan fungsi compute_alignment_flow
    ALIGN_LIB.compute_alignment_flow.restype = ctypes.POINTER(ctypes.c_float)
    ALIGN_LIB.compute_alignment_flow.argtypes = [
        ctypes.POINTER(ctypes.c_float),  # ref_work_data
        ctypes.POINTER(ctypes.c_float),  # current_work_data
        ctypes.c_int,  # work_h
        ctypes.c_int,  # work_w
        ctypes.c_int,  # tile_h
        ctypes.c_int,  # tile_w
        ctypes.c_int,  # n_layers
        ctypes.c_float,  # search_dist
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
            raise RuntimeError(
                f"Gagal memuat atau menginisialisasi model ONNX dari {self.model_path}"
            )

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
                ("DmlExecutionProvider", {"device_id": 1}),
                ("CUDAExecutionProvider", {"device_id": 1}),
                "CPUExecutionProvider",
            ]

            # Filter provider yang tersedia
            providers_to_try = [
                p
                for p in preferred_providers
                if (p if isinstance(p, str) else p[0]) in available_providers
            ]

            if not providers_to_try:
                raise RuntimeError("Tidak ada provider ONNX Runtime yang tersedia.")

            # print(f"Provider yang tersedia dan akan dicoba: {[p if isinstance(p, str) else p[0] for p in providers_to_try]}")

            # SessionOptions dengan logging minimal
            session_options = ort.SessionOptions()
            session_options.graph_optimization_level = (
                ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            )
            session_options.log_severity_level = (
                3  # 0=VERBOSE, 1=INFO, 2=WARNING, 3=ERROR, 4=FATAL
            )

            # Buat session
            session = ort.InferenceSession(
                model_path, providers=providers_to_try, sess_options=session_options
            )
            # print(f"Model RAFT berhasil dimuat menggunakan: {session.get_providers()[0]}")

            return session

        except Exception as e:
            # print(f"Error fatal saat memuat model ONNX: {e}")
            traceback.print_exc()
            return None


# --- Global variable untuk menyimpan session ONNX agar tidak di-load berulang kali ---
MODEL_SESSION = None
FLOW_MODEL_PATH = "database/Learning_Model/optical_flow_estimation_raft_2023aug_int8bq.onnx"  # Ganti dengan path model ONNX Anda


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
    raw_flow_tile = compute_flow_with_raft(
        ref_tile_resized, current_tile_resized, session
    )
    if raw_flow_tile is None:
        return None

    model_h, model_w, _ = ref_tile_resized.shape
    h_flow, w_flow, _ = raw_flow_tile.shape
    if (h_flow != model_h) or (w_flow != model_w):
        flow_tile = scale_flow_to_full_res(
            raw_flow_tile, h_flow, w_flow, model_h, model_w
        )
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


def compute_flow_raft(
    ref_img,
    current_img,
    session,
    grid_rows=2,
    grid_cols=2,
    model_input_size=(360, 480),
    overlap_ratio=0.1,
    progress_callback=None,
    stop_requested=None,
):
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
            ref_tile_resized = cv2.resize(
                ref_tile, (model_w, model_h), interpolation=cv2.INTER_AREA
            )
            cur_tile_resized = cv2.resize(
                cur_tile, (model_w, model_h), interpolation=cv2.INTER_AREA
            )

            # Jalankan inferensi RAFT
            flow_model_res = process_single_tile_resized(
                (
                    ref_tile_resized,
                    cur_tile_resized,
                    session,
                    (y_start, x_start, y_end, x_end),
                )
            )
            if flow_model_res is None:
                print(f"⚠️ Gagal menghitung flow pada tile {tile_idx}/{total_tiles}")
                continue

            flow_res, (y_start, x_start, y_end, x_end) = flow_model_res
            orig_h, orig_w = y_end - y_start, x_end - x_start

            # Skala kembali flow ke ukuran tile asli
            flow_orig = scale_flow_to_full_res(
                flow_res, model_h, model_w, orig_h, orig_w
            )

            # Buat blending mask agar tepi tile halus
            blending = create_blending_weights(
                orig_h, orig_w, min(overlap_h, orig_h // 2), min(overlap_w, orig_w // 2)
            )

            final_flow[y_start:y_end, x_start:x_end] += flow_orig * blending
            weight_acc[y_start:y_end, x_start:x_end] += blending

            # Laporkan progress per tile ke callback
            if progress_callback is not None:
                progress_callback(tile_idx, total_tiles)

        except Exception as e:
            print(f"❌ Error tile {tile_idx}/{total_tiles}: {e}")

    # --- Normalisasi hasil gabungan ---
    final_flow /= weight_acc + 1e-8

    return final_flow


def scale_flow_to_full_res(flow, model_h, model_w, full_h, full_w):
    """
    Scale optical flow field from model resolution back to original resolution.
    Also scales the flow vectors accordingly.
    """
    scale_x = full_w / model_w
    scale_y = full_h / model_h
    flow_resized = cv2.resize(flow, (full_w, full_h), interpolation=cv2.INTER_LINEAR)
    flow_resized[:, :, 0] *= scale_x
    flow_resized[:, :, 1] *= scale_y
    return flow_resized


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
        ref_tensor = np.expand_dims(ref_tensor, axis=0).astype("float32")
        current_tensor = np.expand_dims(current_tensor, axis=0).astype("float32")

        # 3. Jalankan inferensi
        input_names = [inp.name for inp in session.get_inputs()]
        ort_inputs = {input_names[0]: ref_tensor, input_names[1]: current_tensor}
        ort_outs = session.run(None, ort_inputs)

        # 4. Proses output
        # Output flow biasanya (1, 2, H, W). Kita ubah ke (H, W, 2)
        flow = ort_outs[0][0]  # Ambil hasil pertama, buang batch dimension
        flow = np.transpose(flow, (1, 2, 0))  # Ubah 2,H,W -> H,W,2
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


# warp_image_opencv restored for CPU fallback
def warp_image_opencv(
    image,
    flow,
    interpolation=cv2.INTER_CUBIC,
    border_mode=cv2.BORDER_REFLECT_101,
    x_coords=None,
    y_coords=None,
):
    """Warp gambar menggunakan optical flow (CPU path)."""
    h, w = image.shape[:2]

    if x_coords is None or y_coords is None:
        y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)

    new_x = x_coords + flow[:, :, 0]
    new_y = y_coords + flow[:, :, 1]
    warped = cv2.remap(image, new_x, new_y, interpolation, borderMode=border_mode)

    # Eager cleanup of temporary mapping arrays
    del new_x, new_y

    return warped


# ==============================================================================
# === BAGIAN C: Fungsi Utama yang Dimodifikasi
# ==============================================================================
def visualize_flow(flow):
    """
    Mengubah peta optical flow menjadi citra berwarna untuk visualisasi magnitude.
    0px pergeseran: Hijau (0, 255, 0)
    Pergeseran Maksimum: Merah (0, 0, 255)
    """
    # 1. Hitung Magnitude
    magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])

    # 2. Normalisasi Magnitude agar range 0.0 - 1.0 (sesuai pergerakan tertinggi di frame ini)
    max_mag = np.max(magnitude)
    if max_mag < 1e-6:
        # Jika tidak ada gerakan sama sekali, kembalikan frame hijau murni
        vis = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
        vis[:, :, 1] = 255  # Green channel dalam BGR
        return vis

    norm_mag = np.clip(magnitude / max_mag, 0.0, 1.0)

    # 3. Interpolasi Warna (Hijau ke Merah)
    # BGR format: Green = (0, 255, 0), Red = (0, 0, 255)
    vis = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)

    # Red channel (BGR index 2) meningkat seiring magnitude
    vis[:, :, 2] = (norm_mag * 255).astype(np.uint8)

    # Green channel (BGR index 1) menurun seiring magnitude
    vis[:, :, 1] = ((1.0 - norm_mag) * 255).astype(np.uint8)

    # Blue channel (BGR index 0) tetap 0
    return vis


def save_aligned_image(
    aligned_img,
    index,
    backend_name,
    save_folder="save_align_image",
    save_prefix=None,
    harvest_mode=True,
):
    """
    Menyimpan gambar RGB yang telah diselaraskan ke folder output dengan normalisasi dinamis.
    Jika harvest_mode aktif, sistem akan memastikan file tidak menimpa file lama.
    """
    if aligned_img is None:
        return

    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        normalize_image,
    )

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
        os.makedirs(save_folder, exist_ok=True)

    # Tentukan Folder Penyimpanan (Gunakan subfolder jika ada prefix)
    final_save_folder = (
        os.path.join(save_folder, save_prefix) if save_prefix else save_folder
    )
    if not os.path.exists(final_save_folder):
        os.makedirs(final_save_folder, exist_ok=True)

    # Tentukan Nama File
    # Nama file tetap standar agar lebih bersih (folder sudah unik)
    filename = f"aligned_{backend_name}_frame_{index:02d}.jpg"
    output_path = os.path.join(final_save_folder, filename)

    # [SAFE SAVE] Logic: Jika harvest_mode aktif, tambahkan counter agar tidak menimpa
    if harvest_mode and os.path.exists(output_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{base}_{counter}{ext}"
            new_path = os.path.join(final_save_folder, new_filename)
            if not os.path.exists(new_path):
                filename = new_filename
                output_path = new_path
                break
            counter += 1

    # Don't konversi ke BGR — simpan langsung sebagai RGB
    # Note: OpenCV imwrite uses BGR, but save_img here is expected to be BGR or handled accordingly.
    # The original comment said "Jangan konversi ke BGR — simpan langsung sebagai RGB",
    # but imwrite expects BGR. If the input is RGB, it will be saved with swapped channels.
    # We maintain original behavior but fix the naming.
    cv2.imwrite(output_path, save_img, [cv2.IMWRITE_JPEG_QUALITY, 98])
    print(f"  [Save] {filename} disimpan (Harvest: {harvest_mode}).")


def perform_alignment_gpu(
    images,
    reference_image_float,
    work_res_h,
    work_res_w,
    tile_h,
    tile_w,
    ref_dtype,
    update_progress=None,
    stop_requested=None,
    num_alignment_workers=1,
    save_align_image=False,
    harvest_alignment=False,
    progress_start=30,
    progress_end=40,
    return_format: str = "numpy_u16",
    **kwargs,
):
    """
    GPU-accelerated alignment using Taichi AOT.
    Communicates directly with compute_flow (AOT) via AOTEngine.
    """
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import (
        AOTEngine,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features import (
        taichi_bridge,
    )

    engine = AOTEngine()
    num_images = len(images)
    if num_images <= 1:
        return True

    is_linear_mode = kwargs.get("is_linear_mode", False)
    proxy_scale = kwargs.get("proxy_scale", 1.0)
    use_sharpen = kwargs.get("use_sharpen", False)
    search_dist = kwargs.get("search_dist", 2.0)
    index_offset = kwargs.get("index_offset", 0)
    save_prefix = kwargs.get("save_prefix", None)
    save_folder = kwargs.get("save_folder", "save_align_image")

    # [NEW] Simpan gambar referensi (Frame 00)
    if save_align_image:
        save_aligned_image(
            images[0],
            0 + index_offset,
            "REF",
            save_folder=save_folder,
            save_prefix=save_prefix,
            harvest_mode=harvest_alignment,
        )

    # Calculate n_layers to target the resolution floor (Standardize on 3 for stability)
    n_layers = 3

    # Force single worker for GPU
    if num_alignment_workers > 1:
        print("[Info] Forcing single-threaded execution for Taichi GPU alignment.")

    print(f"[GPU Alignment] Processing {num_images - 1} images with Taichi GPU...")
    print(f"[GPU Alignment] Return format: {return_format}")

    # Array to store alignment cost maps (ZMSSD) for each image as confidence
    cost_maps = [None] * num_images

    try:
        # Define GPU alignment task
        # Execute on Taichi worker thread
        def _run_gpu_alignment_loop():
            # 1. Load Alignment Module
            import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

            file_dir = os.path.dirname(os.path.abspath(__file__))
            tcm_path = os.path.abspath(
                os.path.join(
                    file_dir,
                    "../../../../../ui/data/aot_assets/compute_flow_vulkan.tcm",
                )
            )
            mod = engine.load(tcm_path)

            # [LUMA ENHANCEMENT CACHE] Pre-allocate and populate 1D LUT once on GPU (Calibrated: contrast=1.20 (+50% boost), brightness=0.35, gamma=0.78)
            lut_np = np.zeros(256, dtype=np.float32)
            contrast = 1.2  # 0.8 * 1.50 (+50% standard contrast boost)
            brightness = 0.30  # Increased brightness offset
            gamma = 0.80
            for i in range(256):
                val = (i / 255.0) ** gamma * contrast + brightness
                lut_np[i] = np.clip(val, 0.0, 1.0)
            lut_gpu = engine.upload(lut_np)

            # Pre-allocate luma blur buffer for tracking enhancement (ALLOC ONCE, REUSE EVERY FRAME)
            h_w, w_w = work_res_h, work_res_w
            blur_work_gpu = engine.allocate((h_w, w_w), dtype=np.float32)

            # 2. Setup Reference Pyramid on GPU (ALLOCATE ONCE)
            ref_pyramid = taichi_bridge.prepare_reference_for_alignment(
                reference_image_float,
                is_linear_mode,
                proxy_scale,
                work_res_h,
                work_res_w,
                lut_gpu=lut_gpu,
                blur_work_gpu=blur_work_gpu,
            )

            # 3. Allocate Flow Buffers (REUSE ONCE)
            flow_l0 = engine.allocate((h_w, w_w, 2), dtype=np.float32, is_vector=False)
            flow_l1 = engine.allocate(
                (h_w // 2, w_w // 2, 2), dtype=np.float32, is_vector=False
            )
            flow_l2 = engine.allocate(
                (h_w // 4, w_w // 4, 2), dtype=np.float32, is_vector=False
            )

            # Pre-allocate per-frame reusable VRAM buffers (ALLOC ONCE, REUSE EVERY FRAME)
            # smooth_flow_buf: smoothed 2-channel flow (H_work, W_work, 2) — reused per frame
            # map_x_gpu/map_y_gpu: full-res coordinate maps — reused per frame
            full_h_ref, full_w_ref = images[0].shape[:2]
            smooth_flow_buf = engine.allocate((h_w, w_w, 2), dtype=np.float32)
            map_x_gpu = engine.allocate((full_h_ref, full_w_ref), dtype=np.float32)
            map_y_gpu = engine.allocate((full_h_ref, full_w_ref), dtype=np.float32)

            try:
                # 4. Process each image
                for i in range(1, num_images):
                    if stop_requested and stop_requested():
                        break

                    # A. Prepare Comparison Pyramid (Overwrites comp buffers if reuse logic exists)
                    comp_pyramid = taichi_bridge.prepare_comparison_for_alignment(
                        images[i],
                        ref_dtype,
                        is_linear_mode,
                        proxy_scale,
                        work_res_h,
                        work_res_w,
                        lut_gpu=lut_gpu,
                        blur_work_gpu=blur_work_gpu,
                    )

                    # B. Run One Big Graph (End-to-End Alignment)
                    args = {
                        "ref_l0": ref_pyramid[0],
                        "ref_l1": ref_pyramid[1],
                        "ref_l2": ref_pyramid[2],
                        "comp_l0": comp_pyramid[0],
                        "comp_l1": comp_pyramid[1],
                        "comp_l2": comp_pyramid[2],
                        "flow_l0": flow_l0,
                        "flow_l1": flow_l1,
                        "flow_l2": flow_l2,
                        "tile_h": int(tile_h),
                        "tile_w": int(tile_w),
                        "search_radius": 8,
                        "scale": 2.0,
                        "search_dist": int(search_dist),
                        "downscale": 2,
                    }
                    mod.run("align_end_to_end_3layer", **args)
                    engine.sync()

                    # C. Warp Full Resolution Image — Pure GPU Pipeline (Zero CPU Round-Trip)
                    #
                    # Pipeline (all in VRAM, NO .to_numpy(), NO cv2, NO np.mgrid):
                    #   flow_l0 (H_work, W_work, 2)
                    #       → smooth_flow_gpu   → smooth_flow_buf (reuse, Gaussian 5×5)
                    #       → build_flow_maps   → map_x_gpu, map_y_gpu (reuse, bilinear upsample
                    #                                                     + scale + identity grid)
                    #       → remap             → aligned image

                    # Step C1+C2: Smooth both flow channels together in one GPU call
                    smooth_flow_buf = taichi_aot.smooth_flow_gpu(
                        flow_l0, sigma=1.0, kernel_size=5, dst=smooth_flow_buf
                    )

                    # Step C3: Build full-res coordinate maps — bilinear upsample + scale + grid
                    map_x_gpu, map_y_gpu = taichi_aot.build_flow_maps(
                        smooth_flow_buf,  # 2-channel flow (H_work, W_work, 2)
                        full_h_ref,
                        full_w_ref,  # target resolution
                        scale_x=float(full_w_ref) / float(w_w),
                        scale_y=float(full_h_ref) / float(h_w),
                        map_x_buf=map_x_gpu,  # reuse buffer
                        map_y_buf=map_y_gpu,  # reuse buffer
                    )

                    # Step C4: Warp image using GPU coordinate maps
                    if return_format == "ti_ndarray":
                        aligned_gpu = taichi_aot.remap(
                            images[i], map_x_gpu, map_y_gpu, return_gpu=True
                        )
                        if save_align_image:
                            save_img = aligned_gpu.to_numpy()
                            save_aligned_image(
                                save_img,
                                i + index_offset,
                                "GPU_AOT",
                                save_folder=save_folder,
                                save_prefix=save_prefix,
                                harvest_mode=harvest_alignment,
                            )
                        images[i] = aligned_gpu
                    else:
                        images[i] = taichi_aot.remap(
                            images[i], map_x_gpu, map_y_gpu, return_gpu=False
                        )
                        if save_align_image:
                            save_aligned_image(
                                images[i],
                                i + index_offset,
                                "GPU_AOT",
                                save_folder=save_folder,
                                save_prefix=save_prefix,
                                harvest_mode=harvest_alignment,
                            )

                    # Update progress
                    if update_progress:
                        prog_fraction = i / (num_images - 1)
                        update_progress(
                            int(
                                progress_start
                                + prog_fraction * (progress_end - progress_start)
                            ),
                            f"Alignment gambar {i}/{num_images - 1} (GPU)...",
                        )

                    # D. Eager Memory Cleanup for Comparison Pyramid only
                    # (smooth_flow_buf, map_x_gpu, map_y_gpu are REUSED next frame — do NOT destroy)
                    for buf in comp_pyramid:
                        buf.destroy()
                    # No gc.collect() per frame — Python GC is slow; VRAM is managed explicitly

            finally:
                # 5. EXPLICIT CLEANUP (Destroy all persistent buffers)
                for buf in ref_pyramid:
                    buf.destroy()
                flow_l0.destroy()
                flow_l1.destroy()
                flow_l2.destroy()

                # Destroy reusable flow processing buffers
                for _buf in [
                    smooth_flow_buf,
                    map_x_gpu,
                    map_y_gpu,
                    lut_gpu,
                    blur_work_gpu,
                ]:
                    try:
                        _buf.destroy()
                    except Exception:
                        pass

                # [RAM/VRAM OPTIMIZATION] Unload TCM modules and clear pool to reach minimum idle
                taichi_aot.unload_all_modules()
                engine.buffer_pool.clear()

                gc.collect()

            return True

        is_aot = os.environ.get("PIXEL_REFINE_AOT_MODE") == "1"
        if is_aot:
            print(
                "[GPU Alignment] Running synchronously on caller thread (Pure Vulkan AOT C++)..."
            )
            success = _run_gpu_alignment_loop()
        else:
            worker = get_taichi_worker()
            success = worker.submit_and_wait(_run_gpu_alignment_loop)

        print("✅ GPU Alignment selesai (VRAM Stabilized).")
        return success

    except Exception as e:
        print(f"Error during GPU alignment: {e}")
        traceback.print_exc()

        return False


def perform_image_alignment(
    images,
    reference_image_float,
    work_res_h,
    work_res_w,
    tile_h,
    tile_w,
    ref_dtype,
    update_progress=None,
    stop_requested=None,
    optical_flow_type="alignment_tile",
    num_alignment_workers=1,
    visualization=False,
    save_align_image=True,
    harvest_alignment=True,  # [NEW] Harvest mode toggle
    progress_start=30,
    progress_end=40,
    **kwargs,
):
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        normalize_image,
        preprocess_in_python,
        to_gamma_proxy,
    )

    """
    Menyelaraskan (align) gambar dengan manajemen sumber daya yang aman.
    Supported types: 'raft', 'alignment_tile', 'farneback'
    """

    num_images = len(images)
    if num_images <= 1:
        return True

    is_linear_mode = kwargs.get("is_linear_mode", False)
    proxy_scale = kwargs.get("proxy_scale", 1.0)  # [AUTO-SCALE]
    index_offset = kwargs.get("index_offset", 0)
    save_prefix = kwargs.get("save_prefix", None)
    save_folder = kwargs.get("save_folder", "save_align_image")

    # [GPU-AUTO] Redirect to Taichi AOT GPU if type is alignment_tile
    # This ensures that high-level pipelines (SimilarityMNFR) automatically use GPU acceleration.
    if optical_flow_type == "alignment_tile":
        # print("[Alignment Core] Redirecting to GPU Alignment Pipeline (AOT)...")
        return perform_alignment_gpu(
            images,
            reference_image_float,
            work_res_h,
            work_res_w,
            tile_h,
            tile_w,
            ref_dtype,
            update_progress,
            stop_requested,
            search_dist=kwargs.get("search_dist", 2),
            **kwargs,
        )

    # --- Preprocessing referensi (CPU MURNI tanpa Taichi) ---
    # Note: Farneback & Tile alignment use grayscale. Raft uses color.
    if optical_flow_type == "raft":
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import (
            preprocess,
        )

        ref_preprocessed_cpp = preprocess.preprocess_in_python_gpu(
            reference_image_float,
            use_raft=True,
            use_sharpen=False,
            return_numpy=True,
        )
    else:
        # [MODIFIED] Menggunakan preprocess_in_python (CPU) agar benar-benar bersih dari Taichi
        ref_preprocessed_cpp, _ = preprocess_in_python(reference_image_float)
    ref_work_gray_cpp = cv2.resize(
        ref_preprocessed_cpp, (work_res_w, work_res_h), interpolation=cv2.INTER_LINEAR
    ).astype(np.float32)
    ref_work_gray_cpp = np.ascontiguousarray(ref_work_gray_cpp)
    ref_work_ptr = ref_work_gray_cpp.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    # del ref_preprocessed_cpp (Keep it for Farneback/Tile if needed, or move to raft block)

    # Siapkan variabel konfigurasi C++ (HDR+ style: 4 levels for 4x pyramid)
    min_layer_res = min(tile_h, tile_w) * 2
    log_arg = min(work_res_h, work_res_w) / min_layer_res if min_layer_res > 0 else 1
    n_layers = min(4, max(1, int(np.ceil(np.log2(log_arg))) if log_arg > 0 else 1))

    # === BACKEND RAFT (GPU, multi-thread) ===
    if optical_flow_type == "raft":
        print(
            f"Memulai alignment menggunakan backend RAFT dengan {num_alignment_workers} worker paralel..."
        )

        try:
            # RAFT memerlukan sesi ONNX dan referensi gambar warna penuh
            with ONNXSessionManager(FLOW_MODEL_PATH) as MODEL_SESSION:
                ref_full_color_raft = (reference_image_float * 255).astype(np.uint8)
                model_input_size = (360, 480)
                grid_rows, grid_cols = 2, 2

                # --- Fungsi untuk 1 tugas alignment RAFT (dijalankan di worker) ---
                def process_single_alignment_raft(
                    i,
                    original_image,
                    ref_full_color_raft,
                    MODEL_SESSION,
                    ref_dtype,
                    stop_requested=None,
                ):

                    if stop_requested and stop_requested():
                        return (i, None)

                    current_img_float = normalize_image(original_image, ref_dtype)

                    # [PROXY LOGIC] Gunakan Gamma Proxy untuk RAFT alignment di Linear Mode
                    if is_linear_mode:
                        current_img_float_proxy = to_gamma_proxy(
                            current_img_float, scale=proxy_scale
                        )
                        current_full_color_raft = np.clip(
                            current_img_float_proxy * 255, 0, 255
                        ).astype(np.uint8)
                    else:
                        current_full_color_raft = np.clip(
                            current_img_float * 255, 0, 255
                        ).astype(np.uint8)

                    flow_full_res = compute_flow_raft(
                        ref_full_color_raft,
                        current_full_color_raft,
                        MODEL_SESSION,
                        grid_rows=grid_rows,
                        grid_cols=grid_cols,
                        model_input_size=model_input_size,
                        overlap_ratio=0.2,
                        stop_requested=stop_requested,
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
                            i,
                            images[i],
                            ref_full_color_raft,
                            MODEL_SESSION,
                            ref_dtype,
                            stop_requested=stop_requested,
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
                                    save_aligned_image(
                                        aligned_img,
                                        idx + index_offset,
                                        "RAFT",
                                        save_folder=save_folder,
                                        save_prefix=save_prefix,
                                        harvest_mode=harvest_alignment,
                                    )
                                # <<< AKHIR INTEGRASI >>>

                            else:
                                print(
                                    f"Peringatan: Alignment RAFT gagal untuk gambar {i+1}."
                                )
                        except Exception as e:
                            print(f"❌ Worker RAFT gagal untuk gambar {i+1}: {e}")

                        processed_count += 1
                        if update_progress:
                            prog_fraction = processed_count / (num_images - 1)
                            current_msg_progress = int(
                                progress_start
                                + prog_fraction * (progress_end - progress_start)
                            )
                            update_progress(
                                current_msg_progress,
                                f"Alignment gambar {processed_count}/{num_images - 1} (RAFT)...",
                            )

                        gc.collect()

            print("✅ Alignment GPU RAFT selesai.")
            return True

        except Exception as e:
            print(f"Error kritis selama RAFT: {e}")
            traceback.print_exc()
            return False

    # =================================================================
    # === BACKEND FARNEBACK (CPU, OpenCV) - PARALEL ===
    # =================================================================
    elif optical_flow_type == "farneback":
        print(f"Memulai alignment menggunakan Farneback Optical Flow...")
        try:
            # Menggunakan referensi grayscale yang sudah dipreprocess
            # Tetapi Farneback butuh uint8 0-255 biasanya lebih robust
            ref_gray_8u = np.clip(ref_preprocessed_cpp * 255.0, 0, 255).astype(np.uint8)

            def process_single_alignment_farneback(
                i,
                original_image,
                ref_gray_8u,
                ref_dtype,
                stop_requested=None,
            ):
                if stop_requested and stop_requested():
                    return (i, None)

                # Preprocess current image to grayscale
                current_img_float = normalize_image(original_image, ref_dtype)

                # [PROXY LOGIC] Gunakan Gamma Proxy untuk Alignment di Linear Mode
                if is_linear_mode:
                    current_img_float_proxy = to_gamma_proxy(
                        current_img_float, scale=proxy_scale
                    )
                    # [MODIFIED] Menggunakan preprocess_in_python (CPU)
                    current_preproc, _ = preprocess_in_python(current_img_float_proxy)
                else:
                    # [MODIFIED] Menggunakan preprocess_in_python (CPU)
                    current_preproc, _ = preprocess_in_python(current_img_float)

                current_gray_8u = np.clip(current_preproc * 255.0, 0, 255).astype(
                    np.uint8
                )

                # Ensure same size (just in case)
                if current_gray_8u.shape != ref_gray_8u.shape:
                    current_gray_8u = cv2.resize(
                        current_gray_8u, (ref_gray_8u.shape[1], ref_gray_8u.shape[0])
                    )

                # Initial flow can be None in Python, but some stubs prefer a dummy or no argument.
                # We'll use a more explicit approach to satisfy linting.
                flow_init = np.empty(
                    (ref_gray_8u.shape[0], ref_gray_8u.shape[1], 2), dtype=np.float32
                )
                flow = cv2.calcOpticalFlowFarneback(
                    ref_gray_8u,
                    current_gray_8u,
                    flow_init,
                    0.5,
                    3,
                    15,
                    3,
                    5,
                    1.2,
                    0,
                )

                aligned_img = warp_image_opencv(original_image, flow)

                # [OPTIMIZATION] Clear temporaries
                del current_img_float, current_preproc, current_gray_8u, flow, flow_init

                if visualization:
                    flow_vis = visualize_flow(
                        aligned_img
                    )  # This is just a placeholder logic check
                    cv2.imwrite(f"flow_farneback_{i+1:02d}.jpg", flow_vis)
                    del flow_vis

                return (i, aligned_img)

                return (i, aligned_img)

            processed_count = 0
            # Menggunakan ThreadPool untuk IO/OpenCV work
            with ThreadPoolExecutor(max_workers=num_alignment_workers) as executor:
                futures = {}
                for i in range(1, num_images):
                    if stop_requested and stop_requested():
                        return False

                    future = executor.submit(
                        process_single_alignment_farneback,
                        i,
                        images[i],
                        ref_gray_8u,
                        ref_dtype,
                        stop_requested,
                    )
                    futures[future] = i

                for future in as_completed(futures):
                    i = futures[future]
                    try:
                        idx, aligned_img = future.result()
                        if aligned_img is not None:
                            images[idx] = aligned_img
                            if save_align_image:
                                save_aligned_image(
                                    aligned_img,
                                    idx + index_offset,
                                    "FARNEBACK",
                                    save_folder=save_folder,
                                    save_prefix=save_prefix,
                                    harvest_mode=harvest_alignment,
                                )
                        else:
                            print(
                                f"Warning: Farneback alignment returned None for image {i}"
                            )
                    except Exception as e:
                        print(f"Error in Farneback worker: {e}")
                        traceback.print_exc()

                    processed_count += 1
                    if update_progress:
                        prog_fraction = processed_count / (num_images - 1)
                        current_msg_progress = int(
                            progress_start
                            + prog_fraction * (progress_end - progress_start)
                        )
                        update_progress(
                            current_msg_progress,
                            f"Alignment gambar {processed_count}/{num_images - 1} (Farneback)...",
                        )

            print("✅ Alignment Farneback selesai.")
            return True, [None] * num_images

        except Exception as e:
            print(f"Error kritis selama Farneback: {e}")
            traceback.print_exc()
            return False, None

    # =================================================================
    # === BACKEND C++ (alignment_tile) - PARALEL ===
    # =================================================================
    elif optical_flow_type == "alignment_tile":
        if ALIGN_LIB is None:
            error_msg = "Error: Backend C++ dipilih tetapi library 'alignment_tile.dll' tidak tersedia."
            print(error_msg)
            if update_progress:
                update_progress(0, error_msg)
            return False

        try:
            # --- Fungsi untuk 1 tugas alignment C++ (dijalankan di worker) ---
            def process_single_alignment_cpp(
                i,
                ref_work_gray_cpp,
                work_res_h,
                work_res_w,
                tile_h,
                tile_w,
                n_layers,
                original_image,
                ref_dtype,
                ALIGN_LIB,
                stop_requested,
                full_res_reference_image,
                x_coords_full=None,
                y_coords_full=None,
            ):

                if stop_requested and stop_requested():
                    return (i, None)

                try:
                    # --- C++ DLL PATH ---
                    current_img_float = normalize_image(original_image, ref_dtype)
                    if is_linear_mode:
                        current_img_float_proxy = to_gamma_proxy(
                            current_img_float, scale=proxy_scale
                        )
                        # [MODIFIED] Menggunakan preprocess_in_python (CPU)
                        current_preprocessed_cpp, _ = preprocess_in_python(
                            current_img_float_proxy
                        )
                    else:
                        # [MODIFIED] Menggunakan preprocess_in_python (CPU)
                        current_preprocessed_cpp, _ = preprocess_in_python(
                            current_img_float
                        )

                    current_work_gray_cpp = cv2.resize(
                        current_preprocessed_cpp,
                        (work_res_w, work_res_h),
                        interpolation=cv2.INTER_LINEAR,
                    ).astype(np.float32)

                    current_work_gray_cpp = np.ascontiguousarray(current_work_gray_cpp)
                    current_work_ptr = current_work_gray_cpp.ctypes.data_as(
                        ctypes.POINTER(ctypes.c_float)
                    )

                    # Pastikan struktur referensi disiapkan untuk pointer
                    ref_work_gray_cpp = np.ascontiguousarray(ref_work_gray_cpp)
                    ref_work_ptr = ref_work_gray_cpp.ctypes.data_as(
                        ctypes.POINTER(ctypes.c_float)
                    )

                    flow_ptr = ALIGN_LIB.compute_alignment_flow(
                        ref_work_ptr,
                        current_work_ptr,
                        work_res_h,
                        work_res_w,
                        tile_h,
                        tile_w,
                        n_layers,
                        2.0,
                    )

                    aligned_img = None
                    if flow_ptr:
                        try:
                            # 3. Baca Flow dan Rescale
                            flow_buf_cpp = np.empty(
                                (work_res_h, work_res_w, 2), dtype=np.float32
                            )
                            ctypes.memmove(
                                flow_buf_cpp.ctypes.data_as(
                                    ctypes.POINTER(ctypes.c_float)
                                ),
                                flow_ptr,
                                flow_buf_cpp.nbytes,
                            )

                            full_h, full_w = original_image.shape[:2]

                            # Skala flow untuk mapping kembali
                            flow_full_res = scale_flow(
                                flow_buf_cpp,
                                work_res_h,
                                work_res_w,
                                full_h,
                                full_w,
                                ksize=5,
                            )

                            if visualization:
                                flow_vis = visualize_flow(flow_full_res)
                                cv2.imwrite(f"flow_cpp_{i+1:02d}.jpg", flow_vis)
                                del flow_vis

                            # 4. Warp Gambar menggunakan koordinat pre-calculated (OPTIMASI MEMORI 1)
                            aligned_img = warp_image_opencv(
                                original_image,
                                flow_full_res,
                                x_coords=x_coords_full,
                                y_coords=y_coords_full,
                            )

                        except Exception as e:
                            print(f"Error processing flow result for image {i+1}: {e}")
                        finally:
                            # [CRITICAL] Free C++ heap memory (OPTIMASI MEMORI 2)
                            if ALIGN_LIB and flow_ptr:
                                ALIGN_LIB.free_flow_memory(flow_ptr)

                            # Cleanup temporaries
                            if "flow_buf_cpp" in locals():
                                del flow_buf_cpp
                            if "flow_full_res" in locals():
                                del flow_full_res

                except Exception as e:
                    print(f"Error C++ setup/call for image {i+1}: {e}")
                    traceback.print_exc()
                    return (i, None)

                finally:
                    # Pastikan referensi Python lokal dibersihkan
                    if "current_work_gray_cpp" in locals():
                        del current_work_gray_cpp
                    if "current_preprocessed_cpp" in locals():
                        del current_preprocessed_cpp
                    if "current_img_float" in locals():
                        del current_img_float
                    if "flow_ptr" in locals():
                        del flow_ptr

                return (i, aligned_img)

            # [OPTIMIZATION] Pre-calculate coordinate maps once to save GBs of RAM
            full_h, full_w = images[0].shape[:2]
            y_coords_full, x_coords_full = np.mgrid[0:full_h, 0:full_w].astype(
                np.float32
            )

            # --- Parallel execution with ThreadPoolExecutor ---
            with ThreadPoolExecutor(max_workers=num_alignment_workers) as executor:
                futures = {}
                processed_count = 0

                # Kirim tugas ke executor
                for i in range(1, num_images):
                    if stop_requested and stop_requested():
                        executor.shutdown(wait=False, cancel_futures=True)
                        return False

                    if i > 1:
                        time.sleep(0.1)

                    future = executor.submit(
                        process_single_alignment_cpp,
                        i,
                        ref_work_gray_cpp,
                        work_res_h,
                        work_res_w,
                        tile_h,
                        tile_w,
                        n_layers,
                        images[i],
                        ref_dtype,
                        ALIGN_LIB,
                        stop_requested,
                        reference_image_float,
                        x_coords_full,
                        y_coords_full,
                    )
                    futures[future] = i

                # Kumpulkan hasil
                for future in as_completed(futures):
                    i = futures[future]
                    if stop_requested and stop_requested():
                        executor.shutdown(wait=False, cancel_futures=True)
                        return False

                    try:
                        idx, aligned_img = future.result()
                        if aligned_img is not None:
                            images[idx] = aligned_img
                            if save_align_image:
                                save_aligned_image(
                                    aligned_img,
                                    idx + index_offset,
                                    "CPP",
                                    save_folder=save_folder,
                                    save_prefix=save_prefix,
                                    harvest_mode=harvest_alignment,
                                )
                            # [OPTIMIZATION]
                            del aligned_img
                    except Exception as e:
                        print(
                            f"❌ Worker C++ gagal untuk gambar {i+1} (saat fetch result): {e}"
                        )

                    gc.collect()

                    processed_count += 1
                    if update_progress:
                        prog_fraction = processed_count / (num_images - 1)
                        current_msg_progress = int(
                            progress_start
                            + prog_fraction * (progress_end - progress_start)
                        )
                        update_progress(
                            current_msg_progress,
                            f"Alignment gambar {processed_count}/{num_images - 1} (C++)...",
                        )

            print("✅ Alignment C++ selesai.")

            # Explicitly cleanup shared maps
            del x_coords_full, y_coords_full, reference_image_float
            gc.collect()

            return True

        except Exception as e:
            print(f"Error kritis selama C++ Alignment: {e}")
            traceback.print_exc()
            return False
