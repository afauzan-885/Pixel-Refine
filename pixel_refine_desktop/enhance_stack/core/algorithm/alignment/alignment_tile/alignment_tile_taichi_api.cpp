#include "alignment_tile_taichi_api.h"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <limits>
#include <map>
#include <string>
#include <taichi/taichi.h>
#include <vector>

struct PyramidLevel {
  TiMemory ref = TI_NULL_HANDLE;
  TiMemory comp = TI_NULL_HANDLE;
  TiMemory flow = TI_NULL_HANDLE;
  TiMemory flow_temp = TI_NULL_HANDLE;
  uint64_t ref_bytes = 0;
  uint64_t comp_bytes = 0;
  uint64_t flow_bytes = 0;
  uint64_t flow_temp_bytes = 0;
  int h = 0, w = 0;
};

struct AlignmentContext {
  TiRuntime runtime;
  TiAotModule preprocess_mod;
  TiAotModule flow_mod;
  TiAotModule warp_mod;
  std::map<std::string, TiKernel> kernels;
  std::map<std::string, TiComputeGraph> graphs;

  // Persistent GPU state for reference
  TiMemory ref_raw_gpu = TI_NULL_HANDLE;
  TiMemory ref_norm_gpu = TI_NULL_HANDLE;
  TiMemory comp_raw_gpu = TI_NULL_HANDLE;
  TiMemory comp_norm_gpu = TI_NULL_HANDLE;
  TiMemory warped_gpu = TI_NULL_HANDLE;
  uint64_t ref_raw_bytes = 0;
  uint64_t ref_norm_bytes = 0;
  uint64_t comp_raw_bytes = 0;
  uint64_t comp_norm_bytes = 0;
  uint64_t warped_bytes = 0;
  int h = 0, w = 0;
  int channels = 1;

  // Persistent temporary caches
  std::vector<PyramidLevel> pyramid_cache;
  TiMemory safe_prev_flow = TI_NULL_HANDLE;
  uint64_t safe_prev_flow_bytes = 0;
  TiMemory zncc_surface_gpu = TI_NULL_HANDLE;
  uint64_t zncc_surface_bytes = 0;
  int zncc_surface_side = 0;

  TiMemory zncc_results_gpu = TI_NULL_HANDLE;
  uint64_t zncc_results_bytes = 0;

  // Intermediate cascading downsample buffers
  TiMemory temp_down_ref = TI_NULL_HANDLE;
  uint64_t temp_down_ref_bytes = 0;
  TiMemory temp_down_comp = TI_NULL_HANDLE;
  uint64_t temp_down_comp_bytes = 0;

  // Shared preprocess config (mirrors preprocess_pipeline_gpu knobs)
  float preprocess_scale_gamma = 1.0f; // 1.0 = gamma off
  int preprocess_use_sharpen = 0;

  // Shared alignment config (mirrors compute_flow/ImageAlignmentConfig knobs)
  int alignment_downscale_factor = 4;
  int alignment_min_tile_size = 8;
};

static AlignmentContext *g_ctx = nullptr;

namespace {

inline std::vector<uint32_t> _shape_2d(int h, int w) {
  return {(uint32_t)h, (uint32_t)w};
}

inline std::vector<uint32_t> _shape_flow(int h, int w) {
  return {(uint32_t)h, (uint32_t)w, 2u};
}

inline uint64_t _bytes_f32_2d(int h, int w) {
  return (uint64_t)h * w * sizeof(float);
}

inline uint64_t _bytes_f32_flow(int h, int w) {
  return (uint64_t)h * w * 2u * sizeof(float);
}

inline void _copy_field_gpu(TiRuntime runtime, TiMemory src, TiMemory dst,
                            uint64_t bytes) {
  TiMemorySlice src_slice = {src, 0, bytes};
  TiMemorySlice dst_slice = {dst, 0, bytes};
  ti_copy_memory_device_to_device(runtime, &src_slice, &dst_slice);
}

inline bool _ensure_memory(TiRuntime runtime, TiMemory &mem,
                           uint64_t &current_size, uint64_t size,
                           bool host_write = false, bool host_read = false) {
  if (mem != TI_NULL_HANDLE && current_size != size) {
    ti_free_memory(runtime, mem);
    mem = TI_NULL_HANDLE;
    current_size = 0;
  }
  if (mem != TI_NULL_HANDLE && current_size == size)
    return true;

  TiMemoryAllocateInfo info = {};
  info.size = size;
  info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
  info.host_write = host_write ? TI_TRUE : TI_FALSE;
  info.host_read = host_read ? TI_TRUE : TI_FALSE;
  mem = ti_allocate_memory(runtime, &info);
  if (mem == TI_NULL_HANDLE)
    return false;
  current_size = size;
  return true;
}

inline bool _copy_host_to_gpu(TiRuntime runtime, TiMemory dst, const void *src,
                              uint64_t bytes) {
  if (dst == TI_NULL_HANDLE || !src || bytes == 0)
    return false;
  void *mapped = ti_map_memory(runtime, dst);
  if (!mapped)
    return false;
  std::memcpy(mapped, src, bytes);
  ti_unmap_memory(runtime, dst);
  return true;
}

inline void _release_pyramid_level(TiRuntime runtime, PyramidLevel &lvl) {
  if (lvl.ref != TI_NULL_HANDLE) {
    ti_free_memory(runtime, lvl.ref);
    lvl.ref = TI_NULL_HANDLE;
    lvl.ref_bytes = 0;
  }
  if (lvl.comp != TI_NULL_HANDLE) {
    ti_free_memory(runtime, lvl.comp);
    lvl.comp = TI_NULL_HANDLE;
    lvl.comp_bytes = 0;
  }
  if (lvl.flow != TI_NULL_HANDLE) {
    ti_free_memory(runtime, lvl.flow);
    lvl.flow = TI_NULL_HANDLE;
    lvl.flow_bytes = 0;
  }
  if (lvl.flow_temp != TI_NULL_HANDLE) {
    ti_free_memory(runtime, lvl.flow_temp);
    lvl.flow_temp = TI_NULL_HANDLE;
    lvl.flow_temp_bytes = 0;
  }
  lvl.h = 0;
  lvl.w = 0;
}

inline bool
_ensure_pyramid_cache(AlignmentContext *ctx,
                      const std::vector<std::pair<int, int>> &shapes) {
  if (!ctx)
    return false;
  TiRuntime runtime = ctx->runtime;
  if (ctx->pyramid_cache.size() < shapes.size()) {
    ctx->pyramid_cache.resize(shapes.size());
  }
  for (size_t i = 0; i < shapes.size(); ++i) {
    PyramidLevel &p = ctx->pyramid_cache[i];
    p.h = shapes[i].first;
    p.w = shapes[i].second;
    const uint64_t f2d_bytes = _bytes_f32_2d(p.h, p.w);
    const uint64_t flow_bytes = _bytes_f32_flow(p.h, p.w);
    if (!_ensure_memory(runtime, p.ref, p.ref_bytes, f2d_bytes))
      return false;
    if (!_ensure_memory(runtime, p.comp, p.comp_bytes, f2d_bytes))
      return false;
    if (!_ensure_memory(runtime, p.flow, p.flow_bytes, flow_bytes))
      return false;
    if (!_ensure_memory(runtime, p.flow_temp, p.flow_temp_bytes, flow_bytes))
      return false;
  }

  // Allocation for intermediate cascading buffers (max needed is (h0/2)*(w0/2))
  if (!shapes.empty() && ctx->alignment_downscale_factor > 2) {
    uint64_t max_inter_bytes =
        _bytes_f32_2d(shapes[0].first / 2, shapes[0].second / 2);
    if (!_ensure_memory(runtime, ctx->temp_down_ref, ctx->temp_down_ref_bytes,
                        max_inter_bytes))
      return false;
    if (!_ensure_memory(runtime, ctx->temp_down_comp, ctx->temp_down_comp_bytes,
                        max_inter_bytes))
      return false;
  }

  return true;
}

} // namespace

