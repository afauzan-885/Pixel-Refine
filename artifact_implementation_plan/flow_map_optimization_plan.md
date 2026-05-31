# Flow Map VRAM Optimization Plan
## `remap_with_flow` — Fused Kernel Approach

---

## Latar Belakang

Pipeline warp saat ini di [`alignment_core.py`](file:///e:/APP Developer/Pixel Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/alignment_core.py) (L726–L811) terdiri dari **3 langkah terpisah**:

```
Step C1+C2: smooth_flow_gpu(flow_l0)    → smooth_flow_buf  [work_res, 2ch, f32] ~5.7 MB
Step C3:    build_flow_maps(smooth_flow) → map_x_gpu        [full_res, f32]     ~45.8 MB
                                         → map_y_gpu        [full_res, f32]     ~45.8 MB
Step C4:    remap(src, map_x, map_y)    → aligned image
```

**Total VRAM overhead dari map_x + map_y: ~91.6 MB per gambar 12MP (183 MB total kedua buffer)**

Karena `map_x_gpu` dan `map_y_gpu` dialokasikan sekali dan di-reuse antar frame (pre-alloc), mereka tetap duduk di VRAM sepanjang seluruh alignment loop.

---

## Target Optimasi

| Item | Sebelum | Sesudah | Hemat |
|---|---|---|---|
| `map_x_gpu` (full_res f32) | ~45.8 MB | **0** | 45.8 MB |
| `map_y_gpu` (full_res f32) | ~45.8 MB | **0** | 45.8 MB |
| `smooth_flow_buf` (work_res f32 2ch) | ~5.7 MB | ~5.7 MB | 0 |
| **Total** | **~97.3 MB** | **~5.7 MB** | **~91.6 MB** |

---

## Solusi: Kernel `remap_with_flow`

Fusi Step C3 + C4 menjadi **satu kernel GPU tunggal** yang:
1. Membaca flow di `work_res` (kecil)
2. Melakukan bilinear interpolation flow **on-the-fly** ke koordinat full_res
3. Langsung meng-sample source image di posisi yang sudah di-warp

### Logika Kernel (Pseudo-code Taichi)

```python
@ti.kernel
def remap_with_flow_kernel(
    src:        ti.types.ndarray(dtype=ti.u16, ndim=3),  # full_res RGB source
    flow:       ti.types.ndarray(dtype=ti.f32, ndim=3),  # work_res (H_w, W_w, 2)
    dst:        ti.types.ndarray(dtype=ti.u16, ndim=3),  # full_res RGB output
    h_full:     ti.i32,
    w_full:     ti.i32,
    h_work:     ti.i32,
    w_work:     ti.i32,
    sigma_x:    ti.f32,  # smoothing (baked into kernel or pre-smoothed)
):
    for y, x in ti.ndrange(h_full, w_full):
        # 1. Map pixel (x,y) ke koordinat work_res
        fx = x * (w_work / w_full)   # float coordinate di work_res
        fy = y * (h_work / h_full)

        # 2. Bilinear interpolate flow (du, dv) di work_res
        x0 = ti.cast(ti.floor(fx), ti.i32)
        y0 = ti.cast(ti.floor(fy), ti.i32)
        x1 = ti.min(x0 + 1, w_work - 1)
        y1 = ti.min(y0 + 1, h_work - 1)
        wx = fx - x0
        wy = fy - y0

        du = (flow[y0, x0, 0] * (1-wx) * (1-wy) +
              flow[y0, x1, 0] *    wx  * (1-wy) +
              flow[y1, x0, 0] * (1-wx) *    wy  +
              flow[y1, x1, 0] *    wx  *    wy)

        dv = (flow[y0, x0, 1] * (1-wx) * (1-wy) +
              flow[y0, x1, 1] *    wx  * (1-wy) +
              flow[y1, x0, 1] * (1-wx) *    wy  +
              flow[y1, x1, 1] *    wx  *    wy)

        # 3. Scale displacement dari work_res → full_res
        src_x = x + du * (w_full / w_work)
        src_y = y + dv * (h_full / h_work)

        # 4. Clamp ke boundary
        src_x = ti.max(0.0, ti.min(src_x, w_full - 1.001))
        src_y = ti.max(0.0, ti.min(src_y, h_full - 1.001))

        # 5. Bilinear sample dari source image
        ix0, iy0 = ti.cast(ti.floor(src_x), ti.i32), ti.cast(ti.floor(src_y), ti.i32)
        ix1 = ti.min(ix0 + 1, w_full - 1)
        iy1 = ti.min(iy0 + 1, h_full - 1)
        tx = src_x - ix0
        ty = src_y - iy0

        for c in ti.static(range(3)):
            val = (src[iy0, ix0, c] * (1-tx) * (1-ty) +
                   src[iy0, ix1, c] *    tx  * (1-ty) +
                   src[iy1, ix0, c] * (1-tx) *    ty  +
                   src[iy1, ix1, c] *    tx  *    ty)
            dst[y, x, c] = ti.cast(val, ti.u16)
```

---

## Rencana Perubahan File

### 1. [NEW] TCM Kernel — `remap_with_flow`

#### [NEW] `compile_remap_with_flow_tcm.py`
**Path:** `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/compile_remap_with_flow_tcm.py`

- Mendefinisikan kernel `remap_with_flow_u16` dan `remap_with_flow_u8`
- Support dtype: `u8` (JPEG source) dan `u16` (RAW/16-bit source)
- Support `smooth_sigma` parameter untuk bake Gaussian smoothing ke dalam kernel (opsional, alternatif: gunakan `smooth_flow_buf` yang sudah di-smooth sebelumnya)
- Kompilasi ke `remap_with_flow_vulkan.tcm`

**Graph signature:**
```python
args = [
    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src",  ndim=3, dtype=ti.u16),
    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ndim=3, dtype=ti.f32),
    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst",  ndim=3, dtype=ti.u16),
    ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "h_full", dtype=ti.i32),
    ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "w_full", dtype=ti.i32),
    ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "h_work", dtype=ti.i32),
    ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "w_work", dtype=ti.i32),
]
```

---

### 2. [MODIFY] `taichi_aot/__init__.py` atau modul wrapper

Tambah fungsi `remap_with_flow()`:

```python
def remap_with_flow(
    src_gpu,          # TaichiGPUBuffer: full_res image (u8 atau u16, 3ch)
    flow_gpu,         # TaichiGPUBuffer: work_res flow (f32, 2ch)
    full_h, full_w,   # int: dimensi output full-res
    work_h, work_w,   # int: dimensi flow
    dst_gpu=None,     # TaichiGPUBuffer opsional (reuse buffer)
    return_gpu=True,  # True: kembalikan GPU buffer, False: kembalikan numpy
):
    """
    Fused remap: bilinear interpolate flow on-the-fly + warp src image.
    Eliminates need for map_x, map_y full-res buffers (~91.6 MB VRAM saved).
    """
    engine = AOTEngine()
    if dst_gpu is None:
        dst_gpu = engine.allocate(src_gpu.shape, dtype=src_gpu.dtype, host_accessible=not return_gpu)
    
    mod = engine.load("remap_with_flow_vulkan.tcm")
    mod.run("remap_with_flow_u16",
        src=src_gpu, flow=flow_gpu, dst=dst_gpu,
        h_full=full_h, w_full=full_w,
        h_work=work_h, w_work=work_w,
    )
    engine.sync()
    
    if return_gpu:
        return dst_gpu
    return dst_gpu.to_numpy()
```

---

### 3. [MODIFY] `alignment_core.py`

**File:** [`alignment_core.py`](file:///e:/APP Developer/Pixel Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_features/alignment_core.py)

#### Perubahan Pre-alloc (L633–L648)

```python
# HAPUS:
map_x_gpu = engine.allocate((full_h_ref, full_w_ref), dtype=np.float32)
map_y_gpu = engine.allocate((full_h_ref, full_w_ref), dtype=np.float32)

# GANTI dengan:
# Pre-alloc dst buffer untuk hasil warp (reuse setiap frame)
aligned_buf_gpu = engine.allocate(
    (full_h_ref, full_w_ref, 3), dtype=np.uint16, host_accessible=True
)
```

#### Perubahan Warp Loop (L735–L811)

```python
# HAPUS Step C3 (build_flow_maps) dan step C4 (remap):
# map_x_gpu, map_y_gpu = taichi_aot.build_flow_maps(...)
# aligned_np = taichi_aot.remap(full_res_img, map_x_gpu, map_y_gpu, ...)

# GANTI dengan:
# Step C3 (NEW): Fused remap — tidak perlu map_x/map_y lagi!
aligned_buf_gpu = taichi_aot.remap_with_flow(
    src_gpu=full_res_img_gpu,  # upload full_res_img ke GPU
    flow_gpu=smooth_flow_buf,  # work_res flow yang sudah di-smooth
    full_h=full_h_ref,
    full_w=full_w_ref,
    work_h=h_w,
    work_w=w_w,
    dst_gpu=aligned_buf_gpu,   # reuse buffer
    return_gpu=True,
)

# Download result (hanya jika perlu ke HDF5 atau numpy_u16 format)
if h5_file_handle is not None:
    aligned_np = aligned_buf_gpu.to_numpy()
    save_to_hdf5(h5_file_handle, f"image_{i}", aligned_np, exif)
    del aligned_np
```

#### Perubahan Finally Block (hapus map_x/map_y dari cleanup)

```python
# HAPUS dari finally block:
# map_x_gpu.destroy()
# map_y_gpu.destroy()

# TAMBAH ke finally block:
aligned_buf_gpu.destroy()
```

---

## Optimasi Sekunder: float16 Flow Buffers

> [!NOTE]
> Opsional — dampak lebih kecil (~3 MB per frame), tapi mudah diimplementasikan.

```python
# Di alignment_core.py, L634–L640 (alokasi flow buffers)
# Ganti dtype=np.float32 → dtype=np.float16

flow_l0 = engine.allocate((h_w, w_w, 2), dtype=np.float16)   # was float32
flow_l1 = engine.allocate((h_w//2, w_w//2, 2), dtype=np.float16)
flow_l2 = engine.allocate((h_w//4, w_w//4, 2), dtype=np.float16)
smooth_flow_buf = engine.allocate((h_w, w_w, 2), dtype=np.float16)
```

> [!WARNING]
> Perlu verifikasi bahwa AOT kernel `compute_flow` dan `smooth_flow_gpu` mendukung `f16`. Jika belum, perlu recompile TCM dengan dtype `f16`, atau konversi hanya dilakukan setelah flow selesai dihitung.

---

## Ringkasan VRAM Savings

| Fase | Sebelum | Sesudah Opt-1 | Sesudah Opt-1+2 |
|---|---|---|---|
| `map_x_gpu` | ~45.8 MB | **0** | **0** |
| `map_y_gpu` | ~45.8 MB | **0** | **0** |
| `smooth_flow_buf` (f32) | ~5.7 MB | ~5.7 MB | ~2.85 MB (f16) |
| `flow_l0` (f32) | ~5.7 MB | ~5.7 MB | ~2.85 MB (f16) |
| `flow_l1+l2` (f32) | ~1.75 MB | ~1.75 MB | ~0.87 MB (f16) |
| `aligned_buf_gpu` (u16) | ~0 (tmp) | ~34.3 MB (reuse) | ~34.3 MB |
| **NET VRAM SAVE** | — | **~91.6 MB** | **~94.4 MB** |

---

## Verification Plan

### Unit Test
Banding output `taichi_aot.remap(src, map_x, map_y)` vs `taichi_aot.remap_with_flow(src, flow)` pada frame test:
```python
# MAE harus < 1.0 (sub-pixel rounding differences only)
assert np.mean(np.abs(result_old.astype(np.float32) - result_new.astype(np.float32))) < 1.0
```

### Integration Test
Jalankan full Similarity pipeline, pastikan:
1. Tidak ada OOM (out-of-memory) error
2. Output SSIM vs versi lama > 0.999
3. Benchmark VRAM usage via Vulkan memory tracking

### Files to Test
- `test_algorithm/IMG_20250401_182043_B003.png` (9.1 MP standard test)
- Batch test dengan 5 frame

---

## Urutan Implementasi

- [ ] **Step 1**: Tulis dan compile `compile_remap_with_flow_tcm.py` → generate `remap_with_flow_vulkan.tcm`
- [ ] **Step 2**: Tambah `taichi_aot.remap_with_flow()` wrapper di Python bridge
- [ ] **Step 3**: Modifikasi `alignment_core.py` — hapus `map_x_gpu`, `map_y_gpu`, ganti warp step
- [ ] **Step 4**: Unit test akurasi (MAE < 1.0 vs remap lama)
- [ ] **Step 5**: *(Opsional)* Float16 flow buffers — verifikasi kompatibilitas dtype di TCM
- [ ] **Step 6**: Integration test full pipeline + benchmark VRAM
