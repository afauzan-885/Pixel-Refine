# RENCANA INTEGRASI TAICHI KE FARNEBACK_OPTICAL_FLOW.PY

## Tujuan: Kualitas flow lebih baik + performa GPU tetap terjaga

---

## 1. RINGKASAN TEMUAN UJI AKURASI

### Data dari 10 iterasi uji (768x768, 10 displacement)

| Metode | Avg SSIM | Avg PSNR | Avg EPE | Avg Time |
|--------|----------|----------|---------|----------|
| A) OpenCV Murni | 0.4572 | 17.67 dB | 9.73 | 271 ms |
| B) OpenCV Pipeline (block+median uint8) | 0.7627 | 23.75 dB | 5.55 | 1128 ms |
| C) Taichi Pipeline (bilateral+median f32) | 0.4851 | 17.83 dB | 9.01 | 643 ms |

### Kenapa Method B menang?

Block tiling adalah **FAKTOR PALING BESAR** (+30% SSIM). Tanpa block tiling, 
Farneback global hanya bisa menangkap motion kecil (winsize=15). Dengan block tiling,
setiap blok kecil punya "motion sendiri" sehingga displacement besar terpecah rata.

| Faktor | Dampak SSIM | Prioritas |
|--------|-------------|-----------|
| Block tiling | +30% | KRITIS |
| Median smoothing 5x5 | +5% | Penting |
| Denoise bilateral | +3% | Opsional |
| uint8 quantization loss | -2% | Perlu dihilangkan |

### Kenapa Method C kalah?

1. Tidak ada block tiling -> Farneback global gagal untuk displacement besar
2. bilateral_grid_filter terlalu agresif (s_s=16) -> texture hilang
3. median_filter hanya 3x3 -> kurang dari 5x5 di Method B
4. ransac_flow_cleanup punya bug stride param

---

## 2. ARSITEKTUR PIPELINE YANG DIINGINKAN

```
INPUT (base_image, target_image)
    |
    v
[1] Grayscale Conversion ........... ta.cvtColor() .................. GPU
    |
    v
[2] Denoise ......................... ta.bilateral_grid_filter() ..... GPU
    |                                   (s_s=8, s_r=16, sigma_r=0.5)
    v
[3] Block Tiling .................... loop per block ................. CPU control
    |                                   + overlap_ratio=0.3
    v
[4] Farneback per block ............. cv2.calcOpticalFlowFarneback .. CPU
    |                                   (sama seperti sekarang)
    v
[5] Flow Assembly ................... merge blocks ke full flow ...... CPU
    |
    v
[6] Flow Smoothing .................. ta.median_filter per channel .. GPU
    |                                   (float32 native, kernel=3)
    v
[7] Flow Post-process ............... ta.gaussian_blur on flow ...... GPU
    |                                   (ringan, sigma=0.8, ksize=3)
    v
[8] Compensate Motion ............... ta.remap_with_flow() .......... GPU
    |                                   (bicubic 4x4 Catmull-Rom)
    v
OUTPUT (flow, compensated_image)
```

---

## 3. PERUBAHAN PER TAHAP

### Tahap 1: Denoise (ganti cv2.bilateralFilter)

**Lokasi**: `Farneback_optical_flow.py`, method `calculate_optical_flow()`, 
         fungsi `denoise_worker()` di dalamnya (baris ~199-260)

**Kode lama** (di dalam denoise_worker):
```python
noise_level = estimate_noise_variance(gray_8bit)
if noise_level > min_noise_threshold:
    d, sigma_color, sigma_space = get_adaptive_bilateral(...)
    denoised_image = cv2.bilateralFilter(gray_8bit, d, sigma_color, sigma_space)
else:
    denoised_image = gray_8bit
```

