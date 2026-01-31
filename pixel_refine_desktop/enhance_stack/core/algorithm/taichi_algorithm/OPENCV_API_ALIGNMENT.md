# OpenCV API Comparison & Alignment

## 🔍 OpenCV vs Proposed API Comparison

### **Channel Operations**

| Operation | OpenCV | Current (Proposed) | Recommendation |
|-----------|--------|-------------------|----------------|
| **Extract channel** | `cv2.extractChannel(src, ch)` | `ta.get_channel(img, ch)` | ⚠️ Should be `ta.extract_channel()` |
| **Insert channel** | `cv2.insertChannel(src, dst, ch)` | `ta.set_channel(img, data, ch)` | ⚠️ Should be `ta.insert_channel()` |
| **Split channels** | `cv2.split(img)` → `[B, G, R]` | ❌ Not available | ✅ Should add `ta.split()` |
| **Merge channels** | `cv2.merge([B, G, R])` → `img` | ❌ Not available | ✅ Should add `ta.merge()` |

### **Image Copy**

| Operation | OpenCV | Current (Proposed) | Recommendation |
|-----------|--------|-------------------|----------------|
| **Copy image** | `img.copy()` or `np.copy(img)` | `ta.copy(img)` | ✅ Good! Matches NumPy |

### **Type Conversion**

| Operation | OpenCV | Current (Proposed) | Recommendation |
|-----------|--------|-------------------|----------------|
| **Convert type** | `img.astype(np.float32)` | `ta.to_field(arr)` | ⚠️ Different purpose |
| **To NumPy** | N/A (already NumPy) | `ta.to_numpy(field)` | ✅ Good for Taichi |

### **Filtering Operations**

| Operation | OpenCV | Current API | Status |
|-----------|--------|-------------|--------|
| **Gaussian blur** | `cv2.GaussianBlur(img, ksize, sigmaX)` | `ta.gaussian(img, ksize, sigmaX)` | ✅ Perfect match! |
| **Median blur** | `cv2.medianBlur(img, ksize)` | `ta.median(img, ksize)` | ✅ Perfect match! |
| **Box filter** | `cv2.boxFilter(img, -1, ksize)` | `ta.box(img, ksize)` | ✅ Good (simpler) |
| **Bilateral** | `cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)` | `ta.bilateral(img, d, sigmaColor, sigmaSpace)` | ✅ Perfect match! |
| **Sobel** | `cv2.Sobel(img, -1, dx, dy, ksize)` | `ta.sobel(img, dx, dy, ksize)` | ✅ Good (simpler) |
| **Laplacian** | `cv2.Laplacian(img, -1)` | `ta.laplacian(img)` | ✅ Good (simpler) |

### **Resize & Interpolation**

| Operation | OpenCV | Current API | Status |
|-----------|--------|-------------|--------|
| **Resize** | `cv2.resize(img, dsize, interpolation)` | `ta.resize(img, dsize, interpolation)` | ✅ Perfect match! |
| **INTER_NEAREST** | `cv2.INTER_NEAREST` | `ta.INTER_NEAREST` | ✅ Perfect match! |
| **INTER_LINEAR** | `cv2.INTER_LINEAR` | `ta.INTER_LINEAR` | ✅ Perfect match! |
| **INTER_CUBIC** | `cv2.INTER_CUBIC` | `ta.INTER_CUBIC` | ✅ Perfect match! |

---

## ✅ Revised Recommendations (OpenCV-Aligned)

### **1. Channel Operations - Follow OpenCV Exactly**

```python
# ✅ OpenCV-style (RECOMMENDED)
import taichi_algorithm as ta

# Extract single channel
green = ta.extract_channel(rgb, ch=1)  # Like cv2.extractChannel

# Insert single channel
ta.insert_channel(green_modified, rgb, ch=1)  # Like cv2.insertChannel

# Split all channels
b, g, r = ta.split(rgb)  # Like cv2.split → returns tuple

# Merge channels
rgb = ta.merge([b, g, r])  # Like cv2.merge
```

**OpenCV Reference:**
```python
import cv2

# Extract
green = cv2.extractChannel(rgb, 1)

# Insert
cv2.insertChannel(green, rgb, 1)

# Split
b, g, r = cv2.split(rgb)

# Merge
rgb = cv2.merge([b, g, r])
```

---

### **2. Complete API Alignment**

| Category | OpenCV Pattern | Taichi Algorithm API | Status |
|----------|----------------|---------------------|--------|
| **Filtering** | `cv2.gaussianBlur()` | `ta.gaussian()` | ✅ Aligned |
| **Filtering** | `cv2.medianBlur()` | `ta.median()` | ✅ Aligned |
| **Filtering** | `cv2.bilateralFilter()` | `ta.bilateral()` | ✅ Aligned |
| **Resize** | `cv2.resize()` | `ta.resize()` | ✅ Aligned |
| **Gradients** | `cv2.Sobel()` | `ta.sobel()` | ✅ Aligned |
| **Gradients** | `cv2.Laplacian()` | `ta.laplacian()` | ✅ Aligned |
| **Channels** | `cv2.extractChannel()` | `ta.extract_channel()` | ✅ Should add |
| **Channels** | `cv2.insertChannel()` | `ta.insert_channel()` | ✅ Should add |
| **Channels** | `cv2.split()` | `ta.split()` | ✅ Should add |
| **Channels** | `cv2.merge()` | `ta.merge()` | ✅ Should add |
| **Copy** | `img.copy()` | `ta.copy()` | ✅ Aligned (NumPy-style) |

