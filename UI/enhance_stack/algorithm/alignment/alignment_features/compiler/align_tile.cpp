#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <opencv2/opencv.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/types.hpp>
#include <omp.h>
#ifdef _OPENMP
#endif

cv::Mat create_hanning_window_2d_cv(int rows, int cols) {
    if (rows <= 0 || cols <= 0) {
        // std::cerr << "Error: Hanning window dimensions must be positive. Got " << rows << "x" << cols << std::endl;
        return cv::Mat(); 
    }

    cv::Mat hanning_2d;

    if (rows == 1 && cols == 1) {
        hanning_2d = cv::Mat::ones(1, 1, CV_32F);
    } else if (rows == 1) { 
        if (cols > 1) cv::createHanningWindow(hanning_2d, cv::Size(cols, 1), CV_32F);
        else hanning_2d = cv::Mat::ones(1, 1, CV_32F); 
    } else if (cols == 1) { 
        if (rows > 1) {
            cv::Mat h_col_temp; // Gunakan nama variabel sementara yang berbeda
            cv::createHanningWindow(h_col_temp, cv::Size(rows, 1), CV_32F); 
            hanning_2d = h_col_temp.t(); 
        } else {
             hanning_2d = cv::Mat::ones(1, 1, CV_32F); 
        }
    } else { // rows > 1 && cols > 1
        cv::Mat hanning_1d_row, hanning_1d_col_temp;
        cv::createHanningWindow(hanning_1d_row, cv::Size(cols, 1), CV_32F);
        cv::createHanningWindow(hanning_1d_col_temp, cv::Size(rows, 1), CV_32F); 
        cv::Mat hanning_1d_col = hanning_1d_col_temp.t(); 
        hanning_2d = hanning_1d_col * hanning_1d_row; 
    }
    return hanning_2d;
}

cv::Mat prepare_gray_image_cv(const cv::Mat &input_image)
{
    cv::Mat gray_image;
    if (input_image.channels() == 3)
    {
        cv::cvtColor(input_image, gray_image, cv::COLOR_BGR2GRAY);
    }
    else if (input_image.channels() == 4)
    {
        cv::cvtColor(input_image, gray_image, cv::COLOR_BGRA2GRAY);
    }
    else
    {
        gray_image = input_image.clone();
    }

    if (gray_image.type() != CV_8U)
    {
        cv::Mat temp;
        cv::normalize(gray_image, temp, 0, 255, cv::NORM_MINMAX);
        temp.convertTo(gray_image, CV_8U);
    }
    return gray_image;
}

std::vector<cv::Mat> build_gaussian_pyramid_cv(const cv::Mat& image_gray, int num_levels) {
    std::vector<cv::Mat> pyramid;
    if (image_gray.empty() || num_levels <= 0) return pyramid; // Handle input tidak valid

    pyramid.push_back(image_gray.clone());
    cv::Mat current_level = image_gray.clone();
    for (int i = 1; i < num_levels; ++i) {
        if (current_level.rows < 2 || current_level.cols < 2) break; // Stop jika sudah terlalu kecil untuk pyrDown
        cv::Mat next_level;
        cv::pyrDown(current_level, next_level);
        if (next_level.empty() || next_level.rows < 1 || next_level.cols < 1) break; // Stop jika hasil pyrDown terlalu kecil/kosong
        pyramid.push_back(next_level);
        current_level = next_level;
    }
    if (!pyramid.empty()) { // Hanya reverse jika tidak kosong
      std::reverse(pyramid.begin(), pyramid.end());
    }
    return pyramid;
}


