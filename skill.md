# Pixel Refine - Technical Skill Guide & Reusable Library Catalog

> Panduan prosedural untuk menulis, memodifikasi, dan mengintegrasikan fungsi algoritma backend (Taichi GPU JIT/AOT) serta elemen antarmuka (Generic UI Library & Real-time Settings) dalam ekosistem desktop Pixel Refine.

---

## 🗺️ Peta Komponen Core Workspace

Aplikasi desktop ini menggunakan pembagian tanggung jawab yang jelas antara pemrosesan data GPU (Taichi) dan penyajian antarmuka pengguna (PySide6).

```
                            [ main_desktop.py ] (App Entry Point)
                                     │
                 ┌───────────────────┴───────────────────┐
                 ▼                                       ▼
        [ enhance_stack ] (MVC Views)            [ GenericUILibrary ] (UI Toolkit)
                 │                                       │
                 ▼                                       ▼
        [ taichi_aot ] (Public API)             [ mixins / decorators ] (@live_update)
                 │                                       │
                 ▼                                       ▼
        [ engine.py ] (C++ dll Bridge)          [ stylesheet.py ] (Global Styles)
                 │
                 ▼
        [ GPU VRAM (Taichi AOT) ]
```

---

## 1. Taichi JIT & AOT GPU Architecture

Bagian ini mendokumentasikan pemrosesan akselerasi grafis (GPU) menggunakan compiler Taichi AOT (Ahead-Of-Time).

