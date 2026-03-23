#include "alignment_tile_taichi_api.h"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iomanip>
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
  TiAotModule unified_mod = TI_NULL_HANDLE;
  std::map<std::string, TiKernel> kernels;
  std::map<std::string, TiComputeGraph> graphs;

  TiMemory ref_raw_gpu = TI_NULL_HANDLE;
  TiMemory ref_full_gpu = TI_NULL_HANDLE;
  TiMemory ref_norm_gpu = TI_NULL_HANDLE;
  TiMemory comp_raw_gpu = TI_NULL_HANDLE;
  TiMemory comp_full_gpu = TI_NULL_HANDLE;
  TiMemory comp_norm_gpu = TI_NULL_HANDLE;
  TiMemory warped_gpu = TI_NULL_HANDLE;
  uint64_t ref_raw_bytes = 0, ref_full_bytes = 0, ref_norm_bytes = 0;
  uint64_t comp_raw_bytes = 0, comp_full_bytes = 0, comp_norm_bytes = 0;
  uint64_t warped_bytes = 0;

  int h = 0, w = 0;
  int h_full = 0, w_full = 0;
  int channels = 1;

  std::vector<PyramidLevel> pyramid_cache;
  TiMemory safe_prev_flow = TI_NULL_HANDLE;
  uint64_t safe_prev_flow_bytes = 0;
  TiMemory zncc_surface_gpu = TI_NULL_HANDLE;
  uint64_t zncc_surface_bytes = 0;
  int zncc_surface_side = 0;

  TiMemory zncc_results_gpu = TI_NULL_HANDLE;
  uint64_t zncc_results_bytes = 0;

  TiMemory temp_down_ref = TI_NULL_HANDLE;
  uint64_t temp_down_ref_bytes = 0;
  TiMemory temp_down_comp = TI_NULL_HANDLE;
  uint64_t temp_down_comp_bytes = 0;

  TiMemory flow_refine_gpu = TI_NULL_HANDLE;
  uint64_t flow_refine_bytes = 0;
  TiMemory flow_full_gpu = TI_NULL_HANDLE;
  uint64_t flow_full_bytes = 0;

  float preprocess_scale_gamma = 1.0f;
  int preprocess_use_sharpen = 0;

  int alignment_downscale_factor = 4;
  int alignment_min_tile_size = 8;
  int n_layers = 3;
};

static AlignmentContext *g_ctx = nullptr;

struct Timer {
  std::chrono::high_resolution_clock::time_point t_start;
  Timer() { reset(); }
  void reset() { t_start = std::chrono::high_resolution_clock::now(); }
  double elapsed_ms() const {
    auto t_end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double, std::milli>(t_end - t_start).count();
  }
};

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