cv::Mat estimate_displacement_for_tile(
    const cv::Mat &base_level_tile_content,
    const cv::Mat &target_level_img,
    int tile_global_x_start, int tile_global_y_start,
    int tile_processing_w, int tile_processing_h,
    double init_dx, double init_dy)
{

    cv::Mat M_total = (cv::Mat_<double>(2, 3) << 1, 0, -init_dx, 0, 1, -init_dy);

    const int MIN_DIM_FOR_PHASE_CORR = 4;

    if (tile_processing_w < MIN_DIM_FOR_PHASE_CORR || tile_processing_h < MIN_DIM_FOR_PHASE_CORR || base_level_tile_content.empty())
    {
        return M_total;
    }

    cv::Rect target_roi(tile_global_x_start, tile_global_y_start, tile_processing_w, tile_processing_h);
    target_roi = target_roi & cv::Rect(0, 0, target_level_img.cols, target_level_img.rows);

    if (target_roi.width < MIN_DIM_FOR_PHASE_CORR || target_roi.height < MIN_DIM_FOR_PHASE_CORR)
    {
        return M_total;
    }
    cv::Mat target_level_tile_original = target_level_img(target_roi).clone();

    if (base_level_tile_content.rows < MIN_DIM_FOR_PHASE_CORR || base_level_tile_content.cols < MIN_DIM_FOR_PHASE_CORR)
    {
        return M_total;
    }

    if (target_level_tile_original.size() != base_level_tile_content.size())
    {
        return M_total;
    }

    cv::Mat target_level_tile_to_correlate_float;
    target_level_tile_original.convertTo(target_level_tile_to_correlate_float, CV_32F);

    if (std::abs(init_dx) > 1e-6 || std::abs(init_dy) > 1e-6)
    {
        cv::Mat M_guess = (cv::Mat_<double>(2, 3) << 1, 0, -init_dx, 0, 1, -init_dy);
        cv::Mat pre_warped_target_tile;

        if (!target_level_tile_to_correlate_float.empty() && target_level_tile_to_correlate_float.rows > 1 && target_level_tile_to_correlate_float.cols > 1)
        {
            cv::warpAffine(target_level_tile_to_correlate_float, pre_warped_target_tile, M_guess,
                           target_level_tile_to_correlate_float.size(), cv::INTER_LINEAR, cv::BORDER_REFLECT_101);
            target_level_tile_to_correlate_float = pre_warped_target_tile;
        }
    }

    cv::Mat base_level_tile_float;
    base_level_tile_content.convertTo(base_level_tile_float, CV_32F);

    if (base_level_tile_float.rows <= 1 || base_level_tile_float.cols <= 1 ||
        target_level_tile_to_correlate_float.rows <= 1 || target_level_tile_to_correlate_float.cols <= 1)
    {
        return M_total;
    }

    cv::Point2d shift_cv;
    try
    {
        shift_cv = cv::phaseCorrelate(base_level_tile_float, target_level_tile_to_correlate_float);
    }
    catch (const cv::Exception &e)
    {
        return M_total;
    }

    double refined_dx = shift_cv.x;
    double refined_dy = shift_cv.y;

    double total_dx = init_dx + refined_dx;
    double total_dy = init_dy + refined_dy;

    M_total = (cv::Mat_<double>(2, 3) << 1, 0, -total_dx, 0, 1, -total_dy);
    return M_total;
}
std::map<std::pair<int, int>, cv::Mat> compute_tile_displacements_multiscale_cv(
    const cv::Mat &base_gray_full_res_uint8,
    const cv::Mat &target_gray_full_res_uint8,
    int tile_w_orig, int tile_h_orig, float overlap_percent,
    int num_levels, bool use_multi_core)
{

    std::vector<cv::Mat> base_pyr = build_gaussian_pyramid_cv(base_gray_full_res_uint8, num_levels);
    std::vector<cv::Mat> target_pyr = build_gaussian_pyramid_cv(target_gray_full_res_uint8, num_levels);

    std::map<std::pair<int, int>, cv::Mat> current_level_displacement_matrices; // Key: (tile_i, tile_j), Value: M matrix

    if (base_pyr.empty() || target_pyr.empty() || base_pyr.size() != target_pyr.size())
    {
        std::cerr << "Warning: Could not build consistent pyramids. Skipping multiscale displacement." << std::endl;
        return current_level_displacement_matrices;
    }

    int actual_num_levels = base_pyr.size();

    for (int level_idx = 0; level_idx < actual_num_levels; ++level_idx)
    {
        cv::Mat base_level_img = base_pyr[level_idx];
        cv::Mat target_level_img = target_pyr[level_idx];

        double scale_to_original = static_cast<double>(1 << (actual_num_levels - 1 - level_idx));

        int current_tile_w = std::max(16, static_cast<int>(std::round(tile_w_orig / scale_to_original)));
        int current_tile_h = std::max(16, static_cast<int>(std::round(tile_h_orig / scale_to_original)));
        int current_overlap_px_w = static_cast<int>(std::round(current_tile_w * overlap_percent));
        int current_overlap_px_h = static_cast<int>(std::round(current_tile_h * overlap_percent));
        current_overlap_px_w = std::min(current_overlap_px_w, current_tile_w - 1);
        current_overlap_px_h = std::min(current_overlap_px_h, current_tile_h - 1);
        current_overlap_px_w = std::max(0, current_overlap_px_w);
        current_overlap_px_h = std::max(0, current_overlap_px_h);

        int img_h_level = base_level_img.rows;
        int img_w_level = base_level_img.cols;

        if (img_h_level < current_tile_h / 2 || img_w_level < current_tile_w / 2)
        {
            std::map<std::pair<int, int>, cv::Mat> propagated_matrices;
            if (level_idx > 0)
            {
                for (const auto &pair_entry : current_level_displacement_matrices)
                {
                    cv::Mat prev_M = pair_entry.second.clone();
                    prev_M.at<double>(0, 2) *= 2.0; // dx
                    prev_M.at<double>(1, 2) *= 2.0; // dy
                    propagated_matrices[pair_entry.first] = prev_M;
                }
            }
            current_level_displacement_matrices = propagated_matrices;
            continue;
        }

        int step_w_level = std::max(1, current_tile_w - current_overlap_px_w);
        int step_h_level = std::max(1, current_tile_h - current_overlap_px_h);

        int num_tiles_x_level = (img_w_level > current_tile_w) ? static_cast<int>(std::ceil(static_cast<double>(img_w_level) / step_w_level)) : 1;
        int num_tiles_y_level = (img_h_level > current_tile_h) ? static_cast<int>(std::ceil(static_cast<double>(img_h_level) / step_h_level)) : 1;
        num_tiles_x_level = std::max(1, num_tiles_x_level);
        num_tiles_y_level = std::max(1, num_tiles_y_level);

        std::vector<std::tuple<int, int, double, double>> tile_params_for_level;
        for (int i = 0; i < num_tiles_x_level; ++i)
        {
            for (int j = 0; j < num_tiles_y_level; ++j)
            {
                double init_dx_level = 0.0, init_dy_level = 0.0;
                std::pair<int, int> tile_key = {i, j};
                if (level_idx > 0 && current_level_displacement_matrices.count(tile_key))
                {
                    const cv::Mat &prev_M = current_level_displacement_matrices.at(tile_key);
                    init_dx_level = -prev_M.at<double>(0, 2) * 2.0; // M stores -dx
                    init_dy_level = -prev_M.at<double>(1, 2) * 2.0; // M stores -dy
                }
                tile_params_for_level.emplace_back(i, j, init_dx_level, init_dy_level);
            }
        }

        std::map<std::pair<int, int>, cv::Mat> next_level_displacement_matrices_temp;

        struct TileResult
        {
            std::pair<int, int> key;
            cv::Mat M;
        };
        std::vector<TileResult> results_this_level(tile_params_for_level.size());

#pragma omp parallel for if (use_multi_core && tile_params_for_level.size() > 1) schedule(dynamic)
        for (size_t k = 0; k < tile_params_for_level.size(); ++k)
        {
            int tile_idx_i = std::get<0>(tile_params_for_level[k]);
            int tile_idx_j = std::get<1>(tile_params_for_level[k]);
            double init_dx_level = std::get<2>(tile_params_for_level[k]);
            double init_dy_level = std::get<3>(tile_params_for_level[k]);
            std::pair<int, int> tile_key = {tile_idx_i, tile_idx_j};

            int x_coord_grid = tile_idx_i * step_w_level;
            int y_coord_grid = tile_idx_j * step_h_level;

            int tile_global_x_start = std::max(0, x_coord_grid);
            int tile_global_y_start = std::max(0, y_coord_grid);
            int tile_global_x_end = std::min(img_w_level, tile_global_x_start + current_tile_w);
            int tile_global_y_end = std::min(img_h_level, tile_global_y_start + current_tile_h);

            int tile_processing_w = tile_global_x_end - tile_global_x_start;
            int tile_processing_h = tile_global_y_end - tile_global_y_start;

            cv::Mat M_level_tile;
            if (tile_processing_w > 0 && tile_processing_h > 0)
            {
                cv::Rect base_roi(tile_global_x_start, tile_global_y_start, tile_processing_w, tile_processing_h);
                cv::Mat base_tile_content = base_level_img(base_roi); // This is a view, be careful if modifying

                M_level_tile = estimate_displacement_for_tile(
                    base_tile_content, target_level_img,
                    tile_global_x_start, tile_global_y_start,
                    tile_processing_w, tile_processing_h,
                    init_dx_level, init_dy_level);
            }
            else
            { // Fallback if tile is zero-sized
                M_level_tile = (cv::Mat_<double>(2, 3) << 1, 0, -init_dx_level, 0, 1, -init_dy_level);
            }
            results_this_level[k] = {tile_key, M_level_tile};
        }

        for (const auto &res : results_this_level)
        {
            next_level_displacement_matrices_temp[res.key] = res.M;
        }
        current_level_displacement_matrices = next_level_displacement_matrices_temp;
    }
    return current_level_displacement_matrices;
}

