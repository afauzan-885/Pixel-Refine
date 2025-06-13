#include "compute_flat.hpp"
#include <opencv2/imgproc.hpp>

namespace TextureAnalysis
{

    void detect_flat_tiles(
        const std::vector<cv::Mat> &channels,
        int tile_h, int tile_w,
        int num_channels,
        float flatness_threshold,
        std::vector<bool> &is_flat,
        cv::Mat &laplacian_buffer)
    {
        CV_Assert(!channels.empty());
        CV_Assert(num_channels > 0 && num_channels <= static_cast<int>(channels.size()));

        int h = channels[0].rows;
        int w = channels[0].cols;
        int num_tiles_y = h / tile_h;
        int num_tiles_x = w / tile_w;

        is_flat.resize(num_tiles_y * num_tiles_x, false);

        if (laplacian_buffer.empty() ||
            laplacian_buffer.rows != tile_h ||
            laplacian_buffer.cols != tile_w ||
            laplacian_buffer.type() != CV_32F)
        {
            laplacian_buffer.create(tile_h, tile_w, CV_32F);
        }

// Loop per-tile
#pragma omp parallel for collapse(2)
        for (int ty = 0; ty < num_tiles_y; ++ty)
        {
            for (int tx = 0; tx < num_tiles_x; ++tx)
            {
                cv::Rect roi(tx * tile_w, ty * tile_h, tile_w, tile_h);

                double total_laplacian = 0.0;

                for (int c = 0; c < num_channels; ++c)
                {
                    const cv::Mat &ch = channels[c];
                    cv::Mat tile = ch(roi);

                    // Hitung Laplacian tile
                    cv::Laplacian(tile, laplacian_buffer, CV_32F, 1);

                    // Rata-rata absolut nilai Laplacian
                    total_laplacian += cv::mean(cv::abs(laplacian_buffer))[0];
                }

                // Rata-rata antar channel
                double avg_laplacian = total_laplacian / num_channels;

                // Deteksi flat jika di bawah ambang
                if (avg_laplacian < flatness_threshold)
                {
                    is_flat[ty * num_tiles_x + tx] = true;
                }
            }
        }
    }
}
