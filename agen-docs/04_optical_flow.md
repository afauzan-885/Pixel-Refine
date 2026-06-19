# Optical Flow Modules

## Overview

Pixel Refine mendukung berbagai algoritma optical flow yang dikompilasi sebagai AOT modules dan dijalankan melalui `engine.py` (C++ AOT runtime), dengan **zero Taichi JIT dependency** di production.

## Optical Flow AOT Modules

| Backend | TCM File | Size | Graphs | Deskripsi |
|---------|----------|------|--------|-----------|
| **BMA** | `compute_flow_vulkan.tcm` | ~100 KB | `align_end_to_end_3layer` | Multi-size Block Matching Alignment (SAD/SSD, 3-layer pyramid) |
| **Horn-Schunck** | `template_flow_vulkan.tcm` | 43.2 KB | `hs_align_3layer_10`, `hs_align_3layer_20` | Horn-Schunck GPU dengan Jacobi solver (10/20 iterations) |
| **Farneback AOT** | `farneback_flow_vulkan.tcm` | 140.5 KB | `farneback_multi_3`, `farneback_clear_flow`, `farneback_upsample_flow` | Farneback GPU AOT (polynomial expansion, 3 iterations) |
| **Farneback JIT** | N/A | N/A | N/A | Farneback JIT via `taichi_algorithm.farneback_flow()` (requires `AOT_MODE=0`) |

## 1. BMA (Block Matching Alignment)

**Modul**: `compute_flow.py` → `compute_flow_vulkan.tcm`

### Detail
- Mengevaluasi pencocokan ubin secara hierarkis (induk 32×32 dan 4× sub-ubin 16×16)
- Jika rata-rata cost dari 4 sub-ubin lebih baik 15% dari ubin induk (`avg_sub_cost < 0.85 * best_cost`), maka struktur sub-blok diterima (Split) dan dilakukan refinement sub-pixel paraboloid individu
- Menggunakan metrik pencocokan standar **SAD** dan **SSD** untuk akurasi dan performa stabil serta menghemat memori GPU

### Kapan Gunakan
- **Default** untuk alignment umum
- Cepat dan akurat untuk translasi kecil hingga menengah
- Cocok untuk handheld photography dengan slight camera shake

## 2. Horn-Schunck

**Modul**: `template_flow.py` → `template_flow_vulkan.tcm`

### Detail
- Template bersih yang memisahkan device math/cost functions, kernel pencarian kasar & halus, dan builder graf AOT
- Menggunakan **Jacobi solver** untuk iterative optimization
- Mendukung 10 atau 20 iterations per pyramid level

### Graphs
- `hs_align_3layer_10`: 3-level pyramid, 10 Jacobi iterations
- `hs_align_3layer_20`: 3-level pyramid, 20 Jacobi iterations

### Kapan Gunakan
- Gerakan halus (smooth motion)
- Rotasi lambat (slow rotation)
- Video stabilization dengan gradual motion

## 3. Farneback AOT

**Modul**: `taichi_library/taichi_algorithm/farneback_flow.py` → `farneback_flow_vulkan.tcm`

### Detail
- Implementasi AOT Farneback GPU yang telah diselaraskan secara matematis dengan OpenCV Farneback
- Menggunakan filter Gaussian separable (O(N) horizontal + vertikal) untuk efisiensi komputasi sistem tensor di GPU
- Mengimplementasikan estimasi polinomial kuadratik least-squares berbasis bobot Gaussian 5×5 dinamis

### Graphs
- `poly_expansion_f32`: Polynomial expansion (vertical + horizontal)
- `farneback_iteration`: Single iteration (tensors → blur → solve)
- `farneback_multi_2/3/5`: Batched N iterations
- `farneback_upsample_flow`: Bicubic flow upsampling
- `farneback_clear_flow`: Zero-initialize flow field

### Kapan Gunakan
- Gerakan kompleks (complex motion)
- Polynomial expansion memberikan estimasi yang lebih smooth
- Cocok untuk scene dengan varying motion patterns

### Performance (128x128 synthetic tests)

| Test Case | AEPE (px) | SSIM | Time AOT | Time OpenCV |
|-----------|-----------|------|----------|-------------|
| Translation-8bit-gray | 5.72 | 0.09 | 190 ms* | 21 ms |
| Rotation-8bit-gray | 0.07 | 0.99 | 5 ms | 10 ms |
| Diverse-8bit-gray | 0.52 | 0.93 | 5 ms | 8 ms |
| Diverse-16bit-gray | 0.52 | 0.93 | 4 ms | 7 ms |
| Diverse-8bit-color | 0.52 | 0.93 | 3 ms | 7 ms |
| Large-8bit-gray (256x256) | 9.58 | 0.16 | 5 ms | 28 ms |

*Cold start (Vulkan pipeline warm-up). Subsequent calls: 3-6 ms.

## 4. Farneback JIT

**Modul**: `taichi_library/taichi_algorithm/farneback_flow.py`

### Detail
- JIT version dari Farneback optical flow
- Memerlukan `AOT_MODE=0` untuk menjalankan
- Digunakan untuk development/testing, bukan production

### Kapan Gunakan
- Development dan debugging
- Testing algoritma baru sebelum kompilasi AOT
- Prototyping

## Backend Selection di MFDenoiser

```python
# Via UI Settings (JSON config)
{
    "optical_flow_type": "alignment_tile",  # BMA (default)
    # atau
    "optical_flow_type": "horn_schunck",
    # atau
    "optical_flow_type": "farneback_aot",
}

# Via Code Override
processor = MFDenoiserAlgorithm(db_path)
output_path = processor.run_pipeline(
    single_process=True,
    optical_flow_type="farneback_aot",  # Override
)
```

## Compilation

### Farneback AOT
```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_farneback_tcm
```

Output: `taichi_library/taichi_algorithm/aot_tcm/farneback_flow_vulkan.tcm`

### Horn-Schunck AOT
```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_template_flow_tcm
```

Output: `taichi_library/taichi_algorithm/aot_tcm/template_flow_vulkan.tcm`

## Test Results Summary

### TCM Integrity Test
- `farneback_flow_vulkan.tcm`: ✅ Loaded, graphs verified
- `template_flow_vulkan.tcm`: ✅ Loaded, graphs verified

### All Tests Passed (17/17)
- Farneback AOT: 8/8 passed
- Horn-Schunck AOT: 7/7 passed
- TCM Integrity: 2/2 passed
