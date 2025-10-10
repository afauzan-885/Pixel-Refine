#include "refinement.hpp" 
#include "cost_function.hpp"

#include <opencv2/imgproc.hpp> 
#include <opencv2/tracking.hpp>
#include <cmath>              

// Fungsi helper ini hanya terlihat di dalam file ini (linkage internal)
static inline float bicubic_at(const cv::Mat &img, float x, float y)
{
    // Cek batas dasar untuk mencegah crash. Jika di luar, kembalikan 0.
    if (x < 0 || y < 0 || x >= img.cols - 1 || y >= img.rows - 1) {
        return 0.0f;
    }

    // OpenCV Remap adalah cara yang sangat dioptimalkan untuk interpolasi
    // Kita buat map 1x1 untuk mengambil nilai tepat di (x,y)
    cv::Mat map_x(1, 1, CV_32F, x);
    cv::Mat map_y(1, 1, CV_32F, y);
    cv::Mat dst(1, 1, CV_32F);

    // cv::remap akan melakukan interpolasi bicubic dan menangani semua kasus tepi
    cv::remap(img, dst, map_x, map_y, cv::INTER_CUBIC, cv::BORDER_REPLICATE);

    return dst.at<float>(0, 0);
}


cv::Point2f subpixel_refinement(const cv::Mat &ref_layer,
                                      const cv::Mat &comp_layer,
                                      int x,
                                      int y,
                                      int dx,
                                      int dy,
                                      int tile_w,
                                      int tile_h)
{
    // =========================================================================
    // === PARAMETER UNTUK PENILAIAN ===========================================
    // =========================================================================
    constexpr double MIN_CONFIDENCE_RESPONSE = 0.30; 
    constexpr double MAX_CONFIDENCE_RESPONSE = 0.95; 
    constexpr float MAX_FINAL_SAD_PER_PIXEL = 0.05f; 

    // =========================================================================
    // === LANGKAH 1: KOREKSI - Pencarian Integer 5x5 menggunakan ZSAD_AVX =====
    // =========================================================================
    float min_cost = std::numeric_limits<float>::max();
    int best_integer_dx = dx;
    int best_integer_dy = dy;

    // Pencarian 5x5 untuk capture radius yang lebih besar
    for (int ddy = -2; ddy <= 2; ++ddy)
    {
        for (int ddx = -2; ddx <= 2; ++ddx)
        {
            int current_dx = dx + ddx;
            int current_dy = dy + ddy;

            // Pastikan tile berada sepenuhnya di dalam batas gambar
            if (x < 0 || y < 0 || (x + tile_w) > ref_layer.cols || (y + tile_h) > ref_layer.rows ||
                (x + current_dx) < 0 || (y + current_dy) < 0 ||
                (x + current_dx + tile_w) > comp_layer.cols || (y + current_dy + tile_h) > comp_layer.rows)
            {
                continue;
            }

            // Hitung ZSAD menggunakan fungsi AVX Anda yang cepat
            float total_cost = 0.0f;
            for (int r = 0; r < tile_h; ++r)
            {
                const float* p_ref = ref_layer.ptr<float>(y + r, x);
                const float* p_comp = comp_layer.ptr<float>(y + current_dy + r, x + current_dx);
                total_cost += block_cost_zsad_avx(p_ref, p_comp, tile_w);
            }

            if (total_cost < min_cost)
            {
                min_cost = total_cost;
                best_integer_dx = current_dx;
                best_integer_dy = current_dy;
            }
        }
    }
    
    cv::Point2f integer_flow((float)best_integer_dx, (float)best_integer_dy);

    // =========================================================================
    // === LANGKAH 2: PENYEMPURNAAN - Menggunakan ECC ==========================
    // =========================================================================
    int border = 3; 
    cv::Rect final_comp_roi(x + best_integer_dx - border, y + best_integer_dy - border, 
                              tile_w + 2*border, tile_h + 2*border);
    cv::Rect image_bounds(0, 0, comp_layer.cols, comp_layer.rows);

    if ((final_comp_roi & image_bounds) != final_comp_roi)
    {
        return integer_flow;
    }
    
    cv::Mat ref_tile_ecc = ref_layer(cv::Rect(x, y, tile_w, tile_h));
    cv::Mat comp_tile_ecc = comp_layer(final_comp_roi);
    
    cv::Mat warp_matrix = cv::Mat::eye(2, 3, CV_32F);
    warp_matrix.at<float>(0, 2) = (float)border; 
    warp_matrix.at<float>(1, 2) = (float)border;

    try 
    {
        double response = cv::findTransformECC(
            ref_tile_ecc, comp_tile_ecc, warp_matrix, cv::MOTION_TRANSLATION,
            cv::TermCriteria(cv::TermCriteria::COUNT + cv::TermCriteria::EPS, 20, 0.001)
        );

        float shift_x = warp_matrix.at<float>(0, 2) - border;
        float shift_y = warp_matrix.at<float>(1, 2) - border;
        
        cv::Point2f refined_flow(
            (float)best_integer_dx + shift_x,
            (float)best_integer_dy + shift_y
        );

        // =========================================================================
        // === LANGKAH 3: KEPUTUSAN NON-BINER - Interpolasi Berdasarkan Kepercayaan
        // =========================================================================
        double confidence = (response - MIN_CONFIDENCE_RESPONSE) / 
                            (MAX_CONFIDENCE_RESPONSE - MIN_CONFIDENCE_RESPONSE);
        confidence = std::max(0.0, std::min(1.0, confidence));

        cv::Point2f final_flow;
        final_flow.x = (float)(integer_flow.x * (1.0 - confidence) + refined_flow.x * confidence);
        final_flow.y = (float)(integer_flow.y * (1.0 - confidence) + refined_flow.y * confidence);
        
        // =========================================================================
        // === LANGKAH 4: VALIDASI AKHIR - Penjaga Terakhir dengan SAD =========
        // =========================================================================
        float sad_final = 0.0f;
        for (int r = 0; r < tile_h; r++)
        {
            const float *p_ref = ref_layer.ptr<float>(y + r, x);
            for (int c = 0; c < tile_w; c++)
            {
                float ref_val = p_ref[c];
                float comp_val = bicubic_at(comp_layer, (float)(x + final_flow.x + c), (float)(y + final_flow.y + r));
                sad_final += std::fabs(ref_val - comp_val);
            }
        }
        sad_final /= (tile_w * tile_h);

        if (sad_final > MAX_FINAL_SAD_PER_PIXEL)
        {
            return integer_flow;
        }
        
        return final_flow;
    }
    catch (const cv::Exception& e)
    {
        return integer_flow;
    }
}