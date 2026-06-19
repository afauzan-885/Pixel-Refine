# GenericUILibrary dan Arsitektur Mobile

**Sumber**: 4 memory files dari `.qoder/memories/.../project_tech_stack/`

## GenericUILibrary Coverage

### Status: 100% Coverage Tercapai

- **67 to_qml() methods** di SEMUA QWidget subclasses
- **12 kelas tanpa to_qml()**: Non-widget infrastructure
  - Theme
  - DataStore
  - Mixins
  - OverlayPosition enum
  - demos

### Theme System
- Semua to_qml() menggunakan `genericTheme.*` untuk theme-reactive colors
- Tidak hardcoded hex kecuali design conventions:
  - Navbar: `#2c3e50`
  - Overlay: `#80000000`
  - FeatureCard checked green

### Export
- `GridItemWidget` dan `LoadingOverlay` dari `ui_component.py` exported di `__init__.py`

## Dynamic QML Generation Architecture

### Prinsip Utama
**TIDAK ada static QML files** di mobile application!

### Alur
```
Python UI Code → to_qml() methods → QML strings → MobileApp.loadData()
```

### Implementasi
```python
# main_mobile.py
# TIDAK load file QML statis
# QML di-generate secara runtime via to_qml()
MobileApp.loadData(widget.to_qml())
```

### Kompatibilitas
Satu Python UI code bekerja di:
- **Desktop**: QMainWindow dengan native QWidget
- **Mobile**: MobileApp dengan QML (via to_qml() conversion)

## Dual-Styling Architecture

### Desktop (QWidget)
- Global QSS stylesheet via `apply_stylesheet()`
- objectName selectors: `#displayContainer`, `#processButton`

### Mobile (QML)
- Theme values via `QmlThemeBridge` sebagai `genericTheme.*` context properties
- **17 properties**: `primary`, `bgPrimary`, `textSecondary`, `borderColor`, `radiusSm`, dll

## Mobile UI Stack

### Active Path
- **PySide6 + Qt Quick**
- MobileApp + QmlThemeBridge
- Support mouse wheel scrolling (desktop testing)
- Support touch-based scrolling (mobile devices)

### Legacy (Unused)
- Kivy/KivyMD

## Desktop-to-Mobile Code Reuse

### Modul Platform-Agnostic (21 modul)

#### Controllers (4)
- Batch controller
- Processing controller
- Import controller
- Navigation controller

#### Models (3)
- Data models
- Configuration models
- State models

#### Repositories (5)
- Image repository
- Project repository
- Settings repository
- Cache repository
- History repository

#### Core Services
- `database_manager.py`
- `algorithm_logic.py`
- `process_manager.py`
- `image_streamer.py`
- `base_worker.py`

### Sifat Modul
- **Tidak ada** PySide6 widget dependencies
- Hanya menggunakan: `QtCore`, `Signal`, `SQLite`, atau pure Python
- Siap digunakan langsung di mobile

## API Parity Requirement

### Desktop vs Mobile

| Aspek | Desktop | Mobile |
|-------|---------|--------|
| Window wrapper | `QMainWindow` | `MobileApp` |
| Rendering | `QWidget` | `to_qml()` → QML |
| Python API | Identik | Identik |
| Component composition | Identik | Identik |

### Contoh
```python
# KEDUA platform menggunakan kode yang SAMA
from GenericUILibrary import Container, Card, Button

container = Container()
card = Card(title="My Card")
button = Button(text="Click Me")

# Desktop
app = QMainWindow()
app.setCentralWidget(container)

# Mobile
app = MobileApp()
app.loadData(container.to_qml())
```

## QML Implementation Rules

### 1. ID Uniqueness
- ID harus **UNIK** dalam scope yang sama
- Duplikat ID menyebabkan `QQmlApplicationEngine` gagal load

### 2. Height References
- Gunakan `childrenRect.height`
- **JANGAN** gunakan id-based height references

### 3. implicitHeight
- `implicitHeight` adalah **READ-ONLY**
- Tidak bisa di-set langsung
- Gunakan `height` atau constraints lain

## QML Component Usage

### Benar
```qml
Column {
    id: contentCol
    childrenRect.height: children.height  // ✓ Benar
}
```

### Salah
```qml
Column {
    id: contentCol
    height: contentCol.height  // ✗ Salah - circular reference
}
```