// Helper for kernel launch
void launch_kernel_simple(TiRuntime runtime, TiKernel kernel,
                          std::vector<TiArgument> args) {
  if (!kernel)
    return;
  ti_launch_kernel(runtime, kernel, (uint32_t)args.size(), args.data());
}

TiArgument make_ndarray_arg(TiMemory mem, const std::vector<uint32_t> &shape) {
  TiNdArray ndarray = {};
  ndarray.memory = mem;
  ndarray.shape.dim_count = (uint32_t)shape.size();
  for (size_t i = 0; i < shape.size(); ++i)
    ndarray.shape.dims[i] = shape[i];
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

TiNamedArgument make_named_arg(const char *name, TiArgument arg) {
  TiNamedArgument named_arg = {};
  named_arg.name = name;
  named_arg.argument = arg;
  return named_arg;
}

bool _fused_full_pipeline_i32_aot_from_gpu(AlignmentContext *ctx,
                                           TiMemory src_i32_gpu, int h, int w,
                                           int channels, TiMemory dst_f32_2d) {
  if (!ctx || src_i32_gpu == TI_NULL_HANDLE || h <= 0 || w <= 0 ||
      dst_f32_2d == TI_NULL_HANDLE)
    return false;
  TiRuntime runtime = ctx->runtime;
  const char *kernel_key = (channels == 3) ? "_fused_full_pipeline_i32_3d_aot"
                                           : "_fused_full_pipeline_i32_2d_aot";
  TiKernel kernel = ctx->kernels[kernel_key];
  if (kernel == TI_NULL_HANDLE)
    return false;
  std::vector<TiArgument> args;
  if (channels == 3) {
    args = {
        make_ndarray_arg(src_i32_gpu, {(uint32_t)h, (uint32_t)w, 3u}),
        make_ndarray_arg(dst_f32_2d, _shape_2d(h, w)),
        make_i32_arg(h),
        make_i32_arg(w), // src_h, src_w
        make_i32_arg(h),
        make_i32_arg(w),                           // dst_h, dst_w
        make_f32_arg(65535.0f),                    // scale_norm
        make_f32_arg(ctx->preprocess_scale_gamma), // scale_gamma
        make_f32_arg(2.22f),                       // gamma_pow
        make_f32_arg(4.5f),                        // slope
        make_f32_arg(0.018f),                      // cutoff
        make_i32_arg(ctx->preprocess_use_sharpen)  // use_sharpen
    };
  } else {
    args = {
        make_ndarray_arg(src_i32_gpu, _shape_2d(h, w)),
        make_ndarray_arg(dst_f32_2d, _shape_2d(h, w)),
        make_i32_arg(h),
        make_i32_arg(w), // src_h, src_w
        make_i32_arg(h),
        make_i32_arg(w),                           // dst_h, dst_w
        make_f32_arg(65535.0f),                    // scale_norm
        make_f32_arg(ctx->preprocess_scale_gamma), // scale_gamma
        make_f32_arg(2.22f),                       // gamma_pow
        make_f32_arg(4.5f),                        // slope
        make_f32_arg(0.018f),                      // cutoff
        make_i32_arg(ctx->preprocess_use_sharpen)  // use_sharpen
    };
  }
  launch_kernel_simple(runtime, kernel, args);
  return true;
}

// Backward-compatible shim for legacy call-sites (2D only).
bool _fused_full_pipeline_i32_2d_aot(AlignmentContext *ctx,
                                     const int32_t *src_i32, int h, int w,
                                     TiMemory dst_f32_2d) {
  if (!ctx || !src_i32 || h <= 0 || w <= 0 || dst_f32_2d == TI_NULL_HANDLE)
    return false;
  TiRuntime runtime = ctx->runtime;
  TiMemoryAllocateInfo src_info = {};
  src_info.size = (uint64_t)h * w * sizeof(int32_t);
  src_info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
  src_info.host_write = TI_TRUE;
  TiMemory src_gpu = ti_allocate_memory(runtime, &src_info);
  if (src_gpu == TI_NULL_HANDLE)
    return false;
  if (!_copy_host_to_gpu(runtime, src_gpu, src_i32, src_info.size)) {
    ti_free_memory(runtime, src_gpu);
    return false;
  }
  bool ok =
      _fused_full_pipeline_i32_aot_from_gpu(ctx, src_gpu, h, w, 1, dst_f32_2d);
  ti_free_memory(runtime, src_gpu);
  return ok;
}

bool _global_translate_zncc(AlignmentContext *ctx, TiMemory ref_f32_2d,
                            TiMemory comp_f32_2d, int h, int w,
                            int requested_max_shift, int &out_dx, int &out_dy,
                            float &out_cost) {
  out_dx = 0;
  out_dy = 0;
  out_cost = 1e10f;

  if (!ctx || ref_f32_2d == TI_NULL_HANDLE || comp_f32_2d == TI_NULL_HANDLE)
    return false;
  TiKernel k = ctx->kernels["_compute_global_zncc_surface"];
  if (k == TI_NULL_HANDLE)
    return false;

  int max_shift = requested_max_shift;
  max_shift = std::min(max_shift, std::max(0, (h - 1) / 2));
  max_shift = std::min(max_shift, std::max(0, (w - 1) / 2));
  if (max_shift <= 0)
    return true;

  const int size = 2 * max_shift + 1;
  const uint64_t surface_bytes = (uint64_t)size * size * sizeof(float);
  if (!_ensure_memory(ctx->runtime, ctx->zncc_surface_gpu,
                      ctx->zncc_surface_bytes, surface_bytes, false, true))
    return false;
  ctx->zncc_surface_side = size;

  std::vector<TiArgument> args = {
      make_ndarray_arg(ref_f32_2d, _shape_2d(h, w)),
      make_ndarray_arg(comp_f32_2d, _shape_2d(h, w)),
      make_ndarray_arg(ctx->zncc_surface_gpu, {(uint32_t)size, (uint32_t)size}),
      make_i32_arg(max_shift),
      make_i32_arg(h),
      make_i32_arg(w),
  };
  launch_kernel_simple(ctx->runtime, k, args);
  ti_wait(ctx->runtime);

  void *mapped = ti_map_memory(ctx->runtime, ctx->zncc_surface_gpu);
  if (!mapped) {
    return false;
  }
  const float *surf = static_cast<const float *>(mapped);

  float best = std::numeric_limits<float>::infinity();
  int best_x = 0, best_y = 0;
  for (int yy = 0; yy < size; ++yy) {
    for (int xx = 0; xx < size; ++xx) {
      float c = surf[yy * size + xx];
      if (c < best) {
        best = c;
        best_x = xx;
        best_y = yy;
      }
    }
  }
  ti_unmap_memory(ctx->runtime, ctx->zncc_surface_gpu);

  out_dx = best_x - max_shift;
  out_dy = best_y - max_shift;
  out_cost = best;
  return true;
}

extern "C" {

ALIGN_API int init_alignment_modular_tirt(const char *arch_name,
                                          const char *data_dir) {
  if (!arch_name || !data_dir)
    return -2;
  if (g_ctx)
    return 0;

  TiArch arch = TI_ARCH_X64;
  std::string s_arch = arch_name;
  if (s_arch == "cuda")
    arch = TI_ARCH_CUDA;
  else if (s_arch == "vulkan")
    arch = TI_ARCH_VULKAN;
  else if (s_arch == "cpu")
    arch = TI_ARCH_X64;

  g_ctx = new AlignmentContext();
  g_ctx->runtime = ti_create_runtime(arch, 0);
  if (!g_ctx->runtime)
    return -1;

  std::string base_path = data_dir;
  if (base_path.back() != '/' && base_path.back() != '\\')
    base_path += "/";

  std::string preprocess_path = base_path + "preprocess_" + s_arch + ".tcm";
  std::string flow_path = base_path + "compute_flow_" + s_arch + ".tcm";
  std::string warp_path = base_path + "warp_" + s_arch + ".tcm";

  g_ctx->preprocess_mod =
      ti_load_aot_module(g_ctx->runtime, preprocess_path.c_str());
  g_ctx->flow_mod = ti_load_aot_module(g_ctx->runtime, flow_path.c_str());
  g_ctx->warp_mod = ti_load_aot_module(g_ctx->runtime, warp_path.c_str());

  if (!g_ctx->preprocess_mod || !g_ctx->flow_mod || !g_ctx->warp_mod)
    return -2;

  // Load Graphs
  auto load_g = [&](TiAotModule mod, const char *name, const char *key) {
    TiComputeGraph g = ti_get_aot_module_compute_graph(mod, name);
    if (g == TI_NULL_HANDLE) {
      std::cerr << "[TiRT Error] Failed to load graph: " << name << " (" << key
                << ")" << std::endl;
    } else {
      g_ctx->graphs[key] = g;
    }
    return g != TI_NULL_HANDLE;
  };

  struct KernelSpec {
    TiAotModule mod;
    const char *kernel_name;
    const char *key;
  };
  const std::vector<KernelSpec> kernel_specs = {
      {g_ctx->preprocess_mod, "_fused_full_pipeline_i32_2d_aot",
       "_fused_full_pipeline_i32_2d_aot"},
      {g_ctx->preprocess_mod, "_fused_full_pipeline_i32_3d_aot",
       "_fused_full_pipeline_i32_3d_aot"},
      {g_ctx->flow_mod, "_initialize_coarsest_flow_kernel",
       "_initialize_coarsest_flow_kernel"},
      {g_ctx->flow_mod, "_block_search_kernel", "_block_search_kernel"},
      {g_ctx->flow_mod, "_search_coarse_level_kernel",
       "_search_coarse_level_kernel"},
      {g_ctx->flow_mod, "_search_fine_level_kernel",
       "_search_fine_level_kernel"},
      {g_ctx->flow_mod, "_parabolic_subpixel_refinement_kernel",
       "_parabolic_subpixel_refinement_kernel"},
      {g_ctx->flow_mod, "_downsample_2x_kernel", "_downsample_2x_kernel"},
      {g_ctx->flow_mod, "_upsample_flow_kernel", "_upsample_flow_kernel"},
      {g_ctx->flow_mod, "_compute_global_zncc_surface",
       "_compute_global_zncc_surface"},
      {g_ctx->warp_mod, "_warp_guided_i32_aot", "_warp_guided_i32_aot"},
      {g_ctx->warp_mod, "_warp_guided_i32_rgb_aot", "_warp_guided_i32_rgb_aot"},
  };

  bool ok = true;
  for (const auto &spec : kernel_specs) {
    ok &= load_k(spec.mod, spec.kernel_name, spec.key);
  }

  // Load monolithic graphs
  load_g(g_ctx->flow_mod, "compute_flow_3layer", "compute_flow_3layer");
  load_g(g_ctx->flow_mod, "compute_flow_4layer", "compute_flow_4layer");

  if (!ok) {
    std::cerr << "[TiRT Error] One or more kernels failed to load!"
              << std::endl;
    return -3;
  }

  return 0;
}

ALIGN_API int set_preprocess_config_modular_tirt(float scale_gamma,
                                                 int use_sharpen) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  if (scale_gamma <= 0.0f)
    scale_gamma = 1.0f;
  g_ctx->preprocess_scale_gamma = scale_gamma;
  g_ctx->preprocess_use_sharpen = (use_sharpen != 0) ? 1 : 0;
  return 0;
}

ALIGN_API int set_alignment_config_modular_tirt(int downscale_factor,
                                                int min_tile_size) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  // Keep defaults when caller passes invalid values.
  if (downscale_factor < 2)
    downscale_factor = 4;
  if (min_tile_size < 1)
    min_tile_size = 8;
  g_ctx->alignment_downscale_factor = downscale_factor;
  g_ctx->alignment_min_tile_size = min_tile_size;
  return 0;
}

