#include "tile_noise_estimation.hpp"
#include <opencv2/imgproc.hpp>
#include <vector>
#include <algorithm>
#include <cmath>
#include <immintrin.h>

namespace NoiseEstimation
{
    namespace Internal
    {

        static float calculate_median(std::vector<float> &vec)
        {
            size_t n = vec.size();
            if (n == 0)
                return 0.0f;
            std::nth_element(vec.begin(), vec.begin() + n / 2, vec.end());
            float median = vec[n / 2];
            if (n % 2 == 0)
            {
                std::nth_element(vec.begin(), vec.begin() + n / 2 - 1, vec.end());
                median = (median + vec[n / 2 - 1]) / 2.0f;
            }
            return median;
        }

#if defined(__GNUC__) || defined(__clang__)
        __attribute__((target("avx2")))
#endif
        static float
        calculate_mad_from_mat_32f_avx2(const cv::Mat &data_mat_32f, int tile_size)
        {
            CV_Assert(data_mat_32f.type() == CV_32FC1);

            int rows = data_mat_32f.rows;
            int cols = data_mat_32f.cols;

            std::vector<float> local_mads;

            std::vector<float> values_buffer;
            std::vector<float> abs_dev_buffer;

            for (int y = 0; y < rows; y += tile_size)
            {
                for (int x = 0; x < cols; x += tile_size)
                {
                    int w = std::min(tile_size, cols - x);
                    int h = std::min(tile_size, rows - y);
                    cv::Mat tile = data_mat_32f(cv::Rect(x, y, w, h));

                    values_buffer.clear();
                    values_buffer.reserve(tile.total());
                    if (tile.isContinuous())
                    {
                        const float *p = tile.ptr<float>(0);
                        values_buffer.assign(p, p + tile.total());
                    }
                    else
                    {
                        for (int i = 0; i < h; ++i)
                        {
                            const float *p = tile.ptr<float>(i);
                            values_buffer.insert(values_buffer.end(), p, p + w);
                        }
                    }

                    if (values_buffer.size() < 2)
                        continue;

                    float median = calculate_median(values_buffer);

                    abs_dev_buffer.clear();
                    abs_dev_buffer.resize(values_buffer.size());

                    const int total_values = values_buffer.size();
                    const int avx_end = total_values - (total_values % 8);

                    const __m256 v_median = _mm256_set1_ps(median);
                    const __m256 v_sign_mask = _mm256_set1_ps(-0.0f);

                    const float *values_ptr = values_buffer.data();
                    float *abs_dev_ptr = abs_dev_buffer.data();

                    for (int i = 0; i < avx_end; i += 8)
                    {
                        const __m256 v_values = _mm256_loadu_ps(values_ptr + i);
                        const __m256 v_dev = _mm256_sub_ps(v_values, v_median);
                        const __m256 v_abs_dev = _mm256_andnot_ps(v_sign_mask, v_dev);
                        _mm256_storeu_ps(abs_dev_ptr + i, v_abs_dev);
                    }

                    for (int i = avx_end; i < total_values; ++i)
                    {
                        abs_dev_ptr[i] = std::abs(values_ptr[i] - median);
                    }

                    float mad = calculate_median(abs_dev_buffer);
                    local_mads.push_back(mad);
                }
            }

            return calculate_median(local_mads);
        }

        static float calculate_mad_from_mat_32f_scalar(const cv::Mat &data_mat_32f, int tile_size)
        {
            CV_Assert(data_mat_32f.type() == CV_32FC1);
            int rows = data_mat_32f.rows;
            int cols = data_mat_32f.cols;
            std::vector<float> local_mads;
            for (int y = 0; y < rows; y += tile_size)
            {
                for (int x = 0; x < cols; x += tile_size)
                {
                    int w = std::min(tile_size, cols - x);
                    int h = std::min(tile_size, rows - y);
                    cv::Mat tile = data_mat_32f(cv::Rect(x, y, w, h));
                    std::vector<float> values;
                    values.reserve(tile.total());
                    for (int i = 0; i < tile.rows; ++i)
                    {
                        const float *row = tile.ptr<float>(i);
                        values.insert(values.end(), row, row + tile.cols);
                    }
                    if (values.size() < 2)
                        continue;
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

        static float calculate_mad_from_mat_32f(const cv::Mat &data_mat_32f, int tile_size = 16)
        {
#ifdef __AVX2__
            return calculate_mad_from_mat_32f_avx2(data_mat_32f, tile_size);
#else
            return calculate_mad_from_mat_32f_scalar(data_mat_32f, tile_size);
#endif
        }
    }

    float estimate_tile_noise_sigma_mad_laplacian(
        const cv::Mat &tile_gray_float,
        float mad_to_sigma_factor)
    {
        if (tile_gray_float.empty() || tile_gray_float.channels() != 1 || tile_gray_float.type() != CV_32F)
            return 0.0f;
        if (tile_gray_float.rows < 5 || tile_gray_float.cols < 5)
            return 0.0f;

        cv::Mat laplacian_output;
        try
        {
            cv::Laplacian(tile_gray_float, laplacian_output, CV_32F, 3, 1.0, 0.0, cv::BORDER_REFLECT101);
        }
        catch (const cv::Exception &)
        {
            return 0.0f;
        }

        if (laplacian_output.empty())
            return 0.0f;

        float mad_value = Internal::calculate_mad_from_mat_32f(laplacian_output, 16);
        float estimated_sigma = mad_value * mad_to_sigma_factor;
        return std::max(0.0f, estimated_sigma);
    }
}