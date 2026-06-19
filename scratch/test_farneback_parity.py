import os
import sys
import numpy as np
import cv2
import time
import ctypes

# Set path to import project modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from taichi_library.taichi_aot.engine import AOTEngine

def get_polynomial_expansion_filters(poly_n=5, poly_sigma=1.1):
    r = poly_n // 2
    coords = np.arange(-r, r + 1)
    x, y = np.meshgrid(coords, coords)
    x = x.flatten()
    y = y.flatten()
    
    w = np.exp(-(x**2 + y**2) / (2.0 * poly_sigma**2))
    W = np.diag(w)
    
    # Basis: 1, x, y, x^2, y^2, xy
    X = np.stack([np.ones_like(x), x, y, x**2, y**2, x*y], axis=-1)
    
    XTWX = X.T @ W @ X
    P = np.linalg.inv(XTWX) @ X.T @ W
    
    filters = []
    for i in range(6):
        filters.append(P[i].reshape((poly_n, poly_n)))
    return np.array(filters, dtype=np.float32)

def compute_gaussian_weights_1d(sigma, radius):
    weights = []
    total = 0.0
    for i in range(radius + 1):
        w = np.exp(-(i * i) / (2 * sigma * sigma))
        weights.append(w)
        if i == 0: total += w
        else: total += 2 * w
    return np.array(weights, dtype=np.float32) / total

def upload_scalar_3d(engine, data):
    buf = engine.allocate(data.shape, data.dtype, host_accessible=True)
    ptr = buf.map()
    ctypes.memmove(ptr, np.ascontiguousarray(data).ctypes.data, buf.size_bytes)
    buf.unmap()
    return buf

