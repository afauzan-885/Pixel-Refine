# Bicubic Interpolation API - Usage Guide

## 📚 Overview

The `taichi_algorithm` library provides **3 levels** of bicubic interpolation APIs:

### 1️⃣ **High-Level: Full Image Resize** ✨ (Recommended for most users)
```python
import taichi_algorithm as ta

# Resize entire image with bicubic interpolation
upscaled = ta.resize(image, dsize=(1024, 1024), interpolation=ta.INTER_CUBIC)
```

**Use Cases:**
- Image upscaling/downscaling
- Preprocessing pipelines
- Thumbnail generation with high quality

---

### 2️⃣ **Mid-Level: Point-wise Sampling** 🎯 (For custom transformations)
```python
import taichi_algorithm as ta

# Sample single pixel at fractional coordinates
value = ta.sample_at(image, x=10.5, y=20.3)

# Sample specific channel (e.g., green channel for alignment)
green_val = ta.sample_at(rgb_image, x=10.5, y=20.3, channel=1)
```

**Use Cases:**
- Optical flow warping
- Subpixel refinement in image alignment
- Custom geometric transformations
- Feature tracking

**Example: Warping with Optical Flow**
```python
import taichi_algorithm as ta
import numpy as np

def warp_image_simple(src, flow):
    """Warp image using optical flow with bicubic interpolation"""
    h, w = src.shape[:2]
    result = np.zeros_like(src)
    
    for y in range(h):
        for x in range(w):
            # Get flow vector
            dx, dy = flow[y, x]
            
            # Sample at warped coordinates
            new_x = x + dx
            new_y = y + dy
            
            if 0 <= new_x < w and 0 <= new_y < h:
                result[y, x] = ta.sample_at(src, new_x, new_y)
    
    return result
```

---

### 3️⃣ **Low-Level: Catmull-Rom Spline** 🔧 (For advanced users)
```python
import taichi_algorithm as ta

# Direct access to cubic Hermite interpolation function
# Used internally by sample_at() and resize()
result = ta.cubic_hermite(A, B, C, D, t)
```

**Use Cases:**
- Custom interpolation kernels
- Research and experimentation
- Performance-critical code that needs direct control

**Parameters:**
- `A, B, C, D`: Four consecutive sample points
- `t`: Interpolation parameter (0.0 to 1.0)
- Returns: Interpolated value using Catmull-Rom spline

---

## 🎨 Complete Examples

### Example 1: High-Quality Image Upscaling
```python
import taichi_algorithm as ta
import numpy as np
from PIL import Image

# Load image
img = np.array(Image.open("input.jpg")).astype(np.float32)

# Upscale 2x with bicubic interpolation
upscaled = ta.resize(img, dsize=(img.shape[1]*2, img.shape[0]*2), 
                     interpolation=ta.INTER_CUBIC)

# Save result
Image.fromarray(upscaled.astype(np.uint8)).save("upscaled.jpg")
```

### Example 2: Subpixel Refinement in Alignment
```python
import taichi_algorithm as ta

def refine_alignment(ref_image, comp_image, initial_offset):
    """Refine alignment offset to subpixel precision"""
    x0, y0 = initial_offset
    best_sad = float('inf')
    best_offset = (x0, y0)
    
    # Search in 0.1 pixel increments around initial offset
    for dx in np.arange(-1.0, 1.0, 0.1):
        for dy in np.arange(-1.0, 1.0, 0.1):
            # Sample at fractional coordinates
            test_x = x0 + dx
            test_y = y0 + dy
            
            sampled = ta.sample_at(comp_image, test_x, test_y)
            sad = abs(ref_image[y0, x0] - sampled)
            
            if sad < best_sad:
                best_sad = sad
                best_offset = (test_x, test_y)
    
    return best_offset
```

### Example 3: Custom Rotation with Bicubic
```python
import taichi_algorithm as ta
import numpy as np

def rotate_image(img, angle_degrees):
    """Rotate image with bicubic interpolation"""
    h, w = img.shape[:2]
    angle_rad = np.radians(angle_degrees)
    
    # Center of rotation
    cx, cy = w / 2, h / 2
    
    result = np.zeros_like(img)
    
    for y in range(h):
        for x in range(w):
            # Rotate coordinates back to source
            dx = x - cx
            dy = y - cy
            
            src_x = dx * np.cos(-angle_rad) - dy * np.sin(-angle_rad) + cx
            src_y = dx * np.sin(-angle_rad) + dy * np.cos(-angle_rad) + cy
            
            # Sample with bicubic interpolation
            if 0 <= src_x < w and 0 <= src_y < h:
                result[y, x] = ta.sample_at(img, src_x, src_y)
    
    return result
```

---

## 🚀 Performance Tips

1. **Use GPU-accelerated `resize()` for full images** - Much faster than looping with `sample_at()`
2. **Batch operations when possible** - Minimize CPU-GPU transfers
3. **For warping, use the built-in `warp_image_gpu()`** - Optimized kernel implementation

---

## 📊 API Comparison

| API | Speed | Flexibility | Use Case |
|-----|-------|-------------|----------|
| `resize(..., INTER_CUBIC)` | ⚡⚡⚡ Fast | Low | Full image resize |
| `sample_at(img, x, y)` | ⚡⚡ Medium | High | Custom transformations |
| `cubic_hermite(A,B,C,D,t)` | ⚡ Slow | Very High | Research/custom kernels |

---

## 🔗 Related Functions

- `ta.resize()` - Main resize function (supports INTER_LINEAR, INTER_CUBIC)
- `ta.sample_at()` - Point-wise bicubic sampling
- `ta.cubic_hermite()` - Low-level spline function
- `common.bicubic_at()` - Internal Taichi kernel (use `sample_at()` instead)

---

## ✅ Migration Guide

### Before (Confusing low-level API):
```python
from enhance_stack.core.algorithm.taichi_algorithm import common

# Hard to understand what this does
value = common.bicubic_at(img, x, y)
```

### After (Clear high-level API):
```python
import taichi_algorithm as ta

# Clear and intuitive
value = ta.sample_at(img, x, y)
```

---

**Happy coding! 🎉**
