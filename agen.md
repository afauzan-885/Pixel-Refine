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
  - **GenericUILibrary**: Semua pembuatan atau pengeditan komponen antarmuka pengguna (UI) wajib menggunakan pustaka/framework di path `resources/GenericUILibrary` (seperti `Card`, `Button`, `FormGroup`, `ListGroup`, dll.) untuk memastikan keselarasan penuh terhadap sistem tema, tipografi, dan gaya yang telah ditentukan. Jangan membuat styles kustom ad-hoc secara manual.
  - **Animations**: Jika menambahkan desain UI yang memiliki animasi, wajib menggunakan pustaka/library yang ada di dalam path `resources/animations`.
  - **Custom UI Component**: Jika ingin membuat UI baru yang bersifat kustom, sebisa mungkin tambahkan komponen tersebut ke dalam skrip yang ada di dalam path `resources/GenericUILibrary` daripada membuat berkas/skrip baru.
  - **Real-time Setting & Translation Broadcast**: Daftarkan parent container utama (seperti `EnhanceStackView`) menggunakan `@live_update` (atau kustom metode seperti `@live_update("retranslate_ui")`). Pemanggilan pemicu secara otomatis melakukan *cascade* pembaruan secara rekursif ke seluruh widget anak di bawahnya yang mengimplementasikan metode pembaruan tersebut. Pengembang tidak perlu mendekorasi sub-widget secara manual.
    - **Language Configuration Race Bypass**: Gunakan `language_config.reload_language(lang_str)` secara langsung dengan melewatkan string bahasa baru (misalnya "Indonesian") sebelum memanggil `retranslate_ui` atau menyebarkan pembaruan global. Ini mencegah bug race condition I/O berkas pada disk.
    - **Dynamic Child retranslate_ui**: Untuk container dinamis seperti `BulkPageLayout` yang menampung daftar widget anak independen (seperti `CombinedPanel`), override `retranslate_ui()` untuk mengulang secara eksplisit dan memanggil `retranslate_ui()` pada daftar panel aktif (`self.active_batch_panels.values()`).
    - **Compact Sizing on Action Buttons**: Tombol aksi batch (`Buat Batch Baru`, `Hapus Batch`, `Proses Semua Batch`) wajib disusutkan ukurannya sebesar 50% dengan mengatur tinggi tetap menjadi `22px` dan padding `2px 4px` dengan ukuran font `8pt` di kedua tema gelap/terang.
    - **Style consistency in update_theme**: Di dalam metode `update_theme`, gunakan `create_button_style(variant, theme)` untuk menerapkan style warna latar belakang, teks, dan border yang harmonis untuk tombol-tombol bertema.
  - **Absolute Centering Layout Rule**: Layout header utama wajib menggunakan pembagian 3 sub-layout (kiri, tengah, kanan) dengan stretch factor `(1, 1, 1)` untuk menjaga visual tombol mode absolut berada di tengah secara konsisten di semua dimensi layar.
  - **Dynamic Mode Buttons**: Lebih menyukai tombol status dinamis kustom berbasis QPushButton dengan transisi animasi opacity fade daripada ToggleSwitch biasa untuk transisi mode yang premium.
  - **Lazy & Eager Loading Strategy**: Untuk meminimalkan visual freeze saat memuat komponen/grid dengan data besar (misalnya banyak batch di Bulk Mode), implementasikan **eager incremental loading** (memuat batch secara bertahap, e.g., 10 batch terlebih dahulu) dikombinasikan dengan `SkeletonLoader` sebagai visual placeholder sebelum data sebenarnya ter-render sepenuhnya.
  - **Adaptive Empty State & Panel Visibility**: Saat dataset kosong (misal tidak ada batch sama sekali di DB):
    - Sembunyikan panel kontrol kanan (`right_panel`) secara mulus menggunakan animasi fade-out (`QGraphicsOpacityEffect`) dan set lebar maksimum ke 0 untuk mencegah ruang kosong tidak terpakai.
    - Sembunyikan tombol aksi global yang tidak dapat digunakan secara visual (menggunakan `QGraphicsOpacityEffect` ber-opacity `0.0`) agar posisi tombol layout lain/toggle di sekitarnya tetap presisi dan tidak bergeser secara tidak konsisten.
    - Sediakan tombol shortcut kondisional (e.g. "New Batch") di header area utama yang hanya muncul ketika workspace berada dalam kondisi kosong.

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

