# Pixel Refine - Skill Guide: Penggunaan engine.py & __init__.py

> Panduan prosedural untuk menulis dan menambah fungsi algoritma baru ke pipeline Taichi AOT Pixel Refine.
> Dibaca bersama `agen.md` (knowledge base proyek) dan kode sumber di `engine.py` / `__init__.py`.

---

## 🗺️ Gambaran Kasar Proyek & Pipeline

Untuk meminimalkan pembacaan file source code yang besar secara berulang (menghemat token & limit harian), berikut adalah peta lengkap dari seluruh komponen di folder [`pixel_refine_desktop/enhance_stack/core/algorithm/`](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm):

### 1. Peta Lengkap Struktur Folder & File
* **`base_worker.py`**: Kelas dasar (`BaseWorker`) untuk threading / eksekusi asinkron pemrosesan gambar agar GUI tetap responsif.
* **`taichi_aot/`** (Runtime & Public API Bridge):
  * [`engine.py`](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py): **Single Source of Truth backend C++**. Mengatur interaksi low-level C-API Taichi, inisialisasi runtime Vulkan/CUDA/CPU, alokasi buffer (`TaichiGPUBuffer`), buffer pool recycling, pipeline recording (`rec_pipeline`), universal DMA fast-copy, dan C++ direct image IO (WIC decoder). **Sangat dilarang diubah tanpa izin.**
  * [`__init__.py`](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/__init__.py): **Public API Tunggal**. Semua kode Python eksternal memanggil fungsi Taichi lewat sini. Berisi wrapper Python tingkat tinggi untuk pemanggilan grafik TCM (seperti `demosaic`, `warp_affine`, `ofb`, `gaussian_blur`, `resize`, `box_filter`, `median_filter`, dll) yang otomatis menangani upload/download NumPy, alokasi VRAM, dan sinkronisasi GPU.
* **`taichi_algorithm/`** (Kernel Taichi & AOT Compiler):
  * **File Kernel JIT (Python)**:
    * `hamilton_demosaice.py`: Kernel Hamilton-Adams untuk interpolasi Bayer RAW ke RGB/BGR.
    * `remap.py`: Kernel WarpAffine GPU & Remap GPU (inverse mapping bilinear dengan border reflection).
    * `ofb.py`: Kernel O-FAST-BRIEF (FAST detector, 5x5 NMS, centroid orientation, BRIEF descriptor, Hamming matcher).
    * `common.py`: Kernel utilitas dasar (copy, channel merge/split, slice & accumulate tile, gradients Sobel/Scharr).
    * `bilateral_grid.py` & `joint_bilateral_guidance.py`: Kernel filter bilateral cepat menggunakan grid 3D.
    * `median_filter.py`, `box_filter.py`, `gaussian.py`, `pyramid.py` (downsample 2x), `fft.py` (FFT 2D & korelasi fase), `ncc.py` (Normalized Cross Correlation), `ransac.py` (estimasi homografi).
  * **`aot_py/`** (Skrip Compiler):
    * Berisi file `compile_*_tcm.py` (contoh: `compile_ofb_tcm.py`, `compile_remap_tcm.py`) untuk mengompilasi kernel Python menjadi format biner lintas platform `.tcm` (Vulkan, CUDA, CPU).
  * **`aot_tcm/`** (Biner Kompilasi):
    * Target folder penyimpanan file `.tcm` terkompilasi (misal `ofb_vulkan.tcm`, `remap_cuda.tcm`) yang akan dimuat langsung ke VRAM oleh engine C++.
