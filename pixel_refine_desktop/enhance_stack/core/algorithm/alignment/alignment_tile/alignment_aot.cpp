#include "alignment_aot.h"
#include <iostream>
#include <string>
#include <taichi/cpp/taichi.hpp>
#include <vector>

// Internal state structure
struct AlignmentContext {
  ti::Runtime runtime;
  ti::AotModule module;

  // Graphs
  ti::ComputeGraph g_preprocess_rgb;
  ti::ComputeGraph g_preprocess_gray;
  ti::ComputeGraph g_downsample;
  ti::ComputeGraph g_init_flow;
  ti::ComputeGraph g_search_coarse;
  ti::ComputeGraph g_search_fine;
  ti::ComputeGraph g_upsample_flow;
  ti::ComputeGraph g_subpixel;

  // GPU Persistent Buffers (Lazy initialized)
  // Level 0: Work Res, Level 1: Work/4, Level 2: Work/16
  ti::NdArray<float> ref_pyramid[3];
  ti::NdArray<float> comp_pyramid[3];
  ti::NdArray<float> flow_pyramid[3];

  int work_h = 0;
  int work_w = 0;
  bool initialized = false;
};

static AlignmentContext *ctx = nullptr;

// Allocate buffers if size changed
void ensure_pyramid_buffers(int work_h, int work_w) {
  if (ctx->work_h == work_h && ctx->work_w == work_w &&
      ctx->ref_pyramid[0].is_valid())
    return;

  ctx->work_h = work_h;
  ctx->work_w = work_w;

  int cur_h = work_h;
  int cur_w = work_w;

  for (int i = 0; i < 3; ++i) {
    // Allocate 2D float arrays for image pyramid levels
    ctx->ref_pyramid[i] = ctx->runtime.allocate_ndarray<float>(
        {(uint32_t)cur_h, (uint32_t)cur_w}, {});
    ctx->comp_pyramid[i] = ctx->runtime.allocate_ndarray<float>(
        {(uint32_t)cur_h, (uint32_t)cur_w}, {});
    // Allocate 3D float arrays (H, W, 2) for optical flow levels
    ctx->flow_pyramid[i] = ctx->runtime.allocate_ndarray<float>(
        {(uint32_t)cur_h, (uint32_t)cur_w, 2}, {});

    cur_h /= 4;
    cur_w /= 4;
  }
}

