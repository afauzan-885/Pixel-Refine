# Taichi GPU AOT Algorithms & Engine

This directory contains GPU-accelerated algorithms compiled via Taichi Ahead-of-Time (AOT) compiler into modular `.tcm` packages. These modules run natively on GPU backends (Vulkan, CUDA, CPU) via our modular C++ DLL execution engines.

---

## Architecture Overview

```
                        +----------------------------+
                        |     Python Applications     |
                        +----------------------------+
                                      |
                                      v
                        +----------------------------+
                        |  taichi_aot Engine Router  |
                        +----------------------------+
                                      |
                +---------------------+---------------------+
                |                     |                     |
                v                     v                     v
        [modular CPU]          [modular Vulkan]       [modular CUDA]
     (taichi_aot_cpu.dll)   (taichi_aot_vulkan.dll) (taichi_aot_cuda.dll)
                |                     |                     |
                +---------------------+---------------------+
                                      | (Loads AOT Modules)
                                      v
                             +------------------+
                             |   .tcm Modules   |
                             | (e.g. Can, MTB)  |
                             +------------------+
```

### Key Optimizations

1. **Dynamic Shape Context Refresh**:
   Graph cache automatically tracks the shape signatures of input arguments. If shape sizes transition (e.g., down scale pyramid levels), the driver reloads the compute graph dynamically to prevent C-API shape mismatch warnings.
2. **Two-Tier Buffer Pool**:
   VRAM allocations are rounded to $256 \times 256$ block tiles to prevent expensive GPU driver calls at runtime.
3. **Win32 Job Objects**:
   Prevents zombie child processes (such as `vulkaninfo.exe`) from leaking VRAM by automatically binding them to the parent process job.

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

Our comprehensive verification suite (`aot_py/test_comprehensif.py`) automatically profile:
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
