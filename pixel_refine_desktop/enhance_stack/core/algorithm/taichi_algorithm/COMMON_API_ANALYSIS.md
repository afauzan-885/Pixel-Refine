# Common.py API Analysis & Recommendations

## 📋 Current API Status

### **Low-Level Taichi Functions** (Internal Use)
These are `@ti.func` decorated - used inside Taichi kernels:

| Current Name | Type | Exposed? | Recommendation |
|--------------|------|----------|----------------|
| `cubic_weight(x)` | `@ti.func` | ❌ Internal | ✅ Keep as-is (low-level) |
| `bilinear_at(img, x, y)` | `@ti.func` | ❌ Internal | ✅ Keep as-is (used by `sample_at_bilinear`) |
| `bicubic_at(img, x, y)` | `@ti.func` | ❌ Internal | ✅ Keep as-is (used by `sample_at_bicubic`) |
| `sample_green_normalized(...)` | `@ti.func` | ❌ Internal | ⚠️ Very specific, keep internal |
| `bilinear_at_3ch(...)` | `@ti.func` | ❌ Internal | ⚠️ Redundant? (covered by `sample_at_bilinear`) |

### **Buffer Management Functions** (Utility)

| Current Name | Purpose | Recommendation |
|--------------|---------|----------------|
| `get_temp_buffer(shape, dtype, provider)` | Get temp GPU buffer | ✅ Good name |
| `release_temp_buffer(buf)` | Release buffer | ✅ Good name |
| `cleanup_cache()` | Clear buffer cache | ✅ Good name |
| `ensure_taichi_field(arr, ...)` | Convert to Taichi field | ⚠️ Too long, suggest `to_field()` |
| `to_numpy_if_needed(field, was_numpy)` | Convert to NumPy | ⚠️ Confusing logic, suggest `to_numpy()` |

### **Channel Manipulation Functions** (Kernels)

| Current Name | Purpose | Exposed? | Recommendation |
|--------------|---------|----------|----------------|
| `_copy_kernel(src, dst)` | Copy field | ❌ Private | ⚠️ Could expose as `copy()` |
| `_extract_channel_kernel(src, dst, ch)` | Extract channel | ❌ Private | ⚠️ Could expose as `extract_ch()` |
| `_insert_channel_kernel(src, dst, ch)` | Insert channel | ❌ Private | ⚠️ Could expose as `insert_ch()` |
| `copy_field(src, dst)` | Wrapper for copy | ✅ Exposed | ✅ Good, but could be `copy()` |
| `extract_channel(src, dst, ch)` | Wrapper for extract | ✅ Exposed | ⚠️ Could be `extract_ch()` |
| `insert_channel(src, dst, ch)` | Wrapper for insert | ✅ Exposed | ⚠️ Could be `insert_ch()` |

---

## 🎯 Recommendations

### **1. Rename for Brevity & Clarity**

#### **Buffer Management:**
```python
# ❌ OLD: Too verbose
ensure_taichi_field(arr, dtype=ti.f32)
to_numpy_if_needed(field, was_numpy=True)

# ✅ NEW: Concise & clear
to_field(arr, dtype=ti.f32)  # or as_field()
to_numpy(field, auto=True)   # auto-detect if conversion needed
```

#### **Channel Operations:**
```python
# ❌ OLD: Too long
extract_channel(src, dst, channel=1)
insert_channel(src, dst, channel=1)

# ✅ NEW: Shorter
extract_ch(src, dst, ch=1)  # or get_ch()
insert_ch(src, dst, ch=1)   # or set_ch()
```

---

### **2. Add High-Level APIs**

#### **Missing High-Level Channel APIs:**

```python
# Current: Low-level, requires pre-allocated dst
dst = ti.ndarray(dtype=ti.f32, shape=(h, w))
extract_channel(src, dst, channel=1)

# ✅ Proposed: High-level, auto-allocates
green_channel = ta.get_channel(rgb_img, ch=1)  # Returns extracted channel
rgb_img = ta.set_channel(rgb_img, green_modified, ch=1)  # Returns modified image
```

#### **Missing High-Level Copy API:**

```python
# Current: Low-level
dst = ti.ndarray(...)
copy_field(src, dst)

# ✅ Proposed: High-level
dst = ta.copy(src)  # Auto-allocates and returns copy
```

---

## 📊 Proposed API Hierarchy

### **Level 1: High-Level (User-Facing)**
```python
import taichi_algorithm as ta

# Channel operations
green = ta.get_channel(rgb, ch=1)           # Extract channel (auto-alloc)
rgb_new = ta.set_channel(rgb, green, ch=1)  # Insert channel (returns new)
rgb_copy = ta.copy(rgb)                     # Copy image (auto-alloc)

# Type conversion
field = ta.to_field(numpy_array)            # NumPy → Taichi
array = ta.to_numpy(taichi_field)           # Taichi → NumPy
```

