# Optical Flow dan Taichi AOT Modules

**Sumber**: 4 memory files dari `.qoder/memories/.../project_tech_stack/` + `task_summary_experience/`

## Production AOT Modules

### Farneback Optical Flow
- **File**: `farneback_flow_vulkan.tcm`
- **Ukuran**: 140.5 KB
- **Graphs**: 7 graphs
- **Lokasi**: `taichi_library/taichi_algorithm/aot_tcm/`
- **Input**: 8-bit/16-bit grayscale dan color

### Horn-Schunck Optical Flow
- **File**: `template_flow_vulkan.tcm`
- **Ukuran**: 43.2 KB
- **Lokasi**: `taichi_library/taichi_algorithm/aot_tcm/`
- **Input**: 8-bit/16-bit grayscale dan color

### Loading Mechanism
- Loaded via `engine.py` (C++ AOT runtime)
- **Zero** Taichi JIT dependency untuk production

## Horn-Schunck Integration

### Kernels (9 total)
1. Gradient kernels (Sobel-based)
2. Jacobi iterative step kernel
3. Coarsest level kernel (L2 smoothness)
4. Refinement level kernels (L1, L0)
5. Utility kernels (flow projection, averaging)

### AOT Graphs (8 total)
- `hs_align_3layer_10` — 10 iterations
- `hs_align_3layer_20` — 20 iterations
- `hs_align_3layer_50` — 50 iterations
- Base alignment graphs

### Integration Points
- **File**: `alignment_core.py`
- **Features**:
  - Conditional dispatch (AOT vs JIT)
  - Correct TCM path resolution
  - Temp buffer management (`flow_temp_l0`, `flow_temp_l1`, `flow_temp_l2`)
  - Backward compatibility terjamin

## Dynamic Backend Routing

### Function: `_align_taichi_gpu`
- Mendukung **dynamic backend selection**
- Import modules dari `taichi_library.taichi_algorithm.__init__.py`

### Backend Options
```python
# perform_alignment_gpu extended untuk route ke:
flow_backend="farneback_jit"   # JIT-based Farneback
flow_backend="horn_schunck_jit" # JIT-based Horn-Schunck
flow_backend="farneback_aot"    # AOT Farneback (production)
flow_backend="horn_schunck_aot" # AOT Horn-Schunck (production)
```

### Pipeline Strategy
1. **Compute optical flow** di `work_res` (resolusi pyramid level lebih rendah)
2. **Perform warping** di `full_res` (resolusi original)
3. **Hasil**: High-quality alignment dengan performa optimal

## AOT Compilation Process

### Farneback
```bash
# Script: compile_farneback_tcm.py
# Mode: AOT_MODE=0
python -m taichi_algorithm.aot_py.compile_farneback_tcm
# Output: farneback_flow_vulkan.tcm
```

### Analysis Suite
```bash
# Script: compile_analysis_suite_tcm.py
# Compile: CLAHE, NLM, Canny, Guided Filter, Hough, Color Convert, Otsu
python -m taichi_algorithm.aot_py.compile_analysis_suite_tcm
# Output: analysis_suite_vulkan.tcm
```

### Template Flow (Horn-Schunck)
```bash
# Script: compile_template_flow_tcm.py
python -m taichi_algorithm.aot_py.compile_template_flow_tcm
# Output: template_flow_vulkan.tcm
```

## Required TCM Modules (9 Algoritma)

| # | Algoritma | Status | Notes |
|---|-----------|--------|-------|
| 1 | CLAHE | Required | Contrast Limited Adaptive Histogram Equalization |
| 2 | NLM | Required | Non-Local Means denoising |
| 3 | Canny | Required | Edge detection |
| 4 | Guided Filter | Required | Edge-preserving smoothing |
| 5 | Hough | Required | Line/circle detection |
| 6 | Color Convert | Required | Color space conversion |
| 7 | Otsu | Required | Thresholding |
| 8 | Inpaint | Required | Image inpainting |
| 9 | Seamless Clone | Required | Poisson blending |

## Validation Protocol

### Synthetic Accuracy Tests
- **Input**: 8-bit dan 16-bit
- **Channels**: Grayscale (1) dan Color (3)
- **Metrics**: SSIM, MAE
- **Baseline**: OpenCV reference implementations

### Test Coverage
```python
# test_comprehensif.py
run_jit_algorithm_tests()
# 1. AOT tests
# 2. JIT tests (AOT_MODE=0)
# 3. Pipeline stress testing
```

## template_flow.py Refactor Plan

### Status: Direncanakan (belum diimplementasi)

### Tujuan
Refactor dari **281 baris** (block-matching pyramid template) menjadi **template generik** (~250 baris)

### File yang Terlibat

| File | Status | Aksi |
|------|--------|------|
| `alignment_tile/template_flow.py` | EXISTS (281 baris) | **REWRITE** |
| `alignment_tile/aot/shared_math.py` | NEW | **CREATE** |
| `alignment_tile/aot/shared_kernels.py` | NEW | **CREATE** |
| `alignment_tile/aot/cost_function.py` | EXISTS (61 baris) | UNCHANGED |
| `alignment_tile/aot/refinement.py` | EXISTS (23 baris) | UNCHANGED |
| `alignment_tile/compute_flow.py` | EXISTS (657 baris) | UNCHANGED |

### Task 1: `aot/shared_math.py` (~40 baris)
Ekstrak fungsi matematika device-side:
- `bicubic_weight(x)` — Bicubic interpolation weights
- `clamp_coord(val, lo, hi)` — Boundary-safe clamping
- `bilinear_sample(field, y, x, h, w)` — Sub-pixel sampling

### Task 2: `aot/shared_kernels.py` (~50 baris)
Ekstrak kernel reusable:
- `upsample_flow_bicubic_kernel(src, dst, scale)` — Upsampling
- `downsample_2x_kernel(src, dst)` — Downsampling

### Task 3: Rewrite `template_flow.py` (~250 baris)
Section-based structure dengan `# CUSTOMIZE HERE` markers:

```
Section A: Imports & Shared Infrastructure (~15 baris)
Section B: Algorithm-Specific Device Functions (~30 baris)
  # === CUSTOMIZE HERE: Cost Function ===
Section C: Algorithm-Specific Kernels (~100 baris)
  # === CUSTOMIZE HERE: Coarsest Level Kernel ===
  # === CUSTOMIZE HERE: Refinement Kernel ===
Section D: AOT Graph Compilation (~80 baris)
Section E: CLI Entry (~5 baris)
```

### Paradigma yang Didukung

| Paradigm | Cost Function | Kernel | Graph Pipeline |
|----------|---------------|--------|----------------|
| **Block-Matching** (default) | SSD/SAD patch | Exhaustive search → Local refine | pyramid coarse → refine → refine |
| **Horn-Schunck** | Gradient error + smoothness | Jacobi iterative per-pixel | iter_smooth(L2) → upsample → iter_smooth(L1) → upsample → iter_smooth(L0) |
| **Lucas-Kanade** | Patch least-squares | Inverse compositional | pyramid coarse → refine → refine |

### Task 4: Verifikasi Backward Compatibility
- `compute_flow.py` **TIDAK meng-import** dari `template_flow.py`
- `aot/shared_math.py` dan `aot/shared_kernels.py` bersifat ADDITIVE
- **Risiko: NOL**

### Task 5: Verifikasi Kompilasi
1. Jalankan `python -m alignment_tile.template_flow`
2. Pastikan `template_flow_vulkan.tcm` berhasil dihasilkan
3. Pastikan graph `align_generic_3layer` bisa di-load oleh engine
