#include "alignment_tile_taichi_api.h"
#include <taichi/taichi.h>
#include <vector>
#include <string>
#include <iostream>
#include <map>
#include <algorithm>
#include <cstring>

// =========================================================================
// === MONOLITHIC ALIGNMENT CONTEXT ===
// =========================================================================

struct GpuBuffer {
    TiMemory mem = TI_NULL_HANDLE;
    uint64_t bytes = 0;
};

struct AlignmentContext {
    TiRuntime runtime = TI_NULL_HANDLE;
    TiAotModule aot_mod = TI_NULL_HANDLE;
    TiComputeGraph monolithic_graph = TI_NULL_HANDLE;

    // Fixed buffers (pre-allocated)
    GpuBuffer ref_raw, comp_raw, warped;
    std::vector<GpuBuffer> ref_layers, comp_layers;
    std::vector<GpuBuffer> flow_layers, flow_tmp_layers;
    std::vector<GpuBuffer> tmp_ref_layers, tmp_comp_layers;
    GpuBuffer zncc_surf, zncc_res;

    int n_layers = 3;
    int h = 0, w = 0;
    int channels = 3;

    // Config
    float s_gamma = 1.0f;
    int use_sharpen = 0;
};

static AlignmentContext* g_ctx = nullptr;

// =========================================================================
// === HELPER FUNCTIONS ===
// =========================================================================

static bool ensure_buffer(TiRuntime runtime, GpuBuffer& buf, uint64_t size, bool host_read = false) {
    if (buf.mem != TI_NULL_HANDLE && buf.bytes == size) return true;
    if (buf.mem != TI_NULL_HANDLE) ti_free_memory(runtime, buf.mem);
    
    TiMemoryAllocateInfo info = {};
    info.size = size;
    info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
    info.host_read = host_read ? TI_TRUE : TI_FALSE;
    buf.mem = ti_allocate_memory(runtime, &info);
    buf.bytes = size;
    return buf.mem != TI_NULL_HANDLE;
}

static TiArgument make_ndarray_arg(TiMemory mem, const std::vector<uint32_t>& shape, TiDataType type = TI_DATA_TYPE_F32) {
    TiNdArray nd = {};
    nd.memory = mem;
    nd.elem_type = type;
    nd.shape.dim_count = (uint32_t)shape.size();
    for (size_t i = 0; i < shape.size(); ++i) nd.shape.dims[i] = shape[i];
    
    TiArgument arg = {};
    arg.type = TI_ARGUMENT_TYPE_NDARRAY;
    arg.value.ndarray = nd;
    return arg;
}

static TiNamedArgument make_named_arg(const char* name, TiArgument arg) {
    TiNamedArgument n = {};
    n.name = name;
    n.argument = arg;
    return n;
}

// =========================================================================
// === API IMPLEMENTATION ===
// =========================================================================

