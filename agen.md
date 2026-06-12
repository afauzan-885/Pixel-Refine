# Pixel Refine - Development Knowledge Base (Agen)

> File ini menggantikan `gemini.md` sebagai knowledge base utama untuk AI coding agent.
> Berisi status proyek, arsitektur, constraint, dan catatan teknis yang kritis.

---

## 🛠 Project Status (Taichi AOT Pipeline)
- **Status**: Production Ready / Optimized
- **Architecture**: Smart C++ Pipeline (One Big Graph) - **Implemented**
- **Algorithm Coverage**: 100% (19 core algorithms migrated to AOT — termasuk WarpAffine & OFB)
- **Multi-Backend**: Supported (Vulkan, CUDA, CPU)
- **Accuracy**: Verified against OpenCV (MAE within safe thresholds)

## 📊 Latest Performance Benchmarks (9.1 MP - 3016x3016)
*Measured on Chained Operations (Resize + Blur + Median + Bilateral Grid + Sobel)*
- **Smart Pipeline (Grayscale)**: **~17.72 ms** per frame (**56.42 FPS**).
- **Universal Interop Bridge (Fast-Copy)**: **~61.03 ms** for 34MB (9.1 MP) transfer (DMA-based).
- **Smart Image IO (imread)**: **~149 ms** (vs OpenCV ~208 ms) -> **+28% Faster**.
- **Smart Image IO (imwrite)**: Bit-perfect accuracy verified.

> [!NOTE]
> Chained operations using `rec_pipeline` and `run_pipeline` eliminate Python-to-C++ dispatch overhead. The Universal Bridge enables zero-copy-like transfers between Taichi, PyTorch, and ONNX.

---

## 🧱 Technical Constraints & Architecture
- **Smart Overrides**: Identity-based (Memory Handle) swapping using `Placeholder` objects.
- **One Big Graph**: Entire processing chains are recorded once and executed at native C++ speed.
- **Data Type**: 16-bit images are represented in `i32` for AOT precision/safety.
- **Buffer Management**: Managed via `AOTEngine` dan `BufferPool` untuk menjaga footprint memori ~1GB.
- **Universal GPU Bridge**: Cross-vendor (Nvidia/AMD/Intel) DMA transfer via Pinned-Memory Fast-Copy Bridge.
- **Anti-Crash Design**: Explicit synchronization (`rt->wait()`) dan automatic staging-read untuk buffer VRAM-only.
- **Smart Image IO**: Direct C++ decoding to VRAM (imread/imwrite) menggunakan Windows Imaging Component (WIC).
- **Single Source of Truth (`engine.py`)**: `engine.py` adalah jembatan backend C++ yang bersifat *single source of truth*. Logika dan perilakunya tidak boleh diubah kecuali atas instruksi/keputusan eksplisit dari user. Semua algoritma baru atau modifikasi yang menggunakan backend ini harus mematuhi aturan dan perilaku yang ditetapkan oleh `engine.py`.
- **UI Style Consistency (GenericUILibrary & Animations)**:
  - **GenericUILibrary**: Semua pembuatan atau pengeditan komponen antarmuka pengguna (UI) wajib menggunakan pustaka/framework di path `pixel_refine_desktop/ui/resources/GenericUILibrary` (seperti `Card`, `Button`, `FormGroup`, `ListGroup`, dll.) untuk memastikan keselarasan penuh terhadap sistem tema, tipografi, dan gaya yang telah ditentukan. Jangan membuat styles kustom ad-hoc secara manual.
  - **Animations**: Jika menambahkan desain UI yang memiliki animasi, wajib menggunakan pustaka/library yang ada di dalam path `pixel_refine_desktop/ui/resources/animations`.
  - **Custom UI Component**: Jika ingin membuat UI baru yang bersifat kustom, sebisa mungkin tambahkan komponen tersebut ke dalam skrip yang ada di dalam path `pixel_refine_desktop/ui/resources/GenericUILibrary` daripada membuat berkas/skrip baru.