* **`alignment/`** (Logika Penyelarasan / Registration):
  * `__init__.py`: Entrypoint modul penyearah gambar.
  * **`alignment_features/`** (Feature-based Alignment):
    * `alignment_core.py`: Kelas utama `FeatureAlignment` untuk menyelaraskan frame. Mendeteksi titik kunci, mencocokkan deskriptor (Lowe's ratio test), membuang outlier via RANSAC OpenCV, mengestimasi matriks Homography, dan menerapkan warping (CPU/GPU).
    * `taichi_bridge.py`: Kelas `TaichiAlignmentBridge` sebagai adaptor ke akselerasi GPU `taichi_aot` (misal memanggil `warp_affine` dan `ofb` GPU).
  * **`alignment_tile/`** (Block-based / Tile Alignment):
    * Algoritma penyelarasan sub-piksel tingkat tinggi berbasis tile (gaya Google HDR+). Memotong gambar menjadi ubin kecil dan mengevaluasi pergeseran spasial di berbagai tingkat piramida.
    * `compute_alignmentHDRplus.py`, `compute_flow.py`, `compute_flow_kernels.py`: Kontroler pencocokan tile di sisi Python.
    * `alignment_tile.cpp`, `refinement.cpp`, `cost_function.cpp` (beserta binding Python): Akselerasi C++ untuk pencarian sub-piksel cepat dan fungsi biaya (L1/L2 distance).
  * **Algoritma Pembanding (Fallback / Alternatif)**:
    * `ORB.py`, `AKAZE.py`, `Light_Glue.py` (LightGlue PyTorch), dan `Farneback_optical_flow.py` (dense flow OpenCV).

### 2. Alur Pemrosesan Gambar (Pipeline Stack)
Secara garis besar, alur pemrosesan stacking foto RAW / DNG berjalan sebagai berikut:
```
[DNG / RAW Images] 
       │
       ▼
[Hamilton Demosaicing] ──► Demosaic mentah ke RGB float (GPU Taichi)
       │
       ▼
[Feature Detection] ───► Deteksi keypoint (OFB / ORB) pada frame ref & comp
       │
       ▼
[Homography Estimation] ─► Hitung matriks transformasi affine M (OpenCV RANSAC)
       │
       ▼
[GPU WarpAffine] ──────► Selaraskan/geser frame comp ke frame ref (GPU Taichi)
       │
       ▼
[Image Stacking/Stack] ─► Gabungkan frame ter-align (Bilateral Grid / Denoise)
       │
       ▼
[Final Enhancement] ───► Post-process (Bilateral Filter, Sobel, dll) -> Save
```

---

## Daftar Isi
1. [Arsitektur Pemanggilan (Gambaran Umum)](#1-arsitektur-pemanggilan)
2. [Primitif engine.py yang Wajib Diketahui](#2-primitif-enginepy)
3. [Pola Dasar Fungsi di __init__.py](#3-pola-dasar-fungsi-di-__init__py)
4. [Penanganan Buffer Vector vs Scalar](#4-vector-vs-scalar)
5. [Manajemen VRAM: Alokasi, Release, Destroy](#5-manajemen-vram)
6. [Pipeline Recording (One Big Graph)](#6-pipeline-recording)
7. [Template: Menambah Algoritma Baru](#7-template-algoritma-baru)
8. [Template: Compile Script AOT Baru](#8-template-compile-script)
9. [Pitfall & Gotchas yang Harus Dihindari](#9-pitfall--gotchas)

---

## 1. Arsitektur Pemanggilan

```
Kode User / Pipeline
        │
        ▼
taichi_aot/__init__.py          ← Public API (satu-satunya pintu masuk)
        │  _mod("name").run(...)
        ▼
engine.py :: AOTModuleWrapper   ← Wrapper Python untuk modul TCM
        │  run_aot_graph(...)
        ▼
taichi_aot_engine.dll (C++)     ← Executor GPU nyata via Taichi C-API
        │
        ▼
GPU VRAM (Vulkan/CUDA/CPU)
```

**Aturan penting:**
- Kode eksternal **hanya** memanggil fungsi di `taichi_aot/__init__.py`.
- `engine.py` **tidak boleh diubah** tanpa persetujuan eksplisit. Ia adalah *single source of truth*.
- Semua fungsi baru ditambahkan **hanya** ke `__init__.py`.

---

## 2. Primitif engine.py yang Wajib Diketahui

### 2.1 InputArray — Unifikasi Data Masuk
```python
from .engine import InputArray

buf = InputArray(data)
```
- **Menerima**: `np.ndarray`, `TaichiGPUBuffer`, `torch.Tensor`, `list/tuple`, `int/float`
- Jika sudah `TaichiGPUBuffer`, dikembalikan apa adanya (zero-copy passthrough)
- **Gunakan ini** untuk setiap argumen masuk ke fungsi di `__init__.py`

### 2.2 OutputArray — Alokasi Buffer Keluaran
```python
from .engine import OutputArray

dst = OutputArray((h, w), dtype=np.float32)            # 2D grayscale
dst = OutputArray((h, w, 3), dtype=np.float32)         # 3D RGB
```
- Mengalokasikan buffer GPU kosong untuk ditulis oleh kernel
- **Gunakan ini** alih-alih `engine.allocate()` untuk output fungsi publik

### 2.3 engine.allocate() — Buffer Intermediate
```python
tmp = engine.allocate((h, w), dtype=np.float32)
tmp = engine.allocate((h, w, 3), dtype=np.float32, is_vector=True)
```
- Untuk buffer **sementara internal** (bukan input/output publik)
- Mendukung **buffer pool reuse** — lebih efisien dari malloc baru
- `host_accessible=True` jika perlu `.to_numpy()` langsung (tanpa staging)

### 2.4 engine.upload() — NumPy ke VRAM
```python
gpu_buf = engine.upload(numpy_array)
gpu_buf = engine.upload(numpy_array, is_vector=True, vector_dim=3)
```
- Upload NumPy ke VRAM dengan DMA fast-copy
- Otomatis deteksi 3D RGB → `is_vector=True, vector_dim=3`
- Otomatis deteksi Flow (H,W,2) → `is_vector=True, vector_dim=2`

### 2.5 engine.sync() — Flush GPU Command Queue
```python
engine.sync()
```
- Tunggu seluruh antrian perintah GPU selesai
- **Wajib dipanggil** sebelum `buf.release()` / `buf.destroy()` jika ada buffer intermediate
- Jangan terlalu sering — cukup satu kali di akhir fungsi publik

### 2.6 buf.to_numpy() — Baca Balik dari VRAM
```python
result = gpu_buf.to_numpy()   # → np.ndarray
```
- Otomatis gunakan staging buffer untuk VRAM-only buffers
- Tidak perlu manual staging buffer di kode publik

### 2.7 buf.release() vs buf.destroy()
```python
buf.release()   # Kembalikan ke buffer pool → CEPAT, bisa di-reuse
buf.destroy()   # Hapus VRAM seketika → Tidak bisa di-reuse
```
| | `release()` | `destroy()` |
|---|---|---|
| **Kecepatan** | O(1) — masuk pool | O(1) — bebas VRAM |
| **Reuse** | Ya, jika ukuran sama | Tidak |
| **Kapan pakai** | Buffer intermediate | Buffer yang tidak lagi dibutuhkan |

### 2.8 buf.view_as_vector() — Toggle Vector Mode
```python
buf_vec = buf.view_as_vector(True, vector_dim=3)   # baca sebagai RGB vec3
buf_scl = buf.view_as_vector(False)                 # baca sebagai scalar
```
- **Tidak menyalin data** — hanya mengubah metadata interpretasi
- Diperlukan ketika kernel mengharapkan tipe berbeda dari shape yang ada
- Lihat Bagian 4 untuk penjelasan lengkap

---

## 3. Pola Dasar Fungsi di __init__.py

### 3.1 Pola Minimal (Grayscale → Grayscale)
```python
def nama_fungsi(src, return_gpu=False, dst=None):
    """Deskripsi singkat."""
    src_buf = InputArray(src)              # Unifikasi input
    h, w = src_buf.shape[:2]

    if dst is None:
        dst_buf = OutputArray((h, w), dtype=src_buf.dtype)
    else:
        dst_buf = dst                      # Reuse pre-allocated buffer

    _mod("nama_modul").run(
        "nama_graph",
        src=src_buf,
        dst=dst_buf,
        h=int(h),
        w=int(w),
    )

    return dst_buf if return_gpu else dst_buf.to_numpy()
```

### 3.2 Pola dengan Buffer Intermediate
```python
def nama_fungsi(src, sigma=1.0, return_gpu=False):
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]

    tmp_buf = engine.allocate((h, w), dtype=np.float32)  # intermediate
    dst_buf = OutputArray((h, w), dtype=np.float32)

    _mod("modul").run("kernel_pass1", src=src_buf, dst=tmp_buf, h=h, w=w, sigma=sigma)
    _mod("modul").run("kernel_pass2", src=tmp_buf, dst=dst_buf, h=h, w=w)

    engine.sync()          # Pastikan semua perintah selesai
    tmp_buf.release()      # Kembalikan ke pool

    return dst_buf if return_gpu else dst_buf.to_numpy()
```

### 3.3 Pola dengan Pilihan Graph Dinamis (dtype / channel)
```python
def nama_fungsi(src, return_gpu=False):
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]
    is_3d = len(src_buf.shape) == 3
    is_vec = getattr(src_buf, "is_vector", False)

    dst_buf = OutputArray(src_buf.shape, dtype=src_buf.dtype, is_vector=is_3d)

    # Pilih graph berdasarkan tipe dan dimensi
    if is_vec:
        graph = "kernel_vec3_f32"
    elif is_3d:
        graph = "kernel_3ch_f32"
    elif src_buf.dtype == np.float32:
        graph = "kernel_1ch_f32"
    else:
        graph = "kernel_1ch_i32"

    _mod("modul").run(graph, src=src_buf, dst=dst_buf, h=h, w=w)
    return dst_buf if return_gpu else dst_buf.to_numpy()
```

### 3.4 Pola dengan Input yang Mungkin Sudah di GPU
```python
def nama_fungsi(src, return_gpu=False):
    # Pattern: terima GPU buffer atau NumPy, keduanya valid
    is_gpu = isinstance(src, TaichiGPUBuffer)
    src_buf = src if is_gpu else engine.upload(src)
    
    # ... proses ...
    
    # Cleanup jika kita yang upload
    if not is_gpu and hasattr(src_buf, "release"):
        src_buf.release()
    
    return dst_buf if return_gpu else dst_buf.to_numpy()
```

---

## 4. Vector vs Scalar

Ini adalah sumber bug paling umum. Taichi AOT membedakan dua tipe buffer 3D:

| | **Scalar 3D** | **Vector Field** |
|---|---|---|
| **Shape** | `(H, W, 3)` | `(H, W)` atau `(H, W, 3)` |
| **`is_vector`** | `False` | `True` |
| **Kernel mengharapkan** | 3 array terpisah | 1 field berisi vektor |
| **Contoh** | Gambar RGB `i32` | Flow field `vec2`, RGB `vec3` |
| **Nama graph** | `*_3ch_*` | `*_vec3_*` |

### Aturan Praktis:
```python
# 1. Jika src adalah RGB f32 (dari upload/hamilton) → biasanya is_vector=True
src_v = src_buf
if len(src_buf.shape) == 3 and not getattr(src_buf, "is_vector", False):
    src_v = src_buf.view_as_vector(True)   # toggle ke vector mode

# 2. Jika src adalah RGB i32 (gambar integer) → biasanya is_vector=False
# Gunakan graph *_3ch_i32* bukan *_vec3_i32*

# 3. Flow field → selalu vector, vector_dim=2
flow_v = flow_buf.view_as_vector(True, vector_dim=2)
```

---

## 5. Manajemen VRAM

### 5.1 Urutan yang Benar
```python
def fungsi_kompleks(src):
    src_buf = InputArray(src)
    tmp1 = engine.allocate(...)     # 1. Alokasi
    tmp2 = engine.allocate(...)
    dst_buf = OutputArray(...)

    _mod("m").run("k1", ...)        # 2. Jalankan kernel
    _mod("m").run("k2", ...)

    engine.sync()                   # 3. Tunggu GPU selesai
    tmp1.release()                  # 4. Release intermediate
    tmp2.release()

    # dst_buf diserahkan ke pemanggil atau di-to_numpy()
    result = dst_buf.to_numpy()
    dst_buf.release()               # 5. Release output jika sudah tidak perlu
    return result
```

### 5.2 Pola return_gpu (Efisien untuk Chaining)
```python
def fungsi_a(src, return_gpu=False):
    # ...
    return dst_buf if return_gpu else dst_buf.to_numpy()

# Penggunaan efisien (tanpa transfer GPU-CPU di tengah):
gpu_a = fungsi_a(input_np, return_gpu=True)
gpu_b = fungsi_b(gpu_a, return_gpu=True)   # tidak perlu to_numpy() dulu!
result = fungsi_c(gpu_b).to_numpy()

# Cleanup manual jika return_gpu=True
gpu_a.release()
gpu_b.release()
```

### 5.3 Jangan Lupa Release di Finally
```python
tmp = None
try:
    tmp = engine.allocate(...)
    # ... proses ...
finally:
    if tmp is not None:
        engine.sync()
        tmp.release()
```

---

## 6. Pipeline Recording (One Big Graph)

Digunakan untuk **loop yang sama diulang berkali-kali** (contoh: tiling, multi-frame stack).
Menghilangkan overhead dispatch Python-to-C++ di setiap iterasi.

### 6.1 Recording
```python
# Buat placeholders (alias untuk buffer yang akan diganti tiap iterasi)
ph_src = engine.placeholder((tile_h, tile_w), dtype=np.float32)
ph_dst = engine.placeholder((tile_h, tile_w), dtype=np.float32)

# Record sekali
with engine.rec_pipeline("nama_pipeline"):
    _mod("gaussian").run("gaussian_blur_x_1ch_f32",
        src=ph_src, dst=ph_dst, h=tile_h, w=tile_w, weights=weights_buf, radius=3
    )
    _mod("gaussian").run("gaussian_blur_y_1ch_f32",
        src=ph_dst, dst=ph_src, h=tile_h, w=tile_w, weights=weights_buf, radius=3
    )
```

### 6.2 Eksekusi Per Frame (dengan Buffer Nyata)
```python
for frame_buf in frame_list:
    engine.use_pipeline("nama_pipeline", overrides={
        ph_src: frame_buf,   # Ganti placeholder → buffer nyata
        ph_dst: tmp_buf,
    })

engine.sync()  # Satu sync di akhir semua frame
```

### 6.3 Aturan Pipeline
- Buffer yang masuk pipeline otomatis `is_pipeline_intermediate = True` → tidak bisa di-release selama recording aktif
- Jika salah satu buffer pipeline dihapus (destroy/release), pipeline **otomatis diinvalidasi**
- Gunakan `engine.clear_pipeline_by_name("nama")` untuk reset manual

---

## 7. Template: Menambah Algoritma Baru

### Langkah 1: Buat kernel di `taichi_algorithm/nama_algo.py`
```python
import taichi as ti

@ti.kernel
def nama_kernel(src: ti.types.ndarray(ti.f32, ndim=2),
                dst: ti.types.ndarray(ti.f32, ndim=2),
                h: int, w: int):
    for y, x in ti.ndrange(h, w):
        # ... logika kernel ...
        dst[y, x] = src[y, x]
```

### Langkah 2: Buat compile script di `aot_py/compile_nama_tcm.py`
Lihat Bagian 8 untuk template lengkap.

### Langkah 3: Jalankan kompilasi
```bash
cd "e:\APP Developer\Pixel Refine"
python pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/compile_nama_tcm.py
```

### Langkah 4: Tambahkan fungsi ke `taichi_aot/__init__.py`
```python
def nama_fungsi(src, param1=1.0, return_gpu=False, dst=None):
    """Deskripsi: apa yang dilakukan fungsi ini."""
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]

    if dst is None:
        dst_buf = OutputArray((h, w), dtype=src_buf.dtype)
    else:
        dst_buf = dst

    _mod("nama_algo").run(
        "nama_graph",       # nama graph yang dikompilasi di compile script
        src=src_buf,
        dst=dst_buf,
        h=int(h),
        w=int(w),
        param1=float(param1),
    )

    return dst_buf if return_gpu else dst_buf.to_numpy()


# Jika perlu alias
nama_alias = nama_fungsi
```

---

## 8. Template: Compile Script AOT Baru

```python
# compile_nama_tcm.py
import os
os.environ["AOT_MODE"] = "0"   # Matikan AOT worker saat kompilasi

import taichi as ti
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.nama_algo import (
    nama_kernel_1,
    nama_kernel_2,
)


def compile_tcm(arch=ti.vulkan, save_path="nama_vulkan.tcm"):
    print(f"\n>>> Compiling NamaAlgo AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # ─── Graph: operasi utama ───────────────────────────────────────────────
    g = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    h_arg   = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "h",   ti.i32)
    w_arg   = ti.graph.Arg(ti.graph.ArgKind.SCALAR,  "w",   ti.i32)

    g.dispatch(nama_kernel_1, src_arg, dst_arg, h_arg, w_arg)
    module.add_graph("nama_graph", g.compile())

    module.archive(save_path)
    print(f"Saved: {save_path}")
    ti.reset()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(assets_dir, exist_ok=True)

    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda,   "cuda"),
        (ti.cpu,    "cpu"),
    ]
    for arch, suffix in archs:
        path = os.path.join(assets_dir, f"nama_{suffix}.tcm")
        try:
            compile_tcm(arch=arch, save_path=path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
```

### Tipe Arg yang Didukung

| Python type | Taichi AOT Arg | Catatan |
|---|---|---|
| `float` | `ti.graph.ArgKind.SCALAR, ti.f32` | |
| `int` | `ti.graph.ArgKind.SCALAR, ti.i32` | |
| `np.float32 ndarray 2D` | `ti.graph.ArgKind.NDARRAY, ti.f32, ndim=2` | Grayscale |
| `np.float32 ndarray 3D` | `ti.graph.ArgKind.NDARRAY, ti.f32, ndim=2` + vector field | RGB vec3 |
| `np.int32 ndarray 2D` | `ti.graph.ArgKind.NDARRAY, ti.i32, ndim=2` | Integer buffer |

> [!IMPORTANT]
> **NDARRAY RGB/vektor**: Meskipun shape Python adalah `(H, W, 3)`, definisi AOT menggunakan `ndim=2` karena dimensi vektor (3) **bukan** dimensi spasial dalam Taichi — ia adalah `field_dim`. Kesalahan ini menyebabkan `shape mismatch` saat runtime.

---

## 9. Pitfall & Gotchas yang Harus Dihindari

### ❌ 1. Nested `ti.static` berlebihan → Compile hang
```python
# JANGAN:
for i in ti.static(range(16)):
    for j in ti.static(range(9)):   # 16×9=144 iterasi → LLVM hang
        ...

# AMAN:
for i in ti.static(range(16)):      # max ~32 iterasi
    ...
```

### ❌ 2. Popcount i32 Arithmetic Shift Bug
```python
# JANGAN (salah untuk nilai negatif i32):
c = xor_val - ((xor_val >> 1) & 0x55555555)   # >> adalah arithmetic shift!

# BENAR (isolasi sign bit dulu):
sign_bit = (xor_val >> 31) & 1
c = ti.i32(xor_val & 0x7FFFFFFF)
c = c - ((c >> 1) & 0x55555555)   # sekarang c selalu positif
dist += int(c & 0x3F) + sign_bit
```

### ❌ 3. ti.u32 tidak aman di Vulkan AOT
```python
# JANGAN:
xor_val = ti.u32(a) ^ ti.u32(b)   # ti.u32 bisa crash di Vulkan runtime

# GUNAKAN:
xor_val = ti.i32(a ^ b)            # XOR i32 bitwise identik
```

### ❌ 4. release() buffer yang masih dalam pipeline
```python
# JANGAN — akan menyebabkan use-after-free:
with engine.rec_pipeline("pipe"):
    _mod("m").run("k", buf=tmp)
tmp.release()   # ← tmp masih dipakai pipeline!

# BENAR — biarkan pipeline yang mengurus lifetime tmp
# tmp akan otomatis di-destroy ketika pipeline diinvalidasi
```

### ❌ 5. UnicodeEncodeError di Windows
```python
# JANGAN gunakan karakter non-ASCII di print() terminal Windows:
print(f"→ Result: {n}")   # '→' crash di cp1252

# GUNAKAN:
print(f"-> Result: {n}")

# ATAU jalankan dengan:
# python -X utf8 script.py
```

### ❌ 6. Lupa `engine.sync()` sebelum release intermediate
```python
# JANGAN:
_mod("m").run("k", src=a, tmp=tmp, dst=b)
tmp.release()   # GPU mungkin belum selesai pakai tmp!

# BENAR:
_mod("m").run("k", src=a, tmp=tmp, dst=b)
engine.sync()
tmp.release()
```

### ❌ 8. Buffer Overread saat Casting Float ke uint64 (Engine Bridge)
```python
# JANGAN (menyebabkan stack overread 4-byte tambahan karena ctypes casting paksa):
arg.val_u64 = ctypes.cast(ctypes.pointer(ctypes.c_float(float(value))), ctypes.POINTER(ctypes.c_uint64)).contents.value

# BENAR (konversi bit pattern 32-bit float secara aman menggunakan struct.pack/unpack):
import struct
arg.val_u64 = struct.unpack('<I', struct.pack('<f', float(value)))[0]
```

---

## Referensi Cepat

### Modul TCM yang Tersedia
| Nama (`_mod("...")`) | Isi |
|---|---|
| `common` | copy, rgb2gray, merge/split, hanning, slice_tile, accumulate_tile |
| `gaussian` | gaussian_blur (X/Y pass, 1ch/3ch/vec3) |
| `bicubic` | bicubic resize |
| `bilinear` | bilinear resize |
| `area` | INTER_AREA resize |
| `box_filter` | box filter 3x3 dan generic |
| `median_filter` | median 3x3 |
| `pyramid` | downsample 2x |
| `fft` | FFT 2D, phase correlation |
| `hamilton` | Hamilton-Adams demosaicing (DNG) |
| `remap` | WarpAffine + Remap GPU |
| `ncc` | Normalized Cross Correlation |
| `gradients` | Sobel, Scharr, gradient magnitude |
| `bilateral_grid` | Bilateral grid filter |
| `jbf` | Joint Bilateral Filter |
| `ofb` | O-FAST-BRIEF feature matching & Vision Booster |
| `ransac` | RANSAC homography estimation |
| `preprocess` | Image preprocessing utilities |

### Tipe Data Mapping
| numpy dtype | Taichi AOT | Nama graph suffix |
|---|---|---|
| `np.float32` | `ti.f32` | `_f32` |
| `np.int32` | `ti.i32` | `_i32` |
| `np.uint8` | `ti.u8` | (jarang di kernel) |
| `np.uint16` | `ti.u16` | (jarang di kernel) |
