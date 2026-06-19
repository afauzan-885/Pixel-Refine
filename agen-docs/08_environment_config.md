# Environment Configuration

## Project Structure

```
Pixel Refine/
├── pixel_refine_desktop/           # Desktop application
│   └── enhance_stack/
│       └── core/
│           └── algorithm/
│               ├── denoising/      # MFDenoiser, Similarity
│               │   ├── spatial_core/
│               │   │   ├── spatial_fusion_processor.py
│               │   │   └── similarity_taichi/
│               │   │       └── compute_spatial.py
│               │   ├── smart_fusion/
│               │   └── MFDenoiser.py
│               ├── alignment/
│               │   ├── alignment_tile/
│               │   │   ├── compute_flow.py
│               │   │   └── template_flow.py
│               │   └── alignment_features/
│               └── taichi_aot/
│                   ├── engine.py   # Single Source of Truth
│                   └── __init__.py # Public API
│
├── taichi_library/                 # Taichi algorithms library
│   └── taichi_algorithm/
│       ├── aot_py/                 # Compile scripts & tests
│       │   ├── compile_farneback_tcm.py
│       │   ├── compile_template_flow_tcm.py
│       │   └── test_optical_flow_aot.py
│       ├── aot_tcm/                # Compiled TCM modules
│       │   ├── farneback_flow_vulkan.tcm
│       │   ├── template_flow_vulkan.tcm
│       │   └── ...
│       ├── farneback_flow.py
│       └── ...
│
├── ui/
│   └── data/
│       └── aot_assets/             # UI-related TCM modules
│           └── spatial_vulkan.tcm
│
├── resources/
│   └── GenericUILibrary/           # UI toolkit
│
├── agen.md                         # Main knowledge base
├── skill.md                        # Technical skill guide
└── agen_docs/                      # This documentation folder
    ├── 01_project_overview.md
    ├── 02_tech_stack.md
    ├── 03_mfdenoiser_architecture.md
    ├── 04_optical_flow.md
    ├── 05_development_practices.md
    ├── 06_pitfalls_and_fixes.md
    ├── 07_build_and_compile.md
    └── 08_environment_config.md
```

## Environment Variables

