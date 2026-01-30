# 🎯 Point-wise Sampling API - Quick Reference

## API Naming Convention

Untuk clarity dan consistency, semua point-wise sampling functions sekarang menggunakan nama yang spesifik:

| Function | Algorithm | Speed | Quality | Use Case |
|----------|-----------|-------|---------|----------|
| `ta.sample_at_bicubic(img, x, y)` | Bicubic (Catmull-Rom) | ⚡⚡ Fast | ⭐⭐⭐ Excellent | High-quality warping, subpixel alignment |
| `ta.sample_at_bilinear(img, x, y)` | Bilinear | ⚡⚡⚡ Fastest | ⭐⭐ Good | Real-time warping, fast transforms |
| `ta.sample_at(img, x, y)` | Alias for bicubic | ⚡⚡ Fast | ⭐⭐⭐ Excellent | Backward compatibility |

---

## ✅ Recommended Usage

### **Explicit Algorithm (Recommended)**

```python
import taichi_algorithm as ta

# Bicubic - High quality
value = ta.sample_at_bicubic(img, x=10.5, y=20.3)

# Bilinear - Fast
value = ta.sample_at_bilinear(img, x=10.5, y=20.3)
```

**Benefits:**
- ✅ Clear which algorithm is being used
- ✅ Consistent naming with `sample_at_bilinear`
- ✅ Easy to switch between algorithms

### **Backward Compatible (Still Works)**

```python
# This still works (alias for sample_at_bicubic)
value = ta.sample_at(img, x=10.5, y=20.3)
```

---

## 📝 Complete Examples

### **1. Image Warping - Choose Your Speed**

```python
def warp_image(src, flow, quality='high'):
    """Warp image with selectable quality"""
    h, w = src.shape[:2]
    result = np.zeros_like(src)
    
    # Choose sampling method
    if quality == 'high':
        sample_func = ta.sample_at_bicubic  # Best quality
    else:
        sample_func = ta.sample_at_bilinear  # Fastest
    
    for y in range(h):
        for x in range(w):
            new_x = x + flow[y, x, 0]
            new_y = y + flow[y, x, 1]
            
            if 0 <= new_x < w and 0 <= new_y < h:
                result[y, x] = sample_func(src, new_x, new_y)
    
    return result

# Usage
warped_hq = warp_image(img, flow, quality='high')    # Bicubic
warped_fast = warp_image(img, flow, quality='fast')  # Bilinear
```

### **2. Subpixel Alignment**

```python
def refine_alignment(ref, comp, offset):
    """Refine alignment with bicubic sampling"""
    x0, y0 = offset
    best_sad = float('inf')
    best_pos = (x0, y0)
    
    # Use bicubic for accuracy
    for dx in np.arange(-1.0, 1.0, 0.1):
        for dy in np.arange(-1.0, 1.0, 0.1):
            sampled = ta.sample_at_bicubic(comp, x0 + dx, y0 + dy)
            sad = abs(ref[y0, x0] - sampled)
            
            if sad < best_sad:
                best_sad = sad
                best_pos = (x0 + dx, y0 + dy)
    
    return best_pos
```

### **3. Multi-channel Sampling**

```python
# Sample all channels
rgb_value = ta.sample_at_bicubic(rgb_img, x=10.5, y=20.3)
# Returns: np.array([R, G, B])

# Sample specific channel (e.g., green)
green_value = ta.sample_at_bicubic(rgb_img, x=10.5, y=20.3, channel=1)
# Returns: float (green channel value)

# Grayscale
gray_value = ta.sample_at_bicubic(gray_img, x=10.5, y=20.3)
# Returns: float
```

---

## 🔄 Migration Guide

### **From Old API**

```python
# ❌ OLD: Ambiguous name
value = ta.sample_at(img, x, y)

# ✅ NEW: Explicit algorithm
value = ta.sample_at_bicubic(img, x, y)  # Bicubic
# OR
value = ta.sample_at_bilinear(img, x, y)  # Bilinear (faster)
```

### **Backward Compatibility**

```python
# ✅ Still works (alias)
value = ta.sample_at(img, x, y)  # Calls sample_at_bicubic internally

# But prefer explicit naming:
value = ta.sample_at_bicubic(img, x, y)
```

---

## 📊 Performance Comparison

```python
import time
import taichi_algorithm as ta

img = np.random.rand(1024, 1024, 3).astype(np.float32)

# Benchmark bilinear
start = time.time()
for i in range(10000):
    val = ta.sample_at_bilinear(img, 512.5, 512.5)
bilinear_time = time.time() - start

# Benchmark bicubic
start = time.time()
for i in range(10000):
    val = ta.sample_at_bicubic(img, 512.5, 512.5)
bicubic_time = time.time() - start

print(f"Bilinear: {bilinear_time:.3f}s")
print(f"Bicubic:  {bicubic_time:.3f}s")
print(f"Speedup:  {bicubic_time/bilinear_time:.2f}x")
```

**Typical Results:**
- Bilinear: ~0.05s (baseline)
- Bicubic: ~0.12s (2.4x slower, but much better quality)

---

## 🎯 When to Use Each

### **Use `sample_at_bicubic` when:**
- ✅ Quality is more important than speed
- ✅ Upscaling or enlarging images
- ✅ Subpixel refinement in alignment
- ✅ Photo/image processing workflows
- ✅ Accuracy is critical

### **Use `sample_at_bilinear` when:**
- ✅ Speed is critical (real-time processing)
- ✅ Preview/draft quality is acceptable
- ✅ Processing video streams
- ✅ Downscaling (bilinear is good enough)
- ✅ Batch processing large datasets

---

## 📚 Full API Reference

### `ta.sample_at_bicubic(img, x, y, channel=None)`

**Parameters:**
- `img`: Input image (H, W) or (H, W, C)
- `x`: X coordinate (fractional, e.g., 10.5)
- `y`: Y coordinate (fractional, e.g., 20.3)
- `channel`: Optional channel index (0, 1, 2, etc.)

**Returns:**
- Single value (grayscale or specific channel)
- Array of values (all channels if channel=None)

**Algorithm:** Bicubic (Catmull-Rom spline, 4x4 neighborhood)

---

### `ta.sample_at_bilinear(img, x, y, channel=None)`

**Parameters:**
- `img`: Input image (H, W) or (H, W, C)
- `x`: X coordinate (fractional)
- `y`: Y coordinate (fractional)
- `channel`: Optional channel index

**Returns:**
- Single value or array (same as bicubic)

**Algorithm:** Bilinear (2x2 neighborhood)

---

### `ta.sample_at(img, x, y, channel=None)`

**Alias for:** `sample_at_bicubic`

**Note:** Kept for backward compatibility. Prefer explicit `sample_at_bicubic` for clarity.

---

**Happy sampling! 🚀**
