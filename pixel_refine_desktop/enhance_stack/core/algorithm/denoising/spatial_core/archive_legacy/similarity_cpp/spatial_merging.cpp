// spatial_merging.cpp

#include "spatial_merging.hpp"

namespace MotionMatching
{
    namespace MotionMetricsConfig
    {
        constexpr float STABILITY_EPSILON = 1e-6f;
        constexpr float CONFIDENCE_EPSILON = 1e-6f;
    }

    float calculate_match_confidence(
        const MotionMatching::TileMatchResult &result,
        float estimated_noise_sigma,
        float p_mbm_mad_sensitivity,
        float p_mbm_noise_mad_offset_factor)
    {
        using namespace MotionMetricsConfig;

        if (!result.success)
        {
            return 0.0f;
        }

        // Perhitungan "excess MAD" setelah memperhitungkan noise tetap sangat berguna
        float noise_induced_mad_offset = p_mbm_noise_mad_offset_factor * estimated_noise_sigma;
        float excess_mad = std::max(0.0f, result.mad_score - noise_induced_mad_offset); // Menggunakan mad_score

        // --- DIHAPUS ---
        float absolute_quality_confidence = std::exp(-excess_mad * p_mbm_mad_sensitivity);

        return std::max(0.0f, std::min(1.0f, absolute_quality_confidence));
    }
}