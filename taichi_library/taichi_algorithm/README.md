# Taichi GPU AOT Algorithms & Engine

> **Current documentation:** read [`AOT_BACKEND_MATRIX.md`](../AOT_BACKEND_MATRIX.md)
> first. It is the canonical developer/AI handoff for target-qualified
> runtime selection, memory/cache policy, block capability, build matrix, and
> verification gates. This file is a short algorithm index and historical
> usage overview, not a second backend contract.

This directory contains algorithms compiled through Taichi Ahead-of-Time
(AOT) into target-qualified `.tcm` packages. The same public Python call is
dispatched to CPU, CUDA, Vulkan, OpenGL, or GLES according to the selected
target. The native bridge, C API runtime, and TCM archive must belong to the
same backend/OS/architecture/ABI profile.

---

## Architecture Overview

```
                        +----------------------------+
                        |     Python Applications     |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        | taichi_aot Runtime Router  |
                        +----------------------------+
                                      |
                +---------------------+---------------------+
                |                     |                     |
                v                     v                     v
        [CPU/CUDA]              [Vulkan/OpenGL]        [GLES/ARM]
      target bridge            target bridge          target bridge
                |                     |                     |
                +---------------------+---------------------+
                                      | (Loads AOT Modules)
                                      v
                             +------------------+
                             |   .tcm Modules   |
                             | (target .tcm)     |
                             +------------------+
```

### Key runtime guarantees

1. **Shape and lifecycle protection**: graph and buffer metadata are checked
   before dispatch; reinitialization invalidates stale wrappers.
2. **Allocation and result caching**: full-frame buffers and validated tile
   records have independent bounded caches with pressure-based eviction.
3. **Target-qualified dispatch**: an archive is never relabeled as another
   platform, vendor, or ABI.
4. **Safe fallback**: an unqualified or failed native/tile path returns to the
   same-backend full-frame/reference path while preserving the public API.

For exact environment variables, target IDs, dtype policy, and build/test
commands, use the canonical matrix document linked above instead of copying
old examples from this index.

## Maintained source layout

All reusable algorithm implementations and public AOT dispatchers are kept in
this package:

* `aot_api/` — cross-family public AOT dispatch (`research.py` and
  `research_pipeline.py`) plus compatibility shims.
* algorithm-family directories (`alignment/`, `demosaicing/`, `denoising/`,
  `image_processing/`, `optical_flow/`, and others) — kernels, public family
  APIs, and their `compile_*.py` scripts in one place. JPEG is maintained in
  `compression/jpeg_aot.py`; the former `aot_api/jpeg.py` is only a shim.
* `aot_py/` — shared compiler orchestration and build tooling; executable
  validation lives in `aot_py/tests/`.
* `aot_tcm/` — target-qualified compiled modules. These are artifacts, not
  Python algorithm source.

`taichi_library.taichi_aot` remains the stable import path, but is now a thin
runtime façade. New algorithms should be added under `taichi_algorithm` and
exported through `aot_api`; do not add implementation files to the runtime
package.

For a family-local compiler, run it through its package path so imports and
artifact roots are deterministic, for example:

```powershell
python -m taichi_library.taichi_algorithm.feature_matching.compile_akaze_tcm
python -m taichi_library.taichi_algorithm.optical_flow.compile_lucas_kanade_tcm
python -m taichi_library.taichi_algorithm.demosaicing.compile_hamilton_tcm
python -m taichi_library.taichi_algorithm.image_processing.compile_analysis_suite_tcm
```

Use `aot_py/compile_aot_backend_suite.py` for target-qualified batch builds;
it resolves each job to the colocated compiler automatically. Shared
orchestration (`compile_common_tcm.py` and `compile_research_tcm.py`)
intentionally remains in `aot_py` because it spans multiple families.

### Block pre-communication (Lucas--Kanade)

The dense Lucas--Kanade block path uses
`optical_flow/lucas_kanade_batch.py` and the
`lucas_kanade_batch` target-qualified TCM job. Tiles with the same halo shape
are packed into one `(batch, height, width)` dispatch. A scatter graph writes
only each tile core into one resident `(H, W, 2)` atlas, so the host performs
one readback per cold invocation instead of one readback per tile. The memory
governor caps the atlas at 256 MiB (or one quarter of the resident limit) and
admits at most two in-flight batches only when the device-pool budget can hold
them; otherwise it retains the one-fence bounded path. Cache records may store
either a full halo tile or a core-only atlas slice and are validated by shape.

