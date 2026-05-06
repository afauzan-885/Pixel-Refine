# Pixel Refine - Development Knowledge Base (Gemini)

## 🛠 Project Status (Taichi AOT Pipeline)
- **Status**: Production Ready / Stabilized
- **Algorithm Coverage**: 100% (17 core algorithms migrated to AOT)
- **Multi-Backend**: Supported (Vulkan, CUDA, CPU)
- **Accuracy**: Verified against OpenCV (MAE within safe thresholds)

## 📊 Latest Performance Benchmarks (9.1 MP - 3016x3016)
*Measured on Gaussian Blur (Roundtrip with Transfer)*
- **Average Latency**: ~239.24 ms
- **Average FPS**: ~4.18 FPS
- **Resolution**: 9.1 MP (3016x3016)

> [!NOTE]
> FPS "Roundtrip" include PCIe transfer overhead (Upload + Process + Download). Chained operations with `return_gpu=True` can achieve 100+ FPS.

## 🧱 Technical Constraints & Architecture
- **Data Type**: 16-bit images are represented in `i32` for AOT precision/safety.
- **Buffer Management**: Managed via `AOTEngine` and `BufferPool` to keep memory footprint ~1GB.
- **Warping**: Uses "Ultra-Vectorized" 2D NDArrays (`vec3` for pixels, `vec2` for flow) for maximum throughput.

## 🚀 Roadmap & Next Steps
1. **Bilateral Grid Integration**: Incorporate into the main Smart Fusion pipeline for adaptive denoising.
2. **Phase Correlation**: Leverage for initial global alignment before fine-grained matching.
3. **C++ "One Big Graph"**: Move entire chains to C++ for zero Python overhead in production.
4. **Mobile Optimization**: Validate TCM modules on mobile backends.

## 📂 Key Files
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/test_comprehensif.py`: Master test suite.
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/__init__.py`: Primary AOT runtime bridge.
- `test_algorithm/IMG_20250401_182043_B003.png`: Standard test image for high-res benchmarks.
