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
        // Logika `if (matches_found == 1)` dan `ratio_confidence` dihapus
        // karena tidak ada lagi pencarian untuk menghasilkan `second_min_mad`.
        // Kepercayaan sekarang murni berdasarkan kualitas absolut dari satu-satunya pencocokan.

        float absolute_quality_confidence = std::exp(-excess_mad * p_mbm_mad_sensitivity);

        return std::max(0.0f, std::min(1.0f, absolute_quality_confidence));
    }

    // --- TIDAK ADA PERUBAHAN, TAPI MUNGKIN TIDAK DIGUNAKAN LAGI ---
    // Fungsi ini terkait dengan vektor gerak, yang tidak lagi dihitung.
    // Bisa dihapus jika tidak ada bagian lain dari kode Anda yang menggunakannya.
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

}