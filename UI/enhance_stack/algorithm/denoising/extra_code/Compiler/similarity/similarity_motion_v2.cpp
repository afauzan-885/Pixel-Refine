#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig
{
    // Konstanta Dasar
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;

    // --- Konstanta untuk Pembobotan Gradien ---
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.5f; // Masih dipakai oleh find_best_block_match

    // Konstanta Adaptasi Noise
    constexpr float NOISE_ADAPTATION_FACTOR = 6.0f;
    constexpr float MIN_ADAPTIVE_THRESHOLD_MULTIPLIER = 1.0f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;

    // --- Konstanta untuk Penanganan Area Gelap dengan Fading ---
    constexpr float DARK_UPPER_THRESHOLD = 127.0f / 255.0f;
 
    constexpr float MAX_MIN_DARK_CONFIDENCE = 1e-3f;
    constexpr int DARKNESS_MAP_BLUR_KERNEL_SIZE = 1;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;
    constexpr int COARSE_ALIGNMENT_SEARCH_MARGIN = 10;

    // --- Konstanta untuk Merging Domain Frekuensi ---
    constexpr float FREQ_MERGE_WIENER_C_FACTOR = 1.85f; 
    constexpr bool  APPLY_FREQ_DOMAIN_MERGING = true;  
    constexpr float MBM_MAD_SENSITIVITY = 20.0f;
}
//=============================================================================
// Struktur Data Hasil
//=============================================================================
struct BlockMatchResult
{
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    std::vector<float> all_mads;
    int matches_found = 0;
    bool success = false;
    int best_match_r = -1;
    int best_match_c = -1;
};

//=============================================================================
// Fungsi Helper Dasar (Yang Masih Dipakai)
//=============================================================================
// calculate_block_mad, calculate_mad_stddev, calculate_gradient_weighted_mad,
// find_best_block_match, estimate_tile_noise_sigma_mad_laplacian, calculate_mad_from_mat
// (Fungsi calculate_match_confidence dan calculate_block_ssim bisa dihapus jika tidak dipakai lagi)

// (Definisi fungsi-fungsi helper yang masih dipakai diletakkan di sini)
inline float calculate_block_mad(const cv::Mat &block1_color, const cv::Mat &block2_color)
{
    CV_Assert(block1_color.size() == block2_color.size());

    if (block1_color.empty() || block2_color.empty())
    {
        return std::numeric_limits<float>::max();
    }

    cv::Mat block1_gray, block2_gray;
    if (block1_color.channels() > 1)
        cv::cvtColor(block1_color, block1_gray, cv::COLOR_BGR2GRAY);
    else
        block1_gray = block1_color;
    if (block2_color.channels() > 1)
        cv::cvtColor(block2_color, block2_gray, cv::COLOR_BGR2GRAY);
    else
        block2_gray = block2_color;

    if (block1_gray.type() != CV_32F)
        block1_gray.convertTo(block1_gray, CV_32F);
    if (block2_gray.type() != CV_32F)
        block2_gray.convertTo(block2_gray, CV_32F);

    if (block1_gray.empty() || block2_gray.empty())
    {
        return std::numeric_limits<float>::max();
    } 

    cv::Mat diff;
    cv::absdiff(block1_gray, block2_gray, diff); 

    cv::Scalar total_sad_scalar = cv::sum(diff);
    double total_sad = total_sad_scalar.val[0]; 

    float num_elements = static_cast<float>(block1_gray.total());

    if (num_elements <= 0)
    {
        return 0.0f;
    }
    return static_cast<float>(total_sad / num_elements);
}

