#include "taichi_modular_core.h"
#include <iostream>
#include <vector>
#include <chrono>

#ifdef _WIN32
#define ALIGN_API __declspec(dllexport)
#else
#define ALIGN_API
#endif

extern "C" {

/**
 * Run Alignment (Optical Flow) Graph
 * This binds the 3-layer pyramid exactly as defined in aot_compute_flow_compiler.py
 */
ALIGN_API int run_compute_flow_aot(
    void* runtime_ptr,
    void* module_ptr,
    const char* graph_name,
    void** ref_pyramid,  // Array of 3 TiMemory
    int* ref_h, int* ref_w,
    void** comp_pyramid, // Array of 3 TiMemory
    int* comp_h, int* comp_w,
    void** flow_pyramid, // Array of 3 TiMemory
    void** flow_tmp_pyramid, // Array of 3 TiMemory
    void* tmp_ref_l1, void* tmp_ref_l2,
    void* tmp_comp_l1, void* tmp_comp_l2,
    void* zncc_surf,
    void* zncc_res,
    int tile_h, int tile_w,
    int search_radius,
    int coarse_dist,
    float scale,
    int ds_fac,
    int zncc_shift,
    int step_y,
    int step_x
) {
    TiRuntime runtime = (TiRuntime)runtime_ptr;
    TiAotModule module = (TiAotModule)module_ptr;
    if (!runtime || !module) return -1;

    TiComputeGraph graph = ti_get_aot_module_compute_graph(module, graph_name);
    if (!graph) return -2;

    std::vector<TiNamedArgument> args;

    auto t0 = std::chrono::high_resolution_clock::now();
    printf("[ComputeFlowAOT] graph='%s' tile=(%d,%d) radius=%d dist=%d scale=%.1f ds=%d zncc_shift=%d\n",
           graph_name, tile_h, tile_w, search_radius, coarse_dist, scale, ds_fac, zncc_shift);
    for (int i = 0; i < 3; ++i) {
        printf("[ComputeFlowAOT]   L%d: ref(%d,%d) comp(%d,%d)\n",
               i, ref_h[i], ref_w[i], comp_h[i], comp_w[i]);
    }
    fflush(stdout);

    // Keep strings alive until launch
    std::vector<std::string> arg_names;
    arg_names.reserve(40);

    auto add_ndarray = [&](const char* name, void* mem, int h, int w, int c = 1) {
        TiNdArray nd = {};
        nd.memory = (TiMemory)mem;
        nd.shape.dim_count = (c > 1) ? 3 : 2;
        nd.shape.dims[0] = h;
        nd.shape.dims[1] = w;
        if (c > 1) nd.shape.dims[2] = c;
        nd.elem_type = TI_DATA_TYPE_F32;
        
        arg_names.push_back(name);
        args.push_back({arg_names.back().c_str(), {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = nd}}});
    };

    auto add_scalar_i32 = [&](const char* name, int val) {
        arg_names.push_back(name);
        args.push_back({arg_names.back().c_str(), {TI_ARGUMENT_TYPE_I32, {.i32 = val}}});
    };

    auto add_scalar_f32 = [&](const char* name, float val) {
        arg_names.push_back(name);
        args.push_back({arg_names.back().c_str(), {TI_ARGUMENT_TYPE_F32, {.f32 = val}}});
    };

    // 1. Pyramid Levels
    for (int i = 0; i < 3; ++i) {
        char name_ref[16], name_comp[16], name_flow[16], name_ftmp[16];
        sprintf(name_ref, "ref_l%d", i);
        sprintf(name_comp, "comp_l%d", i);
        sprintf(name_flow, "flow_l%d", i);
        sprintf(name_ftmp, "flow_tmp_l%d", i);

        add_ndarray(name_ref, ref_pyramid[i], ref_h[i], ref_w[i]);
        add_ndarray(name_comp, comp_pyramid[i], comp_h[i], comp_w[i]);
        add_ndarray(name_flow, flow_pyramid[i], comp_h[i], comp_w[i], 2);
        add_ndarray(name_ftmp, flow_tmp_pyramid[i], comp_h[i], comp_w[i], 2);
    }

    // 2. Intermediate Buffers
    add_ndarray("tmp_ref_l1", tmp_ref_l1, ref_h[1] * 2, ref_w[1] * 2);
    add_ndarray("tmp_ref_l2", tmp_ref_l2, ref_h[2] * 2, ref_w[2] * 2);
    add_ndarray("tmp_comp_l1", tmp_comp_l1, comp_h[1] * 2, comp_w[1] * 2);
    add_ndarray("tmp_comp_l2", tmp_comp_l2, comp_h[2] * 2, comp_w[2] * 2);

    // 3. ZNCC Surface
    add_ndarray("zncc_surf", zncc_surf, zncc_shift * 2 + 1, zncc_shift * 2 + 1);
    
    // 4. ZNCC Results (ndim=1)
    TiNdArray res_nd = {};
    res_nd.memory = (TiMemory)zncc_res;
    res_nd.shape.dim_count = 1;
    res_nd.shape.dims[0] = 3;
    res_nd.elem_type = TI_DATA_TYPE_F32;
    arg_names.push_back("zncc_res");
    args.push_back({arg_names.back().c_str(), {TI_ARGUMENT_TYPE_NDARRAY, {.ndarray = res_nd}}});

    // 5. Scalars
    add_scalar_i32("tile_h", tile_h);
    add_scalar_i32("tile_w", tile_w);
    add_scalar_i32("search_radius", search_radius);
    add_scalar_i32("coarse_dist", coarse_dist);
    add_scalar_f32("scale", scale);
    add_scalar_i32("ds_fac", ds_fac);
    add_scalar_i32("zncc_shift", zncc_shift);
    add_scalar_i32("step_y", step_y);
    add_scalar_i32("step_x", step_x);

    ti_launch_compute_graph(runtime, graph, (uint32_t)args.size(), args.data());
    ti_wait(runtime);

    auto t1 = std::chrono::high_resolution_clock::now();
    double ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

    // Read back zncc_res to estimate motion magnitude
    float zncc_vals[3] = {0.f, 0.f, 0.f};
    bool map_ok = false;
    void* mapped = ti_map_memory(runtime, (TiMemory)zncc_res);
    if (mapped) {
        memcpy(zncc_vals, mapped, sizeof(zncc_vals));
        ti_unmap_memory(runtime, (TiMemory)zncc_res);
        map_ok = true;
    }
    
    if (map_ok) {
        printf("[ComputeFlowAOT] Done in %.2f ms | zncc_res: cost=%.4f y=%.2f x=%.2f\n",
               ms, zncc_vals[0], zncc_vals[1] - (float)zncc_shift, zncc_vals[2] - (float)zncc_shift);
    } else {
        printf("[ComputeFlowAOT] Done in %.2f ms | (failed to map zncc_res)\n", ms);
    }
    fflush(stdout);

    return 0;
}

} // extern "C"
