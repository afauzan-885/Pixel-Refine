#include <cmath>
#include <cstdlib>
#include <omp.h>
#include <immintrin.h> // Header SIMD untuk AVX/SSE

// Fungsi utilitas untuk reduksi horizontal pada __m256
inline float reduce_add_ps(__m256 vec)
{
    __m128 low = _mm256_castps256_ps128(vec);    // Ambil 128 bit rendah
    __m128 high = _mm256_extractf128_ps(vec, 1); // Ambil 128 bit tinggi
    __m128 sum = _mm_add_ps(low, high);          // Tambahkan dua bagian
    sum = _mm_hadd_ps(sum, sum);                 // Horizontal add (2 elemen pertama)
    sum = _mm_hadd_ps(sum, sum);                 // Horizontal add (2 elemen terakhir)
    return _mm_cvtss_f32(sum);                   // Ambil elemen scalar hasil akhir
}

extern "C"
{
    void compute_motion_metrics(const float *current_tile, const float *reference_tile,
                                int tile_h, int tile_w, int channels, int row_stride,
                                float prev_threshold, float motion_threshold, float noise_threshold,
                                float alpha, int max_passes, float epsilon,
                                float *similarity_weight, float *adaptive_threshold_out)
    {
        int n = tile_h * tile_w * channels;
        double s = 0.0;
        double sum_diff = 0.0;

#pragma omp parallel for collapse(2) reduction(+ : s, sum_diff) schedule(static)
        for (int i = 0; i < tile_h; i++)
        {
            for (int j = 0; j < tile_w; j++)
            {
                int base = i * row_stride + j * channels;

                // Hanya hitung gradien sekali untuk channel pertama (k == 0)
                __m256 grad_diff_sq_shared = _mm256_setzero_ps();
                if (channels > 0)
                {
                    int k_shared = 0;
                    int base_shared = base + k_shared;

                    __m256 current_x = _mm256_setzero_ps();
                    __m256 reference_x = _mm256_setzero_ps();
                    if (j > 0 && j < tile_w - 1)
                    {
                        current_x = _mm256_sub_ps(
                            _mm256_loadu_ps(&current_tile[base_shared + channels]),
                            _mm256_loadu_ps(&current_tile[base_shared - channels]));
                        reference_x = _mm256_sub_ps(
                            _mm256_loadu_ps(&reference_tile[base_shared + channels]),
                            _mm256_loadu_ps(&reference_tile[base_shared - channels]));
                    }

                    __m256 current_y = _mm256_setzero_ps();
                    __m256 reference_y = _mm256_setzero_ps();
                    if (i > 0 && i < tile_h - 1)
                    {
                        current_y = _mm256_sub_ps(
                            _mm256_loadu_ps(&current_tile[base_shared + row_stride]),
                            _mm256_loadu_ps(&current_tile[base_shared - row_stride]));
                        reference_y = _mm256_sub_ps(
                            _mm256_loadu_ps(&reference_tile[base_shared + row_stride]),
                            _mm256_loadu_ps(&reference_tile[base_shared - row_stride]));
                    }

                    __m256 grad_diff_x = _mm256_sub_ps(current_x, reference_x);
                    __m256 grad_diff_y = _mm256_sub_ps(current_y, reference_y);
                    grad_diff_sq_shared = _mm256_add_ps(
                        _mm256_mul_ps(grad_diff_x, grad_diff_x),
                        _mm256_mul_ps(grad_diff_y, grad_diff_y));
                }

#pragma omp simd reduction(+ : s, sum_diff)
                for (int k = 0; k < channels; k += 8)
                {
                    __m256 current = _mm256_loadu_ps(&current_tile[base + k]);
                    __m256 reference = _mm256_loadu_ps(&reference_tile[base + k]);
                    __m256 diff = _mm256_sub_ps(current, reference);
                    __m256 diff_sq = _mm256_mul_ps(diff, diff);

                    // Gunakan hasil perhitungan gradien yang sudah dihitung sebelumnya
                    __m256 grad_diff_sq = grad_diff_sq_shared;

                    // Optimisasi patch-based (3×3)
                    __m256 patch_sum = _mm256_setzero_ps();
                    int patch_count = 0;

                    for (int di = -1; di <= 1; di++)
                    {
                        for (int dj = -1; dj <= 1; dj++)
                        {
                            int ni = i + di;
                            int nj = j + dj;
                            if (ni >= 0 && ni < tile_h && nj >= 0 && nj < tile_w)
                            {
                                int neighbor_base = ni * row_stride + nj * channels;
                                __m256 neighbor_pixel = _mm256_loadu_ps(&current_tile[neighbor_base + k]);
                                __m256 patch_diff = _mm256_sub_ps(current, neighbor_pixel);
                                __m256 patch_diff_sq = _mm256_mul_ps(patch_diff, patch_diff);
                                patch_sum = _mm256_add_ps(patch_sum, patch_diff_sq);
                                patch_count++;
                            }
                        }
                    }

                    // Akumulasi hasil
                    s += reduce_add_ps(diff_sq);
                    s += reduce_add_ps(grad_diff_sq);
                    sum_diff += reduce_add_ps(diff);

                    if (patch_count > 0)
                    {
                        s += reduce_add_ps(patch_sum) / patch_count;
                    }
                }
            }
        }

        // Gabungkan hasil
        float mse_score = static_cast<float>(s / (2.0 * n));
        float mean_diff = static_cast<float>(sum_diff / n);
        float variance = mse_score - mean_diff * mean_diff;
        variance = (variance < 0.0f) ? 0.0f : variance;
        float sigma_noise = std::sqrt(variance);

        // Adaptif threshold
        float dz = mse_score;
        float dz_norm = dz / (1.0f + sigma_noise);
        float new_threshold = motion_threshold + noise_threshold * dz_norm;
        float adaptive_threshold = alpha * prev_threshold + (1.0f - alpha) * new_threshold;

        for (int pass = 0; pass < max_passes; pass++)
        {
            float prev_value = adaptive_threshold;
            adaptive_threshold = alpha * prev_value + (1.0f - alpha) *
                                                          (motion_threshold + noise_threshold * (dz / (1.0f + dz / prev_value)));
            if (std::fabs(adaptive_threshold - prev_value) < epsilon)
            {
                break;
            }
        }

        float sim_weight = std::exp(-dz / (adaptive_threshold + epsilon));
        *similarity_weight = sim_weight;
        *adaptive_threshold_out = adaptive_threshold;
    }

    void accumulate_tiles_jit(float *final_image, float *weight_map,
                              const float *current_image, const float *reference_image,
                              const float *base_window,
                              const int *row_starts, const int *col_starts,
                              int num_row_starts, int num_col_starts,
                              int tile_h, int tile_w,
                              int h, int w, int channels,
                              float motion_threshold, float noise_threshold, float scale,
                              float alpha, int max_passes, float epsilon)
    {
        int row_stride = w * channels;

        omp_set_num_threads(omp_get_max_threads());
#pragma omp parallel for collapse(2) schedule(static)
        for (int i = 0; i < num_row_starts; i++)
        {
            for (int j = 0; j < num_col_starts; j++)
            {
                int r = row_starts[i];
                int c = col_starts[j];

                if (r + tile_h > h || c + tile_w > w)
                    continue;

                const float *current_tile_ptr = current_image + (r * row_stride) + (c * channels);
                const float *reference_tile_ptr = reference_image + (r * row_stride) + (c * channels);

                float sim_weight = 0.0f;
                float adaptive_threshold = motion_threshold;

                compute_motion_metrics(current_tile_ptr, reference_tile_ptr,
                                       tile_h, tile_w, channels, row_stride,
                                       motion_threshold, motion_threshold, noise_threshold,
                                       alpha, max_passes, epsilon,
                                       &sim_weight, &adaptive_threshold);

                // Buffer lokal untuk mengurangi operasi atomik
                float local_final_image[tile_h * tile_w * channels] = {0};
                float local_weight_map[tile_h * tile_w] = {0};

                for (int a = 0; a < tile_h; a++)
                {
                    int global_row = r + a;
                    int final_row_offset = global_row * row_stride;
                    int weight_row_offset = global_row * w;

#pragma omp simd
                    for (int b = 0; b < tile_w; b++)
                    {
                        int final_index = final_row_offset + (c + b) * channels;
                        int weight_index = weight_row_offset + (c + b);
                        int base_window_idx = a * tile_w + b;
                        float window_factor = base_window[base_window_idx] * sim_weight;

                        for (int ch = 0; ch < channels; ch += 4)
                        {
                            __m128 cur_val = _mm_loadu_ps(&current_image[final_index + ch]);
                            __m128 weight_f = _mm_set1_ps(window_factor * scale);
                            __m128 result = _mm_mul_ps(cur_val, weight_f);
                            _mm_storeu_ps(&local_final_image[(a * tile_w + b) * channels + ch], result);
                        }

                        local_weight_map[a * tile_w + b] += window_factor;
                    }
                }

                // Reduksi ke array global untuk menghindari bottleneck
#pragma omp critical
                {
                    for (int a = 0; a < tile_h; a++)
                    {
                        int global_row = r + a;
                        int final_row_offset = global_row * row_stride;
                        int weight_row_offset = global_row * w;

                        for (int b = 0; b < tile_w; b++)
                        {
                            int final_index = final_row_offset + (c + b) * channels;
                            int weight_index = weight_row_offset + (c + b);

                            for (int ch = 0; ch < channels; ch++)
                            {
                                final_image[final_index + ch] += local_final_image[(a * tile_w + b) * channels + ch];
                            }
                            weight_map[weight_index] += local_weight_map[a * tile_w + b];
                        }
                    }
                }
            }
        }
    }
}