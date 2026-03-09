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
        // Fungsi helper untuk estimasi median dari histogram
        float get_median_from_hist(const cv::Mat& hist, float min_val, float max_val, int total_pixels)
        {
            float median = 0.0f;
            int h_bins = hist.rows;
            float bin_width = (max_val - min_val) / h_bins;
            int median_count = total_pixels / 2;

            float cumulative_sum = 0;
            for (int i = 0; i < h_bins; ++i)
            {
                cumulative_sum += hist.at<float>(i);
                if (cumulative_sum >= median_count)
                {
                    median = min_val + (i + 0.5f) * bin_width;
                    break;
                }
            }
            return median;
        }
    }

    float estimate_tile_noise_sigma_mad_laplacian(
        const cv::Mat &tile_gray_float,
        float mad_to_sigma_factor)
    {
        if (tile_gray_float.empty() || tile_gray_float.rows < 20 || tile_gray_float.cols < 20)
            return 0.0f; // Butuh gambar yang cukup besar

        // --- INTI OPTIMISASI ---
        // 1. Bekerja pada versi gambar yang diperkecil (downsampled)
        cv::Mat downsampled_img;
        // Kita perkecil hingga sisi terpanjangnya sekitar 1024 piksel untuk kecepatan
        float scale = 1024.0f / std::max(tile_gray_float.rows, tile_gray_float.cols);
        if (scale < 1.0f) {
            cv::resize(tile_gray_float, downsampled_img, cv::Size(), scale, scale, cv::INTER_AREA);
        } else {
            downsampled_img = tile_gray_float;
        }

        // 2. Sekarang, semua operasi berikutnya berjalan pada gambar yang jauh lebih kecil
        cv::Mat laplacian_output;
        cv::Laplacian(downsampled_img, laplacian_output, CV_32F, 3, 1.0, 0.0, cv::BORDER_REFLECT101);

        if (laplacian_output.empty()) return 0.0f;
        
        // Sisa dari logika histogram Anda tetap sama, tetapi sekarang pada data yang jauh lebih sedikit
        double min_val, max_val;
        cv::minMaxLoc(laplacian_output, &min_val, &max_val);

        int h_bins = 256; // Jumlah bin yang cukup untuk presisi
        float range[] = { (float)min_val, (float)max_val };
        const float* hist_range = { range };

        cv::Mat hist;
        cv::calcHist(&laplacian_output, 1, 0, cv::Mat(), hist, 1, &h_bins, &hist_range, true, false);

        float median = Internal::get_median_from_hist(hist, min_val, max_val, laplacian_output.total());
        
        // Hitung deviasi absolut
        cv::Mat abs_dev;
        cv::absdiff(laplacian_output, cv::Scalar(median), abs_dev);
        
        // Hitung histogram lagi untuk deviasi absolut
        cv::minMaxLoc(abs_dev, &min_val, &max_val);
        range[0] = (float)min_val; range[1] = (float)max_val;

        cv::Mat mad_hist;
        cv::calcHist(&abs_dev, 1, 0, cv::Mat(), mad_hist, 1, &h_bins, &hist_range, true, false);

        float mad_value = Internal::get_median_from_hist(mad_hist, min_val, max_val, abs_dev.total());
        
        return mad_value * mad_to_sigma_factor;
    }
}