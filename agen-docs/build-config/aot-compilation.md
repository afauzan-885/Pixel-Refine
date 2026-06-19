# AOT Compilation dan TCM Generation

**Sumber**: 6 memory files dari `.qoder/memories/.../project_build_configuration/`

## AOT (Ahead-of-Time) Compilation Overview

AOT compilation menghasilkan **TCM (Taichi Compiled Module)** files yang bisa di-load tanpa Taichi JIT runtime.

## Compilation Scripts

### Farneback AOT
```bash
# Script: taichi_library/taichi_algorithm/aot_py/compile_farneback_tcm.py
# Mode: AOT_MODE=0
python -m taichi_algorithm.aot_py.compile_farneback_tcm

# Output: farneback_flow_vulkan.tcm (140.5 KB, 7 graphs)
```

### Analysis Suite AOT
```bash
# Script: taichi_library/taichi_algorithm/aot_py/compile_analysis_suite_tcm.py
# Compile: color_convert, otsu, clahe, canny, hough, guided_filter
python -m taichi_algorithm.aot_py.compile_analysis_suite_tcm

# Output: analysis_suite_vulkan.tcm
```

### Template Flow AOT (Horn-Schunck)
```bash
# Script: taichi_library/taichi_algorithm/aot_py/compile_template_flow_tcm.py
python -m taichi_algorithm.aot_py.compile_template_flow_tcm

# Output: template_flow_vulkan.tcm (43.2 KB)
```

## TCM Module Requirements

### Required Modules

| # | Module | File | Size | Graphs |
|---|--------|------|------|--------|
| 1 | CLAHE | clahe_vulkan.tcm | TBD | TBD |
| 2 | NLM | nlm_vulkan.tcm | TBD | TBD |
| 3 | Canny | canny_vulkan.tcm | TBD | TBD |
| 4 | Guided Filter | guided_filter_vulkan.tcm | TBD | TBD |
| 5 | Hough | hough_vulkan.tcm | TBD | TBD |
| 6 | Color Convert | color_convert_vulkan.tcm | TBD | TBD |
| 7 | Otsu | otsu_vulkan.tcm | TBD | TBD |
| 8 | Inpaint | inpaint_vulkan.tcm | TBD | TBD |
| 9 | Seamless Clone | seamless_clone_vulkan.tcm | TBD | TBD |

### Existing Modules

| Module | File | Size | Graphs |
|--------|------|------|--------|
| Farneback | farneback_flow_vulkan.tcm | 140.5 KB | 7 |
| Horn-Schunck | template_flow_vulkan.tcm | 43.2 KB | 8 |

## Compilation Process

### Step 1: Write Taichi Kernels
```python
import taichi as ti

@ti.kernel
def my_algorithm(input: ti.types.ndarray(), output: ti.types.ndarray()):
    for i, j in input:
        # Algorithm logic
        output[i, j] = input[i, j] * 2
```

### Step 2: Define AOT Graphs
```python
my_graph = ti.Graph()

# Add kernel to graph
my_graph.add_node("process", my_algorithm)

# Define input/output
my_graph.add_image("input", ...)
my_graph.add_image("output", ...)

# Finalize
my_graph.compile()
```

### Step 3: Compile to TCM
```python
# Set AOT_MODE=0
import os
os.environ['AOT_MODE'] = '0'

# Run compilation
ti.init(arch=ti.vulkan)
my_graph.compile()

# Output: my_algorithm_vulkan.tcm
```

## Test Configuration

### Comprehensive Test Suite
```python
# test_comprehensif.py
def run_jit_algorithm_tests():
    # 1. AOT tests
    # 2. JIT tests (AOT_MODE=0)
    # 3. Pipeline stress testing
```

### Test Coverage Requirements

| Test Type | Coverage | Metrics |
|-----------|----------|---------|
| Synthetic accuracy | 100% | SSIM, MAE vs OpenCV |
| Bit depth | 8-bit, 16-bit | Both required |
| Channel support | 1ch, 3ch | Both required |
| Edge cases | All algorithms | Zero tolerance |

### MAE Thresholds

| Algorithm | MAE Threshold | Notes |
|-----------|---------------|-------|
| YCrCb | < 3.0 | Color conversion |
| CLAHE | < 30.0 | Contrast enhancement |
| Canny | < 5.0 | Edge detection |
| Guided Filter | < 10.0 | Smoothing |

## C++ Backend Compatibility

### Guarantee
- `taichi_aot_engine.cpp` **100% backward compatible** dengan existing modules
- Tidak ada function signatures berubah
- Python ctypes bindings identik

### Python-Side Improvements
- 16 improvements ke `engine.py`
- Fully compatible dengan existing `taichi_aot_engine.dll`
- **Tidak perlu** C++ modifications atau DLL recompilation

## DNG Demosaicing Configuration

### Algorithm Options
```python
import rawpy

# Option 1: Hamilton (default, higher quality)
raw = rawpy.imread('image.dng')
rgb = raw.postprocess(demosaic_algorithm='hamilton')

# Option 2: Bilinear (faster, lower quality)
rgb = raw.postprocess(demosaic_algorithm='bilinear')
```

### Supported Formats
- DNG (Digital Negative)
- NEF (Nikon)
- ARW (Sony)
- CR2, CR3 (Canon)
- RAF (Fuji)
- RW2 (Panasonic)

## Environment Variables

### Compilation
```bash
# Set AOT mode
set AOT_MODE=0

# Set Taichi arch
set TI_ARCH=vulkan

# Enable debug (optional)
set TI_DEBUG=1
```

### Runtime
```bash
# Engine path
set TAICHI_AOT_ENGINE_PATH=taichi_aot\engine.dll

# Cache directory
set TAICHI_CACHE_DIR=.taichi_cache
```
