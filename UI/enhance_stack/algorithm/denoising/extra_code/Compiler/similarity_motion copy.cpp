#include <cmath>
#include <cstdlib>
#include <omp.h>
#include <immintrin.h> // Header SIMD untuk AVX/SS

// Fungsi utilitas untuk reduksi horizontal pada __m256
inline float reduce_add_ps(__m256 vec)
{
    __m128 low = _mm256_castps256_ps128(vec);
    __m128 high = _mm256_extractf128_ps(vec, 1);
    __m128 sum = _mm_add_ps(low, high);
    sum = _mm_hadd_ps(sum, sum);
    sum = _mm_hadd_ps(sum, sum);
    return _mm_cvtss_f32(sum);
}

extern "C"
{
    void compute_motion_metrics(const float *current_tile, const float *reference_tiles[10],
                                int tile_h, int tile_w, int channels, int row_stride,
                                float prev_threshold, float motion_threshold, float noise_threshold,
                                float alpha, int max_passes, float epsilon,
                                float *similarity_weight, float *adaptive_threshold_out)
    {
        int n = tile_h * tile_w * channels;
        double s = 0.0;
        double sum_diff = 0.0;
        double temp_diff_sum = 0.0;

        #pragma omp parallel for collapse(2) reduction(+ : s, sum_diff, temp_diff_sum) schedule(static)
        for (int i = 0; i < tile_h; i++)
        {
            for (int j = 0; j < tile_w; j++)
            {
                int base = i * row_stride + j * channels;

                __m256 temp_diff_accum = _mm256_setzero_ps();
                __m256 cos_sim_accum = _mm256_setzero_ps();

                for (int k = 0; k < channels; k += 8)
                {
                    __m256 current = _mm256_loadu_ps(&current_tile[base + k]);

                    __m256 gx_current = _mm256_setzero_ps();
                    __m256 gy_current = _mm256_setzero_ps();

                    for (int ref_idx = 0; ref_idx < 10; ref_idx++)
                    {
                        __m256 reference = _mm256_loadu_ps(&reference_tiles[ref_idx][base + k]);

                        __m256 gx_ref = _mm256_setzero_ps();
                        __m256 gy_ref = _mm256_setzero_ps();

                        __m256 dot_product = _mm256_add_ps(_mm256_mul_ps(gx_current, gx_ref), _mm256_mul_ps(gy_current, gy_ref));
                        __m256 mag_current = _mm256_sqrt_ps(_mm256_add_ps(_mm256_mul_ps(gx_current, gx_current), _mm256_mul_ps(gy_current, gy_current)));
                        __m256 mag_ref = _mm256_sqrt_ps(_mm256_add_ps(_mm256_mul_ps(gx_ref, gx_ref), _mm256_mul_ps(gy_ref, gy_ref)));

                        __m256 cos_sim = _mm256_div_ps(dot_product, _mm256_add_ps(_mm256_mul_ps(mag_current, mag_ref), _mm256_set1_ps(1e-6f)));
                        cos_sim_accum = _mm256_add_ps(cos_sim_accum, cos_sim);

                        __m256 diff = _mm256_sub_ps(current, reference);
                        __m256 diff_sq = _mm256_mul_ps(diff, diff);
                        temp_diff_accum = _mm256_add_ps(temp_diff_accum, diff_sq);
                    }
                }

                __m256 avg_cos_sim = _mm256_div_ps(cos_sim_accum, _mm256_set1_ps(10.0f));
                __m256 gos_score = _mm256_sub_ps(_mm256_set1_ps(1.0f), avg_cos_sim);
                __m256 temp_diff_avg = _mm256_div_ps(temp_diff_accum, _mm256_set1_ps(10.0f));
                __m256 enhanced_threshold = _mm256_add_ps(temp_diff_avg, _mm256_mul_ps(gos_score, _mm256_set1_ps(noise_threshold)));

                s += reduce_add_ps(enhanced_threshold);
                sum_diff += reduce_add_ps(temp_diff_avg);
                temp_diff_sum += reduce_add_ps(temp_diff_avg);
            }
        }

        float mse_score = static_cast<float>(s / (2.0 * n));
        float mean_diff = static_cast<float>(sum_diff / n);
        float variance = mse_score - mean_diff * mean_diff;
        variance = (variance < 0.0f) ? 0.0f : variance;
        float sigma_noise = std::sqrt(variance);

        float temp_variance = static_cast<float>(temp_diff_sum / n);
        float dz = mse_score + temp_variance;
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

                const float *ref_tiles[10] = {
                    reference_tile_ptr, reference_tile_ptr, reference_tile_ptr, reference_tile_ptr, reference_tile_ptr,
                    reference_tile_ptr, reference_tile_ptr, reference_tile_ptr, reference_tile_ptr, reference_tile_ptr
                };
                compute_motion_metrics(current_tile_ptr, ref_tiles,
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