ALIGN_API void clear_reference_modular_tirt() {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return;
  if (g_ctx->ref_raw_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->ref_raw_gpu);
    g_ctx->ref_raw_gpu = TI_NULL_HANDLE;
    g_ctx->ref_raw_bytes = 0;
  }
  if (g_ctx->ref_norm_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->ref_norm_gpu);
    g_ctx->ref_norm_gpu = TI_NULL_HANDLE;
    g_ctx->ref_norm_bytes = 0;
  }
  if (g_ctx->comp_raw_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->comp_raw_gpu);
    g_ctx->comp_raw_gpu = TI_NULL_HANDLE;
    g_ctx->comp_raw_bytes = 0;
  }
  if (g_ctx->comp_norm_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->comp_norm_gpu);
    g_ctx->comp_norm_gpu = TI_NULL_HANDLE;
    g_ctx->comp_norm_bytes = 0;
  }
  if (g_ctx->warped_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->warped_gpu);
    g_ctx->warped_gpu = TI_NULL_HANDLE;
    g_ctx->warped_bytes = 0;
  }
  if (g_ctx->safe_prev_flow != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->safe_prev_flow);
    g_ctx->safe_prev_flow = TI_NULL_HANDLE;
    g_ctx->safe_prev_flow_bytes = 0;
  }
  if (g_ctx->zncc_surface_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->zncc_surface_gpu);
    g_ctx->zncc_surface_gpu = TI_NULL_HANDLE;
    g_ctx->zncc_surface_bytes = 0;
    g_ctx->zncc_surface_side = 0;
  }
  if (g_ctx->zncc_results_gpu != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->zncc_results_gpu);
    g_ctx->zncc_results_gpu = TI_NULL_HANDLE;
    g_ctx->zncc_results_bytes = 0;
  }
  if (g_ctx->temp_down_ref != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->temp_down_ref);
    g_ctx->temp_down_ref = TI_NULL_HANDLE;
    g_ctx->temp_down_ref_bytes = 0;
  }
  if (g_ctx->temp_down_comp != TI_NULL_HANDLE) {
    ti_free_memory(g_ctx->runtime, g_ctx->temp_down_comp);
    g_ctx->temp_down_comp = TI_NULL_HANDLE;
    g_ctx->temp_down_comp_bytes = 0;
  }
  for (auto &lvl : g_ctx->pyramid_cache) {
    _release_pyramid_level(g_ctx->runtime, lvl);
  }
  g_ctx->pyramid_cache.clear();
}

