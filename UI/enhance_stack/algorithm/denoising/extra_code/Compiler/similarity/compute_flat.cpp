#include "compute_flat.hpp"
#include <opencv2/imgproc.hpp>

namespace TextureAnalysis
{
    void detect_flat_tiles(
        const std::vector<cv::Mat> &channels,
        int tile_h, int tile_w,
        int num_channels,
        float flatness_variance_threshold,
        std::vector<bool> &is_flat)
    {
        CV_Assert(!channels.empty());
        int h = channels[0].rows;
        int w = channels[0].cols;

        // --- INTI OPTIMISASI AGRESIF ---
        // Tentukan faktor skala untuk bekerja pada resolusi yang jauh lebih rendah
        const int scale_factor = 4; // Bekerja pada 1/4 resolusi. Angka ini bisa di-tuning.
        int h_small = h / scale_factor;
        int w_small = w / scale_factor;
        int tile_h_small = std::max(1, tile_h / scale_factor);
        int tile_w_small = std::max(1, tile_w / scale_factor);
        
        // Sesuaikan threshold varians untuk resolusi yang lebih rendah
        // Varians akan lebih rendah pada gambar yang di-downsample
        float scaled_variance_threshold = flatness_variance_threshold / (scale_factor * 0.5f);

        int num_tiles_y = h / tile_h;
        int num_tiles_x = w / tile_w;
        is_flat.assign(num_tiles_y * num_tiles_x, false);

        std::vector<cv::Mat> small_channels(num_channels);
        
        #pragma omp parallel for
        for (int c = 0; c < num_channels; ++c) {
            cv::resize(channels[c], small_channels[c], cv::Size(w_small, h_small), 0, 0, cv::INTER_AREA);
        }

        #pragma omp parallel for collapse(2) schedule(static)
        for (int ty = 0; ty < num_tiles_y; ++ty) {
            for (int tx = 0; tx < num_tiles_x; ++tx) {
                // Hitung ROI di skala kecil yang sesuai
                int small_tx = tx * tile_w / scale_factor;
                int small_ty = ty * tile_h / scale_factor;
                cv::Rect roi_small(small_tx, small_ty, tile_w_small, tile_h_small);

                double total_variance = 0.0;
                for (int c = 0; c < num_channels; ++c) {
                    // Pastikan ROI tidak keluar dari batas gambar kecil
                    if (roi_small.x + roi_small.width <= w_small && roi_small.y + roi_small.height <= h_small) {
                        cv::Mat tile_small = small_channels[c](roi_small);
                        cv::Scalar mean, stddev;
                        cv::meanStdDev(tile_small, mean, stddev);
                        total_variance += stddev[0] * stddev[0];
                    }
                }
                
                if ((total_variance / num_channels) < scaled_variance_threshold) {
                    is_flat[ty * num_tiles_x + tx] = true;
                }
            }
        }
    }
}