---

## 🎯 Final Proposed API (OpenCV-Compatible)

### **High-Level Channel APIs**

```python
import taichi_algorithm as ta

# === Extract Channel (OpenCV-style) ===
green = ta.extract_channel(rgb_img, ch=1)
# Equivalent to: cv2.extractChannel(rgb_img, 1)

# === Insert Channel (OpenCV-style) ===
ta.insert_channel(green_modified, rgb_img, ch=1)
# Equivalent to: cv2.insertChannel(green_modified, rgb_img, 1)

# === Split Channels (OpenCV-style) ===
b, g, r = ta.split(rgb_img)
# Equivalent to: b, g, r = cv2.split(rgb_img)

# === Merge Channels (OpenCV-style) ===
rgb_new = ta.merge([b, g, r])
# Equivalent to: rgb_new = cv2.merge([b, g, r])

# === Copy (NumPy-style) ===
img_copy = ta.copy(img)
# Equivalent to: img_copy = img.copy()
```

---

## 📊 Implementation Priority (OpenCV-Aligned)

### **High Priority - Core Channel Operations:**

1. **`ta.split(img)`** - Split into channels
   ```python
   def split(img):
       """Split multi-channel image into separate channels (OpenCV-compatible)"""
       # Returns tuple of channels: (ch0, ch1, ch2, ...)
   ```

2. **`ta.merge(channels)`** - Merge channels
   ```python
   def merge(channels):
       """Merge separate channels into multi-channel image (OpenCV-compatible)"""
       # Input: list/tuple of channels
       # Returns: merged image
   ```

3. **`ta.extract_channel(img, ch)`** - Extract single channel
   ```python
   def extract_channel(img, ch):
       """Extract single channel (OpenCV-compatible)"""
       # Returns: single channel image
   ```

4. **`ta.insert_channel(src, dst, ch)`** - Insert single channel
   ```python
   def insert_channel(src, dst, ch):
       """Insert channel into multi-channel image (OpenCV-compatible, in-place)"""
       # Modifies dst in-place
   ```

---

## 🔄 Migration from Current Proposal

### **Before (My Initial Proposal):**
```python
# ❌ Not OpenCV-compatible
green = ta.get_channel(rgb, ch=1)      # Different from OpenCV
rgb_new = ta.set_channel(rgb, green, ch=1)  # Different from OpenCV
```

### **After (OpenCV-Aligned):**
```python
# ✅ OpenCV-compatible
green = ta.extract_channel(rgb, ch=1)  # Same as cv2.extractChannel
ta.insert_channel(green, rgb, ch=1)    # Same as cv2.insertChannel

# ✅ Additional OpenCV functions
b, g, r = ta.split(rgb)                # Same as cv2.split
rgb = ta.merge([b, g, r])              # Same as cv2.merge
```

---

## 📝 Complete OpenCV-Style API Reference

```python
import taichi_algorithm as ta

# === Image I/O & Basic Operations ===
img_copy = ta.copy(img)                # NumPy-style copy

# === Channel Operations (OpenCV-style) ===
channels = ta.split(img)               # Split → tuple of channels
img = ta.merge(channels)               # Merge channels → image
channel = ta.extract_channel(img, ch)  # Extract single channel
ta.insert_channel(src, dst, ch)        # Insert channel (in-place)

# === Filtering (OpenCV-style) ===
blurred = ta.gaussian(img, ksize, sigmaX)
blurred = ta.median(img, ksize)
blurred = ta.bilateral(img, d, sigmaColor, sigmaSpace)
blurred = ta.box(img, ksize)

# === Resize & Interpolation (OpenCV-style) ===
resized = ta.resize(img, dsize, interpolation=ta.INTER_CUBIC)

# === Gradients (OpenCV-style) ===
grad = ta.sobel(img, dx, dy, ksize)
lap = ta.laplacian(img)

# === Point-wise Sampling (Taichi-specific) ===
value = ta.sample_at_bicubic(img, x, y)   # High quality
value = ta.sample_at_bilinear(img, x, y)  # Fast
```

---

## ✅ Summary

### **Current Status:**
- ✅ **Filtering APIs** - Already OpenCV-aligned (`gaussian`, `median`, `bilateral`)
- ✅ **Resize API** - Already OpenCV-aligned (`resize`, `INTER_*`)
- ✅ **Gradient APIs** - Already OpenCV-aligned (`sobel`, `laplacian`)
- ❌ **Channel APIs** - NOT OpenCV-aligned (missing `split`, `merge`, wrong names)

### **Required Changes:**
1. ✅ Add `ta.split(img)` - OpenCV-compatible
2. ✅ Add `ta.merge(channels)` - OpenCV-compatible
3. ✅ Rename `get_channel` → `extract_channel` - OpenCV-compatible
4. ✅ Rename `set_channel` → `insert_channel` - OpenCV-compatible
5. ✅ Keep `ta.copy(img)` - NumPy-style (acceptable)

### **Benefits:**
- 🎯 **Familiar to OpenCV users** - Easy migration
- 📚 **Consistent naming** - Follows industry standard
- 🔄 **Drop-in replacement** - Similar API surface
- 📖 **Better documentation** - Can reference OpenCV docs

**Recommendation: Follow OpenCV naming exactly for channel operations!** ✅