ALIGN_API int set_reference_modular_tirt(const int32_t *ref_u16, int h, int w) {
  return set_reference_modular_tirt_ex(ref_u16, h, w, 1);
}

ALIGN_API int set_reference_modular_tirt_ex(const int32_t *ref_u16, int h,
                                            int w, int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  if (!ref_u16 || h <= 0 || w <= 0)
    return -2;
  if (channels != 1 && channels != 3)
    channels = 1;

  // Reset persistent buffers if geometry/layout changes.
  if (g_ctx->h != h || g_ctx->w != w || g_ctx->channels != channels) {
    clear_reference_modular_tirt();
  }

  g_ctx->h = h;
  g_ctx->w = w;
  g_ctx->channels = channels;

  const uint64_t raw_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  const uint64_t norm_bytes = (uint64_t)h * w * sizeof(float);
  if (!_ensure_memory(g_ctx->runtime, g_ctx->ref_raw_gpu, g_ctx->ref_raw_bytes,
                      raw_bytes, true, false))
    return -3;
  if (!_ensure_memory(g_ctx->runtime, g_ctx->ref_norm_gpu,
                      g_ctx->ref_norm_bytes, norm_bytes, false, false))
    return -4;

  if (!_copy_host_to_gpu(g_ctx->runtime, g_ctx->ref_raw_gpu, ref_u16,
                         raw_bytes))
    return -5;

  if (!_fused_full_pipeline_i32_aot_from_gpu(g_ctx, g_ctx->ref_raw_gpu, h, w,
                                             channels, g_ctx->ref_norm_gpu)) {
    return -2;
  }

  return 0;
}