extern "C" {

ALIGN_API int init_alignment_modular_tirt(const char* arch_name, const char* data_dir) {
    if (g_ctx) return 0;

    TiArch arch = TI_ARCH_CUDA;
    std::string s_arch = arch_name;
    if (s_arch == "vulkan") arch = TI_ARCH_VULKAN;
    else if (s_arch == "cpu") arch = TI_ARCH_X64;

    g_ctx = new AlignmentContext();
    g_ctx->runtime = ti_create_runtime(arch, 0);
    if (!g_ctx->runtime) return -1;

    std::string tcm_path = std::string(data_dir) + "/compute_flow_taichi_" + s_arch + ".tcm";
    g_ctx->aot_mod = ti_load_aot_module(g_ctx->runtime, tcm_path.c_str());
    if (!g_ctx->aot_mod) return -2;

    g_ctx->monolithic_graph = ti_get_aot_module_compute_graph(g_ctx->aot_mod, "align_end_to_end_3layer");
    if (!g_ctx->monolithic_graph) return -3;

    return 0;
}

ALIGN_API void clear_reference_modular_tirt() {
    if (!g_ctx) return;
    auto free_buf = [&](GpuBuffer& b) {
        if (b.mem) ti_free_memory(g_ctx->runtime, b.mem);
        b.mem = TI_NULL_HANDLE; b.bytes = 0;
    };
    free_buf(g_ctx->ref_raw); free_buf(g_ctx->comp_raw); free_buf(g_ctx->warped);
    for (auto& b : g_ctx->ref_layers) free_buf(b);
    for (auto& b : g_ctx->comp_layers) free_buf(b);
    for (auto& b : g_ctx->flow_layers) free_buf(b);
    for (auto& b : g_ctx->flow_tmp_layers) free_buf(b);
    for (auto& b : g_ctx->tmp_ref_layers) free_buf(b);
    for (auto& b : g_ctx->tmp_comp_layers) free_buf(b);
    free_buf(g_ctx->zncc_surf); free_buf(g_ctx->zncc_res);
}

ALIGN_API int set_preprocess_config_modular_tirt(float scale_gamma, int use_sharpen) {
    if (!g_ctx) return -1;
    g_ctx->s_gamma = scale_gamma;
    g_ctx->use_sharpen = use_sharpen;
    return 0;
}

ALIGN_API int set_alignment_config_modular_tirt(int downscale_factor, int min_tile_size, int n_layers) {
    if (!g_ctx) return -1;
    g_ctx->n_layers = n_layers; // Currently only 3 layers supported by AOT monolithic graph
    return 0;
}

ALIGN_API int set_reference_modular_tirt_ex(const int32_t* ref_u16, int h, int w, int channels) {
    if (!g_ctx) return -1;
    g_ctx->h = h; g_ctx->w = w; g_ctx->channels = channels;

    uint64_t raw_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
    ensure_buffer(g_ctx->runtime, g_ctx->ref_raw, raw_bytes);
    
    void* mapped = ti_map_memory(g_ctx->runtime, g_ctx->ref_raw.mem);
    std::memcpy(mapped, ref_u16, raw_bytes);
    ti_unmap_memory(g_ctx->runtime, g_ctx->ref_raw.mem);

    // Pre-allocate pyramid layers
    g_ctx->ref_layers.resize(g_ctx->n_layers);
    g_ctx->comp_layers.resize(g_ctx->n_layers);
    g_ctx->flow_layers.resize(g_ctx->n_layers);
    g_ctx->flow_tmp_layers.resize(g_ctx->n_layers);
    g_ctx->tmp_ref_layers.resize(g_ctx->n_layers);
    g_ctx->tmp_comp_layers.resize(g_ctx->n_layers);

    int cur_h = h, cur_w = w;
    for (int i = 0; i < g_ctx->n_layers; ++i) {
        ensure_buffer(g_ctx->runtime, g_ctx->ref_layers[i], (uint64_t)cur_h * cur_w * sizeof(float));
        ensure_buffer(g_ctx->runtime, g_ctx->comp_layers[i], (uint64_t)cur_h * cur_w * sizeof(float));
        ensure_buffer(g_ctx->runtime, g_ctx->flow_layers[i], (uint64_t)cur_h * cur_w * 2 * sizeof(float));
        ensure_buffer(g_ctx->runtime, g_ctx->flow_tmp_layers[i], (uint64_t)cur_h * cur_w * 2 * sizeof(float), i == 0); // Level 0 read back

        if (i < g_ctx->n_layers - 1) {
            ensure_buffer(g_ctx->runtime, g_ctx->tmp_ref_layers[i], (uint64_t)(cur_h / 2) * (cur_w / 2) * sizeof(float));
            ensure_buffer(g_ctx->runtime, g_ctx->tmp_comp_layers[i], (uint64_t)(cur_h / 2) * (cur_w / 2) * sizeof(float));
            cur_h /= 4; cur_w /= 4; // HDR+ style 4x jump
        }
    }

    ensure_buffer(g_ctx->runtime, g_ctx->zncc_surf, (uint64_t)65 * 65 * sizeof(float));
    ensure_buffer(g_ctx->runtime, g_ctx->zncc_res, 3 * sizeof(float));
    ensure_buffer(g_ctx->runtime, g_ctx->comp_raw, raw_bytes);
    ensure_buffer(g_ctx->runtime, g_ctx->warped, raw_bytes);

    return 0;
}

// Wrapper for simple call
ALIGN_API int set_reference_modular_tirt(const int32_t* ref_u16, int h, int w) {
    return set_reference_modular_tirt_ex(ref_u16, h, w, 3);
}

ALIGN_API float* compute_alignment_modular_tirt_ex(const int32_t* comp_u16, int h, int w, int tile_h, int tile_w, int n_layers, float search_dist, int channels) {
    if (!g_ctx) return nullptr;

    // Copy compare frame
    uint64_t raw_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
    void* mapped = ti_map_memory(g_ctx->runtime, g_ctx->comp_raw.mem);
    std::memcpy(mapped, comp_u16, raw_bytes);
    ti_unmap_memory(g_ctx->runtime, g_ctx->comp_raw.mem);

    // Prepare arguments for Monolithic Graph
    std::vector<TiNamedArgument> args;
    args.push_back(make_named_arg("ref_raw", make_ndarray_arg(g_ctx->ref_raw.mem, {(uint32_t)h, (uint32_t)w, (uint32_t)channels}, TI_DATA_TYPE_I32)));
    args.push_back(make_named_arg("comp_raw", make_ndarray_arg(g_ctx->comp_raw.mem, {(uint32_t)h, (uint32_t)w, (uint32_t)channels}, TI_DATA_TYPE_I32)));
    args.push_back(make_named_arg("warped", make_ndarray_arg(g_ctx->warped.mem, {(uint32_t)h, (uint32_t)w, (uint32_t)channels}, TI_DATA_TYPE_I32)));

    int cur_h = h, cur_w = w;
    for (int i = 0; i < g_ctx->n_layers; ++i) {
        args.push_back(make_named_arg(("ref_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->ref_layers[i].mem, {(uint32_t)cur_h, (uint32_t)cur_w})));
        args.push_back(make_named_arg(("comp_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->comp_layers[i].mem, {(uint32_t)cur_h, (uint32_t)cur_w})));
        args.push_back(make_named_arg(("flow_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->flow_layers[i].mem, {(uint32_t)cur_h, (uint32_t)cur_w, 2u})));
        args.push_back(make_named_arg(("flow_tmp_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->flow_tmp_layers[i].mem, {(uint32_t)cur_h, (uint32_t)cur_w, 2u})));
        
        if (i > 0) {
            args.push_back(make_named_arg(("tmp_ref_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->tmp_ref_layers[i-1].mem, {(uint32_t)cur_h * 2, (uint32_t)cur_w * 2})));
            args.push_back(make_named_arg(("tmp_comp_l" + std::to_string(i)).c_str(), make_ndarray_arg(g_ctx->tmp_comp_layers[i-1].mem, {(uint32_t)cur_h * 2, (uint32_t)cur_w * 2})));
        }
        cur_h /= 4; cur_w /= 4;
    }

    args.push_back(make_named_arg("zncc_surf", make_ndarray_arg(g_ctx->zncc_surf.mem, {65, 65})));
    args.push_back(make_named_arg("zncc_res", make_ndarray_arg(g_ctx->zncc_res.mem, {3})));

    // Scalars
    TiArgument s_norm = {}; s_norm.type = TI_ARGUMENT_TYPE_F32; s_norm.value.f32 = 1.0f / 65535.f;
    args.push_back(make_named_arg("s_norm", s_norm));
    TiArgument apply_gamma = {}; apply_gamma.type = TI_ARGUMENT_TYPE_I32; apply_gamma.value.i32 = 1;
    args.push_back(make_named_arg("apply_gamma", apply_gamma));
    TiArgument s_gamma = {}; s_gamma.type = TI_ARGUMENT_TYPE_F32; s_gamma.value.f32 = g_ctx->s_gamma;
    args.push_back(make_named_arg("s_gamma", s_gamma));
    TiArgument g_pow = {}; g_pow.type = TI_ARGUMENT_TYPE_F32; g_pow.value.f32 = 1.0f / 2.2f;
    args.push_back(make_named_arg("g_pow", g_pow));
    TiArgument slope = {}; slope.type = TI_ARGUMENT_TYPE_F32; slope.value.f32 = 4.5f;
    args.push_back(make_named_arg("slope", slope));
    TiArgument cutoff = {}; cutoff.type = TI_ARGUMENT_TYPE_F32; cutoff.value.f32 = 0.018f;
    args.push_back(make_named_arg("cutoff", cutoff));
    TiArgument sharpen = {}; sharpen.type = TI_ARGUMENT_TYPE_I32; sharpen.value.i32 = g_ctx->use_sharpen;
    args.push_back(make_named_arg("sharpen", sharpen));

    TiArgument t_h = {}; t_h.type = TI_ARGUMENT_TYPE_I32; t_h.value.i32 = tile_h;
    args.push_back(make_named_arg("tile_h", t_h));
    TiArgument t_w = {}; t_w.type = TI_ARGUMENT_TYPE_I32; t_w.value.i32 = tile_w;
    args.push_back(make_named_arg("tile_w", t_w));
    TiArgument s_rad = {}; s_rad.type = TI_ARGUMENT_TYPE_I32; s_rad.value.i32 = (int)(search_dist * 2);
    args.push_back(make_named_arg("search_radius", s_rad));
    TiArgument c_dist = {}; c_dist.type = TI_ARGUMENT_TYPE_I32; c_dist.value.i32 = (int)search_dist;
    args.push_back(make_named_arg("coarse_dist", c_dist));
    TiArgument scale = {}; scale.type = TI_ARGUMENT_TYPE_F32; scale.value.f32 = 4.0f;
    args.push_back(make_named_arg("scale", scale));
    TiArgument ds_fac = {}; ds_fac.type = TI_ARGUMENT_TYPE_I32; ds_fac.value.i32 = 4;
    args.push_back(make_named_arg("ds_fac", ds_fac));
    TiArgument z_shift = {}; z_shift.type = TI_ARGUMENT_TYPE_I32; z_shift.value.i32 = 32;
    args.push_back(make_named_arg("zncc_shift", z_shift));

    // LAUNCH
    ti_launch_compute_graph(g_ctx->runtime, g_ctx->monolithic_graph, (uint32_t)args.size(), args.data());
    ti_wait(g_ctx->runtime);

    // Read back Flow Field of Layer 0 (flow_tmp_l0 holds final refined result in many graph versions)
    // In our build_monolithic_graph, i=0 result ends up in flow_tmp_l[0] due to parabolic refine output.
    uint64_t flow_bytes = (uint64_t)h * w * 2 * sizeof(float);
    float* output_flow = (float*)malloc(flow_bytes);
    void* res_mapped = ti_map_memory(g_ctx->runtime, g_ctx->flow_tmp_layers[0].mem);
    std::memcpy(output_flow, res_mapped, flow_bytes);
    ti_unmap_memory(g_ctx->runtime, g_ctx->flow_tmp_layers[0].mem);

    return output_flow;
}

// Simple wrapper
ALIGN_API float* compute_alignment_modular_tirt(const int32_t* comp_u16, int tile_h, int tile_w, int n_layers, float search_dist) {
    return compute_alignment_modular_tirt_ex(comp_u16, g_ctx->h, g_ctx->w, tile_h, tile_w, n_layers, search_dist, 3);
}

ALIGN_API void deinit_alignment_modular_tirt() {
    if (!g_ctx) return;
    clear_reference_modular_tirt();
    if (g_ctx->runtime) ti_destroy_runtime(g_ctx->runtime);
    delete g_ctx;
    g_ctx = nullptr;
}

ALIGN_API void free_alignment_memory(void* ptr) {
    if (ptr) free(ptr);
}

} // extern "C"