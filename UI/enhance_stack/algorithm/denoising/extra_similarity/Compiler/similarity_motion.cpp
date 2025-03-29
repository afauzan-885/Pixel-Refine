// compute_motion_metrics.cpp
#include <cmath>
#include <cstdlib>
#include <omp.h>
#include <immintrin.h>  // Header untuk SIMD (AVX, SSE)

extern "C" {
    void compute_motion_metrics(const float* current_tile, const float* reference_tile,
                                int tile_h, int tile_w, int channels, int row_stride,
                                float prev_threshold, float motion_threshold, float noise_threshold,
                                float alpha, int max_passes, float epsilon,
                                float* similarity_weight, float* adaptive_threshold_out) {
        int n = tile_h * tile_w * channels;
        double s = 0.0;
        double sum_diff = 0.0;
        double s_spatial = 0.0;  // Untuk akumulasi perbedaan spasial
    
        #pragma omp parallel for simd reduction(+:s, sum_diff, s_spatial) schedule(static)
        for (int idx = 0; idx < tile_h * tile_w; idx++) {
            int i = idx / tile_w;
            int j = idx % tile_w;
            int base = i * row_stride + j * channels;
    
            for (int k = 0; k < channels; k += 4) {
                // Load current & reference pixel
                __m128 current = _mm_loadu_ps(&current_tile[base + k]);
                __m128 reference = _mm_loadu_ps(&reference_tile[base + k]);
                __m128 diff = _mm_sub_ps(current, reference);
                __m128 diff_sq = _mm_mul_ps(diff, diff);
    
                // Perbedaan langsung
                s += diff_sq[0] + diff_sq[1] + diff_sq[2] + diff_sq[3];
                sum_diff += diff[0] + diff[1] + diff[2] + diff[3];
    
                // Perbedaan Spasial (Horizontal)
                if (j < tile_w - 1) {  
                    __m128 next_pixel = _mm_loadu_ps(&current_tile[base + k + channels]); // Piksel sebelah kanan
                    __m128 diff_x = _mm_sub_ps(current, next_pixel);
                    __m128 diff_x_sq = _mm_mul_ps(diff_x, diff_x);
                    s_spatial += diff_x_sq[0] + diff_x_sq[1] + diff_x_sq[2] + diff_x_sq[3];
                }
    
                // Perbedaan Spasial (Vertikal)
                if (i < tile_h - 1) {  
                    __m128 below_pixel = _mm_loadu_ps(&current_tile[base + k + row_stride]); // Piksel di bawah
                    __m128 diff_y = _mm_sub_ps(current, below_pixel);
                    __m128 diff_y_sq = _mm_mul_ps(diff_y, diff_y);
                    s_spatial += diff_y_sq[0] + diff_y_sq[1] + diff_y_sq[2] + diff_y_sq[3];
                }
            }
        }
    
        // Gabungkan dengan bobot spasial
        float mse_score = static_cast<float>((s + s_spatial) / (2.0f * n));
        float mean_diff = static_cast<float>(sum_diff / n);
        float variance = mse_score - mean_diff * mean_diff;
        if (variance < 0.0f) 
            variance = 0.0f;
        float sigma_noise = std::sqrt(variance);
        
        float dz = mse_score;
        float dz_norm = dz / (1.0f + sigma_noise);
        float new_threshold = motion_threshold + noise_threshold * dz_norm;
        float adaptive_threshold = alpha * prev_threshold + (1.0f - alpha) * new_threshold;
    
        for (int pass = 0; pass < max_passes; pass++) {
            float prev_value = adaptive_threshold;
            adaptive_threshold = alpha * prev_value + (1.0f - alpha) *
                                 (motion_threshold + noise_threshold * (dz / (1.0f + dz / prev_value)));
            if (std::fabs(adaptive_threshold - prev_value) < epsilon) {
                break;
            }
        }
    
        float sim_weight = std::exp(-dz / (adaptive_threshold + epsilon));
        *similarity_weight = sim_weight;
        *adaptive_threshold_out = adaptive_threshold;
    }
    

// Fungsi accumulate_tiles_jit
void accumulate_tiles_jit(float* final_image, float* weight_map,
                          const float* current_image, const float* reference_image,
                          const float* base_window,
                          const int* row_starts, const int* col_starts,
                          int num_row_starts, int num_col_starts,
                          int tile_h, int tile_w,
                          int h, int w, int channels,
                          float motion_threshold, float noise_threshold, float scale,
                          float alpha, int max_passes, float epsilon) {
    int row_stride = w * channels;
    
    omp_set_num_threads(omp_get_max_threads());
    #pragma omp parallel
    {
        #pragma omp for collapse(2) schedule(static) nowait
        for (int i = 0; i < num_row_starts; i++) {
            for (int j = 0; j < num_col_starts; j++) {
                int r = row_starts[i];
                int c = col_starts[j];

                if (r + tile_h > h || c + tile_w > w)
                    continue;

                const float* current_tile_ptr = current_image + (r * row_stride) + (c * channels);
                const float* reference_tile_ptr = reference_image + (r * row_stride) + (c * channels);

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

                for (int a = 0; a < tile_h; a++) {
                    int global_row = r + a;
                    int final_row_offset = global_row * row_stride;
                    int weight_row_offset = global_row * w;

                    #pragma omp simd
                    for (int b = 0; b < tile_w; b++) {
                        int final_index = final_row_offset + (c + b) * channels;
                        int weight_index = weight_row_offset + (c + b);
                        int base_window_idx = a * tile_w + b;
                        float window_factor = base_window[base_window_idx] * sim_weight;

                        for (int ch = 0; ch < channels; ch += 4) {
                            __m128 cur_val = _mm_loadu_ps(&current_image[final_index + ch]);
                            __m128 weight_f = _mm_set1_ps(window_factor * scale);
                            __m128 result = _mm_mul_ps(cur_val, weight_f);
                            _mm_storeu_ps(&local_final_image[(a * tile_w + b) * channels + ch], result);
                        }

                        local_weight_map[a * tile_w + b] += window_factor;
                    }
                }

                // Reduksi ke array global untuk mengurangi operasi atomik
                #pragma omp critical
                {
                    for (int a = 0; a < tile_h; a++) {
                        int global_row = r + a;
                        int final_row_offset = global_row * row_stride;
                        int weight_row_offset = global_row * w;

                        for (int b = 0; b < tile_w; b++) {
                            int final_index = final_row_offset + (c + b) * channels;
                            int weight_index = weight_row_offset + (c + b);

                            for (int ch = 0; ch < channels; ch++) {
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

} // end extern "C"