ALIGN_API int32_t *compute_alignment_modular_tirt(const int32_t *comp_u16,
                                                  int tile_h, int tile_w,
                                                  int n_layers,
                                                  float search_dist) {
  return compute_alignment_modular_tirt_ex(comp_u16, tile_h, tile_w, n_layers,
                                           search_dist, 1);
}

ALIGN_API int32_t *compute_alignment_modular_tirt_ex(const int32_t *comp_u16,
                                                     int tile_h, int tile_w,
                                                     int n_layers,
                                                     float search_dist,
                                                     int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE ||
      g_ctx->ref_norm_gpu == TI_NULL_HANDLE)
    return nullptr;
  if (!comp_u16)
    return nullptr;
  if (channels != 1 && channels != 3)
    channels = 1;
  if (channels != g_ctx->channels) {
    std::cerr
        << "[TiRT Error] Channel mismatch between reference and current frame."
        << std::endl;
    return nullptr;
  }
  TiRuntime runtime = g_ctx->runtime;
  int h = g_ctx->h, w = g_ctx->w;

  // 1. Prepare Comp Normalized
  const uint64_t raw_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  const uint64_t norm_bytes = (uint64_t)h * w * sizeof(float);
  const uint64_t warped_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  if (!_ensure_memory(runtime, g_ctx->comp_raw_gpu, g_ctx->comp_raw_bytes,
                      raw_bytes, true, false))
    return nullptr;
  if (!_ensure_memory(runtime, g_ctx->comp_norm_gpu, g_ctx->comp_norm_bytes,
                      norm_bytes, false, false))
    return nullptr;
  if (!_ensure_memory(runtime, g_ctx->warped_gpu, g_ctx->warped_bytes,
                      warped_bytes, false, true))
    return nullptr;

  if (!_copy_host_to_gpu(runtime, g_ctx->comp_raw_gpu, comp_u16, raw_bytes))
    return nullptr;

  if (!_fused_full_pipeline_i32_aot_from_gpu(g_ctx, g_ctx->comp_raw_gpu, h, w,
                                             channels, g_ctx->comp_norm_gpu)) {
    return nullptr;
  }

  // 2. Pyramid & Alignment (mirrors build_image_pyramid_gpu +
  // process_single_layer workflow)
  const int downscale_factor = g_ctx->alignment_downscale_factor;
  const int min_pyramid_size = 32; // taichi_algorithm.pyramid.MIN_PYRAMID_SIZE
  const int min_tile_size = g_ctx->alignment_min_tile_size;
  if (n_layers < 1)
    n_layers = 1;

  // Calculate cascading steps per level (e.g., 2 steps for 4x downscale)
  int steps_per_level = 1;
  if (downscale_factor > 2) {
    steps_per_level = (int)std::lround(std::log2((double)downscale_factor));
    if (steps_per_level < 1)
      steps_per_level = 1;
  }

  std::vector<std::pair<int, int>> level_shapes;
  level_shapes.reserve((size_t)n_layers);
  level_shapes.push_back({h, w});
  for (int lvl = 1; lvl < n_layers; ++lvl) {
    const int prev_h = level_shapes.back().first;
    const int prev_w = level_shapes.back().second;
    const int next_h =
        (int)std::lround((double)prev_h / (double)downscale_factor);
    const int next_w =
        (int)std::lround((double)prev_w / (double)downscale_factor);
    if (next_h < min_pyramid_size || next_w < min_pyramid_size)
      break;
    level_shapes.push_back({next_h, next_w});
  }

  const int effective_layers = (int)level_shapes.size();
  if (!_ensure_pyramid_cache(g_ctx, level_shapes)) {
    return nullptr;
  }
  std::vector<PyramidLevel> &pyramid = g_ctx->pyramid_cache;

  for (int i = 0; i < effective_layers; ++i) {
    if (i == 0) {
      _copy_field_gpu(runtime, g_ctx->ref_norm_gpu, pyramid[0].ref,
                      _bytes_f32_2d(h, w));
      _copy_field_gpu(runtime, g_ctx->comp_norm_gpu, pyramid[0].comp,
                      _bytes_f32_2d(h, w));
    } else {
      // Cascaded Gaussian Downsampling (mirroring Python steps_per_level)
      auto cascade_down = [&](TiMemory src_root, TiMemory dst_root, int h_in,
                              int w_in, int h_final, int w_final,
                              TiMemory temp_buf) {
        TiMemory current_src = src_root;
        int cur_h = h_in;
        int cur_w = w_in;

        for (int s = 0; s < steps_per_level; ++s) {
          int target_h = (s == steps_per_level - 1) ? h_final : (cur_h / 2);
          int target_w = (s == steps_per_level - 1) ? w_final : (cur_w / 2);
          TiMemory current_dst = (s == steps_per_level - 1) ? dst_root : temp_buf;

          std::vector<TiArgument> args = {
              make_ndarray_arg(current_src, _shape_2d(cur_h, cur_w)),
              make_ndarray_arg(current_dst, _shape_2d(target_h, target_w)),
              make_i32_arg(cur_h),
              make_i32_arg(cur_w),
              make_i32_arg(target_h),
              make_i32_arg(target_w)};

          launch_kernel_simple(runtime, g_ctx->kernels["_downsample_2x_kernel"], args);

          current_src = current_dst;
          cur_h = target_h;
          cur_w = target_w;
        }
      };

      cascade_down(pyramid[i - 1].ref, pyramid[i].ref, pyramid[i - 1].h,
                   pyramid[i - 1].w, pyramid[i].h, pyramid[i].w,
                   g_ctx->temp_down_ref);
      cascade_down(pyramid[i - 1].comp, pyramid[i].comp, pyramid[i - 1].h,
                   pyramid[i - 1].w, pyramid[i].h, pyramid[i].w,
                   g_ctx->temp_down_comp);
    }
  }

  TiMemory safe_prev_flow = TI_NULL_HANDLE;
  if (effective_layers == 1) {
    if (!_ensure_memory(runtime, g_ctx->safe_prev_flow,
                        g_ctx->safe_prev_flow_bytes,
                        (uint64_t)1 * 1 * 2 * sizeof(float), true, false)) {
      return nullptr;
    }
    safe_prev_flow = g_ctx->safe_prev_flow;
    if (safe_prev_flow != TI_NULL_HANDLE) {
      void *tiny_ptr = ti_map_memory(runtime, safe_prev_flow);
      if (tiny_ptr) {
        std::memset(tiny_ptr, 0, (size_t)g_ctx->safe_prev_flow_bytes);
        ti_unmap_memory(runtime, safe_prev_flow);
      }
    }
  }

  if (effective_layers == 4 && g_ctx->graphs.count("compute_flow_4layer")) {
    int search_radius = std::max(4, (int)(search_dist * 2.0f));
    int current_search_dist = std::max(2, (int)search_dist);

    const int zncc_max_shift = 32; // Standard for coarse layer robustness
    const int zncc_size = 2 * zncc_max_shift + 1;
    if (!_ensure_memory(runtime, g_ctx->zncc_surface_gpu, g_ctx->zncc_surface_bytes, (uint64_t)zncc_size * zncc_size * sizeof(float), false, false)) return nullptr;
    if (!_ensure_memory(runtime, g_ctx->zncc_results_gpu, g_ctx->zncc_results_bytes, (uint64_t)3 * sizeof(float), false, false)) return nullptr;

    std::vector<TiNamedArgument> graph_args = {
        make_named_arg("ref_l0", make_ndarray_arg(pyramid[0].ref, _shape_2d(pyramid[0].h, pyramid[0].w))),
        make_named_arg("ref_l1", make_ndarray_arg(pyramid[1].ref, _shape_2d(pyramid[1].h, pyramid[1].w))),
        make_named_arg("ref_l2", make_ndarray_arg(pyramid[2].ref, _shape_2d(pyramid[2].h, pyramid[2].w))),
        make_named_arg("ref_l3", make_ndarray_arg(pyramid[3].ref, _shape_2d(pyramid[3].h, pyramid[3].w))),

        make_named_arg("comp_l0", make_ndarray_arg(pyramid[0].comp, _shape_2d(pyramid[0].h, pyramid[0].w))),
        make_named_arg("comp_l1", make_ndarray_arg(pyramid[1].comp, _shape_2d(pyramid[1].h, pyramid[1].w))),
        make_named_arg("comp_l2", make_ndarray_arg(pyramid[2].comp, _shape_2d(pyramid[2].h, pyramid[2].w))),
        make_named_arg("comp_l3", make_ndarray_arg(pyramid[3].comp, _shape_2d(pyramid[3].h, pyramid[3].w))),

        make_named_arg("flow_l0", make_ndarray_arg(pyramid[0].flow, _shape_flow(pyramid[0].h, pyramid[0].w))),
        make_named_arg("flow_l1", make_ndarray_arg(pyramid[1].flow, _shape_flow(pyramid[1].h, pyramid[1].w))),
        make_named_arg("flow_l2", make_ndarray_arg(pyramid[2].flow, _shape_flow(pyramid[2].h, pyramid[2].w))),
        make_named_arg("flow_l3", make_ndarray_arg(pyramid[3].flow, _shape_flow(pyramid[3].h, pyramid[3].w))),

        make_named_arg("flow_tmp_l0", make_ndarray_arg(pyramid[0].flow_temp, _shape_flow(pyramid[0].h, pyramid[0].w))),
        make_named_arg("flow_tmp_l1", make_ndarray_arg(pyramid[1].flow_temp, _shape_flow(pyramid[1].h, pyramid[1].w))),
        make_named_arg("flow_tmp_l2", make_ndarray_arg(pyramid[2].flow_temp, _shape_flow(pyramid[2].h, pyramid[2].w))),
        make_named_arg("flow_tmp_l3", make_ndarray_arg(pyramid[3].flow_temp, _shape_flow(pyramid[3].h, pyramid[3].w))),

        make_named_arg("zncc_surface", make_ndarray_arg(g_ctx->zncc_surface_gpu, {(uint32_t)zncc_size, (uint32_t)zncc_size})),
        make_named_arg("zncc_results", make_ndarray_arg(g_ctx->zncc_results_gpu, {3u})),
        make_named_arg("zncc_max_shift", make_i32_arg(zncc_max_shift)),

        make_named_arg("tile_h", make_i32_arg(tile_h)),
        make_named_arg("tile_w", make_i32_arg(tile_w)),
        make_named_arg("search_dist", make_i32_arg(current_search_dist)),
        make_named_arg("search_radius", make_i32_arg(search_radius)),
        make_named_arg("scale", make_f32_arg((float)downscale_factor))
    };

    ti_launch_compute_graph(runtime, g_ctx->graphs["compute_flow_4layer"], (uint32_t)graph_args.size(), graph_args.data());
  } else if (effective_layers == 3 && g_ctx->graphs.count("compute_flow_3layer")) {
    // Monolithic Graph Execution (Parity with Python compute_flow.py)
    // Match Python: search_radius = max(4, int(search_dist * 2))
    int search_radius = std::max(4, (int)(search_dist * 2.0f));
    int current_search_dist = std::max(2, (int)search_dist);

    const int zncc_max_shift = 32;
    const int zncc_size = 2 * zncc_max_shift + 1;
    if (!_ensure_memory(runtime, g_ctx->zncc_surface_gpu, g_ctx->zncc_surface_bytes, (uint64_t)zncc_size * zncc_size * sizeof(float), false, false)) return nullptr;
    if (!_ensure_memory(runtime, g_ctx->zncc_results_gpu, g_ctx->zncc_results_bytes, (uint64_t)3 * sizeof(float), false, false)) return nullptr;

    std::vector<TiNamedArgument> graph_args = {
        make_named_arg("ref_l0", make_ndarray_arg(pyramid[0].ref,
                                                  _shape_2d(pyramid[0].h,
                                                            pyramid[0].w))),
        make_named_arg("ref_l1", make_ndarray_arg(pyramid[1].ref,
                                                  _shape_2d(pyramid[1].h,
                                                            pyramid[1].w))),
        make_named_arg("ref_l2", make_ndarray_arg(pyramid[2].ref,
                                                  _shape_2d(pyramid[2].h,
                                                            pyramid[2].w))),

        make_named_arg("comp_l0", make_ndarray_arg(pyramid[0].comp,
                                                   _shape_2d(pyramid[0].h,
                                                             pyramid[0].w))),
        make_named_arg("comp_l1", make_ndarray_arg(pyramid[1].comp,
                                                   _shape_2d(pyramid[1].h,
                                                             pyramid[1].w))),
        make_named_arg("comp_l2", make_ndarray_arg(pyramid[2].comp,
                                                   _shape_2d(pyramid[2].h,
                                                             pyramid[2].w))),

        make_named_arg("flow_l0", make_ndarray_arg(pyramid[0].flow,
                                                   _shape_flow(pyramid[0].h,
                                                               pyramid[0].w))),
        make_named_arg("flow_l1", make_ndarray_arg(pyramid[1].flow,
                                                   _shape_flow(pyramid[1].h,
                                                               pyramid[1].w))),
        make_named_arg("flow_l2", make_ndarray_arg(pyramid[2].flow,
                                                   _shape_flow(pyramid[2].h,
                                                               pyramid[2].w))),

        make_named_arg("flow_tmp_l0",
                       make_ndarray_arg(pyramid[0].flow_temp,
                                        _shape_flow(pyramid[0].h,
                                                    pyramid[0].w))),
        make_named_arg("flow_tmp_l1",
                       make_ndarray_arg(pyramid[1].flow_temp,
                                        _shape_flow(pyramid[1].h,
                                                    pyramid[1].w))),
        make_named_arg("flow_tmp_l2",
                       make_ndarray_arg(pyramid[2].flow_temp,
                                        _shape_flow(pyramid[2].h,
                                                    pyramid[2].w))),

        make_named_arg("zncc_surface", make_ndarray_arg(g_ctx->zncc_surface_gpu, {(uint32_t)zncc_size, (uint32_t)zncc_size})),
        make_named_arg("zncc_results", make_ndarray_arg(g_ctx->zncc_results_gpu, {3u})),
        make_named_arg("zncc_max_shift", make_i32_arg(zncc_max_shift)),

        make_named_arg("tile_h", make_i32_arg(tile_h)),
        make_named_arg("tile_w", make_i32_arg(tile_w)),
        make_named_arg("search_dist", make_i32_arg(current_search_dist)),
        make_named_arg("search_radius", make_i32_arg(search_radius)),
        make_named_arg("scale", make_f32_arg((float)downscale_factor))};

    ti_launch_compute_graph(runtime, g_ctx->graphs["compute_flow_3layer"],
                             (uint32_t)graph_args.size(), graph_args.data());
  } else {
    // Fallback to manual orchestration (dynamic levels)
    for (int i = effective_layers - 1; i >= 0; --i) {
      // Python naming parity:
      // flow_gpu        -> pyramid[i].flow
      // refined_flow_gpu-> pyramid[i].flow_temp
      const bool is_coarsest_layer = (i == effective_layers - 1);
      const bool is_finest_layer = (i == 0);
      const int current_tile_h =
          std::max(min_tile_size, std::min(tile_h, pyramid[i].h));
      const int current_tile_w =
          std::max(min_tile_size, std::min(tile_w, pyramid[i].w));

      // process_single_layer: refined_flow_gpu initialized to zeros.
      std::vector<TiArgument> init_refined_args = {
          make_ndarray_arg(pyramid[i].flow_temp,
                           _shape_flow(pyramid[i].h, pyramid[i].w)),
          make_i32_arg(pyramid[i].h),
          make_i32_arg(pyramid[i].w),
          make_f32_arg(0.0f),
          make_f32_arg(0.0f),
      };
      launch_kernel_simple(runtime,
                           g_ctx->kernels["_initialize_coarsest_flow_kernel"],
                           init_refined_args);

      if (is_coarsest_layer) {
        int global_dx = 0;
        int global_dy = 0;
        float global_cost = 1e10f;
        _global_translate_zncc(g_ctx, pyramid[i].ref, pyramid[i].comp,
                               pyramid[i].h, pyramid[i].w, 32, global_dx,
                               global_dy, global_cost);

        std::vector<TiArgument> args = {
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i].h), make_i32_arg(pyramid[i].w),
            make_f32_arg((float)global_dx), make_f32_arg((float)global_dy)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_initialize_coarsest_flow_kernel"], args);
      } else {
        std::vector<TiArgument> u_args = {
            make_ndarray_arg(pyramid[i + 1].flow,
                             _shape_flow(pyramid[i + 1].h, pyramid[i + 1].w)),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i + 1].h),
            make_i32_arg(pyramid[i + 1].w),
            make_i32_arg(pyramid[i].h),
            make_i32_arg(pyramid[i].w),
            make_f32_arg((float)downscale_factor),
            make_f32_arg((float)downscale_factor),
        };
        launch_kernel_simple(runtime, g_ctx->kernels["_upsample_flow_kernel"],
                             u_args);
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
      }

      if (is_finest_layer) {
        TiMemory prev_flow_mem = TI_NULL_HANDLE;
        int prev_h = 1;
        int prev_w = 1;
        if (is_coarsest_layer) {
          if (safe_prev_flow != TI_NULL_HANDLE) {
            prev_flow_mem = safe_prev_flow;
            prev_h = 1;
            prev_w = 1;
          } else {
            prev_flow_mem = pyramid[i].flow;
            prev_h = pyramid[i].h;
            prev_w = pyramid[i].w;
          }
        } else {
          prev_flow_mem = pyramid[i + 1].flow;
          prev_h = pyramid[i + 1].h;
          prev_w = pyramid[i + 1].w;
        }

        std::vector<TiArgument> r_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(prev_flow_mem, _shape_flow(prev_h, prev_w)),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i].h),
            make_i32_arg(pyramid[i].w),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w)};
        r_args.push_back(make_i32_arg(prev_h));
        r_args.push_back(make_i32_arg(prev_w));
        r_args.push_back(make_i32_arg(downscale_factor));
        launch_kernel_simple(
            runtime, g_ctx->kernels["_search_fine_level_kernel"], r_args);
      } else if (is_coarsest_layer) {
        int search_radius = std::max(4, (int)(search_dist * 2.0f));
        std::vector<TiArgument> s_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i].h),
            make_i32_arg(pyramid[i].w),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w),
            make_i32_arg(search_radius)};
        launch_kernel_simple(runtime, g_ctx->kernels["_block_search_kernel"],
                             s_args);
      } else {
        int current_search_dist = std::max(2, (int)search_dist);
        std::vector<TiArgument> r_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i + 1].flow,
                             _shape_flow(pyramid[i + 1].h, pyramid[i + 1].w)),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i].h),
            make_i32_arg(pyramid[i].w),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w),
            make_i32_arg(current_search_dist),
            make_i32_arg(pyramid[i + 1].h),
            make_i32_arg(pyramid[i + 1].w),
            make_i32_arg(downscale_factor)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_search_coarse_level_kernel"], r_args);
      }

      if (!is_finest_layer) {
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));

        std::vector<TiArgument> sub_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w)),
            make_i32_arg(pyramid[i].h),
            make_i32_arg(pyramid[i].w),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_parabolic_subpixel_refinement_kernel"],
            sub_args);

        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
      } else {
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
      }
    }
  }

  // 3. Warp
  std::vector<TiArgument> w_args;
  TiKernel warp_kernel = TI_NULL_HANDLE;
  if (channels == 3) {
    warp_kernel = g_ctx->kernels["_warp_guided_i32_rgb_aot"];
    w_args = {
        make_ndarray_arg(g_ctx->comp_raw_gpu, {(uint32_t)h, (uint32_t)w, 3u}),
        make_ndarray_arg(pyramid[0].flow, _shape_flow(h, w)),
        make_ndarray_arg(g_ctx->warped_gpu, {(uint32_t)h, (uint32_t)w, 3u}),
        make_ndarray_arg(g_ctx->ref_raw_gpu, {(uint32_t)h, (uint32_t)w, 3u}),
        make_i32_arg(h),
        make_i32_arg(w),
    };
  } else {
    warp_kernel = g_ctx->kernels["_warp_guided_i32_aot"];
    w_args = {
        make_ndarray_arg(g_ctx->comp_raw_gpu, _shape_2d(h, w)),
        make_ndarray_arg(pyramid[0].flow, _shape_flow(h, w)),
        make_ndarray_arg(g_ctx->warped_gpu, _shape_2d(h, w)),
        make_ndarray_arg(g_ctx->ref_raw_gpu, _shape_2d(h, w)),
        make_i32_arg(h),
        make_i32_arg(w),
    };
  }
  launch_kernel_simple(runtime, warp_kernel, w_args);
  ti_wait(runtime);

  int32_t *out =
      (int32_t *)std::malloc((size_t)h * w * channels * sizeof(int32_t));
  void *src_w = ti_map_memory(runtime, g_ctx->warped_gpu);
  std::memcpy(out, src_w, (size_t)h * w * channels * sizeof(int32_t));
  ti_unmap_memory(runtime, g_ctx->warped_gpu);

  // Per-frame temporary buffers are persistent in g_ctx and intentionally
  // reused.
  return out;
}

