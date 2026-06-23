# 📋 Rencana Riset: Camera2 Pipeline dengan Taichi GPU Backend

> **Tujuan**: Mengembangkan algoritma capture gambar dari kamera smartphone (Camera2 API)
> dengan Taichi sebagai backend processing, untuk mencapai FPS tinggi, latensi rendah, dan minim lag.
>
> **Tanggal**: 2025-07-14
> **Status**: Draft Riset

---

## 1. Ringkasan Eksekutif

### 1.1 Aset yang Sudah Ada (Tinggal Panggil)

Dari eksplorasi `taichi_algorithm`, **35+ modul GPU** sudah siap digunakan:

| Kategori | Modul | Fungsi Relevan | File |
|----------|-------|----------------|------|
| **Denoising** | NLM | `non_local_means()` | `denoising/nlm.py` |
| | BM3D/HFCD | `hfcd_denoise()` | `denoising/bm3d.py` |
| **Demosaicing** | Hamilton | `hamilton_demosaic()` | `demosaicing/Hamilton_demosaice.py` |
| | ARM | `arm_demosaic()` | `demosaicing/arm_demosaice.py` |
| **Color** | cvtColor | `cvtColor()`, `cvtColor_extended()` | `common.py`, `image_processing/color_convert.py` |
| | HSV/LAB/YCrCb | BGR↔HSV, BGR↔LAB, BGR↔YCrCb | `image_processing/color_convert.py` |
| **Enhancement** | CLAHE | `clahe()` | `image_processing/clahe.py` |
| | Enhance Gray | `enhance_grayscale()` | `image_processing/enhance_image.py` |
| **Smoothing** | Gaussian | `gaussian()` | `smoothing/gaussian.py` |
| | Bilateral | `bilateral()` / `bilateral_grid_filter()` | `smoothing/bilateral_grid.py` |
| | Guided Filter | `guided_filter()` | `smoothing/guided_filter.py` |
| | Median | `median()` | `smoothing/median_filter.py` |
| | Box Filter | `box_filter()` | `smoothing/box_filter.py` |
| | Joint Bilateral | `joint_bilateral_guidance` | `smoothing/joint_bilateral_guidance.py` |
| **Optical Flow** | Farneback | `farneback_flow()` | `optical_flow/farneback_flow.py` |
| | Template Flow | `template_flow` | `optical_flow/template_flow.py` |
| **Alignment** | Phase Corr | `phase_correlation()` | `alignment/phase_correlation.py` |
| | MTB | `align_mtb()` | `alignment/mtb.py` |
| | NCC | `zncc()`, `match_template()` | `alignment/ncc.py` |
| | RANSAC | `ransac_flow_cleanup()`, `vsac_fundamental()` | `alignment/ransac.py` |
| **Edge** | Canny | `canny()` | `image_processing/canny.py` |
| | Sobel/Lap | `sobel()`, `laplacian()` | `math_ops/gradients.py` |
| **Pyramid** | Build/Upsample | `build_image_pyramid()`, `upsample_flow()` | `pyramid/pyramid.py` |
| **Resize** | Bilinear/Bicubic/Nearest/Area | `resize()` | `interpolation/*.py` |
| **Morphology** | Dilate/Erode | `dilate()`, `erode()` | `morphology.py` |
| **Threshold** | Otsu/Binary | `otsu_threshold()`, `threshold()` | `image_processing/otsu.py`, `threshold.py` |
| **Quality** | SSIM | `ssim()` | `ssim.py` |
| **Spatial** | Ghost Rejection | `compute_spatial_weight()`, `NoiseEstimator` | `compute_spatial.py` |
| **FFT** | Phase Correlation | `fft2()`, `ifft2()` | `pyramid/fft.py` |
| **Infrastructure** | Buffer Pool | `BufferCache`, `get_temp_buffer()`, `release_temp_buffer()` | `common.py` |
| | Worker Thread | `ti_thread`, `get_taichi_worker()` | `taichi_worker.py` |
| | OOM Guard | `execute_tiled()`, `should_tile()` | `oom_guard.py` |
| | Hanning Window | `hanning()` | `common.py` |
| | Mean Division | `mean_division()` | `common.py` |
| | Inpaint | `inpaint()` | `image_processing/inpaint.py` |
| | Seamless Clone | `seamless_clone()` | `image_processing/seamless_clone.py` |

