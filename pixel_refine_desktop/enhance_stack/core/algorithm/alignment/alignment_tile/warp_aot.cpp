#include "taichi_modular_core.h"
#include <vector>
#include <chrono>
#include <cstdio>

#ifdef _WIN32
#define WARP_API __declspec(dllexport)
#else
#define WARP_API
#endif

extern "C" {

/**
 * Run Warp Ops (Upsample + Warp)
 */
WARP_API int run_warp_aot(
    void* runtime_ptr,
    void* module_ptr,
    const char* /* unused */,
    void* src_mem,
    void* flow_low_mem, // The low-res flow from compute_flow
    void* flow_full_mem, // Buffer to store upsampled flow
    void* dst_mem,
    void* guide_mem,
    int h, int w, int c,
    int work_h, int work_w
) {
    TiRuntime runtime = (TiRuntime)runtime_ptr;
    TiAotModule module = (TiAotModule)module_ptr;
    if (!runtime || !module) return -1;

    auto t0 = std::chrono::high_resolution_clock::now();
    float upsample_ratio = (work_h > 0) ? (float)h / (float)work_h : 0.f;
    printf("[WarpAOT] src=(%d,%d,c=%d) work=(%d,%d) -> full=(%d,%d) upsample_ratio=%.3f\n",
           h, w, c, work_h, work_w, h, w, upsample_ratio);
    fflush(stdout);

    // 1. Get Graphs
    TiComputeGraph g_up = ti_get_aot_module_compute_graph(module, "upsample_flow");
    TiComputeGraph g_warp = ti_get_aot_module_compute_graph(module, "warp_rgb");
    if (!g_up || !g_warp) return -2;

    // 1. Launch Upsample Flow
    {
        std::vector<TiNamedArgument> args;
        
        TiNdArray src_nd = {};
        src_nd.memory = (TiMemory)flow_low_mem;
        src_nd.shape.dim_count = 3;
        src_nd.shape.dims[0] = work_h;
        src_nd.shape.dims[1] = work_w;
        src_nd.shape.dims[2] = 2;
        src_nd.elem_type = TI_DATA_TYPE_F32;
        args.push_back({"src", {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = src_nd}}});

        TiNdArray dst_nd = {};
        dst_nd.memory = (TiMemory)flow_full_mem;
        dst_nd.shape.dim_count = 3;
        dst_nd.shape.dims[0] = h;
        dst_nd.shape.dims[1] = w;
        dst_nd.shape.dims[2] = 2;
        dst_nd.elem_type = TI_DATA_TYPE_F32;
        args.push_back({"dst", {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = dst_nd}}});

        args.push_back({"scale", {TI_ARGUMENT_TYPE_F32, {.f32 = (float)h / (float)work_h}}});

        ti_launch_compute_graph(runtime, g_up, (uint32_t)args.size(), args.data());
    }

    // 2. Launch Warp
    {
        std::vector<TiNamedArgument> args;
        
        auto add_ndarray = [&](const char* name, void* mem, int rows, int cols, int channels) {
            TiNdArray nd = {};
            nd.memory = (TiMemory)mem;
            nd.shape.dim_count = 3;
            nd.shape.dims[0] = rows;
            nd.shape.dims[1] = cols;
            nd.shape.dims[2] = channels;
            nd.elem_type = TI_DATA_TYPE_I32;
            args.push_back({name, {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = nd}}});
        };

        add_ndarray("src", src_mem, h, w, c);
        add_ndarray("dst", dst_mem, h, w, c);
        add_ndarray("guide", guide_mem, h, w, c);

        TiNdArray flow_nd = {};
        flow_nd.memory = (TiMemory)flow_full_mem;
        flow_nd.shape.dim_count = 3;
        flow_nd.shape.dims[0] = h;
        flow_nd.shape.dims[1] = w;
        flow_nd.shape.dims[2] = 2;
        flow_nd.elem_type = TI_DATA_TYPE_F32;
        args.push_back({"flow", {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = flow_nd}}});

        ti_launch_compute_graph(runtime, g_warp, (uint32_t)args.size(), args.data());
    }

    ti_wait(runtime);

    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();
    printf("[WarpAOT] Done (upsample+warp) in %.2f ms\n", ms);
    fflush(stdout);

    return 0;
}

WARP_API int read_from_gpu_buffer(void* runtime, void* memory, void* dst_host, uint64_t size) {
    if (!runtime || !memory || !dst_host) return -1;
    void* mapped = ti_map_memory((TiRuntime)runtime, (TiMemory)memory);
    if (!mapped) return -2;
    memcpy(dst_host, mapped, size);
    ti_unmap_memory((TiRuntime)runtime, (TiMemory)memory);
    return 0;
}

} // extern "C"