## 🆕 Algoritma Baru: GPU WarpPerspective & WarpAffine (Taichi AOT)

**Modul**: `remap.py` → `compile_remap_tcm.py` → `remap_{backend}.tcm`

**API Publik** (`taichi_aot/__init__.py`):
```python
# Warp Affine (2x3 Matrix)
result = taichi_aot.warp_affine(src, M, dsize, flags=cv2.INTER_LINEAR, border_mode=cv2.BORDER_REFLECT_101)

# Warp Perspective (3x3 Matrix)
result = taichi_aot.warp_perspective(src, H, dsize, return_gpu=False)
```

**Spesifikasi Teknis:**
- Kernel `_warp_perspective_kernel` & `_warp_perspective_kernel_vec3` mengimplementasikan proyeksi homogen inverse mapping: `u = H_inv @ [x, y, 1]` secara *on-the-fly* di GPU.
- Menghilangkan overhead pembuatan koordinat map spasial 12MP di CPU, sehingga zero-alloc/hemat memori.
- Interpolasi bilinear dengan `BORDER_REFLECT_101` (default OpenCV) atau Clamp.
- Mendukung gambar Grayscale (2D) dan RGB/BGR Multi-channel (3D).
- **Parity**: Geometris bit-perfect dengan `cv2.warpPerspective` dan `cv2.warpAffine`.

---

## 🆕 Algoritma Baru: GPU MAGSAC++ Homography Solver & Consensus

**Modul**: `ransac.py` → `compile_ransac_tcm.py` → `ransac_{backend}.tcm`

**API Publik** (`taichi_aot/__init__.py`):
```python
H, mask = taichi_aot.find_homography(pts1, pts2, method="MAGSAC++", ransacReprojThreshold=3.0, n_hypotheses=1024, return_gpu=False)
```

**Spesifikasi Teknis:**
- **Tukey's Biweight Soft Scoring**: Menilai kualitas hipotesis menggunakan pembobotan kontinu $(1 - err^2/\theta^2)^2$ untuk inlier yang dekat dengan model, mengeliminasi threshold kaku RANSAC standar.
- **Weighted Least Squares (WLS) Refinement**: Optimasi persamaan normal $A^T W A h = A^T W b$ secara langsung di GPU.
- **Zero-Copy VRAM (`return_gpu=True`)**: Menerima input `TaichiGPUBuffer` koordinat dan mengembalikan mask inlier dalam bentuk GPU buffer langsung di VRAM.
- **Hasil Validasi**: Menghasilkan **897 inliers** (vs OpenCV 896) dengan reproj error **1.095 px** (vs OpenCV 1.109 px).

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

