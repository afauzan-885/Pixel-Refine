# Pixel Refine — Project Overview

## Status Proyek
- **Status**: Production Ready / Optimized
- **Architecture**: Smart C++ Pipeline (One Big Graph) — **Implemented**
- **Algorithm Coverage**: 100% (19+ core algorithms migrated to AOT)
- **Multi-Backend**: Supported (Vulkan, CUDA, CPU)
- **Accuracy**: Verified against OpenCV (MAE within safe thresholds)

## Kapabilitas Utama

### 1. Multi-Frame Denoising (MFDenoiser)
Orchestrator pipeline untuk denoising multi-frame dengan dukungan berbagai backend:
- **Spatial Fusion**: GPU AOT ghost rejection berbasis hybrid gradient MAD score
- **Average**: Simple averaging (original resolution)
- **Smart**: AI-based fusion
- **Super Resolution**: GPU-accelerated SR

### 2. Alignment & Optical Flow
- **BMA (Block Matching Alignment)**: SAD/SSD metrics, 3-layer pyramid
- **Horn-Schunck**: GPU AOT dengan Jacobi solver
- **Farneback**: GPU AOT dengan polynomial expansion
- **Phase Correlation**: FFT-based sub-pixel alignment

### 3. Feature Matching
- **O-FAST-BRIEF (OFB)**: Keypoint detector dengan sub-pixel refinement, rotation/scale invariance
- **A-KAZE**: Non-linear scale space (FED), Hessian determinant detector, M-SURF descriptor
- **MAGSAC++**: GPU Homography solver dengan Tukey's biweight scoring

### 4. Image Processing
- **Demosaicing**: Hamilton-Adams, ARM (Adaptive Residual Minimization)
- **WarpAffine/WarpPerspective**: GPU spasial dengan mirror border reflection
- **RANSAC Flow Cleanup**: GPU-based outlier removal
- **Bilateral Grid**: Edge-preserving smoothing
- **Gaussian/Median/Box Filter**: Noise reduction

### 5. RAW Processing
- **DNG Support**: Direct C++ decoding to VRAM via WIC (Windows Imaging Component)
- **16-bit Pipeline**: Full 16-bit processing tanpa precision loss
- **Linear Mode**: Proxy scale untuk high-dynamic-range RAW files

## Entry Points

| File | Deskripsi |
|------|-----------|
| `MFDenoiser.py` | Main orchestrator (single truth source) |
| `Similarity.py` | Legacy orchestrator (backup) |
| `main_desktop.py` | Application entry point |

## Performance Benchmarks (9.1 MP - 3016x3016)

| Operation | Time | FPS |
|-----------|------|-----|
| Smart Pipeline (Grayscale) | ~17.72 ms | 56.42 |
| Universal Interop Bridge | ~61.03 ms (34MB) | — |
| Smart Image IO (imread) | ~149 ms | — |

> Chained operations using `rec_pipeline` and `run_pipeline` eliminate Python-to-C++ dispatch overhead.
