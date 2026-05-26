# Pixel Refine - Development Knowledge Base (Gemini)

## 🛠 Project Status (Taichi AOT Pipeline)
- **Status**: Production Ready / Optimized
- **Architecture**: Smart C++ Pipeline (One Big Graph) - **Implemented**
- **Algorithm Coverage**: 100% (17 core algorithms migrated to AOT)
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

## 🧱 Technical Constraints & Architecture
- **Smart Overrides**: Identity-based (Memory Handle) swapping using `Placeholder` objects.
- **One Big Graph**: Entire processing chains are recorded once and executed at native C++ speed.
- **Data Type**: 16-bit images are represented in `i32` for AOT precision/safety.
- **Buffer Management**: Managed via `AOTEngine` and `BufferPool` to keep memory footprint ~1GB.
- **Universal GPU Bridge**: Cross-vendor (Nvidia/AMD/Intel) DMA transfer via Pinned-Memory Fast-Copy Bridge.
- **Anti-Crash Design**: Explicit synchronization (`rt->wait()`) and automatic staging-read for VRAM-only buffers.
- **Smart Image IO**: Direct C++ decoding to VRAM (imread/imwrite) using Windows Imaging Component (WIC).
- **Single Source of Truth (`engine.py`)**: `engine.py` adalah jembatan backend C++ yang bersifat *single source of truth*. Logika dan perilakunya tidak boleh diubah kecuali atas instruksi/keputusan eksplisit dari user. Semua algoritma baru atau modifikasi yang menggunakan backend ini harus mematuhi aturan dan perilaku yang ditetapkan oleh `engine.py`.

## 🚀 Roadmap & Next Steps
1. **Bilateral Grid Integration**: **Implemented**
2. **High-Performance Image IO**: **Implemented** (8/16-bit support via WIC)
3. **Universal GPU Interop Bridge**: **Implemented & Verified** (50x Stress-Test Passed)
4. **Smart Data Transformation**: **Implemented** (`gpu_buffer.cast` via C++ Backend)
5. **Mobile Optimization**: Validate TCM modules on mobile backends.

