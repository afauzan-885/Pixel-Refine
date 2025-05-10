#include "align_phase_correlation.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>               
#include <algorithm>          

namespace MotionAlignment {

CoarseAlignmentResult align_tile_phase_correlation(
    const cv::Mat& current_tile_gray,
    const cv::Mat& full_reference_gray_image,
    int initial_r_tile_start,
    int initial_c_tile_start,
    int tile_h,
    int tile_w,
    int full_image_h,
    int full_image_w,
    int search_margin)
{
    CoarseAlignmentResult result;
    result.aligned_ref_r_global = initial_r_tile_start; 
    result.aligned_ref_c_global = initial_c_tile_start;

    auto set_fallback_result = [&](CoarseAlignmentResult& res) {
        if (initial_r_tile_start >= 0 && initial_c_tile_start >= 0 &&
            initial_r_tile_start + tile_h <= full_image_h &&
            initial_c_tile_start + tile_w <= full_image_w) {
            try {
                res.aligned_reference_tile_gray = full_reference_gray_image(cv::Rect(initial_c_tile_start, initial_r_tile_start, tile_w, tile_h)).clone();
            } catch (const cv::Exception&) {
                res.aligned_reference_tile_gray = cv::Mat(); 
            }
        } else {
             res.aligned_reference_tile_gray = cv::Mat(); 
        }
        res.success = !res.aligned_reference_tile_gray.empty();
        res.aligned_ref_r_global = initial_r_tile_start;
        res.aligned_ref_c_global = initial_c_tile_start;
    };


    if (current_tile_gray.empty() || full_reference_gray_image.empty() ||
        tile_h <= 0 || tile_w <= 0 || search_margin < 0 ||
        current_tile_gray.rows != tile_h || current_tile_gray.cols != tile_w) {
        set_fallback_result(result);
        return result;
    }
    if (current_tile_gray.type() != CV_32FC1 || full_reference_gray_image.type() != CV_32FC1) {
        
    }


    int ref_search_r_start = std::max(0, initial_r_tile_start - search_margin);
    int ref_search_c_start = std::max(0, initial_c_tile_start - search_margin);
    int ref_search_h = std::min(full_image_h - ref_search_r_start, tile_h + 2 * search_margin);
    int ref_search_w = std::min(full_image_w - ref_search_c_start, tile_w + 2 * search_margin);

    if (ref_search_h < tile_h || ref_search_w < tile_w) {
        set_fallback_result(result);
        return result;
    }

    cv::Mat reference_search_area;
    try {
        if (ref_search_r_start < 0 || ref_search_c_start < 0 ||
            ref_search_r_start + ref_search_h > full_reference_gray_image.rows ||
            ref_search_c_start + ref_search_w > full_reference_gray_image.cols) {
            set_fallback_result(result);
            return result;
        }
        cv::Rect search_area_roi(ref_search_c_start, ref_search_r_start, ref_search_w, ref_search_h);
        reference_search_area = full_reference_gray_image(search_area_roi);
    } catch (const cv::Exception& /*e*/) {
        set_fallback_result(result);
        return result;
    }

    if (reference_search_area.empty()) {
        set_fallback_result(result);
        return result;
    }

    // cv::phaseCorrelate mengharapkan input CV_32F atau CV_64F.
    cv::Mat pc_src_for_corr = current_tile_gray; // Tidak perlu clone jika tipe sudah benar dan tidak dimodif
    cv::Mat pc_ref_for_corr = reference_search_area;


    cv::Point2d shift;
    try {
        if (pc_src_for_corr.rows > pc_ref_for_corr.rows || pc_src_for_corr.cols > pc_ref_for_corr.cols) {
             set_fallback_result(result);
             return result;
        }
        shift = cv::phaseCorrelate(pc_ref_for_corr, pc_src_for_corr); // Cari pc_src di dalam pc_ref
    } catch (const cv::Exception& /*e*/) {
        set_fallback_result(result);
        return result;
    }

    int tentative_aligned_r = ref_search_r_start + static_cast<int>(std::round(shift.y));
    int tentative_aligned_c = ref_search_c_start + static_cast<int>(std::round(shift.x));

    if (tentative_aligned_r >= 0 && tentative_aligned_c >= 0 &&
        tentative_aligned_r + tile_h <= full_image_h &&
        tentative_aligned_c + tile_w <= full_image_w)
    {
        result.aligned_ref_r_global = tentative_aligned_r;
        result.aligned_ref_c_global = tentative_aligned_c;
        try {
            result.aligned_reference_tile_gray = full_reference_gray_image(cv::Rect(result.aligned_ref_c_global, result.aligned_ref_r_global, tile_w, tile_h)).clone();
            result.success = !result.aligned_reference_tile_gray.empty();
        } catch (const cv::Exception& /*e*/) {
            set_fallback_result(result); // Ini akan mengatur ulang r_global, c_global ke initial
        }
    } else {
        set_fallback_result(result);
    }
    
    if (result.success && result.aligned_reference_tile_gray.empty()){
        result.success = false;
    }
    if (!result.success && result.aligned_reference_tile_gray.empty()){
        set_fallback_result(result); // Coba lagi set fallback, success akan tetap false jika tile fallback juga gagal
    }


    return result;
}

}