### **Level 2: Mid-Level (Advanced Users)**
```python
from taichi_algorithm import common

# Buffer management
buf = common.get_temp_buffer((512, 512), ti.f32)
common.release_temp_buffer(buf)
common.cleanup_cache()

# In-place operations (pre-allocated dst)
common.extract_ch(src, dst, ch=1)  # Renamed from extract_channel
common.insert_ch(src, dst, ch=1)   # Renamed from insert_channel
common.copy_field(src, dst)
```

### **Level 3: Low-Level (Internal)**
```python
# Taichi @ti.func - used inside kernels only
common.bilinear_at(img, x, y)
common.bicubic_at(img, x, y)
common.cubic_weight(x)
```

---

## ✅ Specific Changes Needed

### **1. Rename Functions (Backward Compatible)**

```python
# Add shorter aliases, keep old names for compatibility

# Buffer management
def to_field(arr, dtype=None, shape=None, provider=None):
    """Convert to Taichi field (alias for ensure_taichi_field)"""
    return ensure_taichi_field(arr, dtype, shape, provider)

def to_numpy(field, auto=True, out=None):
    """Convert to NumPy (simplified to_numpy_if_needed)"""
    return to_numpy_if_needed(field, auto, out)

# Channel operations
def extract_ch(src, dst, ch):
    """Extract channel (alias for extract_channel)"""
    return extract_channel(src, dst, ch)

def insert_ch(src, dst, ch):
    """Insert channel (alias for insert_channel)"""
    return insert_channel(src, dst, ch)
```

### **2. Add High-Level APIs**

```python
def get_channel(img, ch):
    """
    Extract channel from multi-channel image (auto-allocates output).
    
    Args:
        img: Input image (H, W, C) - NumPy or Taichi field
        ch: Channel index (0, 1, 2, etc.)
    
    Returns:
        Extracted channel (H, W) - same type as input
    
    Example:
        >>> green = ta.get_channel(rgb_img, ch=1)
    """
    # Implementation with auto-allocation
    pass

def set_channel(img, channel_data, ch):
    """
    Insert channel into multi-channel image (returns new image).
    
    Args:
        img: Input image (H, W, C)
        channel_data: Channel to insert (H, W)
        ch: Channel index
    
    Returns:
        Modified image (H, W, C) - same type as input
    
    Example:
        >>> rgb_new = ta.set_channel(rgb_img, green_modified, ch=1)
    """
    # Implementation
    pass

def copy(img):
    """
    Copy image (auto-allocates output).
    
    Args:
        img: Input image - NumPy or Taichi field
    
    Returns:
        Copy of image - same type as input
    
    Example:
        >>> img_copy = ta.copy(img)
    """
    # Implementation
    pass
```

---

## 🎨 Usage Examples

### **Before (Current API):**
```python
# Verbose and requires manual allocation
import taichi as ti
from taichi_algorithm import common

# Extract green channel
h, w = rgb.shape[:2]
green = ti.ndarray(dtype=ti.f32, shape=(h, w))
common.extract_channel(rgb, green, channel=1)

# Modify and insert back
# ... process green ...
common.insert_channel(rgb, green, channel=1)
```

### **After (Proposed High-Level API):**
```python
import taichi_algorithm as ta

# Simple and intuitive
green = ta.get_channel(rgb, ch=1)

# Modify
green_enhanced = ta.gaussian(green, ksize=5, sigmaX=2.0)

# Insert back
rgb_new = ta.set_channel(rgb, green_enhanced, ch=1)
```

---

## 📈 Priority Recommendations

### **High Priority:**
1. ✅ Add `get_channel()` - Very useful for channel manipulation
2. ✅ Add `set_channel()` - Complements get_channel
3. ✅ Add `copy()` - Common operation
4. ✅ Add `to_field()` alias - Shorter than `ensure_taichi_field`
5. ✅ Simplify `to_numpy()` - Current logic is confusing

### **Medium Priority:**
6. ⚠️ Add `extract_ch()` / `insert_ch()` aliases - Shorter names
7. ⚠️ Expose in `__init__.py` - Make high-level APIs accessible

### **Low Priority:**
8. 📝 Document all functions - Add comprehensive docstrings
9. 📝 Create usage guide - Examples for common use cases

---

## 🎯 Summary

**Current Issues:**
- ❌ No high-level APIs for common operations (channel manipulation, copy)
- ❌ Function names too verbose (`ensure_taichi_field`, `to_numpy_if_needed`)
- ❌ Requires manual buffer allocation for simple tasks
- ❌ Not exposed in main `__init__.py`

**Proposed Solutions:**
- ✅ Add high-level APIs: `get_channel()`, `set_channel()`, `copy()`
- ✅ Add shorter aliases: `to_field()`, `to_numpy()`, `extract_ch()`, `insert_ch()`
- ✅ Auto-allocation in high-level APIs
- ✅ Expose in `__init__.py` for easy access
- ✅ Maintain backward compatibility

**Benefits:**
- 🚀 Easier to use for common tasks
- 📝 More intuitive API naming
- 🎯 Consistent with other high-level APIs (resize, gaussian, etc.)
- 🔄 Backward compatible - old code still works