**Kode baru**:
```python
from taichi_algorithm.bilateral_grid import bilateral_grid_filter

gray_f32 = gray_8bit.astype(np.float32)
denoised_f32 = bilateral_grid_filter(gray_f32, s_s=8, s_r=16, sigma_s=1.0, sigma_r=0.5)
denoised_image = np.clip(denoised_f32, 0, 255).astype(np.uint8)
```

**Parameter bilateral_grid yang disarankan**:
- `s_s=8` -> spatial grid size 8px (ringan, menjaga texture)
- `s_r=16` -> intensity range bins
- `sigma_s=1.0` -> spatial blur sigma
- `sigma_r=0.5` -> range blur sigma (lebih kecil = lebih detail)

**Dampak**: Denoise lebih cepat di GPU, texture lebih terjaga

---

### Tahap 2: Flow Smoothing (ganti cv2.medianBlur uint8)

**Lokasi**: `Farneback_optical_flow.py`, baris ~428-451

**Kode lama** (median blur dengan uint8 workaround):
```python
flow_abs_max = max(np.abs(flow_full).max(), 1e-6)
flow_x_u8 = cv2.normalize(flow_x, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
flow_y_u8 = cv2.normalize(flow_y, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
flow_x_smoothed = cv2.medianBlur(flow_x_u8, kernel_size).astype(np.float32) * (flow_abs_max / 255.0)
flow_y_smoothed = cv2.medianBlur(flow_y_u8, kernel_size).astype(np.float32) * (flow_abs_max / 255.0)
flow_full = cv2.merge([flow_x_smoothed, flow_y_smoothed])
```

**Kode baru**:
```python
from taichi_algorithm.median_filter import median_filter

flow_x = flow_full[:, :, 0].copy()
flow_y = flow_full[:, :, 1].copy()
flow_x = median_filter(flow_x, kernel_size=3)  # GPU native float32
flow_y = median_filter(flow_y, kernel_size=3)  # zero quantization loss
flow_full = np.stack([flow_x, flow_y], axis=-1)
```

**Dampak**: Menghilangkan quantization loss ~0.04px, zero-copy GPU

---

### Tahap 3: Compensate Motion (ganti cv2.remap)

**Lokasi**: `Farneback_optical_flow.py`, method `compensate_motion()` (baris ~457-575)

**Kode lama**:
```python
grid_y, grid_x = np.mgrid[0:h, 0:w]
remap_x = (grid_x + flow[:, :, 0]).astype(np.float32)
remap_y = (grid_y + flow[:, :, 1]).astype(np.float32)
compensated = cv2.remap(base_image, remap_x, remap_y,
                        interpolation=interp_flag,
                        borderMode=cv2.BORDER_REFLECT)
```

**Kode baru**:
```python
from taichi_algorithm.remap import remap_with_flow

compensated = remap_with_flow(base_image.astype(np.float32), flow, h, w)
if compensated.dtype != base_image.dtype:
    compensated = np.clip(compensated, 0, 255).astype(base_image.dtype)
```

**Dampak**: Bicubic 4x4 Catmull-Rom vs bilinear -> presisi sub-pixel lebih baik

---

### Tahap 4: Tambah Gaussian Blur Ringan (opsional, post-smoothing)

**Lokasi**: Tambahkan setelah median smoothing, sebelum return

**Kode baru**:
```python
from taichi_algorithm.gaussian import gaussian_blur

flow_full = gaussian_blur(flow_full, sigma=0.8, kernel_size=3)
```

**Dampak**: Smoothing ringan untuk menghaluskan seam antar blok

---

## 4. BUG FIX: RANSAC (prasyarat untuk tahap lanjutan)

**File**: `taichi_library/taichi_algorithm/ransac.py`, baris ~559

**Masalah**: `_compute_mean_flow_kernel` dipanggil tanpa parameter `stride`

**Fix**:
```python
# Baris ~559: tambah stride=1
_compute_mean_flow_kernel(flow_gpu, mean_out, h, w, stride=1)
```

Setelah fix, bisa ditambahkan tahap 5:

### Tahap 5: RANSAC Flow Cleanup (opsional, post-smoothing)

