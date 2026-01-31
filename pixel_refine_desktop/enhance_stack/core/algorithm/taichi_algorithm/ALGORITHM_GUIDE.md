# 🚀 Taichi GPU Algorithm Library - Technical Guide

Welcome to the comprehensive documentation for the `taichi_algorithm` library. This guide provides a detailed technical breakdown of every script, kernel, and architectural decision used to build this high-performance GPU pipeline.

---

## 🏗️ Architectural Overview

The library is designed for **Zero-Copy Performance** and **Thread Safety**.

### 1. `taichi_worker.py` (The Heart)
Taichi operates on a single CUDA context. To prevent `CUDA_ERROR_INVALID_CONTEXT` in multi-threaded environments (like GUI apps), we use a serialized worker thread.

- **`_TaichiWorker`**: A singleton thread that manages the life cycle of Taichi.
- **`@ti_thread`**: A decorator used on every public API. It ensures that whenever you call a function, it is dispatched to the worker thread and waited upon.
  
> [!IMPORTANT]
> Never call Taichi kernels directly from different threads. Always wrap them in `@ti_thread`.

### 2. `oom_guard.py` (The Shield)
Taichi reserves GPU memory. For massive images (e.g., 8K or ultra-high bit depth), we might hit VRAM limits.
- **`should_tile()`**: Automatically detects if an image size exceeds the safety threshold for the current hardware.
- **`execute_tiled()`**: Splits a large image into overlapping tiles, processes them on the GPU, and stitches them back seamlessly.

---

## 🛠️ Core Utilities

### 3. `common.py` (Memory & Channels)
This is the most critical script for efficiency.
- **`BufferCache`**: A pool-based memory manager. Instead of allocating new GPU fields every time (which is slow), it reuses existing buffers of the same shape/type.
- **`ensure_taichi_field()`**: The "Smart Uploader". It takes NumPy or Taichi arrays and ensures they are in a format kernels can read, with minimal overhead.
- **OpenCV Style APIs**:
    - **`split()` / `merge()`**: GPU-native channel separation.
    - **`cvtColor()`**: Supports `BGR2GRAY`, `RGB2GRAY`, `GRAY2RGB` with native GPU kernels.
    - **`absdiff()`**: Element-wise absolute difference on GPU.

---

## 🖼️ Interpolation & Resizing

### 4. `bilinear_interpolation.py`
High-speed bilinear resizing.
- **`_bilinear_resize_kernel_3d`**: A specialized kernel that handles multi-channel images (RGB/RGBA) in a single GPU pass, avoiding per-channel loops.

### 5. `bicubic_interpolation.py`
High-quality resizing using Catmull-Rom splines.
- **`cubic_hermite()`**: The mathematical foundation for smooth gradients.
- **`bicubic_resize()`**: Better than bilinear for upscaling, producing fewer artifacts.

---

## 🌫️ Image Filtering (The Filter Suite)

### 6. `gaussian.py` (Gaussian Blur)
A sophisticated, separable implementation.
- **Two-Pass Optimization**: Instead of an $O(K^2)$ 2D convolution, it runs a horizontal pass then a vertical pass ($O(K)$), significantly increasing speed.
- **OpenCV Parity**: Automatically calculates `sigma` from `ksize` (or vice versa) using the standard CV2 formula.
- **Multi-channel Support**: Native GPU kernels for 1-channel and 3-channel images.

### 7. `box_filter.py` (Mean Blur)
Uniformly distributes pixel values.
- **Kernels**: Includes `2d`, `3d`, and `flow_kernel` (for optical flow denoising).
- **Auto-radius**: Handles kernel sizes consistently.

### 8. `median_filter.py`
Non-linear filter excellent for salt-and-pepper noise removal.
- **Sorting Kernel**: Uses a 3x3 or 5x5 window sorting algorithm executed in parallel across every pixel.

---

## 📐 Gradients & Specialized Logic

### 9. `gradients.py`
Foundational for edge detection.
- **`sobel()`**: Calculates horizontal (`dx`) and vertical (`dy`) derivatives.
- **`laplacian()`**: Calculates the second derivative (excellent for sharpening).

### 10. `ransac.py` (Robust Flow)
- **`ransac_flow_cleanup()`**: A high-speed GPU implementation of Random Sample Consensus tailored for optical flow. It removes outlier vectors that don't fit the global motion model.

### 11. `bilateral_grid.py`
Edge-preserving smoothing.
- **Algorithm**: Uses a 3D Bilateral Grid (Space + Range) to perform bilateral filtering in $O(N)$ time instead of $O(N \cdot K^2)$. This is the "God Tier" of filters for photo enhancement.

---

## 🚀 How to Use (GPU Pipeline Pattern)

To get maximum speed, **stay on the GPU**:

```python
import taichi_algorithm as ta

# 1. Upload once
img_gpu = ta.common.ensure_taichi_field(my_numpy_img)

# 2. Chain operations (NO DOWNLOADS HERE)
tmp = ta.resize(img_gpu, (1280, 720))
tmp = ta.gaussian(tmp, ksize=5)
tmp = ta.cvtColor(tmp, ta.COLOR_RGB2GRAY)

# 3. Download only at the very end
final_result = tmp.to_numpy()
```

---

## 📜 Documentation Summary Table

| Script | Responsibility | Key API |
| :--- | :--- | :--- |
| `__init__.py` | Public Interface | `resize`, `gaussian`, `box`, `median` |
| `common.py` | Buffer Management | `ensure_taichi_field`, `cvtColor`, `split` |
| `taichi_worker.py` | Thread Safety | `@ti_thread` |
| `oom_guard.py` | Memory Safety | `execute_tiled` |
| `gaussian.py` | High Quality Blur | `gaussian(src, ksize, sigmaX)` |
| `bilateral_grid.py`| Edge Preservation | `bilateral(src, d, sigmaColor, sigmaSpace)` |

---
*Documentation generated for Pixel Refine GPU Stack.*