### 1.2 Modul Baru yang Perlu Dibuat

| Modul | Prioritas | Kompleksitas | Alasan |
|-------|-----------|-------------|--------|
| `yuv_to_rgb.py` | **KRITIS** | Rendah | Camera2 output YUV → pintu masuk pipeline |
| `camera2_pipeline.py` | **KRITIS** | Tinggi | Orchestrator real-time pipeline |
| `temporal_merge.py` | **TINGGI** | Sedang | Multi-frame stacking untuk noise reduction |
| `white_balance.py` | **SEDANG** | Rendah | Koreksi WB dari Camera2 metadata |
| `tone_mapping.py` | **SEDANG** | Sedang | HDR tone mapping |
| `camera2_bridge.py` | **KRITIS** | Sedang | Bridge Android Camera2 → Python/Taichi |
| `frame_dropper.py` | **TINGGI** | Rendah | Adaptive frame skip untuk konsistensi FPS |

---

## 2. Arsitektur Pipeline

### 2.1 Pipeline Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAMERA2 → TAICHI PIPELINE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐        │
│  │ Camera2  │──→│  Stage 1 │──→│  Stage 2 │──→│  Stage 3 │        │
│  │ Sensor   │   │ YUV→RGB  │   │ Denoise  │   │ Color &  │        │
│  │ (Android)│   │ [BARU]   │   │ [ADA]    │   │ Tone     │        │
│  └──────────┘   └──────────┘   └──────────┘   └────┬─────┘        │
│       │                                             │              │
│       │ ImageReader                                  ▼              │
│       │ (YUV_420_888)                           ┌──────────┐       │
│       │                                         │  Stage 4 │       │
│       ▼                                         │ Enhance  │       │
│  ┌──────────┐                                   │ [ADA]    │       │
│  │ Bridge   │                                   └────┬─────┘       │
│  │ [BARU]   │                                        │             │
│  │ NumPy→   │                                        ▼             │
│  │ Taichi   │                                   ┌──────────┐       │
│  └──────────┘                                   │  Stage 5 │       │
│                                                  │ Multi-   │       │
│                                                  │ Frame    │       │
│                                                  │ [BARU+   │       │
│                                                  │  ADA]    │       │
│                                                  └────┬─────┘       │
│                                                       │             │
│                                                       ▼             │
│                                                  ┌──────────┐       │
│                                                  │  Stage 6 │       │
│                                                  │ Output   │       │
│                                                  │ [ADA]    │       │
│                                                  └──────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Detail Setiap Stage

#### Stage 0: Capture (Android Camera2 API)
```
Input:  Camera2 ImageReader → Image (YUV_420_888, 3-plane)
Bridge: Extract Y, U, V planes → NumPy array
Output: YUV bytes sebagai NumPy contiguous array
```
**Modul**: `camera2_bridge.py` [BARU]
**Fungsi**:
- `extract_yuv_planes(image)` → `np.ndarray` (Y flat, U flat, V flat)
- `get_camera_metadata(capture_result)` → dict (ISO, exposure_time, AWB_gains, AF_state)

#### Stage 1: Format Conversion (YUV → RGB)
```
Input:  YUV NumPy array
Proses: Upload ke Taichi field → YUV→RGB kernel di GPU
Output: RGB float32 Taichi field (H, W, 3)
```
**Modul**: `yuv_to_rgb.py` [BARU - tapi formula sederhana, ~50 baris kernel]
**Fungsi yang dipanggil**:
- `common.ensure_taichi_field()` - Upload NumPy → Taichi field
- `common.get_temp_buffer()` - Buffer dari pool
- `common.release_temp_buffer()` - Return buffer ke pool
**Kernel**: BT.601/BT.709 YUV→RGB conversion (per-pixel, embarrassingly parallel)
**Untuk RAW**: Langsung pakai `hamilton_demosaic()` atau `arm_demosaic()` yang SUDAH ADA

#### Stage 2: Denoising (Per-Frame)
```
Input:  RGB float32 Taichi field
Proses: Select denoiser berdasarkan ISO dari metadata
Output: Denoised RGB float32 Taichi field
```
**Modul yang SUDAH ADA**:
- `nlm.non_local_means(h_param, search_window, patch_size)` → ISO < 800: fast (s3_p1), ISO 800-3200: balanced (s5_p2), ISO > 3200: quality (s7_p3)
- `bm3d.hfcd_denoise()` → Heavy denoise untuk night mode
- `smoothing.guided_filter()` → Edge-preserving alternatif
- `smoothing.bilateral_grid_filter()` → Real-time edge-preserving