// --- [FIX] Sinkronisasi Logika Kalkulasi Ukuran Pyramid ---
inline std::vector<std::pair<int, int>>
_get_pyramid_shapes(int h, int w, int n_layers, int downscale_factor) {
  std::vector<std::pair<int, int>> level_shapes;
  const int min_w = 253;
  level_shapes.push_back({h, w});
  for (int lvl = 1; lvl < n_layers; ++lvl) {
    int next_w = (level_shapes.back().second / downscale_factor / 2) * 2;
    int next_h = (level_shapes.back().first / downscale_factor / 2) * 2;
    if (next_w < min_w || next_h < 4 || next_w < 4)
      break;
    level_shapes.push_back({next_h, next_w});
  }
  return level_shapes;
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
  if (lvl.ref) {
    ti_free_memory(runtime, lvl.ref);
    lvl.ref = TI_NULL_HANDLE;
    lvl.ref_bytes = 0;
  }
  if (lvl.comp) {
    ti_free_memory(runtime, lvl.comp);
    lvl.comp = TI_NULL_HANDLE;
    lvl.comp_bytes = 0;
  }
  if (lvl.flow) {
    ti_free_memory(runtime, lvl.flow);
    lvl.flow = TI_NULL_HANDLE;
    lvl.flow_bytes = 0;
  }
  if (lvl.flow_temp) {
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
  if (ctx->pyramid_cache.size() < shapes.size())
    ctx->pyramid_cache.resize(shapes.size());
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

void launch_kernel_simple(TiRuntime runtime, TiKernel kernel,
                          std::vector<TiArgument> args) {
  if (!kernel)
    return;
  ti_launch_kernel(runtime, kernel, (uint32_t)args.size(), args.data());
}

TiArgument make_ndarray_arg(TiMemory mem, const std::vector<uint32_t> &shape,
                            TiDataType elem_type = TI_DATA_TYPE_F32) {
  TiNdArray ndarray = {};
  ndarray.memory = mem;
  ndarray.shape.dim_count = (uint32_t)shape.size();
  for (size_t i = 0; i < shape.size(); ++i)
    ndarray.shape.dims[i] = shape[i];
  ndarray.elem_type = elem_type;
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
                                           TiMemory src_i32_gpu, int src_h,
                                           int src_w, int channels,
                                           TiMemory dst_f32_2d, int dst_h,
                                           int dst_w) {
  if (!ctx || src_i32_gpu == TI_NULL_HANDLE || src_h <= 0 || src_w <= 0 ||
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
    args.push_back(make_ndarray_arg(
        src_i32_gpu, {(uint32_t)src_h, (uint32_t)src_w, 3u}, TI_DATA_TYPE_I32));
  } else {
    args.push_back(make_ndarray_arg(
        src_i32_gpu, {(uint32_t)src_h, (uint32_t)src_w}, TI_DATA_TYPE_I32));
  }

  args.push_back(
      make_ndarray_arg(dst_f32_2d, _shape_2d(dst_h, dst_w), TI_DATA_TYPE_F32));
  args.push_back(make_f32_arg(65535.0f));
  args.push_back(make_f32_arg(ctx->preprocess_scale_gamma));
  args.push_back(make_f32_arg(2.22f));
  args.push_back(make_f32_arg(4.5f));
  args.push_back(make_f32_arg(0.018f));
  args.push_back(make_i32_arg(ctx->preprocess_use_sharpen));

  launch_kernel_simple(runtime, kernel, args);
  return true;
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

  int max_shift = std::min({requested_max_shift, std::max(0, (h - 1) / 2),
                            std::max(0, (w - 1) / 2)});
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
      make_i32_arg(max_shift)};
  launch_kernel_simple(ctx->runtime, k, args);
  ti_wait(ctx->runtime);

  void *mapped = ti_map_memory(ctx->runtime, ctx->zncc_surface_gpu);
  if (!mapped)
    return false;
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

  g_ctx = new AlignmentContext();
  g_ctx->runtime = ti_create_runtime(arch, 0);
  if (!g_ctx->runtime)
    return -1;

  std::string base_path = data_dir;
  if (base_path.back() != '/' && base_path.back() != '\\')
    base_path += "/";

  std::string unified_path =
      base_path + "alignment_tile_taichi_" + s_arch + ".tcm";
  g_ctx->unified_mod = ti_load_aot_module(g_ctx->runtime, unified_path.c_str());

  if (g_ctx->unified_mod == TI_NULL_HANDLE) {
    std::cerr << "[TiRT Error] Failed to load module: " << unified_path
              << std::endl;
    return -2;
  }

  auto load_k = [&](const char *name) {
    TiKernel k = ti_get_aot_module_kernel(g_ctx->unified_mod, name);
    if (k != TI_NULL_HANDLE)
      g_ctx->kernels[name] = k;
    return k != TI_NULL_HANDLE;
  };

  auto load_g = [&](const char *name) {
    TiComputeGraph g =
        ti_get_aot_module_compute_graph(g_ctx->unified_mod, name);
    if (g != TI_NULL_HANDLE)
      g_ctx->graphs[name] = g;
    return g != TI_NULL_HANDLE;
  };

  const std::vector<const char *> kernel_specs = {
      "_fused_full_pipeline_i32_2d_aot",
      "_fused_full_pipeline_i32_3d_aot",
      "_initialize_coarsest_flow_kernel",
      "_block_search_kernel",
      "_search_coarse_level_kernel",
      "_search_fine_level_kernel",
      "_parabolic_subpixel_refinement_kernel",
      "_downsample_2x_kernel",
      "_upsample_flow_kernel",
      "_compute_global_zncc_surface",
      "_warp_naked_i32_aot",
      "_warp_naked_i32_rgb_aot"};

  for (const auto &k_name : kernel_specs)
    load_k(k_name);

  load_g("setup_reference_3layer");
  load_g("setup_comparison_3layer");
  load_g("align_frame_3layer_coarse");
  load_g("align_frame_3layer_fine");
  load_g("align_end_to_end_3layer");

  return 0;
}

ALIGN_API int set_preprocess_config_modular_tirt(float scale_gamma,
                                                 int use_sharpen) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  g_ctx->preprocess_scale_gamma = scale_gamma > 0 ? scale_gamma : 1.0f;
  g_ctx->preprocess_use_sharpen = (use_sharpen != 0) ? 1 : 0;
  return 0;
}

ALIGN_API int set_alignment_config_modular_tirt(int downscale_factor,
                                                int min_tile_size,
                                                int n_layers) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  g_ctx->alignment_downscale_factor =
      downscale_factor < 2 ? 4 : downscale_factor;
  g_ctx->alignment_min_tile_size = min_tile_size < 1 ? 8 : min_tile_size;
  g_ctx->n_layers = n_layers < 1 ? 1 : n_layers;
  return 0;
}

