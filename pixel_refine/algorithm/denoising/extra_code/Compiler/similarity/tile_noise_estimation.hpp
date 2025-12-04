#ifndef TILE_NOISE_ESTIMATION_HPP
#define TILE_NOISE_ESTIMATION_HPP

#include <opencv2/core.hpp>

namespace NoiseEstimation {


float estimate_tile_noise_sigma_mad_laplacian(
    const cv::Mat &tile_gray_float,
    float mad_to_sigma_factor
);


} 
#endif