| **Keypoint Detector** | FAST-9 dengan **Sub-pixel Refinement** (paraboloid fitting 3x3 score map) | Menghasilkan sub-pixel coordinates berakurasi tinggi dengan 2D quadratic interpolation. |
| **Scale Invariance** | Multi-Scale Image Pyramid (L0, L1, L2) | Mendeteksi keypoints pada berbagai skala level citra secara dinamis (misal, 3 skala untuk resolusi normal, adaptif 2 atau 1 skala untuk resolusi sangat rendah di bawah 240px). |
| **Rotation Invariance** | Intensity Centroid Angle Alignment | Menghitung sudut orientasi centroid intensitas lokal melalui `compute_centroid_angle` untuk memutar BRIEF sampling pattern secara dinamis sebelum pencocokan deskriptor. |
| **ANMS** | Grid-based Adaptive Non-Maximal Suppression | Mendistribusikan keypoints secara homogen ke seluruh area gambar, menghindari penumpukan keypoint pada satu cluster tekstur tinggi. |
| **Vision Booster & Filter** | Local Contrast Normalization di GPU & Unboosted Score | Meregangkan kontras pada detail redup (bintang gelap/siluet gunung) berdasarkan noise floor (`local_contrast > 0.003`) tanpa mengubah gambar asli. Filter membedakan bintang nyata dari derau sensor menggunakan *unboosted* FAST score. |
| **Median & Blur Pre-pass** | Fused GPU Filter Stack | Integrasi Median Filter untuk menyapu hot pixels sebelum deteksi keypoints, dipadukan dengan Gaussian Blur (sigma=2.0) pada citra deskriptor untuk meredam noise berfrekuensi tinggi. |
| **Margin Sensor** | Batas tepi sensor adaptif | Parameter `margin` yang terskala secara adaptif tiap level pyramid untuk mengabaikan noise di tepi sensor. |
| **Matcher** | Bidirectional Cross-Check | Pencocokan dua arah (forward/backward) untuk membuang pencocokan ganda (*many-to-one*). |
| **Astro Fallback** | Spatiotemporal Geometric Matcher | Jika pencocokan deskriptor BRIEF menghasilkan `< 30` pasang titik (karena patch bintang didominasi oleh langit gelap tanpa tekstur), otomatis fallback ke *Nearest-Neighbor* dalam radius 50px. |
| **Dual-RANSAC Split** | Horizon/Motion clustering | Membagi inliers menjadi dua kelompok gerakan terpisah: **Landscape** (tripod: dx=0, dy=0) dan **Sky/Stars** (drift akibat rotasi bumi). |

**Bug Kritis & Engine Fixes:**
* **Float Scalar Overread Fix (`engine.py`)**: Memperbaiki bug casting ctypes float 4-byte ke uint64 8-byte yang menyebabkan pembacaan derau memori (*stack garbage*), merusak parameter float seperti `threshold` dan `ratio_threshold` di GPU. Menggunakan `struct.pack/unpack` untuk konversi bit pattern 32-bit yang aman.
* **i32 Popcount Bug (Vulkan/AOT)**: Lihat constraint `i32 Popcount Bug` di bagian atas.
* FAST score: Gunakan SAD sederhana (bukan nested `ti.static` 16×9 — menyebabkan compile hang).

**Hasil Verifikasi (Tripod Night & Low-Res Align):**
* **Landscape Matches (dx=0.0, dy=0.0)**: **415 Matches**
* **Low-Res Alignment (< 240px)**: Teruji sukses pada 180x120px dengan akurasi sub-pixel dan visual alignment sangat presisi.
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

### A-KAZE (Accelerated KAZE) Feature Matching
```python
pts_ref, pts_comp, scores = taichi_aot.akaze(img_ref, img_comp, threshold=0.008, k_contrast=0.02)
H, inliers = cv2.findHomography(pts_ref, pts_comp, cv2.RANSAC, 5.0)
```

---

## 🆕 Algoritma Baru: A-KAZE GPU Feature Matcher (Superior Quality)

**Nama resmi**: A-KAZE | **Alias**: AKAZE
**Modul**: `akaze.py` → `compile_akaze_tcm.py` → `akaze_{backend}.tcm`

**API Publik** (`taichi_aot/__init__.py`):
```python
pts_ref, pts_comp, scores = taichi_aot.akaze(img_ref, img_comp, ratio_threshold=0.8, grid_size=32, threshold=0.008, k_contrast=0.02)
```

**Spesifikasi Teknis:**
* **Non-Linear Scale Space (FED)**: Menggunakan Fast Explicit Diffusion (8 langkah FED per level piramida) untuk meredam noise sensor tinggi sembari mempertahankan detail tepi struktur medis/mikroskopik halus yang biasanya hilang pada Gaussian blur.
* **Hessian Determinant Detector**: Respon fitur dihitung berdasarkan determinan Hessian orde-dua untuk stabilitas struktural organik yang superior.
* **M-SURF Binary Descriptor**: Menggunakan deskriptor biner 256-bit berbasis tanggapan wavelet Haar yang dirotasikan terhadap sudut centroid lokal untuk pencocokan Hamming dua arah yang sangat tangguh.
* **GPU Packing (pack_matches)**: Seluruh koordinat keypoint dan matches dipaketkan langsung pada memori VRAM GPU, menghasilkan jeda sinkronisasi seminimal mungkin (hanya 1 pemanggilan `to_numpy()` per level piramida).
* **Paritas Kualitas**: Teruji memberikan rasio inlier RANSAC sebesar **13.64%** pada gambar medis terdegradasi parah, mengungguli OFB (**5.19%**) secara signifikan.

