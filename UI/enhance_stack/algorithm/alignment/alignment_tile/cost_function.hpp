#ifndef cost_function_HPP
#define cost_function_HPP

#include <opencv2/core/mat.hpp>

// Deklarasi fungsi Zero-Mean SAD dengan AVX
float block_cost_zsad_avx(const float* ref, const float* comp, int len);

// Deklarasi fungsi cost menggunakan FFT
float block_cost_fft(const cv::Mat &ref, const cv::Mat &comp);

#endif // cost_function_HPP