Useful diagnostics are returned by `taichi_aot.get_last_block_execution()`:
`readback_strategy` is `atlas` for a cold atlas invocation and
`resident_output_bytes` reports its resident footprint. Set
`PIXEL_REFINE_AOT_DISABLE_LK_ATLAS=1` or
`PIXEL_REFINE_AOT_DISABLE_LK_BATCH_PIPELINE=1` only for controlled regression
comparisons. OpenGL remains on its established host/reference LK path until a
driver-produced native batch artifact passes the target validator.

The same resident-core sink is available as the `common` graph
`scatter_core_f32_3d`. It is used by the generic Block Matching and Farneback
GPU-tile paths, preserving their existing kernels while consolidating tile
readback into one atlas readback per cold invocation.

---

## List of AOT Algorithms

The following algorithms are compiled and available in `aot_tcm/`:

*   **Geometric**: Resize (Bicubic, Bilinear, Area, Nearest), Image Pyramids.
*   **Filters**: Gaussian Blur, Box Filter, Median Filter, Joint Bilateral Filter, Joint Bilateral Upsample.
*   **Gradients**: Sobel, Laplacian, Canny Edge Detector.
*   **Denoising & Restoration**: BM3D Denoising, Bilateral Grid, Inpainting, Non-Local Means (NLM).
*   **Color & Threshold**: Color conversions (BGR/RGB/YCrCb/HSV), Otsu Thresholding, CLAHE.
*   **Alignment & Matching**: NCC Alignment, RANSAC outlier cleanup, OFB, AKAZE, Find Homography, Warp Perspective, and MTB (Median Threshold Bitmap).

---

## Latency & Memory Profiling

Our comprehensive verification suite (`aot_py/tests/test_comprehensif.py`) automatically profile:
1. **Latency (ms)**: High-resolution computational time.
2. **RAM delta (MB)**: Memory footprint using `psutil`.
3. **Active VRAM (MB)**: Physically allocated GPU memory.

---

## End-to-End Example: Optical Flow Alignment & Warping

Here is how to load images, calculate optical flow on GPU, build displacement coordinate maps, and warp/align images entirely on the GPU:

```python
import numpy as np
import cv2
from taichi_library import taichi_aot

def align_images(ref_path, target_path, output_path):
    # 1. Load Grayscale float32 inputs in range [0, 255]
    ref_gray = cv2.imread(ref_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
    tgt_gray = cv2.imread(target_path, cv2.IMREAD_GRAYSCALE).astype(np.float32)
    tgt_color = cv2.imread(target_path).astype(np.float32) / 255.0

    # 2. Upload to GPU VRAM
    ref_gpu = taichi_aot.InputArray(ref_gray)
    tgt_gpu = taichi_aot.InputArray(tgt_gray)
    tgt_color_gpu = taichi_aot.InputArray(tgt_color, is_vector=True)

    # 3. Compute GPU Farneback Optical Flow
    flow_gpu = taichi_aot.farneback_flow(ref_gpu, tgt_gpu, num_levels=3, win_size=15, num_iters=3, return_gpu=True)

    # 4. Smooth flow vectors to remove noise
    flow_smooth = taichi_aot.smooth_flow_gpu(flow_gpu, sigma=1.5, kernel_size=5)

    # 5. Warp/Remap Target image using flow maps
    aligned_gpu = taichi_aot.remap_with_flow(tgt_color_gpu, flow_smooth, ref_gray.shape[1], ref_gray.shape[0])

    # 6. Save result to disk
    aligned_np = (aligned_gpu.to_numpy() * 255.0).astype(np.uint8)
    cv2.imwrite(output_path, aligned_np)

    # 7. Release VRAM
    ref_gpu.release()
    tgt_gpu.release()
    tgt_color_gpu.release()
    flow_gpu.release()
    flow_smooth.release()
    aligned_gpu.release()

if __name__ == "__main__":
    align_images("reference.png", "target.png", "aligned.png")
```
