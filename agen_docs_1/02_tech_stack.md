# Technical Stack

## Taichi AOT Architecture

### Overview
Pixel Refine menggunakan **Taichi AOT (Ahead-Of-Time)** compilation untuk menjalankan kernel GPU dengan performa tinggi tanpa runtime JIT overhead.

```
┌─────────────────────────────────────────────────────────────┐
│  Python API (taichi_aot/__init__.py)                        │
│  └─ Public functions: warp_affine, ofb, akaze, etc.         │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  engine.py (Single Source of Truth)                         │
│  └─ TaichiGPUBuffer, AOTEngine, BufferPool                  │
│  └─ ctypes bridge → taichi_aot_engine.dll                   │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  C++ Backend (taichi_aot_engine.dll)                        │
│  └─ Taichi C-API, Vulkan Runtime, Graph Cache               │
│  └─ Smart Image IO (WIC), Universal GPU Bridge              │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  GPU VRAM (Taichi AOT Compiled Graphs)                      │
│  └─ .tcm modules (Vulkan/CUDA/CPU)                          │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. `engine.py` — Single Source of Truth
- **File**: `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py`
- **Status**: DILAR dimodifikasi tanpa persetujuan eksplisit
- **Tanggung Jawab**:
  - `TaichiGPUBuffer`: Abstraksi Python untuk handle `TiMemory` C++
  - `AOTEngine`: Loading TCM modules, graph caching, buffer management
  - `BufferPool`: Reusable buffer pool untuk efisiensi memori
  - Smart Image IO (imread/imwrite via WIC)
  - Universal GPU Pinned Fast-Copy Bridge

#### 2. `__init__.py` — Public API Bridge
- **File**: `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/__init__.py`
- **Tanggung Jawab**: Menjembatani NumPy/PyTorch dari CPU ke kernel TCM VRAM

#### 3. C++ Backend (`taichi_aot_engine.cpp` → `taichi_aot_engine.dll`)
- Menggunakan **Taichi C-API** untuk memuat modul AOT langsung di VRAM
- `graph_cache` berbasis `std::unordered_map` menghindari pencarian grafik berulang
- Smart Image IO: Membaca/menulis gambar langsung ke VRAM tanpa konversi NumPy
- Recording Pipeline: `add_to_pipeline` + `run_pipeline` mengeksekusi rantai grafik dalam satu siklus

### Primitif Pemrograman

```python
# Input conversion
InputArray(data)  # NumPy/torch → GPU pointer (zero-copy if already TaichiGPUBuffer)

# Output allocation
OutputArray(shape, dtype)  # Allocate new GPU buffer

# Buffer management
engine.allocate(shape, dtype)  # Get from buffer pool (efficient, no malloc)
engine.sync()                  # Force GPU queue completion (REQUIRED before release)
buf.release()                  # Return buffer to pool

# Graph execution
mod.run("graph_name", arg1=val1, arg2=val2)
engine.sync()  # Wait for completion
```

### TCM Modules

| Module | TCM File | Deskripsi |
|--------|----------|-----------|
| `common` | `common_vulkan.tcm` | Copy, rgb2gray, merge/split, hanning, slice/accumulate |
| `gaussian` | `gaussian_vulkan.tcm` | Gaussian blur (1ch/3ch/vec3) |
| `bicubic` | `bicubic_vulkan.tcm` | Bicubic interpolation |
| `bilinear` | `bilinear_vulkan.tcm` | Bilinear interpolation |
| `median_filter` | `median_filter_vulkan.tcm` | 3x3 median filter |
| `hamilton` | `hamilton_vulkan.tcm` | Hamilton-Adams demosaicing |
| `arm` | `arm_vulkan.tcm` | ARM demosaicing |
| `remap` | `remap_vulkan.tcm` | WarpAffine, WarpPerspective, remap_with_flow |
| `ofb` | `ofb_vulkan.tcm` | O-FAST-BRIEF feature matcher |
| `akaze` | `akaze_vulkan.tcm` | A-KAZE feature matcher |
| `ransac` | `ransac_vulkan.tcm` | RANSAC flow cleanup, MAGSAC++ |
| `compute_flow` | `compute_flow_vulkan.tcm` | BMA alignment (SAD/SSD) |
| `template_flow` | `template_flow_vulkan.tcm` | Horn-Schunck GPU |
| `farneback_flow` | `farneback_flow_vulkan.tcm` | Farneback GPU AOT |
| `spatial` | `spatial_vulkan.tcm` | Spatial fusion (ghost rejection) |

### Thread Management

- **GUI Stability**: Taichi JIT calls dilokalisasi dalam thread `AutomatedTaichiWorker`
- **AOT Bypass**: Saat `_IS_AOT_MODE` aktif, graph calls dieksekusi langsung
- **Paralelisme**: `async_run` menggunakan `ThreadPoolExecutor` (max 8 threads)
- **Thread-safe**: `threading.RLock` untuk akses pointer CPU ↔ GPU

### VRAM Protection (3-Layer Auto-Cleanup)

1. **Layer 1 (atexit)**: Cleanup saat aplikasi exit normal atau uncaught exceptions
2. **Layer 2 (Signal Handlers)**: Catch SIGTERM/SIGINT/SIGBREAK/SIGSEGV/SIGILL/SIGABRT/SIGFPE
3. **Layer 3 (Watchdog)**: Daemon thread monitoring setiap 2 detik
   - Stateful smart VRAM reclamation saat idle (>10 detik)
   - Staging eviction cap: max 8 entries