---

## 🚀 Fitur Paralel & Watchdog VRAM (Session 3)

### Fitur Saat Ini:
* **Multi-threaded Execute (`async_run`)**: Thread pool asinkron untuk submit shader Vulkan paralel tanpa UI freezing.
* **Thread-safe Resource Pool**: Penyekatan akses pointer memori CPU <-> GPU menggunakan `threading.RLock` dan pooling dinamis.
* **3-Layer Auto-Cleanup Guard**: Proteksi runtime dengan menangkap sinyal `SIGSEGV`/`SIGILL`/`SIGABRT`/`SIGFPE` dan monitoring watchdog daemon (2 detik heartbeat) untuk memaksa pelepasan VRAM di Windows.
  * **Stateful Smart VRAM Reclamation**: Ketika aplikasi idle (>10 detik), watchdog melakukan pembersihan VRAM pintar (buffer pool, staging, GC) secara **satu kali** per sesi idle (guarded by `_vram_reclaimed`) agar tidak berulang-ulang tanpa mematikan aplikasi.
* **Staging Eviction Cap**: Batas tampungan staging buffer pool diatur maksimal `_MAX_STAGING_POOL_ENTRIES = 8` untuk mencegah konsumsi berlebih *pinned memory* pada GPU.
* **Context Staging Manager**: Mendukung dekorator `with engine.staging_buffer(shape, dtype) as buf:` untuk sewa dan pelepasan otomatis staging buffer.
* **Vulkaninfo Bypass**: Bypassing pemanggilan `vulkaninfo.exe` dinamis dengan mengunci ID device GPU ke `0` via `PIXEL_REFINE_AOT_DEVICE = 0`.

---

## 🚀 Analisis Arsitektur Stable AOTEngine & C++ Backend (Session 6)

### Status Saat Ini:
* **Vulkan Singleton & Bypassing**: Deteksi perangkat GPU terpusat pada `Device 0` dengan melewati pemanggilan dynamic scanning. Semua thread paralel asinkron berbagi satu konteks GPU yang sama secara aman.
* **Stateful Watchdog Idle**: Penyekatan monitoring `_vram_reclaimed` di watchdog mendeteksi kondisi idle aplikasi. Pembersihan VRAM (staging pool, buffer pool, GC) hanya dipicu **satu kali** per sesi idle, mengeliminasi polling redundan berulang.
* **AVX2 SIMD Bit-Perfect Casting**: Kecepatan konversi data hingga **~8x lebih cepat** menggunakan intrinsics 256-bit dengan pembulatan truncate + $0.5f$ untuk menjaga paritas biner $100\%$ dengan standard NumPy `.astype()`.
* **WIC Direct VRAM IO**: DLL C++ menggunakan antarmuka WIC (Windows Imaging Component) untuk memetakan pixel gambar langsung ke alokasi memory GPU (`ti_map_memory`), meniadakan perantara NumPy RAM dengan peningkatan kecepatan IO **+28% lebih cepat**. Alokasi GPU otomatis dibebaskan kembali jika terjadi kegagalan muat gambar untuk mencegah kebocoran VRAM.

