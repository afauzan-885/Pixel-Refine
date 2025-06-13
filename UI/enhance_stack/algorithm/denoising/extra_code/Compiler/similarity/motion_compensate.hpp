#ifndef MOTION_COMPENSATE_HPP
#define MOTION_COMPENSATE_HPP

#include "block_matching.hpp" 
#include <opencv2/opencv.hpp>

namespace MotionCompensate
{
    struct MotionData
    {
        bool compensation_applied = false;
        float motion_offset_magnitude = 0.0f;
        float offset_weight = 1.0f;
        cv::Mat compensated_color_tile;
        cv::Mat compensated_gray_tile;
    };

    struct MotionCompensationBuffers
    {
        MotionMatching::MBMBuffers mbm_buffers; 
        cv::Mat compensated_tile_color;         
        cv::Mat compensated_tile_gray;         
    };

    template<typename T>
    inline std::pair<float, float> get_motion_offsets(const T& result) {
        if constexpr (requires { result.offset_x; result.offset_y; }) {
            return {result.offset_x, result.offset_y};
        } else if constexpr (requires { result.x_offset; result.y_offset; }) {
            return {result.x_offset, result.y_offset};
        } else if constexpr (requires { result.dx; result.dy; }) {
            return {result.dx, result.dy};
        } else if constexpr (requires { result.x; result.y; }) {
            return {result.x, result.y};
        } else {
            return {0.0f, 0.0f};
        }
    }

    MotionData process_tile_motion(
        const cv::Mat &full_current_image,
        const cv::Mat &full_current_gray,
        const cv::Mat &full_reference_gray,
        const cv::Rect &tile_roi,
        int search_radius,
        MotionCompensationBuffers &buffers);

}

#endif