```python
from taichi_algorithm.ransac import ransac_flow_cleanup
flow_full = ransac_flow_cleanup(flow_full, threshold=3.0, n_iterations=5)
```

---

## 5. IMPOR YANG DIBUTUHKAN

Tambahkan di bagian atas `Farneback_optical_flow.py`:

```python
# --- Taichi GPU Acceleration (opsional, fallback ke CPU jika tidak tersedia) ---
TAICHI_AVAILABLE = False
try:
    import os
    os.environ["AOT_MODE"] = "0"
    from taichi_algorithm.median_filter import median_filter
    from taichi_algorithm.bilateral_grid import bilateral_grid_filter
    from taichi_algorithm.remap import remap_with_flow as ta_remap_with_flow
    from taichi_algorithm.gaussian import gaussian_blur as ta_gaussian_blur
    TAICHI_AVAILABLE = True
except ImportError:
    pass
```

Setiap tahap di-wrap dengan try/except fallback:
```python
if TAICHI_AVAILABLE:
    try:
        # ... taichi GPU path ...
    except Exception:
        # ... fallback ke OpenCV CPU ...
else:
    # ... OpenCV CPU path (existing) ...
```

---

## 6. STRATEGI FALLBACK

| Komponen | Taichi Path | Fallback (CPU) |
|----------|------------|----------------|
| Denoise | `bilateral_grid_filter` | `cv2.bilateralFilter` (existing) |
| Median | `median_filter` per-channel | `cv2.medianBlur` + uint8 scale (existing) |
| Remap | `ta.remap_with_flow` | `cv2.remap` (existing) |
| Gaussian | `ta.gaussian_blur` | `cv2.GaussianBlur` (existing) |

**Prinsip**: Taichi tidak wajib, selalu ada fallback. Pipeline existing tetap jalan
jika Taichi tidak terinstall atau GPU tidak tersedia.

---

## 7. FILE YANG PERLU DIMODIFIKASI

| # | File | Perubahan |
|---|------|-----------|
| 1 | `Farneback_optical_flow.py` | Tambah import taichi, ganti 3 komponen + fallback |
| 2 | `ransac.py` (opsional) | Fix stride param bug di baris ~559 |
| 3 | `farneback_3way_comparison.py` | Update test untuk memverifikasi integrasi |

---

## 8. URUTAN IMPLEMENTASI

1. **Tahap 1**: Denoise (risiko rendah, drop-in replacement)
2. **Tahap 2**: Median smoothing (risiko rendah, blok kecil)
3. **Tahap 3**: Remap (risiko sedang, API beda)
4. **Tahap 4**: Gaussian ringan (risiko rendah, tambahan baru)
5. **Tahap 5**: RANSAC fix + integrasi (risiko tinggi)

---

## 9. TARGET AKURASI

| Kondisi | SSIM Sekarang | SSIM Target |
|---------|--------------|-------------|
| Displacement kecil (2-3px) | 0.93-0.94 | 0.95-0.97 |
| Displacement sedang (5-8px) | 0.70-0.86 | 0.85-0.92 |
| Displacement besar (8-10px) | 0.39-0.85 | 0.75-0.88 |
| Sub-pixel (1.5px) | 0.97 | 0.98+ |
| **Rata-rata 10 iterasi** | **0.76** | **0.85-0.90** |

---

## 10. ESTIMASI DAMPAK PER TAHAP

| Tahap | Komponen | SSIM Gain | Time Impact |
|-------|----------|-----------|-------------|
| 1 | Denoise GPU | +1-2% | -20% waktu denoise |
| 2 | Median float32 | +1-3% | -50% waktu median |
| 3 | Remap bicubic | +2-5% | ~sama |
| 4 | Gaussian ringan | +0.5% | +5% waktu |
| 5 | RANSAC | +2-5% | +10% waktu |
| **Total** | | **+6-15%** | **-10-20% total** |
