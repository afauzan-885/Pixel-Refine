#include "tile_noise_estimation.hpp"
#include <opencv2/imgproc.hpp>
#include <vector>
#include <algorithm>
#include <cmath>

namespace NoiseEstimation {
namespace Internal {

static float calculate_median(std::vector<float>& vec) {
    size_t n = vec.size();
    if (n == 0) return 0.0f;
    std::nth_element(vec.begin(), vec.begin() + n / 2, vec.end());
    float median = vec[n / 2];
    if (n % 2 == 0) {
        std::nth_element(vec.begin(), vec.begin() + n / 2 - 1, vec.end());
        median = (median + vec[n / 2 - 1]) / 2.0f;
    }
    return median;
}

static float calculate_mad_from_mat_32f(const cv::Mat &data_mat_32f, int tile_size = 16) {
    CV_Assert(data_mat_32f.type() == CV_32FC1);

    int rows = data_mat_32f.rows;
    int cols = data_mat_32f.cols;

    std::vector<float> local_mads;

    for (int y = 0; y < rows; y += tile_size) {
        for (int x = 0; x < cols; x += tile_size) {
            int w = std::min(tile_size, cols - x);
            int h = std::min(tile_size, rows - y);
            cv::Mat tile = data_mat_32f(cv::Rect(x, y, w, h)).clone();

            std::vector<float> values;
            values.reserve(tile.total());

            for (int i = 0; i < tile.rows; ++i) {
                const float* row = tile.ptr<float>(i);
                for (int j = 0; j < tile.cols; ++j)
                    values.push_back(row[j]);
            }

            if (values.size() < 2) continue;

            float median = calculate_median(values);

            std::vector<float> abs_dev;
            abs_dev.reserve(values.size());
            for (float v : values)
                abs_dev.push_back(std::abs(v - median));

            float mad = calculate_median(abs_dev);
            local_mads.push_back(mad);
        }
    }

    return calculate_median(local_mads);
}

} // namespace Internal

float estimate_tile_noise_sigma_mad_laplacian(
    const cv::Mat &tile_gray_float,
    float mad_to_sigma_factor)
{
    if (tile_gray_float.empty() || tile_gray_float.channels() != 1 || tile_gray_float.type() != CV_32F)
        return 0.0f;
    if (tile_gray_float.rows < 5 || tile_gray_float.cols < 5)
        return 0.0f;

    cv::Mat laplacian_output;
    try {
        cv::Laplacian(tile_gray_float, laplacian_output, CV_32F, 3, 1.0, 0.0, cv::BORDER_REFLECT101);
    } catch (const cv::Exception&) {
        return 0.0f;
    }

    if (laplacian_output.empty()) return 0.0f;

    float mad_value = Internal::calculate_mad_from_mat_32f(laplacian_output, 16);
    float estimated_sigma = mad_value * mad_to_sigma_factor;
    return std::max(0.0f, estimated_sigma);
}

} // namespace NoiseEstimation
