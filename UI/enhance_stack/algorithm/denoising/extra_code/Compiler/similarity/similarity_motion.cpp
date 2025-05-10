#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp> // Untuk CV_Assert

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig {
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-5f;
    constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f;
    constexpr float ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR = 1.5f;
    constexpr int DEFAULT_SEARCH_RADIUS = 7; 
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
}

//=============================================================================
// Struktur Data Hasil
//=============================================================================


struct BlockMatchResult {
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    std::vector<float> all_mads; 
    int matches_found = 0;       
    bool success = false;     
};

//=============================================================================
// Fungsi Helper Dasar
//=============================================================================
inline float calculate_block_mad(const cv::Mat& block1, const cv::Mat& block2)
{
    CV_Assert(block1.size() == block2.size() && block1.type() == block2.type());
    CV_Assert(block1.type() == CV_32FC(block1.channels())); // Pastikan tipe float

    // Jika salah satu blok kosong (bisa terjadi di tepi jika tidak hati-hati)
    if (block1.empty() || block2.empty()) {
        return std::numeric_limits<float>::max(); // Kembalikan nilai tinggi sebagai indikasi error/tidak valid
    }

    cv::Mat diff;
    cv::absdiff(block1, block2, diff);

    cv::Scalar sad_per_channel = cv::sum(diff);
    double total_sad = 0.0;
    for (int i = 0; i < diff.channels(); ++i) {
        total_sad += sad_per_channel[i];
    }

    // Jumlah elemen total (piksel * channel)
    float num_elements = static_cast<float>(block1.total() * block1.channels());

    if (num_elements <= 0) {
        return 0.0f; 
    }

    return static_cast<float>(total_sad / num_elements);
}

float calculate_mad_stddev(const std::vector<float>& mad_values) {
    if (mad_values.size() <= 1) {
        return 0.0f;
    }

    cv::Mat mad_mat(mad_values.size(), 1, CV_32F, const_cast<float*>(mad_values.data()));

    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(mad_mat, mean_val, stddev_val);

    // Ambil nilai stddev dari channel pertama (karena input 1D)
    return static_cast<float>(stddev_val.val[0]);
}

float calculate_match_confidence(const BlockMatchResult& result, float motion_threshold)
{
    using namespace MotionMetricsConfig;

    float match_confidence = 0.0f;
    float quality_denominator = CONFIDENCE_SCALE_FACTOR * motion_threshold + STABILITY_EPSILON;

    if (!result.success || result.matches_found <= 0) {
        match_confidence = 0.0f;
    } else if (result.matches_found == 1) {
        if (quality_denominator > 0) {
            match_confidence = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
             match_confidence = (result.min_mad <= CONFIDENCE_EPSILON) ? 0.5f : 0.0f; // Batas atas 0.5
        }
        match_confidence = std::min(0.5f, std::max(0.0f, match_confidence));
    } else {
        
        float ratio = 1.0f;
        if (result.second_min_mad > CONFIDENCE_EPSILON) {
            float safe_min_mad = std::max(0.0f, result.min_mad); // Pastikan non-negatif
            ratio = safe_min_mad / result.second_min_mad;
        }
        float ratio_confidence = std::max(0.0f, 1.0f - ratio);

        float absolute_quality = 0.0f;
        if (quality_denominator > 0) {
            absolute_quality = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
            absolute_quality = (std::max(0.0f, result.min_mad) <= CONFIDENCE_EPSILON) ? 1.0f : 0.0f;
        }
        absolute_quality = std::max(0.0f, std::min(1.0f, absolute_quality));

        match_confidence = ratio_confidence * absolute_quality;
    }

    return std::max(0.0f, std::min(1.0f, match_confidence));
}

//=============================================================================
// Fungsi Pencarian Blok
//=============================================================================


BlockMatchResult find_best_block_match(
    const cv::Mat& current_block,
    const cv::Mat& reference_tile,
    int block_r_start, int block_c_start,
    int search_radius)
{
    BlockMatchResult result;

    int tile_h = reference_tile.rows;
    int tile_w = reference_tile.cols;
    int current_block_h = current_block.rows;
    int current_block_w = current_block.cols;

    int search_r_start = std::max(0, block_r_start - search_radius);
    int search_c_start = std::max(0, block_c_start - search_radius);
    int search_r_end = std::min(tile_h - current_block_h, block_r_start + search_radius);
    int search_c_end = std::min(tile_w - current_block_w, block_c_start + search_radius);

    int estimated_matches = (search_r_end - search_r_start + 1) * (search_c_end - search_c_start + 1);
    if (estimated_matches > 0) {
        result.all_mads.reserve(estimated_matches);
    }

    for (int search_r = search_r_start; search_r <= search_r_end; ++search_r) {
        for (int search_c = search_c_start; search_c <= search_c_end; ++search_c) {
            if (search_r < 0 || search_c < 0 ||
                search_r + current_block_h > tile_h ||
                search_c + current_block_w > tile_w) {
                continue;
            }

            cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
            const cv::Mat ref_block = reference_tile(ref_block_roi);

            float current_mad = calculate_block_mad(current_block, ref_block);

            result.all_mads.push_back(current_mad);
            result.matches_found++;
            result.success = true; // Setidaknya satu perbandingan berhasil

            if (current_mad < result.min_mad) {
                result.second_min_mad = result.min_mad; // Geser min lama ke second min
                result.min_mad = current_mad;        // Simpan min baru
            } else if (current_mad < result.second_min_mad) {
                result.second_min_mad = current_mad; // Update second min
            }
        }
    }
    return result;
}


