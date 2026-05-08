# Pixel Refine - Development Knowledge Base (Gemini)

## 🛠 Project Status (Taichi AOT Pipeline)
- **Status**: Production Ready / Optimized
- **Architecture**: Smart C++ Pipeline (One Big Graph) - **Implemented**
- **Algorithm Coverage**: 100% (17 core algorithms migrated to AOT)
- **Multi-Backend**: Supported (Vulkan, CUDA, CPU)
- **Accuracy**: Verified against OpenCV (MAE within safe thresholds)

## 📊 Latest Performance Benchmarks (9.1 MP - 3016x3016)
*Measured on Chained Operations (Resize + Blur + Median + Bilateral Grid + Sobel)*
- **Smart Pipeline (Grayscale)**: **~17.72 ms** per frame (**56.42 FPS**).
- **Universal Interop Bridge (Fast-Copy)**: **~61.03 ms** for 34MB (9.1 MP) transfer (DMA-based).
- **Smart Image IO (imread)**: **~149 ms** (vs OpenCV ~208 ms) -> **+28% Faster**.
- **Smart Image IO (imwrite)**: Bit-perfect accuracy verified.

> [!NOTE]
> Chained operations using `rec_pipeline` and `run_pipeline` eliminate Python-to-C++ dispatch overhead. The Universal Bridge enables zero-copy-like transfers between Taichi, PyTorch, and ONNX.

## 🧱 Technical Constraints & Architecture
- **Smart Overrides**: Identity-based (Memory Handle) swapping using `Placeholder` objects.
- **One Big Graph**: Entire processing chains are recorded once and executed at native C++ speed.
- **Data Type**: 16-bit images are represented in `i32` for AOT precision/safety.
- **Buffer Management**: Managed via `AOTEngine` and `BufferPool` to keep memory footprint ~1GB.
- **Universal GPU Bridge**: Cross-vendor (Nvidia/AMD/Intel) DMA transfer via Pinned-Memory Fast-Copy Bridge.
- **Anti-Crash Design**: Explicit synchronization (`rt->wait()`) and automatic staging-read for VRAM-only buffers.
- **Smart Image IO**: Direct C++ decoding to VRAM (imread/imwrite) using Windows Imaging Component (WIC).

## 🚀 Roadmap & Next Steps
1. **Bilateral Grid Integration**: **Implemented**
2. **High-Performance Image IO**: **Implemented** (8/16-bit support via WIC)
3. **Universal GPU Interop Bridge**: **Implemented & Verified** (50x Stress-Test Passed)
4. **Smart Data Transformation**: **Implemented** (`gpu_buffer.cast` via C++ Backend)
5. **Mobile Optimization**: Validate TCM modules on mobile backends.

## 📂 Key Files
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_aot/engine.py`: Primary AOT runtime bridge (with Pipeline & IO support).
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/taichi_aot_engine.cpp`: C++ Backend Orchestrator.
- `pixel_refine_desktop/enhance_stack/core/algorithm/taichi_algorithm/aot_py/test_comprehensif.py`: Master test suite.
- `test_algorithm/IMG_20250401_182043_B003.png`: Standard test image for high-res benchmarks.
