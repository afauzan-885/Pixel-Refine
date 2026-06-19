# Struktur Proyek dan Environment Configuration

**Sumber**: 5 memory files dari `.qoder/memories/.../project_environment_configuration/`

## Project Structure

### Root Directory
```
E:\APP Developer\Pixel Refine\
├── pixel_refine_desktop/          # Aplikasi desktop utama
│   ├── enhance_stack/             # Core processing stack
│   │   ├── core/                  # Core logic
│   │   │   ├── logic/             # Business logic
│   │   │   └── algorithm/         # Algorithm implementations
│   │   ├── views/                 # UI views
│   │   └── components/            # Reusable components
│   └── resources/                 # Static resources
├── taichi_library/                # Taichi GPU algorithms
│   ├── taichi_algorithm/          # Algorithm implementations
│   │   ├── aot_tcm/              # AOT compiled modules
│   │   ├── aot_py/               # AOT compilation scripts
│   │   └── *.py                  # Source files
│   └── taichi_aot/               # AOT engine
│       └── engine.py             # Single Source of Truth
├── test_algorithm/                # Test data
│   ├── IMG_20260606_073156Z.dng  # Test image 1
│   └── IMG_20260606_073157Z.dng  # Test image 2
└── pixel_refine_mobile/           # Aplikasi mobile
    └── ui/                        # Mobile UI
```

### Key Modules
- **Root**: `e:\APP Developer\Pixel Refine`
- **Main modules**: `pixel_refine_desktop\enhance_stack\`
- **Core logic**: `pixel_refine_desktop\enhance_stack\core\logic\`
- **Views**: `pixel_refine_desktop\enhance_stack\views\`
- **Components**: `pixel_refine_desktop\enhance_stack\components\`

## Auto VRAM Destruction System

### Overview
Backward-compatible safety feature yang mendeteksi dan memulihkan dari GPU issues.

### Fitur
- Detect dan recover dari **GPU freezes, hangs, deadlocks, error storms**
- Auto free semua VRAM dan terminate process
- **Zero changes** ke importing module (25+ files)
- **No API breaks**

### Module
```
taichi_aot/engine.py
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PIXEL_REFINE_HEARTBEAT_TIMEOUT` | 60s | Idle timeout threshold |
| `PIXEL_REFINE_OP_TIMEOUT` | 120s | Operation timeout |
| `PIXEL_REFINE_LOCK_TIMEOUT` | 30s | Lock contention timeout |
| `PIXEL_REFINE_ERROR_WINDOW` | 30s | Error rate measurement window |
| `PIXEL_REFINE_ERROR_THRESHOLD` | 5 | Max errors per window |
| `PIXEL_REFINE_AUTO_DESTROY` | "1" | Enable auto-destroy |

### 5-Layer Watchdog System

1. **Thread Death Detection**
   - Monitor thread liveness
   - Trigger cleanup jika thread mati

2. **Hung Operations Detection**
   - Monitor operation duration
   - Trigger jika melebihi `OP_TIMEOUT`

3. **Lock Contention Detection**
   - Monitor lock waiting time
   - Trigger jika melebihi `LOCK_TIMEOUT`

4. **Idle Freeze Detection**
   - Monitor activity heartbeat
   - Trigger jika idle melebihi `HEARTBEAT_TIMEOUT`

5. **Error Storm Detection**
   - Monitor error rate dalam window
   - Trigger jika errors melebihi `ERROR_THRESHOLD`

### Usage
```python
# Set environment variables sebelum import engine
import os
os.environ['PIXEL_REFINE_AUTO_DESTROY'] = '1'
os.environ['PIXEL_REFINE_HEARTBEAT_TIMEOUT'] = '60'

# Import engine (akan otomatis setup watchdog)
from taichi_aot import engine
```

## Real DNG Test Image Paths

### Lokasi Test Images
```
test_algorithm\IMG_20260606_073156Z.dng
test_algorithm\IMG_20260606_073157Z.dng
```

### Spesifikasi
- Format: DNG (Digital Negative)
- Kamera: Mobile device
- Resolusi: High-resolution RAW

## Resolution Handling Configuration

### Mode Average
```python
# _compute_work_resolution() DI-BYPASS
# Proses di original resolution
# Contoh: 4096×3072 tanpa downscaling
```

### Mode Similarity
```python
# _compute_work_resolution() AKTIF
# Downscaling untuk optimasi performa
# Contoh: >12.5MP images → ~4082×3060
```

### Algoritma-Specific Resolution Policy

| Algoritma | Resolusi | Alasan |
|-----------|----------|--------|
| Average | Original | Computational cost rendah |
| Similarity | Work resolution | Movement-robust, butuh optimasi |
| Median | Original | Pattern sama dengan Average |
| HFCD | Original | Single-pass, efisien |