std::pair<cv::Mat, cv::Mat> process_single_tile_for_blending_cv(
    const cv::Mat &base_gray_enhanced,
    const cv::Mat &target_gray_enhanced,
    const cv::Mat &target_image_to_warp,
    int tile_idx_i, int tile_idx_j,
    int tile_w, int tile_h,
    int overlap_px_w, int overlap_px_h,
    int img_h, int img_w,
    double init_dx, double init_dy)
{

    cv::Mat M_final_for_tile = (cv::Mat_<double>(2, 3) << 1, 0, -init_dx, 0, 1, -init_dy); // Default

    int step_w = std::max(1, tile_w - overlap_px_w);
    int step_h = std::max(1, tile_h - overlap_px_h);

    int x_coord_grid = tile_idx_i * step_w;
    int y_coord_grid = tile_idx_j * step_h;
    int current_tile_global_x_start = std::max(0, x_coord_grid);
    int current_tile_global_y_start = std::max(0, y_coord_grid);
    int current_tile_global_x_end = std::min(img_w, current_tile_global_x_start + tile_w);
    int current_tile_global_y_end = std::min(img_h, current_tile_global_y_start + tile_h);

    int current_tile_processing_w = current_tile_global_x_end - current_tile_global_x_start;
    int current_tile_processing_h = current_tile_global_y_end - current_tile_global_y_start;

    cv::Mat empty_mat; // For returning on failure

    if (current_tile_processing_w <= 0 || current_tile_processing_h <= 0)
    {
        return {empty_mat, M_final_for_tile};
    }

    cv::Rect tile_roi_global(current_tile_global_x_start, current_tile_global_y_start, current_tile_processing_w, current_tile_processing_h);
    cv::Mat tile_target_content_to_warp_current = target_image_to_warp(tile_roi_global).clone();

    if (tile_target_content_to_warp_current.empty())
    {
        return {empty_mat, M_final_for_tile};
    }

    if (current_tile_processing_w <= std::max(1, overlap_px_w / 2) ||
        current_tile_processing_h <= std::max(1, overlap_px_h / 2) ||
        current_tile_processing_w < 16 || current_tile_processing_h < 16)
    {

        cv::Mat hanning_win_skip = create_hanning_window_2d_cv(tile_target_content_to_warp_current.rows, tile_target_content_to_warp_current.cols);
        cv::Mat windowed_tile_skip_float;
        tile_target_content_to_warp_current.convertTo(windowed_tile_skip_float, CV_32F);

        if (tile_target_content_to_warp_current.channels() > 1)
        {
            std::vector<cv::Mat> channels(tile_target_content_to_warp_current.channels());
            for (int c = 0; c < tile_target_content_to_warp_current.channels(); ++c)
                channels[c] = hanning_win_skip.clone();
            cv::merge(channels, hanning_win_skip);
        }

        cv::multiply(windowed_tile_skip_float, hanning_win_skip, windowed_tile_skip_float);

        if (std::abs(init_dx) > 1e-6 || std::abs(init_dy) > 1e-6)
        {
            cv::Mat warped_content_skip;
            try
            {
                cv::warpAffine(tile_target_content_to_warp_current, warped_content_skip, M_final_for_tile,
                               tile_target_content_to_warp_current.size(), cv::INTER_AREA, cv::BORDER_REFLECT_101);
                warped_content_skip.convertTo(windowed_tile_skip_float, CV_32F);
                cv::multiply(windowed_tile_skip_float, hanning_win_skip, windowed_tile_skip_float);
            }
            catch (...)
            {
            } // Ignore warp error, use original tile with Hanning
        }
        return {windowed_tile_skip_float, M_final_for_tile};
    }

    // Normal processing path
    cv::Mat tile_base_for_phase = base_gray_enhanced(tile_roi_global);              // View
    cv::Mat tile_target_for_phase_original = target_gray_enhanced(tile_roi_global); // View

    if (tile_base_for_phase.empty() || tile_target_for_phase_original.empty() ||
        tile_base_for_phase.size() != tile_target_for_phase_original.size())
    {
        // Fallback: similar to small tile skip
        cv::Mat hanning_win_fallback = create_hanning_window_2d_cv(tile_target_content_to_warp_current.rows, tile_target_content_to_warp_current.cols);
        cv::Mat windowed_tile_fallback_float;
        tile_target_content_to_warp_current.convertTo(windowed_tile_fallback_float, CV_32F);

        if (tile_target_content_to_warp_current.channels() > 1)
        {
            std::vector<cv::Mat> channels(tile_target_content_to_warp_current.channels());
            for (int c = 0; c < tile_target_content_to_warp_current.channels(); ++c)
                channels[c] = hanning_win_fallback.clone();
            cv::merge(channels, hanning_win_fallback);
        }
        cv::multiply(windowed_tile_fallback_float, hanning_win_fallback, windowed_tile_fallback_float);
        return {windowed_tile_fallback_float, M_final_for_tile};
    }

    cv::Mat M_from_phase_corr = estimate_displacement_for_tile(
        tile_base_for_phase, target_gray_enhanced, // Pass full target gray for extraction robustness if needed
        current_tile_global_x_start, current_tile_global_y_start,
        current_tile_processing_w, current_tile_processing_h,
        init_dx, init_dy);

    M_final_for_tile = M_from_phase_corr;

    cv::Mat warped_tile_target_content_float;
    cv::Mat tile_target_content_to_warp_float;
    tile_target_content_to_warp_current.convertTo(tile_target_content_to_warp_float, CV_32F);

    bool perform_final_warp = (std::abs(M_final_for_tile.at<double>(0, 2)) > 1e-6 || // if -dx is non-zero
                               std::abs(M_final_for_tile.at<double>(1, 2)) > 1e-6);  // if -dy is non-zero

    if (perform_final_warp)
    {
        try
        {
            cv::Mat temp_warped;
            cv::warpAffine(tile_target_content_to_warp_float, temp_warped, M_final_for_tile,
                           tile_target_content_to_warp_float.size(), cv::INTER_AREA, cv::BORDER_REFLECT_101);
            warped_tile_target_content_float = temp_warped;
        }
        catch (...)
        {
            warped_tile_target_content_float = tile_target_content_to_warp_float.clone(); // fallback to unwarped
        }
    }
    else
    {
        warped_tile_target_content_float = tile_target_content_to_warp_float.clone();
    }

    if (warped_tile_target_content_float.empty())
    { // Should not happen if tile_target_content_to_warp_current was valid
        return {empty_mat, M_final_for_tile};
    }

    // Apply Hanning window
    cv::Mat hanning_win = create_hanning_window_2d_cv(warped_tile_target_content_float.rows, warped_tile_target_content_float.cols);
    if (warped_tile_target_content_float.channels() > 1)
    {
        std::vector<cv::Mat> channels_vec;
        for (int c = 0; c < warped_tile_target_content_float.channels(); ++c)
        {
            channels_vec.push_back(hanning_win.clone());
        }
        cv::Mat hanning_win_multi_channel;
        cv::merge(channels_vec, hanning_win_multi_channel);
        cv::multiply(warped_tile_target_content_float, hanning_win_multi_channel, warped_tile_target_content_float);
    }
    else
    {
        cv::multiply(warped_tile_target_content_float, hanning_win, warped_tile_target_content_float);
    }

    return {warped_tile_target_content_float, M_final_for_tile};
}

