#ifndef PREPROCESSING_AOT_H
#define PREPROCESSING_AOT_H

#ifdef _WIN32
    #ifdef PREPROCESSING_AOT_EXPORTS
        #define PREPROCESS_API __declspec(dllexport)
    #else
        #define PREPROCESS_API __declspec(dllimport)
    #endif
#else
    #define PREPROCESS_API
#endif

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Inisialisasi Taichi AOT Runtime
 */
PREPROCESS_API int init_taichi_aot_runtime(const char* module_path);

/**
 * Eksekusi pipeline preprocessing terpadu:
 * Normalize -> Gamma -> Extract Green -> Resize
 */
PREPROCESS_API int compute_preprocess_aot(
    const int* src_ptr,  // Input: Raw image data (int32)
    float* dst_ptr,      // Output: Preprocessed data (float32)
    int src_h, int src_w, int src_c,
    int dst_h, int dst_w,
    float scale_norm,
    float scale_gamma,
    float gamma_pow,
    float slope,
    float cutoff,
    int use_sharpen
);

#ifdef __cplusplus
}
#endif

#endif // PREPROCESSING_AOT_H
