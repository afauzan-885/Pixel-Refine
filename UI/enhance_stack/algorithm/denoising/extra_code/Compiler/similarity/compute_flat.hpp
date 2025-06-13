#ifndef COMPUTE_FLAT_HPP
#define COMPUTE_FLAT_HPP

#include <opencv2/core.hpp>
#include <vector>

namespace TextureAnalysis
{

    void detect_flat_tiles(
        const std::vector<cv::Mat> &channels,
        int tile_h, int tile_w,
        int num_channels,
        float flatness_threshold,
        std::vector<bool> &is_flat,
        cv::Mat &laplacian_buffer);

}

#endif // COMPUTE_FLAT_HPP