ALIGN_API void clear_reference_modular_tirt() {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return;
#define FREE_MEM(x)                                                            \
  if (g_ctx->x != TI_NULL_HANDLE) {                                            \
    ti_free_memory(g_ctx->runtime, g_ctx->x);                                  \
    g_ctx->x = TI_NULL_HANDLE;                                                 \
  }
  FREE_MEM(ref_raw_gpu);
  FREE_MEM(ref_norm_gpu);
  FREE_MEM(comp_raw_gpu);
  FREE_MEM(ref_full_gpu);
  FREE_MEM(comp_full_gpu);
  FREE_MEM(comp_norm_gpu);
  FREE_MEM(warped_gpu);
  FREE_MEM(safe_prev_flow);
  FREE_MEM(zncc_surface_gpu);
  FREE_MEM(zncc_results_gpu);
  FREE_MEM(temp_down_ref);
  FREE_MEM(temp_down_comp);
  FREE_MEM(flow_refine_gpu);
  FREE_MEM(flow_full_gpu);
#undef FREE_MEM
  for (auto &lvl : g_ctx->pyramid_cache)
    _release_pyramid_level(g_ctx->runtime, lvl);
  g_ctx->pyramid_cache.clear();
}

ALIGN_API int set_reference_modular_tirt(const int32_t *ref_u16, int h, int w) {
  return set_reference_modular_tirt_ex(ref_u16, h, w, 1);
}

ALIGN_API int set_reference_full_modular_tirt_ex(const int32_t *ref_full_u16,
                                                 int h, int w, int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  g_ctx->h_full = h;
  g_ctx->w_full = w;
  const uint64_t full_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  if (!_ensure_memory(g_ctx->runtime, g_ctx->ref_full_gpu,
                      g_ctx->ref_full_bytes, full_bytes, true, false))
    return -2;
  if (!_copy_host_to_gpu(g_ctx->runtime, g_ctx->ref_full_gpu, ref_full_u16,
                         full_bytes))
    return -3;
  return 0;
}

ALIGN_API int set_comparison_full_modular_tirt_ex(const int32_t *comp_full_u16,
                                                  int h, int w, int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  g_ctx->h_full = h;
  g_ctx->w_full = w;
  const uint64_t full_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  if (!_ensure_memory(g_ctx->runtime, g_ctx->comp_full_gpu,
                      g_ctx->comp_full_bytes, full_bytes, true, false))
    return -1;
  if (!_copy_host_to_gpu(g_ctx->runtime, g_ctx->comp_full_gpu, comp_full_u16,
                         full_bytes))
    return -2;
  return 0;
}