**Auto-select logic** (berdasarkan Camera2 metadata):
```python
def select_denoiser(iso: int, noise_sigma: float):
    if iso < 400:
        return None  # Skip denoise, noise rendah
    elif iso < 800:
        return lambda img: guided_filter(img, radius=2, epsilon=0.01)
    elif iso < 3200:
        return lambda img: non_local_means(img, h_param=noise_sigma*0.6, 
                                            search_window=5, patch_size=2)
    else:
        return lambda img: non_local_means(img, h_param=noise_sigma*0.8,
                                            search_window=7, patch_size=3)
```

#### Stage 3: Color & Tone
```
Input:  Denoised RGB float32
Proses: White balance, color space ops, tone mapping
Output: Color-corrected RGB float32
```
**Modul yang SUDAH ADA**:
- `cvtColor_extended(code=COLOR_BGR2LAB)` → Konversi ke LAB untuk manipulasi L channel
- `cvtColor_extended(code=COLOR_BGR2HSV)` → Konversi ke HSV untuk manipulasi saturation
- `clahe()` → Adaptive histogram equalization di L channel

**Modul BARU**:
- `white_balance.py` - Apply AWB gains dari Camera2 metadata ke RGB channels
- `tone_mapping.py` - Reinhard/ACES tone mapping untuk HDR merge

#### Stage 4: Enhancement
```
Input:  Color-corrected RGB float32
Proses: Sharpening, detail enhancement
Output: Enhanced RGB float32
```
**Modul yang SUDAH ADA**:
- `smoothing.gaussian()` → Untuk unsharp mask: `sharpened = img + alpha * (img - gaussian(img))`
- `math_ops.gradients.sobel()` → Edge-aware enhancement
- `smoothing.guided_filter()` → Detail smoothing (separate base/detail layers)

#### Stage 5: Multi-Frame (Opsional - Burst/HDR Mode)
```
Input:  N frame RGB float32
Proses: Align frames → merge → reject ghost
Output: Single merged RGB float32 (lebih sedikit noise)
```
**Modul yang SUDAH ADA**:
- `farneback_flow()` → Optical flow alignment antar frame
- `phase_correlation()` → Global translation estimation (cepat, untuk coarse alignment)
- `alignment.ncc.zncc()` → Template matching untuk sub-pixel alignment
- `compute_spatial_weight()` → Ghost rejection weight maps
- `common.mean_division()` → Final weighted merge
- `common.hanning()` → Hanning accumulation weights
- `pyramid.build_image_pyramid()` → Multi-scale alignment
- `alignment.ransac.ransac_flow_cleanup()` → Outlier removal pada flow field

**Modul BARU**:
- `temporal_merge.py` - Orchestrator yang menggabungkan semua di atas

#### Stage 6: Output
```
Input:  Final RGB float32
Proses: Convert ke uint8, resize jika perlu
Output: NumPy array siap display
```
**Modul yang SUDAH ADA**:
- `common.to_numpy_if_needed()` → Download GPU → CPU
- `interpolation.bilinear_interpolation.bilinear_resize()` → Resize jika perlu
- `common._copy_kernel()` → Fast GPU copy

---

## 3. Strategi Zero-Copy

### 3.1 Alur Data Optimal

```
[YUV NumPy] ──upload──→ [Taichi Field] ──GPU chain──→ [Result Field] ──download──→ [NumPy Output]
     ↑                           │                            │                        ↑
     │                     BufferCache                  BufferCache                   │
     │                    (reuse buffer)               (reuse buffer)                 │
   1x copy                0x copy                    0x copy                    1x copy
                                                                              (hanya akhir)
```

**Total copy: 2x** (upload awal + download akhir)
**Target overhead: < 5ms** untuk 1080p

### 3.2 Buffer Reuse Pattern