def test_parity():
    print("=== BENCHMARK FARNEBACK 10x RUNS: OPENCV VS GPU AOT ===")
    
    # 1. Parameter
    h, w = 512, 512
    poly_n = 5
    poly_sigma = 1.1
    win_size = 15
    win_sigma = 1.2
    num_iterations = 5
    
    true_dx = 2.5
    true_dy = -1.5
    
    # 2. Buat Gambar Sintetis
    np.random.seed(42)
    base_noise = np.random.randn(h, w).astype(np.float32) * 0.1
    y_idx, x_idx = np.mgrid[0:h, 0:w]
    circle = np.sin(np.sqrt((y_idx - h/2)**2 + (x_idx - w/2)**2) * 0.05).astype(np.float32)
    img_ref = np.clip(circle + base_noise + 0.5, 0.0, 1.0)
    
    M = np.float32([[1, 0, true_dx], [0, 1, true_dy]])
    img_comp = cv2.warpAffine(img_ref, M, (w, h), borderMode=cv2.BORDER_REFLECT_101)
    
    # Konversi ke uint8 untuk OpenCV
    img_ref_u8 = (img_ref * 255).astype(np.uint8)
    img_comp_u8 = (img_comp * 255).astype(np.uint8)
    
    # 3. Benchmark OpenCV Farneback (10x Runs)
    print("Menjalankan 10x OpenCV Farneback...")
    cv_times = []
    # Warmup OpenCV
    cv2.calcOpticalFlowFarneback(
        img_ref_u8, img_comp_u8, None, 0.5, 1, win_size, num_iterations, poly_n, poly_sigma, cv2.OPTFLOW_FARNEBACK_GAUSSIAN
    )
    
    for i in range(10):
        t0 = time.perf_counter()
        cv_flow = cv2.calcOpticalFlowFarneback(
            img_ref_u8,
            img_comp_u8,
            None,
            pyr_scale=0.5,
            levels=1,
            winsize=win_size,
            iterations=num_iterations,
            poly_n=poly_n,
            poly_sigma=poly_sigma,
            flags=cv2.OPTFLOW_FARNEBACK_GAUSSIAN
        )
        t_cv = (time.perf_counter() - t0) * 1000.0
        cv_times.append(t_cv)
        print(f"  Run {i+1}: {t_cv:.2f} ms")
    
    # 4. Inisialisasi GPU AOT Farneback
    engine = AOTEngine()
    tcm_path = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets", "farneback_flow_vulkan.tcm")
    mod = engine.load(tcm_path)
    
    ref_gpu = engine.upload(img_ref)
    comp_gpu = engine.upload(img_comp)
    
    flow_np = np.zeros((h, w, 2), dtype=np.float32)
    # Alokasi flow buffer sekali saja di awal (host_accessible=True agar dapat dibaca kembali)
    flow_gpu = upload_scalar_3d(engine, flow_np)
    
    warped_comp_gpu = engine.allocate((h, w), dtype=np.float32)
    poly_ref_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    poly_comp_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    tensors_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    smooth_tensors_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    
    poly_filters_np = get_polynomial_expansion_filters(poly_n, poly_sigma)
    poly_filters_gpu = engine.upload(poly_filters_np)
    
    win_radius = win_size // 2
    gaussian_weights_np = compute_gaussian_weights_1d(win_sigma, win_radius)
    if len(gaussian_weights_np) < 21:
        padded = np.zeros(21, dtype=np.float32)
        padded[:len(gaussian_weights_np)] = gaussian_weights_np
        gaussian_weights_np = padded
    gaussian_weights_gpu = engine.upload(gaussian_weights_np)
    
    args = {
        "ref": ref_gpu,
        "comp": comp_gpu,
        "flow": flow_gpu,
        "warped_comp": warped_comp_gpu,
        "poly_ref": poly_ref_gpu,
        "poly_comp": poly_comp_gpu,
        "tensors": tensors_gpu,
        "smooth_tensors": smooth_tensors_gpu,
        "poly_filters": poly_filters_gpu,
        "gaussian_weights": gaussian_weights_gpu,
        "win_radius": int(win_radius),
        "poly_n": int(poly_n)
    }
    
    # Warmup GPU
    mod.run("farneback_iteration", **args)
    engine.sync()
    
    # Benchmark GPU AOT Farneback (10x Runs)
    # Catatan: Kita membiarkan flow berakumulasi sepanjang run untuk menguji konvergensi tanpa memicu Vulkan memory coherency bugs.
    print("\nMenjalankan 10x GPU AOT Farneback...")
    gpu_times = []
    
    for i in range(10):
        t1 = time.perf_counter()
        for _ in range(num_iterations):
            mod.run("farneback_iteration", **args)
        engine.sync()
        t_gpu = (time.perf_counter() - t1) * 1000.0
        gpu_times.append(t_gpu)
        print(f"  Run {i+1}: {t_gpu:.2f} ms")
        
        # Download flow untuk validasi run terakhir
        if i == 9:
            final_flow_gpu = flow_gpu.to_numpy()
    
    # Taichi flow ke visual (dx, dy)
    gpu_flow_visual = np.zeros_like(final_flow_gpu)
    gpu_flow_visual[..., 0] = -final_flow_gpu[..., 0]
    gpu_flow_visual[..., 1] = final_flow_gpu[..., 1]
    
    # Evaluasi Paritas di Area Tengah (Crop size 100x100)
    crop_size = 100
    y_s, y_e = h//2 - crop_size, h//2 + crop_size
    x_s, x_e = w//2 - crop_size, w//2 + crop_size
    
    crop_cv = cv_flow[y_s:y_e, x_s:x_e]
    crop_gpu = gpu_flow_visual[y_s:y_e, x_s:x_e]
    
    mean_cv_dx = np.mean(crop_cv[..., 0])
    mean_cv_dy = np.mean(crop_cv[..., 1])
    mean_gpu_dx = np.mean(crop_gpu[..., 0])
    mean_gpu_dy = np.mean(crop_gpu[..., 1])
    
    # Rata-rata waktu
    avg_cv_time = np.mean(cv_times)
    avg_gpu_time = np.mean(gpu_times)
    
    print("\n" + "="*50)
    print("=== RINGKASAN BENCHMARK 10x RUNS ===")
    print(f"Rata-rata Waktu OpenCV Farneback (CPU) : {avg_cv_time:.3f} ms")
    print(f"Rata-rata Waktu GPU AOT Farneback (GPU): {avg_gpu_time:.3f} ms")
    print(f"Peningkatan Kecepatan (Speedup)        : {avg_cv_time / avg_gpu_time:.2f}x")
    print("-"*50)
    print("EVALUASI AKURASI & KONVERGENSI:")
    print(f"OpenCV Est Shift (Single-run)          : dx = {mean_cv_dx:.4f}, dy = {mean_cv_dy:.4f}")
    print(f"GPU Est Shift (10x Runs Accumulative)  : dx = {mean_gpu_dx:.4f}, dy = {mean_gpu_dy:.4f}")
    print(f"Ground Truth Target                    : dx = {true_dx:.3f}, dy = {true_dy:.3f}")
    print("="*50)
    
    # Pembersihan VRAM secara aman
    for buf in [ref_gpu, comp_gpu, flow_gpu, warped_comp_gpu, poly_ref_gpu, poly_comp_gpu, tensors_gpu, smooth_tensors_gpu, poly_filters_gpu, gaussian_weights_gpu]:
        try:
            buf.destroy()
        except:
            pass

if __name__ == "__main__":
    test_parity()
