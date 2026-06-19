# Build & Compilation

## AOT TCM Compilation

### Overview
Semua kernel Taichi dikompilasi menjadi modul TCM (Taichi Compiled Module) untuk runtime yang efisien tanpa JIT overhead.

### Compile Scripts Location
- **Path**: `taichi_library/taichi_algorithm/aot_py/`
- **Pattern**: `compile_*.py`

### General Compilation Flow

```bash
# Set JIT mode for compilation
$env:AOT_MODE="0"

# Run compile script
python -m taichi_library.taichi_algorithm.aot_py.compile_<module>_tcm
```

### Output Location
- **Path**: `taichi_library/taichi_algorithm/aot_tcm/`
- **Format**: `<module>_<arch>.tcm` (e.g., `farneback_flow_vulkan.tcm`)

## Module-Specific Compilation

### 1. Farneback Optical Flow

**Script**: `taichi_library/taichi_algorithm/aot_py/compile_farneback_tcm.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_farneback_tcm
```

**Output**: `taichi_library/taichi_algorithm/aot_tcm/farneback_flow_vulkan.tcm` (140.5 KB, 7 graphs)

**Graphs Compiled**:
- `poly_expansion_f32`
- `farneback_iteration`
- `farneback_multi_2`, `farneback_multi_3`, `farneback_multi_5`
- `farneback_upsample_flow`
- `farneback_clear_flow`

### 2. Horn-Schunck Optical Flow

**Script**: `taichi_library/taichi_algorithm/aot_py/compile_template_flow_tcm.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_template_flow_tcm
```

**Output**: `taichi_library/taichi_algorithm/aot_tcm/template_flow_vulkan.tcm` (43.2 KB)

**Graphs Compiled**:
- `hs_align_3layer_10` (10 Jacobi iterations)
- `hs_align_3layer_20` (20 Jacobi iterations)

### 3. Spatial Fusion (Ghost Rejection)

**Script**: `pixel_refine_desktop/enhance_stack/core/algorithm/denoising/spatial_core/similarity_taichi/compute_spatial.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python pixel_refine_desktop\enhance_stack\core\algorithm\denoising\spatial_core\similarity_taichi\compute_spatial.py
```

**Output**: `ui/data/aot_assets/spatial_vulkan.tcm`

**Graphs Compiled**:
- `precompute_gradients`
- `equalize_brightness`
- `phase1_coarse_analysis`
- `phase2_fine_analysis`
- `generate_fine_weights_4passes`
- `accumulate_spatial_merging`
- `fine_analysis_and_accumulate`

### 4. Remap (WarpAffine/WarpPerspective)

**Script**: `taichi_library/taichi_algorithm/aot_py/compile_remap_tcm.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_remap_tcm
```

**Output**: `taichi_library/taichi_algorithm/aot_tcm/remap_vulkan.tcm`

### 5. OFB (O-FAST-BRIEF)

**Script**: `taichi_library/taichi_algorithm/aot_py/compile_ofb_tcm.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_ofb_tcm
```

**Output**: `taichi_library/taichi_algorithm/aot_tcm/ofb_vulkan.tcm` (~103 KB)

### 6. A-KAZE

**Script**: `taichi_library/taichi_algorithm/aot_py/compile_akaze_tcm.py`

```bash
cd "e:\APP Developer\Pixel Refine"
$env:AOT_MODE="0"
python -m taichi_library.taichi_algorithm.aot_py.compile_akaze_tcm
```

**Output**: `taichi_library/taichi_algorithm/aot_tcm/akaze_vulkan.tcm` (~149 KB)

## Compilation Rules

### 1. Signature Registration
Daftarkan signature input secara eksplisit menggunakan `ti.graph.Arg`:

```python
# NDARRAY argument
sym_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype=ti.f32, ndim=2)

# SCALAR argument
sym_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)

# Multi-channel vector (use ndim=2 with vector field in Taichi)
sym_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype=ti.types.vector(3, ti.f32), ndim=2)
```

### 2. Graph Building

```python
module = ti.aot.Module(arch)
g = ti.graph.GraphBuilder()

# Dispatch kernels
g.dispatch(kernel_func, arg1, arg2, ...)

# Add graph to module
module.add_graph("graph_name", g.compile())

# Save to temp directory
tmp_dir = os.path.join(out_dir, "_tmp_module")
module.save(tmp_dir)

# Package as .tcm (zip)
tcm_path = os.path.join(out_dir, "module_vulkan.tcm")
with zipfile.ZipFile(tcm_path, 'w', zipfile.ZIP_DEFLATED) as tcm_zip:
    for root, dirs, files in os.walk(tmp_dir):
        for file in files:
            tcm_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), tmp_dir))

shutil.rmtree(tmp_dir)
```

### 3. Fallback CPU
Selalu sediakan fallback CPU untuk memastikan ketahanan pipeline jika driver Vulkan/CUDA target crash.

## Testing

### Run Comprehensive Test Suite
```bash
cd "e:\APP Developer\Pixel Refine"
python -m taichi_library.taichi_algorithm.aot_py.test_comprehensif
```

### Run Optical Flow Test
```bash
cd "e:\APP Developer\Pixel Refine"
python -m taichi_library.taichi_algorithm.aot_py.test_optical_flow_aot
```

## Architecture Support

| Architecture | Support | Notes |
|--------------|---------|-------|
| Vulkan | ✅ Primary | Windows GPU |
| CUDA | ✅ Secondary | NVIDIA GPU |
| CPU | ✅ Fallback | Testing/debugging |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AOT_MODE` | `1` | `0` = JIT (compile), `1` = AOT (production) |
| `PIXEL_REFINE_AOT_DEVICE` | `0` | GPU device ID |
| `VK_LOADER_DEBUG` | `error` | Vulkan loader debug level |
