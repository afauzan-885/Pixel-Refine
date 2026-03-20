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
 * @brief Menginisialisasi Taichi Runtime dan memuat 3 modul AOT modular.
 *
 * @param arch_name Nama arsitektur target ("cuda", "vulkan", atau "cpu").
 * @param data_dir Path ke direktori yang berisi file .tcm
 * (preprocess_{arch}.tcm, dll).
 * @return int 0 jika sukses, negatif jika gagal.
 */
ALIGN_API int init_alignment_modular_tirt(const char *arch_name,
                                          const char *data_dir);

/**
 * @brief Mengatur parameter preprocess shared (gamma/scale/sharpen) untuk
 * kernel AOT.
 */
ALIGN_API int set_preprocess_config_modular_tirt(float scale_gamma,
                                                 int use_sharpen);

/**
 * @brief Mengatur parameter alignment shared agar parity dengan Python tetap
 * sinkron.
 *
 * @param downscale_factor Faktor downsample antar level pyramid (umumnya 4).
 * @param min_tile_size Ukuran tile minimum clamp (setara
 * ImageAlignmentConfig.MIN_TILE_SIZE).
 */
ALIGN_API int set_alignment_config_modular_tirt(int downscale_factor,
                                                int min_tile_size);

/**
 * @brief Mengunggah dan menormalisasi gambar referensi ke GPU.
 */
ALIGN_API int set_reference_modular_tirt(const int32_t *ref_u16, int h, int w);
ALIGN_API int set_reference_modular_tirt_ex(const int32_t *ref_u16, int h,
                                            int w, int channels);

/**
 * @brief Menjalankan alignment dan warping untuk gambar komparasi menggunakan
 * referensi yang sudah ada di GPU.
 */
ALIGN_API int32_t *compute_alignment_modular_tirt(const int32_t *comp_u16,
                                                  int tile_h, int tile_w,
                                                  int n_layers,
                                                  float search_dist);
ALIGN_API int32_t *compute_alignment_modular_tirt_ex(const int32_t *comp_u16,
                                                     int tile_h, int tile_w,
                                                     int n_layers,
                                                     float search_dist,
                                                     int channels);
ALIGN_API int compute_alignment_modular_tirt_into_ex(
    const int32_t *comp_u16, int tile_h, int tile_w, int n_layers,
    float search_dist, int channels, int32_t *out_u16);

/**
 * @brief Membersihkan data referensi di GPU.
 */
ALIGN_API void clear_reference_modular_tirt();

/**
 * @brief Membersihkan dan menghancurkan (destroy) Taichi Runtime.
 */
ALIGN_API void deinit_alignment_modular_tirt();

/**
 * @brief Membebasakan memori yang dialokasikan oleh DLL.
 */
ALIGN_API void free_u16_memory(int32_t *ptr);

} // extern "C"

#endif // ALIGNMENT_TILE_TAICHI_API_H
