#ifndef ALIGNMENT_AOT_H
#define ALIGNMENT_AOT_H

#include <stdint.h>

#ifdef _WIN32
#ifdef ALIGNMENT_AOT_EXPORTS
#define ALIGNMENT_AOT_API __declspec(dllexport)
#else
#define ALIGNMENT_AOT_API __declspec(dllimport)
#endif
#else
#define ALIGNMENT_AOT_API
#endif

extern "C" {
// Initialize the AOT runtime and load the module
ALIGNMENT_AOT_API int init_taichi_aot_runtime(const char *module_path);

// Compute only preprocessing (fused) for a single image layer
ALIGNMENT_AOT_API int compute_preprocess_aot(const int *src_ptr, float *dst_ptr,
                                              int h, int w, int c,
                                              int dst_h, int dst_w,
                                              float scale_norm,
                                              int apply_gamma,
                                              float scale_gamma,
                                              float gamma_pow, float slope,
                                              float cutoff, int use_sharpen);

// Set the reference image (Preprocessing + Pyramid L0, L1, L2)
ALIGNMENT_AOT_API int set_reference_image_aot(const int *src_ptr, int h, int w,
                                              int work_h, int work_w,
                                              float scale_norm,
                                              int apply_gamma,
                                              float scale_gamma,
                                              float gamma_pow, float slope,
                                              float cutoff, int use_sharpen);

// Compute alignment for a comparative frame
ALIGNMENT_AOT_API int compute_alignment_aot(const int *src_ptr, float *flow_ptr,
                                            int h, int w, int work_h,
                                            int work_w, float scale_norm,
                                            int apply_gamma,
                                            float scale_gamma, float init_dx,
                                            float init_dy, int use_sharpen);

// Destroy runtime and free resources
ALIGNMENT_AOT_API void destroy_alignment_aot_runtime();
}

#endif // ALIGNMENT_AOT_H
