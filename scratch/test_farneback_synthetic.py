import os
import sys
import numpy as np
import cv2
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

def test_farneback_gpu():
    print("=== Memulai Pengujian Farneback GPU AOT dengan Gambar Sintetis ===")
    
    # 1. Inisialisasi Engine & Load Module
    engine = AOTEngine()
    tcm_path = os.path.join(project_root, "pixel_refine_desktop", "ui", "data", "aot_assets", "farneback_flow_vulkan.tcm")
    print(f"Loading modul dari: {tcm_path}")
    mod = engine.load(tcm_path)
    
    # 2. Buat Gambar Sintetis (Grid berpola noise)
    h, w = 512, 512
    np.random.seed(42)
    base_noise = np.random.randn(h, w).astype(np.float32) * 0.1
    # Gambar berpola lingkaran besar di tengah
    y_idx, x_idx = np.mgrid[0:h, 0:w]
    circle = np.sin(np.sqrt((y_idx - h/2)**2 + (x_idx - w/2)**2) * 0.05).astype(np.float32)
    img_ref = np.clip(circle + base_noise + 0.5, 0.0, 1.0)
    
    # 3. Terapkan Pergerakan Sintetis Terprediksi (dx = 2.5, dy = -1.5)
    true_dx = 2.5
    true_dy = -1.5
    M = np.float32([[1, 0, true_dx], [0, 1, true_dy]])
    img_comp = cv2.warpAffine(img_ref, M, (w, h), borderMode=cv2.BORDER_REFLECT_101)
    
    # 4. Alokasikan GPU Buffer
    print("Mengalokasikan buffer VRAM...")
    ref_gpu = engine.upload(img_ref)
    comp_gpu = engine.upload(img_comp)
    
    # Inisialisasi flow dengan nol
    flow_np = np.zeros((h, w, 2), dtype=np.float32)
    flow_gpu = upload_scalar_3d(engine, flow_np)
    
    # Scratch buffers untuk iterasi
    warped_comp_gpu = engine.allocate((h, w), dtype=np.float32)
    poly_ref_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    poly_comp_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    tensors_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    smooth_tensors_gpu = engine.allocate((h, w, 5), dtype=np.float32)
    
    # 5. Precompute Filter Koefisien & Bobot Gaussian
    poly_n = 5
    poly_sigma = 1.1
    win_size = 15
    win_sigma = 1.2
    
    poly_filters_np = get_polynomial_expansion_filters(poly_n, poly_sigma)
    poly_filters_gpu = engine.upload(poly_filters_np)
    
    win_radius = win_size // 2
    gaussian_weights_np = compute_gaussian_weights_1d(win_sigma, win_radius)
    gaussian_weights_gpu = engine.upload(gaussian_weights_np)
    
    # 6. Jalankan Iterasi Farneback di GPU
    num_iterations = 5
    print(f"Menjalankan {num_iterations} iterasi Farneback di GPU...")
    
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
    
    for i in range(num_iterations):
        mod.run("farneback_iteration", **args)
    engine.sync()
        
    # 7. Download dan Evaluasi Akurasi
    final_flow = flow_gpu.to_numpy()
    
    # Ambil nilai rata-rata estimasi flow di area tengah yang bertekstur
    crop_size = 100
    center_flow = final_flow[h//2 - crop_size : h//2 + crop_size, w//2 - crop_size : w//2 + crop_size]
    
    # Taichi flow mengembalikan -dx dan dy (sesuai warp convention kami)
    # Mari kita ubah kembali ke orientasi visual (dx, dy)
    est_dx = -np.mean(center_flow[..., 0])
    est_dy = np.mean(center_flow[..., 1])
    
    print("\n=== HASIL ESTIMASI VS GROUND TRUTH ===")
    print(f"Pergeseran Sebenarnya  : dx = {true_dx:.3f}, dy = {true_dy:.3f}")
    print(f"Estimasi Farneback GPU : dx = {est_dx:.3f}, dy = {est_dy:.3f}")
    print(f"Error Absolut Rata-rata: dx_err = {abs(est_dx - true_dx):.4f}, dy_err = {abs(est_dy - true_dy):.4f}")
    
    # Pembersihan VRAM
    for buf in [ref_gpu, comp_gpu, flow_gpu, warped_comp_gpu, poly_ref_gpu, poly_comp_gpu, tensors_gpu, smooth_tensors_gpu, poly_filters_gpu, gaussian_weights_gpu]:
        buf.destroy()
        
    print("Pembersihan memori VRAM selesai.")

if __name__ == "__main__":
    test_farneback_gpu()
