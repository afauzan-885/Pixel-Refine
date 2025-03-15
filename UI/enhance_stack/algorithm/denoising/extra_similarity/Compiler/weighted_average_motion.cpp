// compute_motion_metrics.cpp
#include <cmath>
#include <cstdlib>
#include <omp.h>
#include <immintrin.h>  // Header untuk SIMD (AVX, SSE)
#include <vector>
#include <algorithm>

extern "C" {    
    extern "C" {    
        void compute_motion_metrics(const float* current_tile, const float* reference_tile,
                                    int tile_h, int tile_w, int channels, int row_stride,
                                    float prev_threshold, float motion_threshold, 
                                    float alpha, int max_passes, float epsilon,
                                    float* similarity_weight, float* adaptive_threshold_out) {
            
            float sum_grad_diff = 0.0f;
            int count = 0;
            float delta = 1.0f; // Huber loss threshold
    
            // Menggunakan OpenMP untuk paralelisasi loop
            #pragma omp parallel for reduction(+:sum_grad_diff, count) schedule(static) collapse(2)
            for (int i = 1; i < tile_h - 1; i++) {
                for (int j = 1; j < tile_w - 1; j++) {
                    int base = i * row_stride + j * channels;
                    
                    for (int k = 0; k < channels; k += 8) { // Proses 8 elemen sekaligus dengan AVX
                        __m256 gx_current, gy_current, gx_ref, gy_ref;
    
                        __m256 cur_left   = _mm256_loadu_ps(&current_tile[base - channels + k]);
                        __m256 cur_right  = _mm256_loadu_ps(&current_tile[base + channels + k]);
                        __m256 cur_top    = _mm256_loadu_ps(&current_tile[base - row_stride + k]);
                        __m256 cur_bottom = _mm256_loadu_ps(&current_tile[base + row_stride + k]);
    
                        __m256 ref_left   = _mm256_loadu_ps(&reference_tile[base - channels + k]);
                        __m256 ref_right  = _mm256_loadu_ps(&reference_tile[base + channels + k]);
                        __m256 ref_top    = _mm256_loadu_ps(&reference_tile[base - row_stride + k]);
                        __m256 ref_bottom = _mm256_loadu_ps(&reference_tile[base + row_stride + k]);
    
                        // Gradien X dan Y
                        gx_current = _mm256_sub_ps(cur_right, cur_left);
                        gy_current = _mm256_sub_ps(cur_bottom, cur_top);
                        gx_ref     = _mm256_sub_ps(ref_right, ref_left);
                        gy_ref     = _mm256_sub_ps(ref_bottom, ref_top);
    
                        // Gradien magnitude
                        __m256 grad_cur = _mm256_sqrt_ps(_mm256_add_ps(
                            _mm256_mul_ps(gx_current, gx_current), 
                            _mm256_mul_ps(gy_current, gy_current)));
    
                        __m256 grad_ref = _mm256_sqrt_ps(_mm256_add_ps(
                            _mm256_mul_ps(gx_ref, gx_ref), 
                            _mm256_mul_ps(gy_ref, gy_ref)));
    
                        // Perbedaan gradien absolut
                        __m256 grad_diff = _mm256_sub_ps(grad_cur, grad_ref);
                        grad_diff = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), grad_diff); // abs()
    
                        // Huber loss
                        __m256 delta_vec = _mm256_set1_ps(delta);
                        __m256 huber_mask = _mm256_cmp_ps(grad_diff, delta_vec, _CMP_LT_OS);
                        __m256 huber_part1 = _mm256_mul_ps(_mm256_set1_ps(0.5f), _mm256_mul_ps(grad_diff, grad_diff));
                        __m256 huber_part2 = _mm256_sub_ps(_mm256_mul_ps(delta_vec, grad_diff), _mm256_set1_ps(0.5f * delta));
    
                        __m256 huber_loss = _mm256_blendv_ps(huber_part2, huber_part1, huber_mask);
    
                        // Simpan hasil dalam array untuk reduksi
                        float diff_vals[8];
                        _mm256_storeu_ps(diff_vals, huber_loss);
    
                        sum_grad_diff += diff_vals[0] + diff_vals[1] + diff_vals[2] + diff_vals[3] +
                                         diff_vals[4] + diff_vals[5] + diff_vals[6] + diff_vals[7];
    
                        count += 8;
                    }
                }
            }
    
            // Rata-rata gradien sebagai pengganti median (lebih cepat)
            float dz = sum_grad_diff / count;
    
            // Clipping threshold (mengabaikan outlier ekstrem)
            dz = std::min(dz, 3.0f); // Jika dz lebih dari 5, anggap noise dan potong nilainya
    
            // Threshold adaptif lebih ringan
            float beta = 0.5f;  // Mengurangi osilasi threshold
            float new_threshold = beta * prev_threshold + (1 - beta) * (motion_threshold / (dz + 1.0f));
    
            float adaptive_threshold = alpha * prev_threshold + (1.0f - alpha) * new_threshold;
    
            // Perbaiki threshold dengan iterasi yang lebih ringan
            for (int pass = 0; pass < max_passes; pass++) {
                float prev_value = adaptive_threshold;
                adaptive_threshold = alpha * prev_value + (1.0f - alpha) * new_threshold;
                if (std::fabs(adaptive_threshold - prev_value) < epsilon) {
                    break;
                }
            }
    
            // Bobot similarity menggunakan eksponensial (lebih ringan)
            float sim_weight = std::exp(-dz / (adaptive_threshold + epsilon));
    
            *similarity_weight = sim_weight;
            *adaptive_threshold_out = adaptive_threshold;
        }
    }

// Fungsi accumulate_tiles_jit tidak berubah, tetap memanggil compute_motion_metrics di atas
void accumulate_tiles_jit(float* final_image, float* weight_map,
                          const float* current_image, const float* reference_image,
                          const float* base_window,
                          const int* row_starts, const int* col_starts,
                          int num_row_starts, int num_col_starts,
                          int tile_h, int tile_w,
                          int h, int w, int channels,
                          float motion_threshold, float scale,
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
                                       motion_threshold, motion_threshold, 
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
