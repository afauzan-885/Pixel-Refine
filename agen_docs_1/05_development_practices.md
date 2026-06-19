# Development Practices & Coding Rules

## Core Principles

> **Prinsip utama**: Tulis kode sesederhana mungkin, hindari boilerplate dan sintaks tidak perlu.

## 1. Code Simplicity Rules

### 1.1 Hindari Lambda untuk Koneksi Signal

**Salah:**
```python
window.bridge.tool_requested.connect(
    lambda name: state.navigate_to(name)
)
```

**Benar:**
```python
window.bridge.tool_requested.connect(state.navigate_to)
```

### 1.2 Hindari Lambda untuk Function Reference

**Salah:**
```python
state.register_page("MFDenoiser", lambda b: build_workspace_page(b, "MFDenoiser"))
```

**Benar:**
```python
state.register_page("MFDenoiser", build_workspace_page)
```

### 1.3 Gunakan Fungsi Terpisah untuk Callback

**Salah:**
```python
window.bridge.tool_requested.connect(
    lambda name: print(f"[Mobile] Tool selected: {name}")
)
```

**Benar:**
```python
def on_tool_selected(tool_name):
    print(f"[Mobile] Tool selected: {tool_name}")

window.bridge.tool_requested.connect(on_tool_selected)
```

### 1.4 Hindari Komentar Berlebihan

**Salah:**
```python
# Register pages
state.register_page("Home", build_home_page)

# Connect navigation
window.bridge.tool_requested.connect(state.navigate_to)

# Show home page
window.setCentralWidget(build_home_page(window.bridge))
```

**Benar:**
```python
state.register_page("Home", build_home_page)
window.bridge.tool_requested.connect(state.navigate_to)
window.setCentralWidget(build_home_page(window.bridge))
```

### 1.5 Hindari Docstring Berlebihan

**Salah:**
```python
def build_workspace_page(bridge, tool_type: str = "MFDenoiser") -> Container:
    """
    Build the Workspace Page layout.

    Args:
        bridge: AppBridge instance
        tool_type: Current tool type

    Returns:
        Container with all workspace components
    """
```

**Benar:**
```python
def build_workspace_page(bridge) -> Container:
    """Build the Workspace Page layout."""
```

### 1.6 Hindari Duplikasi Code

**Salah:**
```python
# File memiliki dua blok kode yang sama
import sys
from PySide6.QtWidgets import QApplication
...
import sys
from PySide6.QtWidgets import QApplication
```

**Benar:**
```python
# Hanya satu blok import
import sys
from PySide6.QtWidgets import QApplication
```

### 1.7 Simpulkan Variabel yang Sering Dipakai

**Salah:**
```python
title_card = Card(title="Settings")
title_card.set_body_content("App preferences and configuration")
layout.add_widget(title_card)
```

**Benar:**
```python
layout.add_widget(Card(title="Settings"))
```

## 2. Taichi & Backend Rules

### 2.1 `engine.py` — Single Source of Truth
- **DILAR** memodifikasi `engine.py` tanpa persetujuan eksplisit dari user
- Semua algoritma baru yang menggunakan backend ini harus mematuhi aturan dan perilaku yang ditetapkan oleh `engine.py`

### 2.2 GenericUILibrary
- Semua pembuatan atau pengeditan komponen UI **wajib** menggunakan pustaka/framework di path `resources/GenericUILibrary`
- Jangan membuat styles kustom ad-hoc secara manual
- Jika ingin membuat UI baru yang bersifat kustom, sebisa mungkin tambahkan komponen tersebut ke dalam skrip yang ada di dalam path `resources/GenericUILibrary`

### 2.3 Nested `ti.static`
- Batasi unrolling statis loop
- Nested loop statis dengan iterasi total `> 32` akan menyebabkan LLVM backend macet (compile hang)
- Hindari nested `ti.static` lebih dari ~32 iterasi total

### 2.4 Memory Synchronize
- **Selalu** panggil `engine.sync()` sebelum mengeksekusi `.release()` pada buffer sementara
- Wajib digunakan sebelum melepas buffer intermediate antar pipeline untuk mencegah race condition

### 2.5 Sub-pixel Refinement
- Gunakan fitting kuadratik paraboloid 2D pada peta skor 3x3 di sekitar keypoint
- Pastikan pembagi (`2.0 * s_center - s_left - s_right`) di atas threshold aman (e.g. `1e-5`)
- Batasi offset hasil fitting dalam rentang `[-0.5, 0.5]`

