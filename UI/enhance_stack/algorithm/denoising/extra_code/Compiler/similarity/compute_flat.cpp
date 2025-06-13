#include "compute_flat.hpp"
#include <opencv2/imgproc.hpp>
#include <immintrin.h>

namespace TextureAnalysis
{
    namespace Internal
    {
        static inline float horizontal_add_m256(__m256 reg)
        {
            __m128 lo = _mm256_castps256_ps128(reg);
            __m128 hi = _mm256_extractf128_ps(reg, 1);
            __m128 sum = _mm_add_ps(lo, hi);
            sum = _mm_hadd_ps(sum, sum);
            sum = _mm_hadd_ps(sum, sum);
            return _mm_cvtss_f32(sum);
        }

#if defined(__GNUC__) || defined(__clang__)
        __attribute__((target("avx2,fma")))
#endif
        static std::pair<double, double>
        calculate_sum_and_sum_sq_avx2(const cv::Mat &mat)
        {
            const int total = mat.total();
            const int avx_end = total - (total % 8);
            const float *ptr = mat.ptr<float>();

            __m256 v_sum = _mm256_setzero_ps();
            __m256 v_sum_sq = _mm256_setzero_ps();

            for (int i = 0; i < avx_end; i += 8)
            {
                const __m256 v_data = _mm256_loadu_ps(ptr + i);

                v_sum = _mm256_add_ps(v_sum, v_data);

                v_sum_sq = _mm256_fmadd_ps(v_data, v_data, v_sum_sq);
            }

            double total_sum = static_cast<double>(horizontal_add_m256(v_sum));
            double total_sum_sq = static_cast<double>(horizontal_add_m256(v_sum_sq));

            for (int i = avx_end; i < total; ++i)
            {
                double val = static_cast<double>(ptr[i]);
                total_sum += val;
                total_sum_sq += val * val;
            }

            return {total_sum, total_sum_sq};
        }
    }

    void detect_flat_tiles(
        const std::vector<cv::Mat> &channels,
        int tile_h, int tile_w,
        int num_channels,
        float flatness_variance_threshold,
        std::vector<bool> &is_flat)
    {
        CV_Assert(!channels.empty());
        CV_Assert(num_channels > 0 && num_channels <= static_cast<int>(channels.size()));

        int h = channels[0].rows;
        int w = channels[0].cols;
        int num_tiles_y = h / tile_h;
        int num_tiles_x = w / tile_w;

        is_flat.resize(num_tiles_y * num_tiles_x, false);

#pragma omp parallel
        {
            // Buat buffer per-thread untuk menghindari race condition
            cv::Mat laplacian_buffer(tile_h, tile_w, CV_32F);

#pragma omp for collapse(2)
            for (int ty = 0; ty < num_tiles_y; ++ty)
            {
                for (int tx = 0; tx < num_tiles_x; ++tx)
                {
                    cv::Rect roi(tx * tile_w, ty * tile_h, tile_w, tile_h);

                    double total_variance = 0.0;

                    for (int c = 0; c < num_channels; ++c)
                    {
                        const cv::Mat &ch = channels[c];
                        cv::Mat tile = ch(roi);

                        // 1. Hitung Laplacian (tetap menggunakan OpenCV yang cepat)
                        cv::Laplacian(tile, laplacian_buffer, CV_32F, 1, 1.0, 0.0, cv::BORDER_REFLECT101);

                        // 2. Hitung statistik menggunakan fungsi AVX2 kita
                        auto [sum, sum_sq] = Internal::calculate_sum_and_sum_sq_avx2(laplacian_buffer);

                        double num_pixels = static_cast<double>(laplacian_buffer.total());
                        if (num_pixels > 0)
                        {
                            double mean = sum / num_pixels;
                            double variance = (sum_sq / num_pixels) - (mean * mean);
                            total_variance += variance;
                        }
                    }

                    double avg_variance = total_variance / num_channels;

                    if (avg_variance < flatness_variance_threshold)
                    {
                        is_flat[ty * num_tiles_x + tx] = true;
                    }
                }
            }
        }
    }
}