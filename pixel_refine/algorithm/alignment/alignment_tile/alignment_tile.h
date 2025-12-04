#ifndef ALIGNMENT_TILE_H
#define ALIGNMENT_TILE_H

#include <opencv2/core.hpp>

// --- API Export/Import (Tetap sama) ---
#ifdef _WIN32
    #ifdef ALIGNMENT_TILE_EXPORTS
        #define ALIGNMENT_API __declspec(dllexport)
    #else
        #define ALIGNMENT_API __declspec(dllimport)
    #endif
#else
    #define ALIGNMENT_API
#endif


namespace ImageAlignment {

cv::Mat getGaussianWindow(int rows, int cols);
void refineFlowLayer(const cv::Mat& ref_layer, const cv::Mat& comp_layer, cv::Mat& flow, 
                     const cv::Mat& window, int search_dist);

}

#ifdef __cplusplus
extern "C" {
#endif

ALIGNMENT_API float* compute_alignment_flow(
    const float* ref_work_data,
    const float* current_work_data,
    int work_h, int work_w,
    int tile_h, int tile_w,
    int n_layers, float search_dist
);

ALIGNMENT_API void free_flow_memory(float* flow_data);

#ifdef __cplusplus
}
#endif

#endif