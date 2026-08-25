# Taichi Algorithm Package
# Reusable GPU-accelerated functions
# API Style: OpenCV-like (ta.resize, ta.median, ta.sobel, etc.)

import numpy as np
import os
import importlib
import builtins
from taichi_vision.config import AOT_MODE

ti = None
if AOT_MODE == "0":
    try:
        ti = importlib.import_module("taichi")
    except ImportError:
        pass

# --- Core Imports ---
from . import common
from . import aot_wrapper

if AOT_MODE == "1":
    from .aot_wrapper import *
else:
    from .common import (
        split,
        merge,
        extract_channel,
        insert_channel,
        copy,
    )

    # --- Underlying Implementations ---
    from .interpolation.bilinear_interpolation import (
        bilinear_resize,
        sample_at_bilinear,
    )
    from .interpolation.nearest_interpolation import nearest_resize
    from .interpolation.bicubic_interpolation import (
        bicubic_resize,
        sample_at_bicubic,
        sample_at,
        cubic_hermite,
    )
    from .smoothing.box_filter import box_filter, box_filter_2d
    from .smoothing.median_filter import median_filter
    from .smoothing.gaussian import gaussian_blur as _gaussian_blur_impl
    from .math_ops.gradients import sobel as _sobel_impl
    from .math_ops.gradients import laplacian as _laplacian_impl
    from .alignment.ransac import ransac_flow_cleanup
    from .smoothing.bilateral_grid import bilateral_grid_filter
    from .pyramid.pyramid import (
        build_image_pyramid,
        build_image_pyramid_gpu,
        upsample_flow,
    )
    from .alignment.phase_correlation import phase_correlation
    from .pyramid.fft import fft2, ifft2
    from .alignment.ncc import zncc, match_template, global_translate_zncc
    from .interpolation.remap import remap
    from .demosaicing.Hamilton_demosaice import hamilton, hamilton_demosaic
    from .demosaicing.arm_demosaice import arm, arm_demosaic
    from .demosaicing.mlri_admm_demosaice import (
        mlri_admm,
        mlri_admm_demosaic,
        mlri_admm_demosaic_1channel,
        mlri_admm_demosaic_half_res,
        mlri_admm_demosaic_rgb_half_res,
        mlri_admm_demosaic_3channel,
    )
    from .alignment.mtb import align_mtb
    from .image_processing.enhance_image import enhance_grayscale
    from .image_processing.color_convert import (
        cvtColor_extended,
        COLOR_BGR2HSV,
        COLOR_HSV2BGR,
        COLOR_BGR2LAB,
        COLOR_LAB2BGR,
        COLOR_BGR2YCrCb,
        COLOR_YCrCb2BGR,
    )
    from .image_processing.otsu import (
        otsu_threshold,
        THRESH_BINARY,
        THRESH_BINARY_INV,
        THRESH_OTSU,
    )
    from .smoothing.guided_filter import guided_filter
    from .image_processing.clahe import clahe
    from .image_processing.canny import canny
    from .image_processing.hough import hough_lines, hough_lines_with_canny
    from .denoising.nlm import non_local_means
    from .denoising.bm3d import hfcd_denoise, build_dct_matrix
    from .image_processing.inpaint import inpaint, INPAINT_TELEA, INPAINT_NS
    from .image_processing.seamless_clone import (
        seamless_clone,
        NORMAL_CLONE,
        MIXED_CLONE,
        MONOCHROME_TRANSFER,
    )
    from .optical_flow.farneback_flow import farneback_flow
    from .optical_flow.lucas_kanade import calcOpticalFlowPyrLK as lucas_kanade_flow
    from .image_processing.morphology import dilate, erode
    from .image_processing.filter2d import filter2d
    from .image_processing.normalize import (
        normalize,
        NORM_INF,
        NORM_L1,
        NORM_L2,
        NORM_MINMAX,
    )
    from .image_processing.copy_make_border import (
        copy_make_border,
        BORDER_CONSTANT,
        BORDER_REFLECT_101,
        BORDER_REPLICATE,
    )
    from .image_processing.threshold import (
        threshold,
        THRESH_BINARY,
        THRESH_BINARY_INV,
        THRESH_TRUNC,
        THRESH_TOZERO,
        THRESH_TOZERO_INV,
        THRESH_OTSU,
    )
    from .math_ops.ssim import ssim
    from .image_processing.histogram import histogram as gpu_histogram
    from .image_processing.hdr_fusion import hdr_fuse, hdr_fuse_simple
    from .image_processing.tone_mapping import (
        reinhard_tone_map,
        srgb_gamma,
        local_tone_map,
        contrast_adjust,
        tone_map,
    )
    from .alignment.ransac import vsac_fundamental
    from .sfm.five_point_solver import solve_five_point
    from .sfm.cheirality_check import check_cheirality_minimal, check_cheirality_full
    from .sfm.triangulation import triangulate_adaptive
    from .sfm.feature_matching import bfmatcher_l2, bfmatcher_hamming
    from .sfm.bundle_adjustment import bundle_adjust_lm
    from .sfm.plane_sweep import plane_sweep_stereo, multi_view_plane_sweep
    from .sfm.point_cloud import (
        statistical_outlier_removal,
        radius_outlier_removal,
        voxel_downsample,
        estimate_normals,
        preprocess_point_cloud,
    )
    from .sfm.poisson_recon import poisson_reconstruct
    from .common import (
        svd_3x3_np,
        enforce_essential_np,
        hartley_normalize,
        denormalize_fundamental,
    )


    # The AOT image families live in their own small modules so each TCM can be
    # compiled and loaded independently.  Re-export them here as the normal
    # taichi_algorithm API when AOT mode is active; the JIT branch above keeps its
    # original implementations and signatures.