```python
# Pre-allocate saat init pipeline
buffers = {
    'yuv':   get_temp_buffer((H * 3 // 2, W), ti.f32, "pool"),  # YUV planar
    'rgb':   get_temp_buffer((H, W, 3), ti.f32, "pool"),        # RGB working
    'gray':  get_temp_buffer((H, W), ti.f32, "pool"),           # Grayscale temp
    'flow':  get_temp_buffer((H, W, 2), ti.f32, "pool"),        # Optical flow
    'temp1': get_temp_buffer((H, W, 3), ti.f32, "pool"),        # Stage temp
}

# Chain processing - TIDAK ada alloc/dealloc di hot path
rgb = yuv_to_rgb(yuv_field, dst=buffers['rgb'])
denoised = non_local_means(rgb, dst=buffers['temp1'])
enhanced = clahe(denoised, dst=buffers['rgb'])  # Reuse rgb buffer
result = to_numpy_if_needed(enhanced, True)
```

### 3.3 Integrasi dengan Infrastructure yang Ada

| Infrastruktur | Lokasi | Peran di Pipeline |
|--------------|--------|-------------------|
| `BufferCache` | `common.py` | Pool buffer GPU, hindari realloc per-frame |
| `ti_thread` | `taichi_worker.py` | Serialized CUDA context, hindari context error |
| `ensure_taichi_field` | `common.py` | Upload NumPy→GPU dengan auto dtype mapping |
| `to_numpy_if_needed` | `common.py` | Download GPU→NumPy (hanya saat perlu) |
| `execute_tiled` | `oom_guard.py` | Auto-tiling untuk frame besar (4K+) |
| `cleanup_taichi` | `taichi_worker.py` | VRAM cleanup (cache/memory/full) |

---

## 4. Target Performa

### 4.1 Mode dan Target FPS

| Mode | Resolusi | Pipeline | Target FPS | Target Latency |
|------|----------|----------|------------|----------------|
| **Preview** | 1080p | YUV→RGB→Light Denoise→Output | 30 FPS | < 33ms |
| **Preview+** | 1080p | YUV→RGB→NLM→CLAHE→Output | 24 FPS | < 42ms |
| **Capture** | 4K (12MP) | YUV→RGB→NLM→Enhance→Output | 15 FPS | < 67ms |
| **Burst** | 1080p × 4 | 4-frame align→merge→Output | 10 FPS | < 100ms |
| **Night** | 4K × 8 | 8-frame align→heavy denoise→Output | 2 FPS | < 500ms |

### 4.2 Estimasi Latency per Stage (1080p, GPU mid-range)

| Stage | Algoritma | Estimasi | Modul |
|-------|-----------|----------|-------|
| Upload | NumPy → Taichi field | ~2ms | `ensure_taichi_field` |
| YUV→RGB | BT.601 kernel | ~1ms | `yuv_to_rgb` [BARU] |
| Denoise (fast) | NLM s3_p1 | ~3ms | `nlm.non_local_means` |
| Denoise (balanced) | NLM s5_p2 | ~8ms | `nlm.non_local_means` |
| Denoise (quality) | NLM s7_p3 | ~15ms | `nlm.non_local_means` |
| CLAHE | Adaptive histogram | ~4ms | `clahe` |
| Guided Filter | Edge-preserving | ~3ms | `guided_filter` |
| Gaussian | Separable blur | ~1ms | `gaussian` |
| Color Convert | BGR→LAB | ~1ms | `cvtColor_extended` |
| Optical Flow | Farneback 3-level | ~12ms | `farneback_flow` |
| Phase Correlation | FFT-based | ~3ms | `phase_correlation` |
| Spatial Weight | Ghost rejection | ~5ms | `compute_spatial_weight` |
| Resize | Bilinear | ~1ms | `resize` |
| Download | Taichi → NumPy | ~2ms | `to_numpy_if_needed` |

**Total Preview mode**: 2 + 1 + 3 + 2 = **~8ms** → **> 60 FPS capable**
**Total Preview+ mode**: 2 + 1 + 8 + 4 + 2 = **~17ms** → **~58 FPS**
**Total Capture mode**: 2 + 1 + 15 + 4 + 3 + 2 = **~27ms** → **~37 FPS**

---

## 5. Struktur Folder Baru

