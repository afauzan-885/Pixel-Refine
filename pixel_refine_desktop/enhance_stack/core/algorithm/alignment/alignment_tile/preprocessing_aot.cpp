#include "preprocessing_aot.h"
#include <taichi/cpp/taichi.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <cstdint>

// Struktur internal untuk menyimpan konteks runtime
struct AotContext {
    ti::Runtime runtime;
    ti::AotModule module;
    ti::ComputeGraph preprocess_rgb;
    ti::ComputeGraph preprocess_gray;
    bool initialized = false;
};

// Singleton context
static AotContext& get_context() {
    static AotContext ctx;
    return ctx;
}

extern "C" {

/**
 * Inisialisasi TiRT Runtime dan memuat modul AOT.
 */
PREPROCESS_API int init_taichi_aot_runtime(const char* module_path) {
    auto& ctx = get_context();
    if (ctx.initialized) return 0;

    try {
        // 1. Inisialisasi Runtime (Vulkan direkomendasikan untuk Desktop Windows)
        ctx.runtime = ti::Runtime(TI_ARCH_VULKAN);
        
        // 2. Muat Modul AOT
        ctx.module = ctx.runtime.load_aot_module(module_path);
        
        // 3. Ambil Grafik yang sudah didefinisikan di compiler
        ctx.preprocess_rgb = ctx.module.get_compute_graph("preprocess_rgb");
        ctx.preprocess_gray = ctx.module.get_compute_graph("preprocess_gray");
        
        ctx.initialized = true;
        std::cout << "[TaichiAOT] Runtime initialized from: " << module_path << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "[TaichiAOT] Initialization failed: " << e.what() << std::endl;
        return -1;
    }
}

/**
 * Melakukan preprocessing (Normalize -> Gamma -> Extract Green -> Resize) secara AOT.
 */
PREPROCESS_API int compute_preprocess_aot(
    const int* src_ptr,  // Input pointer (int32)
    float* dst_ptr,      // Output pointer (float32)
    int src_h, int src_w, int src_c,
    int dst_h, int dst_w,
    float scale_norm,
    int apply_gamma,
    float scale_gamma,
    float gamma_pow,
    float slope,
    float cutoff,
    int use_sharpen
) {
    auto& ctx = get_context();
    if (!ctx.initialized) return -1;

    try {
        // 1. Siapkan NdArray untuk Input (Raw data dari CPU)
        std::vector<uint32_t> src_shape;
        if (src_c > 1) {
            src_shape = {(uint32_t)src_h, (uint32_t)src_w, (uint32_t)src_c};
        } else {
            src_shape = {(uint32_t)src_h, (uint32_t)src_w};
        }
        
        // Alokasi NdArray di GPU (host_accessible=true agar bisa ditulisi langsung)
        ti::NdArray src_array = ctx.runtime.allocate_ndarray<int32_t>(src_shape, {}, true);
        src_array.write(src_ptr, (size_t)src_h * src_w * src_c);

        // 2. Siapkan NdArray untuk Output (H, W) f32
        ti::NdArray dst_array = ctx.runtime.allocate_ndarray<float>({(uint32_t)dst_h, (uint32_t)dst_w}, {}, true);

        // 3. Pilih Grafik (RGB vs Gray)
        ti::ComputeGraph* graph_ptr = (src_c > 1) ? &ctx.preprocess_rgb : &ctx.preprocess_gray;
        ti::ComputeGraph& graph = *graph_ptr;

        // 4. Bind Argumen sesuai urutan (Named arguments matching aot_alignment_compiler.py)
        graph["src"] = src_array;
        graph["dst"] = dst_array;
        graph["src_h"] = (int32_t)src_h;
        graph["src_w"] = (int32_t)src_w;
        graph["dst_h"] = (int32_t)dst_h;
        graph["dst_w"] = (int32_t)dst_w;
        graph["scale_norm"] = (float)scale_norm;
        graph["apply_gamma"] = (int32_t)apply_gamma;
        graph["scale_gamma"] = (float)scale_gamma;
        graph["gamma_pow"] = (float)gamma_pow;
        graph["slope"] = (float)slope;
        graph["cutoff"] = (float)cutoff;
        graph["use_sharpen"] = (int32_t)use_sharpen;

        // 5. Eksekusi di GPU
        graph.launch();
        ctx.runtime.wait(); // Sinkronisasi CPU-GPU

        // 6. Baca hasil kembali ke pointer output NumPy (H*W float32)
        dst_array.read(dst_ptr, (size_t)dst_h * dst_w);
        
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "[TaichiAOT] Execution failed: " << e.what() << std::endl;
        return -2;
    }
}

} // extern "C"