ALIGN_API int compute_alignment_modular_tirt_into_ex(
    const int32_t *comp_u16, int tile_h, int tile_w, int n_layers,
    float search_dist, int channels, int32_t *out_u16) {
  if (!out_u16)
    return -1;
  int32_t *tmp = compute_alignment_modular_tirt_ex(
      comp_u16, tile_h, tile_w, n_layers, search_dist, channels);
  if (!tmp)
    return -2;
  const size_t count = (size_t)g_ctx->h * g_ctx->w * ((channels == 3) ? 3 : 1);
  std::memcpy(out_u16, tmp, count * sizeof(int32_t));
  std::free(tmp);
  return 0;
}

ALIGN_API void deinit_alignment_modular_tirt() {
  if (!g_ctx)
    return;
  if (g_ctx->runtime != TI_NULL_HANDLE) {
    clear_reference_modular_tirt();
    ti_destroy_aot_module(g_ctx->preprocess_mod);
    ti_destroy_aot_module(g_ctx->flow_mod);
    ti_destroy_aot_module(g_ctx->warp_mod);
    // Graphs and kernels are owned by the modules and destroyed with them
    ti_destroy_runtime(g_ctx->runtime);
  }
  delete g_ctx;
  g_ctx = nullptr;
}

ALIGN_API void free_u16_memory(int32_t *ptr) {
  if (ptr)
    std::free(ptr);
}

} // extern "C"
