# Ikhtisar Proyek Pixel Refine

**Sumber**: 16 memory files dari `.qoder/memories/.../project_introduction/`

## Domain
Pixel Refine adalah aplikasi **fotografi komputasi** yang meningkatkan gambar melalui **fusi multi-frame**.

## Kemampuan Inti

### Alignment
- **AKAZE** — Robust, cocok untuk berbagai kondisi
- **ORB** — Fast, ringan
- **LightGlue** — SOTA (State of the Art), GPU-heavy, menggunakan ONNX Runtime

### Denoising
- **Average** — Simple averaging, diproses di original resolution
- **Median** — Median filtering multi-frame
- **Similarity** — Custom method, movement-robust, menggunakan work resolution downsampling
- **HFCD** — Hybrid Fast Collaborative Denoising (single-pass, FFT block matching + 2D DCT)

### Super Resolution
- Interpolation-based (sementara disabled)

### Lainnya
- HDR processing, ghost removal, RAW tone rendering, detail enhancement
- Mendukung: JPG, TIFF, PNG, RAW (DNG, NEF, ARW, CR2, CR3)
- DNG export: direncanakan
- Minimum spec: Win10, 6GB RAM, MX150 GPU, dual-core CPU

## Status
- Taichi AOT Pipeline: **production-ready** dengan 19 algoritma sudah dimigrasi
- Farneback Optical Flow: sedang di-upgrade ke multi-scale implementation (target 5× speedup vs OpenCV)

## Scope Mobile
Terbatas pada **5 komponen inti**:
1. Home Page
2. MFDenoiser
3. MFResolution
4. HDR
5. Panorama

## Arsitektur Mobile Core
- GenericUI UI components → Screen Builders → AppState Router → Controllers → Core Logic → Repositories → SQLite DB
- Thumbnail management: 2-tier cache (RAM + Disk), 96×96 size, CPU fallback
- Navigation: Home Page (tool cards) → Workspace Page (shared layout)
