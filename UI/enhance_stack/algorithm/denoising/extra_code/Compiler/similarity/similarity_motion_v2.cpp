#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>
#include "align_phase_correlation.hpp"
#include "frequency_merging.hpp"
#include "tile_noise_estimation.hpp"
#include "block_matching.hpp"

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig
{
    // Konstanta Dasar
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    // constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f; // Tampaknya tidak digunakan
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;

    // --- Konstanta untuk Pembobotan Gradien ---
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;

    // Konstanta Adaptasi Noise
    // constexpr float NOISE_ADAPTATION_FACTOR = 6.0f; // Tampaknya tidak digunakan
    // constexpr float MIN_ADAPTIVE_THRESHOLD_MULTIPLIER = 1.0f; // Tampaknya tidak digunakan
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;

    // --- Konstanta untuk Penanganan Area Gelap dengan Fading ---
    constexpr float DARK_UPPER_THRESHOLD = 127.0f / 255.0f;
    constexpr float MAX_MIN_DARK_CONFIDENCE = 1e-3f;
    constexpr int DARKNESS_MAP_BLUR_KERNEL_SIZE = 1;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;

    // --- Konstanta untuk Merging Domain Frekuensi ---
    constexpr bool  APPLY_FREQ_DOMAIN_MERGING = true;
}