extern "C" {

ALIGNMENT_AOT_API int init_taichi_aot_runtime(const char *module_path) {
  try {
    if (ctx) {
      delete ctx;
      ctx = nullptr;
    }
    ctx = new AlignmentContext();

    // Initialize CUDA Runtime
    ctx->runtime = ti::Runtime(TI_ARCH_CUDA);
    ctx->module = ctx->runtime.load_aot_module(module_path);

    // Map AOT Graphs
    ctx->g_preprocess_rgb = ctx->module.get_compute_graph("preprocess_rgb");
    ctx->g_preprocess_gray = ctx->module.get_compute_graph("preprocess_gray");
    ctx->g_downsample = ctx->module.get_compute_graph("downsample");
    ctx->g_init_flow = ctx->module.get_compute_graph("init_flow");
    ctx->g_search_coarse = ctx->module.get_compute_graph("search_coarse");
    ctx->g_search_fine = ctx->module.get_compute_graph("search_fine");
    ctx->g_upsample_flow = ctx->module.get_compute_graph("upsample_flow");
    ctx->g_subpixel = ctx->module.get_compute_graph("subpixel_refine");

    ctx->initialized = true;
    printf("[AlignmentAOT] Unified TCM Pipeline Initialized (AOT Mode).\n");
    return 0;
  } catch (const std::exception &e) {
    fprintf(stderr, "[AlignmentAOT] Init error: %s\n", e.what());
    return -1;
  }
}

ALIGNMENT_AOT_API int compute_preprocess_aot(const int *src_ptr, float *dst_ptr,
                                              int h, int w, int c,
                                              int dst_h, int dst_w,
                                              float scale_norm,
                                              int apply_gamma,
                                              float scale_gamma,
                                              float gamma_pow, float slope,
                                              float cutoff, int use_sharpen) {
  if (!ctx || !ctx->initialized)
    return -1;

  try {
    // Upload Source Image (i32)
    ti::NdArray<int> src_array = ctx->runtime.allocate_ndarray<int>(
        {(uint32_t)h, (uint32_t)w, (uint32_t)c}, {}, true);
    src_array.write(src_ptr, (uint32_t)(h * w * c));

    // Allocate Destination Buffer (f32)
    ti::NdArray<float> dst_array = ctx->runtime.allocate_ndarray<float>(
        {(uint32_t)dst_h, (uint32_t)dst_w}, {}, true);

    // Select Graph
    ti::ComputeGraph &g = (c == 3) ? ctx->g_preprocess_rgb : ctx->g_preprocess_gray;

    // Dispatch (Named arguments matching aot_alignment_compiler.py)
    g["src"] = src_array;
    g["dst"] = dst_array;
    g["src_h"] = h;
    g["src_w"] = w;
    g["dst_h"] = dst_h;
    g["dst_w"] = dst_w;
    g["scale_norm"] = scale_norm;
    g["apply_gamma"] = apply_gamma;
    g["scale_gamma"] = scale_gamma;
    g["gamma_pow"] = gamma_pow;
    g["slope"] = slope;
    g["cutoff"] = cutoff;
    g["use_sharpen"] = use_sharpen;
    g.launch();

    ctx->runtime.wait();

    // Download Result
    dst_array.read(dst_ptr, (uint32_t)(dst_h * dst_w));

    return 0;
  } catch (const std::exception &e) {
    fprintf(stderr, "[AlignmentAOT] Preprocess failed: %s\n", e.what());
    return -2;
  }
}

ALIGNMENT_AOT_API int set_reference_image_aot(const int *src_ptr, int h, int w,
                                              int work_h, int work_w,
                                              float scale_norm,
                                              int apply_gamma,
                                              float scale_gamma,
                                              float gamma_pow, float slope,
                                              float cutoff, int use_sharpen) {
  if (!ctx || !ctx->initialized)
    return -1;

  try {
    ensure_pyramid_buffers(work_h, work_w);

    // Upload Reference Image (RGB i32)
    ti::NdArray<int> src_array = ctx->runtime.allocate_ndarray<int>(
        {(uint32_t)h, (uint32_t)w, 3}, {}, true);
    src_array.write(src_ptr, (uint32_t)(h * w * 3));

    // Graph 1: Preprocess RGB -> Gray (Work Res L0)
    ctx->g_preprocess_rgb["src"] = src_array;
    ctx->g_preprocess_rgb["dst"] = ctx->ref_pyramid[0];
    ctx->g_preprocess_rgb["src_h"] = h;
    ctx->g_preprocess_rgb["src_w"] = w;
    ctx->g_preprocess_rgb["dst_h"] = work_h;
    ctx->g_preprocess_rgb["dst_w"] = work_w;
    ctx->g_preprocess_rgb["scale_norm"] = scale_norm;
    ctx->g_preprocess_rgb["apply_gamma"] = apply_gamma;
    ctx->g_preprocess_rgb["scale_gamma"] = scale_gamma;
    ctx->g_preprocess_rgb["gamma_pow"] = gamma_pow;
    ctx->g_preprocess_rgb["slope"] = slope;
    ctx->g_preprocess_rgb["cutoff"] = cutoff;
    ctx->g_preprocess_rgb["use_sharpen"] = use_sharpen;
    ctx->g_preprocess_rgb.launch();

    // Graph 2: Build Reference Pyramid (L0 -> L1 -> L2)
    int cur_h = work_h;
    int cur_w = work_w;
    for (int i = 0; i < 2; ++i) {
      ctx->g_downsample["src"] = ctx->ref_pyramid[i];
      ctx->g_downsample["dst"] = ctx->ref_pyramid[i + 1];
      ctx->g_downsample["h_src"] = cur_h;
      ctx->g_downsample["w_src"] = cur_w;
      ctx->g_downsample["h_dst"] = cur_h / 4;
      ctx->g_downsample["w_dst"] = cur_w / 4;
      ctx->g_downsample.launch();
      cur_h /= 4;
      cur_w /= 4;
    }

    ctx->runtime.wait();
    return 0;
  } catch (const std::exception &e) {
    fprintf(stderr, "[AlignmentAOT] Reference setup failed: %s\n", e.what());
    return -2;
  }
}

ALIGNMENT_AOT_API int compute_alignment_aot(const int *src_ptr, float *flow_ptr,
                                            int h, int w, int work_h,
                                            int work_w, float scale_norm,
                                            int apply_gamma,
                                            float scale_gamma, float init_dx,
                                            float init_dy, int use_sharpen) {
  if (!ctx || !ctx->initialized)
    return -1;

  // Standard Alignment Params (Identical to Python constants)
  const float GAMMA_POW = 2.22f;
  const float SLOPE = 4.5f;
  const float CUTOFF = 0.018f;

  try {
    ensure_pyramid_buffers(work_h, work_w);

    // 1. Preprocess Comparison Frame
    ti::NdArray<int> src_array = ctx->runtime.allocate_ndarray<int>(
        {(uint32_t)h, (uint32_t)w, 3}, {}, true);
    src_array.write(src_ptr, (uint32_t)(h * w * 3));

    ctx->g_preprocess_rgb["src"] = src_array;
    ctx->g_preprocess_rgb["dst"] = ctx->comp_pyramid[0];
    ctx->g_preprocess_rgb["src_h"] = h;
    ctx->g_preprocess_rgb["src_w"] = w;
    ctx->g_preprocess_rgb["dst_h"] = work_h;
    ctx->g_preprocess_rgb["dst_w"] = work_w;
    ctx->g_preprocess_rgb["scale_norm"] = scale_norm;
    ctx->g_preprocess_rgb["apply_gamma"] = apply_gamma;
    ctx->g_preprocess_rgb["scale_gamma"] = scale_gamma;
    ctx->g_preprocess_rgb["gamma_pow"] = GAMMA_POW;
    ctx->g_preprocess_rgb["slope"] = SLOPE;
    ctx->g_preprocess_rgb["cutoff"] = CUTOFF;
    ctx->g_preprocess_rgb["use_sharpen"] = use_sharpen;
    ctx->g_preprocess_rgb.launch();

    // 2. Build Comparison Pyramid
    int cur_h = work_h;
    int cur_w = work_w;
    for (int i = 0; i < 2; ++i) {
      ctx->g_downsample["src"] = ctx->comp_pyramid[i];
      ctx->g_downsample["dst"] = ctx->comp_pyramid[i + 1];
      ctx->g_downsample["h_src"] = cur_h;
      ctx->g_downsample["w_src"] = cur_w;
      ctx->g_downsample["h_dst"] = cur_h / 4;
      ctx->g_downsample["w_dst"] = cur_w / 4;
      ctx->g_downsample.launch();
      cur_h /= 4;
      cur_w /= 4;
    }

    // --- 3. Hierarchical Refinement (L2 -> L1 -> L0) ---

    // Coarsest Level (L2: 1/16 res)
    int h2 = work_h / 16;
    int w2 = work_w / 16;

    ctx->g_init_flow["flow"] = ctx->flow_pyramid[2];
    ctx->g_init_flow["h"] = h2;
    ctx->g_init_flow["w"] = w2;
    ctx->g_init_flow["init_dx"] = init_dx / 16.0f;
    ctx->g_init_flow["init_dy"] = init_dy / 16.0f;
    ctx->g_init_flow.launch();

    // Search L2
    ctx->g_search_coarse["ref"] = ctx->ref_pyramid[2];
    ctx->g_search_coarse["comp"] = ctx->comp_pyramid[2];
    ctx->g_search_coarse["flow"] = ctx->flow_pyramid[2];
    ctx->g_search_coarse["prev_flow"] = ctx->flow_pyramid[2]; // self fallback
    ctx->g_search_coarse["out_flow"] = ctx->flow_pyramid[2]; // out
    ctx->g_search_coarse["h"] = h2;
    ctx->g_search_coarse["w"] = w2;
    ctx->g_search_coarse["tile_h"] = 8;  // tile_h (MIN_TILE_SIZE)
    ctx->g_search_coarse["tile_w"] = 8;  // tile_w
    ctx->g_search_coarse["dist"] = 16; // search_radius
    ctx->g_search_coarse["prev_h"] = 1; // dummy 
    ctx->g_search_coarse["prev_w"] = 1; // dummy 
    ctx->g_search_coarse["downscale"] = 4; // factor
    ctx->g_search_coarse.launch();

    // Refine L1 (1/4 res)
    ctx->g_upsample_flow["src"] = ctx->flow_pyramid[2];
    ctx->g_upsample_flow["dst"] = ctx->flow_pyramid[1];
    ctx->g_upsample_flow["h_src"] = h2;
    ctx->g_upsample_flow["w_src"] = w2;
    ctx->g_upsample_flow["h_dst"] = work_h / 4;
    ctx->g_upsample_flow["w_dst"] = work_w / 4;
    ctx->g_upsample_flow["scale"] = 4.0f;
    ctx->g_upsample_flow.launch();

    ctx->g_search_fine["ref"] = ctx->ref_pyramid[1];
    ctx->g_search_fine["comp"] = ctx->comp_pyramid[1];
    ctx->g_search_fine["flow"] = ctx->flow_pyramid[1]; // guide
    ctx->g_search_fine["prev_flow"] = ctx->flow_pyramid[2]; // coarase level
    ctx->g_search_fine["out_flow"] = ctx->flow_pyramid[1]; // out
    ctx->g_search_fine["h"] = work_h / 4;
    ctx->g_search_fine["w"] = work_w / 4;
    ctx->g_search_fine["tile_h"] = 8;
    ctx->g_search_fine["tile_w"] = 8;
    ctx->g_search_fine["prev_h"] = h2;
    ctx->g_search_fine["prev_w"] = w2;
    ctx->g_search_fine["downscale"] = 4;
    ctx->g_search_fine.launch();

    // Refine L0 (Full Res)
    ctx->g_upsample_flow["src"] = ctx->flow_pyramid[1];
    ctx->g_upsample_flow["dst"] = ctx->flow_pyramid[0];
    ctx->g_upsample_flow["h_src"] = work_h / 4;
    ctx->g_upsample_flow["w_src"] = work_w / 4;
    ctx->g_upsample_flow["h_dst"] = work_h;
    ctx->g_upsample_flow["w_dst"] = work_w;
    ctx->g_upsample_flow["scale"] = 4.0f;
    ctx->g_upsample_flow.launch();

    ctx->g_search_fine["ref"] = ctx->ref_pyramid[0];
    ctx->g_search_fine["comp"] = ctx->comp_pyramid[0];
    ctx->g_search_fine["flow"] = ctx->flow_pyramid[0];
    ctx->g_search_fine["prev_flow"] = ctx->flow_pyramid[1];
    ctx->g_search_fine["out_flow"] = ctx->flow_pyramid[0];
    ctx->g_search_fine["h"] = work_h;
    ctx->g_search_fine["w"] = work_w;
    ctx->g_search_fine["tile_h"] = 16; // Larger tiles for fine res
    ctx->g_search_fine["tile_w"] = 16;
    ctx->g_search_fine["prev_h"] = work_h / 4;
    ctx->g_search_fine["prev_w"] = work_w / 4;
    ctx->g_search_fine["downscale"] = 4;
    ctx->g_search_fine.launch();

    // Subpixel Peak Refinement
    ctx->g_subpixel["ref"] = ctx->ref_pyramid[0];
    ctx->g_subpixel["comp"] = ctx->comp_pyramid[0];
    ctx->g_subpixel["flow"] = ctx->flow_pyramid[0];
    ctx->g_subpixel["out_flow"] = ctx->flow_pyramid[0];
    ctx->g_subpixel["h"] = work_h;
    ctx->g_subpixel["w"] = work_w;
    ctx->g_subpixel["tile_h"] = 16;
    ctx->g_subpixel["tile_w"] = 16;
    ctx->g_subpixel.launch();

    // Download Result
    ctx->flow_pyramid[0].read(flow_ptr, (uint32_t)(work_h * work_w * 2));

    ctx->runtime.wait();
    return 0;
  } catch (const std::exception &e) {
    fprintf(stderr, "[AlignmentAOT] Alignment execution failed: %s\n", e.what());
    return -3;
  }
}

ALIGNMENT_AOT_API void destroy_alignment_aot_runtime() {
  if (ctx) {
    delete ctx;
    ctx = nullptr;
  }
}

} // extern "C"
