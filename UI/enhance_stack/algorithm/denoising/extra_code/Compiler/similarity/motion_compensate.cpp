#include "motion_compensate.hpp"
#include <cmath>
#include <utility>

namespace
{
    constexpr float MAX_MOTION_OFFSET = 6.0f;
    constexpr float MIN_MOTION_THRESHOLD = 0.3f;
    constexpr float SUBPIXEL_THRESHOLD = 0.15f;
    constexpr float OFFSET_WEIGHT_BASE = 1.0f;
    constexpr float OFFSET_WEIGHT_DECAY = 0.15f;
    constexpr float GRADIENT_WEIGHT_FACTOR = 0.5f;
    constexpr float STABILITY_EPSILON = 1e-4f;

    std::pair<float, float> get_motion_offsets(const auto &result)
    {
        if constexpr (requires { result.offset_x; result.offset_y; })
        {
            return {result.offset_x, result.offset_y};
        }
        else
        {
            return {0.0f, 0.0f};
        }
    }

    float calculate_offset_weight(float offset_magnitude, float max_offset)
    {
        if (offset_magnitude <= 0.01f)
            return OFFSET_WEIGHT_BASE;
        const float normalized_offset = std::min(offset_magnitude / max_offset, 1.0f);
        return OFFSET_WEIGHT_BASE * std::exp(-OFFSET_WEIGHT_DECAY * normalized_offset * normalized_offset);
    }

    bool apply_motion_compensation(const cv::Mat &source_mat,
                                   const cv::Rect &tile_roi,
                                   float offset_x, float offset_y,
                                   cv::Mat &compensated_tile)
    {
        const float abs_offset_x = std::abs(offset_x);
        const float abs_offset_y = std::abs(offset_y);

        if (abs_offset_x < MIN_MOTION_THRESHOLD && abs_offset_y < MIN_MOTION_THRESHOLD)
        {
            return false;
        }

        const int comp_x = static_cast<int>(std::round(tile_roi.x + offset_x));
        const int comp_y = static_cast<int>(std::round(tile_roi.y + offset_y));

        const int margin = 1;
        if (comp_x < margin || comp_y < margin ||
            comp_x + tile_roi.width >= source_mat.cols - margin ||
            comp_y + tile_roi.height >= source_mat.rows - margin)
        {
            return false;
        }

        // Alokasi buffer tujuan jika ukurannya tidak sesuai
        if (compensated_tile.size() != tile_roi.size() || compensated_tile.type() != source_mat.type())
        {
            compensated_tile.create(tile_roi.size(), source_mat.type());
        }

        if (abs_offset_x - std::floor(abs_offset_x) > SUBPIXEL_THRESHOLD ||
            abs_offset_y - std::floor(abs_offset_y) > SUBPIXEL_THRESHOLD)
        {
            cv::Mat transform_matrix = (cv::Mat_<float>(2, 3) << 1, 0, offset_x, 0, 1, offset_y);
            cv::warpAffine(source_mat(tile_roi), compensated_tile, transform_matrix,
                           cv::Size(tile_roi.width, tile_roi.height),
                           cv::INTER_LINEAR | cv::WARP_INVERSE_MAP);
        }
        else
        {
            const cv::Rect comp_roi(comp_x, comp_y, tile_roi.width, tile_roi.height);
            source_mat(comp_roi).copyTo(compensated_tile);
        }

        return true;
    }
}

namespace MotionCompensate
{

    MotionData process_tile_motion(
        const cv::Mat &full_current_image,
        const cv::Mat &full_current_gray,
        const cv::Mat &full_reference_gray,
        const cv::Rect &tile_roi,
        int search_radius,
        MotionCompensationBuffers &buffers)
    {
        MotionData result;

        const cv::Mat current_tile_gray = full_current_gray(tile_roi);
        const cv::Mat reference_tile_gray = full_reference_gray(tile_roi);

        // Jalankan motion matching untuk seluruh tile
        const auto global_motion_result = MotionMatching::find_best_block_match_mad(
            current_tile_gray, reference_tile_gray, 0, 0, search_radius,
            GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers.mbm_buffers);

        if (global_motion_result.success)
        {
            const auto [offset_x, offset_y] = get_motion_offsets(global_motion_result);
            result.motion_offset_magnitude = std::sqrt(offset_x * offset_x + offset_y * offset_y);

            result.offset_weight = calculate_offset_weight(result.motion_offset_magnitude, MAX_MOTION_OFFSET);

            if (result.motion_offset_magnitude > MIN_MOTION_THRESHOLD && result.motion_offset_magnitude <= MAX_MOTION_OFFSET)
            {

                if (apply_motion_compensation(full_current_image, tile_roi, -offset_x, -offset_y, buffers.compensated_tile_color))
                {

                    if (apply_motion_compensation(full_current_gray, tile_roi, -offset_x, -offset_y, buffers.compensated_tile_gray))
                    {
                        result.compensation_applied = true;
                        result.compensated_color_tile = buffers.compensated_tile_color;
                        result.compensated_gray_tile = buffers.compensated_tile_gray;
                    }
                }
            }
        }

        return result;
    }
}