### Batasan-Batasan (Limitations):
1. **Thread vs Process**: Paralelisme hanya aman jika menggunakan **Multi-threading** (`ThreadPoolExecutor`). Jika dijalankan menggunakan multi-proses (`ProcessPoolExecutor` / `multiprocessing`), sistem akan men-spawn proses `python.exe` baru secara independen yang memuat konteks Vulkan terpisah, berpotensi memicu overhead inisialisasi ganda di driver GPU.
2. **Crash Keras Tingkat Kernel**: Jika sistem mengalami **BSOD (Blue Screen)** atau kernel Windows crash secara fisik, proteksi pembersihan level user-space tidak akan sempat dipanggil, sehingga restart fisik PC tetap diperlukan.
3. **iGPU Memory Swapping**: Laptop dengan memori GPU terintegrasi (iGPU Intel/AMD) yang membagi RAM sistem (Shared VRAM) dapat mengalami *throttling* atau kegagalan alokasi memori cepat jika ukuran antrean paralel melebihi kapasitas memori fisik yang dialokasikan. Disarankan membatasi ukuran batch asinkron di bawah 10 gambar pada iGPU.
4. **Vulkan Queue Lock**: Fungsi sinkronisasi `engine.sync()` wajib digunakan sebelum melepas buffer intermediate antar pipeline untuk mencegah race condition pembacaan VRAM.


---

## 🆕 Algoritma & Modul Baru: Multi-size BMA & Generic AOT Template

### 1. Multi-size Block Matching Alignment (BMA)
*   **Modul**: `compute_flow.py` → `compute_flow_vulkan.tcm`
*   **Detail**: 
    *   Mengevaluasi pencocokan ubin secara hierarkis (induk $32 \times 32$ dan $4 \times$ sub-ubin $16 \times 16$).
    *   Jika rata-rata cost dari 4 sub-ubin lebih baik 15% dari ubin induk (`avg_sub_cost < 0.85 * best_cost`), maka struktur sub-blok diterima (Split) dan dilakukan refinement sub-pixel paraboloid individu.
    *   Menggunakan metrik pencocokan standar **SAD** dan **SSD** untuk akurasi dan performa stabil serta menghemat memori GPU.

### 2. Generic Optical Flow Template
*   **Modul**: [template_flow.py](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/template_flow.py) → `template_flow_vulkan.tcm`
*   **Detail**:
    *   Template bersih yang memisahkan device math/cost functions (`custom_matching_cost`), kernel pencarian kasar & halus (`initial_coarse_search_kernel`, `hierarchical_refine_kernel`), dan builder graf AOT.
    *   Berfungsi sebagai kerangka kerja awal untuk membangun variasi algoritma estimasi gerakan/aliran spasial (optical flow) berbasis piramida di Taichi GPU.

