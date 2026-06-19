# Technology Stack Pixel Refine

**Sumber**: 16 memory files dari `.qoder/memories/.../project_tech_stack/`

## Desktop Application
- **PySide6**: Cross-platform GUI framework (Qt for Python)
- **OpenCV**: Core CV operations (alignment: AKAZE/ORB/LightGlue, denoising)
- **rawpy**: RAW image decoding (DNG, NEF, ARW, CR2, CR3, dll)
- **Pillow & tifffile**: JPG/TIFF/PNG support
- **ONNX Runtime**: LightGlue deep learning alignment inference
- **scipy**: Numerical operations
- **h5py**: Data storage
- **exifread**: Metadata extraction

## GPU Processing
- **Taichi**: GPU-accelerated computation framework (Vulkan backend)
- **engine.py**: Single Source of Truth, backend orchestrator
- **Taichi AOT Pipeline**: Smart C++ Pipeline architecture
- **TCM Modules**: Vulkan AOT compiled kernels

### Existing GPU Algorithms
- WarpAffine, WarpPerspective, MAGSAC++
- OFB (O-FAST-BRIEF), A-KAZE
- Multi-size BMA, Farneback Flow
- Box filter, Sobel, Gaussian, FFT2, IFFT2
- Phase correlation, RANSAC

## Mobile Stack
- **PySide6 + Qt Quick**: Active UI framework
- **MobileApp**: QML application wrapper
- **QmlThemeBridge**: Theme integration between Python and QML
- **Dynamic QML Generation**: via `to_qml()` methods

### Legacy (Unused)
- Kivy/KivyMD: Tidak digunakan

## Dual-Styling Architecture

### Desktop (QWidget)
- Global QSS stylesheet via `apply_stylesheet()`
- objectName selectors (misal: `#displayContainer`, `#processButton`)

### Mobile (QML)
- Theme values via `QmlThemeBridge` sebagai `genericTheme.*` context properties
- 17 properties: `primary`, `bgPrimary`, `textSecondary`, `borderColor`, `radiusSm`, dll

## Technology Requirements
- **Minimum**: Win10, 6GB RAM, MX150 GPU, dual-core CPU
- **Recommended**: Dedicated GPU dengan Vulkan support
- **Python**: 3.8+ (kompatibel dengan PySide6)