inline float calculate_gradient_weighted_mad(
    const cv::Mat &block1_gray,    
    const cv::Mat &block2_gray,    
    const cv::Mat &grad_mag_block1, 
    float gradient_weight_factor)
{
    using namespace MotionMetricsConfig;
    CV_Assert(block1_gray.size() == block2_gray.size());
    CV_Assert(block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1);
    CV_Assert(grad_mag_block1.size() == block1_gray.size() && grad_mag_block1.type() == CV_32FC1);

    if (block1_gray.empty() || block2_gray.empty())
    { 
        return std::numeric_limits<float>::max();
    }

    double weighted_sad_sum = 0.0;
    double total_weight_sum = 0.0;

    for (int row = 0; row < block1_gray.rows; ++row)
    {
        const float *p1_row = block1_gray.ptr<float>(row);
        const float *p2_row = block2_gray.ptr<float>(row);
        const float *mag_row = grad_mag_block1.ptr<float>(row);

        for (int col = 0; col < block1_gray.cols; ++col)
        {
            float magnitude = mag_row[col];
            float weight = 1.0f + gradient_weight_factor * magnitude;
            total_weight_sum += weight;
            float diff = std::abs(p1_row[col] - p2_row[col]);
            weighted_sad_sum += diff * weight;
        }
    }
    double denominator = total_weight_sum + STABILITY_EPSILON;

    if (denominator <= STABILITY_EPSILON)
    {
        return calculate_block_mad(block1_gray, block2_gray);
    }
    return static_cast<float>(weighted_sad_sum / denominator);
}

BlockMatchResult find_best_block_match(
    const cv::Mat &current_block_gray,      
    const cv::Mat &reference_tile_for_mbm_gray, 
    int block_r_start_in_tile, int block_c_start_in_tile, 
    int search_radius)
{
    using namespace MotionMetricsConfig;
    BlockMatchResult result;

    int tile_h_ref = reference_tile_for_mbm_gray.rows; 
    int tile_w_ref = reference_tile_for_mbm_gray.cols;
    int current_block_h = current_block_gray.rows;
    int current_block_w = current_block_gray.cols;

    CV_Assert(current_block_gray.type() == CV_32FC1 && reference_tile_for_mbm_gray.type() == CV_32FC1);
    CV_Assert(tile_h_ref >= current_block_h && tile_w_ref >= current_block_w);

    cv::Mat grad_x, grad_y, grad_mag_current;
    if (!current_block_gray.empty() && current_block_gray.rows >= 3 && current_block_gray.cols >= 3)
    {
        cv::Scharr(current_block_gray, grad_x, CV_32F, 1, 0);
        cv::Scharr(current_block_gray, grad_y, CV_32F, 0, 1);
        cv::magnitude(grad_x, grad_y, grad_mag_current);
    }
    else
    {
        grad_mag_current = cv::Mat::zeros(current_block_gray.size(), CV_32FC1);
    }

    int search_r_start_abs = std::max(0, block_r_start_in_tile - search_radius);
    int search_c_start_abs = std::max(0, block_c_start_in_tile - search_radius);
    int search_r_end_abs = std::min(tile_h_ref - current_block_h, block_r_start_in_tile + search_radius);
    int search_c_end_abs = std::min(tile_w_ref - current_block_w, block_c_start_in_tile + search_radius);

    for (int search_r = search_r_start_abs; search_r <= search_r_end_abs; ++search_r)
    {
        for (int search_c = search_c_start_abs; search_c <= search_c_end_abs; ++search_c)
        {
            cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
            const cv::Mat ref_block_gray = reference_tile_for_mbm_gray(ref_block_roi);

            float current_metric_score = calculate_gradient_weighted_mad(
                current_block_gray,
                ref_block_gray,
                grad_mag_current,
                GRADIENT_WEIGHT_FACTOR);
            // Tidak perlu menyimpan all_mads jika hanya untuk alignment
            // result.all_mads.push_back(current_metric_score); 
            result.matches_found++;
            
            if (current_metric_score < result.min_mad)
            {
                // second_min_mad tidak lagi terlalu penting jika hanya untuk alignment
                // result.second_min_mad = result.min_mad; 
                result.min_mad = current_metric_score;
                result.best_match_r = search_r; 
                result.best_match_c = search_c;
                result.success = true; // Set success di sini, saat match pertama ditemukan
            }
        }
    }
    return result;
}

