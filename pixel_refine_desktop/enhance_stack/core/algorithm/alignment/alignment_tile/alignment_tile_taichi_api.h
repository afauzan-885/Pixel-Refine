#ifndef ALIGNMENT_TILE_TAICHI_API_H
#define ALIGNMENT_TILE_TAICHI_API_H

#ifdef _WIN32
#ifdef ALIGNMENT_TILE_EXPORTS
#define ALIGN_API __declspec(dllexport)
#else
#define ALIGN_API __declspec(dllimport)
#endif
#else
#define ALIGN_API
#endif

#include <cstdint>

extern "C" {

/**
 * @brief Initialize Taichi Runtime and load the monolithic AOT module.
 */
ALIGN_API int init_alignment_modular_tirt(const char *arch_name,
                                          const char *data_dir);

/**
 * @brief Set shared preprocess parameters.
 */
ALIGN_API int set_preprocess_config_modular_tirt(float scale_gamma,
                                                 int use_sharpen);

/**
 * @brief Set alignment configuration.
 */
ALIGN_API int set_alignment_config_modular_tirt(int downscale_factor,
                                                int min_tile_size,
                                                int n_layers);

/**
 * @brief Upload reference frame to GPU.
 */
ALIGN_API int set_reference_modular_tirt(const int32_t *ref_u16, int h, int w);
ALIGN_API int set_reference_modular_tirt_ex(const int32_t *ref_u16, int h,
                                            int w, int channels);

/**
 * @brief Run Monolithic Alignment and return the Flow Field.
 * @return float* Pointer to the flow field (h * w * 2 floats).
 */
ALIGN_API float *compute_alignment_modular_tirt(const int32_t *comp_u16,
                                                 int tile_h, int tile_w,
                                                 int n_layers,
                                                 float search_dist);

ALIGN_API float *compute_alignment_modular_tirt_ex(const int32_t *comp_u16,
                                                    int h, int w,
                                                    int tile_h, int tile_w,
                                                    int n_layers,
                                                    float search_dist,
                                                    int channels);

/**
 * @brief Cleanup reference data on GPU.
 */
ALIGN_API void clear_reference_modular_tirt();

/**
 * @brief Deinitialize Taichi runtime.
 */
ALIGN_API void deinit_alignment_modular_tirt();

/**
 * @brief Free memory allocated by the DLL.
 */
ALIGN_API void free_alignment_memory(void *ptr);

} // extern "C"

#endif // ALIGNMENT_TILE_TAICHI_API_H