//=============================================================================
// Fungsi Perhitungan Metrik Gerak per Tile
//=============================================================================
extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, 
        float *weight_map_sum_ptr,  
        const float *current_image_ptr,
        const float *reference_image_ptr, 
        const float *base_window_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h, int w, int channels,
        float motion_threshold, 
        int mbm_block_h, int mbm_block_w, int mbm_search_radius)
    {
        using namespace MotionMetricsConfig;

        // --- Validasi & Setup Mat Header (Sama seperti sebelumnya) ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h <= 0 || w <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            mbm_block_h <= 0 || mbm_block_w <= 0) {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0) return;

        // Mat header untuk buffer AKUMULASI (target penambahan)
        cv::Mat final_image_sum_mat(h, w, mat_type, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h, w, CV_32FC1, weight_map_sum_ptr);
        // Mat header untuk input frame saat ini & referensi
        const cv::Mat current_image_mat(h, w, mat_type, const_cast<float*>(current_image_ptr));
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float*>(reference_image_ptr)); // Untuk confidence
        const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

        #pragma omp parallel
        {
            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w) continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    const cv::Mat current_tile = current_image_mat(tile_roi);
                    const cv::Mat reference_tile = reference_image_mat(tile_roi); // Untuk confidence

                    // Tahap 1: Hitung Confidence (Sama seperti sebelumnya)
                    int num_blocks_h = (mbm_block_h > 0) ? (tile_h + mbm_block_h - 1) / mbm_block_h : 0;
                    int num_blocks_w = (mbm_block_w > 0) ? (tile_w + mbm_block_w - 1) / mbm_block_w : 0;
                    int num_blocks_in_tile = num_blocks_h * num_blocks_w;
                    cv::Mat block_confidences = cv::Mat::zeros(num_blocks_h, num_blocks_w, CV_32FC1);
                    
                    if (num_blocks_in_tile > 0) {
                        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                                int block_local_r_start = bh_idx * mbm_block_h;
                                int block_local_c_start = bw_idx * mbm_block_w;
                                int current_block_h = std::min(mbm_block_h, tile_h - block_local_r_start);
                                int current_block_w = std::min(mbm_block_w, tile_w - block_local_c_start);

                                if (current_block_h <= 0 || current_block_w <= 0) continue;

                                cv::Rect current_block_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                const cv::Mat current_block = current_tile(current_block_roi);

                                BlockMatchResult block_result = find_best_block_match(
                                    current_block, reference_tile, // Bandingkan DENGAN referensi
                                    block_local_r_start, block_local_c_start,
                                    mbm_search_radius
                                );

                                if (!block_result.success) { // Fallback (sama seperti sebelumnya)
                                     if (block_local_r_start + current_block_h <= tile_h && block_local_c_start + current_block_w <= tile_w) {
                                         cv::Rect ref_block_orig_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                         const cv::Mat ref_block_orig = reference_tile(ref_block_orig_roi); // Bandingkan DENGAN referensi
                                         block_result.min_mad = calculate_block_mad(current_block, ref_block_orig);
                                         block_result.second_min_mad = block_result.min_mad;
                                         block_result.matches_found = 1;
                                         block_result.success = true;
                                     } else {
                                         block_result.success = false;
                                     }
                                }

                                float confidence = 0.0f;
                                if(block_result.success) {
                                    // Gunakan motion_threshold yang diterima fungsi ini
                                    confidence = calculate_match_confidence(block_result, motion_threshold);
                                }
                                block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                            }
                        }
                    } 

                    // Tahap 2: Akumulasi Piksel & Bobot (Sama seperti sebelumnya, TAPI targetnya beda)
                    if (num_blocks_in_tile > 0) {
                        for (int y = 0; y < tile_h; ++y) {
                            const float* current_tile_row = current_tile.ptr<float>(y);
                            const float* base_window_row = base_window_tile_mat.ptr<float>(y);
                            int gy = r + y;
                            // Pointer ke buffer AKUMULASI global
                            float* global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                            float* global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);

                            for (int x = 0; x < tile_w; ++x) {
                                int bh_idx = std::min(y / mbm_block_h, num_blocks_h - 1);
                                int bw_idx = std::min(x / mbm_block_w, num_blocks_w - 1);
                                float block_confidence = block_confidences.at<float>(bh_idx, bw_idx);
                                float base_win_val = base_window_row[x];
                                float pixel_weight = base_win_val * block_confidence;

                                if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    int gx = c + x;
                                    // Akumulasi Bobot (Atomic) - Target: weight_map_sum_mat
                                    #pragma omp atomic update
                                    global_weight_sum_row[gx] += pixel_weight;

                                    // Akumulasi Piksel Terbobot (Atomic) - Target: final_image_sum_mat
                                    float weighted_pixel_value;
                                    int current_pixel_idx_local = x * channels;
                                    int current_pixel_idx_global = gx * channels;
                                    for (int ch = 0; ch < channels; ++ch) {
                                        // Pixel * weight (input pixel sudah [0,1])
                                        weighted_pixel_value = current_tile_row[current_pixel_idx_local + ch] * pixel_weight;
                                        #pragma omp atomic update
                                        global_pixel_sum_row[current_pixel_idx_global + ch] += weighted_pixel_value;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        } 
    } 

    // Fungsi BARU: Normalisasi Setelah Semua Frame Diakumulasi
    void normalize_accumulated_image_jit(
        float *final_image_ptr,     
        const float *weight_map_sum_ptr,
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0) {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0) return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float*>(weight_map_sum_ptr));

        #pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            for (int gx = 0; gx < w; ++gx) {
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);

                // Dapatkan pointer ke baris di buffer sum piksel (yang akan dinormalisasi)
                float* final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx + ch] *= inv_total_weight;
                    }
                } else {
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx + ch] = 0.0f;
                    }
                }
            } 
        } 
    } 

}