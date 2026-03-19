#include <taichi/taichi_c_api.h>
#include <iostream>
#include <vector>
#include <string>
#include <map>
#include <cmath>

#ifdef _WIN32
#define ALIGN_API __declspec(dllexport)
#else
#define ALIGN_API
#endif

extern "C" {

struct AlignmentContext {
    TiRuntime runtime;
    TiModule module;
    std::map<std::string, TiKernel> kernels;
};

static AlignmentContext* g_ctx = nullptr;

struct PyramidLevel {
    TiMemory ref;
    TiMemory comp;
    TiMemory flow;
    int h, w;
};

// Helper for kernel launch
void launch_kernel_simple(TiRuntime runtime, TiKernel kernel, std::vector<TiArgument> args) {
    ti_launch_kernel(runtime, kernel, (uint32_t)args.size(), args.data());
}

TiArgument make_ndarray_arg(TiMemory mem, const std::vector<uint32_t>& shape) {
    TiNdArray ndarray = {};
    ndarray.memory = mem;
    ndarray.shape.num_dims = (uint32_t)shape.size();
    for (size_t i = 0; i < shape.size(); ++i) ndarray.shape.dims[i] = shape[i];
    // Layout and other fields are often default 0 for contiguous
    TiArgument arg = {};
    arg.type = TI_ARGUMENT_TYPE_NDARRAY;
    arg.value.ndarray = ndarray;
    return arg;
}

TiArgument make_i32_arg(int32_t val) {
    TiArgument arg = {};
    arg.type = TI_ARGUMENT_TYPE_I32;
    arg.value.i32 = val;
    return arg;
}

TiArgument make_f32_arg(float val) {
    TiArgument arg = {};
    arg.type = TI_ARGUMENT_TYPE_F32;
    arg.value.f32 = val;
    return arg;
}

ALIGN_API int init_alignment_tirt(const char* arch_name, const char* tcm_path) {
    if (g_ctx) return 0;

    TiArch arch = TI_ARCH_X64;
    std::string s_arch = arch_name;
    if (s_arch == "cuda") arch = TI_ARCH_CUDA;
    else if (s_arch == "vulkan") arch = TI_ARCH_VULKAN;
    else if (s_arch == "cpu") arch = TI_ARCH_X64;

    g_ctx = new AlignmentContext();
    g_ctx->runtime = ti_create_runtime(arch, 0);
    if (!g_ctx->runtime) return -1;

    g_ctx->module = ti_load_aot_module(g_ctx->runtime, tcm_path);
    if (!g_ctx->module) return -2;

    const char* kernel_names[] = {
        "_initialize_coarsest_flow_kernel",
        "_block_search_kernel",
        "_search_coarse_level_kernel",
        "_search_fine_level_kernel",
        "_parabolic_subpixel_refinement_kernel",
        "_downsample_2x_kernel",
        "_upsample_flow_kernel"
    };

    for (const char* name : kernel_names) {
        g_ctx->kernels[name] = ti_get_module_kernel(g_ctx->module, name);
    }

    return 0;
}

ALIGN_API float* compute_alignment_flow_tirt(
    const float* ref_data, 
    const float* comp_data, 
    int h, int w, 
    int tile_h, int tile_w, 
    int n_layers,
    float search_dist
) {
    if (!g_ctx) return nullptr;
    TiRuntime runtime = g_ctx->runtime;

    std::vector<PyramidLevel> pyramid(n_layers);
    int curr_h = h, curr_w = w;

    // 1. Allocate & Build Pyramid
    for (int i = 0; i < n_layers; ++i) {
        pyramid[i].h = curr_h;
        pyramid[i].w = curr_w;

        TiMemoryAllocateInfo info = {};
        info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
        
        info.size = curr_h * curr_w * sizeof(float);
        pyramid[i].ref = ti_allocate_memory(runtime, &info);
        pyramid[i].comp = ti_allocate_memory(runtime, &info);

        info.size = curr_h * curr_w * 2 * sizeof(float);
        pyramid[i].flow = ti_allocate_memory(runtime, &info);

        if (i == 0) {
            ti_copy_host_to_memory(runtime, pyramid[0].ref, {0, (uint64_t)h * w * sizeof(float), (void*)ref_data});
            ti_copy_host_to_memory(runtime, pyramid[0].comp, {0, (uint64_t)h * w * sizeof(float), (void*)comp_data});
        } else {
            // Downsample from i-1 to i
            // _downsample_2x_kernel(src, dst, src_h, src_w)
            std::vector<TiArgument> args_ref = {
                make_ndarray_arg(pyramid[i-1].ref, {(uint32_t)pyramid[i-1].h, (uint32_t)pyramid[i-1].w}),
                make_ndarray_arg(pyramid[i].ref, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_i32_arg(pyramid[i-1].h), make_i32_arg(pyramid[i-1].w)
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_downsample_2x_kernel"], args_ref);

            std::vector<TiArgument> args_comp = {
                make_ndarray_arg(pyramid[i-1].comp, {(uint32_t)pyramid[i-1].h, (uint32_t)pyramid[i-1].w}),
                make_ndarray_arg(pyramid[i].comp, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_i32_arg(pyramid[i-1].h), make_i32_arg(pyramid[i-1].w)
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_downsample_2x_kernel"], args_comp);
        }
        curr_h /= 2; curr_w /= 2;
    }

    // 2. Coarse-to-Fine Alignment
    for (int i = n_layers - 1; i >= 0; --i) {
        if (i == n_layers - 1) {
            // Coarsest: Init Flow & Block Search
            std::vector<TiArgument> init_args = {
                make_ndarray_arg(pyramid[i].flow, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w, 2}),
                make_i32_arg(pyramid[i].h), make_i32_arg(pyramid[i].w)
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_initialize_coarsest_flow_kernel"], init_args);

            std::vector<TiArgument> search_args = {
                make_ndarray_arg(pyramid[i].ref, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_ndarray_arg(pyramid[i].comp, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_ndarray_arg(pyramid[i].flow, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w, 2}),
                make_i32_arg(pyramid[i].h), make_i32_arg(pyramid[i].w),
                make_i32_arg(tile_h), make_i32_arg(tile_w),
                make_f32_arg(search_dist)
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_block_search_kernel"], search_args);
        } else {
            // Upsample flow from i+1 to i
            std::vector<TiArgument> up_args = {
                make_ndarray_arg(pyramid[i+1].flow, {(uint32_t)pyramid[i+1].h, (uint32_t)pyramid[i+1].w, 2}),
                make_ndarray_arg(pyramid[i].flow, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w, 2}),
                make_i32_arg(pyramid[i].h), make_i32_arg(pyramid[i].w),
                make_i32_arg(2) // scale factor
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_upsample_flow_kernel"], up_args);

            // Refine at Level i
            // _search_fine_level_kernel(ref, comp, flow, prev_flow, refined_flow, ...)
            // (Simplified: for now reuse _block_search or dedicated refinement if added in AOT)
            // Using search_args pattern as base
            std::vector<TiArgument> refine_args = {
                make_ndarray_arg(pyramid[i].ref, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_ndarray_arg(pyramid[i].comp, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w}),
                make_ndarray_arg(pyramid[i].flow, {(uint32_t)pyramid[i].h, (uint32_t)pyramid[i].w, 2}),
                make_i32_arg(pyramid[i].h), make_i32_arg(pyramid[i].w),
                make_i32_arg(tile_h), make_i32_arg(tile_w),
                make_f32_arg(search_dist / 2.0f) // tighter search at fine levels
            };
            launch_kernel_simple(runtime, g_ctx->kernels["_search_coarse_level_kernel"], refine_args);
        }
    }

    // 3. Subpixel Refinement (Finest Level)
    std::vector<TiArgument> subpix_args = {
        make_ndarray_arg(pyramid[0].ref, {(uint32_t)pyramid[0].h, (uint32_t)pyramid[0].w}),
        make_ndarray_arg(pyramid[0].comp, {(uint32_t)pyramid[0].h, (uint32_t)pyramid[0].w}),
        make_ndarray_arg(pyramid[0].flow, {(uint32_t)pyramid[0].h, (uint32_t)pyramid[0].w, 2}),
        make_i32_arg(pyramid[0].h), make_i32_arg(pyramid[0].w),
        make_i32_arg(tile_h), make_i32_arg(tile_w)
    };
    launch_kernel_simple(runtime, g_ctx->kernels["_parabolic_subpixel_refinement_kernel"], subpix_args);

    // 4. Download result from Level 0
    float* out_flow = (float*)malloc(h * w * 2 * sizeof(float));
    ti_copy_memory_to_host(runtime, pyramid[0].flow, {0, (uint64_t)h * w * 2 * sizeof(float), out_flow});

    // 5. Cleanup
    for (int i = 0; i < n_layers; ++i) {
        ti_free_memory(runtime, pyramid[i].ref);
        ti_free_memory(runtime, pyramid[i].comp);
        ti_free_memory(runtime, pyramid[i].flow);
    }
    ti_submit(runtime); // Ensure all work is submitted
    ti_wait(runtime);

    return out_flow;
}

ALIGN_API void deinit_alignment_tirt() {
    if (g_ctx) {
        ti_destroy_runtime(g_ctx->runtime);
        delete g_ctx;
        g_ctx = nullptr;
    }
}

ALIGN_API void free_flow_memory(float* ptr) {
    if (ptr) free(ptr);
}

} // extern "C"
