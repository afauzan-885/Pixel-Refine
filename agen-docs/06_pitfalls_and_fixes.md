# Known Pitfalls & Solutions

## Critical Bugs

### 1. i32 Popcount Bug (Vulkan/AOT)
**Penyebab**: Operator bitwise shift `>>` pada integer 32-bit bertanda (`ti.i32`) adalah **arithmetic shift** (menyebarkan sign bit). Untuk nilai i32 dengan bit-31 aktif, popcount **AKAN SALAH**.

**Fix**:
```python
# Isolasi bit-31 terpisah sebelum bit-trick popcount
sign_bit = (xor_val >> 31) & 1
c = ti.i32(xor_val & 0x7FFFFFFF)  # clear MSB -> selalu positif
c = c - ((c >> 1) & 0x55555555)   # sekarang benar
dist += int(c & 0x3F) + sign_bit
```

### 2. Compile Hang (AOT)
**Penyebab**: `ti.static(range(16)) × ti.static(range(9))` = 144 iterasi unrolled.

**Fix**: Hindari nested `ti.static` lebih dari ~32 iterasi total.

### 3. Float Scalar Overread Bug (`engine.py`)
**Penyebab**: Bug casting ctypes float 4-byte ke uint64 8-byte yang menyebabkan pembacaan derau memori (stack garbage).

**Fix**: Gunakan `struct.pack/unpack` untuk konversi bit pattern 32-bit yang aman.

### 4. FAST Detector Too Restrictive
**Penyebab**: Early-exit `count < 3` terlalu ketat.

**Fix**: Ubah ke `count < 2`.

### 5. UnicodeEncodeError (Windows)
**Penyebab**: Windows terminal default cp1252, bukan UTF-8.

**Fix**: 
- Jalankan dengan `python -X utf8`
- Atau set `PYTHONIOENCODING=utf-8`

## Common Pitfalls

### 6. cv2.imshow dari Background Task
**Penyebab**: Task runner tidak punya display context.

**Fix**: Gunakan `os.startfile()` atau simpan ke file saja.

### 7. cv2.remap() Requires np.float32 Coordinate Maps
**Penyebab**: OpenCV's `cv2.remap()` requires coordinate maps to be `np.float32` type.

**Fix**: 
```python
# Ensure float32 before remap
map_x = map_x.astype(np.float32)
map_y = map_y.astype(np.float32)
warped = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)
```

### 8. SSIM win_size Constraint
**Penyebab**: `skimage.metrics.structural_similarity` has `win_size` constraint.

**Fix**:
```python
from skimage.metrics import structural_similarity as ssim

h, w = img1.shape[:2]
win_size = min(7, min(h, w) // 2 * 2 + 1)  # Ensure odd and <= image size
if h < 7 or w < 7:
    win_size = 3 if min(h, w) >= 3 else 1

if img1.ndim == 3:
    score = ssim(img1, img2, channel_axis=2, win_size=win_size, data_range=1.0)
else:
    score = ssim(img1, img2, win_size=win_size, data_range=1.0)
```

### 9. MFDenoiser Boolean Indexing Dimension Mismatch
**Penyebab**: Work resolution scaling menyebabkan shape mismatch antara `sum_weight` dan `sum_img`.

**Fix**: 
```python
# Check dimensions before boolean indexing
work_h, work_w = sum_weight.shape[:2]
ref_h, ref_w = ctx.reference_float.shape[:2]
if (work_h, work_w) != (ref_h, ref_w):
    ref_resized = cv2.resize(ctx.reference_float, (work_w, work_h), interpolation=cv2.INTER_AREA)
else:
    ref_resized = ctx.reference_float
normalized[~valid_mask] = ref_resized[~valid_mask]
```

### 10. PowerShell Lacks `ls -la` Syntax
**Penyebab**: PowerShell tidak mendukung `ls -la` seperti bash.

**Fix**: Gunakan `Get-ChildItem` atau `ls` dengan PowerShell syntax:
```powershell
# PowerShell equivalent of ls -la
Get-ChildItem -Force
# or
ls -Force
```

## QML Pitfalls

### 11. QML static id Uniqueness Violation
**Penyebab**: `id` values must be globally unique across entire loaded object tree. Declaring static `id` inside reusable component causes duplication.

**Fix**: Replace static `id` with internal aliases:
```qml
// Wrong - causes duplication when component instantiated multiple times
ButtonBase.qml:
    id: button1

// Right - use internal aliases
ButtonBase.qml:
    id: _internalButton
```

### 12. QML implicitHeight is Read-Only
**Penyebab**: `implicitHeight` is a read-only property in QML.

**Fix**: Use `height` instead of `implicitHeight` for explicit sizing, or bind to a calculated value.

## Environment & Runtime

### 13. Vulkan Queue Lock
**Penyebab**: Race condition pembacaan VRAM antar pipeline.

**Fix**: Selalu panggil `engine.sync()` sebelum melepas buffer intermediate.

### 14. iGPU Memory Swapping
**Penyebab**: Laptop dengan iGPU (Shared VRAM) dapat mengalami throttling jika ukuran antrean paralel melebihi kapasitas memori fisik.

**Fix**: Batasi ukuran batch asinkron di bawah 10 gambar pada iGPU.

### 15. Thread vs Process
**Penyebab**: Multi-proses (`ProcessPoolExecutor`) spawn proses `python.exe` baru yang memuat konteks Vulkan terpisah.

**Fix**: Gunakan **Multi-threading** (`ThreadPoolExecutor`) untuk paralelisme yang aman.

## Debugging Tips

### Enable Profiling
```python
# Enable spatial fusion profiling
os.environ["PROFILE_SPATIAL"] = "1"
```

### Vulkan Debug
```python
# Enable Vulkan loader debug messages
os.environ["VK_LOADER_DEBUG"] = "all"  # or "error", "warn", "info"
```

### Taichi AOT Debug
```python
# Force JIT mode for debugging
os.environ["AOT_MODE"] = "0"
```