### 3. GPU Farneback Optical Flow
*   **Modul**: [farneback_flow.py](file:///E:/APP%20Developer/Pixel%20Refine/taichi_library/taichi_algorithm/farneback_flow.py) → `farneback_flow_vulkan.tcm`
*   **Detail**:
    *   Implementasi AOT Farneback GPU yang telah diselaraskan secara matematis dengan OpenCV Farneback.
    *   Menggunakan filter Gaussian separable ($O(N)$ horizontal + vertikal) untuk efisiensi komputasi sistem tensor di GPU, menggantikan operasi non-separable $O(N^2)$ yang lambat.
    *   Mengimplementasikan estimasi polinomial kuadratik least-squares berbasis bobot Gaussian $5 \times 5$ dinamis melalui proyeksi matriks filter konvolusi.

---

## 🆕 MFDenoiser: Single Truth Orchestrator & Spatial Fusion (Session 5)

### Arsitektur MFDenoiser Algorithm

`MFDenoiserAlgorithm` adalah orchestrator pipeline multi-frame denoising yang menggantikan `Similarity.py` sebagai entry point utama. Pipeline: **Load → Align → Merge → PostProcess → Save**.

**Single Truth Source (`_load_params()`)**:
```python
def _load_params(self):
    """Reads from load_similarity_config() — same config as Similarity.py."""
    sim_config = load_similarity_config()
    params = {
        # Tiling
        "tile_size": (tile_val, tile_val),           # (h, w) tuple
        "overlap": 0.30,                              # 0.0-1.0
        # Ghost Rejection
        "motion_sensitivity": 150.0,                  # Higher = more aggressive
        "noise_offset_factor": 0.15,                  # Noise floor offset
        # Backend Selection
        "merging_mode": "spatial_fusion",             # Default backend
        "optical_flow_type": "alignment_tile",        # Farneback/Horn-Schunck/BMA
        "alignment_backend": "taichi_gpu",
        # Smart Fusion (AI)
        "similarity_smart_noise_alpha": 1.0,
        # Spatial Fusion specific
        "early_exit_threshold": 0.05,
        "equalize_brightness": False,
    }
    return params
```

### Backend Selection (Pluggable via `ctx.params`)

| Stage | Parameter | Options | Default |
|-------|-----------|---------|---------|
| **Align** | `alignment_backend` | `"taichi_gpu"`, `"none"`, callable | `"taichi_gpu"` |
| **Align** | `optical_flow_type` | `"alignment_tile"` (BMA), `"horn_schunck"`, `"farneback_aot"`, `"farneback_jit"`, `"block_align"` | `"alignment_tile"` |
| **Merge** | `merging_mode` | `"spatial_fusion"`, `"average"`, `"smart"`, `"super_resolution"`, `"spatial"` | `"spatial_fusion"` |
| **Post** | `postprocessor` | `"adaptive_box"`, `"none"`, callable | `"adaptive_box"` |

### Spatial Fusion Processor (GPU AOT Ghost Rejection)

**Modul**: [spatial_fusion_processor.py](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/spatial_fusion_processor.py)

`SpatialFusionProcessor` menggunakan kernel Taichi AOT dari `compute_spatial.py` untuk ghost rejection berbasis hybrid gradient MAD score dengan analisis coarse-to-fine.

**Pipeline per Frame**:
```
1. Precompute gradients (GPU AOT) → grad_x, grad_y
2. Coarse analysis (1/4 res) → guidance map
3. Fine analysis (4-pass sliding window MAD) → per-frame weight map
4. Bilinear upsample work-res weights → full-res
5. Accumulate: sum += frame * weight
6. Finalize: result = sum / weight_sum
```

**AOT Graphs (dari `spatial_vulkan.tcm`)**:
| Graph | Fungsi |
|-------|--------|
| `precompute_gradients` | Sobel DX/DY gradients |
| `equalize_brightness` | Brightness equalization (optional) |
| `phase1_coarse_analysis` | Coarse confidence map (1/4 res) |
| `phase2_fine_analysis` | Fine weight map (4-pass sliding window) |
| `generate_fine_weights_4passes` | Fused 4-pass fine analysis |
| `accumulate_spatial_merging` | Bilinear upsample + accumulate |
| `fine_analysis_and_accumulate` | Fused fine + accumulate |

**Error Handling**: Jika GPU AOT engine tidak tersedia, raise `RuntimeError` dengan pesan jelas.

### Optical Flow AOT Modules

| Module | TCM File | Graph | Deskripsi |
|--------|----------|-------|-----------|
| **BMA** | `compute_flow_vulkan.tcm` | `align_end_to_end_3layer` | Multi-size Block Matching Alignment (SAD/SSD, 3-layer pyramid) |
| **Horn-Schunck** | `template_flow_vulkan.tcm` | `hs_align_3layer_10`, `hs_align_3layer_20` | Horn-Schunck GPU dengan Jacobi solver (10/20 iterations) |
| **Farneback AOT** | `farneback_flow_vulkan.tcm` | `farneback_multi_3`, `farneback_clear_flow`, `farneback_upsample_flow` | Farneback GPU AOT (polynomial expansion, 3 iterations) |
| **Farneback JIT** | N/A | N/A | Farneback JIT via `taichi_algorithm.farneback_flow()` (requires `AOT_MODE=0`) |

### Cara Penggunaan

**Via UI Settings (JSON config)**:
```json
{
    "merging_mode": "spatial_fusion",
    "optical_flow_type": "alignment_tile",
    "similarity_spatial_tile_size": 16,
    "similarity_spatial_motion_sensitivity": 150.0,
    "similarity_spatial_noise_mad_offset_factor": 0.15,
    "similarity_spatial_overlap_percent": 0.30
}
```

**Via Code Override**:
```python
processor = MFDenoiserAlgorithm(db_path)
output_path = processor.run_pipeline(
    single_process=True,
    merging_mode="spatial_fusion",  # Override backend
)
```


---

## 📱 Mobile QML Integration & Visual Parity (Session 4)

### Kendala & Solusi Penting:
1. **Kesalahan Kustomisasi Gaya QML (`The current style does not support customization...`)**:
   * **Penyebab**: Engine QML memuat gaya native (Windows style) secara default jika modul PySide6/QtQuick di-import sebelum environment variable penyetelan gaya diatur.
   * **Solusi**: Wajib menyetel `os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"` di baris paling atas berkas entri pengujian/aplikasi sebelum meng-import library PySide6 apa pun.
2. **TypeError Properti Null (`TypeError: Cannot read property '...' of null`)**:
   * **Penyebab**: Objek jembatan C++ yang didaftarkan ke QML Context via `setContextProperty` (`theme_bridge` & `app_bridge`) terhapus oleh Python/C++ Garbage Collector jika di-parent-kan menggunakan `.setParent(quick_widget.engine())` karena siklus hidup engine bersifat dinamis.
   * **Solusi**: Parent-kan objek jembatan langsung ke kontainer visual utama, yaitu objek `QQuickWidget` sendiri menggunakan `.setParent(quick_widget)`. Ini memastikan referensi tetap ada selama antarmuka ditampilkan.

---

## 📐 Coding Conventions — Code Simplicity Rules

> **Prinsip utama**: Tulis kode sesederhana mungkin, hindari boilerplate dan sintaks tidak perlu.

### 1. Hindari Lambda untuk Koneksi Signal

**Salah:**
```python
window.bridge.tool_requested.connect(
    lambda name: state.navigate_to(name)
)
```

**Benar:**
```python
window.bridge.tool_requested.connect(state.navigate_to)
```

### 2. Hindari Lambda untuk Function Reference

**Salah:**
```python
state.register_page("MFDenoiser", lambda b: build_workspace_page(b, "MFDenoiser"))
```

**Benar:**
```python
state.register_page("MFDenoiser", build_workspace_page)
```

### 3. Gunakan Fungsi Terpisah untuk Callback

**Salah:**
```python
window.bridge.tool_requested.connect(
    lambda name: print(f"[Mobile] Tool selected: {name}")
)
```

**Benar:**
```python
def on_tool_selected(tool_name):
    print(f"[Mobile] Tool selected: {tool_name}")

window.bridge.tool_requested.connect(on_tool_selected)
```

### 4. Hindari Komentar Berlebihan

**Salah:**
```python
# Register pages
state.register_page("Home", build_home_page)

# Connect navigation
window.bridge.tool_requested.connect(state.navigate_to)

# Show home page
window.setCentralWidget(build_home_page(window.bridge))
```

**Benar:**
```python
state.register_page("Home", build_home_page)
window.bridge.tool_requested.connect(state.navigate_to)
window.setCentralWidget(build_home_page(window.bridge))
```

### 5. Hindari Docstring Berlebihan

**Salah:**
```python
def build_workspace_page(bridge, tool_type: str = "MFDenoiser") -> Container:
    """
    Build the Workspace Page layout.

    Args:
        bridge: AppBridge instance
        tool_type: Current tool type

    Returns:
        Container with all workspace components
    """
```

**Benar:**
```python
def build_workspace_page(bridge) -> Container:
    """Build the Workspace Page layout."""
```

### 6. Hindari Duplikasi Code

**Salah:**
```python
# File memiliki dua blok kode yang sama
import sys
from PySide6.QtWidgets import QApplication
...
import sys
from PySide6.QtWidgets import QApplication
```

**Benar:**
```python
# Hanya satu blok import
import sys
from PySide6.QtWidgets import QApplication
```

### 7. Simpulkan Variabel yang Sering Dipakai

**Salah:**
```python
title_card = Card(title="Settings")
title_card.set_body_content("App preferences and configuration")
layout.add_widget(title_card)
```

**Benar:**
```python
layout.add_widget(Card(title="Settings"))
```



