#include "image_accumulator.hpp"    // Header sendiri
#include "tile_processor.hpp"       // Perlu compute_tile_motion_metrics
#include "motion_metrics_config.hpp"// Perlu konstanta

#include <vector>                   // Jika dipakai di implementasi (tidak secara eksplisit di sini)
#include <omp.h>                    // Untuk OpenMP
#include <opencv2/core.hpp>         // Perlu cv::Mat, CV_32FC, cv::Rect, cv::Scalar
#include <opencv2/imgproc.hpp>      // Perlu cv::Mat::setTo (implisit via Scalar)

// Definisi fungsi accumulate_tiles_jit
// TIDAK perlu extern "C" di sini
void accumulate_tiles_jit(
    float *final_image_ptr, float *weight_map_ptr,
    const float *current_image_ptr, const float *reference_image_ptr,
    const float *base_window_ptr,
    const int *row_starts, const int *col_starts,
    int num_row_starts, int num_col_starts,
    int tile_h, int tile_w,
    int h, int w, int channels,
    float motion_threshold, float scale,
    int mbm_block_h, int mbm_block_w, int mbm_search_radius
) {
    using namespace MotionMetricsConfig;

    if (!final_image_ptr || !weight_map_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
        !row_starts || !col_starts || h <= 0 || w <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0) {
        return;
    }

    int mat_type = CV_32FC(channels);
    if (mat_type == 0) {
         return;
    }

    cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
    cv::Mat weight_map_mat(h, w, CV_32FC1, weight_map_ptr);
    const cv::Mat current_image_mat(h, w, mat_type, const_cast<float*>(current_image_ptr));
    const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float*>(reference_image_ptr));
    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

    #pragma omp parallel
    {
         cv::Mat local_final_image_buffer = cv::Mat::zeros(tile_h, tile_w, mat_type);
         cv::Mat local_weight_map_buffer = cv::Mat::zeros(tile_h, tile_w, CV_32FC1);

        #pragma omp for collapse(2) schedule(static) nowait
        for (int i = 0; i < num_row_starts; i++) {
            for (int j = 0; j < num_col_starts; j++) {
                int r = row_starts[i];
                int c = col_starts[j];

                if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w) {
                    continue;
                }

                cv::Rect tile_roi(c, r, tile_w, tile_h);
                const cv::Mat current_tile = current_image_mat(tile_roi);
                const cv::Mat reference_tile = reference_image_mat(tile_roi);

                float similarity_weight = 0.0f;
                float adaptive_threshold = motion_threshold;

                // Panggil fungsi dari tile_processor
                compute_tile_motion_metrics(
                    current_tile, reference_tile,
                    mbm_block_h, mbm_block_w,
                    mbm_search_radius,
                    motion_threshold,
                    &similarity_weight, &adaptive_threshold);

                local_final_image_buffer.setTo(cv::Scalar::all(0.0));
                local_weight_map_buffer.setTo(cv::Scalar::all(0.0));

                if (similarity_weight >= GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    for (int y = 0; y < tile_h; ++y) {
                        float* local_final_row = local_final_image_buffer.ptr<float>(y);
                        float* local_weight_row = local_weight_map_buffer.ptr<float>(y);
                        const float* current_tile_row = current_tile.ptr<float>(y);
                        const float* base_window_row = base_window_tile_mat.ptr<float>(y);

                        for (int x = 0; x < tile_w; ++x) {
                            float base_win_val = base_window_row[x];
                            float pixel_weight = base_win_val * similarity_weight;
                            local_weight_row[x] = pixel_weight;
                            float weighted_scale = pixel_weight * scale;
                            int pixel_col_idx = x * channels;
                            for (int ch = 0; ch < channels; ++ch) {
                                local_final_row[pixel_col_idx + ch] = current_tile_row[pixel_col_idx + ch] * weighted_scale;
                            }
                        }
                    }
                }

                #pragma omp critical
                {
                    cv::Mat final_image_global_roi = final_image_mat(tile_roi);
                    cv::Mat weight_map_global_roi = weight_map_mat(tile_roi);

                    for (int y = 0; y < tile_h; ++y) {
                        float* global_final_row = final_image_global_roi.ptr<float>(y);
                        float* global_weight_row = weight_map_global_roi.ptr<float>(y);
                        const float* local_final_row = local_final_image_buffer.ptr<float>(y);
                        const float* local_weight_row = local_weight_map_buffer.ptr<float>(y);

                        for (int x = 0; x < tile_w; ++x) {
                            float current_local_weight = local_weight_row[x];

                            if (current_local_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                float previous_global_weight = global_weight_row[x];
                                float new_total_weight = previous_global_weight + current_local_weight;
                                int pixel_col_idx = x * channels;

                                if (new_total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    for (int ch = 0; ch < channels; ++ch) {
                                        global_final_row[pixel_col_idx + ch] = (global_final_row[pixel_col_idx + ch] * previous_global_weight + local_final_row[pixel_col_idx + ch]) / new_total_weight;
                                    }
                                    global_weight_row[x] = new_total_weight;
                                } else {
                                    for (int ch = 0; ch < channels; ++ch) {
                                        global_final_row[pixel_col_idx + ch] = 0.0f;
                                    }
                                    global_weight_row[x] = 0.0f;
                                }
                            }
                        }
                    }
                } // end critical section
            } // End inner loop (j)
        } // End outer loop (i)
    } // End parallel region
}