```
taichi_library/
├── taichi_algorithm/
│   ├── camera_api2/                    ← FOLDER BARU
│   │   ├── __init__.py                 ← Public API exports
│   │   ├── yuv_to_rgb.py              ← YUV_420_888/NV21/NV12 → RGB kernel
│   │   ├── camera2_pipeline.py        ← Pipeline orchestrator (Pusat)
│   │   ├── frame_dropper.py           ← Adaptive frame skip controller
│   │   ├── temporal_merge.py          ← Multi-frame stacking
│   │   ├── white_balance.py           ← AWB dari Camera2 metadata
│   │   ├── tone_mapping.py            ← HDR tone mapping
│   │   ├── camera2_bridge.py          ← Android Camera2 ↔ Python bridge
│   │   ├── camera2_config.py          ← Device profiles & capability detection
│   │   ├── algoritma_baru/            ← Sub-folder untuk eksperimen
│   │   │   ├── temporal_denoise.py    ← Temporal noise reduction
│   │   │   ├── motion_compensated.py  ← Motion-compensated processing
│   │   │   └── adaptive_exposure.py   ← Multi-exposure fusion
│   │   └── tests/
│   │       ├── test_yuv_conversion.py ← Parity test YUV→RGB vs OpenCV
│   │       ├── test_pipeline.py       ← Integration test
│   │       └── test_latency.py        ← Benchmark per stage
│   ├── alignment/          [SUDAH ADA]
│   ├── demosaicing/        [SUDAH ADA]
│   ├── denoising/          [SUDAH ADA]
│   ├── features/           [SUDAH ADA]
│   ├── image_processing/   [SUDAH ADA]
│   ├── interpolation/      [SUDAH ADA]
│   ├── math_ops/           [SUDAH ADA]
│   ├── optical_flow/       [SUDAH ADA]
│   ├── pyramid/            [SUDAH ADA]
│   ├── sfm/                [SUDAH ADA]
│   ├── smoothing/          [SUDAH ADA]
│   └── ...
```

---

## 6. Rencana Implementasi per Fase

### Fase 1: Foundation (Minggu 1-2)
**Goal**: Pipeline dasar berjalan, YUV→RGB→Denoise→Output

| # | Task | Modul | Dependensi |
|---|------|-------|-----------|
| 1.1 | Buat `yuv_to_rgb.py` dengan 3 format (YUV420, NV12, NV21) | `camera_api2/yuv_to_rgb.py` | `common.py` |
| 1.2 | Buat `camera2_config.py` - device profiles | `camera_api2/camera2_config.py` | - |
| 1.3 | Buat `frame_dropper.py` - adaptive skip | `camera_api2/frame_dropper.py` | - |
| 1.4 | Buat `camera2_pipeline.py` - basic chain | `camera_api2/camera2_pipeline.py` | 1.1, common.py |
| 1.5 | Integrasi denoising (NLM + Guided Filter) | Pipeline stage 2 | `denoising/nlm.py`, `smoothing/guided_filter.py` |
| 1.6 | Unit test YUV→RGB parity vs OpenCV | `tests/test_yuv_conversion.py` | 1.1 |
| 1.7 | Latency benchmark per stage | `tests/test_latency.py` | 1.4 |

**Deliverable**: Pipeline bisa proses 1 frame dari YUV → denoised RGB

### Fase 2: Enhancement & Color (Minggu 3-4)
**Goal**: Full preview pipeline dengan color correction

| # | Task | Modul | Dependensi |
|---|------|-------|-----------|
| 2.1 | Buat `white_balance.py` - apply AWB gains | `camera_api2/white_balance.py` | `common.py` |
| 2.2 | Integrasi CLAHE ke pipeline | Pipeline stage 3 | `image_processing/clahe.py` |
| 2.3 | Integrasi color conversion (LAB/HSV) | Pipeline stage 3 | `image_processing/color_convert.py` |
| 2.4 | Unsharp mask menggunakan Gaussian | Pipeline stage 4 | `smoothing/gaussian.py` |
| 2.5 | Buat `tone_mapping.py` - Reinhard/ACES | `camera_api2/tone_mapping.py` | `common.py` |
| 2.6 | Full preview pipeline integration | Pipeline orchestrator | Semua di atas |
| 2.7 | Parity test vs OpenCV untuk semua stage | Tests | Semua |

**Deliverable**: Preview pipeline lengkap (30 FPS target)

### Fase 3: Multi-Frame (Minggu 5-6)
**Goal**: Burst capture dengan multi-frame noise reduction

