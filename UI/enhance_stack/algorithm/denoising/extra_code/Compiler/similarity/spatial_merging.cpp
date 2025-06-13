#include "spatial_merging.hpp"

namespace MotionMatching
{
    namespace MotionMetricsConfig
    {
        constexpr float STABILITY_EPSILON = 1e-6f;
        constexpr float CONFIDENCE_EPSILON = 1e-6f;
    }

    float calculate_match_confidence(
        const MotionMatching::BlockMatchResult &result,
        float estimated_noise_sigma,
        float p_mbm_mad_sensitivity,
        float p_mbm_noise_mad_offset_factor)
    {
        using namespace MotionMetricsConfig;
        float match_confidence = 0.0f;

        if (!result.success || result.matches_found <= 0)
        {
            return 0.0f;
        }

        float noise_induced_mad_offset = p_mbm_noise_mad_offset_factor * estimated_noise_sigma;
        float excess_mad = std::max(0.0f, result.min_mad - noise_induced_mad_offset);

        float absolute_quality_confidence = std::exp(-excess_mad * p_mbm_mad_sensitivity);
        absolute_quality_confidence = std::max(0.0f, std::min(1.0f, absolute_quality_confidence));

        if (result.matches_found == 1)
        {
            match_confidence = std::min(0.75f, absolute_quality_confidence);
        }
        else
        {
            float ratio_confidence = 1.0f;
            if (result.second_min_mad < std::numeric_limits<float>::max() && result.second_min_mad > CONFIDENCE_EPSILON)
            {
                float excess_second_min_mad = std::max(0.0f, result.second_min_mad - noise_induced_mad_offset);
                float ratio = 1.0f;
                if (excess_second_min_mad > STABILITY_EPSILON)
                {
                    ratio = excess_mad / excess_second_min_mad;
                }
                else if (excess_mad < CONFIDENCE_EPSILON)
                {
                    ratio = 0.0f;
                }
                ratio_confidence = std::max(0.0f, 1.0f - ratio);
            }
            match_confidence = absolute_quality_confidence * ratio_confidence;
        }

        return std::max(0.0f, std::min(1.0f, match_confidence));
    }

    bool is_motion_vector_outlier(
        float dx_main, float dy_main,
        float dx_neighbor, float dy_neighbor,
        float motion_jump_threshold)
    {
        float dx_diff = dx_main - dx_neighbor;
        float dy_diff = dy_main - dy_neighbor;
        float distance_squared = dx_diff * dx_diff + dy_diff * dy_diff;
        return distance_squared > (motion_jump_threshold * motion_jump_threshold);
    }

} // namespace MotionMatching