## 📂 Key Files
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py`: Primary AOT runtime bridge (with Pipeline & IO support).
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/taichi_aot_engine.cpp`: C++ Backend Orchestrator.
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/test_comprehensif.py`: Master test suite.
- `test_algorithm/IMG_20250401_182043_B003.png`: Standard test image for high-res benchmarks.

---

## 📘 Deep Dive: Taichi AOT Architecture & Execution Stack

Untuk pengembangan jangka panjang, berikut adalah spesifikasi dan alur kerja utama dari subsistem **Taichi AOT (Ahead-of-Time)** di Pixel Refine:

### 1. Proses Kompilasi (Compile-Time)
* **Penyusun Graf (`compile_*_tcm.py`)**:
  * Mengimpor kernel Taichi dari kode JIT (misalnya `gaussian.py`).
  * Menggunakan `ti.aot.Module(arch)` untuk menginisialisasi modul AOT untuk arsitektur target (`vulkan`, `cuda`, atau `cpu`).
  * Mendefinisikan signature input secara eksplisit menggunakan `ti.graph.Arg` (misalnya `SCALAR` untuk parameter primitif dan `NDARRAY` dengan dimensi tertentu `ndim` untuk data array).
  * Menyusun graf terpadu menggunakan `ti.graph.GraphBuilder()`, menambahkan pemanggilan kernel via `dispatch()`, lalu mengarsipkan menjadi berkas `.tcm` menggunakan `module.archive(save_path)`.

### 2. C++ Generic AOT Engine (`taichi_aot_engine.cpp` -> `taichi_aot_engine.dll`)
* **Core Bridge**: Menggunakan **Taichi C-API** untuk memuat modul AOT secara langsung di memori GPU dengan format biner `.tcm`.
* **Caching Pintar**: Menyediakan `graph_cache` berbasis `std::unordered_map` untuk menghindari pencarian grafik berulang (`get_compute_graph`) yang lambat saat eksekusi real-time.
* **Smart Image IO (WIC)**: Menggunakan COM Windows Imaging Component untuk membaca (`ti_imread_to_gpu`) dan menulis (`ti_imwrite_from_gpu`) gambar langsung ke memori GPU (VRAM) tanpa konversi NumPy perantara di CPU, mendukung kedalaman bit 8-bit dan 16-bit.
* **Recording Pipeline**: Mendukung perekaman sekumpulan grafik eksekusi (`add_to_pipeline`) dan mengeksekusinya dalam satu siklus pemicu tunggal (`run_pipeline`) dengan mekanisme pencarian memori handle/placeholder swap.

### 3. Python ctypes Bridge (`engine.py`)
* **`TaichiGPUBuffer`**: Abstraksi tingkat Python untuk handle memori `TiMemory` di sisi C++. Mendukung `.to_numpy()` via staging buffer VRAM-to-RAM, `.destroy()` instan untuk pembebasan VRAM secara agresif, dan casting tipe data terakselerasi GPU (`.cast()`).
* **OpenCV Hybrid Diagnostics**: Melakukan validasi ketat terhadap input graf (Tipe data, bentuk spasial, dan kesesuaian dimensi vektor/skalar) sebelum dikirim ke C-API, menghasilkan error assert detail dengan call-stack traceback lengkap.
* **Single Source of Truth**: Modul `engine.py` bertindak sebagai satu-satunya kebenaran (*single truth*) untuk jembatan backend C++. Struktur logika, parameter, dan alur eksekusi di dalamnya bersifat sakral dan tidak boleh dimodifikasi tanpa persetujuan eksplisit dari user. Setiap algoritma harus menyesuaikan diri dengan regulasi yang ada di `engine.py`.

### 4. Manajemen Thread GUI & AOT (`taichi_worker.py`)
* **GUI Stability**: Melokalisasi pemanggilan Taichi JIT dalam thread latar belakang tunggal `AutomatedTaichiWorker` untuk mencegah kegagalan context GPU pada aplikasi Qt/PySide.
* **AOT Bypass**: Ketika program berjalan dalam mode AOT compiler/eksekusi (`_IS_AOT_MODE`), siklus thread worker otomatis di-bypass, mengeksekusi panggilan graf secara langsung dan sinkron di thread pemanggil untuk menghindari overhead multi-threading.

### 5. Backup Formulasi Non-Linear (Sebelum Migrasi Linear)
*Catatan: Formulir di bawah ini dipertahankan sebagai cadangan setelah migrasi ke pipeline GPU Linear Demosaicing.*
Subsistem demosaicing (`compile_hamilton_tcm.py`) sebelumnya mengimplementasikan pipeline pemrosesan warna non-linear berikut di GPU:
* **Matriks Transformasi Warna (Camera-to-sRGB):**
  Mengonversi piksel dari ruang warna linear sensor kamera (*Camera Space*) ke ruang warna sRGB menggunakan matriks transformasi $3 \times 3$ yang diekstrak dari metadata RAW/DNG:
  $$\begin{aligned}
  sR &= C_{00} \cdot R + C_{01} \cdot G + C_{02} \cdot B \\
  sG &= C_{10} \cdot R + C_{11} \cdot G + C_{12} \cdot B \\
  sB &= C_{20} \cdot R + C_{21} \cdot G + C_{22} \cdot B
  \end{aligned}$$
* **Dynamic Algebraic Sigmoid Highlight Roll-off (Tone Mapping):**
  Memetakan rentang dinamis tinggi (HDR) $[0, \infty)$ ke SDR $[0, 1)$ secara halus dan asimtotik untuk menghindari hard clipping pada area super terang:
  $$f(x) = \frac{x}{\sqrt{1 + x^2}}$$
  Implementasi Taichi:
  ```python
  sR = sR / ti.math.sqrt(1.0 + sR * sR)
  ```
* **Gamma Correction:**
  Menerapkan koreksi gamma standar sRGB untuk tampilan monitor:
  $$\text{Output} = \text{clamp}(sRGB, 0.0, 1.0)^{1 / 2.22}$$
