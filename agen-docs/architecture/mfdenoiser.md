# Arsitektur MFDenoiser dan Denoising

**Sumber**: 3 memory files dari `.qoder/memories/.../project_introduction/` + `project_tech_stack/`

## MFDenoiser Universal Tiling Orchestrator

MFDenoiser berfungsi sebagai **universal tiling orchestrator** yang menangani semua infrastruktur tiling.

### Tanggung Jawab Utama
- **Grid computation**: Menghitung grid tiling berdasarkan ukuran gambar
- **Hanning-weighted accumulation**: Stitching tile dengan Hanning window untuk menghindari artefak
- **Work resolution scaling**: Mengatur resolusi kerja untuk optimasi performa

### Arsitektur Decoupled
MFDenoiser memisahkan **tiling logic** dari **algorithm logic**:
- MFDenoiser = tiling infrastructure
- External processors = per-tile computation

### Processor Interface
Setiap processor mengimplementasi standardized interface:
```python
setup()                    # Inisialisasi
preprocess_batch()         # Preprocess batch gambar
process_tile(tile)         # Proses satu tile
teardown()                 # Cleanup
```

## Mode Denoising

### 1. Average
- **Resolusi**: Original resolution (misal 4096×3072) tanpa downscaling
- **Alasan**: Computational cost rendah, tidak perlu optimasi resolusi
- **Routing**: Melalui MFDenoiser universal tiling infrastructure
- **Status**: Foundational tiling pattern (algoritma pertama yang menggunakan pattern ini)

### 2. Similarity
- **Resolusi**: Work resolution downsampling (>12.5MP images ke ~4082×3060)
- **Alasan**: Movement-robust, lebih intensif komputasi
- **Optimasi**: Work resolution untuk menjaga performa

### 3. Median
- **Resolusi**: Pattern sama dengan Average
- **Status**: Mengikuti pattern yang established oleh Average

### 4. HFCD (Hybrid Fast Collaborative Denoising)
- **Paradigma**: Single-pass denoising
- **Kombinasi**:
  - FFT cross-correlation untuk block matching (dari G-BM3D)
  - Per-group 2D DCT + hard thresholding (dari BM3D Full)
  - Exponential-weighted atomic aggregation (dari NLM)
- **Parameter**: Fixed group K=16, no 3D Haar, no two-step dependency
- **Interface**: Invoke eksklusif sebagai `taichi_aot.bm3d()`
- **Sifat**: Fully self-contained, no fallback dependencies
- **GPU Efficiency**: Didesain untuk efisiensi GPU

## Spatial Fusion Extension

MFDenoiser mendukung **`spatial_fusion` backend**:
- Module: `compute_spatial`
- Fungsi: Ghost rejection
- Implementasi: GPU-accelerated spatial weight computation via Taichi AOT kernels
- Lokasi: `process_in_gpu`

## Resolution Handling

### Mode Average
```python
# _compute_work_resolution() HARUS di-bypass
# Proses di original resolution tanpa downscaling
```

### Mode Similarity
```python
# _compute_work_resolution() AKTIF
# Downscaling untuk optimasi performa
```

## Alur Kerja Tiling
```
Input Images → MFDenoiser (Grid Computation) → Tile Processing → Hanning Stitching → Output
                    ↓                              ↓
            Work Resolution Scaling      External Processor
                                         (Average/Similarity/HFCD)
```