> [!IMPORTANT]
> **i32 Popcount Bug (Vulkan/AOT):** Algoritma parallel popcount (`0x55555555` trick) hanya benar pada **unsigned** integer. Pada `ti.i32`, operator `>>` adalah **arithmetic shift** (propagasi sign bit). Untuk nilai i32 dengan bit-31 aktif, popcount AKAN SALAH. **Fix wajib**: isolasi bit-31 terpisah sebelum menerapkan bit-trick pada 31 bit bawah.
> ```python
> sign_bit = (xor_val >> 31) & 1
> c = ti.i32(xor_val & 0x7FFFFFFF)  # clear MSB -> selalu positif
> c = c - ((c >> 1) & 0x55555555)   # sekarang benar
> dist += int(c & 0x3F) + sign_bit
> ```

---

## 🚀 Roadmap & Status Implementasi
1. **Bilateral Grid Integration**: **Implemented**
2. **High-Performance Image IO**: **Implemented** (8/16-bit support via WIC)
3. **Universal GPU Interop Bridge**: **Implemented & Verified** (50x Stress-Test Passed)
4. **Smart Data Transformation**: **Implemented** (`gpu_buffer.cast` via C++ Backend)
5. **GPU WarpAffine (Taichi AOT)**: **Implemented & Verified** (bit-perfect parity dengan OpenCV)
6. **O-FAST-BRIEF (OFB) GPU Feature Matcher**: **Implemented & Verified** (75 matches, 100% RANSAC inliers)
7. **Mobile Optimization**: Validate TCM modules on mobile backends.

---

## 📂 Key Files

### Core Backend
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py`: Primary AOT runtime bridge (Pipeline & IO support).
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/taichi_aot_engine.cpp`: C++ Backend Orchestrator (DLL).
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/__init__.py`: **Public API** - semua fungsi taichi_aot dipanggil dari sini.

### Kernel Taichi (JIT Source)
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/remap.py`: Kernel WarpAffine + Remap.
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/ofb.py`: Kernel OFB (FAST detector, NMS, BRIEF descriptor, Hamming matcher).
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/common.py`: Kernel umum (resize, blur, sobel, dll).

### Compile Scripts (AOT)
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/compile_remap_tcm.py`: Kompilasi WarpAffine + Remap ke `.tcm`.
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/compile_ofb_tcm.py`: Kompilasi OFB ke `.tcm` (Vulkan + CUDA).

