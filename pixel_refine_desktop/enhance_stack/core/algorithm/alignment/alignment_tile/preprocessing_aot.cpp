#include "taichi_modular_core.h"
#include <iostream>
#include <cstring>
#include <chrono>

#ifdef _WIN32
#define PREPROCESS_API __declspec(dllexport)
#else
#define PREPROCESS_API
#endif

extern "C" {

/**
 * Initialize Taichi Runtime (Vulkan)
 */
PREPROCESS_API void* init_taichi_runtime() {
    TiRuntime runtime = ti_create_runtime(TI_ARCH_VULKAN, 0);
    return (void*)runtime;
}

/**
 * Load AOT Module
 */
PREPROCESS_API void* load_aot_module(void* runtime, const char* path) {
    if (!runtime || !path) return nullptr;
    TiAotModule mod = ti_load_aot_module((TiRuntime)runtime, path);
    return (void*)mod;
}

/**
 * Allocate GPU Buffer (TiMemory)
 */
PREPROCESS_API void* allocate_gpu_buffer(void* runtime, uint64_t size, int host_accessible) {
    if (!runtime) return nullptr;
    TiMemoryAllocateInfo info = {};
    info.size = size;
    info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
    info.host_write = (host_accessible != 0);
    info.host_read = (host_accessible != 0);
    
    TiMemory mem = ti_allocate_memory((TiRuntime)runtime, &info);
    return (void*)mem;
}

/**
 * Free GPU Buffer
 */
PREPROCESS_API void free_gpu_buffer(void* runtime, void* memory) {
    if (runtime && memory) {
        ti_free_memory((TiRuntime)runtime, (TiMemory)memory);
    }
}

/**
 * Map and Write data to GPU buffer
 */
PREPROCESS_API int write_to_gpu_buffer(void* runtime, void* memory, void* src_host, uint64_t size) {
    if (!runtime || !memory || !src_host) return -1;
    void* mapped = ti_map_memory((TiRuntime)runtime, (TiMemory)memory);
    if (!mapped) return -2;
    memcpy(mapped, src_host, size);
    ti_unmap_memory((TiRuntime)runtime, (TiMemory)memory);
    return 0;
}

/**
 * Run Preprocessing Graph
 */
PREPROCESS_API int run_preprocess_aot(
    void* runtime_ptr, 
    void* module_ptr,
    const char* graph_name,
    void* src_mem, // TiMemory handle
    int src_h, int src_w, int src_c,
    void* dst_mem, // TiMemory handle
    int dst_h, int dst_w,
    float scale_norm,
    int apply_gamma,
    float scale_gamma,
    float gamma_pow,
    float slope,
    float cutoff,
    int use_sharpen
) {
    TiRuntime runtime = (TiRuntime)runtime_ptr;
    TiAotModule module = (TiAotModule)module_ptr;
    if (!runtime || !module) return -1;

    auto t0 = std::chrono::high_resolution_clock::now();
    printf("[PreprocessAOT] graph='%s' src=(%d,%d,c=%d) dst=(%d,%d) scale_norm=%.0f gamma=%d\n",
           graph_name, src_h, src_w, src_c, dst_h, dst_w, scale_norm, apply_gamma);
    fflush(stdout);

    TiComputeGraph graph = ti_get_aot_module_compute_graph(module, graph_name);
    if (!graph) return -2;

    std::vector<TiNamedArgument> args;
    
    // Src NdArray
    TiNdArray src_nd = {};
    src_nd.memory = (TiMemory)src_mem;
    src_nd.shape.dim_count = (src_c > 1) ? 3 : 2;
    src_nd.shape.dims[0] = src_h;
    src_nd.shape.dims[1] = src_w;
    if (src_c > 1) src_nd.shape.dims[2] = src_c;
    src_nd.elem_type = TI_DATA_TYPE_I32;

    // Dst NdArray
    TiNdArray dst_nd = {};
    dst_nd.memory = (TiMemory)dst_mem;
    dst_nd.shape.dim_count = 2;
    dst_nd.shape.dims[0] = dst_h;
    dst_nd.shape.dims[1] = dst_w;
    dst_nd.elem_type = TI_DATA_TYPE_F32;

    args.push_back({"src", {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = src_nd}}});
    args.push_back({"dst", {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = dst_nd}}});
    
    // Scalars
    TiArgument arg_snorm = {TI_ARGUMENT_TYPE_F32, {.f32 = scale_norm}};
    args.push_back({"scale_norm", arg_snorm});
    
    TiArgument arg_gamma = {TI_ARGUMENT_TYPE_I32, {.i32 = apply_gamma}};
    args.push_back({"apply_gamma", arg_gamma});

    TiArgument arg_sgamma = {TI_ARGUMENT_TYPE_F32, {.f32 = scale_gamma}};
    args.push_back({"scale_gamma", arg_sgamma});

    TiArgument arg_gpow = {TI_ARGUMENT_TYPE_F32, {.f32 = gamma_pow}};
    args.push_back({"gamma_pow", arg_gpow});

    TiArgument arg_slope = {TI_ARGUMENT_TYPE_F32, {.f32 = slope}};
    args.push_back({"slope", arg_slope});

    TiArgument arg_cutoff = {TI_ARGUMENT_TYPE_F32, {.f32 = cutoff}};
    args.push_back({"cutoff", arg_cutoff});

    TiArgument arg_sharpen = {TI_ARGUMENT_TYPE_I32, {.i32 = use_sharpen}};
    args.push_back({"use_sharpen", arg_sharpen});

    ti_launch_compute_graph(runtime, graph, (uint32_t)args.size(), args.data());
    ti_wait(runtime);

    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    printf("[PreprocessAOT] Done in %.2f ms\n", ms);
    fflush(stdout);

    return 0;
}

} // extern "C"