### Core Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AOT_MODE` | `1` | `0` = JIT mode (compile/test), `1` = AOT mode (production) |
| `PIXEL_REFINE_AOT_DEVICE` | `0` | GPU device ID (bypass vulkaninfo scan) |
| `VK_LOADER_DEBUG` | `error` | Vulkan loader debug level (`all`, `error`, `warn`, `info`) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROFILE_SPATIAL` | `0` | Enable spatial fusion profiling (`1` = on) |
| `PYTHONIOENCODING` | `cp1252` | Python I/O encoding (set `utf-8` for Windows) |
| `TI_OFFLINE_CACHE` | `1` | Taichi offline cache (set by compile scripts) |
| `TI_ENABLE_CUDA_MALLOC_ASYNC` | `0` | Disable async CUDA malloc (set for stability) |

## Configuration Files

### 1. Algorithm Parameters
**File**: `database/setting/Parameter_Stack_Enhance.json`

```json
{
    "Similarity": {
        "use_multi_core": true,
        "spatial_params": {
            "similarity_spatial_tile_size": 16,
            "similarity_spatial_motion_sensitivity": 150.0,
            "similarity_spatial_noise_mad_offset_factor": 0.15,
            "similarity_spatial_overlap_percent": 0.30,
            "similarity_spatial_num_workers": 1
        },
        "merging_mode": "spatial_fusion",
        "optical_flow_type": "alignment_tile"
    }
}
```

### 2. General Settings
**File**: `config/general_settings.json`

```json
{
    "enable_linear_mode": false,
    "language": "Indonesian"
}
```

## Runtime Configuration

### MFDenoiser Parameter Loading

```python
# MFDenoiserAlgorithm._load_params()
sim_config = load_similarity_config()
params = {
    "tile_size": (tile_val, tile_val),
    "overlap": sim_config.get("similarity_spatial_overlap_percent", 0.30),
    "motion_sensitivity": sim_config.get("similarity_spatial_motion_sensitivity", 150.0),
    "noise_offset_factor": sim_config.get("similarity_spatial_noise_mad_offset_factor", 0.15),
    "merging_mode": sim_config.get("merging_mode", "spatial_fusion"),
    "optical_flow_type": sim_config.get("optical_flow_type", "alignment_tile"),
    "alignment_backend": sim_config.get("alignment_backend", "taichi_gpu"),
}
```

### Resolution Handling

```python
# MFDenoiser._compute_work_resolution()
def _compute_work_resolution(ref_h, ref_w, target_mp=12.5e6):
    """Downscale if exceeding target megapixels."""
    if (ref_h * ref_w) > target_mp:
        scale = np.sqrt(target_mp / (ref_h * ref_w))
        wh = int(ref_h * scale)
        ww = int(ref_w * scale)
    else:
        wh, ww = ref_h, ref_w
    return (wh // 2) * 2, (ww // 2) * 2  # Ensure even dimensions
```

## VRAM Management

### Buffer Pool
```python
# AOTEngine manages reusable buffer pool
buffer = engine.allocate(shape, dtype)  # Get from pool
# ... use buffer ...
engine.sync()  # REQUIRED before release
buffer.release()  # Return to pool
```

### Staging Buffer Eviction
- Max staging entries: `_MAX_STAGING_POOL_ENTRIES = 8`
- Oldest staging buffers evicted when limit exceeded

### Watchdog Configuration
- Monitoring interval: 2 seconds
- Idle threshold: 10 seconds
- VRAM reclamation: Once per idle session (`_vram_reclaimed` flag)

## Debugging

### Enable Verbose Logging
```python
# Vulkan loader
os.environ["VK_LOADER_DEBUG"] = "all"

# Spatial profiling
os.environ["PROFILE_SPATIAL"] = "1"

# Force JIT mode
os.environ["AOT_MODE"] = "0"
```

### GPU Device Selection
```python
# Bypass vulkaninfo.exe scan
os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"  # Use GPU 0
```

## Common Commands

### Run Application
```bash
cd "e:\APP Developer\Pixel Refine"
python main_desktop.py
```

### Compile All TCM Modules
```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"

# Farneback
python -m taichi_library.taichi_algorithm.aot_py.compile_farneback_tcm

# Horn-Schunck
python -m taichi_library.taichi_algorithm.aot_py.compile_template_flow_tcm

# Spatial
python pixel_refine_desktop\enhance_stack\core\algorithm\denoising\spatial_core\similarity_taichi\compute_spatial.py

# Remap
python -m taichi_library.taichi_algorithm.aot_py.compile_remap_tcm

# OFB
python -m taichi_library.taichi_algorithm.aot_py.compile_ofb_tcm

# A-KAZE
python -m taichi_library.taichi_algorithm.aot_py.compile_akaze_tcm
```

### Run Tests
```bash
cd "e:\APP Developer\Pixel Refine"

# Comprehensive test suite
python -m taichi_library.taichi_algorithm.aot_py.test_comprehensif

# Optical flow test
python -m taichi_library.taichi_algorithm.aot_py.test_optical_flow_aot
```

## Dependencies

### Core Dependencies
- **Taichi**: GPU compute framework (for JIT compilation only)
- **PySide6**: Qt6 Python bindings (UI)
- **OpenCV**: Computer vision (CPU fallback, image I/O)
- **NumPy**: Array operations
- **h5py**: HDF5 file handling

### GPU Requirements
- **Vulkan**: Primary backend (Windows GPU)
- **CUDA**: Secondary backend (NVIDIA GPU)
- **CPU**: Fallback backend (testing/debugging)
