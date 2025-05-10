// align_phase_correlation.hpp
#ifndef align_phase_correlation_HPP
#define align_phase_correlation_HPP

#include <opencv2/core.hpp>
namespace MotionAlignment {

struct CoarseAlignmentResult {
    cv::Mat aligned_reference_tile_gray;  
    int aligned_ref_r_global = -1;        
    int aligned_ref_c_global = -1;        
    bool success = false;                
};

CoarseAlignmentResult align_tile_phase_correlation(
    const cv::Mat& current_tile_gray,         // Tile dari frame saat ini (template)
    const cv::Mat& full_reference_gray_image, // Gambar referensi penuh untuk dicari
    int initial_r_tile_start,                 // Posisi baris awal tile pada gambar referensi (sebelum alignment)
    int initial_c_tile_start,                 // Posisi kolom awal tile pada gambar referensi (sebelum alignment)
    int tile_h,                               // Tinggi tile
    int tile_w,                               // Lebar tile
    int full_image_h,                         // Tinggi gambar referensi penuh
    int full_image_w,                         // Lebar gambar referensi penuh
    int search_margin                         // Margin tambahan di sekitar tile awal untuk area pencarian
);

} // namespace MotionAlignment

#endif // align_phase_correlation_HPP