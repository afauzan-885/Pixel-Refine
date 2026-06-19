# Common Pitfalls (Jebakan yang Sering Terjadi)

**Sumber**: 9 memory files dari `.qoder/memories/.../common_pitfalls_experience/`

## 1. cv2.remap() Coordinate Type
**Masalah**: `cv2.remap()` membutuhkan koordinat `np.float32`, bukan `float64` atau `int`

**Solusi**:
```python
# Salah
map_x = np.array([...], dtype=np.float64)  # ✗
map_y = np.array([...], dtype=np.int32)     # ✗

# Benar
map_x = np.array([...], dtype=np.float32)  # ✓
map_y = np.array([...], dtype=np.float32)  # ✓
```

## 2. MFDenoiser Boolean Indexing Dimension Mismatch
**Masalah**: Boolean indexing bisa gagal dimensi karena work resolution scaling

**Solusi**: Pastikan tensor dimensions sejajar sebelum indexing
```python
# Pastikan work_res dan full_res dimensions konsisten
assert mask.shape == tensor.shape[:2], "Dimension mismatch!"
result = tensor[mask]
```

## 3. PowerShell Syntax
**Masalah**: PowerShell TIDAK mendukung syntax `ls -la` (Unix style)

**Solusi**:
```powershell
# Salah
ls -la  # ✗

# Benar
Get-ChildItem -Force           # ✓
dir -Force                     # ✓
ls -Force                      # ✓
```

## 4. QML implicitHeight
**Masalah**: `implicitHeight` adalah READ-ONLY property

**Solusi**:
```qml
// Salah
Column {
    implicitHeight: 200  // ✗ Tidak bisa di-set
}

// Benar
Column {
    height: 200  // ✓ Gunakan height biasa
}
```

## 5. QML Static ID Uniqueness
**Masalah**: Duplikat ID dalam scope yang sama menyebabkan `QQmlApplicationEngine` gagal load

**Solusi**:
```qml
// Salah - duplikat ID
Item { id: contentCol }  // ✓
Item { id: contentCol }  // ✗ Duplikat!

// Benar - ID unik
Item { id: contentCol }
Item { id: contentCol2 }
// atau gunakan dynamic IDs
```

## 6. SSIM win_size Constraint
**Masalah**: SSIM `window_size` punya constraint terhadap ukuran input

**Solusi**:
```python
import cv2

# Pastikan window_size sesuai
height, width = image.shape[:2]
win_size = min(height, width, 7)  # Batasi sesuai ukuran gambar
ssim_score = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED)
```

## 7. Taichi Kernel External Array Type
**Masalah**: Taichi kernel external array argument harus tipe yang benar

**Solusi**:
```python
import taichi as ti

@ti.kernel
def process(field: ti.types.ndarray()):
    for i in field:
        field[i] *= 2

# Pastikan tipe data sesuai
arr = np.array([...], dtype=np.float32)  # ✓ Sesuai kernel
process(arr)
```

## 8. Windows Python Unicode Output
**Masalah**: Windows Python Unicode console output memerlukan environment variable

**Solusi**:
```powershell
# Set environment variable sebelum menjalankan script
$env:PYTHONIOENCODING = "utf-8"
python script.py

# atau
set PYTHONIOENCODING=utf-8
python script.py
```

## 9. Taichi Kernel Array Argument Type Mismatch
**Masalah**: Taichi kernel external array argument type harus sesuai antara Python dan Taichi

**Solusi**:
```python
import taichi as ti
import numpy as np

@ti.kernel
def process(field: ti.types.ndarray(dtype=ti.f32)):
    for i in field:
        field[i] = ti.cast(field[i], ti.f32)

# Pastikan numpy array dtype sesuai
arr = np.array([...], dtype=np.float32)  # ✓
process(arr)
```

## Best Practices Checklist

- [ ] Selalu gunakan `np.float32` untuk cv2.remap() coordinates
- [ ] Verifikasi tensor dimensions sebelum boolean indexing
- [ ] Gunakan PowerShell native commands, bukan Unix syntax
- [ ] Gunakan `height` bukan `implicitHeight` di QML
- [ ] Pastikan ID QML unik dalam setiap scope
- [ ] Batasi SSIM window_size sesuai ukuran gambar
- [ ] Sesuaikan dtype numpy array dengan Taichi kernel requirements
- [ ] Set `PYTHONIOENCODING=utf-8` di Windows untuk Unicode output
- [ ] Periksa tipe data array sebelum passing ke Taichi kernel