ALIGN_API int set_reference_modular_tirt_ex(const int32_t *ref_u16, int h,
                                            int w, int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE)
    return -1;
  if (!ref_u16 || h <= 0 || w <= 0)
    return -2;
  if (channels != 1 && channels != 3)
    channels = 1;

  if (g_ctx->h != h || g_ctx->w != w || g_ctx->channels != channels)
    clear_reference_modular_tirt();

  h = (h / 2) * 2;
  w = (w / 2) * 2;
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

  // --- [FIX] Gunakan get_pyramid_shapes untuk kalkulasi level secara presisi
  // ---
  std::vector<std::pair<int, int>> level_shapes = _get_pyramid_shapes(
      h, w, g_ctx->n_layers, g_ctx->alignment_downscale_factor);
  int effective_layers = (int)level_shapes.size();

  std::string graph_setup_name =
      "setup_reference_" + std::to_string(g_ctx->n_layers) + "layer";
  bool use_setup_graph =
      (channels == 3 && effective_layers == g_ctx->n_layers &&
       g_ctx->graphs.count(graph_setup_name));

  if (!_ensure_pyramid_cache(g_ctx, level_shapes))
    return -6;
  std::vector<PyramidLevel> &pyramid = g_ctx->pyramid_cache;

  if (use_setup_graph) {
    std::vector<TiNamedArgument> args;
    std::vector<std::string> arg_names;
    auto add_named_arg = [&](const std::string &name, TiArgument arg) {
      arg_names.push_back(name);
      args.push_back(make_named_arg(arg_names.back().c_str(), arg));
    };

    add_named_arg(
        "raw", make_ndarray_arg(g_ctx->ref_raw_gpu,
                                {(uint32_t)h, (uint32_t)w, (uint32_t)channels},
                                TI_DATA_TYPE_I32));
    for (int i = 0; i < effective_layers; ++i) {
      add_named_arg("l" + std::to_string(i),
                    make_ndarray_arg(pyramid[i].ref,
                                     _shape_2d(pyramid[i].h, pyramid[i].w),
                                     TI_DATA_TYPE_F32));
      if (i > 0)
        add_named_arg("tmp_l" + std::to_string(i),
                      make_ndarray_arg(
                          g_ctx->temp_down_ref,
                          _shape_2d(pyramid[i - 1].h / 2, pyramid[i - 1].w / 2),
                          TI_DATA_TYPE_F32));
    }

    add_named_arg("s_norm", make_f32_arg(1.0f / 65535.0f));
    add_named_arg("s_gamma", make_f32_arg(g_ctx->preprocess_scale_gamma));
    add_named_arg("g_pow", make_f32_arg(1.0f / 2.222f));
    add_named_arg("slope", make_f32_arg(4.5f));
    add_named_arg("cutoff", make_f32_arg(0.018f));
    add_named_arg("sharpen", make_i32_arg(g_ctx->preprocess_use_sharpen));

    ti_launch_compute_graph(g_ctx->runtime, g_ctx->graphs[graph_setup_name],
                            (uint32_t)args.size(), args.data());
    ti_wait(g_ctx->runtime);
  } else {
    // Manual fallback
    if (!_fused_full_pipeline_i32_aot_from_gpu(g_ctx, g_ctx->ref_raw_gpu, h, w,
                                               channels, pyramid[0].ref, h, w))
      return -7;

    TiKernel down_k = g_ctx->kernels["_downsample_2x_kernel"];
    if (down_k != TI_NULL_HANDLE) {
      int steps_per_level = 1;
      if (g_ctx->alignment_downscale_factor > 2) {
        steps_per_level = (int)std::lround(
            std::log2((double)g_ctx->alignment_downscale_factor));
        if (steps_per_level < 1)
          steps_per_level = 1;
      }

      auto cascade_down = [&](TiMemory src_root, TiMemory dst_root, int h_in,
                              int w_in, int h_final, int w_final,
                              TiMemory temp_buf) {
        TiMemory current_src = src_root;
        int cur_h = h_in, cur_w = w_in;
        for (int s = 0; s < steps_per_level; ++s) {
          int target_h = (s == steps_per_level - 1) ? h_final : (cur_h / 2);
          int target_w = (s == steps_per_level - 1) ? w_final : (cur_w / 2);
          TiMemory current_dst =
              (s == steps_per_level - 1) ? dst_root : temp_buf;

          std::vector<TiArgument> d_args = {
              make_ndarray_arg(current_src, _shape_2d(cur_h, cur_w),
                               TI_DATA_TYPE_F32),
              make_ndarray_arg(current_dst, _shape_2d(target_h, target_w),
                               TI_DATA_TYPE_F32)};
          launch_kernel_simple(g_ctx->runtime, down_k, d_args);
          current_src = current_dst;
          cur_h = target_h;
          cur_w = target_w;
        }
      };

      for (int i = 0; i < effective_layers - 1; ++i) {
        cascade_down(pyramid[i].ref, pyramid[i + 1].ref, pyramid[i].h,
                     pyramid[i].w, pyramid[i + 1].h, pyramid[i + 1].w,
                     g_ctx->temp_down_ref);
      }
      ti_wait(g_ctx->runtime);
    }
  }
  return 0;
}

ALIGN_API int32_t *compute_alignment_modular_tirt(const int32_t *comp_u16,
                                                  int tile_h, int tile_w,
                                                  int n_layers,
                                                  float search_dist) {
  if (!g_ctx)
    return nullptr;
  return compute_alignment_modular_tirt_ex(comp_u16, g_ctx->h, g_ctx->w, tile_h,
                                           tile_w, n_layers, search_dist, 1);
}