if AOT_MODE == "1":
    # Keep the concise demosaic entrypoints available from the canonical
    # algorithm package as well as from the taichi_aot compatibility facade.
    # Historical *_demosaic names remain exported for callers that still use
    # them; graph/TCM names are intentionally unchanged.
    from .aot_api import (
        hamilton,
        hamilton_demosaic,
        arm,
        arm_demosaic,
        dcb,
        dcb_demosaic,
        mlri_admm,
        mlri_admm_demosaic,
        mlri_admm_demosaic_1channel,
        mlri_admm_demosaic_half_res,
        mlri_admm_demosaic_rgb_half_res,
        mlri_admm_demosaic_3channel,
        demosaic,
        cvtColor_extended as _aot_cvtColor_extended,
        cvtColor as _aot_cvtColor,
        absdiff as _aot_absdiff,
        resize as _aot_resize,
        median_filter as _aot_median_filter,
        gaussian_blur as _aot_gaussian_blur,
        box_filter as _aot_box_filter,
        sobel as _aot_sobel,
        laplacian as _aot_laplacian,
        bilateral_grid_filter as _aot_bilateral_grid_filter,
        ransac_flow_cleanup as _aot_ransac_flow_cleanup,
        otsu_threshold_aot as _aot_otsu_threshold,
        guided_filter_aot as _aot_guided_filter,
        clahe_aot as _aot_clahe,
        canny_aot as _aot_canny,
        hough_lines_aot as _aot_hough_lines,
        seamless_clone_aot as _aot_seamless_clone,
        image_pyramid as _aot_image_pyramid,
        split_3ch as _aot_split_3ch,
        extract_channel as _aot_extract_channel,
        insert_channel as _aot_insert_channel,
        phase_correlation as _aot_phase_correlation,
        zncc as _aot_zncc,
        ncc_alignment as _aot_ncc_alignment,
        align_mtb as _aot_align_mtb,
        farneback_flow as _aot_farneback_flow,
        sfm_match_l2_aot as _aot_match_l2,
        vsac_fundamental_aot as _aot_vsac_fundamental,
        sfm_cheirality_minimal_aot as _aot_cheirality_minimal,
        sfm_cheirality_full_aot as _aot_cheirality_full,
        sfm_triangulate_adaptive_aot as _aot_triangulate_adaptive,
        sfm_reprojection_errors_aot as _aot_reprojection_errors,
        sfm_bundle_normal_equations_aot as _aot_bundle_normal_equations,
        hdr_fuse_aot as _aot_hdr_fuse,
        hdr_fusion_aot as _aot_hdr_fusion,
        tone_reinhard_aot as _aot_tone_reinhard,
        tone_srgb_aot as _aot_tone_srgb,
        tone_contrast_aot as _aot_tone_contrast,
        local_tone_map_aot as _aot_local_tone_map,
        tone_map_aot as _aot_tone_map,
        bundle_adjust_lm_aot as _aot_bundle_adjust_lm,
        plane_sweep_stereo_aot as _aot_plane_sweep_stereo,
        multi_view_plane_sweep_aot as _aot_multi_view_plane_sweep,
        point_cloud_preprocess_aot as _aot_point_cloud_preprocess,
        poisson_reconstruct_aot as _aot_poisson_reconstruct,
        sfm_radius_filter_aot as _aot_radius_filter,
        sfm_knn_distance_aot as _aot_knn_distance,
        sfm_sor_filter_aot as _aot_sor_filter,
        sfm_voxel_hash_aot as _aot_voxel_hash,
        sfm_normals_pca_aot as _aot_normals_pca,
        bm3d as _aot_bm3d,
        sample_at_bicubic as _aot_sample_at_bicubic,
        sample_at as _aot_sample_at,
        sample_at_bilinear as _aot_sample_at_bilinear,
    )

    def _aot_extended(name):
        # Lazy import keeps compiler workers from constructing the runtime
        # during package initialization.  The canonical implementation lives
        # under taichi_algorithm; taichi_aot only provides compatibility shims.
        from taichi_vision.taichi_algorithm.image_processing import extended_aot as _extended
        return getattr(_extended, name)

    def _aot_jpeg(name):
        from taichi_vision.taichi_algorithm.compression import jpeg_aot as _jpeg
        return getattr(_jpeg, name)

    def dilate(src, kernel=None, iterations=1):
        return _aot_extended("dilate_aot")(src, kernel=kernel, iterations=iterations)

    def erode(src, kernel=None, iterations=1):
        return _aot_extended("erode_aot")(src, kernel=kernel, iterations=iterations)

    def filter2d(src, kernel, border_mode="REFLECT_101"):
        return _aot_extended("filter2d_aot")(src, kernel, border_mode=border_mode)

    def normalize(src, min_val=0.0, max_val=1.0, norm_type="MINMAX"):
        return _aot_extended("normalize_aot")(src, alpha=min_val, beta=max_val, norm_type=norm_type)

    def copyMakeBorder(src, top, bottom, left, right, borderType=4, dst=None, value=0):
        result = _aot_extended("copy_make_border_aot")(src, top, bottom, left, right, border_type=borderType, value=value)
        if dst is not None:
            dst[...] = result
            return dst
        return result

    copy_make_border = copyMakeBorder

    def threshold(src, thresh, maxval=255, type=THRESH_BINARY):
        return _aot_extended("threshold_aot")(src, thresh=thresh, maxval=maxval, thresh_type=type)

    def ssim(img1, img2, window_size=11, data_range=None, k1=0.01, k2=0.03):
        return _aot_extended("ssim_aot")(img1, img2, window_size=window_size, data_range=data_range, k1=k1, k2=k2)

    def gpu_histogram(src, bins=256, range=(0, 256)):
        return _aot_extended("histogram_aot")(src, bins=bins, range=range)

    histogram = gpu_histogram

    def gaussian_window(*args, **kwargs):
        return _aot_extended("gaussian_window_aot")(*args, **kwargs)

    create_gaussian_window = gaussian_window

    def warp_affine(*args, **kwargs):
        return _aot_extended("warp_affine_aot")(*args, **kwargs)

    def joint_bilateral_guidance(*args, **kwargs):
        return _aot_extended("joint_bilateral_guidance_aot")(*args, **kwargs)

    def enhance_image(
        src,
        blur,
        lut,
        micro_contrast=2.93,
        clarity=0.0,
        noise_coring=0.0,
        dst=None,
        buffer_provider="pool",
        return_gpu=False,
    ):
        result = _aot_extended("enhance_image_aot")(
            src,
            blur,
            lut,
            micro_contrast=micro_contrast,
            clarity=clarity,
            noise_coring=noise_coring,
        )
        if return_gpu:
            # The current leaf is host-returning; accepting return_gpu here
            # would falsely advertise a GPU buffer, so fail closed.
            raise NotImplementedError(
                "AOT enhance_image currently exposes a host result only"
            )
        if dst is not None:
            dst[...] = result.to_numpy() if hasattr(result, "to_numpy") else result
            return dst
        return result

    enhance_grayscale = enhance_image

    def encode_grayscale_aot(*args, **kwargs):
        return _aot_jpeg("encode_grayscale_aot")(*args, **kwargs)

    def encode_rgb_aot(*args, **kwargs):
        return _aot_jpeg("encode_rgb_aot")(*args, **kwargs)

    def jpeg_encode_aot(*args, **kwargs):
        return _aot_jpeg("jpeg_encode_aot")(*args, **kwargs)

    # Keep every historical ``__all__`` symbol present in AOT mode.  The
    # symbols below are either direct target-qualified leaves/compositions or
    # explicit fail-closed placeholders when no equivalent AOT contract
    # exists.  In particular, we never import the JIT implementation here as
    # a silent CPU fallback.
    def cvtColor_extended(src, code, dst=None, buffer_provider="pool", return_gpu=False):
        """AOT color conversion with the historical ``dst``/pool arguments.

        ``buffer_provider`` is retained for source compatibility; native AOT
        allocation is owned by the graph/runtime and therefore does not accept
        an arbitrary Python pool object.  Supplying it remains harmless and is
        deliberately not routed to a host implementation.
        """
        result = _aot_cvtColor_extended(src, code, return_gpu=return_gpu)
        if dst is not None:
            dst[...] = result.to_numpy() if hasattr(result, "to_numpy") else result
            return dst
        return result

    def otsu_threshold(
        src,
        dst=None,
        thresh_type=THRESH_BINARY,
        max_val=255.0,
        num_bins=0,
        buffer_provider="pool",
        return_gpu=False,
    ):
        if int(num_bins or 0) not in (0, 256):
            raise NotImplementedError(
                "AOT Otsu uses the qualified 256-bin histogram; "
                "num_bins must be 0 or 256"
            )
        result = _aot_otsu_threshold(
            src,
            thresh_type=thresh_type,
            max_val=max_val,
            return_gpu=return_gpu,
        )
        if dst is not None:
            payload = result[1] if isinstance(result, tuple) else result
            dst[...] = payload.to_numpy() if hasattr(payload, "to_numpy") else payload
            return (result[0], dst) if isinstance(result, tuple) else dst
        return result

    def guided_filter(
        guide,
        src,
        radius=8,
        epsilon=1e-4,
        dst=None,
        buffer_provider="pool",
        return_gpu=False,
    ):
        result = _aot_guided_filter(
            guide, src, radius=radius, epsilon=epsilon, return_gpu=return_gpu
        )
        if dst is not None:
            dst[...] = result.to_numpy() if hasattr(result, "to_numpy") else result
            return dst
        return result

    def clahe(
        src,
        clip_limit=2.0,
        tile_grid_size=(8, 8),
        num_bins=0,
        dst=None,
        buffer_provider="pool",
        return_gpu=False,
    ):
        if int(num_bins or 0) not in (0, 256):
            raise NotImplementedError(
                "AOT CLAHE uses the qualified 256-bin histogram; "
                "num_bins must be 0 or 256"
            )
        result = _aot_clahe(
            src,
            clip_limit=clip_limit,
            tile_grid_size=tile_grid_size,
            return_gpu=return_gpu,
        )
        if dst is not None:
            dst[...] = result.to_numpy() if hasattr(result, "to_numpy") else result
            return dst
        return result

    def canny(
        src,
        low_threshold=50.0,
        high_threshold=150.0,
        aperture_size=3,
        dst=None,
        buffer_provider="pool",
        return_gpu=False,
    ):
        if int(aperture_size) != 3:
            raise NotImplementedError("AOT Canny supports the fixed 3x3 aperture")
        result = _aot_canny(
            src,
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            return_gpu=return_gpu,
        )
        if dst is not None:
            dst[...] = result.to_numpy() if hasattr(result, "to_numpy") else result
            return dst
        return result

    def hough_lines(
        edge_image,
        rho_resolution=1.0,
        theta_resolution=1.0,
        threshold=80,
        buffer_provider="pool",
        return_gpu=False,
    ):
        return _aot_hough_lines(
            edge_image,
            rho_resolution=rho_resolution,
            theta_resolution=theta_resolution,
            threshold=threshold,
            return_gpu=return_gpu,
        )

    def hough_lines_with_canny(
        src,
        low_threshold=50.0,
        high_threshold=150.0,
        rho_resolution=1.0,
        theta_resolution=1.0,
        vote_threshold=80,
        buffer_provider="pool",
        return_gpu=False,
        **kwargs,
    ):
        if kwargs:
            unexpected = ", ".join(sorted(kwargs))
            raise TypeError(f"unexpected hough_lines_with_canny arguments: {unexpected}")
        edges = _aot_canny(
            src,
            low_threshold=low_threshold,
            high_threshold=high_threshold,
            return_gpu=return_gpu,
        )
        lines = _aot_hough_lines(
            edges,
            rho_resolution=rho_resolution,
            theta_resolution=theta_resolution,
            threshold=vote_threshold,
            return_gpu=return_gpu,
        )
        return lines, edges

    def seamless_clone(
        src,
        dst,
        mask,
        center=(0, 0),
        flags=NORMAL_CLONE,
        max_iterations=200,
        buffer_provider="pool",
        return_gpu=False,
    ):
        return _aot_seamless_clone(
            src,
            dst,
            mask,
            center=center,
            flags=flags,
            max_iterations=max_iterations,
            return_gpu=return_gpu,
        )

    def _aot_pyramid_levels(src, levels, *, return_gpu=False):
        levels = builtins.max(1, int(levels))
        current = src
        if return_gpu and isinstance(src, np.ndarray):
            from .aot_api import upload as _aot_upload
            current = _aot_upload(np.ascontiguousarray(src, dtype=np.float32))
        result = [current]
        for _ in range(levels - 1):
            next_level = _aot_image_pyramid(current, levels=1, return_gpu=return_gpu)
            if tuple(next_level.shape[:2]) == tuple(current.shape[:2]):
                break
            result.append(next_level)
            current = next_level
        return result

    def build_image_pyramid(src, levels=4, **kwargs):
        return [
            level.to_numpy() if hasattr(level, "to_numpy") else np.asarray(level)
            for level in _aot_pyramid_levels(
                src, levels, return_gpu=bool(kwargs.pop("return_gpu", False))
            )
        ]

    def build_image_pyramid_gpu(src, levels=4, **kwargs):
        return _aot_pyramid_levels(src, levels, return_gpu=True)

    from .common import (
        split as _common_split,
        extract_channel as _common_extract_channel,
        insert_channel as _common_insert_channel,
    )
    split = _common_split
    extract_channel = _common_extract_channel
    insert_channel = _common_insert_channel
    def phase_correlation(ref, comp, max_shift=16, use_hanning=True):
        if int(max_shift) <= 0:
            raise ValueError("max_shift must be positive")
        if int(max_shift) != 16:
            raise NotImplementedError(
                "AOT phase correlation uses the qualified full search; "
                "non-default max_shift is not available"
            )
        return _aot_phase_correlation(ref, comp, use_hanning=use_hanning)

    def align_mtb(ref_img, target_img, max_levels=6, tolerance=4.0 / 255.0, mode="simple"):
        if str(mode).lower() != "simple":
            raise NotImplementedError("AOT MTB supports only mode='simple'")
        return _aot_align_mtb(
            ref_img, target_img, max_levels=max_levels, tolerance=tolerance
        )

    def farneback_flow(
        ref_gray,
        comp_gray,
        pyr_scale=0.5,
        num_levels=3,
        win_size=15,
        num_iters=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0,
        flow_init=None,
        buffer_provider="pool",
        return_gpu=False,
    ):
        return _aot_farneback_flow(
            ref_gray,
            comp_gray,
            pyr_scale=pyr_scale,
            num_levels=num_levels,
            win_size=win_size,
            num_iters=num_iters,
            poly_n=poly_n,
            poly_sigma=poly_sigma,
            flags=flags,
            flow_init=flow_init,
            return_gpu=return_gpu,
        )
    zncc = _aot_zncc

    # ``enhance_image`` and the channel helpers above have established AOT
    # signatures.  These adapters preserve the existing lower-case facade
    # names while keeping the native graph as the only execution backend.
    def match_template(image, template, method="zncc"):
        if str(method).lower() != "zncc":
            raise NotImplementedError("AOT match_template supports only method='zncc'")
        return _aot_zncc(image, template)

    def global_translate_zncc(image, template):
        return _aot_ncc_alignment(image, template)

    def _aot_unavailable(name, capability):
        def _missing(*args, **kwargs):
            raise NotImplementedError(
                f"{name} has no target-qualified AOT implementation ({capability}); "
                "use AOT_MODE=0 explicitly for the JIT/reference implementation"
            )
        _missing.__name__ = name
        _missing.__doc__ = f"Fail-closed AOT placeholder for {name}."
        return _missing

    # Exact direct research wrappers.
    def check_cheirality_minimal(*args, **kwargs):
        raise NotImplementedError(
            "AOT cheirality-minimal exposes only a validity/candidate index leaf; "
            "the legacy API also requires decomposed (R, t)"
        )

    def check_cheirality_full(R, t, K1, K2, pts1_all, pts2_all, inlier_mask=None):
        depths, mask, count = _aot_cheirality_full(R, t, K1, K2, pts1_all, pts2_all)
        mask = np.asarray(mask, dtype=bool)
        if inlier_mask is not None:
            supplied = np.asarray(inlier_mask, dtype=bool)
            if supplied.shape != mask.shape:
                raise ValueError("inlier_mask must match correspondence count")
            mask &= supplied
        return int(mask.sum()), mask

    def triangulate_adaptive(
        pts1,
        pts2,
        P1,
        P2,
        K1,
        K2,
        parallax_threshold=4.0,
        noise_sigma=0.5,
    ):
        if float(noise_sigma) != 0.5:
            raise NotImplementedError(
                "AOT triangulation uses the qualified fixed-noise leaf; "
                "noise_sigma must remain 0.5"
            )
        p1 = np.ascontiguousarray(np.asarray(P1, dtype=np.float32))
        p2 = np.ascontiguousarray(np.asarray(P2, dtype=np.float32))
        if p1.shape != (3, 4) or p2.shape != (3, 4):
            raise ValueError("P1 and P2 must have shape (3, 4)")
        c1 = -np.linalg.solve(p1[:, :3].astype(np.float64), p1[:, 3].astype(np.float64))
        c2 = -np.linalg.solve(p2[:, :3].astype(np.float64), p2[:, 3].astype(np.float64))
        import time as _time
        started = _time.perf_counter()
        points, methods = _aot_triangulate_adaptive(
            pts1,
            pts2,
            p1,
            p2,
            c1.astype(np.float32),
            c2.astype(np.float32),
            parallax_threshold=float(parallax_threshold),
            K1=K1,
            K2=K2,
        )
        methods = np.asarray(methods, dtype=np.int32)
        points = np.asarray(points, dtype=np.float32)
        valid_points = np.isfinite(points).all(axis=1)
        parallax_deg = 0.0
        if np.any(valid_points):
            rays1 = points[valid_points].astype(np.float64) - c1[None, :]
            rays2 = points[valid_points].astype(np.float64) - c2[None, :]
            norms1 = np.linalg.norm(rays1, axis=1)
            norms2 = np.linalg.norm(rays2, axis=1)
            good = (norms1 > 1.0e-12) & (norms2 > 1.0e-12)
            if np.any(good):
                cosine = np.sum(rays1[good] * rays2[good], axis=1) / (norms1[good] * norms2[good])
                parallax_deg = float(np.degrees(np.mean(np.arccos(np.clip(cosine, -1.0, 1.0)))))
        stats = {
            "time_ms": float((_time.perf_counter() - started) * 1000.0),
            "n_wmid2": int(np.count_nonzero(methods == 0)),
            "n_lost": int(np.count_nonzero(methods == 1)),
            "mean_parallax_deg": parallax_deg,
        }
        return points, methods, stats

    def bfmatcher_l2(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
        return _aot_match_l2(
            desc1,
            desc2,
            k=int(k),
            ratio_threshold=float(ratio_threshold),
            cross_check=bool(cross_check),
        )
    bundle_adjust_lm = _aot_bundle_adjust_lm
    def plane_sweep_stereo(
        ref_img,
        target_img,
        K_ref,
        K_target,
        R_rel,
        t_rel,
        depth_min=0.1,
        depth_max=100.0,
        n_depths=64,
        patch_radius=3,
        depth_spacing="linear",
        backend="aot",
    ):
        if str(backend).lower() not in {"aot", "auto"}:
            raise ValueError("AOT facade plane_sweep_stereo requires backend='aot'")
        return _aot_plane_sweep_stereo(
            ref_img,
            target_img,
            K_ref,
            K_target,
            R_rel,
            t_rel,
            depth_min=depth_min,
            depth_max=depth_max,
            n_depths=n_depths,
            patch_radius=patch_radius,
            depth_spacing=depth_spacing,
        )

    def multi_view_plane_sweep(
        ref_img,
        target_images,
        K_ref,
        K_targets,
        R_rels,
        t_rels,
        depth_min=0.1,
        depth_max=100.0,
        n_depths=64,
        patch_radius=3,
        backend="aot",
    ):
        if str(backend).lower() not in {"aot", "auto"}:
            raise ValueError("AOT facade multi_view_plane_sweep requires backend='aot'")
        return _aot_multi_view_plane_sweep(
            ref_img,
            target_images,
            K_ref,
            K_targets,
            R_rels,
            t_rels,
            depth_min=depth_min,
            depth_max=depth_max,
            n_depths=n_depths,
            patch_radius=patch_radius,
        )
    preprocess_point_cloud = _aot_point_cloud_preprocess
    poisson_reconstruct = _aot_poisson_reconstruct

    def statistical_outlier_removal(points, k=20, std_multiplier=2.0):
        data = np.ascontiguousarray(np.asarray(points, dtype=np.float32))
        if data.ndim != 2 or data.shape[1] != 3:
            raise ValueError("points must have shape (N, 3)")
        if len(data) == 0 or len(data) < int(k) + 1:
            return data.copy(), np.arange(len(data), dtype=np.int32)
        distances, _ = _aot_knn_distance(data, k=int(k))
        keep_mask = np.asarray(
            _aot_sor_filter(distances, std_multiplier=float(std_multiplier))
        )
        keep_indices = np.flatnonzero(keep_mask > 0).astype(np.int32)
        return data[keep_indices].copy(), keep_indices

    def radius_outlier_removal(points, radius=0.1, min_neighbors=5):
        data = np.ascontiguousarray(np.asarray(points, dtype=np.float32))
        if data.ndim != 2 or data.shape[1] != 3:
            raise ValueError("points must have shape (N, 3)")
        keep_mask = np.asarray(
            _aot_radius_filter(data, radius=float(radius), min_neighbors=int(min_neighbors))
        )
        keep_indices = np.flatnonzero(keep_mask > 0).astype(np.int32)
        return data[keep_indices].copy(), keep_indices

    def estimate_normals(points, k=20):
        data = np.ascontiguousarray(np.asarray(points, dtype=np.float32))
        if data.ndim != 2 or data.shape[1] != 3:
            raise ValueError("points must have shape (N, 3)")
        if len(data) == 0:
            return np.empty((0, 3), dtype=np.float32)
        k = builtins.min(int(k), len(data) - 1)
        if k < 3:
            return np.tile(np.asarray([[0.0, 0.0, 1.0]], dtype=np.float32), (len(data), 1))
        _, knn_idx = _aot_knn_distance(data, k=k)
        return _aot_normals_pca(data, knn_idx)

    def voxel_downsample(points, voxel_size=0.01):
        data = np.ascontiguousarray(np.asarray(points, dtype=np.float32))
        if data.ndim != 2 or data.shape[1] != 3:
            raise ValueError("points must have shape (N, 3)")
        if not np.isfinite(data).all():
            raise ValueError("points must contain only finite values")
        if not np.isfinite(voxel_size) or float(voxel_size) <= 0.0:
            raise ValueError("voxel_size must be positive and finite")
        if data.shape[0] == 0:
            return data.copy()
        voxel_indices = np.asarray(
            _aot_voxel_hash(data, voxel_size=float(voxel_size)), dtype=np.int32
        )
        order = np.argsort(voxel_indices, kind="stable")
        sorted_hash = voxel_indices[order]
        _, inverse, counts = np.unique(
            sorted_hash, return_inverse=True, return_counts=True
        )
        sorted_points = data[order]
        sums = np.column_stack(
            [
                np.bincount(inverse, weights=sorted_points[:, axis], minlength=len(counts))
                for axis in range(3)
            ]
        )
        return np.ascontiguousarray((sums / counts[:, None]).astype(np.float32))

    def hdr_fuse(
        frames,
        noise_sigmas=None,
        noise_power=2.0,
        exposure_sigma=0.2,
        exposure_power=1.0,
        detail_power=1.0,
        saturation_power=1.0,
        n_levels=None,
        noise_estimator=None,
    ):
        if noise_estimator is not None:
            raise NotImplementedError(
                "AOT HDR fusion has no stateful noise_estimator contract; "
                "pass noise_sigmas explicitly"
            )
        return _aot_hdr_fuse(
            frames,
            noise_sigmas=noise_sigmas,
            noise_power=noise_power,
            exposure_sigma=exposure_sigma,
            exposure_power=exposure_power,
            detail_power=detail_power,
            saturation_power=saturation_power,
            n_levels=n_levels,
        )

    def hdr_fuse_simple(
        frames,
        noise_sigmas=None,
        noise_power=2.0,
        exposure_sigma=0.2,
        n_levels=None,
    ):
        return _aot_hdr_fuse(
            frames,
            noise_sigmas=noise_sigmas,
            noise_power=noise_power,
            exposure_sigma=exposure_sigma,
            n_levels=n_levels,
        )

    def reinhard_tone_map(img, key=0.18, lum_white=1.0, epsilon=1e-6):
        return _aot_tone_reinhard(img, key=key, lum_white=lum_white, epsilon=epsilon)

    def srgb_gamma(img, gamma=2.2, use_srgb_curve=True):
        return _aot_tone_srgb(img, gamma=gamma, use_srgb_curve=use_srgb_curve)

    def local_tone_map(
        img,
        gain=2.0,
        target_lum=0.5,
        sigma=0.3,
        n_levels=None,
        n_iterations=2,
        apply_gamma=True,
        gamma=2.2,
    ):
        return _aot_local_tone_map(
            img,
            gain=gain,
            target_lum=target_lum,
            sigma=sigma,
            n_levels=n_levels,
            n_iterations=n_iterations,
            apply_gamma=apply_gamma,
            gamma=gamma,
        )

    def contrast_adjust(img, contrast=1.0, brightness=0.0):
        return _aot_tone_contrast(img, contrast=contrast, brightness=brightness)

    def tone_map(
        img,
        method="local",
        key=0.18,
        lum_white=1.0,
        gain=2.0,
        target_lum=0.5,
        sigma=0.3,
        n_iterations=2,
        apply_gamma=True,
        gamma=2.2,
        contrast=1.0,
        brightness=0.0,
    ):
        return _aot_tone_map(
            img,
            method=method,
            key=key,
            lum_white=lum_white,
            gain=gain,
            target_lum=target_lum,
            sigma=sigma,
            n_iterations=n_iterations,
            apply_gamma=apply_gamma,
            gamma=gamma,
            contrast=contrast,
            brightness=brightness,
        )

    # Constants are part of the OpenCV-compatible facade, not algorithm
    # dispatches.  Keep them available in both branches.
    NORM_INF, NORM_L1, NORM_L2, NORM_MINMAX = 0, 1, 2, 32
    BORDER_CONSTANT, BORDER_REPLICATE, BORDER_REFLECT_101 = 0, 1, 4

    # These historical routines already have canonical implementations or
    # compiled leaves elsewhere in the package.  Bind lightweight adapters
    # instead of keeping unnecessary AOT placeholders: the adapters do not
    # create kernels and never import a JIT image-processing fallback.
    def upsample_flow(flow, target_h, target_w, scale=2.0, buffer_provider="pool"):
        # The maintained pyramid graph consumes a plain HxWx2 ndarray.  The
        # engine auto-tags two-channel host arrays as vector buffers, so use a
        # non-owning scalar view at this ABI boundary (the old family helper
        # otherwise reports a shape mismatch on the graph).
        if isinstance(scale, (tuple, list)):
            if len(scale) != 2 or not np.isclose(float(scale[0]), float(scale[1])):
                raise NotImplementedError(
                    "AOT flow upsampling currently supports one isotropic scale"
                )
            scale = float(scale[0])
        from .aot_api import _mod as _aot_mod, engine as _aot_engine, TaichiGPUBuffer
        owned = False
        if isinstance(flow, TaichiGPUBuffer):
            owner = flow
            source = owner.view_as_vector(False, 2) if getattr(owner, "is_vector", False) else owner
        else:
            data = np.ascontiguousarray(np.asarray(flow, dtype=np.float32))
            if data.ndim != 3 or data.shape[2] != 2:
                raise ValueError("flow must have shape (H, W, 2)")
            owner = _aot_engine.upload(data, is_vector=True, vector_dim=2)
            source = owner.view_as_vector(False, 2)
            owned = True
        if len(source.shape) != 3 or int(source.shape[2]) != 2:
            if owned:
                owner.destroy()
            raise ValueError("flow must have shape (H, W, 2)")
        dst = _aot_engine.allocate(
            (int(target_h), int(target_w), 2), dtype=np.float32, is_vector=False
        )
        try:
            _aot_mod("pyramid").run(
                "upsample_flow_f32", src=source, dst=dst, scale=float(scale)
            )
            return dst.to_numpy()
        finally:
            dst.destroy()
            if owned:
                owner.destroy()

    sample_at_bicubic = _aot_sample_at_bicubic
    sample_at = _aot_sample_at
    sample_at_bilinear = _aot_sample_at_bilinear

    def cubic_hermite(A, B, C, D, t):
        """Pure arithmetic Catmull--Rom helper shared by interpolation APIs."""
        a = -np.asarray(A) / 2.0 + 1.5 * np.asarray(B) - 1.5 * np.asarray(C) + np.asarray(D) / 2.0
        b = np.asarray(A) - 2.5 * np.asarray(B) + 2.0 * np.asarray(C) - np.asarray(D) / 2.0
        c = -np.asarray(A) / 2.0 + np.asarray(C) / 2.0
        d = np.asarray(B)
        value = ((a * t + b) * t + c) * t + d
        return value.item() if np.asarray(value).ndim == 0 else value

    def hfcd_denoise(
        src,
        sigma,
        block_size=8,
        search_radius=15,
        max_matches=16,
        lambda_3d=2.7,
        cycle_spins=1,
        buffer_provider="pool",
    ):
        # ``bm3d`` is the maintained AOT implementation of this HFCD
        # pipeline; preserve the original parameter names and semantics.
        return _aot_bm3d(
            src,
            sigma=sigma,
            block_size=block_size,
            search_radius=search_radius,
            max_matches=max_matches,
            lambda_3d=lambda_3d,
            cycle_spins=cycle_spins,
            return_gpu=hasattr(src, "to_numpy"),
        )

    def build_dct_matrix(N):
        from .denoising.bm3d import build_dct_matrix as _impl
        return _impl(int(N))

    # The spatial-weight adapter composes the target-qualified gradient,
    # coarse-guidance, and four-pass fine-analysis leaves.  It raises
    # explicitly when the selected target artifact is stale/missing instead
    # of silently entering the JIT implementation.
    # These adapters keep the native leaf dispatch explicit.  Five-point
    # candidate polynomial solving and match compaction are intentionally
    # documented hybrid/host phases; distance, KNN, and correspondence
    # assembly remain on the selected AOT backend.  Missing target graphs
    # still raise from the module loader instead of silently using JIT/CPU.
    vsac_fundamental = _aot_vsac_fundamental

    def bfmatcher_hamming(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
        """Binary matching compatibility adapter.

        The qualified research suite has no portable u8 graph on every AOT
        target yet.  Reuse the canonical Hamming implementation's bounded
        host phase explicitly; this is reported as a hybrid adapter rather
        than pretending that byte popcount ran in a target graph.
        """
        from .sfm.feature_matching import _bfmatcher_hamming_numpy
        a = np.ascontiguousarray(np.asarray(desc1, dtype=np.uint8))
        b = np.ascontiguousarray(np.asarray(desc2, dtype=np.uint8))
        if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[1]:
            raise ValueError("binary descriptors must be 2-D with equal byte width")
        return _bfmatcher_hamming_numpy(a, b, int(k), float(ratio_threshold), bool(cross_check))

    def solve_five_point(pts1, pts2, K1=None, K2=None):
        """Native 5-point system assembly plus canonical host candidate solve."""
        from .sfm.five_point_solver import solve_five_point as _solve_five_point
        p1 = np.ascontiguousarray(np.asarray(pts1, dtype=np.float32))
        p2 = np.ascontiguousarray(np.asarray(pts2, dtype=np.float32))
        if p1.ndim != 2 or p2.ndim != 2 or p1.shape != p2.shape or p1.shape[0] < 5:
            raise ValueError("pts1 and pts2 must have matching shape (N, 2), N >= 5")
        # Keep the native graph in the path when its artifact is available;
        # the polynomial candidate enumeration remains the maintained host
        # phase because no target-qualified solver graph exists yet.
        try:
            from .aot_api.research import sfm_build_5pt_system_aot
            indices = np.arange(5, dtype=np.int32)
            sfm_build_5pt_system_aot(p1[:5], p2[:5], indices)
        except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
            raise NotImplementedError(
                "solve_five_point AOT requires the sfm_build_5pt_system_f32 artifact"
            ) from exc
        return _solve_five_point(p1, p2, K1=K1, K2=K2)
    # These are deliberately backend-neutral numerical utilities (they never
    # touch image buffers or dispatch a kernel).  Re-export the canonical
    # NumPy implementations rather than reporting them as unavailable in AOT
    # mode; this keeps SfM callers mode-independent without a hidden device
    # fallback or duplicate math implementation.
    from .common import (
        svd_3x3_np,
        enforce_essential_np,
        hartley_normalize,
        denormalize_fundamental,
    )

    # Legacy aliases not covered by the direct AOT demosaic import above.
    # Their implementations are present in aot_api; retaining the names here
    # avoids a mode-dependent public surface.
    mlri_admm_demosaic_1channel = mlri_admm_demosaic_1channel
    mlri_admm_demosaic_half_res = mlri_admm_demosaic_half_res
    mlri_admm_demosaic_rgb_half_res = mlri_admm_demosaic_rgb_half_res
    mlri_admm_demosaic_3channel = mlri_admm_demosaic_3channel

    # Keep the singleton OpenCV-like facade on the same native paths as the
    # module-level functions.  Without this bridge ``ta.dilate`` and friends
    # would still resolve to the historical approximation in aot_wrapper.
    for _name, _function in {
        "dilate": dilate,
        "erode": erode,
        "filter2d": filter2d,
        "normalize": normalize,
        "copyMakeBorder": copyMakeBorder,
        "copy_make_border": copy_make_border,
        "threshold": threshold,
        "ssim": ssim,
        "gpu_histogram": gpu_histogram,
        "histogram": histogram,
        "warp_affine": warp_affine,
        "gaussian_window": gaussian_window,
        "create_gaussian_window": create_gaussian_window,
        "joint_bilateral_guidance": joint_bilateral_guidance,
        "enhance_image": enhance_image,
        "enhance_grayscale": enhance_grayscale,
        "jpeg_encode_aot": jpeg_encode_aot,
    }.items():
        setattr(type(ta), _name, staticmethod(_function))


if AOT_MODE == "0":
    # The historical ``__all__`` has always advertised these names, although
    # the original JIT branch forgot to bind them.  Bind them to the existing
    # implementations (or to the existing qualified AOT leaf where no JIT
    # implementation exists) so mode selection no longer changes import
    # compatibility.  These are aliases only; no algorithm is duplicated.
    # Do not import ``aot_api`` while the package is being initialized.  The
    # compiler workers import family modules in AOT_MODE=0, and eager loading
    # the runtime facade here creates a circular ``aot_api -> taichi_aot ->
    # taichi_algorithm`` dependency.  Lazy forwarding preserves the public
    # names without making compiler imports depend on runtime initialization.
    def _jit_mode_dcb(*args, **kwargs):
        from .aot_api import dcb as implementation
        return implementation(*args, **kwargs)

    def _jit_mode_dcb_demosaic(*args, **kwargs):
        from .aot_api import dcb_demosaic as implementation
        return implementation(*args, **kwargs)

    def _jit_mode_demosaic(*args, **kwargs):
        from .aot_api import demosaic as implementation
        return implementation(*args, **kwargs)
    from .image_processing.warp_affine import warpAffine as warp_affine
    def gaussian_window(*args, **kwargs):
        from .image_processing.extended_aot import gaussian_window_aot
        return gaussian_window_aot(*args, **kwargs)

    def joint_bilateral_guidance(*args, **kwargs):
        from .image_processing.extended_aot import joint_bilateral_guidance_aot
        return joint_bilateral_guidance_aot(*args, **kwargs)

    def enhance_image(*args, **kwargs):
        from .image_processing.enhance_image import enhance_grayscale
        return enhance_grayscale(*args, **kwargs)

    def jpeg_encode_aot(*args, **kwargs):
        from .compression.jpeg_aot import jpeg_encode_aot as implementation
        return implementation(*args, **kwargs)

    def encode_grayscale_aot(*args, **kwargs):
        from .compression.jpeg_aot import encode_grayscale_aot as implementation
        return implementation(*args, **kwargs)

    def encode_rgb_aot(*args, **kwargs):
        from .compression.jpeg_aot import encode_rgb_aot as implementation
        return implementation(*args, **kwargs)

    from .image_processing.histogram import histogram

    dcb = _jit_mode_dcb
    dcb_demosaic = _jit_mode_dcb_demosaic
    demosaic = _jit_mode_demosaic
    create_gaussian_window = gaussian_window


# --- Constants ---
INTER_LINEAR = 1
INTER_NEAREST = 0
INTER_CUBIC = 2

# Color Constants
COLOR_BGR2GRAY = common.COLOR_BGR2GRAY
COLOR_RGB2GRAY = common.COLOR_RGB2GRAY
COLOR_GRAY2BGR = common.COLOR_GRAY2BGR
COLOR_GRAY2RGB = common.COLOR_GRAY2RGB

# Extended Color Conversion Constants
# (Imported from color_convert module above)


# --- Helper: Universal Channel Handler ---
def _process_generic(func, src, *args, **kwargs):
    """
    Generic wrapper to handle Single-Channel (H, W) and Multi-Channel (H, W, C).
    Applies 'func' to each channel independently if input is multi-channel.
    """
    is_taichi_field = False
    if ti is not None:
        is_taichi_field = isinstance(src, (ti.Field, ti.MatrixField))
    if not isinstance(src, np.ndarray) and not is_taichi_field:
        # Try to handle as generic sequence if needed, but usually we expect numpy/taichi
        pass

    shape = src.shape
    is_3d = len(shape) == 3
    if not is_3d:
        # 2D case: Call directly
        return func(src, *args, **kwargs)

    # --- Multi-Channel Handling ---
    if ti is None:
        raise ImportError("Taichi is not available for JIT multi-channel processing")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = shape[:2]
    c_count = shape[2]

    # Allocate output (we need to know what func returns? Usually same size image)
    # This wrapper assumes image-to-image filter.
    dst_gpu = common.get_temp_buffer(shape, ti.f32)

    # Temp buffer for single channel processing
    ch_buf_in = common.get_temp_buffer((h, w), ti.f32)
    ch_buf_out = common.get_temp_buffer((h, w), ti.f32)

    for c in range(c_count):
        # Extract (use low-level function)
        common._extract_channel_lowlevel(src_gpu, ch_buf_in, c)

        # Process
        # We pass 'dst=ch_buf_out' if the func supports it to avoid alloc
        # But 'func' might not take dst.
        # Let's assume standard signature: func(src, ..., dst=None)
        # Verify specific functions key args.

        # We'll rely on func returning a result, or writing to passed dst.
        res = func(ch_buf_in, *args, dst=ch_buf_out, **kwargs)

        # The result might be 'ch_buf_out' or a new buffer if func ignored dst.
        # Insert back
        # If func returns a numpy array (because logic in func decidied to download), that would be bad for perf.
        # But ensure_taichi_field inside func will see 'ch_buf_in' is a field, so it won't force numpy return
        # unless 'dst' logic forces it.

        # We need to make sure 'func' doesn't download.

        # Most implementations in this package:
        # return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
        # Here src_is_temp (inside func) will be False because we pass an existing field 'ch_buf_in'.
        # So it returns field (likely `res` is `ch_buf_out`).

        # Insert back (use low-level function)
        common._insert_channel_lowlevel(res, dst_gpu, c)

    # Cleanup temps
    common.release_temp_buffer(ch_buf_in)
    common.release_temp_buffer(ch_buf_out)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    # Download if input was numpy
    return common.to_numpy_if_needed(dst_gpu, isinstance(src, np.ndarray))


# --- Public API Wrappers ---


def resize(src, dsize, interpolation=INTER_LINEAR, dst=None):
    """
    Resize image with full GPU pipeline support.
    OpenCV-compatible: Same as cv2.resize()

    Args:
        src: Input image (H, W) or (H, W, C).
        dsize: Tuple (width, height). NOTE: OpenCV uses (width, height).
        interpolation: INTER_LINEAR (default), INTER_CUBIC.
        dst: Optional output buffer.
    """
    target_w, target_h = dsize

    if interpolation == INTER_CUBIC:
        return bicubic_resize(src, target_h, target_w)
    elif interpolation == INTER_NEAREST:
        return nearest_resize(src, target_h, target_w)
    else:
        return bilinear_resize(src, target_h, target_w, dst=dst)


def median(src, ksize, dst=None):
    """
    Apply Median filter.
    OpenCV-compatible: Same as cv2.medianBlur()
    """
    # Median implementation might still need 3D support in its kernel
    # If not supported, _process_generic handles it.
    return _process_generic(median_filter, src, kernel_size=ksize, dst=dst)


def gaussian(src, ksize, sigmaX=0, sigmaY=0, dst=None):
    """
    Apply Gaussian Blur.
    OpenCV-compatible: Same as cv2.GaussianBlur()

    Args:
        src: Input image.
        ksize: Tuple (w, h) or int.
        sigmaX: Standard deviation in X.
        sigmaY: Standard deviation in Y (ignored for now, uses sigmaX).
        dst: Optional output buffer.
    """
    ks = ksize[0] if isinstance(ksize, (tuple, list)) else ksize
    # OpenCV derives sigma from the kernel when sigmaX/sigmaY are zero.  The
    # previous wrapper forwarded zero directly to the Taichi implementation,
    # which divided by ``2*sigma**2`` and failed for the documented default.
    sigma = float(sigmaX or sigmaY)
    if sigma <= 0.0:
        sigma = 0.3 * ((int(ks) - 1) * 0.5 - 1.0) + 0.8
    return _gaussian_blur_impl(src, dst=dst, sigma=sigma, kernel_size=ks)


def box(src, ksize, dst=None):
    """
    Apply Box Filter (mean blur).
    OpenCV-compatible: Same as cv2.blur() or cv2.boxFilter()
    """
    ks = ksize[0] if isinstance(ksize, tuple) else ksize
    return box_filter(src, dst=dst, kernel_size=ks)


def sobel(src, dx, dy, ksize=3):
    """
    Apply Sobel operator.
    Args:
        dx: order of derivative x.
        dy: order of derivative y.
    Returns:
        The requested derivative map.
    """
    # logic: call _sobel_impl which returns (grad_x, grad_y)
    # We need to handle this specially because _process_generic expects func to return 1 image.

    # We can wrap sobel to return just one.

    def _sobel_wrapper(img, dst=None):
        # We ignore dst here for the internal call, we handle result selection
        gx, gy = _sobel_impl(img)
        if dx >= 1 and dy == 0:
            return gx
        elif dx == 0 and dy >= 1:
            return gy
        else:
            # Combined? OpenCV usually separates.
            # If user asks both, we return weighted?
            # For now return Gx + Gy or Magnitude?
            # OpenCV 'sobel' returns one output.
            # If dx=1, dy=1 -> mixed partial?
            # Let's support dx=1,dy=0 and dx=0,dy=1 primarily.
            return gx  # Default fallthrough

    return _process_generic(_sobel_wrapper, src)


def laplacian(src, ksize=1):
    """Laplacian operator."""
    return _process_generic(_laplacian_impl, src)


def bilateral(src, d, sigmaColor, sigmaSpace):
    """
    Bilateral Filter.
    Args:
        d: Diameter (mapped to s_s/spatial step loosely or ignored if using grid params).
           OpenCV uses 'd'. Taichi bilateral grid uses s_s, s_r.
           Let's map: sigmaSpace -> sigma_s. sigmaColor -> sigma_r.
           d -> s_s (spatial step)? actually s_s controls grid coarseness.
    """
    # Mapping OpenCV params to Bilateral Grid
    # OpenCV: bilateralFilter(src, d, sigmaColor, sigmaSpace)
    # Grid: s_s (spatial bin size), s_r (range bin size), sigma_s, sigma_r

    # We'll use reasonable defaults for bin sizes based on sigmas or d.
    # s_s approx sigmaSpace or d.
    # s_r approx sigmaColor.

    _s_s = builtins.max(int(sigmaSpace), 4)
    _s_r = builtins.max(int(sigmaColor), 4)

    return bilateral_grid_filter(
        src, s_s=_s_s, s_r=_s_r, sigma_s=sigmaSpace, sigma_r=sigmaColor
    )


def ransac(flow, threshold=3.0):
    """
    Apply RANSAC to flow field.
    Args:
        flow: Optical flow field (H, W, 2).
        threshold: Inlier threshold.
    """
    # RANSAC expects 2-channel flow (vector field).
    # Do NOT use _process_generic which splits channels.
    return ransac_flow_cleanup(flow, threshold=threshold)


OPTFLOW_USE_INITIAL_FLOW = 4
OPTFLOW_FARNEBACK_GAUSSIAN = 256


def calcOpticalFlowFarneback(
    prev,
    next,
    flow=None,
    pyr_scale=0.5,
    levels=3,
    winsize=15,
    iterations=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    preset="opencv",
    return_diagnostics=False,
):
    """OpenCV-style dense Farneback optical flow backed by taichi_aot."""
    from taichi_vision import taichi_aot

    if preset != "opencv" or return_diagnostics:
        raise ValueError("Taichi AOT Farneback supports the OpenCV preset without diagnostics")
    return taichi_aot.farneback_flow(
        prev,
        next,
        pyr_scale=pyr_scale,
        num_levels=levels,
        win_size=winsize,
        num_iters=iterations,
        poly_n=poly_n,
        poly_sigma=poly_sigma,
        flags=flags,
        flow_init=flow,
    )


def calcOpticalFlowPyrLK(
    prev,
    next,
    prevPts=None,
    nextPts=None,
    winSize=(13, 13),
    maxLevel=2,
    criteria=None,
    flags=0,
    minEigThreshold=1e-4,
    grid_step=48,
    border_margin=8,
    overlap=0.35,
    adaptive=False,
    adaptive_threshold=1,
    motion_mode="fast",
    dense_mode="smooth",
    max_flow_px=0.0,
    return_gpu=False,
    return_diagnostics=False,
):
    """OpenCV-style Lucas-Kanade entrypoint with internal grid dense flow."""
    return aot_wrapper.calcOpticalFlowPyrLK(
        prev,
        next,
        prevPts=prevPts,
        nextPts=nextPts,
        winSize=winSize,
        maxLevel=maxLevel,
        criteria=criteria,
        flags=flags,
        minEigThreshold=minEigThreshold,
        grid_step=grid_step,
        border_margin=border_margin,
        overlap=overlap,
        adaptive=adaptive,
        adaptive_threshold=adaptive_threshold,
        motion_mode=motion_mode,
        dense_mode=dense_mode,
        max_flow_px=max_flow_px,
        return_gpu=return_gpu,
        return_diagnostics=return_diagnostics,
    )


def calcOpticalFlowPyrLKGrid(
    prev,
    next,
    winSize=(17, 17),
    maxLevel=2,
    criteria=None,
    grid_step=16,
    border_margin=8,
    motion_mode="fast",
    return_diagnostics=False,
):
    """Lucas-Kanade compact grid flow entrypoint for CPU-like densification."""
    return aot_wrapper.calcOpticalFlowPyrLKGrid(
        prev,
        next,
        winSize=winSize,
        maxLevel=maxLevel,
        criteria=criteria,
        grid_step=grid_step,
        border_margin=border_margin,
        motion_mode=motion_mode,
        return_diagnostics=return_diagnostics,
    )


# --- Core Utilities ---
cvtColor = common.cvtColor
absdiff = common.absdiff


def ncc(image, template):
    """
    Simplified Normalized Cross-Correlation (ZNCC) interface.
    Plug-and-play template matching using Spatial backend.
    """
    return zncc(image, template)


if AOT_MODE == "1":
    # The generic OpenCV-like helpers below are defined after the mode-specific
    # imports for historical reasons.  Rebind them here to the canonical AOT
    # leaves; otherwise their JIT-only implementation globals (for example
    # ``bilinear_resize`` and ``median_filter``) are absent in AOT mode and a
    # seemingly valid public call raises ``NameError``.  These are adapters,
    # not duplicate kernels: every operation still dispatches through
    # ``aot_api`` and its target-qualified graph.
    def _aot_store_destination(result, dst):
        if dst is None:
            return result
        if hasattr(dst, "to_numpy") and hasattr(result, "to_numpy"):
            from .aot_api import copy_field as _aot_copy_field

            _aot_copy_field(result, dst)
            return dst
        payload = result.to_numpy() if hasattr(result, "to_numpy") else result
        dst[...] = payload
        return dst

    def resize(src, dsize, interpolation=INTER_LINEAR, dst=None):
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        native_dst = (
            dst
            if is_gpu and hasattr(dst, "handle") and hasattr(dst, "shape")
            else None
        )
        result = _aot_resize(
            src,
            dsize,
            interpolation=interpolation,
            return_gpu=is_gpu,
            dst=native_dst,
        )
        return result if result is dst else (_aot_store_destination(result, dst) if dst is not None else result)

    def median(src, ksize, dst=None):
        size = int(ksize[0] if isinstance(ksize, (tuple, list)) else ksize)
        if size != 3:
            raise NotImplementedError("AOT median currently supports only a 3x3 kernel")
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        result = _aot_median_filter(src, return_gpu=is_gpu, kernel_size=size)
        return result if result is dst else (_aot_store_destination(result, dst) if dst is not None else result)

    def gaussian(src, ksize, sigmaX=0, sigmaY=0, dst=None):
        size = int(ksize[0] if isinstance(ksize, (tuple, list)) else ksize)
        sigma = float(sigmaX or sigmaY or 1.0)
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        native_dst = (
            dst
            if is_gpu and hasattr(dst, "handle") and hasattr(dst, "shape")
            else None
        )
        result = _aot_gaussian_blur(
            src,
            sigma=sigma,
            kernel_size=size,
            return_gpu=is_gpu,
            dst=native_dst,
        )
        return result if result is dst else (_aot_store_destination(result, dst) if dst is not None else result)

    def box(src, ksize, dst=None):
        size = int(ksize[0] if isinstance(ksize, (tuple, list)) else ksize)
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        native_dst = (
            dst
            if is_gpu and hasattr(dst, "handle") and hasattr(dst, "shape")
            else None
        )
        result = _aot_box_filter(
            src,
            kernel_size=size,
            return_gpu=is_gpu,
            dst=native_dst,
        )
        return _aot_store_destination(result, dst) if dst is not None else result

    def sobel(src, dx, dy, ksize=3):
        if int(ksize) != 3:
            raise NotImplementedError("AOT Sobel currently supports only a 3x3 kernel")
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        gx, gy = _aot_sobel(src, return_gpu=is_gpu)
        if int(dx) >= 1 and int(dy) == 0:
            return gx
        if int(dx) == 0 and int(dy) >= 1:
            return gy
        # Preserve the historical facade behaviour for mixed derivatives: the
        # old wrapper selected the horizontal component as its fallback.
        return gx

    def laplacian(src, ksize=1):
        if int(ksize) not in (1, 3):
            raise NotImplementedError("AOT Laplacian supports ksize=1 or ksize=3")
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        return _aot_laplacian(src, return_gpu=is_gpu)

    def bilateral(src, d, sigmaColor, sigmaSpace):
        # The existing AOT leaf exposes validated presets rather than the
        # OpenCV d/sigma tuple.  Select the closest preset deterministically;
        # do not call the leaf with unsupported ``s_s``/``s_r`` keywords.
        strength = builtins.max(float(sigmaColor), float(sigmaSpace), 0.0)
        preset = "heavy" if strength >= 8.0 else ("light" if strength <= 2.0 else "medium")
        is_gpu = hasattr(src, "to_numpy") and not isinstance(src, np.ndarray)
        return _aot_bilateral_grid_filter(src, preset=preset, return_gpu=is_gpu)

    def ransac(flow, threshold=3.0):
        return _aot_ransac_flow_cleanup(flow, threshold=float(threshold), return_gpu=False)

    def cvtColor(src, code, dst=None):
        result = _aot_cvtColor(src, code)
        return _aot_store_destination(result, dst)

    def absdiff(src1, src2, dst=None):
        result = _aot_absdiff(src1, src2)
        return _aot_store_destination(result, dst)


# --- AOT Math Ops ---
# Keep these API names aligned with the experimental wrapper while preserving
# the existing taichi_algorithm import surface in both AOT and JIT modes.
ta = aot_wrapper.ta
array = aot_wrapper.array
gpu_abs = aot_wrapper.gpu_abs
gpu_sqrt = aot_wrapper.gpu_sqrt
gpu_log = aot_wrapper.gpu_log
gpu_exp = aot_wrapper.gpu_exp
gpu_square = aot_wrapper.gpu_square
gpu_power = aot_wrapper.gpu_power
gpu_clip = aot_wrapper.gpu_clip
gpu_where = aot_wrapper.gpu_where
gpu_sum = aot_wrapper.gpu_sum
gpu_max = aot_wrapper.gpu_max
gpu_min = aot_wrapper.gpu_min
gpu_mean = aot_wrapper.gpu_mean
gpu_std = aot_wrapper.gpu_std
gpu_matmul = aot_wrapper.gpu_matmul
gpu_mat3_inv = aot_wrapper.gpu_mat3_inv
gpu_mat3_det = aot_wrapper.gpu_mat3_det
gpu_sort = aot_wrapper.gpu_sort
gpu_argsort = aot_wrapper.gpu_argsort
gpu_unique = aot_wrapper.gpu_unique
gpu_meshgrid = aot_wrapper.gpu_meshgrid
abs = aot_wrapper.gpu_abs
sqrt = aot_wrapper.gpu_sqrt
log = aot_wrapper.gpu_log
exp = aot_wrapper.gpu_exp
square = aot_wrapper.gpu_square
power = aot_wrapper.gpu_power
clip = aot_wrapper.gpu_clip
where = aot_wrapper.gpu_where
sum = aot_wrapper.gpu_sum
max = aot_wrapper.gpu_max
min = aot_wrapper.gpu_min
mean = aot_wrapper.gpu_mean
std = aot_wrapper.gpu_std
matmul = aot_wrapper.matmul
mat3_inv = aot_wrapper.gpu_mat3_inv
mat3_det = aot_wrapper.gpu_mat3_det
sort = aot_wrapper.gpu_sort
argsort = aot_wrapper.gpu_argsort
unique = aot_wrapper.gpu_unique
meshgrid = aot_wrapper.gpu_meshgrid


__all__ = [
    "INTER_LINEAR",
    "INTER_NEAREST",
    "INTER_CUBIC",
    "COLOR_BGR2GRAY",
    "COLOR_RGB2GRAY",
    "COLOR_GRAY2BGR",
    "COLOR_GRAY2RGB",
    # Extended color conversions
    "COLOR_BGR2HSV",
    "COLOR_HSV2BGR",
    "COLOR_BGR2LAB",
    "COLOR_LAB2BGR",
    "COLOR_BGR2YCrCb",
    "COLOR_YCrCb2BGR",
    "cvtColor_extended",
    # Thresholding
    "THRESH_BINARY",
    "THRESH_BINARY_INV",
    "THRESH_OTSU",
    "otsu_threshold",
    # Inpainting flags
    "INPAINT_TELEA",
    "INPAINT_NS",
    # Seamless clone flags
    "NORMAL_CLONE",
    "MIXED_CLONE",
    "MONOCHROME_TRANSFER",
    # Core API
    "resize",
    "median",
    "gaussian",
    "box",
    "sobel",
    "laplacian",
    "bilateral",
    "ransac",
    "cvtColor",
    "absdiff",
    "remap",
    # New algorithms
    "guided_filter",
    "clahe",
    "canny",
    "hough_lines",
    "hough_lines_with_canny",
    "non_local_means",
    "hfcd_denoise",
    "build_dct_matrix",
    "inpaint",
    "seamless_clone",
    # Pyramid APIs
    "build_image_pyramid",
    "build_image_pyramid_gpu",
    "upsample_flow",
    # Bicubic Interpolation APIs
    "sample_at_bicubic",
    "sample_at",
    "cubic_hermite",
    # Bilinear Interpolation APIs
    "sample_at_bilinear",
    # Channel Operations
    "split",
    "merge",
    "extract_channel",
    "insert_channel",
    "copy",
    "phase_correlation",
    "fft2",
    "ifft2",
    "zncc",
    "match_template",
    "global_translate_zncc",
    "ncc",
    "enhance_grayscale",
    "hamilton",
    "hamilton_demosaic",
    "arm",
    "arm_demosaic",
    "dcb",
    "dcb_demosaic",
    "mlri_admm",
    "mlri_admm_demosaic",
    "mlri_admm_demosaic_1channel",
    "mlri_admm_demosaic_half_res",
    "mlri_admm_demosaic_rgb_half_res",
    "mlri_admm_demosaic_3channel",
    "demosaic",
    "align_mtb",
    "farneback_flow",
    "calcOpticalFlowFarneback",
    "calcOpticalFlowPyrLK",
    "calcOpticalFlowPyrLKGrid",
    "OPTFLOW_USE_INITIAL_FLOW",
    "OPTFLOW_FARNEBACK_GAUSSIAN",
    "dilate",
    "erode",
    "warp_affine",
    "gaussian_window",
    "create_gaussian_window",
    "joint_bilateral_guidance",
    "enhance_image",
    "encode_grayscale_aot",
    "encode_rgb_aot",
    "jpeg_encode_aot",
    # New native GPU modules
    "filter2d",
    "normalize",
    "NORM_INF",
    "NORM_L1",
    "NORM_L2",
    "NORM_MINMAX",
    "copy_make_border",
    "BORDER_CONSTANT",
    "BORDER_REFLECT_101",
    "BORDER_REPLICATE",
    "threshold",
    "THRESH_BINARY",
    "THRESH_BINARY_INV",
    "THRESH_TRUNC",
    "THRESH_TOZERO",
    "THRESH_TOZERO_INV",
    "THRESH_OTSU",
    "ssim",
    "gpu_histogram",
    "histogram",
    "hdr_fuse",
    "hdr_fuse_simple",
    "reinhard_tone_map",
    "srgb_gamma",
    "local_tone_map",
    "contrast_adjust",
    "tone_map",
    # SfM Pipeline
    "vsac_fundamental",
    "solve_five_point",
    "check_cheirality_minimal",
    "check_cheirality_full",
    "triangulate_adaptive",
    "bfmatcher_l2",
    "bfmatcher_hamming",
    "bundle_adjust_lm",
    "plane_sweep_stereo",
    "multi_view_plane_sweep",
    "statistical_outlier_removal",
    "radius_outlier_removal",
    "voxel_downsample",
    "estimate_normals",
    "preprocess_point_cloud",
    "poisson_reconstruct",
    "svd_3x3_np",
    "enforce_essential_np",
    "hartley_normalize",
    "denormalize_fundamental",
    "aot_wrapper",
    "ta",
    "array",
    # Math Ops GPU
    "gpu_abs",
    "gpu_sqrt",
    "gpu_log",
    "gpu_exp",
    "gpu_square",
    "gpu_power",
    "gpu_clip",
    "gpu_where",
    "gpu_sum",
    "gpu_max",
    "gpu_min",
    "gpu_mean",
    "gpu_std",
    "gpu_matmul",
    "gpu_mat3_inv",
    "gpu_mat3_det",
    "gpu_sort",
    "gpu_argsort",
    "gpu_unique",
    "gpu_meshgrid",
    # NumPy-like Math Ops aliases
    "abs",
    "sqrt",
    "log",
    "exp",
    "square",
    "power",
    "clip",
    "where",
    "sum",
    "max",
    "min",
    "mean",
    "std",
    "matmul",
    "mat3_inv",
    "mat3_det",
    "sort",
    "argsort",
    "unique",
    "meshgrid",
]