### 1.1 `engine.py` (C++ ctypes Bridge)
- **Status**: *Single Source of Truth* untuk interaksi driver dan VRAM.
- **Tanggung Jawab**: Mengatur alokasi VRAM (`TaichiGPUBuffer`), manajemen memori terpadu, caching grafik TCM, input/output menggunakan Windows Imaging Component (WIC), dan *Universal GPU Pinned Fast-Copy Bridge*.
- **Aturan**: File [`engine.py`](file:///e:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py) dilarang dimodifikasi secara langsung kecuali atas persetujuan eksplisit.

### 1.2 `__init__.py` (API Bridge Publik)
- **Tanggung Jawab**: Menjembatani array NumPy/PyTorch dari CPU/GPU ke kernel TCM VRAM.
- **Contoh Fungsi API Standard**:
```python
def warp_affine(src, M, dsize, flags=0, border_mode=0, return_gpu=False):
    src_buf = InputArray(src)
    h, w = src_buf.shape[:2]
    # ... memanggil modul remap TCM ...
    return dst_buf if return_gpu else dst_buf.to_numpy()
```

### 1.3 Primitif Pemrograman Taichi AOT
- `InputArray(data)`: Mengubah NumPy array, torch tensor, atau data CPU menjadi penunjuk GPU secara aman (zero-copy jika input sudah berupa `TaichiGPUBuffer`).
- `OutputArray(shape, dtype)`: Mengalokasikan buffer GPU baru yang ditujukan sebagai wadah hasil pemrosesan.
- `engine.allocate(shape, dtype)`: Mengambil buffer sementara dari *buffer reuse pool*. Efisien karena tidak melakukan alokasi malloc fisik berulang kali.
- `engine.sync()`: Memaksa antrean eksekusi GPU untuk menyelesaikan tugasnya. Wajib dipanggil sebelum merilis buffer intermediate.
- `buf.release()`: Mengembalikan buffer ke pool untuk digunakan kembali oleh proses berikutnya.

---

## 2. Katalog Taichi Library (TCM Modules)

Berikut adalah daftar modul Ahead-of-Time (.tcm) terkompilasi yang dikelola oleh engine backend C++:

| Nama Modul (`_mod("...")`) | Jenis Operasi | Graph & Deskripsi |
|---|---|---|
| `common` | Utilitas | `copy`, `rgb2gray`, `merge/split`, `hanning`, `slice_tile`, `accumulate_tile` |
| `gaussian` | Blur | `gaussian_blur` (1ch/3ch/vec3) untuk reduksi noise spasial |
| `bicubic` / `bilinear` | Resizing | Algoritma interpolasi citra resolusi tinggi |
| `median_filter` | Filter Spasial | Eliminasi salt-and-pepper noise 3x3 |
| `hamilton` | Bayer RAW | Hamilton-Adams Demosaicing untuk mengubah RAW RGGB 16-bit ke RGB |
| `arm` | Bayer RAW | Adaptive Residual Minimization (ARM) Demosaicing kustom dengan Laplacian Residual & Soft-Decision |
| `remap` | Registrasi | WarpAffine GPU & WarpPerspective GPU spasial dengan mirror border reflection |
| `ofb` | Fitur | O-FAST-BRIEF Keypoint Detector dengan Sub-pixel Refinement, Rotation/Scale-Invariance (Image Pyramid L0-L2), Adaptive Grid ANMS, Astro Fallback Matcher |
| `akaze` | Fitur | A-KAZE Keypoint Detector berbasis Hessian Determinant, Non-Linear Scale Space (FED), deskriptor M-LDB 486-bit binary, dan Hamming matcher (16-int buffer) |
| `ransac` | Geometri | RANSAC Flow Cleanup, MAGSAC++ GPU Homography Solver (Tukey's Biweight scoring & Weighted Least Squares refinement) |
| `compute_flow` | Registrasi | Alinyemen ubin hierarkis (3-skala) dengan pembagian ubin adaptif (Multi-size BMA) menggunakan metrik SAD/SSD standar |
| `template_flow` | Registrasi / Template | Kerangka kerja generik untuk pengembangan variasi algoritma optical flow AOT kustom |
| `farneback_flow` | Registrasi / Optical Flow | Farneback Optical Flow GPU dengan pencocokan polinomial least-squares 5x5 dan filter Gaussian separable |


### Aturan Kompilasi TCM Baru:
1. Daftarkan signature input secara eksplisit menggunakan `ti.graph.Arg` pada `compile_*.py`.
2. Vektor multi-channel (seperti RGB `vec3` float) didefinisikan sebagai `ArgKind.NDARRAY` dengan `ndim=2` dan field dimensi vektor internal di Taichi (bukan dimensi spasial tambahan `ndim=3`).
3. Selalu sediakan fallback CPU untuk memastikan ketahanan pipeline jika driver Vulkan/CUDA target crash.

---

## 3. Katalog Generic UI Library

Generic UI Library adalah modul toolkit mandiri yang meniru arsitektur Bootstrap 5 untuk PySide6 desktop. Aturan gaya, tata letak, dan animasi diatur secara terpusat di bawah [`GenericUILibrary`](file:///e:/APP%20Developer/Pixel%20Refine/resources/GenericUILibrary).

### 3.1 Komponen Widget Standar

#### `Button(text, variant="primary", parent=None)`
- **Variant**: `primary` (hijau solid), `secondary` (abu-abu/biru), `danger` (merah), `ghost` (outline transparan).
- **Style**: Rounded border (6px), font Segoe UI / Inter (11pt), semi-bold.

#### `Container(padding=20, parent=None)`
- Panel pembungkus dasar dengan margin internal (padding) terpadu.

#### `FormGroup(label, input_type="text")`
- Komponen input yang dilengkapi label atas terintegrasi.
- **Input Type**: `text`, `select` (dropdown QComboBox), `checkbox`, `radio`.

#### `FeatureCard(title, description, options, fallback_val, parent)`
- Kartu kontrol premium untuk memilih parameter algoritma yang dilengkapi dengan animasi switch toggle.

#### `ListGroup(reordering=True)`
- Antarmuka daftar list dinamis yang mendukung drag and drop reordering item.

#### `SkeletonLoader(minimalist=True)`
- Animasi placeholder pulsing abu-abu lembut untuk menyembunyikan visual freeze ketika memuat dataset grid yang besar.

---

## 4. Real-time Settings & Broadcast Translation System

Untuk menjamin perubahan setelan (termasuk bahasa dan parameter performa) ter-apply secara instan tanpa perlu merestart program utama, Pixel Refine menerapkan sistem pembaruan realtime berbasis listener dan decorator.

### 4.1 Decorator `@live_update`
All main container classes or main window classes are decorated with `@live_update` to manage dynamic updates and prevent memory leaks.

When a live update is triggered via `trigger_live_update()`, it recursively traverses the widget hierarchy (`findChildren(QWidget)`) and executes the target method (typically `retranslate_ui` or `update_theme`). 

#### Best Practices for Live Updates:
1. **Pass Language Strings Directly**: To avoid I/O disk race conditions when switching languages, pass the selected language string directly to `language_config.reload_language(lang_str)` before calling `retranslate_ui()` or triggering broadcasts.
2. **Explicit Child Translating**: For dynamic views containing dynamically added children (like `BulkPageLayout` holding `CombinedPanel`s), override `retranslate_ui` to explicitly iterate and call `retranslate_ui` on the active child instances.
3. **Compact Buttons sizing**: Set compact action buttons (`Buat Batch Baru`, `Hapus Batch`, `Proses Semua Batch`) to a height of `22px` and custom padding `2px 4px` with a font size of `8pt` to maintain visually proportional size constraints.
4. **Button Variant styling**: In `update_theme`, use `create_button_style(variant, theme)` to apply soft borders and theme colors instead of hardcoded stylesheet text.

**Usage Example**:
```python
from resources.GenericUILibrary import live_update, trigger_live_update

@live_update
class EnhanceStackView(QWidget):
    # Registered to receive trigger_live_update() broadcasts
    ...
```

### 4.2 Mixin `SyncMixin` (Declarative Data Binding)
Digunakan untuk sinkronisasi otomatis nilai widget langsung dengan state penyimpanan (DataStore):
```python
class RightPanel(QWidget, SyncMixin):
    def _setup_ui(self):
        # Binding otomatis: perubahan state di self.sr_card langsung mengubah data store
        self.add_binding("super_resolution_algo", self.sr_card, fallback="No Super Resolution")
```

---

## 5. Development Rules (Aturan Coding)

Untuk menjaga paritas kode dan arsitektur tetap bersih, pengembang wajib mematuhi aturan berikut:

### 5.1 Aturan Komputasi Taichi & Backend
- **i32 Popcount Bug**: Operator bitwise shift `>>` pada integer 32-bit bertanda (`ti.i32`) adalah arithmetic shift (menyebarkan sign bit). Selalu hilangkan MSB (sign bit) sebelum menerapkan trik popcount cepat.
- **Nested `ti.static`**: Batasi unrolling statis loop. Nested loop statis dengan iterasi total `> 32` akan menyebabkan LLVM backend macet (compile hang).
- **Memory Synchronize**: Selalu panggil `engine.sync()` sebelum mengeksekusi `.release()` pada buffer sementara.
- **Sub-pixel Refinement**: Ketika melakukan sub-pixel interpolation untuk keypoint, gunakan fitting kuadratik paraboloid 2D pada peta skor 3x3 di sekitar keypoint. Pastikan pembagi (`2.0 * s_center - s_left - s_right`) di atas threshold aman (e.g. `1e-5`) untuk menghindari division by zero, dan batasi offset hasil fitting dalam rentang `[-0.5, 0.5]`.
- **Rotation Invariance (Centroid Angle)**: Orientasi pola BRIEF wajib dihitung dinamis menggunakan intensitas momen centroid local patch (`m10` dan `m01` melalui `ti.atan2(m01, m10)`) alih-alih sudut statis `0.0`.
- **Multi-scale Image Pyramid & Adaptive Parameters**: Untuk menjaga ketangguhan pencocokan citra pada resolusi rendah (di bawah 240px), batasi tingkat pyramid (levels) secara dinamis sesuai resolusi input, skala parameter `grid_size`, `margin`, dan `threshold` di setiap level, serta lakukan *fused* median filter + Gaussian pre-pass secara terpisah untuk meredam noise sensor.
- **Adaptive Residual Minimization (ARM) Demosaice**: Saat merancang rekonstruksi demosaic kustom berfrekuensi tinggi, gunakan pembobotan Gauss soft-decision spasial adaptif berdasarkan Laplacian orde-dua spasial lokal $5\times5$ untuk meredam zipper artifacts di sepanjang garis diagonal, serta terapkan penyaringan median $3\times3$ bertingkat di atas peta perbedaan warna residual spasial ($R-G$ dan $B-G$) untuk mengeliminasi false color noise secara efektif pada wilayah linier.
- **A-KAZE Non-Linear Diffusion (FED)**: Ketika membangun ruang skala non-linear, gunakan koefisien konduktivitas Perona-Malik II berbasis magnitudo gradien filter Scharr. Skema difusi FED (Fast Explicit Diffusion) wajib menggunakan ukuran langkah $\tau_j$ siklik yang bervariasi untuk menjamin stabilitas kisi 2D numerik. Integrasikan `pack_matches_kernel` untuk menyatukan pengemasan keypoint/matches di GPU sebelum pengunduhan host.



### 5.2 Aturan Antarmuka & Generic UI
- **Styling Konsisten**: Dilarang menulis style custom secara ad-hoc menggunakan `.setStyleSheet()` yang menimpa warna dasar sistem. Gunakan variabel kelas/mixins bawaan untuk menjaga harmoni palet warna.
- **Centering Absolut Layout**: Untuk memposisikan widget di tengah secara absolut (seperti tombol Mode), bagi layout header utama menjadi 3 sub-layout QHBoxLayout (`left`, `center`, `right`) dan masukkan ke layout utama dengan stretch factor setara `(1, 1, 1)`.
- **Eager Incremental Loading**: Selalu batasi jumlah visualisasi thumbnail yang dimuat pertama kali di halaman grid (e.g. limit ke 10 item) dikombinasikan dengan `SkeletonLoader` sebelum memuat sisa gambar di background thread.

### 5.3 Aturan QML Mobile & Visual Parity
- **Environment Variable Urutan Pertama**: Selalu setel `os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"` sebelum meng-import modul PySide6 apa pun pada file pengujian QML atau aplikasi mobile.
- **Parenting Konteks QML**: Jangan menggunakan `.setParent(quick_widget.engine())` karena engine internal Qt Quick dapat merekonstruksi instansnya sewaktu-waktu dan memicu *garbage collection* dini. Gunakan `.setParent(quick_widget)` (pada `QQuickWidget` / `QQuickView`) atau simpan referensi kuat sebagai atribut *parent widget/window* utama.

### 5.4 Aturan Kesederhanaan Kode (Code Simplicity Rules)

> **Prinsip utama**: Tulis kode sesederhana mungkin, hindari boilerplate dan sintaks tidak perlu.

#### 5.4.1 Hindari Lambda untuk Koneksi Signal
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

#### 5.4.2 Hindari Lambda untuk Function Reference
**Salah:**
```python
state.register_page("MFDenoiser", lambda b: build_workspace_page(b, "MFDenoiser"))
```

**Benar:**
```python
state.register_page("MFDenoiser", build_workspace_page)
```

#### 5.4.3 Gunakan Fungsi Terpisah untuk Callback
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

#### 5.4.4 Hindari Komentar Berlebihan
**Salah:**
```python
# Register pages
state.register_page("Home", build_home_page)

# Connect navigation
window.bridge.tool_requested.connect(state.navigate_to)
```

**Benar:**
```python
state.register_page("Home", build_home_page)
window.bridge.tool_requested.connect(state.navigate_to)
```

#### 5.4.5 Hindari Docstring Berlebihan
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

#### 5.4.6 Hindari Duplikasi Code
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

#### 5.4.7 Simpulkan Variabel yang Sering Dipakai
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

---

## 6. Parallel Runtime & Anti-Crash Auto-Cleanup Engine (Session 3)

Backend AOT Engine mendukung pemrosesan asinkron paralel yang aman dan kebal terhadap kebocoran VRAM di Windows.

### 6.1 Paralel & Asinkron (`async_run`)
Fungsi `async_run` mengeksekusi kernel grafis secara paralel menggunakan `ThreadPoolExecutor` (maksimal 8 thread worker). Semua akses ke driver Vulkan disinkronkan secara internal melalui pengunci bertingkat (`threading.RLock`) di dalam `AOTEngine`:
```python
future = module.async_run("gaussian_blur", src=img_gpu, dst=dst_gpu, sigma=1.5)
# Tunggu hasil tanpa blocking thread UI utama
future.result()
```

### 6.2 3-Layer VRAM Auto-Cleanup Guard
Untuk mencegah "Zombie VRAM" atau driver Vulkan membeku (yang menyebabkan Windows terjebak dalam kondisi *endless shutdown/restart*), engine menerapkan perlindungan 3 lapis:
1. **Layer 1 (atexit)**: `atexit.register(_global_cleanup)` membebaskan semua memori GPU secara tertib saat aplikasi keluar normal atau mengalami uncaught Python exceptions.
2. **Layer 2 (Signal Handlers)**: Menangkap sinyal OS utama (`SIGTERM`, `SIGINT`, `SIGBREAK`) serta sinyal fatal C++ crash (`SIGSEGV` / Access Violation, `SIGILL`, `SIGABRT`, `SIGFPE`) untuk membersihkan VRAM sebelum proses dihancurkan.
3. **Layer 3 (Watchdog Thread)**: Thread daemon latar belakang memantau thread utama setiap 2 detik. Jika thread utama mati/freeze, watchdog langsung memicu pembersihan darurat dan memanggil `os._exit(1)`.
   * **Stateful Smart VRAM Reclamation**: Ketika aplikasi terdeteksi idle (tidak ada aktivitas GPU >10 detik), watchdog tidak mematikan aplikasi, melainkan hanya melakukan pembersihan VRAM pintar (mengosongkan buffer pool, staging buffers, dan memicu garbage collection). Proses pembersihan ini hanya dijalankan **sekali saja** per sesi idle (guarded by `_vram_reclaimed = True`) untuk menghindari looping pembersihan berulang yang tidak efisien. Bendera `_vram_reclaimed` otomatis di-reset menjadi `False` begitu ada aktivitas GPU baru terdeteksi.

### 6.3 Vulkan Device Lock Bypass & Staging Eviction
* **Vulkan Device Bypass**: Untuk menghindari instansiasi proses pembantu `vulkaninfo.exe` secara berulang yang dapat mengunci memori driver video, deteksi GPU dinamis dilewati secara permanen dengan mengunci ID device utama ke `0` melalui environment variable:
  ```python
  os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"  # Bypass scan, langsung pakai GPU 0
  os.environ["VK_LOADER_DEBUG"] = "error"      # Bungkam loader warnings
  ```
* **Staging Buffer Eviction Strategy**: Guna mencegah akumulasi buffer pinned memory yang tidak digunakan di VRAM, pool staging dibatasi maksimal `_MAX_STAGING_POOL_ENTRIES = 8`. Begitu terlampaui, alokasi staging tertua dibersihkan dari memori secara otomatis menggunakan `_evict_staging_pool()` saat pelepasan buffer sewaan.
* **Context Staging Manager**: Gunakan `with engine.staging_buffer(shape, dtype) as buf:` untuk penulisan kode asinkron yang otomatis mengembalikan sewaan buffer staging secara aman saat keluar dari blok konteks.

---

## 7. MFDenoiser: Spatial Fusion & Backend Selection (Session 5)

MFDenoiser adalah orchestrator utama untuk multi-frame denoising yang mendukung berbagai backend alignment dan merging melalui parameter konfigurasi.

### 7.1 Arsitektur Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│  UI Settings (similarity_parameter_settings.py)             │
│  └─ load_similarity_config() → JSON config                  │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  MFDenoiserAlgorithm._load_params()  ← SINGLE TRUTH        │
│  └─ Simpan ke ctx.params (dict)                             │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  run_pipeline() → ctx.params ke setiap stage                │
│                                                             │
│  stage_align(ctx):                                          │
│    ├─ alignment_backend → "taichi_gpu" / "none" / callable │
│    └─ optical_flow_type → "alignment_tile" / "horn_schunck" │
│         / "farneback_aot" / "farneback_jit" / "block_align" │
│                                                             │
│  stage_merge(ctx):                                          │
│    ├─ merging_mode="spatial_fusion" → SpatialFusionProcessor│
│    ├─ merging_mode="average" → AverageDenoiseProcessor     │
│    ├─ merging_mode="smart" → SmartDenoiseProcessor (AI)    │
│    ├─ merging_mode="super_resolution" → SRProcessor        │
│    └─ merging_mode="spatial" → SpatialDenoiseProcessor     │
│                                                             │
│  stage_postprocess(ctx):                                    │
│    ├─ postprocessor="adaptive_box" → HF Denoise            │
│    ├─ postprocessor="none" → Skip                          │
│    └─ postprocessor=callable → Custom function             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Parameter Mapping

| Parameter | Config Key | Default | Digunakan di |
|-----------|-----------|---------|--------------|
| `merging_mode` | `merging_mode` | `"spatial_fusion"` | `stage_merge()` |
| `optical_flow_type` | `optical_flow_type` | `"alignment_tile"` | `_align_taichi_gpu()` |
| `tile_size` | `similarity_spatial_tile_size` | `16` | `_align_taichi_gpu()`, `_run_tiled_merge()` |
| `overlap` | `similarity_spatial_overlap_percent` | `0.30` | `_run_tiled_merge()` |
| `motion_sensitivity` | `similarity_spatial_motion_sensitivity` | `150.0` | `SpatialFusionProcessor` |
| `noise_offset_factor` | `similarity_spatial_noise_mad_offset_factor` | `0.15` | `SpatialFusionProcessor` |
| `early_exit_threshold` | `early_exit_threshold` | `0.05` | `SpatialFusionProcessor` |

### 7.3 Cara Penggunaan

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
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import MFDenoiserAlgorithm

processor = MFDenoiserAlgorithm(db_path)
output_path = processor.run_pipeline(
    single_process=True,
    merging_mode="spatial_fusion",  # Override backend
)
```

### 7.4 Spatial Fusion Processor API

```python
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion_processor import SpatialFusionProcessor

processor = SpatialFusionProcessor(
    motion_sensitivity=150.0,
    noise_offset_factor=0.15,
    early_exit_threshold=0.05,
    equalize_brightness=False,
)

frame_count, sum_img, sum_weight, ref_noise_sigma = processor.process(
    images=images_list,
    reference_image_float=ref_float,
    ref_h=h, ref_w=w,
    ref_dtype=np.uint16,
    work_res_h=work_h, work_res_w=work_w,
    update_progress=callback,
    stop_requested=stop_check,
)
```

**Error Handling**: Jika GPU AOT engine tidak tersedia, `SpatialFusionProcessor.process()` akan raise `RuntimeError` dengan pesan yang jelas.

### 7.5 Optical Flow Backend Selection

| Backend | TCM File | Deskripsi | Kapan Gunakan |
|---------|----------|-----------|---------------|
| `alignment_tile` | `compute_flow_vulkan.tcm` | BMA (Block Matching Alignment) dengan SAD/SSD | Default, cepat, akurat untuk translasi kecil |
| `horn_schunck` | `template_flow_vulkan.tcm` | Horn-Schunck dengan Jacobi solver | Gerakan halus, rotasi lambat |
| `farneback_aot` | `farneback_flow_vulkan.tcm` | Farneback GPU AOT | Gerakan kompleks, polynomial expansion |
| `farneback_jit` | N/A | Farneback JIT (requires `AOT_MODE=0`) | Development/testing |
| `block_align` | `block_align_vulkan.tcm` | Block alignment variant | Experimental |

### 7.6 Key Files

| File | Deskripsi |
|------|-----------|
| [`MFDenoiser.py`](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/MFDenoiser.py) | Orchestrator utama (single truth source) |
| [`Similarity.py`](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/Similarity.py) | Legacy orchestrator (backup) |
| [`spatial_fusion_processor.py`](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/spatial_fusion_processor.py) | Spatial Fusion GPU AOT processor |
| [`compute_spatial.py`](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi/compute_spatial.py) | Taichi AOT kernels untuk ghost rejection |
| [`similarity_parameter_settings.py`](file:///E:/APP%20Developer/Pixel%20Refine/pixel_refine_desktop/enhance_stack/components/batch_page_v2/parameter_denoising/similarity_parameter_settings.py) | UI settings & config loader |

---

## 7.7 Deep Architectural Analysis of AOTEngine & C++ Backend (Session 6)

Untuk menjaga stabilitas maksimal pada driver WDDM grafis Windows dan mencegah memori GPU tersangkut saat shutdown, backend mengimplementasikan arsitektur runtime berikut:

### 7.7.1 Manajemen Konteks Vulkan Tunggal (Singleton)
Semua thread paralel asinkron yang diluncurkan oleh `ThreadPoolExecutor` berbagi instansiasi `AOTEngine` yang sama. Perangkat dikunci ke indeks `Device 0` secara statis via environment variable `PIXEL_REFINE_AOT_DEVICE = 0` sebelum CDLL memuat backend C++. Hal ini mem-bypass pemanggilan dynamic scanning (`vulkaninfo.exe`) secara total untuk menghindari tabrakan driver grafis tingkat rendah.

### 7.7.2 Stateful Watchdog & Smart VRAM Reclamation
Watchdog daemon memantau deteksi idle melalui flag penanda `_vram_reclaimed` yang disinkronkan di bawah `_heartbeat_lock`.
* Saat tidak ada operasi GPU aktif selama 10 detik (`activity_age > 10.0s` dan `op_elapsed == 0.0`), watchdog akan memicu reklamasi VRAM secara **satu kali** per sesi idle.
* Konfigurasi staging pool dibebaskan secara menyeluruh, free list buffer dinonaktifkan, dan garbage collection Python (`gc.collect()`) dijalankan.
* Bendera `_vram_reclaimed` disetel menjadi `True` sehingga watchdog tidak melakukan polling pembersihan berulang yang membuang siklus CPU.
* Aktivitas GPU baru apa pun otomatis mereset bendera ini ke `False` untuk siklus pembersihan berikutnya.

### 7.7.3 AVX2 SIMD Cast dengan Presisi Bit-Perfect
Konversi u8/u16 ke float32 (dan sebaliknya) diakselerasi di tingkat native C++ menggunakan vector intrinsics 256-bit. Untuk menjamin keselarasan bit-perfect dengan pembulatan standard NumPy (`astype`), backend C++ melakukan penskalaan konversi disusul dengan penambahan konstanta offset `+0.5f` sebelum menerapkan instruksi pemotongan linear `_mm256_cvttps_epi32` (truncate):
$$\text{Output} = \text{truncate}(x \times 255.0 + 0.5)$$

### 7.7.4 WIC Direct-to-VRAM Image Loader
Fungsi `ti_imread_to_gpu` di C++ DLL membaca dan mengonversi format raster piksel gambar langsung ke memori grafis yang terpetak menggunakan *Windows Imaging Component (WIC)*. Ini memotong sirkuit pembuatan array Python/NumPy intermediat, mengurangi latensi IO sistem hingga **28%**. 
* Jika pembacaan atau alokasi gagal di tengah jalan, DLL C++ secara otomatis memanggil `ti_free_memory` pada instansiasi memori GPU yang sudah sempat dipesan untuk mencegah kebocoran VRAM.