float calculate_mad_from_mat(const cv::Mat &data_mat)
{
    CV_Assert(data_mat.type() == CV_32FC1);
    if (data_mat.empty()) return 0.0f;

    std::vector<float> data_vec;
    data_vec.reserve(data_mat.total());
    if (data_mat.isContinuous())
    {
        const float *ptr = data_mat.ptr<float>(0);
        data_vec.assign(ptr, ptr + data_mat.total());
    }
    else
    {
        for (int r_idx = 0; r_idx < data_mat.rows; ++r_idx)
        {
            const float *ptr_row = data_mat.ptr<float>(r_idx);
            data_vec.insert(data_vec.end(), ptr_row, ptr_row + data_mat.cols);
        }
    }

    size_t n = data_vec.size();
    if (n <= 1) return 0.0f;

    std::vector<float> original_data_copy = data_vec; 

    std::vector<float>::iterator median_it = data_vec.begin() + n / 2;
    std::nth_element(data_vec.begin(), median_it, data_vec.end());
    float median_val = *median_it;
    if (n % 2 == 0)
    {
        std::vector<float>::iterator median_it_prev = data_vec.begin() + (n / 2 - 1);
        std::nth_element(data_vec.begin(), median_it_prev, median_it); 
        median_val = (median_val + *median_it_prev) / 2.0f;
    }

    std::vector<float> abs_deviations;
    abs_deviations.reserve(n);
    for (float val : original_data_copy) { 
        abs_deviations.push_back(std::abs(val - median_val));
    }

    size_t n_dev = abs_deviations.size();
    if (n_dev == 0) return 0.0f;

    std::vector<float>::iterator mad_it = abs_deviations.begin() + n_dev / 2;
    std::nth_element(abs_deviations.begin(), mad_it, abs_deviations.end());
    float mad_val = *mad_it;

    if (n_dev % 2 == 0)
    {
        std::vector<float>::iterator mad_it_prev = abs_deviations.begin() + (n_dev / 2 - 1);
        std::nth_element(abs_deviations.begin(), mad_it_prev, mad_it);
        mad_val = (mad_val + *mad_it_prev) / 2.0f;
    }
    return mad_val;
}

float estimate_tile_noise_sigma_mad_laplacian(const cv::Mat &tile_gray_float)
{
    using namespace MotionMetricsConfig;
    if (tile_gray_float.empty() || tile_gray_float.channels() != 1 || tile_gray_float.type() != CV_32F)
    {
        return 0.0f;
    }
    if (tile_gray_float.rows < 3 || tile_gray_float.cols < 3)
    {
        return 0.0f;
    }

    cv::Mat laplacian_output;
    cv::Laplacian(tile_gray_float, laplacian_output, CV_32F, 1);
    float mad_value = calculate_mad_from_mat(laplacian_output);
    float estimated_sigma = mad_value * MAD_TO_SIGMA_FACTOR;
    return std::max(0.0f, estimated_sigma);
}


