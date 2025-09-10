// spatial_merging.hpp

#ifndef SPATIAL_MERGING_HPP
#define SPATIAL_MERGING_HPP

#include "block_matching.hpp" 
#include <cmath>               
#include <limits>             

namespace MotionMatching { 

float calculate_match_confidence( 
    const MotionMatching::TileMatchResult& result,
    float estimated_noise_sigma,
    float p_mbm_mad_sensitivity, 
    float p_mbm_noise_mad_offset_factor 
);
// --- AKHIR PERBAIKAN ---

} // namespace MotionMatching

#endif // SPATIAL_MERGING_HPP