// Fungsi Akumulasi Tile (Tingkat Atas)
extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, float *weight_map_sum_ptr,
        const float *current_image_ptr, const float *reference_image_ptr,
        const float *base_window_ptr, const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts, int tile_h, int tile_w,
        int h_img, int w_img, int channels_input,
        int mbm_block_h, int mbm_block_w, int mbm_search_radius,
        float frame_max_adaptive_multiplier,
        float p_mbm_mad_sensitivity,
        float p_mbm_noise_mad_offset_factor,
        float p_mbm_confidence_skip_dft_threshold,
        int p_coarse_alignment_search_margin,
        float p_freq_merge_wiener_c_factor
        )
    {
        using namespace MotionMetricsConfig;

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels_input <= 0 ||
            (mbm_block_h <=0 && tile_h > 0) || (mbm_block_w <=0 && tile_w > 0) ) {
            return;
        }

        int channels_cpp = channels_input;
        int mat_type_color = CV_32FC(channels_cpp);
        if (mat_type_color == 0 && channels_cpp > 0) return;

        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat_input(h_img, w_img, CV_32FC(channels_input), const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat_input(h_img, w_img, CV_32FC(channels_input), const_cast<float *>(reference_image_ptr));

        // ... (konversi ke gray tetap sama) ...
        cv::Mat current_image_gray_mat;
        cv::Mat reference_image_gray_mat;

        if (current_image_mat_input.channels() > 1) {
            cv::cvtColor(current_image_mat_input, current_image_gray_mat, cv::COLOR_BGR2GRAY);
        } else {
            current_image_mat_input.copyTo(current_image_gray_mat);
        }
        if (current_image_gray_mat.type() != CV_32F) {
            current_image_gray_mat.convertTo(current_image_gray_mat, CV_32F);
        }

        if (reference_image_mat_input.channels() > 1) {
            cv::cvtColor(reference_image_mat_input, reference_image_gray_mat, cv::COLOR_BGR2GRAY);
        } else {
            reference_image_mat_input.copyTo(reference_image_gray_mat);
        }
        if (reference_image_gray_mat.type() != CV_32F) {
            reference_image_gray_mat.convertTo(reference_image_gray_mat, CV_32F);
        }
        if (current_image_gray_mat.empty() || reference_image_gray_mat.empty()) return;


#pragma omp parallel
        {
        
            cv::Mat thread_darkness_map_raw, thread_darkness_map_smoothed;
            cv::Mat thread_block_confidences_raw, thread_block_confidences_smoothed;
            cv::Mat thread_larger_ref_tile_gray, thread_reference_search_area;
            
            cv::Mat thread_current_block_gray;
            cv::Mat thread_ref_block_from_mbm_gray; 
            cv::Mat thread_current_block_gray_for_darkness;

            cv::Mat thread_current_padded, thread_ref_padded;
            cv::Mat thread_current_dft, thread_ref_dft, thread_merged_dft;


            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) { 
                for (int j = 0; j < num_col_starts; j++) { 
                    int r_tile_start = row_starts[i];
                    int c_tile_start = col_starts[j];

                    if (r_tile_start < 0 || c_tile_start < 0 || (r_tile_start + tile_h) > h_img || (c_tile_start + tile_w) > w_img || tile_h <= 0 || tile_w <= 0)
                        continue;

                    cv::Rect tile_roi_orig(c_tile_start, r_tile_start, tile_w, tile_h);
                    const cv::Mat current_tile_color = current_image_mat_input(tile_roi_orig);
                    const cv::Mat current_tile_gray_master = current_image_gray_mat(tile_roi_orig);
                    const cv::Mat reference_tile_gray_master_orig = reference_image_gray_mat(tile_roi_orig);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

                    cv::Mat reference_tile_gray_for_mbm; // Akan diisi
                    int aligned_ref_r_global = r_tile_start; 
                    int aligned_ref_c_global = c_tile_start;

                    // --- Kontrol untuk menonaktifkan alignment ---
                    bool perform_coarse_alignment = false; // Ganti ke 'false' untuk menonaktifkan
                                                          // Atau bisa dijadikan parameter fungsi/konfigurasi
                                                          // jika ingin dikontrol dari luar.

                    if (perform_coarse_alignment && !current_tile_gray_master.empty() && p_coarse_alignment_search_margin >= 0) {
                        MotionAlignment::CoarseAlignmentResult alignment_result =
                            MotionAlignment::align_tile_phase_correlation(
                                current_tile_gray_master,
                                reference_image_gray_mat,
                                r_tile_start, c_tile_start,
                                tile_h, tile_w,
                                h_img, w_img,
                                p_coarse_alignment_search_margin
                            );
                        
                        if (alignment_result.success && !alignment_result.aligned_reference_tile_gray.empty()) {
                            reference_tile_gray_for_mbm = alignment_result.aligned_reference_tile_gray;
                            aligned_ref_r_global = alignment_result.aligned_ref_r_global;
                            aligned_ref_c_global = alignment_result.aligned_ref_c_global;
                        } else {
                            // Fallback jika alignment gagal
                            if (alignment_result.aligned_reference_tile_gray.empty()){
                                try {
                                   reference_tile_gray_for_mbm = reference_image_gray_mat(cv::Rect(c_tile_start, r_tile_start, tile_w, tile_h)).clone();
                                } catch(const cv::Exception&) {
                                    reference_tile_gray_for_mbm = cv::Mat();
                                }
                            } else {
                                reference_tile_gray_for_mbm = alignment_result.aligned_reference_tile_gray;
                            }
                            // Jika fallback pun gagal atau alignment tidak sukses, reset posisi
                            if (reference_tile_gray_for_mbm.empty() || !alignment_result.success) {
                                aligned_ref_r_global = r_tile_start;
                                aligned_ref_c_global = c_tile_start;
                                // Pastikan reference_tile_gray_for_mbm diisi dengan tile original jika kosong
                                if (reference_tile_gray_for_mbm.empty()) {
                                     try {
                                        reference_tile_gray_for_mbm = reference_image_gray_mat(cv::Rect(c_tile_start, r_tile_start, tile_w, tile_h)).clone();
                                     } catch(const cv::Exception&) { /* biarkan kosong jika ini juga gagal */ }
                                }
                            }
                        }
                    } else { 
                        // Alignment dinonaktifkan atau tidak memenuhi syarat, gunakan tile referensi original
                        try {
                            reference_tile_gray_for_mbm = reference_image_gray_mat(cv::Rect(c_tile_start, r_tile_start, tile_w, tile_h)).clone();
                        } catch (const cv::Exception&) {
                            reference_tile_gray_for_mbm = cv::Mat();
                        }
                        // Posisi global tetap r_tile_start, c_tile_start
                        aligned_ref_r_global = r_tile_start;
                        aligned_ref_c_global = c_tile_start;
                    }

                    if (reference_tile_gray_for_mbm.empty()) {
                        // Jika setelah semua usaha tile referensi masih kosong, kita tidak bisa melanjutkan untuk tile ini
                        // Mungkin set block_confidences ke nol dan lanjutkan ke akumulasi, atau skip tile.
                        // Untuk amannya, skip tile jika tidak ada referensi.
                        continue;
                    }
                    // ... (estimasi noise sigma tetap sama) ...
                    float estimated_noise_sigma = 0.0f;
                    int larger_tile_factor = 2;
                    int noise_est_base_r = aligned_ref_r_global; 
                    int noise_est_base_c = aligned_ref_c_global;
                    int larger_r = std::max(0, noise_est_base_r - tile_h * (larger_tile_factor - 1) / 2);
                    int larger_c = std::max(0, noise_est_base_c - tile_w * (larger_tile_factor - 1) / 2);
                    int larger_h_dim_noise = std::min(h_img - larger_r, tile_h * larger_tile_factor);
                    int larger_w_dim_noise = std::min(w_img - larger_c, tile_w * larger_tile_factor);

                    if (larger_h_dim_noise >= 3 && larger_w_dim_noise >= 3) {
                        cv::Rect larger_roi_noise(larger_c, larger_r, larger_w_dim_noise, larger_h_dim_noise);
                         if (larger_roi_noise.x >=0 && larger_roi_noise.y >=0 && 
                             larger_roi_noise.x + larger_roi_noise.width <= reference_image_gray_mat.cols &&
                             larger_roi_noise.y + larger_roi_noise.height <= reference_image_gray_mat.rows) {
                            thread_larger_ref_tile_gray = reference_image_gray_mat(larger_roi_noise);
                            if (!thread_larger_ref_tile_gray.empty()) {
                                estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian( // <--- PERBAIKAN
                                                        thread_larger_ref_tile_gray,
                                                        MAD_TO_SIGMA_FACTOR // Menggunakan konstanta dari MotionMetricsConfig
                                                    );
                            }
                        }
                    } else if (reference_tile_gray_for_mbm.rows >= 3 && reference_tile_gray_for_mbm.cols >= 3) {
                        if (!reference_tile_gray_for_mbm.empty()) {
                             NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian( // <--- PERBAIKAN
                                                        reference_tile_gray_for_mbm,
                                                        MAD_TO_SIGMA_FACTOR // Menggunakan konstanta dari MotionMetricsConfig
                                                    );
                        }
                    }

                    // ... (darkness map tetap sama) ...
                    int num_blocks_h = (mbm_block_h > 0 && tile_h > 0) ? (tile_h + mbm_block_h - 1) / mbm_block_h : (tile_h > 0 ? 1 : 0);
                    int num_blocks_w = (mbm_block_w > 0 && tile_w > 0) ? (tile_w + mbm_block_w - 1) / mbm_block_w : (tile_w > 0 ? 1 : 0);
                    if (num_blocks_h == 0 || num_blocks_w == 0) continue;
                    int actual_mbm_block_h = (mbm_block_h > 0) ? mbm_block_h : tile_h;
                    int actual_mbm_block_w = (mbm_block_w > 0) ? mbm_block_w : tile_w;

                    thread_darkness_map_raw.create(num_blocks_h, num_blocks_w, CV_32F);
                    thread_darkness_map_raw.setTo(cv::Scalar(0.0f));
                     for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                            int block_local_r_start = bh_idx * actual_mbm_block_h;
                            int block_local_c_start = bw_idx * actual_mbm_block_w;
                            int current_block_h_dim = std::min(actual_mbm_block_h, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_mbm_block_w, tile_w - block_local_c_start);
                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) continue;
                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            if (current_block_roi_local.x + current_block_roi_local.width <= current_tile_gray_master.cols &&
                                current_block_roi_local.y + current_block_roi_local.height <= current_tile_gray_master.rows) {
                                thread_current_block_gray_for_darkness = current_tile_gray_master(current_block_roi_local);
                                if (!thread_current_block_gray_for_darkness.empty()) {
                                    float avg_intensity = static_cast<float>(cv::mean(thread_current_block_gray_for_darkness)[0]);
                                    float darkness_factor = 0.0f;
                                    if (avg_intensity < DARK_UPPER_THRESHOLD) {
                                        float norm_intens = avg_intensity / DARK_UPPER_THRESHOLD;
                                        darkness_factor = 1.0f - norm_intens * norm_intens;
                                    }
                                    thread_darkness_map_raw.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, darkness_factor));
                                } else { thread_darkness_map_raw.at<float>(bh_idx, bw_idx) = 0.0f;}
                            } else { thread_darkness_map_raw.at<float>(bh_idx, bw_idx) = 0.0f; }
                        }
                    }
                    
                    int kernel_sz_dark = (DARKNESS_MAP_BLUR_KERNEL_SIZE >= 1 && DARKNESS_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? DARKNESS_MAP_BLUR_KERNEL_SIZE : 1;
                    if (!thread_darkness_map_raw.empty() && kernel_sz_dark >=3 && thread_darkness_map_raw.rows > 0 && thread_darkness_map_raw.cols > 0) {
                        cv::GaussianBlur(thread_darkness_map_raw, thread_darkness_map_smoothed, cv::Size(kernel_sz_dark, kernel_sz_dark), 0);
                    } else if (!thread_darkness_map_raw.empty()) {
                        thread_darkness_map_raw.copyTo(thread_darkness_map_smoothed);
                    } else {
                        thread_darkness_map_smoothed.create(num_blocks_h, num_blocks_w, CV_32F);
                        thread_darkness_map_smoothed.setTo(cv::Scalar(0.0f));
                    }


                    thread_block_confidences_raw.create(num_blocks_h, num_blocks_w, CV_32F);
                    thread_block_confidences_raw.setTo(cv::Scalar(0.0f));
                    bool darkness_map_is_usable = !thread_darkness_map_smoothed.empty() &&
                                              thread_darkness_map_smoothed.rows == num_blocks_h &&
                                              thread_darkness_map_smoothed.cols == num_blocks_w;
                    std::vector<cv::Mat> merged_gray_blocks_for_tile(num_blocks_h * num_blocks_w);

                    for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                            int block_idx_flat = bh_idx * num_blocks_w + bw_idx;
                            int block_local_r_start = bh_idx * actual_mbm_block_h;
                            int block_local_c_start = bw_idx * actual_mbm_block_w;
                            int current_block_h_dim = std::min(actual_mbm_block_h, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_mbm_block_w, tile_w - block_local_c_start);

                            cv::Mat current_block_merged_gray_output_temp; 
                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) {
                                thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                if(merged_gray_blocks_for_tile[block_idx_flat].empty() && actual_mbm_block_h > 0 && actual_mbm_block_w >0) {
                                     merged_gray_blocks_for_tile[block_idx_flat] = cv::Mat::zeros(1, 1, CV_32FC1);
                                }
                                continue;
                            }
                            current_block_merged_gray_output_temp.create(current_block_h_dim, current_block_w_dim, CV_32FC1);
                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                             if (!(current_block_roi_local.x + current_block_roi_local.width <= current_tile_gray_master.cols &&
                                   current_block_roi_local.y + current_block_roi_local.height <= current_tile_gray_master.rows)) {
                                 thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                 try { current_tile_gray_master(current_block_roi_local).copyTo(merged_gray_blocks_for_tile[block_idx_flat]);} catch(...){ merged_gray_blocks_for_tile[block_idx_flat] = cv::Mat::zeros(current_block_h_dim, current_block_w_dim, CV_32FC1);}
                                 continue;
                             }
                             thread_current_block_gray = current_tile_gray_master(current_block_roi_local);
                             thread_current_block_gray.copyTo(current_block_merged_gray_output_temp); 

                             if (thread_current_block_gray.empty() || reference_tile_gray_for_mbm.empty()) {
                                  thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                  merged_gray_blocks_for_tile[block_idx_flat] = current_block_merged_gray_output_temp.clone();
                                  continue;
                             }

                            MotionMatching::BlockMatchResult block_result =
                                MotionMatching::find_best_block_match_mad(
                                    thread_current_block_gray, reference_tile_gray_for_mbm,
                                    block_local_r_start, block_local_c_start, mbm_search_radius,
                                    GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON
                                );

                            float mbm_confidence_score = 0.0f;
                            if (block_result.success) {
                                float noise_induced_mad_offset = p_mbm_noise_mad_offset_factor * estimated_noise_sigma;
                                float excess_mad = std::max(0.0f, block_result.min_mad - noise_induced_mad_offset);
                                mbm_confidence_score = std::exp(-excess_mad * p_mbm_mad_sensitivity);
                                mbm_confidence_score = std::max(0.0f, std::min(1.0f, mbm_confidence_score));
                            }

                            float freq_merge_confidence_dft = 0.0f;
                            if (APPLY_FREQ_DOMAIN_MERGING && block_result.success && mbm_confidence_score >= p_mbm_confidence_skip_dft_threshold) {
                                cv::Rect best_ref_block_roi(block_result.best_match_c, block_result.best_match_r, current_block_w_dim, current_block_h_dim);
                                if (best_ref_block_roi.x >= 0 && best_ref_block_roi.y >= 0 &&
                                    best_ref_block_roi.x + best_ref_block_roi.width <= reference_tile_gray_for_mbm.cols &&
                                    best_ref_block_roi.y + best_ref_block_roi.height <= reference_tile_gray_for_mbm.rows)
                                {
                                    thread_ref_block_from_mbm_gray = reference_tile_gray_for_mbm(best_ref_block_roi);
                                    MotionMerging::FrequencyMergeResult merge_result =
                                        MotionMerging::merge_blocks_frequency_domain(
                                            thread_current_block_gray,
                                            thread_ref_block_from_mbm_gray,
                                            estimated_noise_sigma,
                                            p_freq_merge_wiener_c_factor,
                                            STABILITY_EPSILON
                                        );

                                    if (merge_result.success && !merge_result.merged_block_gray.empty()) {
                                        current_block_merged_gray_output_temp = merge_result.merged_block_gray;
                                        freq_merge_confidence_dft = merge_result.merge_confidence;
                                    } else {
                                        freq_merge_confidence_dft = 0.0f;
                                    }
                                } else {
                                    freq_merge_confidence_dft = 0.0f;
                                }
                            } else if (!APPLY_FREQ_DOMAIN_MERGING && block_result.success) {
                                freq_merge_confidence_dft = 1.0f;
                            } else {
                                freq_merge_confidence_dft = 0.0f;
                            }
                            
                            merged_gray_blocks_for_tile[block_idx_flat] = current_block_merged_gray_output_temp.clone();
                            float combined_confidence = mbm_confidence_score * freq_merge_confidence_dft;
                            if (mbm_confidence_score > CONFIDENCE_EPSILON && !APPLY_FREQ_DOMAIN_MERGING && block_result.success) {
                                combined_confidence = mbm_confidence_score;
                            }

                            float final_confidence = combined_confidence;
                            float smoothed_darkness_factor = 0.0f;
                            if (darkness_map_is_usable && bh_idx < thread_darkness_map_smoothed.rows && bw_idx < thread_darkness_map_smoothed.cols) {
                                smoothed_darkness_factor = thread_darkness_map_smoothed.at<float>(bh_idx, bw_idx);
                            }
                            final_confidence = std::max(final_confidence, smoothed_darkness_factor * MAX_MIN_DARK_CONFIDENCE);
                            thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = final_confidence;

                        }
                    } 

                    int kernel_sz_conf = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE >= 1 && CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : 1;
                    if (!thread_block_confidences_raw.empty() && kernel_sz_conf >=3 && thread_block_confidences_raw.rows > 0 && thread_block_confidences_raw.cols > 0) {
                        cv::GaussianBlur(thread_block_confidences_raw, thread_block_confidences_smoothed, cv::Size(kernel_sz_conf, kernel_sz_conf), 0);
                    } else if (!thread_block_confidences_raw.empty()) {
                        thread_block_confidences_raw.copyTo(thread_block_confidences_smoothed);
                    } else {
                        thread_block_confidences_smoothed.create(num_blocks_h, num_blocks_w, CV_32F);
                        thread_block_confidences_smoothed.setTo(cv::Scalar(0.0f));
                    }
                    
                    bool confidence_map_is_usable_for_pixels = !thread_block_confidences_smoothed.empty() &&
                                                               thread_block_confidences_smoothed.rows == num_blocks_h &&
                                                               thread_block_confidences_smoothed.cols == num_blocks_w;

                    if (confidence_map_is_usable_for_pixels && num_blocks_h > 0 && num_blocks_w > 0) {
                        for (int y_in_tile = 0; y_in_tile < tile_h; ++y_in_tile) {
                            const float *base_window_row = base_window_tile_mat.ptr<float>(y_in_tile);
                            int gy = r_tile_start + y_in_tile;
                            if (gy < 0 || gy >= h_img) continue;

                            for (int x_in_tile = 0; x_in_tile < tile_w; ++x_in_tile) {
                                int bh_idx_pixel = (actual_mbm_block_h > 0) ? std::min(y_in_tile / actual_mbm_block_h, num_blocks_h - 1) : 0;
                                int bw_idx_pixel = (actual_mbm_block_w > 0) ? std::min(x_in_tile / actual_mbm_block_w, num_blocks_w - 1) : 0;
                                bh_idx_pixel = std::max(0, std::min(bh_idx_pixel, num_blocks_h - 1));
                                bw_idx_pixel = std::max(0, std::min(bw_idx_pixel, num_blocks_w - 1));

                                float block_confidence_pixel = thread_block_confidences_smoothed.at<float>(bh_idx_pixel, bw_idx_pixel);
                                float base_win_val = base_window_row[x_in_tile];
                                float pixel_weight = base_win_val * block_confidence_pixel;

                                if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    int gx = c_tile_start + x_in_tile;
                                    if (gx >= 0 && gx < w_img) {
                                        #pragma omp atomic update
                                        weight_map_sum_mat.at<float>(gy, gx) += pixel_weight;

                                        int block_local_r_start_pixel = bh_idx_pixel * actual_mbm_block_h;
                                        int block_local_c_start_pixel = bw_idx_pixel * actual_mbm_block_w;
                                        int y_in_block_pixel = y_in_tile - block_local_r_start_pixel;
                                        int x_in_block_pixel = x_in_tile - block_local_c_start_pixel;
                                        
                                        int current_block_h_dim_for_pixel = std::min(actual_mbm_block_h, tile_h - block_local_r_start_pixel);
                                        int current_block_w_dim_for_pixel = std::min(actual_mbm_block_w, tile_w - block_local_c_start_pixel);

                                        cv::Rect current_block_roi_pixel(block_local_c_start_pixel, block_local_r_start_pixel, 
                                                                         current_block_w_dim_for_pixel, current_block_h_dim_for_pixel);
                                        
                                        int flat_block_index = bh_idx_pixel * num_blocks_w + bw_idx_pixel;
                                        if (flat_block_index >= merged_gray_blocks_for_tile.size() || merged_gray_blocks_for_tile[flat_block_index].empty()) {
                                            continue; 
                                        }
                                        const cv::Mat& active_merged_gray_block = merged_gray_blocks_for_tile[flat_block_index];
                                        
                                        if (y_in_block_pixel >= 0 && y_in_block_pixel < active_merged_gray_block.rows &&
                                            x_in_block_pixel >= 0 && x_in_block_pixel < active_merged_gray_block.cols &&
                                            current_block_roi_pixel.contains(cv::Point(x_in_tile, y_in_tile))) { 
                                            
                                            const cv::Mat current_block_color_orig_pixel = current_tile_color(current_block_roi_pixel);
                                            const cv::Mat current_block_gray_orig_pixel = current_tile_gray_master(current_block_roi_pixel);

                                            if (!current_block_color_orig_pixel.empty() && !current_block_gray_orig_pixel.empty() &&
                                                y_in_block_pixel < current_block_gray_orig_pixel.rows && x_in_block_pixel < current_block_gray_orig_pixel.cols &&
                                                y_in_block_pixel < current_block_color_orig_pixel.rows && x_in_block_pixel < current_block_color_orig_pixel.cols ) { 
                                                
                                                float gray_merged_val = active_merged_gray_block.at<float>(y_in_block_pixel, x_in_block_pixel);
                                                float gray_orig_val = current_block_gray_orig_pixel.at<float>(y_in_block_pixel, x_in_block_pixel);
                                                for (int ch = 0; ch < channels_cpp; ++ch) {
                                                    float color_val_orig = 0.0f;
                                                    if (channels_cpp == 1) { 
                                                        color_val_orig = current_block_color_orig_pixel.at<float>(y_in_block_pixel, x_in_block_pixel);
                                                    } else { 
                                                        color_val_orig = current_block_color_orig_pixel.ptr<float>(y_in_block_pixel)[x_in_block_pixel * channels_cpp + ch];
                                                    }

                                                    float ratio = (gray_orig_val > STABILITY_EPSILON) ? (gray_merged_val / gray_orig_val) : 1.0f;
                                                    float final_color_val = color_val_orig * ratio;
                                                    final_color_val = std::max(0.0f, std::min(1.0f, final_color_val)); 

                                                    float weighted_pixel_value = final_color_val * pixel_weight;
                                                    #pragma omp atomic update
                                                    final_image_sum_mat.ptr<float>(gy)[gx * channels_cpp + ch] += weighted_pixel_value;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                } 
            }
        } 
    }

    [[nodiscard]] float estimate_global_noise(
        const float *reference_image_ptr,
        int h, int w, int channels,
        int tile_h, int tile_w,
        const int *row_starts, int num_row_starts,
        const int *col_starts, int num_col_starts)
    {
        using namespace MotionMetricsConfig;

        if (!reference_image_ptr || !row_starts || !col_starts || h <= 0 || w <= 0 ||
            channels <= 0 || tile_h <= 0 || tile_w <= 0 || num_row_starts <= 0 || num_col_starts <= 0)
        {
            return 0.0f;
        }

        int mat_type = CV_32FC(channels);
        if (mat_type == 0 && channels > 0) return 0.0f;

        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float *>(reference_image_ptr));
        cv::Mat ref_gray_float;

        if (reference_image_mat.channels() > 1) {
            cv::cvtColor(reference_image_mat, ref_gray_float, cv::COLOR_BGR2GRAY);
        } else {
            reference_image_mat.copyTo(ref_gray_float);
        }
        if (ref_gray_float.type() != CV_32F) {
            ref_gray_float.convertTo(ref_gray_float, CV_32F);
        }

        if (ref_gray_float.empty()) {
            return 0.0f;
        }

        double total_sigma_sum = 0.0;
        long long valid_tile_count = 0;

        #pragma omp parallel
        {
            cv::Mat thread_tile;

            #pragma omp for collapse(2) schedule(static) reduction(+:total_sigma_sum, valid_tile_count)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w)
                        continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    thread_tile = ref_gray_float(tile_roi);

                    if (thread_tile.rows < 3 || thread_tile.cols < 3) {
                        continue;
                    }

                    float estimated_sigma_tile = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                                                    thread_tile,
                                                    MAD_TO_SIGMA_FACTOR
                                                );

                    if (estimated_sigma_tile > 0) {
                        total_sigma_sum += static_cast<double>(estimated_sigma_tile);
                        valid_tile_count++;
                    }
                }
            }
        }

        if (valid_tile_count > 0) {
            return static_cast<float>(total_sigma_sum / valid_tile_count);
        } else {
            return 0.0f;
        }
    }

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
        if (mat_type == 0 && channels > 0) return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

        #pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            for (int gx = 0; gx < w; ++gx) {
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);
                float *final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx_base = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx_base + ch] *= inv_total_weight;
                    }
                } else {
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx_base + ch] = 0.0f;
                    }
                }
            }
        }
    }
}