// Fungsi Akumulasi Tile (Tingkat Atas) - DIMODIFIKASI
extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, float *weight_map_sum_ptr,
        const float *current_image_ptr, const float *reference_image_ptr,
        const float *base_window_ptr, const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts, int tile_h, int tile_w,
        int h_img, int w_img, int channels_input,
        float motion_threshold, 
        int mbm_block_h, int mbm_block_w, int mbm_search_radius,
        float frame_max_adaptive_multiplier) 
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
            // cv::Mat thread_block_to_accumulate_gray; // Tidak lagi jadi satu variabel tunggal, diganti vector di bawah

            cv::Mat thread_current_padded, thread_ref_padded;
            cv::Mat thread_current_dft, thread_ref_dft, thread_merged_dft;

            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) { // Loop Tile i
                for (int j = 0; j < num_col_starts; j++) { // Loop Tile j
                    int r_tile_start = row_starts[i];
                    int c_tile_start = col_starts[j];

                    if (r_tile_start < 0 || c_tile_start < 0 || (r_tile_start + tile_h) > h_img || (c_tile_start + tile_w) > w_img || tile_h <= 0 || tile_w <= 0)
                        continue;

                    cv::Rect tile_roi_orig(c_tile_start, r_tile_start, tile_w, tile_h);
                    const cv::Mat current_tile_color = current_image_mat_input(tile_roi_orig);
                    const cv::Mat current_tile_gray_master = current_image_gray_mat(tile_roi_orig);
                    const cv::Mat reference_tile_gray_master_orig = reference_image_gray_mat(tile_roi_orig);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

                    cv::Mat reference_tile_gray_for_mbm = reference_tile_gray_master_orig.clone(); 
                    int aligned_ref_r_global = r_tile_start; 
                    int aligned_ref_c_global = c_tile_start;

                    if (!current_tile_gray_master.empty() && current_tile_gray_master.rows > 0 && current_tile_gray_master.cols > 0 && COARSE_ALIGNMENT_SEARCH_MARGIN >= 0) {
                        int search_margin = COARSE_ALIGNMENT_SEARCH_MARGIN;
                        int ref_search_r_start = std::max(0, r_tile_start - search_margin);
                        int ref_search_c_start = std::max(0, c_tile_start - search_margin);
                        int ref_search_h = std::min(h_img - ref_search_r_start, tile_h + 2 * search_margin);
                        int ref_search_w = std::min(w_img - ref_search_c_start, tile_w + 2 * search_margin);

                        if (ref_search_h >= tile_h && ref_search_w >= tile_w && ref_search_h > 0 && ref_search_w > 0) {
                            cv::Rect search_area_roi(ref_search_c_start, ref_search_r_start, ref_search_w, ref_search_h);
                            if (search_area_roi.x >= 0 && search_area_roi.y >= 0 && 
                                search_area_roi.x + search_area_roi.width <= reference_image_gray_mat.cols &&
                                search_area_roi.y + search_area_roi.height <= reference_image_gray_mat.rows) {
                                thread_reference_search_area = reference_image_gray_mat(search_area_roi);
                                if (!thread_reference_search_area.empty()) { 
                                    try {
                                        cv::Mat pc_src = current_tile_gray_master;
                                        cv::Mat pc_ref = thread_reference_search_area;
                                        if(pc_src.type() != CV_32F) pc_src.convertTo(pc_src, CV_32F);
                                        if(pc_ref.type() != CV_32F) pc_ref.convertTo(pc_ref, CV_32F);

                                        cv::Point2d shift = cv::phaseCorrelate(pc_ref, pc_src);
                                        aligned_ref_r_global = ref_search_r_start + static_cast<int>(std::round(shift.y));
                                        aligned_ref_c_global = ref_search_c_start + static_cast<int>(std::round(shift.x));
                                        
                                        if (aligned_ref_r_global >= 0 && aligned_ref_c_global >= 0 &&
                                            aligned_ref_r_global + tile_h <= h_img &&
                                            aligned_ref_c_global + tile_w <= w_img) {
                                            reference_tile_gray_for_mbm = reference_image_gray_mat(cv::Rect(aligned_ref_c_global, aligned_ref_r_global, tile_w, tile_h)).clone();
                                        } else { 
                                            aligned_ref_r_global = r_tile_start;
                                            aligned_ref_c_global = c_tile_start;
                                            reference_tile_gray_for_mbm = reference_tile_gray_master_orig.clone();
                                        }
                                    } catch (const cv::Exception& ) { 
                                        aligned_ref_r_global = r_tile_start;
                                        aligned_ref_c_global = c_tile_start;
                                        reference_tile_gray_for_mbm = reference_tile_gray_master_orig.clone();
                                    }
                                }
                            }
                        }
                    }
                    
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
                                estimated_noise_sigma = estimate_tile_noise_sigma_mad_laplacian(thread_larger_ref_tile_gray);
                            }
                        }
                    } else if (reference_tile_gray_for_mbm.rows >= 3 && reference_tile_gray_for_mbm.cols >= 3) {
                        if (!reference_tile_gray_for_mbm.empty()) {
                             estimated_noise_sigma = estimate_tile_noise_sigma_mad_laplacian(reference_tile_gray_for_mbm);
                        }
                    }
                    
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

                            cv::Mat current_block_merged_gray_output_temp; // Hasil DFT/original untuk blok ini

                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) {
                                thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                // Inisialisasi placeholder jika perlu
                                if(merged_gray_blocks_for_tile[block_idx_flat].empty() && actual_mbm_block_h > 0 && actual_mbm_block_w >0) {
                                     merged_gray_blocks_for_tile[block_idx_flat] = cv::Mat::zeros(1, 1, CV_32FC1);
                                }
                                continue;
                            }
                            // Inisialisasi output temp dengan ukuran yang benar
                            current_block_merged_gray_output_temp.create(current_block_h_dim, current_block_w_dim, CV_32FC1);

                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);

                            // --- Ambil blok saat ini (selalu diperlukan) ---
                             if (!(current_block_roi_local.x + current_block_roi_local.width <= current_tile_gray_master.cols &&
                                   current_block_roi_local.y + current_block_roi_local.height <= current_tile_gray_master.rows)) {
                                 thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                 // Jika ROI tidak valid, isi dengan data original (meskipun mungkin sebagian) atau nol
                                 try { current_tile_gray_master(current_block_roi_local).copyTo(merged_gray_blocks_for_tile[block_idx_flat]);} catch(...){ merged_gray_blocks_for_tile[block_idx_flat] = cv::Mat::zeros(current_block_h_dim, current_block_w_dim, CV_32FC1);}
                                 continue;
                             }
                             thread_current_block_gray = current_tile_gray_master(current_block_roi_local);
                             thread_current_block_gray.copyTo(current_block_merged_gray_output_temp); // Default: gunakan original

                             if (thread_current_block_gray.empty() || reference_tile_gray_for_mbm.empty()) {
                                  thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f;
                                  merged_gray_blocks_for_tile[block_idx_flat] = current_block_merged_gray_output_temp.clone();
                                  continue;
                             }

                            // --- Lakukan MBM ---
                            BlockMatchResult block_result = find_best_block_match(
                                thread_current_block_gray, reference_tile_gray_for_mbm,
                                block_local_r_start, block_local_c_start, mbm_search_radius);

                            // --- Hitung Kepercayaan MBM Dinamis ---
                            float mbm_confidence_score = 0.0f;
                            if (block_result.success) {
                                // Fungsi eksponensial: confidence = exp(-mad * sensitivitas)
                                mbm_confidence_score = std::exp(-block_result.min_mad * MBM_MAD_SENSITIVITY);
                                // Pastikan clamped antara 0 dan 1
                                mbm_confidence_score = std::max(0.0f, std::min(1.0f, mbm_confidence_score));
                            }
                            // Jika block_result.success == false, mbm_confidence_score tetap 0.

                            // --- Lakukan DFT Merge jika Diperlukan dan MBM Menemukan Sesuatu ---
                            float freq_merge_confidence_dft = 0.0f;
                            if (APPLY_FREQ_DOMAIN_MERGING && block_result.success) { // Kita tetap lakukan DFT jika MBM success, tapi confidence akhirnya dimodulasi
                                cv::Rect best_ref_block_roi(block_result.best_match_c, block_result.best_match_r, current_block_w_dim, current_block_h_dim);
                                if (best_ref_block_roi.x >= 0 && best_ref_block_roi.y >= 0 &&
                                    best_ref_block_roi.x + best_ref_block_roi.width <= reference_tile_gray_for_mbm.cols &&
                                    best_ref_block_roi.y + best_ref_block_roi.height <= reference_tile_gray_for_mbm.rows)
                                {
                                    thread_ref_block_from_mbm_gray = reference_tile_gray_for_mbm(best_ref_block_roi);
                                    if (!thread_ref_block_from_mbm_gray.empty()) {
                                        // ... (Proses DFT, Wiener Filter, IDFT seperti sebelumnya) ...
                                        int optimal_rows = cv::getOptimalDFTSize(current_block_h_dim);
                                        int optimal_cols = cv::getOptimalDFTSize(current_block_w_dim);
                                        cv::copyMakeBorder(thread_current_block_gray, thread_current_padded, 0, optimal_rows - current_block_h_dim, 0, optimal_cols - current_block_w_dim, cv::BORDER_CONSTANT, cv::Scalar::all(0));
                                        cv::copyMakeBorder(thread_ref_block_from_mbm_gray, thread_ref_padded, 0, optimal_rows - current_block_h_dim, 0, optimal_cols - current_block_w_dim, cv::BORDER_CONSTANT, cv::Scalar::all(0));
                                        cv::dft(thread_current_padded, thread_current_dft, cv::DFT_COMPLEX_OUTPUT);
                                        cv::dft(thread_ref_padded, thread_ref_dft, cv::DFT_COMPLEX_OUTPUT);
                                        float sigma_sq_spatial_block = estimated_noise_sigma * estimated_noise_sigma;
                                        float sigma_sq_dft_eff_block = sigma_sq_spatial_block * static_cast<float>(optimal_rows * optimal_cols);
                                        if (sigma_sq_dft_eff_block < STABILITY_EPSILON) sigma_sq_dft_eff_block = STABILITY_EPSILON;
                                        thread_merged_dft.create(thread_current_dft.size(), thread_current_dft.type());
                                        float sum_freq_weights = 0.0f; int count_freq_weights = 0;
                                        for (int r_f = 0; r_f < thread_current_dft.rows; ++r_f) {
                                            for (int c_f = 0; c_f < thread_current_dft.cols; ++c_f) {
                                                const cv::Vec2f& coeff_curr = thread_current_dft.at<cv::Vec2f>(r_f, c_f);
                                                const cv::Vec2f& coeff_ref = thread_ref_dft.at<cv::Vec2f>(r_f, c_f);
                                                cv::Vec2f diff_coeff = coeff_ref - coeff_curr;
                                                float mag_sq_diff = diff_coeff[0]*diff_coeff[0] + diff_coeff[1]*diff_coeff[1];
                                                float noise_floor_freq = FREQ_MERGE_WIENER_C_FACTOR * sigma_sq_dft_eff_block;
                                                float weight_curr_freq = noise_floor_freq / (mag_sq_diff + noise_floor_freq + STABILITY_EPSILON);
                                                weight_curr_freq = std::max(0.0f, std::min(1.0f, weight_curr_freq));
                                                thread_merged_dft.at<cv::Vec2f>(r_f, c_f) = coeff_ref * (1.0f - weight_curr_freq) + coeff_curr * weight_curr_freq;
                                                sum_freq_weights += weight_curr_freq; count_freq_weights++;
                                            }
                                        }
                                        if (count_freq_weights > 0) freq_merge_confidence_dft = sum_freq_weights / count_freq_weights;
                                        // ... (IDFT) ...
                                        cv::Mat temp_spatial;
                                        cv::idft(thread_merged_dft, temp_spatial, cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);
                                        current_block_merged_gray_output_temp = temp_spatial(cv::Rect(0, 0, current_block_w_dim, current_block_h_dim)).clone(); // Update dengan hasil DFT
                                    } else {
                                         freq_merge_confidence_dft = 0.0f; // Ref block kosong
                                    }
                                } else {
                                    freq_merge_confidence_dft = 0.0f; // ROI ref tidak valid
                                }
                            } else if (!APPLY_FREQ_DOMAIN_MERGING && block_result.success) {
                                // Kasus hanya alignment MBM tanpa DFT
                                freq_merge_confidence_dft = 1.0f; // Anggap confidence penuh pada data original
                                // current_block_merged_gray_output_temp sudah berisi original
                            }
                            // Jika MBM gagal (!block_result.success), freq_merge_confidence_dft tetap 0

                            // --- Gabungkan Kepercayaan & Simpan Hasil Blok ---
                            merged_gray_blocks_for_tile[block_idx_flat] = current_block_merged_gray_output_temp.clone(); // Simpan hasil (merge atau original)

                            // Kepercayaan gabungan: dimodulasi oleh keandalan MBM
                            float combined_confidence = mbm_confidence_score * freq_merge_confidence_dft;
                            // Jika MBM reliable tapi DFT tidak aktif, gunakan confidence MBM
                            if (mbm_confidence_score > CONFIDENCE_EPSILON && !APPLY_FREQ_DOMAIN_MERGING) {
                                combined_confidence = mbm_confidence_score;
                            }


                            // --- Hitung Final Raw Confidence (Termasuk Darkness) ---
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
                                            // Harusnya tidak terjadi jika inisialisasi merged_gray_blocks_for_tile benar
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

                                                // Ini adalah bagian kode original Anda TANPA clipping dan TANPA blending per piksel
                                                // (Blending sudah implisit dalam pixel_weight yang menggunakan block_confidence)
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

    float estimate_global_noise(
        const float *reference_image_ptr,
        int h, int w, int channels,
        int tile_h, int tile_w,
        const int *row_starts, int num_row_starts,
        const int *col_starts, int num_col_starts)
    {
        using namespace MotionMetricsConfig;

        // --- Validasi Input Dasar ---
        if (!reference_image_ptr || !row_starts || !col_starts || h <= 0 || w <= 0 ||
            channels <= 0 || tile_h <= 0 || tile_w <= 0 || num_row_starts <= 0 || num_col_starts <= 0)
        {
            return 0.0f; // Kembalikan 0 jika input tidak valid
        }

        int mat_type = CV_32FC(channels);
        if (mat_type == 0)
        {
            return 0.0f;
        } // Tipe tidak valid

        // --- Buat Mat Header untuk Input ---
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float *>(reference_image_ptr));
        cv::Mat ref_gray_float;

        // --- Konversi ke Grayscale Float ---
        if (reference_image_mat.channels() > 1)
        {
            cv::cvtColor(reference_image_mat, ref_gray_float, cv::COLOR_BGR2GRAY); // Asumsi BGR jika > 1
            if (ref_gray_float.type() != CV_32F)
            { // Pastikan float setelah cvtColor
                ref_gray_float.convertTo(ref_gray_float, CV_32F);
            }
        }
        else
        {
            // Jika sudah 1 channel, pastikan tipenya float
            if (reference_image_mat.type() != CV_32F)
            {
                reference_image_mat.convertTo(ref_gray_float, CV_32F);
            }
            else
            {
                // Tidak perlu copy jika tipe sudah benar
                ref_gray_float = reference_image_mat;
            }
        }

        if (ref_gray_float.empty())
        {
            return 0.0f;
        }

        // --- Variabel untuk Akumulasi Sigma ---
        double total_sigma_sum = 0.0;
        long long valid_tile_count = 0; // Gunakan long long untuk jumlah tile yang besar

