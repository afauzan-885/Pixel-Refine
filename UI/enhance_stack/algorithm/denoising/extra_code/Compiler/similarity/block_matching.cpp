#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>

namespace MotionMatching
{
    namespace Internal
    {

        // Fungsi MAD biasa (tanpa workspace)
        static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1);

            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;
            float total_diff = 0.0f;

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y);
                const float *__restrict ptr2 = block2_gray.ptr<float>(y);

#pragma omp simd reduction(+ : total_diff)
                for (int x = 0; x < cols; ++x)
                {
                    total_diff += std::abs(ptr1[x] - ptr2[x]);
                }
            }

            return total_diff / static_cast<float>(rows * cols);
        }

        // Fungsi weighted MAD yang aware noise + motion
        static float calculate_noise_motion_aware_weighted_mad(
            const cv::Mat &block1_gray,
            const cv::Mat &block2_gray,
            const cv::Mat &grad_mag_block1,
            const cv::Mat &abs_diff_block,
            float noise_level,
            float noise_threshold,
            float diff_threshold,
            float grad_weight_factor,
            float stab_epsilon)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      grad_mag_block1.size() == block1_gray.size() &&
                      abs_diff_block.size() == block1_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1 &&
                      grad_mag_block1.type() == CV_32FC1 &&
                      abs_diff_block.type() == CV_32FC1);

            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;

            float weighted_sum = 0.0f;
            float total_weight = 0.0f;

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y);
                const float *__restrict ptr2 = block2_gray.ptr<float>(y);
                const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y);
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);

#pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < cols; ++x)
                {
                    float noise_weight = 1.0f;
                    if (noise_level > noise_threshold)
                    {
                        if (diff_ptr[x] < diff_threshold)
                        {
                            noise_weight = 2.0f; // noisy + statis => bobot tinggi
                        }
                        else
                        {
                            noise_weight = 0.5f; // noisy + motion => bobot rendah
                        }
                    }

                    float grad_weight = 1.0f + grad_weight_factor * mag_ptr[x];
                    float weight = grad_weight * noise_weight;

                    total_weight += weight;
                    weighted_sum += std::abs(ptr1[x] - ptr2[x]) * weight;
                }
            }

            if (total_weight <= stab_epsilon)
            {
                return calculate_plain_mad_32f(block1_gray, block2_gray);
            }

            return weighted_sum / total_weight;
        }

    } // namespace Internal

    BlockMatchResult find_best_block_match_mad(
        const cv::Mat &current_block_gray,
        const cv::Mat &reference_tile_gray,
        int block_r_start_in_ref_tile,
        int block_c_start_in_ref_tile,
        int search_radius,
        float gradient_weight_factor,
        float stability_epsilon,
        MBMBuffers &buffers)
    {
        BlockMatchResult result;

        if (current_block_gray.empty() || reference_tile_gray.empty())
        {
            result.success = false;
            return result;
        }

        const int bh = current_block_gray.rows;
        const int bw = current_block_gray.cols;
        const int rh = reference_tile_gray.rows;
        const int rw = reference_tile_gray.cols;

        if (bh <= 0 || bw <= 0 || rh < bh || rw < bw)
        {
            result.success = false;
            return result;
        }

        // Tentukan apakah gunakan weighted atau plain MAD
        const bool use_plain = (std::abs(gradient_weight_factor) < stability_epsilon || bh < 3 || bw < 3);

        cv::Mat grad_mag;
        if (!use_plain)
        {
            CV_Assert(buffers.grad_x.rows >= bh && buffers.grad_x.cols >= bw);
            CV_Assert(buffers.grad_y.rows >= bh && buffers.grad_y.cols >= bw);
            CV_Assert(buffers.grad_mag_current.rows >= bh && buffers.grad_mag_current.cols >= bw);

            cv::Mat grad_x = buffers.grad_x(cv::Rect(0, 0, bw, bh));
            cv::Mat grad_y = buffers.grad_y(cv::Rect(0, 0, bw, bh));
            grad_mag = buffers.grad_mag_current(cv::Rect(0, 0, bw, bh));

            cv::Scharr(current_block_gray, grad_x, CV_32F, 1, 0, 1, 0, cv::BORDER_REPLICATE);
            cv::Scharr(current_block_gray, grad_y, CV_32F, 0, 1, 1, 0, cv::BORDER_REPLICATE);
            cv::magnitude(grad_x, grad_y, grad_mag);
        }

        // Cari min dan max pixel nilai untuk estimasi noise sederhana tile
        double min_val, max_val;
        cv::minMaxLoc(current_block_gray, &min_val, &max_val);
        // estimasi noise level kasar (misal range / 10)
        float noise_level = static_cast<float>((max_val - min_val) / 10.0);

        // Threshold sederhana untuk noisy dan perbedaan
        constexpr float noise_threshold = 0.05f; // bisa kamu sesuaikan
        constexpr float diff_threshold = 0.02f;  // threshold beda pixel kecil dianggap statis

        // Batas pencarian seluruh tile (full tile search)
        const int r0 = 0;
        const int r1 = rh - bh;
        const int c0 = 0;
        const int c1 = rw - bw;

        cv::Mat abs_diff_block(cv::Size(bw, bh), CV_32FC1);

        for (int r = r0; r <= r1; ++r)
        {
            for (int c = c0; c <= c1; ++c)
            {
                cv::Rect roi(c, r, bw, bh);
                const cv::Mat ref_block = reference_tile_gray(roi);

                // Hitung abs difference pixel block
                for (int y = 0; y < bh; ++y)
                {
                    const float *ptr_cur = current_block_gray.ptr<float>(y);
                    const float *ptr_ref = ref_block.ptr<float>(y);
                    float *ptr_diff = abs_diff_block.ptr<float>(y);
#pragma omp simd
                    for (int x = 0; x < bw; ++x)
                    {
                        ptr_diff[x] = std::abs(ptr_cur[x] - ptr_ref[x]);
                    }
                }

                float score;
                if (use_plain)
                {
                    cv::Mat diff = buffers.diff_workspace(cv::Rect(0, 0, bw, bh));
                    score = Internal::calculate_plain_mad_32f(current_block_gray, ref_block);
                }
                else
                {
                    score = Internal::calculate_noise_motion_aware_weighted_mad(
                        current_block_gray, ref_block, grad_mag, abs_diff_block,
                        noise_level, noise_threshold, diff_threshold,
                        gradient_weight_factor, stability_epsilon);
                }

                result.matches_found++;
                if (score < result.min_mad)
                {
                    result.second_min_mad = result.min_mad;
                    result.min_mad = score;
                    result.best_match_r = r;
                    result.best_match_c = c;
                    result.success = true;
                }
                else if (score < result.second_min_mad)
                {
                    result.second_min_mad = score;
                }
            }
        }

        return result;
    }

} // namespace MotionMatching