| # | Task | Modul | Dependensi |
|---|------|-------|-----------|
| 3.1 | Buat `temporal_merge.py` - frame accumulator | `camera_api2/temporal_merge.py` | `common.py` |
| 3.2 | Integrasi optical flow alignment | Multi-frame align | `optical_flow/farneback_flow.py` |
| 3.3 | Integrasi phase correlation (coarse align) | Multi-frame align | `alignment/phase_correlation.py` |
| 3.4 | Integrasi ghost rejection | Multi-frame merge | `compute_spatial.py` |
| 3.5 | Integrasi Hanning window accumulation | Multi-frame merge | `common.hanning` |
| 3.6 | Multi-frame denoise (align → stack → denoise) | Full burst pipeline | 3.1-3.5 + `denoising/nlm.py` |
| 3.7 | Benchmark multi-frame (4-frame, 8-frame) | Tests | 3.6 |

**Deliverable**: Burst capture 4-8 frame dengan noise reduction signifikan

### Fase 4: Android Bridge & Integration (Minggu 7-8)
**Goal**: Pipeline berjalan di Android device

| # | Task | Modul | Dependensi |
|---|------|-------|-----------|
| 4.1 | Buat `camera2_bridge.py` - Android bridge | `camera_api2/camera2_bridge.py` | - |
| 4.2 | Camera2 ImageReader → NumPy extraction | Bridge | Android JNI/Chaquopy |
| 4.3 | Camera2 metadata extraction (ISO, AWB, AF) | Bridge | Android API |
| 4.4 | End-to-end integration test di Android | Tests | Semua |
| 4.5 | Performance profiling di real device | Benchmark | Semua |
| 4.6 | OOM guard integration untuk 4K+ | Pipeline | `oom_guard.py` |
| 4.7 | Documentation & API reference | Docs | Semua |

**Deliverable**: Pipeline berjalan di Android dengan Camera2 API

---

## 7. Modul Baru Detail

### 7.1 `yuv_to_rgb.py` (~150 baris)

```python
"""
YUV to RGB Conversion - Taichi GPU
====================================
Camera2 API output format: YUV_420_888 (3-plane), NV12, NV21
Target: RGB float32 [0, 1] untuk processing pipeline

Reference: ITU-R BT.601 / BT.709
"""

# Kernel 1: YUV_420_888 3-plane → RGB
# Input: Y plane (H×W), U plane (H/2×W/2), V plane (H/2×W/2)
# Output: RGB (H×W×3) float32 [0,1]
# Formula (BT.601):
#   R = Y + 1.402 * (V - 128)
#   G = Y - 0.344136 * (U - 128) - 0.714136 * (V - 128)
#   B = Y + 1.772 * (U - 128)

# Kernel 2: NV12 (semi-planar Y + interleaved UV) → RGB
# Kernel 3: NV21 (semi-planar Y + interleaved VU) → RGB

# Dipanggil dari:
#   camera2_pipeline.py (Stage 1)
# Menggunakan:
#   common.ensure_taichi_field() - upload
#   common.get_temp_buffer() - buffer allocation
#   common.release_temp_buffer() - buffer return
```

### 7.2 `camera2_pipeline.py` (~400 baris)

```python
"""
Camera2 Real-Time Pipeline Orchestrator
========================================
Mengorkestrasi semua processing stages untuk Camera2 frame.

Architecture:
  - Pipeline pattern: Stage1 → Stage2 → ... → StageN
  - Zero-copy chaining di GPU (stay on Taichi field)
  - Buffer pool reuse (BufferCache)
  - Adaptive frame dropping (FrameDropper)
  - Mode presets (Preview, Capture, Burst, Night)
"""

class Camera2Pipeline:
    def __init__(self, width, height, mode="preview"):
        # Pre-allocate buffers dari BufferCache
        # Configure stages berdasarkan mode
        
    def process_frame(self, yuv_data, metadata=None):
        """Process single frame melalui pipeline"""
        # Upload sekali
        # Chain stages di GPU
        # Download sekali
        return result
    
    def process_burst(self, frames, metadata_list=None):
        """Process burst frames (multi-frame)"""
        # Align → Stack → Denoise → Enhance
        return merged_result

# Preset modes:
# PIPELINE_PREVIEW  = [YUV→RGB, light_denoise, output]
# PIPELINE_STANDARD = [YUV→RGB, denoise, CLAHE, sharpen, output]  
# PIPELINE_CAPTURE  = [YUV→RGB, heavy_denoise, full_enhance, output]
# PIPELINE_BURST    = [align, stack, denoise, enhance, output]
# PIPELINE_NIGHT    = [align, stack, heavy_denoise, tone_map, output]
```

### 7.3 `frame_dropper.py` (~100 baris)