// --- Paralelisasi Loop Tile ---
#pragma omp parallel
        {
            // Buffer per thread untuk menghindari race condition pada Mat temporary
            cv::Mat thread_tile;
            cv::Mat thread_laplacian_output;
            double thread_local_sigma_sum = 0.0;
            long long thread_local_valid_count = 0;

#pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    // Boundary check dasar untuk ROI
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w)
                        continue;

                    // --- Ekstrak Tile ROI ---
                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    // Ambil ROI dari gambar grayscale (tidak perlu copy jika hanya dibaca)
                    thread_tile = ref_gray_float(tile_roi);

                    // Cek ukuran minimum untuk Laplacian
                    if (thread_tile.rows < 3 || thread_tile.cols < 3)
                    {
                        continue;
                    }

                    // --- Hitung Laplacian (output ke buffer thread) ---
                    cv::Laplacian(thread_tile, thread_laplacian_output, CV_32F, 1);

                    // --- Hitung MAD (menggunakan fungsi yang sudah ada) ---
                    float mad_value = calculate_mad_from_mat(thread_laplacian_output);

                    // --- Konversi ke Sigma ---
                    float estimated_sigma = mad_value * MAD_TO_SIGMA_FACTOR;

                    // Akumulasi hasil thread lokal
                    thread_local_sigma_sum += static_cast<double>(std::max(0.0f, estimated_sigma)); // Pastikan non-negatif
                    thread_local_valid_count++;

                } // end loop j
            } // end loop i

// --- Reduksi hasil dari setiap thread (Aman untuk dilakukan setelah loop parallel for) ---
#pragma omp critical
            {
                total_sigma_sum += thread_local_sigma_sum;
                valid_tile_count += thread_local_valid_count;
            }

        } // End parallel region

        // --- Hitung Rata-rata Global ---
        if (valid_tile_count > 0)
        {
            return static_cast<float>(total_sigma_sum / valid_tile_count);
        }
        else
        {
            return 0.0f; // Kembalikan 0 jika tidak ada tile valid yang diproses
        }
    }

    // Fungsi Normalisasi (Tidak Berubah)
    void normalize_accumulated_image_jit(
        float *final_image_ptr,
        const float *weight_map_sum_ptr,
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0)
        {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0)
            return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

#pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy)
        {
            for (int gx = 0; gx < w; ++gx)
            {
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);
                float *final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row[pixel_idx + ch] *= inv_total_weight;
                    }
                }
                else
                {
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row[pixel_idx + ch] = 0.0f;
                    }
                }
            } 
        }
    } 
}