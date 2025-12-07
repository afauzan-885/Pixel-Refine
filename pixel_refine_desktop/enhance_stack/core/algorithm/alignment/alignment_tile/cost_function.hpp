#ifndef cost_function_HPP
#define cost_function_HPP

#include <opencv2/core/mat.hpp>

// Deklarasi fungsi Zero-Mean SAD dengan AVX
float calculate_fine_analysis(const float* ref, const float* comp, int len);

// Deklarasi fungsi cost menggunakan FFT + Geman–McClure Robust Cost
float block_cost_fft(const cv::Mat &ref, const cv::Mat &comp);


#endif