```python
"""
Adaptive Frame Dropper
======================
Monitor processing latency dan drop frame secara adaptif
untuk menjaga target FPS dan mencegah queue buildup (lag).

Leverage: compute_spatial.NoiseEstimator untuk noise-aware decisions
"""

class FrameDropper:
    def __init__(self, target_fps=30):
        self.target_frame_time_ms = 1000.0 / target_fps
        self.processing_times = CircularBuffer(30)
    
    def should_process(self) -> bool:
        """Return True jika frame ini perlu diproses, False jika skip"""
        avg_ms = self.processing_times.average()
        return avg_ms < self.target_frame_time_ms * 0.95
    
    def record(self, start_ns, end_ns):
        """Record processing time untuk adaptive decisions"""
```

### 7.4 `temporal_merge.py` (~300 baris)

```python
"""
Temporal Multi-Frame Merge
============================
Align dan merge multiple frames untuk noise reduction / HDR.

Leverage (semua sudah ada):
  - farneback_flow()       → optical flow alignment
  - phase_correlation()    → global translation (coarse)
  - compute_spatial_weight() → ghost rejection
  - hanning() → accumulation weights
  - mean_division()        → final weighted merge
  - build_image_pyramid()  → multi-scale alignment
  - ransac_flow_cleanup()  → outlier removal
"""

def temporal_merge(frames, mode="denoise"):
    """
    Merge N frames menjadi 1 frame dengan noise reduction.
    
    Pipeline internal:
    1. Coarse align (phase_correlation)
    2. Fine align (farneback_flow)
    3. Ghost rejection (compute_spatial_weight)
    4. Weighted accumulation (hanning + mean_division)
    """
```

---

## 8. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Taichi tidak tersedia di Android | Pipeline tidak jalan | AOT mode: compile ke .tcm, load via C++ engine. Fallback: export sebagai native function |
| YUV→RGB parity tidak match OpenCV | Color accuracy buruk | Unit test parity vs `cv2.cvtColor(YUV2RGB)` dengan tolerance < 1 per channel |
| NLM terlalu lambat untuk real-time | FPS drop | Gunakan fast variant (s3_p1) untuk preview, quality (s7_p3) hanya untuk capture |
| Buffer pool OOM di 4K | Crash | Integrasi `oom_guard.execute_tiled()` untuk auto-tiling |
| CUDA context error | Crash | Semua operasi via `ti_thread` decorator (serialized worker) |
| Optical flow alignment terlalu mahal | Burst mode lambat | Gunakan phase_correlation (FFT, ~3ms) untuk coarse align, skip fine flow jika motion kecil |

---

## 9. Kriteria Sukses

| Kriteria | Target | Cara Ukur |
|----------|--------|-----------|
| Preview FPS | ≥ 30 FPS @ 1080p | `test_latency.py` benchmark |
| Preview latency | < 33ms per frame | Timestamp per stage |
| Capture quality | SSIM > 0.95 vs reference | `ssim()` comparison |
| Denoise effectiveness | PSNR improvement > 3dB | Test dengan synthetic noise |
| Memory stability | Zero OOM dalam 1000 frame | Stress test |
| Multi-frame alignment | Sub-pixel accuracy < 0.5px | `phase_correlation` + `zncc` validation |
| YUV→RGB parity | Max diff < 2 per channel vs OpenCV | `test_yuv_conversion.py` |
| Zero-copy overhead | < 5ms total upload+download | Timestamp measurement |

---

## 10. Pemetaan Fungsi → Modul (Quick Reference)

Untuk setiap kebutuhan pipeline, ini fungsi spesifik yang dipanggil:

```
KEBUTUHAN                          → FUNGSI                    → FILE
─────────────────────────────────────────────────────────────────────
Upload NumPy → GPU                 → common.ensure_taichi_field    → common.py
Download GPU → NumPy               → common.to_numpy_if_needed     → common.py
Buffer dari pool                   → common.get_temp_buffer        → common.py
Return buffer ke pool              → common.release_temp_buffer    → common.py
YUV → RGB [BARU]                   → yuv_to_rgb()                  → camera_api2/yuv_to_rgb.py
RAW Bayer → RGB                    → hamilton_demosaic()           → demosaicing/Hamilton_demosaice.py
Grayscale conversion               → common.cvtColor()             → common.py
Color space (HSV/LAB/YCrCb)       → cvtColor_extended()           → image_processing/color_convert.py
Split channels                     → common.split()                → common.py
Merge channels                     → common.merge()                → common.py
Denoise (fast)                     → non_local_means(sr=3, pr=1)   → denoising/nlm.py
Denoise (balanced)                 → non_local_means(sr=5, pr=2)   → denoising/nlm.py
Denoise (quality)                  → non_local_means(sr=7, pr=3)   → denoising/nlm.py
Denoise (heavy)                    → hfcd_denoise()                → denoising/bm3d.py
Edge-preserving smooth             → guided_filter()               → smoothing/guided_filter.py
Bilateral filter                   → bilateral_grid_filter()       → smoothing/bilateral_grid.py
Gaussian blur                      → gaussian()                    → smoothing/gaussian.py
Median filter                      → median()                      → smoothing/median_filter.py
CLAHE                              → clahe()                       → image_processing/clahe.py
Sharpen (unsharp mask)             → gaussian() + absdiff()        → smoothing/gaussian.py + common.py
Edge detection                     → canny()                       → image_processing/canny.py
Sobel gradient                     → sobel()                       → math_ops/gradients.py
Optical flow                       → farneback_flow()              → optical_flow/farneback_flow.py
Phase correlation                  → phase_correlation()           → alignment/phase_correlation.py
Template matching                  → zncc() / match_template()     → alignment/ncc.py
Ghost rejection                    → compute_spatial_weight()       → compute_spatial.py
Noise estimation                   → NoiseEstimator                → compute_spatial.py
Hanning window                     → hanning()  → common.py
Weighted merge                     → mean_division()               → common.py
Build pyramid                      → build_image_pyramid()         → pyramid/pyramid.py
Upsample flow                      → upsample_flow()               → pyramid/pyramid.py
RANSAC cleanup                     → ransac_flow_cleanup()         → alignment/ransac.py
MTB alignment                      → align_mtb()                   → alignment/mtb.py
Resize                             → resize()                      → __init__.py (dispatch)
Remap with flow                    → remap()                       → interpolation/remap.py
SSIM quality                       → ssim()                        → ssim.py
Auto-tile besar image              → execute_tiled()               → oom_guard.py
Serialized GPU thread              → @ti_thread                    → taichi_worker.py
Cleanup VRAM                       → cleanup_taichi()              → taichi_worker.py
Abs difference                     → absdiff()                     → common.py
Normalize                          → normalize()                   → normalize.py
Threshold                          → threshold() / otsu_threshold()→ threshold.py / otsu.py
Morphology                         → dilate() / erode()            → morphology.py
```

---

## 11. AOT Compilation Plan

Modul baru perlu di-compile ke .tcm untuk production deployment:

| Modul Baru | Target .tcm | Backend | Priority |
|-----------|-------------|---------|----------|
| `yuv_to_rgb` | `yuv_to_rgb_{cpu,cuda,vulkan}.tcm` | All 3 | KRITIS |
| `white_balance` | `white_balance_{cpu,cuda,vulkan}.tcm` | All 3 | SEDANG |
| `tone_mapping` | `tone_mapping_{cpu,cuda,vulkan}.tcm` | All 3 | SEDANG |

Mengikuti pattern yang SUDAH ADA di `aot_py/compile_*.py` (40+ compiler scripts sudah ada).

---

## 12. Kompatibilitas Android Camera2

| Android Version | API Level | Camera2 Level | Dampak ke Pipeline |
|----------------|-----------|---------------|-------------------|
| 5.0-5.1 | 21-22 | LEGACY/LIMITED | Preview only, no manual control |
| 6.0-7.1 | 23-25 | LIMITED/FULL | Standard pipeline |
| 8.0-9.0 | 26-28 | FULL | + Multi-camera |
| 10+ | 29+ | FULL/LEVEL_3 | + RAW, full manual, reprocessing |
| 11+ | 30+ | LEVEL_3 | + Concurrent camera |
| 13+ | 33+ | LEVEL_3 | + HDR video, stream config |

**Strategy**: Pipeline auto-detect hardware level dan adjust:
- `LEGACY` → Preview-only pipeline, skip heavy processing
- `LIMITED` → Standard pipeline tanpa manual 3A
- `FULL` → Full pipeline dengan manual control
- `LEVEL_3` → Full pipeline + RAW capture + reprocessing

---

*Dokumen ini akan di-update seiring progress implementasi.*
