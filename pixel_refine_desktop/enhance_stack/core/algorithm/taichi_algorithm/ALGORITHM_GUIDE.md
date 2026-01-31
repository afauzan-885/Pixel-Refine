# 🚀 Taichi GPU Algorithm Library - Master Technical Guide

Welcome to the definitive documentation for the `taichi_algorithm` library. This guide provides a detailed technical breakdown, practical usage examples, and **deep-dive logic explanations** for every script in this high-performance GPU pipeline.

---

## 🏗️ Core Architecture

### 1. `taichi_worker.py` (The Heart)
Taichi operates on a single CUDA context. To prevent context errors in multi-threaded apps, we use a serialized worker thread.
- **Use Case**: Running Taichi in complex GUI applications (Qt/PySide) where multiple threads might trigger GPU calls.
- **Internal Logic**: When a function is called via `@ti_thread`, it is added to a queue. a background daemon thread executes it sequentially. This ensures that all GPU allocations and kernel launches happen on the same thread that initialized Taichi.

### 2. `oom_guard.py` (The Shield)
Prevents GPU Out-Of-Memory (OOM) by automatically tiling large images (e.g., 8K).
- **High-Frequency Tiling**: Optimized for UI responsiveness. Uses smaller tiles (768-1536px) to ensure shorter GPU kernel launches, allowing the OS to refresh the screen between tiles.
- **Progress Callbacks**: Supports `progress_callback(fraction)` for real-time UI updates.
- **`execute_tiled()` logic**: 
    1. Calculates tile size based on available VRAM and responsiveness limits.
    2. Clips tiles with an **overlap** (padding).
    3. Stitches results while yielding control back to the OS.

### 2.1 UI Responsiveness (Non-Blocking)
The library is designed to keep the application fluid even during 100% GPU load:
- **Event-Loop Yielding**: When called from the Main Thread, `taichi_worker` uses a non-blocking poll. This allow the OS to process window events (drag, resize) without the app entering a "Not Responding" state.
- **Match C++ Feel**: Mirages the performance and responsiveness of native C++ backends.

---

---

## 🛠️ Module Breakdown & Usage Examples

### 3. `common.py` - The Engine Room
Manages the bridge between CPU (NumPy) and GPU (Taichi) and core channel operations.

- **Use Case**: Preparing images for GPU kernels, converting color spaces, or splitting BGR to process channels independently.
- **Example**:
```python
import taichi_algorithm as ta
gray = ta.cvtColor(img_np, ta.COLOR_BGR2GRAY)
b, g, r = ta.split(img_np)
```
- **💡 Technical Deep Dive**:
    *   **`BufferCache`**: Uses a `dict` to store allocated GPU resources. Key is `(shape, dtype)`. This eliminates the ~10ms allocation overhead in real-time loops.
    *   **Color Kernels**: Uses standard OpenCV weights (0.299, 0.587, 0.114) for fast parallel BGR/RGB to Gray conversion.

---

### 4. `pyramid.py` - Image Pyramids
Used for coarse-to-fine optical flow and multi-scale analysis.

- **Use Case**: Downsampling images to create search hierarchies for matching or upsampling flow fields between levels.
- **Example**:
```python
levels = ta.build_image_pyramid(img, n_levels=4)
new_flow = ta.upsample_flow(low_res_flow, target_h=1080, target_w=1920)
```
- **💡 Technical Deep Dive**:
    - **`_downsample_2x_kernel`**: Performs a 2x2 area average. Prevents aliasing by acting as a low-pass filter.
    - **`_upsample_flow_kernel`**: Bilinearly interpolates coordinates AND scales the flow vector magnitudes by the resolution ratio.

---

### 5. `warp.py` - Motion Compensation
Aligns one image to another using a displacement field (flow).

- **Use Case**: Frame interpolation, temporal alignment for burst denoising, or local motion compensation.
- **Example**:
```python
warped = ta.warp_image_gpu(src_img, flow_field, guidance=ref_img)
```
- **💡 Technical Deep Dive**:
    - **`sample_bicubic`**: uses a 4x4 neighborhood with Catmull-Rom splines for sub-pixel precision.
    - **`_warp_kernel_guided`**: Applies a **Joint Bilateral Weight** using a guidance image. If neighborhood pixels in the guidance are similar, their flow vectors are weighted higher, forcing boundaries to align with edges.

---

### 6. `gaussian.py` - Optimized Blur
High-performance implementation of Gaussian convolution.

- **Use Case**: Denoising, anti-aliasing, or creating spatial gradients for pre-alignment.
- **Example**:
```python
blurred = ta.gaussian(img, ksize=5, sigmaX=1.2)
```
- **💡 Technical Deep Dive**:
    - **Separable Pass**: Instead of $O(K^2)$, it launches two 1D kernels ($O(K)$). Horizontally blurs, then vertically blurs the intermediate result.
    - **Sigma Logic**: Automatically calculates sigma from kernel size using the OpenCV standard formula.

---

### 7. `bilateral_grid.py` - Edge-Preserving Filter

- **Use Case**: Smoothing skin or surfaces without blurring critical edges (eyelashes, hair, object boundaries).
- **Example**:
```python
smooth = ta.bilateral(img, d=9, sigmaColor=75, sigmaSpace=75)
```
- **💡 Technical Deep Dive**:
    - Uses a **3D Bilateral Grid** (X, Y, Intensity).
    1. **Splat**: Project 2D pixels into 3D.
    2. **Blur**: 3D Gaussian blur on the grid.
    3. **Slice**: Sample back to 2D.
    - Result: Real-time edge-preserving smoothing.

---

## 🚀 Deployment Pattern: Zero-Copy Pipeline

Avoid downloading to NumPy between steps. **Stay on the GPU**.

```python
import taichi_algorithm as ta

field = ta.common.ensure_taichi_field(img)
# Chain 3 operations on GPU without any download
res = ta.resize(field, (1000, 1000))
res = ta.gaussian(res, ksize=7)
res = ta.absdiff(res, prev_gpu) 

# Download once at the end
final = res.to_numpy()
```

---

## 📜 Full API Summary

| Module | Use Case | Common Call |
| :--- | :--- | :--- |
| `common.py` | Color/Channels | `ta.cvtColor`, `ta.split`, `ta.merge` |
| `pyramid.py` | Hierarchies | `ta.build_image_pyramid` |
| `warp.py` | Motion warping | `ta.warp_image_gpu` |
| `gaussian.py` | Efficient Blur | `ta.gaussian(src, ksize, sigmaX)` |
| `bilateral_grid.py`| High-end Denoise | `ta.bilateral(src, d, sc, ss)` |
| `interpolation.py` | Quality Scaling | `ta.resize(src, (w, h))` |

---
*Technical documentation finalized for Pixel Refine GPU Stack.*
