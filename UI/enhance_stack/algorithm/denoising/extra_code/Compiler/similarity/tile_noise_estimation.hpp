#ifndef TILE_NOISE_ESTIMATION_HPP
#define TILE_NOISE_ESTIMATION_HPP

#include <opencv2/core.hpp>

namespace NoiseEstimation {

/**
 * @brief Mengestimasi standar deviasi noise dari sebuah tile grayscale menggunakan MAD dari output Laplacian.
 *
 * @param tile_gray_float Tile input (CV_32FC1).
 * @param mad_to_sigma_factor Faktor konversi dari MAD ke sigma.
 * @return float Estimasi standar deviasi noise (sigma).
 */
float estimate_tile_noise_sigma_mad_laplacian(
    const cv::Mat &tile_gray_float,
    float mad_to_sigma_factor
);


} 
#endif