extern "C"
{

    // Main function to be called from Python
    // Parameters:
    // - base_image_data, target_image_data: raw pixel data (unsigned char*)
    // - rows, cols, channels: dimensions of the images
    // - config: tile_size_w, tile_size_h, overlap_percent, num_pyramid_levels, use_multi_core_omp
    // - aligned_target_image_data: output buffer for the aligned image (pre-allocated by Python)
    // - M_matrices_data: output buffer for transformation matrices (6 doubles per tile: m00,m01,m02,m10,m11,m12)
    // - tile_indices_i_data, tile_indices_j_data: output buffers for tile indices
    // - max_tiles_output: capacity of the M_matrices and tile_indices arrays
    // - num_tiles_written: pointer to int, will be filled with the number of tiles for which M was stored
    // Returns an int status code (0 for success, -1 for error)
    int align_local_cpp(
        const unsigned char *base_image_data, int base_rows, int base_cols, int base_channels,
        const unsigned char *target_image_data, int target_rows, int target_cols, int target_channels,
        int tile_size_w, int tile_size_h, float overlap_percent_in, int num_pyramid_levels,
        bool use_multi_core_omp,
        unsigned char *aligned_target_image_data, // Output
        double *M_matrices_data,                  // Output (flattened 2x3 matrices)
        int *tile_indices_i_data,                 // Output
        int *tile_indices_j_data,                 // Output
        int max_tiles_output,
        int *num_tiles_written_ptr)
    {
        if (!base_image_data || !target_image_data || !aligned_target_image_data ||
            !M_matrices_data || !tile_indices_i_data || !tile_indices_j_data || !num_tiles_written_ptr)
        {
            std::cerr << "Error: Null pointer passed to align_local_cpp." << std::endl;
            return -1;
        }

        *num_tiles_written_ptr = 0; // Initialize output count

        // Determine Mat type based on channels
        int base_type = (base_channels == 3) ? CV_8UC3 : (base_channels == 1) ? CV_8UC1
                                                     : (base_channels == 4)   ? CV_8UC4
                                                                              : -1;
        int target_type = (target_channels == 3) ? CV_8UC3 : (target_channels == 1) ? CV_8UC1
                                                         : (target_channels == 4)   ? CV_8UC4
                                                                                    : -1;

        if (base_type == -1 || target_type == -1)
        {
            std::cerr << "Error: Unsupported number of channels." << std::endl;
            return -2;
        }

        // Wrap raw data with cv::Mat. NOTE: This doesn't copy data.
        // Ensure data is const correct for input. For output, it's non-const.
        cv::Mat base_image_orig(base_rows, base_cols, base_type, const_cast<unsigned char *>(base_image_data));
        cv::Mat target_image_orig(target_rows, target_cols, target_type, const_cast<unsigned char *>(target_image_data));
        cv::Mat aligned_target_stitched_output(target_rows, target_cols, target_type, aligned_target_image_data);

        if (base_image_orig.empty() || target_image_orig.empty())
        {
            std::cerr << "Error: Base or target image is empty after Mat creation." << std::endl;
            return -3;
        }
        if (base_image_orig.size() != target_image_orig.size() || base_image_orig.type() != target_image_orig.type())
        {
            std::cerr << "Error: Base and target images must have same dimensions and type for this simplified example." << std::endl;
            // In a real scenario, you might handle resizing or type conversion.
            // For now, copy target to output if sizes differ, and return.
            if (target_image_orig.size() == aligned_target_stitched_output.size() && target_image_orig.type() == aligned_target_stitched_output.type())
            {
                target_image_orig.copyTo(aligned_target_stitched_output);
            }
            return -4;
        }

        // --- Config variables ---
        float overlap_percent = std::max(0.01f, std::min(overlap_percent_in, 0.9f)); // Clip overlap

        // --- Prepare gray images and enhance ---
        cv::Mat base_gray_prepared = prepare_gray_image_cv(base_image_orig);
        cv::Mat target_gray_prepared = prepare_gray_image_cv(target_image_orig);

        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(2.0, cv::Size(8, 8));
        cv::Mat base_gray_enhanced, target_gray_enhanced;
        try
        {
            clahe->apply(base_gray_prepared, base_gray_enhanced);
            clahe->apply(target_gray_prepared, target_gray_enhanced);
        }
        catch (const cv::Exception &e)
        {
            std::cerr << "CLAHE application error: " << e.what() << ". Using original gray." << std::endl;
            base_gray_enhanced = base_gray_prepared.clone();
            target_gray_enhanced = target_gray_prepared.clone();
        }

        // --- Coarse-to-fine displacement estimation ---
        std::cout << "  C++: Starting coarse-to-fine displacement estimation with " << num_pyramid_levels << " levels..." << std::endl;
        std::map<std::pair<int, int>, cv::Mat> displacement_matrices_map =
            compute_tile_displacements_multiscale_cv(
                base_gray_enhanced, target_gray_enhanced,
                tile_size_w, tile_size_h, overlap_percent,
                num_pyramid_levels, use_multi_core_omp);
        std::cout << "  C++: Coarse-to-fine estimation finished. Found " << displacement_matrices_map.size() << " initial M matrices." << std::endl;

        // --- Full-resolution alignment and stitching ---
        int img_h_orig = base_image_orig.rows;
        int img_w_orig = base_image_orig.cols;

        int overlap_px_w = static_cast<int>(tile_size_w * overlap_percent);
        int overlap_px_h = static_cast<int>(tile_size_h * overlap_percent);
        overlap_px_w = std::min(std::max(0, overlap_px_w), tile_size_w - 1);
        overlap_px_h = std::min(std::max(0, overlap_px_h), tile_size_h - 1);

        cv::Mat aligned_target_stitched_float;
        if (target_channels > 1)
        {
            aligned_target_stitched_float = cv::Mat::zeros(img_h_orig, img_w_orig, CV_32FC(target_channels));
        }
        else
        {
            aligned_target_stitched_float = cv::Mat::zeros(img_h_orig, img_w_orig, CV_32FC1);
        }
        cv::Mat weight_sum_map = cv::Mat::zeros(img_h_orig, img_w_orig, CV_32F);

        int step_w = std::max(1, tile_size_w - overlap_px_w);
        int step_h = std::max(1, tile_size_h - overlap_px_h);

        int num_tiles_x = (img_w_orig > tile_size_w) ? static_cast<int>(std::ceil(static_cast<double>(img_w_orig) / step_w)) : 1;
        int num_tiles_y = (img_h_orig > tile_size_h) ? static_cast<int>(std::ceil(static_cast<double>(img_h_orig) / step_h)) : 1;
        num_tiles_x = std::max(1, num_tiles_x);
        num_tiles_y = std::max(1, num_tiles_y);

        struct TileToProcessFullRes
        {
            int i, j;
            double init_dx, init_dy;
        };
        std::vector<TileToProcessFullRes> tiles_for_final_pass;
        for (int i = 0; i < num_tiles_x; ++i)
        {
            for (int j = 0; j < num_tiles_y; ++j)
            {
                double initial_dx = 0.0, initial_dy = 0.0;
                std::pair<int, int> tile_key_map = {i, j}; // Assuming tile indices for map match grid indices

                if (displacement_matrices_map.count(tile_key_map))
                {
                    const cv::Mat &M_coarse = displacement_matrices_map.at(tile_key_map);
                    // M stores -dx, -dy. Need to scale if pyramid levels were involved.
                    // The current C++ displacement_matrices_map returns M for the *finest pyramid level*.
                    // If num_pyramid_levels > 1, the displacement is for level 0 of pyramid (smallest one in build_gaussian_pyramid_cv)
                    // So, scale it up to full resolution. Smallest level had scale_to_original = 2^(actual_num_levels-1)
                    // The displacement is for (base_pyr[0]).size().
                    // The `scale_to_original` in _compute_tile_displacements_multiscale was for `level_idx`
                    // Let's assume for now the displacements in displacement_matrices_map are roughly at the original scale
                    // or that they are relative and phase correlation at full res will refine them.
                    // This part might need careful adjustment based on how displacements are scaled and propagated.
                    // For simplicity, let's use them directly as init_dx, init_dy for full-res refinement.
                    initial_dx = -M_coarse.at<double>(0, 2);
                    initial_dy = -M_coarse.at<double>(1, 2);
                }
                tiles_for_final_pass.push_back({i, j, initial_dx, initial_dy});
            }
        }

        if (tiles_for_final_pass.empty())
        {
            std::cerr << "No tiles to process in final pass." << std::endl;
            target_image_orig.copyTo(aligned_target_stitched_output); // Copy original if no processing
            return -5;
        }

        struct FinalTileResult
        {
            cv::Mat windowed_tile_float;
            cv::Mat M_loc;
            int y_start_global, x_start_global;
            int tile_idx_i_orig, tile_idx_j_orig; // For storing M
        };
        std::vector<FinalTileResult> final_results_vector(tiles_for_final_pass.size());

#pragma omp parallel for if (use_multi_core_omp && tiles_for_final_pass.size() > 1) schedule(dynamic)
        for (size_t k = 0; k < tiles_for_final_pass.size(); ++k)
        {
            const auto &params = tiles_for_final_pass[k];
            std::pair<cv::Mat, cv::Mat> tile_processing_result = process_single_tile_for_blending_cv(
                base_gray_enhanced, target_gray_enhanced, target_image_orig, /* pass original target for warping */
                params.i, params.j,
                tile_size_w, tile_size_h, overlap_px_w, overlap_px_h,
                img_h_orig, img_w_orig,
                params.init_dx, params.init_dy);

            // Calculate global start for this tile based on its index and step
            int x_coord_grid = params.i * step_w;
            int y_coord_grid = params.j * step_h;

            final_results_vector[k] = {
                tile_processing_result.first,  // windowed_tile_float
                tile_processing_result.second, // M_loc
                std::max(0, y_coord_grid),
                std::max(0, x_coord_grid),
                params.i, params.j};
        }

        int current_M_idx = 0;
        for (const auto &res : final_results_vector)
        {
            if (res.windowed_tile_float.empty())
                continue;

            int y_start_g = res.y_start_global;
            int x_start_g = res.x_start_global;
            int h_tile_proc = res.windowed_tile_float.rows;
            int w_tile_proc = res.windowed_tile_float.cols;

            cv::Rect target_roi_rect(x_start_g, y_start_g, w_tile_proc, h_tile_proc);
            // Ensure ROI is within the bounds of the main image
            target_roi_rect &= cv::Rect(0, 0, img_w_orig, img_h_orig);

            if (target_roi_rect.width <= 0 || target_roi_rect.height <= 0)
                continue;

            cv::Mat tile_to_place = res.windowed_tile_float(cv::Rect(0, 0, target_roi_rect.width, target_roi_rect.height));
            cv::Mat target_buffer_roi = aligned_target_stitched_float(target_roi_rect);
            cv::Mat weight_map_roi = weight_sum_map(target_roi_rect);

            if (target_buffer_roi.size() != tile_to_place.size() || target_buffer_roi.type() != tile_to_place.type())
            {
                // std::cerr << "ROI size/type mismatch during blending. Skipping tile." << std::endl;
                continue;
            }

            cv::add(target_buffer_roi, tile_to_place, target_buffer_roi);

            cv::Mat hanning_for_weight = create_hanning_window_2d_cv(target_roi_rect.height, target_roi_rect.width);
            cv::add(weight_map_roi, hanning_for_weight, weight_map_roi);

            // Store M matrix if space available
            if (res.M_loc.cols == 3 && res.M_loc.rows == 2 && current_M_idx < max_tiles_output)
            {
                M_matrices_data[current_M_idx * 6 + 0] = res.M_loc.at<double>(0, 0);
                M_matrices_data[current_M_idx * 6 + 1] = res.M_loc.at<double>(0, 1);
                M_matrices_data[current_M_idx * 6 + 2] = res.M_loc.at<double>(0, 2);
                M_matrices_data[current_M_idx * 6 + 3] = res.M_loc.at<double>(1, 0);
                M_matrices_data[current_M_idx * 6 + 4] = res.M_loc.at<double>(1, 1);
                M_matrices_data[current_M_idx * 6 + 5] = res.M_loc.at<double>(1, 2);
                tile_indices_i_data[current_M_idx] = res.tile_idx_i_orig;
                tile_indices_j_data[current_M_idx] = res.tile_idx_j_orig;
                current_M_idx++;
            }
        }
        *num_tiles_written_ptr = current_M_idx;

        // Normalize by weight map
        cv::Mat denominator;
        if (target_channels > 1)
        {
            std::vector<cv::Mat> weight_sum_map_channels(target_channels);
            for (int c = 0; c < target_channels; ++c)
                weight_sum_map_channels[c] = weight_sum_map.clone();
            cv::merge(weight_sum_map_channels, denominator);
        }
        else
        {
            denominator = weight_sum_map;
        }

        // Avoid division by zero: set very small weights to 1.0
        cv::Mat below_thresh_mask = denominator < 1e-6;
        denominator.setTo(1.0, below_thresh_mask); // Set elements where mask is true to 1.0

        cv::divide(aligned_target_stitched_float, denominator, aligned_target_stitched_float);

        // Convert to original uchar type for output
        double min_val_out = 0;
        double max_val_out = 255; // Assuming CV_8U from target_image_orig.type()
        // Add proper handling if target_image_orig.depth() is CV_16U etc.
        if (target_image_orig.depth() == CV_16U)
            max_val_out = 65535;

        aligned_target_stitched_float.convertTo(aligned_target_stitched_output, target_image_orig.type(), 1.0, 0.0);

        std::cout << "  C++: Finished full-resolution alignment. Final image generated." << std::endl;
        return 0; // Success
    }
} // extern "C"