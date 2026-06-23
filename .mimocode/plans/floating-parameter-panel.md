# Floating Parameter Panel Overlay

## Context

Saat ini parameter alignment dan denoising ditampilkan di bagian bawah `LeftPanel` sebagai `AlgorithmPanel` yang mengambil ruang layout secara vertikal. User ingin parameter panel ini berubah menjadi **floating overlay** yang mengambang di atas area display (seperti tombol "Mulai Proses" yang sudah ada), sehingga tidak lagi memakan ruang layout dan memberikan tampilan yang lebih bersih.

Panel mengambang ini memiliki dua tombol toggle di sisi kiri:
- **Tombol Hijau** (success): Menampilkan parameter Alignment
- **Tombol Merah** (danger): Menampilkan parameter Denoising (hanya untuk Similarity)

## Komponen GenericUI yang Digunakan

| Komponen | Fungsi |
|----------|--------|
| `OverlayContainer` + `OverlayPosition.RIGHT_CENTER` | Container overlay mengambang di sisi kanan display |
| `Button` (variant="success") | Tombol toggle hijau untuk alignment |
| `Button` (variant="danger") | Tombol toggle merah untuk denoising |
| `ScrollContainer` | Scrollable area untuk konten parameter |
| `QStackedWidget` | Switching konten alignment <-> denoising |

## Rencana Implementasi

### Task 1: Buat `floating_parameter_panel.py` (File Baru)

**Path**: `pixel_refine_desktop/enhance_stack/components/batch_page_v2/floating_parameter_panel.py`

Buat widget baru `FloatingParameterPanel(QWidget)` yang merupakan konten dari overlay:

```
FloatingParameterPanel (QWidget)
  └── outer_layout (QHBoxLayout)
        ├── toggle_column (QWidget, fixed-width ~44px)
        │     └── QVBoxLayout
        │           ├── green_btn (Button variant="success", teks "A")
        │           └── red_btn (Button variant="danger", teks "D")
        └── content_stack (QStackedWidget)
              ├── Page 0: Alignment Parameter (dari ParameterPages)
              └── Page 1: Denoising Parameter (dari ParameterPages)
```

**Detail:**
- Import `ParameterPages` dari `parameter_pages.py` untuk membuat halaman parameter aktual
- Tombol toggle menggunakan `Button` dari GenericUI, dengan gaya aktif/nonaktif
- `update_from_settings(settings)` method menentukan tombol mana yang ditampilkan berdasarkan mode
- Signal: `process_requested = Signal(dict)` untuk forwarding proses

### Task 2: Tambah Overlay ke `display_panel.py`

**Path**: `pixel_refine_desktop/enhance_stack/components/batch_page_v2/display_panel.py`

**Tambah method baru:**
- `_setup_floating_parameter_overlay()` - Setup overlay dengan `OverlayContainer(position=RIGHT_CENTER)`
- `show_floating_parameters(visible)` - Show/hide overlay
- `update_floating_parameters(settings)` - Update content berdasarkan settings

**Overlay Config:** Position=`RIGHT_CENTER`, margin=15, shadow enabled, non-modal, smart_positioning=True

### Task 3: Modifikasi `algorithm_panel.py`

**Path**: `pixel_refine_desktop/enhance_stack/components/batch_page_v2/algorithm_panel.py`

- Tambah signal: `floating_panel_update = Signal(dict)`
- Di `_update_adaptive_ui()`, emit `floating_panel_update` dengan settings

### Task 4: Modifikasi `left_panel.py`

**Path**: `pixel_refine_desktop/enhance_stack/components/batch_page_v2/left_panel.py`

- Tambah `_update_floating_panel(settings)` method
- Hubungkan: `algorithm_panel.floating_panel_update.connect(self._update_floating_panel)`

### Task 5: Modifikasi `page_layout.py`

**Path**: `pixel_refine_desktop/enhance_stack/components/batch_page_v2/page_layout.py`

- Hubungkan `batch_panel.algorithm_settings_changed` ke `_update_floating_panel`

## Matriks Visibilitas Tombol

| Alignment | Denoising | Hijau | Merah | Panel |
|-----------|-----------|-------|-------|-------|
| Aktif | Similarity | ✅ | ✅ | Ya |
| Aktif | Average | ✅ | ❌ | Ya |
| Aktif | Median | ✅ | ❌ | Ya |
| Aktif | MFDenoiser | ✅ | ✅ | Ya |
| Aktif | No Denoising | ✅ | ❌ | Ya |
| No Align | Similarity | ❌ | ✅ | Ya |
| No Align | Average | ❌ | ❌ | Tidak |
| No Align | MFDenoiser | ❌ | ✅ | Ya |
| No Align | No Denoising | ❌ | ❌ | Tidak |

## File yang Dimodifikasi

| File | Aksi |
|------|------|
| `batch_page_v2/floating_parameter_panel.py` | **BARU** |
| `batch_page_v2/display_panel.py` | Tambah overlay + methods |
| `batch_page_v2/algorithm_panel.py` | Tambah signal |
| `batch_page_v2/left_panel.py` | Tambah method + connection |
| `batch_page_v2/page_layout.py` | Tambah connection |

## Verification

1. Jalankan `main_desktop.py`
2. Test mode Average: Floating panel TIDAK tampil, hanya "Mulai Proses"
3. Test mode Similarity + Alignment: Floating panel muncul di kanan dengan 2 tombol
4. Klik tombol hijau -> konten alignment
5. Klik tombol merah -> konten denoising
6. Test ubah dropdown -> panel update real-time
7. Resize window -> overlay tetap posisi benar