ALIGN_API int32_t *compute_alignment_modular_tirt_ex(const int32_t *comp_u16,
                                                     int h, int w, int tile_h,
                                                     int tile_w, int n_layers,
                                                     float search_dist,
                                                     int channels) {
  if (!g_ctx || g_ctx->runtime == TI_NULL_HANDLE ||
      g_ctx->ref_norm_gpu == TI_NULL_HANDLE || !comp_u16)
    return nullptr;
  h = (h / 2) * 2;
  w = (w / 2) * 2;

  TiRuntime runtime = g_ctx->runtime;
  int full_h = (g_ctx->h_full > 0) ? g_ctx->h_full : h;
  int full_w = (g_ctx->w_full > 0) ? g_ctx->w_full : w;

  if (channels != 1 && channels != 3)
    channels = 1;
  if (channels != g_ctx->channels) {
    std::cerr << "[TiRT Error] Channel mismatch (" << channels << " vs "
              << g_ctx->channels << ")." << std::endl;
    return nullptr;
  }

  const int downscale_factor = g_ctx->alignment_downscale_factor;
  const int min_tile_size = g_ctx->alignment_min_tile_size;
  if (n_layers < 1)
    n_layers = 1;

  // --- [FIX] Menggunakan fungsi helper agar bentuk level 100% konsisten dengan
  // set_reference ---
  std::vector<std::pair<int, int>> level_shapes =
      _get_pyramid_shapes(h, w, n_layers, downscale_factor);
  int effective_layers = (int)level_shapes.size();

  bool use_monolithic = (channels == 3 && effective_layers == 3 &&
                         g_ctx->graphs.count("align_end_to_end_3layer"));
  bool use_split_graph =
      (!use_monolithic && channels == 3 && effective_layers == 3 &&
       g_ctx->graphs.count("align_frame_3layer_coarse"));

  const uint64_t raw_bytes = (uint64_t)h * w * channels * sizeof(int32_t);
  const uint64_t norm_bytes = (uint64_t)h * w * sizeof(float);
  int out_h = full_h, out_w = full_w;
  const uint64_t warped_bytes =
      (uint64_t)out_h * out_w * channels * sizeof(int32_t);

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
  if (!_ensure_pyramid_cache(g_ctx, level_shapes))
    return nullptr;
  std::vector<PyramidLevel> &pyramid = g_ctx->pyramid_cache;

  TiMemory comp_raw_use =
      (g_ctx->h_full > 0) ? g_ctx->comp_full_gpu : g_ctx->comp_raw_gpu;
  TiMemory ref_raw_use =
      (g_ctx->h_full > 0) ? g_ctx->ref_full_gpu : g_ctx->ref_raw_gpu;

  Timer t_total;

  if (use_monolithic) {
    std::cout << "[GPU Alignment] Mode: Monolithic Graph" << std::endl;
    std::vector<TiNamedArgument> m_args;
    std::vector<std::string> m_arg_names;
    auto add_m_arg = [&](const std::string &name, TiArgument arg) {
      m_arg_names.push_back(name);
      m_args.push_back(make_named_arg(m_arg_names.back().c_str(), arg));
    };

    add_m_arg("ref_raw", make_ndarray_arg(ref_raw_use,
                                          {(uint32_t)out_h, (uint32_t)out_w,
                                           (uint32_t)channels},
                                          TI_DATA_TYPE_I32));
    add_m_arg("comp_raw", make_ndarray_arg(comp_raw_use,
                                           {(uint32_t)out_h, (uint32_t)out_w,
                                            (uint32_t)channels},
                                           TI_DATA_TYPE_I32));
    add_m_arg("warped", make_ndarray_arg(g_ctx->warped_gpu,
                                         {(uint32_t)out_h, (uint32_t)out_w,
                                          (uint32_t)channels},
                                         TI_DATA_TYPE_I32));

    for (int i = 0; i < 3; ++i) {
      add_m_arg("ref_l" + std::to_string(i),
                make_ndarray_arg(pyramid[i].ref,
                                 _shape_2d(pyramid[i].h, pyramid[i].w),
                                 TI_DATA_TYPE_F32));
      add_m_arg("comp_l" + std::to_string(i),
                make_ndarray_arg(pyramid[i].comp,
                                 _shape_2d(pyramid[i].h, pyramid[i].w),
                                 TI_DATA_TYPE_F32));
      add_m_arg("flow_l" + std::to_string(i),
                make_ndarray_arg(pyramid[i].flow,
                                 _shape_flow(pyramid[i].h, pyramid[i].w),
                                 TI_DATA_TYPE_F32));
      add_m_arg("flow_tmp_l" + std::to_string(i),
                make_ndarray_arg(pyramid[i].flow_temp,
                                 _shape_flow(pyramid[i].h, pyramid[i].w),
                                 TI_DATA_TYPE_F32));
      if (i > 0) {
        add_m_arg("tmp_ref_l" + std::to_string(i),
                  make_ndarray_arg(
                      g_ctx->temp_down_ref,
                      _shape_2d(pyramid[i - 1].h / 2, pyramid[i - 1].w / 2),
                      TI_DATA_TYPE_F32));
        add_m_arg("tmp_comp_l" + std::to_string(i),
                  make_ndarray_arg(
                      g_ctx->temp_down_comp,
                      _shape_2d(pyramid[i - 1].h / 2, pyramid[i - 1].w / 2),
                      TI_DATA_TYPE_F32));
      }
    }

    const int search_radius = std::max(4, (int)(search_dist * 2.0f));
    const int coarse_dist = std::max(2, (int)search_dist);
    const int zncc_max_shift = 32;
    const int zncc_size = 2 * zncc_max_shift + 1;

    _ensure_memory(runtime, g_ctx->zncc_surface_gpu, g_ctx->zncc_surface_bytes,
                   (uint64_t)zncc_size * zncc_size * sizeof(float), false,
                   false);
    _ensure_memory(runtime, g_ctx->zncc_results_gpu, g_ctx->zncc_results_bytes,
                   3 * sizeof(float), false, false);
    add_m_arg("zncc_surf",
              make_ndarray_arg(g_ctx->zncc_surface_gpu,
                               {(uint32_t)zncc_size, (uint32_t)zncc_size},
                               TI_DATA_TYPE_F32));
    add_m_arg("zncc_res", make_ndarray_arg(g_ctx->zncc_results_gpu, {3u},
                                           TI_DATA_TYPE_F32));

    add_m_arg("s_norm", make_f32_arg(1.0f / 65535.0f));
    add_m_arg("s_gamma", make_f32_arg(g_ctx->preprocess_scale_gamma));
    add_m_arg("g_pow", make_f32_arg(1.0f / 2.222f));
    add_m_arg("slope", make_f32_arg(4.5f));
    add_m_arg("cutoff", make_f32_arg(0.018f));
    add_m_arg("sharpen", make_i32_arg(g_ctx->preprocess_use_sharpen));
    add_m_arg("tile_h", make_i32_arg(tile_h));
    add_m_arg("tile_w", make_i32_arg(tile_w));
    add_m_arg("search_radius", make_i32_arg(search_radius));
    add_m_arg("coarse_dist", make_i32_arg(coarse_dist));
    add_m_arg("scale", make_f32_arg((float)downscale_factor));
    add_m_arg("ds_fac", make_i32_arg(downscale_factor));
    add_m_arg("zncc_shift", make_i32_arg(zncc_max_shift));

    ti_launch_compute_graph(runtime, g_ctx->graphs["align_end_to_end_3layer"],
                            (uint32_t)m_args.size(), m_args.data());
    ti_wait(runtime);

  } else if (use_split_graph) {
    std::cout << "[GPU Alignment] Mode: Split Graph" << std::endl;
    // ... (Graph Split) ...
  } else {
    std::cout << "[GPU Alignment] Mode: Manual (Channels: " << channels << ")"
              << std::endl;
    std::cout << "[GPU Alignment] Pyramid Initiation (" << downscale_factor
              << "x):" << std::endl;

    Timer t_pyr;
    if (!_fused_full_pipeline_i32_aot_from_gpu(g_ctx, comp_raw_use, out_h,
                                               out_w, channels,
                                               g_ctx->comp_norm_gpu, h, w))
      return nullptr;

    int steps_per_level = 1;
    if (downscale_factor > 2) {
      steps_per_level = (int)std::lround(std::log2((double)downscale_factor));
      if (steps_per_level < 1)
        steps_per_level = 1;
    }

    for (int i = 0; i < effective_layers; ++i) {
      if (i == 0) {
        _copy_field_gpu(runtime, g_ctx->comp_norm_gpu, pyramid[0].comp,
                        _bytes_f32_2d(h, w));
      } else {
        auto cascade_down = [&](TiMemory src_root, TiMemory dst_root, int h_in,
                                int w_in, int h_final, int w_final,
                                TiMemory temp_buf) {
          TiMemory current_src = src_root;
          int cur_h = h_in, cur_w = w_in;

          for (int s = 0; s < steps_per_level; ++s) {
            int target_h = (s == steps_per_level - 1) ? h_final : (cur_h / 2);
            int target_w = (s == steps_per_level - 1) ? w_final : (cur_w / 2);
            TiMemory current_dst =
                (s == steps_per_level - 1) ? dst_root : temp_buf;

            std::vector<TiArgument> args = {
                make_ndarray_arg(current_src, _shape_2d(cur_h, cur_w),
                                 TI_DATA_TYPE_F32),
                make_ndarray_arg(current_dst, _shape_2d(target_h, target_w),
                                 TI_DATA_TYPE_F32)};

            launch_kernel_simple(runtime,
                                 g_ctx->kernels["_downsample_2x_kernel"], args);
            current_src = current_dst;
            cur_h = target_h;
            cur_w = target_w;
          }
        };

        cascade_down(pyramid[i - 1].comp, pyramid[i].comp, pyramid[i - 1].h,
                     pyramid[i - 1].w, pyramid[i].h, pyramid[i].w,
                     g_ctx->temp_down_comp);
      }
    }
    ti_wait(runtime);
    std::cout << " - Comp Pyramid: " << std::fixed << std::setprecision(2)
              << t_pyr.elapsed_ms() << "ms (" << effective_layers << " levels)"
              << std::endl;

    TiMemory safe_prev_flow = TI_NULL_HANDLE;
    if (effective_layers == 1) {
      if (!_ensure_memory(runtime, g_ctx->safe_prev_flow,
                          g_ctx->safe_prev_flow_bytes,
                          (uint64_t)1 * 1 * 2 * sizeof(float), true, false))
        return nullptr;
      safe_prev_flow = g_ctx->safe_prev_flow;
      if (safe_prev_flow != TI_NULL_HANDLE) {
        void *tiny_ptr = ti_map_memory(runtime, safe_prev_flow);
        if (tiny_ptr) {
          std::memset(tiny_ptr, 0, (size_t)g_ctx->safe_prev_flow_bytes);
          ti_unmap_memory(runtime, safe_prev_flow);
        }
      }
    }

    for (int i = effective_layers - 1; i >= 0; --i) {
      std::string layer_label = "Layer " + std::to_string(i);
      if (i == effective_layers - 1)
        layer_label += " (Coarsest)";
      else if (i == 0)
        layer_label += " (Finest)";
      std::cout << layer_label << ":" << std::endl;

      Timer t_init;
      const bool is_coarsest_layer = (i == effective_layers - 1);
      const bool is_finest_layer = (i == 0);
      const int current_tile_h =
          std::max(min_tile_size, std::min(tile_h, pyramid[i].h));
      const int current_tile_w =
          std::max(min_tile_size, std::min(tile_w, pyramid[i].w));

      std::vector<TiArgument> init_refined_args = {
          make_ndarray_arg(pyramid[i].flow_temp,
                           _shape_flow(pyramid[i].h, pyramid[i].w),
                           TI_DATA_TYPE_F32),
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
        std::cout << " - [ZNCC] Global Prior: dx=" << global_dx
                  << ", dy=" << global_dy << ", cost=" << global_cost
                  << std::endl;

        std::vector<TiArgument> args = {
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_f32_arg((float)global_dx), make_f32_arg((float)global_dy)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_initialize_coarsest_flow_kernel"], args);
      } else {
        std::vector<TiArgument> u_args = {
            make_ndarray_arg(pyramid[i + 1].flow,
                             _shape_flow(pyramid[i + 1].h, pyramid[i + 1].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_f32_arg((float)downscale_factor),
        };
        launch_kernel_simple(runtime, g_ctx->kernels["_upsample_flow_kernel"],
                             u_args);
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
      }
      ti_wait(runtime);
      std::cout << " - Initiation / Upsample: " << t_init.elapsed_ms() << "ms"
                << std::endl;

      Timer t_match;
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
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(prev_flow_mem, _shape_flow(prev_h, prev_w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w),
            make_i32_arg(downscale_factor)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_search_fine_level_kernel"], r_args);
      } else if (is_coarsest_layer) {
        int search_radius = std::max(4, (int)(search_dist * 2.0f));
        std::vector<TiArgument> s_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w),
            make_i32_arg(search_radius)};
        launch_kernel_simple(runtime, g_ctx->kernels["_block_search_kernel"],
                             s_args);
      } else {
        int current_search_dist = std::max(2, (int)search_dist);
        std::vector<TiArgument> r_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i + 1].flow,
                             _shape_flow(pyramid[i + 1].h, pyramid[i + 1].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w),
            make_i32_arg(current_search_dist),
            make_i32_arg(downscale_factor)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_search_coarse_level_kernel"], r_args);
      }
      ti_wait(runtime);
      std::cout << " - Tile Matching: " << t_match.elapsed_ms() << "ms"
                << std::endl;

      if (!is_finest_layer) {
        Timer t_sub;
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
        std::vector<TiArgument> sub_args = {
            make_ndarray_arg(pyramid[i].ref,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].comp,
                             _shape_2d(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(pyramid[i].flow_temp,
                             _shape_flow(pyramid[i].h, pyramid[i].w),
                             TI_DATA_TYPE_F32),
            make_i32_arg(current_tile_h),
            make_i32_arg(current_tile_w)};
        launch_kernel_simple(
            runtime, g_ctx->kernels["_parabolic_subpixel_refinement_kernel"],
            sub_args);
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
        ti_wait(runtime);
        std::cout << " - Subpixel Refinement: " << t_sub.elapsed_ms() << "ms"
                  << std::endl;
      } else {
        _copy_field_gpu(runtime, pyramid[i].flow_temp, pyramid[i].flow,
                        _bytes_f32_flow(pyramid[i].h, pyramid[i].w));
      }

      // --- [FIX] Download & Print Flow Stats via TIRT Staging Buffer yang Aman
      // ---
      TiMemoryAllocateInfo staging_info = {};
      staging_info.size = _bytes_f32_flow(pyramid[i].h, pyramid[i].w);
      staging_info.usage = TI_MEMORY_USAGE_STORAGE_BIT;
      staging_info.host_read = TI_TRUE; // MEMBUATNYA AMAN UNTUK TI_MAP_MEMORY
      staging_info.host_write = TI_FALSE;

      TiMemory staging_gpu = ti_allocate_memory(runtime, &staging_info);
      if (staging_gpu != TI_NULL_HANDLE) {
        _copy_field_gpu(runtime, pyramid[i].flow, staging_gpu,
                        staging_info.size);
        ti_wait(runtime);

        void *ptr = ti_map_memory(runtime, staging_gpu);
        if (ptr) {
          float *f_ptr = static_cast<float *>(ptr);
          float min_x = 1e10, max_x = -1e10, sum_x = 0;
          float min_y = 1e10, max_y = -1e10, sum_y = 0;
          int count = pyramid[i].h * pyramid[i].w;
          for (int k = 0; k < count; ++k) {
            float d_x = f_ptr[k * 2];
            float d_y = f_ptr[k * 2 + 1];
            if (d_x < min_x)
              min_x = d_x;
            if (d_x > max_x)
              max_x = d_x;
            if (d_y < min_y)
              min_y = d_y;
            if (d_y > max_y)
              max_y = d_y;
            sum_x += d_x;
            sum_y += d_y;
          }
          std::cout << "   -> Flow Stats: dx[" << min_x << ".." << max_x
                    << "] avg=" << (sum_x / count) << " | dy[" << min_y << ".."
                    << max_y << "] avg=" << (sum_y / count) << std::endl;
          ti_unmap_memory(runtime, staging_gpu);
        }
        ti_free_memory(runtime, staging_gpu);
      }
    }

    Timer t_warp;
    if (out_h != h || out_w != w) {
      uint64_t full_flow_bytes = _bytes_f32_flow(out_h, out_w);
      _ensure_memory(runtime, g_ctx->flow_full_gpu, g_ctx->flow_full_bytes,
                     full_flow_bytes, false, false);
      std::vector<TiArgument> u_args = {
          make_ndarray_arg(pyramid[0].flow, _shape_flow(h, w),
                           TI_DATA_TYPE_F32),
          make_ndarray_arg(g_ctx->flow_full_gpu, _shape_flow(out_h, out_w),
                           TI_DATA_TYPE_F32),
          make_f32_arg((float)out_w / w)};
      launch_kernel_simple(runtime, g_ctx->kernels["_upsample_flow_kernel"],
                           u_args);
    }

    TiKernel warp_k = (channels == 3)
                          ? g_ctx->kernels["_warp_naked_i32_rgb_aot"]
                          : g_ctx->kernels["_warp_naked_i32_aot"];
    if (warp_k != TI_NULL_HANDLE) {
      TiMemory flow_to_use =
          (out_h != h || out_w != w) ? g_ctx->flow_full_gpu : pyramid[0].flow;

      if (channels == 3) {
        std::vector<TiArgument> w_args = {
            make_ndarray_arg(comp_raw_use,
                             {(uint32_t)out_h, (uint32_t)out_w, 3u},
                             TI_DATA_TYPE_I32),
            make_ndarray_arg(flow_to_use, _shape_flow(out_h, out_w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(g_ctx->warped_gpu,
                             {(uint32_t)out_h, (uint32_t)out_w, 3u},
                             TI_DATA_TYPE_I32)};
        launch_kernel_simple(runtime, warp_k, w_args);
      } else {
        std::vector<TiArgument> w_args = {
            make_ndarray_arg(comp_raw_use, {(uint32_t)out_h, (uint32_t)out_w},
                             TI_DATA_TYPE_I32),
            make_ndarray_arg(flow_to_use, _shape_flow(out_h, out_w),
                             TI_DATA_TYPE_F32),
            make_ndarray_arg(g_ctx->warped_gpu,
                             {(uint32_t)out_h, (uint32_t)out_w},
                             TI_DATA_TYPE_I32)};
        launch_kernel_simple(runtime, warp_k, w_args);
      }
    }
    ti_wait(runtime);
    std::cout << "[GPU Alignment] Warping Time: " << std::fixed
              << std::setprecision(2) << t_warp.elapsed_ms() << "ms"
              << std::endl;
  }

  std::cout << "[GPU Alignment] Total Execution Time: " << std::fixed
            << std::setprecision(2) << t_total.elapsed_ms() << "ms\n"
            << std::endl;

  int32_t *out = (int32_t *)std::malloc((size_t)out_h * out_w * channels *
                                        sizeof(int32_t));
  if (!out)
    return nullptr;

  const size_t download_size =
      (size_t)out_h * out_w * channels * sizeof(int32_t);
  void *src_w = ti_map_memory(runtime, g_ctx->warped_gpu);
  if (!src_w) {
    std::free(out);
    return nullptr;
  }
  std::memcpy(out, src_w, download_size);
  ti_unmap_memory(runtime, g_ctx->warped_gpu);

  return out;
}

ALIGN_API int compute_alignment_modular_tirt_into_ex(
    const int32_t *comp_u16, int h, int w, int tile_h, int tile_w, int n_layers,
    float search_dist, int channels, int32_t *out_u16) {
  if (!out_u16 || !g_ctx)
    return -1;
  int32_t *tmp = compute_alignment_modular_tirt_ex(
      comp_u16, h, w, tile_h, tile_w, n_layers, search_dist, channels);
  if (!tmp)
    return -2;

  int out_h = (g_ctx->h_full > 0) ? g_ctx->h_full : h;
  int out_w = (g_ctx->w_full > 0) ? g_ctx->w_full : w;

  const size_t count = (size_t)out_h * out_w * (size_t)channels;
  std::memcpy(out_u16, tmp, count * sizeof(int32_t));
  std::free(tmp);
  return 0;
}

ALIGN_API void deinit_alignment_modular_tirt() {
  if (!g_ctx)
    return;
  if (g_ctx->runtime != TI_NULL_HANDLE) {
    clear_reference_modular_tirt();
    if (g_ctx->unified_mod != TI_NULL_HANDLE) {
      ti_destroy_aot_module(g_ctx->unified_mod);
      g_ctx->unified_mod = TI_NULL_HANDLE;
    }
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