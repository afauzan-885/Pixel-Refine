# Rencana Refactor template_flow.py

**Sumber**: `.qoder/plans/generic-optical-flow-template.md` (5626 bytes)

## Context

`template_flow.py` saat ini (281 baris) **bukan template yang benar-benar generik** — ia adalah template **block-matching pyramid** yang sudah terikat pada satu paradigma algoritma.

### Masalah
1. `custom_matching_cost` terikat pada patch comparison (SSD)
2. Kernel-kernel berstruktur tile-based search
3. Graph pipeline tetap: `coarse_search → upsample → refine → upsample → refine`
4. Kode duplikat dengan `compute_flow.py` (bicubic_weight, upsample_flow_bicubic_kernel)

### Constraint Taichi AOT Kritis
**Tidak ada runtime-polymorphic dispatch** dalam graph yang sudah dikompilasi. Setiap paradigma algoritma butuh kernel sendiri dan graph compilation sendiri.

## File yang Terlibat

| File | Status | Aksi |
|------|--------|------|
| `alignment_tile/template_flow.py` | EXISTS (281 baris) | **REWRITE** — jadi template generik |
| `alignment_tile/aot/shared_math.py` | NEW | **CREATE** — device math functions bersama |
| `alignment_tile/aot/shared_kernels.py` | NEW | **CREATE** — kernel reusable (upsample, downsample) |
| `alignment_tile/aot/cost_function.py` | EXISTS (61 baris) | **UNCHANGED** |
| `alignment_tile/aot/refinement.py` | EXISTS (23 baris) | **UNCHANGED** |
| `alignment_tile/compute_flow.py` | EXISTS (657 baris) | **UNCHANGED** — backward compatible |

## Task 1: Buat `aot/shared_math.py` (~40 baris)

Ekstrak fungsi matematika device-side yang digunakan bersama oleh semua algoritma flow.

### Isi
- `bicubic_weight(x)` — dari template_flow.py baris 14-23
- `clamp_coord(val, lo, hi)` — utility boundary-safe
- `bilinear_sample(field, y, x, h, w)` — sub-pixel sampling generic

**Path**: `pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/shared_math.py`

## Task 2: Buat `aot/shared_kernels.py` (~50 baris)

Ekstrak kernel `@ti.kernel` yang reusable dan tidak spesifik pada algoritma tertentu.

### Isi
- `upsample_flow_bicubic_kernel(src, dst, scale)` — dari template_flow.py baris 148-170
- `downsample_2x_kernel(src, dst)` — dari compute_flow_kernels.py baris 24-28

**Path**: `pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot/shared_kernels.py`

## Task 3: Rewrite `template_flow.py` (~250 baris)

Struktur baru dengan section-section yang jelas dan marking `# CUSTOMIZE HERE`:

```
Section A: Imports & Shared Infrastructure (~15 baris)
  - Import dari aot/shared_math, aot/shared_kernels, aot/cost_function, aot/refinement

Section B: Algorithm-Specific Device Functions (~30 baris)
  - # === CUSTOMIZE HERE: Cost Function ===
  - compute_flow_cost() — default SSD, dokumentasi cara ganti ke SAD/ZNCC/gradient

Section C: Algorithm-Specific Kernels (~100 baris)
  - # === CUSTOMIZE HERE: Coarsest Level Kernel ===
  - coarsest_level_kernel() — dokumentasi input contract, output contract
  - # === CUSTOMIZE HERE: Refinement Kernel ===
  - refinement_level_kernel() — dokumentasi cara proyeksikan flow dari level sebelumnya

Section D: AOT Graph Compilation (~80 baris)
  - compile_template_flow() — dokumentasi graph argument contract
  - Instruksi cara menambah/menghapus dispatch steps

Section E: CLI Entry (~5 baris)
```

**Path**: `pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/template_flow.py`

## Task 4: Verifikasi Backward Compatibility

- `compute_flow.py` **TIDAK meng-import** dari `template_flow.py` (verified via grep)
- `compute_flow.py` punya `bicubic_weight` dan `upsample_flow_bicubic_kernel` sendiri
- File `aot/shared_math.py` dan `aot/shared_kernels.py` bersifat ADDITIVE
- `template_flow_vulkan.tcm` tidak di-load oleh `alignment_core.py` (hanya contoh kompilasi)
- **Risiko: NOL** — tidak ada file yang terpengaruh

## Task 5: Verifikasi Kompilasi

- Jalankan `python -m alignment_tile.template_flow` untuk kompilasi AOT
- Pastikan `template_flow_vulkan.tcm` berhasil dihasilkan
- Pastikan graph `align_generic_3layer` bisa di-load oleh engine

## Paradigma yang Didukung Template Baru

| Paradigm | Cost Function | Kernel | Graph Pipeline |
|----------|---------------|--------|----------------|
| **Block-Matching** (default) | SSD/SAD patch | Exhaustive search → Local refine | pyramid coarse → refine → refine |
| **Horn-Schunck** | Gradient error + smoothness | Jacobi iterative per-pixel | iter_smooth(L2) → upsample → iter_smooth(L1) → upsample → iter_smooth(L0) |
| **Lucas-Kanade** | Patch least-squares | Inverse compositional | pyramid coarse → refine → refine |

## Constraint Compliance

- **Nested `ti.static` < 32 iterasi** — template menggunakan runtime loops
- **i32 safety** — tidak ada bit tricks berbahaya di template
- **Engine sync** — dokumentasi wajib `engine.sync()` sebelum `.release()`
- **Tidak mengubah `engine.py`** — single source of truth tidak disentuh

## Verification

1. **Kompilasi AOT**: Jalankan `template_flow.py` → hasilkan `template_flow_vulkan.tcm`
2. **Load test**: Load TCM via engine, pastikan graph `align_generic_3layer` bisa di-run
3. **Compute flow**: Pastikan `compute_flow.py` masih bisa dikompilasi tanpa error
4. **Import test**: Pastikan `from .aot.shared_math import bicubic_weight` berhasil