### Test Files
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/test_comprehensif.py`: Master test suite.
- `test_algorithm/IMG_20250401_182043_B003.png`: Standard test image for high-res benchmarks.

---

## 📘 Deep Dive: Taichi AOT Architecture & Execution Stack

### 1. Proses Kompilasi (Compile-Time)
* **Penyusun Graf (`compile_*_tcm.py`)**:
  * Mengimpor kernel Taichi dari kode JIT (misalnya `gaussian.py`).
  * Menggunakan `ti.aot.Module(arch)` untuk menginisialisasi modul AOT untuk arsitektur target (`vulkan`, `cuda`, atau `cpu`).
  * Mendefinisikan signature input secara eksplisit menggunakan `ti.graph.Arg` (`SCALAR` untuk primitif, `NDARRAY` dengan `ndim` tertentu untuk array).
  * Menyusun graf menggunakan `ti.graph.GraphBuilder()`, menambahkan kernel via `dispatch()`, lalu mengarsipkan ke `.tcm` via `module.archive(save_path)`.

### 2. C++ Generic AOT Engine (`taichi_aot_engine.cpp` -> `taichi_aot_engine.dll`)
* **Core Bridge**: Menggunakan **Taichi C-API** untuk memuat modul AOT secara langsung di VRAM dengan format biner `.tcm`.
* **Caching Pintar**: `graph_cache` berbasis `std::unordered_map` menghindari pencarian grafik berulang saat real-time.
* **Smart Image IO (WIC)**: Membaca (`ti_imread_to_gpu`) dan menulis (`ti_imwrite_from_gpu`) gambar langsung ke VRAM tanpa konversi NumPy, mendukung 8-bit dan 16-bit.
* **Recording Pipeline**: `add_to_pipeline` + `run_pipeline` mengeksekusi rantai grafik dalam satu siklus tunggal dengan placeholder swap.

### 3. Python ctypes Bridge (`engine.py`)
* **`TaichiGPUBuffer`**: Abstraksi Python untuk handle `TiMemory` C++. Mendukung `.to_numpy()`, `.destroy()`, dan `.cast()`.
* **OpenCV Hybrid Diagnostics**: Validasi ketat input (tipe data, bentuk, dimensi) sebelum dikirim ke C-API.
* **Single Source of Truth**: Tidak boleh dimodifikasi tanpa persetujuan eksplisit.

### 4. Manajemen Thread GUI & AOT (`taichi_worker.py`)
* **GUI Stability**: Pemanggilan Taichi JIT dilokalisasi dalam thread tunggal `AutomatedTaichiWorker`.
* **AOT Bypass**: Ketika `_IS_AOT_MODE` aktif, pemanggilan grafik dieksekusi langsung (tanpa thread worker).

### 5. Backup Formulasi Non-Linear (Hamilton - Sebelum Migrasi Linear)
*Catatan: Dipertahankan sebagai cadangan setelah migrasi ke pipeline Linear Demosaicing.*
* **Color Matrix Transform (Camera-to-sRGB):** $sR = C_{00} R + C_{01} G + C_{02} B$, dst.
* **Dynamic Algebraic Sigmoid Tone Mapping:** $f(x) = x / \sqrt{1 + x^2}$
* **Gamma Correction:** $\text{Output} = \text{clamp}(sRGB)^{1/2.22}$

---

## 🆕 Algoritma Baru: GPU WarpAffine (Taichi AOT)

**Modul**: `remap.py` → `compile_remap_tcm.py` → `remap_{backend}.tcm`

**API Publik** (`taichi_aot/__init__.py`):
```python
result = taichi_aot.warp_affine(src, M, dsize, flags=cv2.INTER_LINEAR, border_mode=cv2.BORDER_REFLECT_101)
```

**Spesifikasi Teknis:**
- Kernel mengimplementasikan inverse mapping: untuk setiap piksel output, hitung koordinat di input via `M_inv @ [x, y, 1]`
- Interpolasi bilinear dengan `BORDER_REFLECT_101` (default OpenCV)
- Mendukung grayscale (2D) dan RGB (3D)
- **Parity**: Bit-perfect match dengan `cv2.warpAffine` (MAE < 0.5/255)
- **Backend**: Vulkan, CUDA, CPU

**Catatan Implementasi:**
- Matriks affine M disediakan sebagai (2×3) → di-inverse secara Python sebelum dikirim ke kernel
- Kernel menyimpan M_inv sebagai 6 scalar NDARRAY 1D untuk AOT compatibility

---

## 🆕 Algoritma Baru: O-FAST-BRIEF (OFB) GPU Feature Matcher & Vision Booster

**Nama resmi**: O-FAST-BRIEF | **Alias**: OFB
**Modul**: `ofb.py` → `compile_ofb_tcm.py` → `ofb_{backend}.tcm`

**API Publik** (`taichi_aot/__init__.py`):
```python
# Mode standar (mencocokkan seluruh gambar):
pts_ref, pts_comp = taichi_aot.ofb(img_ref, img_comp, max_kps=1500, threshold=4.0, margin=32)