### 2.6 Rotation Invariance (Centroid Angle)
- Orientasi pola BRIEF **wajib** dihitung dinamis menggunakan intensitas momen centroid local patch
- Gunakan `ti.atan2(m01, m10)` alih-alih sudut statis `0.0`

### 2.7 Multi-scale Image Pyramid
- Untuk menjaga ketangguhan pada resolusi rendah (di bawah 240px):
  - Batasi tingkat pyramid (levels) secara dinamis sesuai resolusi input
  - Skala parameter `grid_size`, `margin`, dan `threshold` di setiap level
  - Lakukan *fused* median filter + Gaussian pre-pass secara terpisah

### 2.8 A-KAZE Non-Linear Diffusion (FED)
- Gunakan koefisien konduktivitas Perona-Malik II berbasis magnitudo gradien filter Scharr
- Skema difusi FED wajib menggunakan ukuran langkah τ_j siklik yang bervariasi
- Integrasikan `pack_matches_kernel` untuk menyatukan pengemasan keypoint/matches di GPU

## 3. UI & Styling Rules

### 3.1 Style Consistency
- Dilarang menulis style custom secara ad-hoc menggunakan `.setStyleSheet()` yang menimpa warna dasar sistem
- Gunakan variabel kelas/mixins bawaan untuk menjaga harmoni palet warna

### 3.2 Centering Absolut Layout
- Untuk memposisikan widget di tengah secara absolut:
  - Bagi layout header utama menjadi 3 sub-layout QHBoxLayout (`left`, `center`, `right`)
  - Masukkan ke layout utama dengan stretch factor setara `(1, 1, 1)`

### 3.3 Eager Incremental Loading
- Selalu batasi jumlah visualisasi thumbnail yang dimuat pertama kali di halaman grid
- Limit ke 10 item dikombinasikan dengan `SkeletonLoader` sebelum memuat sisa gambar

### 3.4 Real-time Settings & Translation
- Daftarkan parent container utama menggunakan `@live_update` decorator
- Pemanggilan pemicu secara otomatis melakukan *cascade* pembaruan secara rekursif
- Gunakan `language_config.reload_language(lang_str)` secara langsung dengan string bahasa baru

### 3.5 Compact Sizing on Action Buttons
- Tombol aksi batch wajib disusutkan ukurannya sebesar 50%
- Set tinggi tetap menjadi `22px` dan padding `2px 4px` dengan ukuran font `8pt`

## 4. QML Mobile Rules

### 4.1 Environment Variable
- **Selalu** setel `os.environ["QT_QUICK_CONTROLS_STYLE"] = "Basic"` sebelum meng-import modul PySide6
- Ini mencegah engine QML memuat gaya native secara default

### 4.2 Parenting Konteks QML
- **Jangan** menggunakan `.setParent(quick_widget.engine())` karena engine internal Qt Quick dapat merekonstruksi instansnya
- Gunakan `.setParent(quick_widget)` (pada `QQuickWidget` / `QQuickView`)

### 4.3 ID Uniqueness
- `id` values **wajib** globally unique across entire loaded object tree
- Declaring static `id` inside reusable component causes duplication
- Solution: replace static `id` with internal aliases (e.g., `id: _internalButton`)

### 4.4 Touch Scrolling
- Use `Flickable` with `contentHeight: childrenRect.height` for touch-enabled scrolling
- `childrenRect.height` is read-only, cannot be assigned

## 5. Build & Compilation Rules

### 5.1 TCM Compilation
- Daftarkan signature input secara eksplisit menggunakan `ti.graph.Arg`
- Vektor multi-channel (seperti RGB `vec3` float) didefinisikan sebagai `ArgKind.NDARRAY` dengan `ndim=2`
- Selalu sediakan fallback CPU untuk memastikan ketahanan pipeline

### 5.2 AOT Mode
- Production: `AOT_MODE=1` (default) — menggunakan pre-compiled TCM modules
- Development: `AOT_MODE=0` — menggunakan Taichi JIT untuk testing/debugging

### 5.3 Vulkan Device Lock
- Untuk menghindari instansiasi `vulkaninfo.exe` berulang:
  ```python
  os.environ["PIXEL_REFINE_AOT_DEVICE"] = "0"  # Bypass scan
  os.environ["VK_LOADER_DEBUG"] = "error"      # Suppress warnings
  ```
