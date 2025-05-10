#include "tile_noise_estimation.hpp"
#include <opencv2/imgproc.hpp>
#include <vector>
#include <numeric>   
#include <algorithm> 
#include <cmath>     

namespace NoiseEstimation {
namespace Internal { 
    
static float calculate_mad_from_mat_32f(const cv::Mat &data_mat_32f) {
    CV_Assert(data_mat_32f.type() == CV_32FC1);
    if (data_mat_32f.empty()) return 0.0f;

    std::vector<float> data_vec;
    data_vec.reserve(data_mat_32f.total());
    if (data_mat_32f.isContinuous()) {
        const float *ptr = data_mat_32f.ptr<float>(0);
        data_vec.assign(ptr, ptr + data_mat_32f.total());
    } else {
        for (int r_idx = 0; r_idx < data_mat_32f.rows; ++r_idx) {
            const float *ptr_row = data_mat_32f.ptr<float>(r_idx);
            data_vec.insert(data_vec.end(), ptr_row, ptr_row + data_mat_32f.cols);
        }
    }

    size_t n = data_vec.size();
    if (n <= 1) return 0.0f;

    std::vector<float> original_data_copy = data_vec;

    std::vector<float>::iterator median_it = data_vec.begin() + n / 2;
    std::nth_element(data_vec.begin(), median_it, data_vec.end());
    float median_val = *median_it;
    if (n > 0 && n % 2 == 0) { // Pastikan n > 0
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

    if (n_dev > 0 && n_dev % 2 == 0) { // Pastikan n_dev > 0
        std::vector<float>::iterator mad_it_prev = abs_deviations.begin() + (n_dev / 2 - 1);
        std::nth_element(abs_deviations.begin(), mad_it_prev, mad_it);
        mad_val = (mad_val + *mad_it_prev) / 2.0f;
    }
    return mad_val;
}

} // namespace Internal

float estimate_tile_noise_sigma_mad_laplacian(
    const cv::Mat &tile_gray_float,
    float mad_to_sigma_factor)
{
    if (tile_gray_float.empty() || tile_gray_float.channels() != 1 || tile_gray_float.type() != CV_32F) {
        return 0.0f;
    }
    if (tile_gray_float.rows < 3 || tile_gray_float.cols < 3) { // Laplacian ksize=1 (3x3 kernel)
        return 0.0f;
    }

    cv::Mat laplacian_output;
    try {
        cv::Laplacian(tile_gray_float, laplacian_output, CV_32F, 1, 1.0, 0.0, cv::BORDER_REPLICATE);
    } catch (const cv::Exception&) {
        return 0.0f; // Gagal hitung Laplacian
    }
    
    if (laplacian_output.empty()) return 0.0f;

    float mad_value = Internal::calculate_mad_from_mat_32f(laplacian_output);
    float estimated_sigma = mad_value * mad_to_sigma_factor;
    return std::max(0.0f, estimated_sigma); // Sigma tidak boleh negatif
}

}