# Mode terpisah (memisahkan langit/bintang dan landscape untuk astro-landscape):
sky_ref, sky_comp, land_ref, land_comp = taichi_aot.ofb(img_ref, img_comp, threshold=4.0, return_split=True)
```

**Komponen Algoritma & Fitur Tangguh:**

| Komponen | Implementasi | Catatan |
|---|---|---|
| **Keypoint Detector** | FAST-9 (Bresenham circle 16px) | SAD score untuk NMS |
| **Vision Booster** | Local Contrast Normalization di GPU | Meregangkan kontras pada detail redup (bintang gelap/siluet gunung) berdasarkan noise floor (`local_contrast > 0.003`) tanpa mengubah gambar asli. |
| **Star/Feature Filter** | Unboosted score thresholding | FAST-9 mendeteksi dengan kontras ter-boost, namun akumulasi skor keypoint tetap menggunakan selisih intensitas asli (*unboosted*). Ini membedakan bintang nyata dari derau sensor ber-skor rendah. |
| **Margin Sensor** | Batas tepi sensor | Parameter `margin` (default 32px) mengabaikan tepi sensor agar keypoint tidak tersumbat oleh derau sensor terluar. |
| **Matcher** | Bidirectional Cross-Check | Pencocokan dua arah (forward/backward) untuk membuang pencocokan ganda (*many-to-one*). |
| **Astro Fallback** | Spatiotemporal Geometric Matcher | Jika pencocokan deskriptor BRIEF menghasilkan `< 30` pasang titik (karena patch bintang didominasi oleh langit gelap tanpa tekstur), otomatis fallback ke *Nearest-Neighbor* dalam radius 50px. |
| **Dual-RANSAC Split** | Horizon/Motion clustering | Membagi inliers menjadi dua kelompok gerakan terpisah: **Landscape** (tripod: dx=0, dy=0) dan **Sky/Stars** (drift akibat rotasi bumi). |

**Bug Kritis & Engine Fixes:**
* **Float Scalar Overread Fix (`engine.py`)**: Memperbaiki bug casting ctypes float 4-byte ke uint64 8-byte yang menyebabkan pembacaan derau memori (*stack garbage*), merusak parameter float seperti `threshold` dan `ratio_threshold` di GPU. Menggunakan `struct.pack/unpack` untuk konversi bit pattern 32-bit yang aman.
* **i32 Popcount Bug (Vulkan/AOT)**: Lihat constraint `i32 Popcount Bug` di bagian atas.
* FAST score: Gunakan SAD sederhana (bukan nested `ti.static` 16×9 — menyebabkan compile hang).

**Hasil Verifikasi (Tripod Night Burst):**
* **Landscape Matches (dx=0.0, dy=0.0)**: **415 Matches**
* **Sky/Star Matches (dx=+8.0, dy=+15.0)**: **14 Matches**
* **TCM yang dikompilasi**: `ofb_vulkan.tcm` (~103 KB) & `ofb_cuda.tcm` (~255 KB) dengan dukungan parameter `margin` dan `threshold`.

---

## 🐛 Known Bugs & Gotchas

| Bug | Penyebab | Fix |
|---|---|---|
| **Popcount salah di GPU** | `ti.i32 >>` adalah arithmetic shift (sign extend) | Isolasi bit-31 sebelum bit-trick popcount |
| **Compile hang (AOT)** | `ti.static(range(16)) × ti.static(range(9))` = 144 iterasi unrolled | Hindari nested `ti.static` lebih dari ~32 iterasi total |
| **UnicodeEncodeError** | Windows terminal default cp1252, bukan UTF-8 | Jalankan dengan `python -X utf8` atau hindari char non-ASCII di print |
| **cv2.imshow dari background task** | Task runner tidak punya display context | Gunakan `os.startfile()` atau simpan ke file saja |
| **FAST detector terlalu restriktif** | Early-exit `count < 3` terlalu ketat | Ubah ke `count < 2` |

---

## 📋 Cara Penggunaan API Utama

### Hamilton Demosaicing (DNG)
```python
import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot

# Dari file path langsung (metadata diekstrak otomatis)
bgr_u16 = taichi_aot.demosaic("path/to/image.dng", method="hamilton", output_bgr_u16=True)
bgr_u8  = (bgr_u16 >> 8).astype(np.uint8)
```

### WarpAffine GPU
```python
M = cv2.getRotationMatrix2D(center, angle_deg, scale)
warped = taichi_aot.warp_affine(src_img, M, dsize=(w, h))
```

### O-FAST-BRIEF (OFB) Feature Matching
```python
pts_ref, pts_comp = taichi_aot.ofb(img_ref, img_comp, max_kps=2000, threshold=0.08)
H, inliers = cv2.findHomography(pts_ref, pts_comp, cv2.RANSAC, 5.0)
```
